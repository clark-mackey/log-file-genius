# LFG Cleanup — Consistency & Correctness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the shipped LFG product internally consistent and correct — a fresh install and an updated install produce identical, non-contradictory artifacts — with no new capabilities.

**Architecture:** Markdown-template product distributed via git submodule + installer scripts (bash + PowerShell). A single canonical `.logfile-config.yml` (written by the installer) carries `paths:` and `token_targets:` blocks that all consumers read. `ai-rules/` is the single source for rule files. STATE.md is the single home for "the now."

**Tech Stack:** Bash, PowerShell, Python 3.11+ (stdlib only — no PyYAML), Markdown, YAML config, pytest.

**Source spec:** `docs/superpowers/specs/2026-05-27-lfg-cleanup-consistency-design.md`

---

## Design decisions made during planning (review these)

1. **Budget source of truth = config `token_targets:` block** (per the AskUserQuestion recommendation). The installer writes it; `lint-logs.py` already reads `token_targets.*`; the shell validators are converted to read it. `profiles/*.yml` become documented presets, not runtime-loaded, reconciled by a consistency test.
2. **PyYAML removal is Phase 1**, not last — the stdlib parser underpins budget loading.
3. **Canonical config schema** (what the installer writes):
   ```yaml
   paths:
     changelog: logs/CHANGELOG.md
     devlog: logs/DEVLOG.md
     state: logs/STATE.md
     adr_dir: logs/adr/
   token_targets:
     changelog: 10000
     devlog: 15000
     combined: 25000
     state: 500
   ```
4. **Shell validators** (`validate-log-files.sh/.ps1`) get block-aware parsing (awk for bash, regex-with-context for PowerShell) to read `paths:` and `token_targets:`; canonical defaults remain as the only fallback.
5. **Tests live in** `product/tests/` (new dir) for pytest; the installer smoke test is a script under `product/tests/` runnable on both platforms.

## Canonical numbers (single set, used everywhere)

- CHANGELOG: 10000 (warning at 80% = 8000)
- DEVLOG: 15000 (warning at 80% = 12000)
- Combined: 25000 (warning at 80% = 20000)
- STATE: 500 (warning at 80% = 400)

---

## File structure

- `product/scripts/config_parser.py` — **new**: stdlib YAML-subset parser (one responsibility: parse the config).
- `product/scripts/lint-logs.py` — modify: use `config_parser`; drop `import yaml`; move "Current Context" requirement from DEVLOG to STATE; add STATE validation.
- `product/scripts/validate-log-files.sh` / `.ps1` — modify: read `paths:` + `token_targets:` from config; remove hardcoded constants (keep canonical defaults as fallback).
- `product/scripts/install.sh` / `.ps1` — modify: write `paths:` + `token_targets:` config blocks.
- `product/scripts/update.sh` / `.ps1` — modify: source rules from `ai-rules/` (not `starter-packs/`); update the full `.claude/rules/` dir; add brownfield STATE migration.
- `product/scripts/check-ai-rules.py` — modify: update stale dedup comment.
- `product/scripts/pre-commit` — modify: remove `--with-hooks` reference in header comment.
- `product/templates/{CHANGELOG,DEVLOG,STATE,ADR}_template.md` — modify: add YAML frontmatter `related:`; fix prose link symmetry; move "now" into STATE; trim DEVLOG.
- `product/ai-rules/{augment,claude-code}/log-file-maintenance.md` — modify: SESSION START/END use STATE; compress (token diet).
- `product/ai-rules/claude-code/project_instructions.md` — modify: budgets, paths, STATE role.
- `product/ai-rules/{augment,claude-code}/status-update.md`, `update-planning-docs.md` — modify: read config paths, not hardcoded `docs/planning/`.
- `product/starter-packs/**` — **delete**.
- `README.md`, `product/docs/log_file_how_to.md` — modify: correct claims, STATE role, budgets.
- This repo's `logs/DEVLOG.md` + new root `STATE.md` — re-dogfood.
- `product/tests/` — **new**: pytest + smoke test + directive checklist.

---

## Phase 1 — Stdlib config parser (replaces PyYAML)

### Task 1: Stdlib config parser module

**Files:**
- Create: `product/scripts/config_parser.py`
- Test: `product/tests/test_config_parser.py`

- [ ] **Step 1: Write the failing test**

```python
# product/tests/test_config_parser.py
import textwrap
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from config_parser import parse_config, ConfigError


def write(tmp_path, text):
    p = tmp_path / ".logfile-config.yml"
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return str(p)


def test_flat_and_nested_keys(tmp_path):
    cfg = parse_config(write(tmp_path, """
        profile: solo-developer
        ai_assistant: claude-code
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 10000
          combined: 25000
    """))
    assert cfg["profile"] == "solo-developer"
    assert cfg["paths"]["changelog"] == "logs/CHANGELOG.md"
    assert cfg["token_targets"]["changelog"] == 10000
    assert cfg["token_targets"]["combined"] == 25000


def test_quotes_and_inline_comments(tmp_path):
    cfg = parse_config(write(tmp_path, """
        log_file_genius_version: "0.2.0"   # version
        profile: 'team'
    """))
    assert cfg["log_file_genius_version"] == "0.2.0"
    assert cfg["profile"] == "team"


def test_missing_file_returns_empty(tmp_path):
    assert parse_config(str(tmp_path / "nope.yml")) == {}


def test_tabs_fail_loudly(tmp_path):
    p = tmp_path / ".logfile-config.yml"
    p.write_text("paths:\n\tchangelog: x\n", encoding="utf-8")
    with pytest.raises(ConfigError):
        parse_config(str(p))


def test_real_profiles_parse(tmp_path):
    # The preset profile files are documentation, but must at least not crash
    # the parser on their top-level scalars.
    profiles = Path(__file__).resolve().parents[1] / "profiles"
    for f in profiles.glob("*.yml"):
        # Should not raise on the top-level scalar keys we rely on.
        parse_config(str(f))
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest product/tests/test_config_parser.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'config_parser'`

- [ ] **Step 3: Write minimal implementation**

```python
# product/scripts/config_parser.py
"""Minimal, dependency-free parser for the LFG config subset.

Supported subset (documented contract):
  - UTF-8 text, space indentation only (tabs are an error)
  - top-level `key: value` scalars
  - one level of nesting: a `key:` line followed by 2-space-indented `key: value`
  - `#` comments (full-line or trailing), blank lines ignored
  - values may be optionally single- or double-quoted
  - integer-looking values are coerced to int

Anything outside this subset raises ConfigError (fail loudly, never guess).
"""
from __future__ import annotations
import os
from typing import Dict, Any


class ConfigError(ValueError):
    pass


def _coerce(value: str) -> Any:
    v = value.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    if v.lstrip("-").isdigit():
        return int(v)
    return v


def _strip_comment(line: str) -> str:
    # Remove trailing comments not inside quotes (config subset has no '#' in values).
    out = []
    quote = None
    for ch in line:
        if quote:
            if ch == quote:
                quote = None
            out.append(ch)
        elif ch in "\"'":
            quote = ch
            out.append(ch)
        elif ch == "#":
            break
        else:
            out.append(ch)
    return "".join(out).rstrip()


def parse_config(config_path: str) -> Dict[str, Any]:
    if not os.path.exists(config_path):
        return {}

    result: Dict[str, Any] = {}
    current_parent = None

    with open(config_path, "r", encoding="utf-8") as f:
        for lineno, raw in enumerate(f, 1):
            if "\t" in raw:
                raise ConfigError(f"Tab indentation not allowed (line {lineno})")
            line = _strip_comment(raw)
            if not line.strip():
                continue

            indent = len(line) - len(line.lstrip(" "))
            stripped = line.strip()

            if ":" not in stripped:
                raise ConfigError(f"Expected 'key: value' (line {lineno}): {stripped!r}")

            key, _, value = stripped.partition(":")
            key = key.strip()
            value = value.strip()

            if indent == 0:
                if value == "":
                    result[key] = {}
                    current_parent = key
                else:
                    result[key] = _coerce(value)
                    current_parent = None
            elif indent == 2:
                if current_parent is None or not isinstance(result.get(current_parent), dict):
                    raise ConfigError(f"Nested key without parent block (line {lineno})")
                result[current_parent][key] = _coerce(value)
            else:
                raise ConfigError(f"Unexpected indentation {indent} (line {lineno})")

    return result
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest product/tests/test_config_parser.py -v`
Expected: PASS (all 5 tests)

- [ ] **Step 5: Commit**

```bash
git add product/scripts/config_parser.py product/tests/test_config_parser.py
git commit -m "feat: add stdlib config parser (removes PyYAML dependency)"
```

### Task 2: Switch lint-logs.py to the stdlib parser

**Files:**
- Modify: `product/scripts/lint-logs.py:23-31` (imports), `277-287` (`_load_config`)
- Test: `product/tests/test_lint_logs_config.py`

- [ ] **Step 1: Write the failing test**

```python
# product/tests/test_lint_logs_config.py
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import importlib.util
spec = importlib.util.spec_from_file_location(
    "lint_logs", Path(__file__).resolve().parents[1] / "scripts" / "lint-logs.py")
lint_logs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lint_logs)


def test_loglinter_reads_token_targets_from_config(tmp_path):
    cfg = tmp_path / ".logfile-config.yml"
    cfg.write_text(
        "paths:\n  changelog: logs/CHANGELOG.md\n"
        "token_targets:\n  changelog: 9999\n  devlog: 12345\n  combined: 22222\n",
        encoding="utf-8")
    linter = lint_logs.LogLinter(config_path=str(cfg))
    assert linter.changelog_target == 9999
    assert linter.devlog_target == 12345
    assert linter.combined_target == 22222
    assert linter.changelog_path == "logs/CHANGELOG.md"


def test_loglinter_defaults_without_config(tmp_path):
    linter = lint_logs.LogLinter(config_path=str(tmp_path / "absent.yml"))
    assert linter.changelog_target == 10000
    assert linter.devlog_target == 15000
    assert linter.combined_target == 25000
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m pytest product/tests/test_lint_logs_config.py -v`
Expected: FAIL — currently `import yaml` raises `ModuleNotFoundError` in environments without PyYAML, or the import line errors.

- [ ] **Step 3: Make the change**

In `product/scripts/lint-logs.py`, replace the import block. Change:

```python
from typing import List, Dict, Optional, Tuple
import yaml
```

to:

```python
from typing import List, Dict, Optional, Tuple
from config_parser import parse_config, ConfigError
```

Add at the top of the file, after the existing `import sys` (so the sibling module resolves when run as a script):

```python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
```

Replace the `_load_config` method body. Change:

```python
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            print(f"Warning: Could not load config: {e}", file=sys.stderr)
            return {}
```

to:

```python
        try:
            return parse_config(config_path)
        except ConfigError as e:
            print(f"ERROR: Invalid .logfile-config.yml: {e}", file=sys.stderr)
            sys.exit(2)
```

(Removing the `if not os.path.exists(...)` guard is unnecessary — `parse_config` already returns `{}` for a missing file; leave the existing guard in place, it is harmless.)

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m pytest product/tests/test_lint_logs_config.py -v`
Expected: PASS

- [ ] **Step 5: Verify no PyYAML references remain**

Run: `grep -rn "import yaml\|yaml\.safe_load\|PyYAML" product/scripts/`
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add product/scripts/lint-logs.py product/tests/test_lint_logs_config.py
git commit -m "refactor: lint-logs.py uses stdlib config parser, drops PyYAML"
```

---

## Phase 2 — Budget source of truth (loaders)

### Task 3: Shell validators read paths + token_targets from config (bash)

**Files:**
- Modify: `product/scripts/validate-log-files.sh:22-29` (constants), `119-161` (`load_profile_config`)
- Test: `product/tests/test_validate_sh.sh`

- [ ] **Step 1: Write the failing test**

```bash
# product/tests/test_validate_sh.sh
#!/usr/bin/env bash
set -euo pipefail
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
mkdir -p logs alt
cat > .logfile-config.yml <<'EOF'
paths:
  changelog: alt/CHANGELOG.md
  devlog: alt/DEVLOG.md
token_targets:
  changelog: 9000
  devlog: 13000
EOF
printf '# x\n' > alt/CHANGELOG.md
printf '# x\n' > alt/DEVLOG.md

# Source the script's config loader in a way that prints resolved values.
cp "$OLDPWD/product/scripts/validate-log-files.sh" ./vlf.sh
# Run with a debug flag we add in Step 3 that echoes resolved config then exits 0.
OUT="$(bash ./vlf.sh --print-config)"
echo "$OUT" | grep -q "CHANGELOG_PATH=alt/CHANGELOG.md" || { echo "path not read"; exit 1; }
echo "$OUT" | grep -q "CHANGELOG_TOKEN_ERROR=9000" || { echo "token not read"; exit 1; }
echo "$OUT" | grep -q "CHANGELOG_TOKEN_WARNING=7200" || { echo "warning not 80%"; exit 1; }
echo "PASS"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `bash product/tests/test_validate_sh.sh`
Expected: FAIL — `--print-config` flag does not exist yet; script ignores `paths:`/`token_targets:`.

- [ ] **Step 3: Make the change**

In `product/scripts/validate-log-files.sh`, the defaults stay as canonical fallbacks (lines 22-29 already hold `logs/` paths and 8000/10000/12000/15000). Replace the body of `load_profile_config()` (lines ~119-161) with block-aware awk extraction:

```bash
load_profile_config() {
    local config_file=".logfile-config.yml"
    if [ ! -f "$config_file" ]; then
        return 0
    fi

    # Block-aware extraction: read `key` under a given parent block.
    read_nested() {
        awk -v parent="$1" -v key="$2" '
            /^[A-Za-z_]+:/ { inblk = ($0 ~ "^" parent ":") }
            inblk && $1 == key":" { print $2; exit }
        ' "$config_file"
    }

    local v
    v=$(read_nested "paths" "changelog"); [ -n "$v" ] && CHANGELOG_PATH="$v"
    v=$(read_nested "paths" "devlog");    [ -n "$v" ] && DEVLOG_PATH="$v"

    v=$(read_nested "token_targets" "changelog")
    if [ -n "$v" ]; then CHANGELOG_TOKEN_ERROR="$v"; CHANGELOG_TOKEN_WARNING=$((v * 80 / 100)); fi
    v=$(read_nested "token_targets" "devlog")
    if [ -n "$v" ]; then DEVLOG_TOKEN_ERROR="$v"; DEVLOG_TOKEN_WARNING=$((v * 80 / 100)); fi
}
```

Add a `--print-config` debug branch. After argument parsing (near line 56-62 where flags are handled), add a case for `--print-config`, and after `load_profile_config` runs (near line 386-387), add:

```bash
if [ "${PRINT_CONFIG:-false}" = true ]; then
    load_profile_config
    echo "CHANGELOG_PATH=$CHANGELOG_PATH"
    echo "DEVLOG_PATH=$DEVLOG_PATH"
    echo "CHANGELOG_TOKEN_ERROR=$CHANGELOG_TOKEN_ERROR"
    echo "CHANGELOG_TOKEN_WARNING=$CHANGELOG_TOKEN_WARNING"
    echo "DEVLOG_TOKEN_ERROR=$DEVLOG_TOKEN_ERROR"
    echo "DEVLOG_TOKEN_WARNING=$DEVLOG_TOKEN_WARNING"
    exit 0
fi
```

Add `--print-config) PRINT_CONFIG=true ;;` to the argument `case` block and initialize `PRINT_CONFIG=false` with the other flag defaults (near line 49-50).

- [ ] **Step 4: Run test to verify it passes**

Run: `bash product/tests/test_validate_sh.sh`
Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add product/scripts/validate-log-files.sh product/tests/test_validate_sh.sh
git commit -m "feat: validate-log-files.sh reads paths and token_targets from config"
```

### Task 4: Shell validator reads config (PowerShell)

**Files:**
- Modify: `product/scripts/validate-log-files.ps1:42-50` (constants), `~145-180` (config load)
- Test: `product/tests/test_validate_ps1.ps1`

- [ ] **Step 1: Write the failing test**

```powershell
# product/tests/test_validate_ps1.ps1
$ErrorActionPreference = "Stop"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tmp "alt") | Out-Null
Push-Location $tmp
@"
paths:
  changelog: alt/CHANGELOG.md
  devlog: alt/DEVLOG.md
token_targets:
  changelog: 9000
  devlog: 13000
"@ | Set-Content -Path ".logfile-config.yml" -Encoding utf8
"# x" | Set-Content alt/CHANGELOG.md
"# x" | Set-Content alt/DEVLOG.md
$repo = $env:LFG_REPO
$out = & pwsh (Join-Path $repo "product/scripts/validate-log-files.ps1") -PrintConfig
Pop-Location
Remove-Item -Recurse -Force $tmp
if ($out -notmatch "CHANGELOG_PATH=alt/CHANGELOG.md") { throw "path not read" }
if ($out -notmatch "CHANGELOG_TOKEN_ERROR=9000") { throw "token not read" }
if ($out -notmatch "CHANGELOG_TOKEN_WARNING=7200") { throw "warning not 80%" }
Write-Host "PASS"
```

- [ ] **Step 2: Run test to verify it fails**

Run: `pwsh product/tests/test_validate_ps1.ps1` (set `$env:LFG_REPO` to repo root first)
Expected: FAIL — `-PrintConfig` switch and config reading don't exist yet.

- [ ] **Step 3: Make the change**

In `product/scripts/validate-log-files.ps1`, keep the canonical default constants (lines 43-50). Replace the config-loading regex block (the section near lines 145-180 that matches `changelog_warning:` etc.) with block-aware parsing:

```powershell
function Read-NestedConfig {
    param([string]$Content, [string]$Parent, [string]$Key)
    # Match the parent block, then the indented key within it.
    $pattern = "(?ms)^$Parent:\s*$(.*?)(?:^\S|\z)"
    $m = [regex]::Match($Content, $pattern)
    if (-not $m.Success) { return $null }
    $block = $m.Groups[1].Value
    $km = [regex]::Match($block, "(?m)^\s+$Key:\s*(\S+)")
    if ($km.Success) { return $km.Groups[1].Value }
    return $null
}

if (Test-Path ".logfile-config.yml") {
    $cfg = Get-Content ".logfile-config.yml" -Raw
    $v = Read-NestedConfig $cfg "paths" "changelog"; if ($v) { $CHANGELOG_PATH = $v }
    $v = Read-NestedConfig $cfg "paths" "devlog";    if ($v) { $DEVLOG_PATH = $v }
    $v = Read-NestedConfig $cfg "token_targets" "changelog"
    if ($v) { $CHANGELOG_TOKEN_ERROR = [int]$v; $CHANGELOG_TOKEN_WARNING = [int]([int]$v * 0.8) }
    $v = Read-NestedConfig $cfg "token_targets" "devlog"
    if ($v) { $DEVLOG_TOKEN_ERROR = [int]$v; $DEVLOG_TOKEN_WARNING = [int]([int]$v * 0.8) }
}
```

Add a `-PrintConfig` switch to the `param(...)` block at the top, and immediately after the config-loading block add:

```powershell
if ($PrintConfig) {
    Write-Output "CHANGELOG_PATH=$CHANGELOG_PATH"
    Write-Output "DEVLOG_PATH=$DEVLOG_PATH"
    Write-Output "CHANGELOG_TOKEN_ERROR=$CHANGELOG_TOKEN_ERROR"
    Write-Output "CHANGELOG_TOKEN_WARNING=$CHANGELOG_TOKEN_WARNING"
    Write-Output "DEVLOG_TOKEN_ERROR=$DEVLOG_TOKEN_ERROR"
    Write-Output "DEVLOG_TOKEN_WARNING=$DEVLOG_TOKEN_WARNING"
    exit 0
}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `$env:LFG_REPO=(Resolve-Path .); pwsh product/tests/test_validate_ps1.ps1`
Expected: `PASS`

- [ ] **Step 5: Commit**

```bash
git add product/scripts/validate-log-files.ps1 product/tests/test_validate_ps1.ps1
git commit -m "feat: validate-log-files.ps1 reads paths and token_targets from config"
```

### Task 5: Budget consistency test

**Files:**
- Test: `product/tests/test_budget_consistency.py`

- [ ] **Step 1: Write the test (this is the guard, no implementation follows)**

```python
# product/tests/test_budget_consistency.py
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANON = {"changelog": 10000, "devlog": 15000, "combined": 25000, "state": 500}


def test_lint_logs_defaults_match_canon():
    txt = (ROOT / "product/scripts/lint-logs.py").read_text(encoding="utf-8")
    assert "'changelog', 10000" in txt
    assert "'devlog', 15000" in txt
    assert "'combined', 25000" in txt


def test_shell_validator_defaults_match_canon():
    sh = (ROOT / "product/scripts/validate-log-files.sh").read_text(encoding="utf-8")
    assert "CHANGELOG_TOKEN_ERROR=10000" in sh
    assert "DEVLOG_TOKEN_ERROR=15000" in sh
    ps = (ROOT / "product/scripts/validate-log-files.ps1").read_text(encoding="utf-8")
    assert "CHANGELOG_TOKEN_ERROR = 10000" in ps
    assert "DEVLOG_TOKEN_ERROR = 15000" in ps


def test_no_contradictory_combined_budget_string():
    # The old "<10k combined" contradiction must be gone everywhere.
    for p in (ROOT / "product").rglob("*.md"):
        txt = p.read_text(encoding="utf-8", errors="ignore")
        assert "under 10,000 tokens combined" not in txt.lower().replace("-", " ")
        assert "10,000 tokens combined" not in txt


def test_profile_presets_match_canon():
    # profiles/*.yml are presets/documentation; their error numbers must match canon.
    for f in (ROOT / "product/profiles").glob("*.yml"):
        txt = f.read_text(encoding="utf-8")
        if "changelog_error:" in txt:
            assert re.search(r"changelog_error:\s*10000", txt), f"{f.name} changelog_error"
            assert re.search(r"devlog_error:\s*15000", txt), f"{f.name} devlog_error"
```

- [ ] **Step 2: Run it; fix any divergence it reports**

Run: `python -m pytest product/tests/test_budget_consistency.py -v`
Expected: It may FAIL on `test_profile_presets_match_canon` if any profile preset disagrees, or on the `<10k combined` checks until Phase 4. Fix each reported file to the canonical numbers (e.g., edit `product/profiles/*.yml` so all `changelog_error: 10000`, `devlog_error: 15000`). Re-run until green for Phase 1-2 scope; the `<10k combined` and project_instructions checks go green after Phase 4.

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_budget_consistency.py product/profiles/
git commit -m "test: budget consistency guard; align profile presets to canonical numbers"
```

---

## Phase 3 — Templates + frontmatter graph

### Cross-link graph (single definition — both representations derive from this)

| Doc | frontmatter `doc` | `related:` keys → paths |
|-----|------|------|
| CHANGELOG | CHANGELOG | devlog `./DEVLOG.md`, state `./STATE.md`, adr_index `./adr/README.md` |
| DEVLOG | DEVLOG | changelog `./CHANGELOG.md`, state `./STATE.md`, adr_index `./adr/README.md` |
| STATE | STATE | changelog `./CHANGELOG.md`, devlog `./DEVLOG.md`, adr_index `./adr/README.md` |
| ADR | ADR | changelog `../CHANGELOG.md`, devlog `../DEVLOG.md`, state `../STATE.md` |

### Task 6: Add frontmatter + fix prose links in templates

**Files:**
- Modify: `product/templates/CHANGELOG_template.md` (top), `DEVLOG_template.md` (top), `STATE_template.md` (top), `ADR_template.md` (top)

- [ ] **Step 1: CHANGELOG_template.md** — insert frontmatter as the very first lines (before `# Changelog`):

```markdown
---
doc: CHANGELOG
related:
  devlog: ./DEVLOG.md
  state: ./STATE.md
  adr_index: ./adr/README.md
---
```

Then in its `## Related Documents` section add the missing STATE and ADR links so prose matches frontmatter:

```markdown
📖 **[DEVLOG](./DEVLOG.md)** - Development narrative and decision rationale
📈 **[STATE](./STATE.md)** - Current project state (the now)
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records
```

- [ ] **Step 2: DEVLOG_template.md** — insert frontmatter first:

```markdown
---
doc: DEVLOG
related:
  changelog: ./CHANGELOG.md
  state: ./STATE.md
  adr_index: ./adr/README.md
---
```

Update its `## Related Documents` to include ADR:

```markdown
📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
📈 **[STATE](./STATE.md)** - Current project state (the now)
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records
```

- [ ] **Step 3: STATE_template.md** — insert frontmatter first:

```markdown
---
doc: STATE
related:
  changelog: ./CHANGELOG.md
  devlog: ./DEVLOG.md
  adr_index: ./adr/README.md
---
```

(Its prose `## Related Documents` already lists CHANGELOG/DEVLOG/ADRs — leave as is.)

- [ ] **Step 4: ADR_template.md** — insert frontmatter first (note `../` because ADRs live in `logs/adr/`):

```markdown
---
doc: ADR
related:
  changelog: ../CHANGELOG.md
  devlog: ../DEVLOG.md
  state: ../STATE.md
---
```

Add a `## Related Documents` section after the header block (it currently has none):

```markdown
## Related Documents

📊 **[CHANGELOG](../CHANGELOG.md)** · 📖 **[DEVLOG](../DEVLOG.md)** · 📈 **[STATE](../STATE.md)**
```

- [ ] **Step 5: Commit**

```bash
git add product/templates/CHANGELOG_template.md product/templates/DEVLOG_template.md product/templates/STATE_template.md product/templates/ADR_template.md
git commit -m "feat: add frontmatter related graph and symmetric prose links to templates"
```

### Task 7: Make STATE the single "now"; trim DEVLOG

**Files:**
- Modify: `product/templates/STATE_template.md` (add Current Context + Last Session blocks)
- Modify: `product/templates/DEVLOG_template.md` (remove Current Context + Last Session)

- [ ] **Step 1: STATE_template.md** — add a `## Current Context` block and a `## Last Session` block immediately after the `> **For AI Agents:**` note and before `## Active Work`:

```markdown
## Current Context

- **Project:** [Your Project Name]
- **Version:** v0.1.0-dev
- **Active Branch:** `main`
- **Phase:** Initial setup
- **Current Objectives:**
  - [ ] [First objective]
- **Known Risks/Blockers:** None yet

---

## Last Session

- **Done:** [What was completed]
- **In Progress:** [What's partially done]
- **Next:** [What to start next]
- **Branch:** `main` | **Last Commit:** `initial`
```

- [ ] **Step 2: DEVLOG_template.md** — delete the `## Current Context` section (lines ~16-34, from `## Current Context` through the `---` before `## Last Session`) and the `## Last Session` section (lines ~36-42). Update the `> **For AI Agents:**` note to:

```markdown
> **For AI Agents:** This file tells the story of *why* decisions were made. For current project state and session handoff, read **STATE.md** (the now). For technical details of *what* changed, see CHANGELOG.md.
```

- [ ] **Step 3: Run the frontmatter↔prose sync + STATE/DEVLOG tests** (defined in Task 8 below); for now verify manually:

Run: `grep -c "Current Context" product/templates/DEVLOG_template.md`
Expected: `0`
Run: `grep -c "Current Context" product/templates/STATE_template.md`
Expected: `1`

- [ ] **Step 4: Commit**

```bash
git add product/templates/STATE_template.md product/templates/DEVLOG_template.md
git commit -m "feat: STATE owns current context + last session; DEVLOG trimmed to narrative"
```

### Task 8: Frontmatter↔prose sync test

**Files:**
- Test: `product/tests/test_frontmatter_sync.py`

- [ ] **Step 1: Write the test**

```python
# product/tests/test_frontmatter_sync.py
import re
from pathlib import Path

T = Path(__file__).resolve().parents[1] / "templates"
EXPECTED = {
    "CHANGELOG_template.md": {"DEVLOG", "STATE", "ADRs"},
    "DEVLOG_template.md": {"CHANGELOG", "STATE", "ADRs"},
    "STATE_template.md": {"CHANGELOG", "DEVLOG", "ADRs"},
}


def _frontmatter(text):
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "missing frontmatter"
    return m.group(1)


def test_each_template_has_frontmatter():
    for name in list(EXPECTED) + ["ADR_template.md"]:
        text = (T / name).read_text(encoding="utf-8")
        fm = _frontmatter(text)
        assert "doc:" in fm and "related:" in fm


def test_prose_links_match_frontmatter_targets():
    # Every related: target path must also appear as a markdown link in prose.
    for name in EXPECTED:
        text = (T / name).read_text(encoding="utf-8")
        fm = _frontmatter(text)
        targets = re.findall(r":\s*(\./[^\s]+)", fm)
        body = text[text.index("---", 3) + 3:]
        for tgt in targets:
            assert f"({tgt})" in body, f"{name}: {tgt} missing from prose links"
```

- [ ] **Step 2: Run**

Run: `python -m pytest product/tests/test_frontmatter_sync.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_frontmatter_sync.py
git commit -m "test: frontmatter and prose link graphs must stay in sync"
```

---

## Phase 4 — Rule files (single pass per file: STATE repoint + paths + token diet)

> Do all three concerns in one editing pass per file to avoid churn. The directive-completeness gate (Task 12) protects against accidental rule loss during compression.

### Task 9: Capture rule directive checklist (the completeness gate input)

**Files:**
- Create: `docs/superpowers/specs/2026-05-27-rule-directives.md`

- [ ] **Step 1: Extract current directives**

Run: `grep -nE '^##|^###|MANDATORY|⛔|MUST' product/ai-rules/claude-code/log-file-maintenance.md`

- [ ] **Step 2: Write the checklist artifact** listing every section heading and directive currently present (one per line), e.g.:

```markdown
# Rule Directive Checklist (pre-compression snapshot)

## log-file-maintenance.md required sections/directives
- MANDATORY RULE - NO EXCEPTIONS
- BEFORE EVERY COMMIT (update CHANGELOG, update STATE if milestone, stage, checklist)
- AFTER EVERY COMMIT (self-checks, verification)
- FAILURE DETECTION & SELF-CORRECTION
- SESSION START (read STATE current context + last session, staleness check, acknowledge)
- SESSION END (write STATE last session; subagent skip clause)
- TOKEN SELF-ASSESSMENT (chars/4 heuristic, budgets)
- ENTRY VERBOSITY (compact, incident, standard; rubric; decision guide)
- CROSS-REFERENCES
- ARCHIVAL
- TEMPLATES (read-only)
- SUCCESS CRITERIA
```

- [ ] **Step 3: Commit**

```bash
git add docs/superpowers/specs/2026-05-27-rule-directives.md
git commit -m "docs: snapshot rule directives before token diet (completeness gate)"
```

### Task 10: Edit claude-code rule files (STATE repoint + paths + compress)

**Files:**
- Modify: `product/ai-rules/claude-code/log-file-maintenance.md`
- Modify: `product/ai-rules/claude-code/project_instructions.md`
- Modify: `product/ai-rules/claude-code/status-update.md`
- Modify: `product/ai-rules/claude-code/update-planning-docs.md`

- [ ] **Step 1: log-file-maintenance.md — SESSION START** — replace the SESSION START steps so they read STATE, not DEVLOG:

```markdown
## 🔄 SESSION START

**At start of EVERY session:**
1. Read `.logfile-config.yml` → `paths.state` (fallback `logs/STATE.md`)
2. Read STATE → "Current Context" and "Last Session"
3. **Staleness check:** if STATE `Last Updated` is >7 days old, update Current Context first; tell the user "Current Context is X days old. Updating before proceeding."
4. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"
```

- [ ] **Step 2: log-file-maintenance.md — SESSION END** — repoint to STATE:

```markdown
## 🔚 SESSION END

**⚠️ Multi-agent:** subagents/teammates skip this — only the lead writes handoffs.

**Before ending a session:**
1. Update STATE → "Last Session" (overwrite previous), 3 bullets max, <150 tokens:
   `Done / In Progress / Next / Branch + Last Commit`
2. Stage and commit with other changes.
```

- [ ] **Step 3: log-file-maintenance.md — BEFORE EVERY COMMIT** — change "Update DEVLOG.md (if milestone)" path reference to read from config, and change step 2's "Current Context" wording to point at STATE. Replace the path-bearing lines so all read `.logfile-config.yml` → `paths.*` with `logs/` fallback. (CHANGELOG → `paths.changelog`, DEVLOG → `paths.devlog`, STATE → `paths.state`.)

- [ ] **Step 4: Compress** the file. Apply wording compression across all sections (merge restated preamble, tighten bullet prose) targeting a meaningful reduction. Do NOT remove any heading/directive from the Task 9 checklist.

- [ ] **Step 5: project_instructions.md** — apply these exact changes:
  - Token efficiency: replace "Keep CHANGELOG + DEVLOG + STATE under 10,000 tokens combined" with "CHANGELOG <10k, DEVLOG <15k, combined <25k tokens; STATE <500 tokens."
  - Default paths: replace the `docs/planning/...` / `docs/STATE.md` / `docs/adr/` defaults with `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/STATE.md`, `logs/adr/`, and instruct "read `.logfile-config.yml` → `paths`, fall back to `logs/`."
  - Five-document list: change STATE's line to "**STATE** — What's happening now (the single source for current state + session handoff)" and DEVLOG's to "**DEVLOG** — Why it changed (narrative only)."
  - Validation quick-reference path: change `./log-file-genius/scripts/validate-log-files.sh` to match the installed `scripts/validate-log-files.sh`.

- [ ] **Step 6: status-update.md** — replace the hardcoded `docs/planning/DEVLOG.md`, `docs/planning/CHANGELOG.md`, `docs/adr/README.md` references in "Step 1: Read These Files" with: "Read paths from `.logfile-config.yml` → `paths` (fallback `logs/`): STATE (current context + last session), CHANGELOG Unreleased, recent ADRs." Pull current state from **STATE**, not DEVLOG Current Context.

- [ ] **Step 7: update-planning-docs.md** — replace all `docs/planning/CHANGELOG.md` / `docs/planning/DEVLOG.md` / `docs/adr/` literals with config-driven paths (fallback `logs/`). In the menu, change "Update DEVLOG Current Context" to "Update STATE (Current Context + Last Session)".

- [ ] **Step 8: Verify directive completeness**

Run: `python -m pytest product/tests/test_rule_directives.py -v` (defined in Task 12)
Expected: PASS (after Task 12 exists; if running before, do the manual grep from Task 9 Step 1 and confirm every heading still present).

- [ ] **Step 9: Commit**

```bash
git add product/ai-rules/claude-code/
git commit -m "refactor(claude-code rules): STATE-based now, config paths, token diet"
```

### Task 11: Edit augment rule files (mirror of Task 10)

**Files:**
- Modify: `product/ai-rules/augment/log-file-maintenance.md`
- Modify: `product/ai-rules/augment/status-update.md`
- Modify: `product/ai-rules/augment/update-planning-docs.md`

> The augment `log-file-maintenance.md` is structurally identical to claude-code's (they diverged only in the incident-format merge, now resolved). Apply the **same** SESSION START, SESSION END, BEFORE EVERY COMMIT, and compression edits from Task 10 Steps 1-4. The augment pack has no `project_instructions.md`.

- [ ] **Step 1:** Apply Task 10 Step 1 (SESSION START → STATE) to `augment/log-file-maintenance.md`.
- [ ] **Step 2:** Apply Task 10 Step 2 (SESSION END → STATE).
- [ ] **Step 3:** Apply Task 10 Step 3 (config-driven paths in BEFORE EVERY COMMIT).
- [ ] **Step 4:** Apply Task 10 Step 4 (compression; no directive loss).
- [ ] **Step 5:** Apply Task 10 Step 6 to `augment/status-update.md` (config paths, STATE for current state).
- [ ] **Step 6:** Apply Task 10 Step 7 to `augment/update-planning-docs.md` (config paths, STATE menu item).
- [ ] **Step 7: Commit**

```bash
git add product/ai-rules/augment/
git commit -m "refactor(augment rules): STATE-based now, config paths, token diet"
```

### Task 12: Rule-directive completeness test

**Files:**
- Test: `product/tests/test_rule_directives.py`

- [ ] **Step 1: Write the test**

```python
# product/tests/test_rule_directives.py
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RULES = [
    ROOT / "product/ai-rules/claude-code/log-file-maintenance.md",
    ROOT / "product/ai-rules/augment/log-file-maintenance.md",
]
REQUIRED_HEADINGS = [
    "MANDATORY RULE",
    "BEFORE EVERY COMMIT",
    "AFTER EVERY COMMIT",
    "FAILURE DETECTION",
    "SESSION START",
    "SESSION END",
    "TOKEN SELF-ASSESSMENT",
    "ENTRY VERBOSITY",
    "CROSS-REFERENCES",
    "ARCHIVAL",
    "TEMPLATES",
    "SUCCESS CRITERIA",
]


def test_no_directive_dropped_during_compression():
    for rule in RULES:
        txt = rule.read_text(encoding="utf-8")
        for heading in REQUIRED_HEADINGS:
            assert heading in txt, f"{rule.name} missing '{heading}'"


def test_session_start_reads_state_not_devlog_current_context():
    for rule in RULES:
        txt = rule.read_text(encoding="utf-8")
        i = txt.index("SESSION START")
        j = txt.index("SESSION END")
        section = txt[i:j]
        assert "STATE" in section
        assert "DEVLOG Current Context" not in section


def test_no_hardcoded_docs_planning_paths():
    for d in ["claude-code", "augment"]:
        for f in (ROOT / "product/ai-rules" / d).glob("*.md"):
            assert "docs/planning/" not in f.read_text(encoding="utf-8"), f.name
```

- [ ] **Step 2: Run**

Run: `python -m pytest product/tests/test_rule_directives.py -v`
Expected: PASS

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_rule_directives.py
git commit -m "test: rule directive completeness + STATE repoint guards"
```

---

## Phase 5 — Installer config block, kill starter-packs, fix update, README

### Task 13: Installer writes paths + token_targets (bash + PowerShell)

**Files:**
- Modify: `product/scripts/install.sh:364-380` (config heredoc)
- Modify: `product/scripts/install.ps1:353-369` (config here-string)

- [ ] **Step 1: install.sh** — replace the `cat > .logfile-config.yml` heredoc body so it appends the two blocks:

```bash
cat > .logfile-config.yml << EOF
# Log File Genius Configuration
# All log files are in /logs/ folder (standard structure)

log_file_genius_version: "$VERSION"
profile: $PROFILE
ai_assistant: $AI_ASSISTANT

paths:
  changelog: logs/CHANGELOG.md
  devlog: logs/DEVLOG.md
  state: logs/STATE.md
  adr_dir: logs/adr/

token_targets:
  changelog: 10000
  devlog: 15000
  combined: 25000
  state: 500

# Presets and customization: .log-file-genius/product/profiles/*.yml
EOF
```

- [ ] **Step 2: install.ps1** — replace the `$configContent = @"..."@` here-string with the same content:

```powershell
$configContent = @"
# Log File Genius Configuration
# All log files are in /logs/ folder (standard structure)

log_file_genius_version: "$VERSION"
profile: $Profile
ai_assistant: $AiAssistant

paths:
  changelog: logs/CHANGELOG.md
  devlog: logs/DEVLOG.md
  state: logs/STATE.md
  adr_dir: logs/adr/

token_targets:
  changelog: 10000
  devlog: 15000
  combined: 25000
  state: 500

# Presets and customization: .log-file-genius/product/profiles/*.yml
"@
```

- [ ] **Step 3: Smoke check (manual until Task 17)**

Run: `bash -c 'cd $(mktemp -d) && mkdir .claude && bash '"$PWD"'/product/scripts/install.sh --profile solo-developer --ai-assistant claude-code --force && grep -A4 "^paths:" .logfile-config.yml'`
Expected: prints the `paths:` block.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/install.sh product/scripts/install.ps1
git commit -m "feat: installer writes paths and token_targets config blocks"
```

### Task 14: Repoint update scripts to ai-rules; update full claude rules dir; delete starter-packs

**Files:**
- Modify: `product/scripts/update.sh:144-170`
- Modify: `product/scripts/update.ps1:156-191`
- Modify: `product/scripts/check-ai-rules.py:202-204` (comment)
- Delete: `product/starter-packs/**`

- [ ] **Step 1: update.sh** — change the rules source and make claude-code update the whole `.claude/rules/` dir (not just project_instructions). Replace lines ~144-170:

```bash
    RULES_SRC="$SOURCE_ROOT/product/ai-rules/$AI_ASSISTANT"

    if [[ "$AI_ASSISTANT" == "augment" ]]; then
        for rule_file in "$RULES_SRC/"*.md; do
            [[ -f "$rule_file" ]] || continue
            rule_name=$(basename "$rule_file")
            dest_file="$PROJECT_ROOT/.augment/rules/$rule_name"
            if prompt_update "Augment rule: $rule_name" "$rule_file" "$dest_file"; then
                mkdir -p "$PROJECT_ROOT/.augment/rules"
                cp "$rule_file" "$dest_file"
                print_success "Updated: $rule_name"
            fi
        done
    elif [[ "$AI_ASSISTANT" == "claude-code" ]]; then
        for rule_file in "$RULES_SRC/"*.md; do
            [[ -f "$rule_file" ]] || continue
            rule_name=$(basename "$rule_file")
            if [[ "$rule_name" == "project_instructions.md" ]]; then
                dest_file="$PROJECT_ROOT/.claude/project_instructions.md"
            else
                dest_file="$PROJECT_ROOT/.claude/rules/$rule_name"
            fi
            if prompt_update "Claude rule: $rule_name" "$rule_file" "$dest_file"; then
                mkdir -p "$(dirname "$dest_file")"
                cp "$rule_file" "$dest_file"
                print_success "Updated: $rule_name"
            fi
        done
    fi
```

- [ ] **Step 2: update.ps1** — mirror it. Replace lines ~156-191:

```powershell
    $RulesSrc = Join-Path $SourceRoot "product\ai-rules\$AiAssistant"

    if ($AiAssistant -eq "augment") {
        Get-ChildItem -Path $RulesSrc -Filter "*.md" | ForEach-Object {
            $ruleName = $_.Name
            $destFile = Join-Path $ProjectRoot ".augment\rules\$ruleName"
            if (Prompt-Update "Augment rule: $ruleName" $_.FullName $destFile) {
                $destDir = Split-Path -Parent $destFile
                if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                Copy-Item -Path $_.FullName -Destination $destFile -Force
                Print-Success "Updated: $ruleName"
            }
        }
    } elseif ($AiAssistant -eq "claude-code") {
        Get-ChildItem -Path $RulesSrc -Filter "*.md" | ForEach-Object {
            $ruleName = $_.Name
            if ($ruleName -eq "project_instructions.md") {
                $destFile = Join-Path $ProjectRoot ".claude\project_instructions.md"
            } else {
                $destFile = Join-Path $ProjectRoot ".claude\rules\$ruleName"
            }
            if (Prompt-Update "Claude rule: $ruleName" $_.FullName $destFile) {
                $destDir = Split-Path -Parent $destFile
                if (-not (Test-Path $destDir)) { New-Item -ItemType Directory -Path $destDir -Force | Out-Null }
                Copy-Item -Path $_.FullName -Destination $destFile -Force
                Print-Success "Updated: $ruleName"
            }
        }
    }
```

- [ ] **Step 3: check-ai-rules.py** — update the now-stale dedup comment (lines ~202-204) to remove the starter-packs reference:

```python
    # Deduplicate by filename - if the same filename appears in multiple dirs,
    # keep only the first occurrence.
```

- [ ] **Step 4: Delete starter-packs**

```bash
git rm -r product/starter-packs
```

- [ ] **Step 5: Verify no references remain**

Run: `grep -rn "starter-packs" product/ README.md INSTALL.md`
Expected: no output.

- [ ] **Step 6: Commit**

```bash
git add product/scripts/update.sh product/scripts/update.ps1 product/scripts/check-ai-rules.py
git commit -m "fix: update scripts source rules from ai-rules; remove starter-packs"
```

### Task 15: README + pre-commit claim corrections

**Files:**
- Modify: `README.md:72` (frontmatter claim), `README.md:76` (safety claim)
- Modify: `product/scripts/pre-commit:14` (remove `--with-hooks` reference)

- [ ] **Step 1: README.md line 76** — replace the Safety bullet to match reality (these are opt-in, not installed by default):

```markdown
- **🔒 Safety Tools Available:** Optional secret detection, log validation, and a pre-commit hook you can enable to catch problems before they hit the repo. Run them manually or wire the hook into `.git/hooks/`.
```

- [ ] **Step 2: README.md line 72** — the frontmatter claim is now TRUE after Phase 3; leave the wording but verify it's accurate:

Run: `grep -n "frontmatter" README.md`
Expected: line ~72 claim stands; no edit needed unless wording overreaches.

- [ ] **Step 3: pre-commit header** — remove the `--with-hooks` line from the install comment (lines ~13-15), since that flag does not exist. Replace with:

```bash
# Installation:
#   cp .log-file-genius/product/scripts/pre-commit .git/hooks/pre-commit
#   chmod +x .git/hooks/pre-commit
```

- [ ] **Step 4: Commit**

```bash
git add README.md product/scripts/pre-commit
git commit -m "docs: correct safety claims; remove nonexistent --with-hooks reference"
```

### Task 16: log_file_how_to.md — STATE role + budgets

**Files:**
- Modify: `product/docs/log_file_how_to.md`

- [ ] **Step 1:** Find STATE/DEVLOG role descriptions and the token-budget figures:

Run: `grep -nE "STATE|Current Context|combined|10,000|25,000|five-document|five document" product/docs/log_file_how_to.md`

- [ ] **Step 2:** Update so STATE is described as the single home for current state + session handoff, DEVLOG as narrative-only, and budgets read CHANGELOG <10k / DEVLOG <15k / combined <25k / STATE <500. Apply edits to each matched location.

- [ ] **Step 3: Commit**

```bash
git add product/docs/log_file_how_to.md
git commit -m "docs: align how-to with STATE-as-now and canonical budgets"
```

---

## Phase 6 — Brownfield migration + cross-platform smoke test + re-dogfood

### Task 17: Brownfield STATE migration in update scripts

**Files:**
- Modify: `product/scripts/update.sh` (add migration function, call after rules update)
- Modify: `product/scripts/update.ps1` (mirror)
- Test: `product/tests/test_brownfield_migration.sh`

- [ ] **Step 1: Write the failing test**

```bash
# product/tests/test_brownfield_migration.sh
#!/usr/bin/env bash
set -euo pipefail
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$TMP"; mkdir -p logs
cat > logs/DEVLOG.md <<'EOF'
# Development Log
## Current Context
- Version: v1.2.3
## Last Session
- Done: stuff
## Daily Log
### 2026-01-01: x
EOF
# Run only the migration function (sourced) to keep the test hermetic.
LFG_MIGRATE_ONLY=1 bash "$OLDPWD/product/scripts/update.sh" || true
test -f logs/STATE.md || { echo "STATE.md not created"; exit 1; }
grep -q "v1.2.3" logs/STATE.md || { echo "Current Context not migrated"; exit 1; }
echo "PASS"
```

- [ ] **Step 2: Run to verify it fails**

Run: `bash product/tests/test_brownfield_migration.sh`
Expected: FAIL — no migration logic; STATE.md not created.

- [ ] **Step 3: Add migration to update.sh** — near the top after helper functions, add:

```bash
migrate_devlog_to_state() {
    local devlog="logs/DEVLOG.md"
    local state="logs/STATE.md"
    [ -f "$devlog" ] || return 0
    if ! grep -q "## Current Context" "$devlog"; then return 0; fi
    if [ -f "$state" ]; then
        print_warning "DEVLOG has a legacy Current Context, but STATE.md already exists."
        print_info "Review and move it manually if needed; leaving files unchanged."
        return 0
    fi
    print_info "Migrating DEVLOG Current Context / Last Session into new STATE.md"
    {
        echo "# Current State"
        echo ""
        awk '/^## Current Context/{f=1} /^## Daily Log/{f=0} f' "$devlog"
    } > "$state"
    print_success "Created logs/STATE.md from legacy DEVLOG sections (review it)."
}
```

Near the top of the main flow add an early hook so the test can run it in isolation, and call it during normal runs:

```bash
if [ "${LFG_MIGRATE_ONLY:-0}" = "1" ]; then
    migrate_devlog_to_state
    exit 0
fi
```

Place a normal call to `migrate_devlog_to_state` after the AI-rules update block.

- [ ] **Step 4: Run to verify it passes**

Run: `bash product/tests/test_brownfield_migration.sh`
Expected: `PASS`

- [ ] **Step 5: Mirror in update.ps1** — add an equivalent `Migrate-DevlogToState` function (same logic: if `logs/DEVLOG.md` contains `## Current Context` and `logs/STATE.md` does not exist, write a new STATE.md containing the lines from `## Current Context` up to `## Daily Log`), guarded by `$env:LFG_MIGRATE_ONLY -eq "1"` for isolated runs, and called after the rules update.

- [ ] **Step 6: Commit**

```bash
git add product/scripts/update.sh product/scripts/update.ps1 product/tests/test_brownfield_migration.sh
git commit -m "feat: update scripts migrate legacy DEVLOG context into STATE.md"
```

### Task 18: Cross-platform installer smoke test

**Files:**
- Test: `product/tests/smoke_install.sh`, `product/tests/smoke_install.ps1`

- [ ] **Step 1: Write smoke_install.sh**

```bash
# product/tests/smoke_install.sh
#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$TMP"; mkdir .claude
# Simulate the submodule layout the scripts expect.
mkdir -p .log-file-genius && cp -r "$REPO/product" .log-file-genius/
( cd .log-file-genius && git init -q && git add -A && git commit -qm seed )

bash "$REPO/product/scripts/install.sh" --profile solo-developer --ai-assistant claude-code --force >/dev/null

for f in logs/CHANGELOG.md logs/DEVLOG.md logs/STATE.md .logfile-config.yml \
         .claude/rules/log-file-maintenance.md; do
    test -f "$f" || { echo "missing $f"; exit 1; }
done
test -d logs/adr || { echo "missing logs/adr"; exit 1; }
grep -q "^paths:" .logfile-config.yml || { echo "no paths block"; exit 1; }
grep -q "^token_targets:" .logfile-config.yml || { echo "no token_targets"; exit 1; }
head -1 logs/CHANGELOG.md | grep -q '^---$' || { echo "no frontmatter"; exit 1; }

# install==update parity, checked deterministically (update.sh needs a git remote,
# so we verify the property directly): the installed rule must equal the canonical
# ai-rules source, and update.sh must source from ai-rules (not starter-packs).
diff -q .claude/rules/log-file-maintenance.md \
    "$REPO/product/ai-rules/claude-code/log-file-maintenance.md" \
    || { echo "installed rule != canonical ai-rules source"; exit 1; }
grep -q 'product/ai-rules/\$AI_ASSISTANT' "$REPO/product/scripts/update.sh" \
    || { echo "update.sh does not source from ai-rules"; exit 1; }
grep -q 'starter-packs' "$REPO/product/scripts/update.sh" \
    && { echo "update.sh still references starter-packs"; exit 1; } || true
echo "PASS (bash)"
```

- [ ] **Step 2: Run**

Run: `bash product/tests/smoke_install.sh`
Expected: `PASS (bash)`

- [ ] **Step 3: Write smoke_install.ps1** — equivalent assertions using `pwsh`/`install.ps1`/`update.ps1`: temp dir, `.claude` present, run installer with `-Profile solo-developer -AiAssistant claude-code -Force`, assert the same files, `paths:`/`token_targets:` blocks, frontmatter first line, and rule-file identity before/after update.

- [ ] **Step 4: Run**

Run: `pwsh product/tests/smoke_install.ps1`
Expected: `PASS (powershell)`

- [ ] **Step 5: Commit**

```bash
git add product/tests/smoke_install.sh product/tests/smoke_install.ps1
git commit -m "test: cross-platform installer smoke test with install==update parity"
```

### Task 19: lint-logs.py — STATE validation, drop DEVLOG Current Context requirement

**Files:**
- Modify: `product/scripts/lint-logs.py:406-450` (`validate_devlog`), add `validate_state`
- Test: extend `product/tests/test_lint_logs_config.py`

- [ ] **Step 1: Write failing test** (append to `test_lint_logs_config.py`):

```python
def test_devlog_no_longer_requires_current_context(tmp_path):
    cfg = tmp_path / ".logfile-config.yml"
    cfg.write_text("paths:\n  devlog: D.md\n  state: S.md\n", encoding="utf-8")
    (tmp_path / "D.md").write_text("# Development Log\n## Daily Log\n### 2026-01-01: x\n", encoding="utf-8")
    import os
    os.chdir(tmp_path)
    linter = lint_logs.LogLinter(config_path=str(cfg))
    result = linter.validate_devlog()
    assert all("Current Context" not in i.message for i in result.issues)
```

- [ ] **Step 2: Run to verify it fails**

Run: `python -m pytest product/tests/test_lint_logs_config.py::test_devlog_no_longer_requires_current_context -v`
Expected: FAIL — current `validate_devlog` errors on missing "Current Context."

- [ ] **Step 3: Edit `validate_devlog`** — remove the `has_current_context` requirement block (lines ~418-431): delete the `has_current_context` tracking and the `if not has_current_context: result.add_issue('error', ...)`. Keep the Daily Log check and token check. Add `state_path` to `__init__` (read `paths.state`, default `logs/STATE.md`) and a minimal `validate_state` that warns if STATE missing and errors if STATE exceeds `token_targets.state` (default 500). Add `validate_state` to `run_all_validations`.

- [ ] **Step 4: Run to verify it passes**

Run: `python -m pytest product/tests/test_lint_logs_config.py -v`
Expected: PASS

- [ ] **Step 5: Commit**

```bash
git add product/scripts/lint-logs.py product/tests/test_lint_logs_config.py
git commit -m "feat: lint-logs validates STATE; DEVLOG no longer requires Current Context"
```

### Task 20: Re-dogfood this repository

**Files:**
- Create: `STATE.md` (repo root)
- Modify: `logs/DEVLOG.md`

- [ ] **Step 1:** Create root `STATE.md` from the new STATE template, populated with this repo's real current state (version, branch `development`, current phase = "Spec 1 cleanup implementation", objectives). Move the stale "Current Context (Source of Truth)" content (dated 2026-02-01) out of `logs/DEVLOG.md` into STATE's Current Context, refreshed to today.

- [ ] **Step 2:** Remove the "Current Context (Source of Truth)" and any "Last Session" section from `logs/DEVLOG.md`, leaving the narrative Daily Log + Archive. Add frontmatter + STATE link to `logs/DEVLOG.md` matching the template.

- [ ] **Step 3: Validate the dogfood**

Run: `python product/scripts/lint-logs.py --skip-self-test`
Expected: no errors about missing Current Context; STATE validated.

- [ ] **Step 4: Commit**

```bash
git add STATE.md logs/DEVLOG.md
git commit -m "chore: re-dogfood — STATE.md owns current context, DEVLOG trimmed"
```

---

## Final verification

- [ ] **Run the full test suite**

Run: `python -m pytest product/tests/ -v && bash product/tests/test_validate_sh.sh && bash product/tests/test_brownfield_migration.sh && bash product/tests/smoke_install.sh`
Expected: all PASS.

- [ ] **Run PowerShell tests** (on Windows/pwsh): `pwsh product/tests/test_validate_ps1.ps1; pwsh product/tests/smoke_install.ps1`
Expected: all PASS.

- [ ] **Consistency greps**

Run: `grep -rn "starter-packs\|docs/planning/\|import yaml\|--with-hooks" product/ README.md INSTALL.md`
Expected: no output.

- [ ] **Budget consistency**

Run: `python -m pytest product/tests/test_budget_consistency.py -v`
Expected: PASS.

---

## Spec coverage map

- Spec A (kill starter-packs, repoint update, README) → Tasks 14, 15
- Spec B (canonical budgets, single source) → Tasks 2, 3, 4, 5, 13
- Spec C (STATE Option 3) → Tasks 6, 7, 10, 11, 19, 20
- Spec D (paths) → Tasks 3, 4, 10, 11, 13
- Spec E (token diet) → Tasks 9, 10, 11, 12
- Spec F (frontmatter) → Tasks 6, 8
- Spec G (migration + re-dogfood) → Tasks 17, 20
- Bonus (PyYAML) → Tasks 1, 2
- Testing (cross-platform, all guards) → Tasks 5, 8, 12, 17, 18
