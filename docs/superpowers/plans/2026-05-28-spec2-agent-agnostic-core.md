# LFG Spec 2 — Agent-Agnostic Core Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Collapse per-tool rule duplication into one canonical fragment set; generate a neutral `AGENTS.md` entry point any agent can read; ship a small deterministic-command surface (`lfg generate`, `lfg prime`, `lfg promote`) and a real subagent protocol (identity signal + staged writes).

**Architecture:** Fragments under `product/rules/` are canonical. `lfg generate` concatenates them into `product/AGENTS.md` (committed; one generated file, gated by CI). Per-tool rule directories are generated at *install time* on the user's machine — no committed `install-payload/`. Subagents are identified by an `LFG_SUBAGENT_PRIME` header in their prime digest and write to `.lfg/staged/<id>/` for the lead to promote.

**Tech Stack:** Python 3.11+ (stdlib only — no PyYAML, no new deps), Bash, PowerShell, Markdown with YAML frontmatter, pytest.

**Source spec:** `docs/superpowers/specs/2026-05-28-spec2-agent-agnostic-core-design.md`

---

## Design decisions baked in (from spec; flag if you disagree)

1. **`product/rules/` is canonical.** Old `product/ai-rules/{augment,claude-code}/` directories are deleted at the end.
2. **Fragment frontmatter** carries `fragment`, `order` (int), `targets` (subset of `{agents_md, claude_rules, augment_rules}`), `summary`. Fragment frontmatter is comma-separated for `targets` to fit the stdlib parser (`targets: agents_md, claude_rules, augment_rules`).
3. **Only `AGENTS.md` is a committed generated artifact.** Per-tool dirs are install-time only.
4. **`lfg generate --check`** is the CI gate; `lfg generate` writes.
5. **`lfg prime`** has `--n N` (default 5) and `--json`. No `--topic`.
6. **`lfg promote <id>`** reads `.lfg/staged/<id>/{changelog,devlog}.md`, appends to canonical, writes `.lfg/promoted.log`, removes the staged dir.
7. **Generator output is LF + UTF-8 (no BOM) + single trailing newline.** Both writer and asserter enforce this.
8. **3000-token AGENTS.md gate is a hard test**, not a soft target.

## Canonical token budgets and constants (single source — match exactly)

- AGENTS.md token budget: **3000** (chars/4 heuristic).
- `lfg prime` default `--n`: **5**.
- `LFG_SUBAGENT_PRIME` marker: exact literal at line 1 of `lfg prime` output.

---

## File structure

- `product/rules/*.md` — **new** canonical fragments (deduplicated from `product/ai-rules/{augment,claude-code}/`).
- `product/AGENTS.md` — **new**, generated, committed.
- `product/install-templates/claude/project_instructions.md.tmpl` — **new**, rendered at install time.
- `product/scripts/generator.py` — **new**, generator logic. Imported by `lfg.py`.
- `product/scripts/primer.py` — **new**, prime-digest logic. Imported by `lfg.py`.
- `product/scripts/promoter.py` — **new**, promote logic. Imported by `lfg.py`.
- `product/scripts/lfg.py` — **modify**, add `generate`, `prime`, `promote` subcommands.
- `product/scripts/install.sh` / `install.ps1` — **modify**, generate per-tool dirs from fragments at install time; render templates; drop AGENTS.md at project root.
- `product/scripts/update.sh` / `update.ps1` — **modify**, mirror.
- `product/ai-rules/` — **delete** at end.
- `product/docs/log_file_how_to.md` — **modify**, document the canonical-fragments model.
- `CONTRIBUTING.md` — **modify**, acknowledge Python build-time dep + pre-commit hook.
- `.github/workflows/test-installer.yml` (or equivalent) — **modify**, add `lfg generate --check` job.
- `product/tests/` — new tests per the test plan.

---

## Phase 1 — Canonical fragments + frontmatter

### Task 1: Move and dedupe fragments to `product/rules/`

**Files:**
- Create: `product/rules/log-file-maintenance.md`
- Create: `product/rules/status-update.md`
- Create: `product/rules/update-planning-docs.md`
- Create: `product/rules/token-usage.md`

The `product/ai-rules/{augment,claude-code}/` directories currently hold the same content twice (post-Spec 1 they're aligned). Pick the `claude-code/` set as the canonical source — it has one extra file (`project_instructions.md`) which becomes the template in Task 19.

- [ ] **Step 1: Move (don't copy) the fragments**

```bash
mkdir -p product/rules
git mv product/ai-rules/claude-code/log-file-maintenance.md product/rules/log-file-maintenance.md
git mv product/ai-rules/claude-code/status-update.md       product/rules/status-update.md
git mv product/ai-rules/claude-code/update-planning-docs.md product/rules/update-planning-docs.md
git mv product/ai-rules/claude-code/token-usage.md         product/rules/token-usage.md
```

Note: `project_instructions.md` stays under `product/ai-rules/claude-code/` for now (handled in Task 19).

- [ ] **Step 2: Delete the augment duplicates**

```bash
git rm product/ai-rules/augment/log-file-maintenance.md \
       product/ai-rules/augment/status-update.md \
       product/ai-rules/augment/update-planning-docs.md \
       product/ai-rules/augment/token-usage.md
```

- [ ] **Step 3: Verify the move**

Run: `ls product/rules/ && ls product/ai-rules/`
Expected: `product/rules/` has 4 files; `product/ai-rules/` contains only `claude-code/project_instructions.md` (and the README).

- [ ] **Step 4: Commit**

```bash
git commit -m "refactor: move canonical fragments to product/rules/ (dedupe per-tool copies)"
```

### Task 2: Add YAML frontmatter to each fragment

**Files:**
- Modify: `product/rules/log-file-maintenance.md` (prepend frontmatter)
- Modify: `product/rules/status-update.md` (prepend frontmatter)
- Modify: `product/rules/update-planning-docs.md` (prepend frontmatter)
- Modify: `product/rules/token-usage.md` (prepend frontmatter)

- [ ] **Step 1:** Prepend the following to `product/rules/log-file-maintenance.md` as the very first lines (before the existing `# log-file-maintenance` heading):

```markdown
---
fragment: log-file-maintenance
order: 10
targets: agents_md, claude_rules, augment_rules
summary: Always-active rules for log maintenance (commits, sessions, archival, formats).
---

```

- [ ] **Step 2:** Prepend to `product/rules/status-update.md`:

```markdown
---
fragment: status-update
order: 20
targets: agents_md, claude_rules, augment_rules
summary: "@status update" command — concise project state summary.
---

```

- [ ] **Step 3:** Prepend to `product/rules/update-planning-docs.md`:

```markdown
---
fragment: update-planning-docs
order: 30
targets: agents_md, claude_rules, augment_rules
summary: "@update planning docs" command — guided CHANGELOG/DEVLOG/ADR/STATE updates.
---

```

- [ ] **Step 4:** Prepend to `product/rules/token-usage.md`:

```markdown
---
fragment: token-usage
order: 40
targets: agents_md, claude_rules, augment_rules
summary: "@token usage" command — report context-window usage and component token costs.
---

```

(`token-usage.md` already has Augment-style `type: "manual"` frontmatter — keep it; the parser supports multiple keys.)

Wait — the file already has frontmatter. Inspect first:

```bash
head -5 product/rules/token-usage.md
```

If it starts with `---` … `type: "manual"` … `---`, merge: insert the new keys *inside* the existing frontmatter block (between the opening `---` and closing `---`), preserving `type: "manual"`. Do not produce two consecutive frontmatter blocks.

- [ ] **Step 5: Commit**

```bash
git add product/rules/
git commit -m "feat(rules): add canonical YAML frontmatter (fragment/order/targets/summary)"
```

### Task 3: Content scrub — remove per-tool path literals from fragments

**Files:**
- Modify: `product/rules/log-file-maintenance.md`
- Modify: `product/rules/status-update.md`
- Modify: `product/rules/update-planning-docs.md`
- Modify: `product/rules/token-usage.md`

The fragments must not contain literal `.claude/` or `.augment/` paths (per spec §Fragment content rules). Spec 1 already converted most path references to config-driven; this task catches any remaining ones.

- [ ] **Step 1: Audit**

```bash
grep -nE '\.(claude|augment)/' product/rules/*.md | grep -v '```'  # exclude code-block examples
```

If output is empty, skip to Step 3.

- [ ] **Step 2: Replace any remaining literals**

For each occurrence, replace with either `.logfile-config.yml → paths.<key>` references (with `logs/<key>` fallback) or a tool-neutral phrasing ("your AI assistant's rules directory"). Apply edits inline.

- [ ] **Step 3: Verify**

```bash
grep -nE '\.(claude|augment)/' product/rules/*.md | grep -v '```' && echo "STILL HAS LITERALS" || echo "clean"
```

Expected: `clean`.

- [ ] **Step 4: Commit (only if changes made; otherwise skip)**

```bash
git add product/rules/
git commit -m "fix(rules): scrub remaining per-tool path literals in canonical fragments"
```

### Task 4: Frontmatter schema + content-scrub tests

**Files:**
- Create: `product/tests/test_fragments.py`

- [ ] **Step 1: Write the tests**

```python
# product/tests/test_fragments.py
import re
from pathlib import Path
import pytest

ROOT = Path(__file__).resolve().parents[2]
RULES = ROOT / "product/rules"
ALLOWED_TARGETS = {"agents_md", "claude_rules", "augment_rules"}


def _frontmatter(path):
    text = path.read_text(encoding="utf-8")
    assert text.startswith("---\n"), f"{path.name}: missing opening frontmatter delimiter"
    end = text.find("\n---\n", 4)
    assert end != -1, f"{path.name}: unterminated frontmatter"
    return text[4:end]


def _parse_fm(text):
    fm = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert ":" in line, f"bad frontmatter line: {line!r}"
        k, _, v = line.partition(":")
        fm[k.strip()] = v.strip()
    return fm


@pytest.mark.parametrize("path", list(RULES.glob("*.md")))
def test_fragment_has_required_frontmatter_keys(path):
    fm = _parse_fm(_frontmatter(path))
    assert "fragment" in fm, f"{path.name}: missing 'fragment'"
    assert "order" in fm, f"{path.name}: missing 'order'"
    assert "targets" in fm, f"{path.name}: missing 'targets'"
    assert "summary" in fm, f"{path.name}: missing 'summary'"
    # order is an integer
    int(fm["order"])
    # targets is a subset of the allowed set
    targets = {t.strip() for t in fm["targets"].lstrip("[").rstrip("]").split(",") if t.strip()}
    assert targets <= ALLOWED_TARGETS, f"{path.name}: unknown targets {targets - ALLOWED_TARGETS}"


def test_no_per_tool_path_literals_in_fragments():
    """Fragments must reference paths via .logfile-config.yml, not literal
    .claude/ or .augment/ strings. Code-block examples (between triple
    backticks) are allowed."""
    offenders = []
    pattern = re.compile(r"\.(claude|augment)/")
    for path in RULES.glob("*.md"):
        in_code = False
        for i, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if line.strip().startswith("```"):
                in_code = not in_code
                continue
            if in_code:
                continue
            if pattern.search(line):
                offenders.append(f"{path.name}:{i}: {line.strip()}")
    assert not offenders, "per-tool paths in fragments:\n  " + "\n  ".join(offenders)


def test_fragment_orders_unique():
    orders = []
    for path in RULES.glob("*.md"):
        fm = _parse_fm(_frontmatter(path))
        orders.append(int(fm["order"]))
    assert len(orders) == len(set(orders)), f"duplicate order values: {orders}"
```

- [ ] **Step 2: Run**

```bash
python -m pytest product/tests/test_fragments.py -v
```

Expected: all pass (4 fragments + 3 tests = 6 parametrized pass + 2 standalone pass = roughly 6 PASS depending on parametrization). If any fail, fix the fragment frontmatter / content.

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_fragments.py
git commit -m "test: guard fragment frontmatter schema and content-scrub invariants"
```

---

## Phase 2 — `lfg generate` (the generator)

### Task 5: Generator module

**Files:**
- Create: `product/scripts/generator.py`
- Test: `product/tests/test_generator.py`

The generator is a pure transformation: read fragments → sort → render AGENTS.md → return string (no I/O at the rendering layer). I/O is the caller's job. This makes it trivially testable.

- [ ] **Step 1: Write the failing tests**

```python
# product/tests/test_generator.py
import textwrap
import pytest
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from generator import (
    parse_fragment, render_agents_md, GeneratorError, AGENTS_TOKEN_BUDGET,
)


def write(tmp_path, name, frontmatter, body):
    p = tmp_path / name
    p.write_text(f"---\n{frontmatter.strip()}\n---\n\n{body}\n", encoding="utf-8")
    return p


def test_parse_fragment_extracts_frontmatter_and_body(tmp_path):
    p = write(tmp_path, "x.md",
              "fragment: x\norder: 1\ntargets: agents_md\nsummary: A short summary.",
              "# Body\n\nHello.")
    fm, body = parse_fragment(p)
    assert fm["fragment"] == "x"
    assert fm["order"] == 1
    assert fm["targets"] == ["agents_md"]
    assert fm["summary"] == "A short summary."
    assert body.strip() == "# Body\n\nHello."


def test_parse_fragment_targets_multi(tmp_path):
    p = write(tmp_path, "x.md",
              "fragment: x\norder: 1\ntargets: agents_md, claude_rules, augment_rules\nsummary: s",
              "body")
    fm, _ = parse_fragment(p)
    assert fm["targets"] == ["agents_md", "claude_rules", "augment_rules"]


def test_parse_fragment_missing_frontmatter_raises(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("no frontmatter here\n", encoding="utf-8")
    with pytest.raises(GeneratorError):
        parse_fragment(p)


def test_render_agents_md_includes_sections_in_order(tmp_path):
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 20\ntargets: agents_md\nsummary: Second.",
              "Body of A.")
    b = write(tmp_path, "b.md",
              "fragment: b\norder: 10\ntargets: agents_md\nsummary: First.",
              "Body of B.")
    out = render_agents_md([parse_fragment(b), parse_fragment(a)])
    # b before a (order 10 < 20)
    assert out.index("## b") < out.index("## a")
    # both bodies present
    assert "Body of A." in out
    assert "Body of B." in out
    # frontmatter present
    assert out.startswith("---\n")
    assert "doc: AGENTS" in out
    # read-this-first block
    assert "Read this first" in out
    # available commands
    assert "lfg validate" in out
    assert "lfg prime" in out
    assert "lfg promote" in out
    # section index
    assert "- **a**" in out
    assert "- **b**" in out


def test_render_skips_fragments_not_targeted_for_agents_md(tmp_path):
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 10\ntargets: agents_md\nsummary: s",
              "in agents")
    b = write(tmp_path, "b.md",
              "fragment: b\norder: 20\ntargets: claude_rules\nsummary: s",
              "claude only")
    out = render_agents_md([parse_fragment(a), parse_fragment(b)])
    assert "in agents" in out
    assert "claude only" not in out
    assert "## b" not in out


def test_render_uses_lf_no_bom_trailing_newline(tmp_path):
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 10\ntargets: agents_md\nsummary: s",
              "body")
    out = render_agents_md([parse_fragment(a)])
    assert "\r\n" not in out, "CRLF leaked into output"
    assert not out.startswith("﻿"), "BOM leaked into output"
    assert out.endswith("\n"), "missing trailing newline"
    assert not out.endswith("\n\n"), "double trailing newline"


def test_render_fails_above_budget(tmp_path, monkeypatch):
    # Force a tiny budget so a small fragment trips the gate.
    monkeypatch.setattr("generator.AGENTS_TOKEN_BUDGET", 50)
    a = write(tmp_path, "a.md",
              "fragment: a\norder: 10\ntargets: agents_md\nsummary: s",
              "x" * 1000)  # ~250 tokens at chars/4
    with pytest.raises(GeneratorError, match="exceeds token budget"):
        render_agents_md([parse_fragment(a)])
```

- [ ] **Step 2: Run, see fail**

```bash
python -m pytest product/tests/test_generator.py -v
```

Expected: `ModuleNotFoundError: No module named 'generator'`.

- [ ] **Step 3: Implement `product/scripts/generator.py`**

```python
"""Generator: fragments -> AGENTS.md.

Pure functions: parse_fragment(path) returns (frontmatter_dict, body_str);
render_agents_md(fragments) returns the rendered AGENTS.md string. Neither
function does I/O on AGENTS.md itself — the caller writes.

Output is LF, UTF-8 (no BOM), single trailing newline. Fails loudly on
malformed frontmatter or above-budget output. Same inputs => byte-identical
output (idempotent).
"""
from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Tuple

AGENTS_TOKEN_BUDGET = 3000  # chars/4 heuristic, matches Spec 1 canonical


class GeneratorError(ValueError):
    pass


def _parse_frontmatter(text: str) -> Dict[str, Any]:
    fm: Dict[str, Any] = {}
    for line in text.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if ":" not in s:
            raise GeneratorError(f"bad frontmatter line: {s!r}")
        k, _, v = s.partition(":")
        k = k.strip()
        v = v.strip()
        if k == "order":
            try:
                fm[k] = int(v)
            except ValueError as e:
                raise GeneratorError(f"'order' must be an integer, got {v!r}") from e
        elif k == "targets":
            v = v.lstrip("[").rstrip("]")
            fm[k] = [t.strip() for t in v.split(",") if t.strip()]
        else:
            if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
                v = v[1:-1]
            fm[k] = v
    return fm


def parse_fragment(path: Path) -> Tuple[Dict[str, Any], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise GeneratorError(f"{path.name}: missing opening frontmatter delimiter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise GeneratorError(f"{path.name}: unterminated frontmatter")
    fm = _parse_frontmatter(text[4:end])
    body = text[end + 5:]  # skip past closing '\n---\n'
    return fm, body


def render_agents_md(fragments: List[Tuple[Dict[str, Any], str]]) -> str:
    # Keep only fragments destined for AGENTS.md; sort by order.
    in_agents = [f for f in fragments if "agents_md" in f[0].get("targets", [])]
    in_agents.sort(key=lambda fb: fb[0]["order"])

    lines: List[str] = []
    # 1. Own frontmatter
    lines += [
        "---",
        "doc: AGENTS",
        "related:",
        "  state: ./logs/STATE.md",
        "  changelog: ./logs/CHANGELOG.md",
        "  devlog: ./logs/DEVLOG.md",
        "---",
        "",
    ]
    # 2. Read this first
    lines += [
        "# Log File Genius — AGENTS guidance",
        "",
        "**Read this first.** This project uses Log File Genius. To orient cold:",
        "",
        "- `logs/STATE.md` — the now (current context + last session)",
        "- `logs/CHANGELOG.md` Unreleased — recent changes",
        "- `logs/DEVLOG.md` Daily Log — why decisions were made",
        "",
    ]
    # 3. Available commands
    lines += [
        "## Available commands",
        "",
        "- `lfg validate` — validate log files (format + token budget)",
        "- `lfg prime [--n N]` — emit a subagent context digest (the lead pastes this into a subagent prompt to establish role + give context)",
        "- `lfg promote <id>` — lead-only; promote a subagent's staged entries to canonical CHANGELOG/DEVLOG",
        "- `lfg status` — quick project status",
        "- `lfg generate` — regenerate AGENTS.md from product/rules/ fragments (LFG contributors)",
        "",
    ]
    # 4. Section index
    lines += ["## Sections", ""]
    for fm, _ in in_agents:
        lines.append(f"- **{fm['fragment']}** — {fm['summary']}")
    lines.append("")
    # 5. Fragments
    for fm, body in in_agents:
        lines.append(f"## {fm['fragment']}")
        lines.append("")
        lines.append(body.strip())
        lines.append("")

    out = "\n".join(lines)
    if not out.endswith("\n"):
        out += "\n"

    # Hard budget gate
    tokens = len(out) // 4
    if tokens > AGENTS_TOKEN_BUDGET:
        raise GeneratorError(
            f"AGENTS.md exceeds token budget ({tokens} > {AGENTS_TOKEN_BUDGET}); "
            "compress fragments or raise the budget intentionally"
        )
    return out
```

- [ ] **Step 4: Run, see pass**

```bash
python -m pytest product/tests/test_generator.py -v
```

Expected: all pass.

- [ ] **Step 5: Commit**

```bash
git add product/scripts/generator.py product/tests/test_generator.py
git commit -m "feat(generator): pure fragments->AGENTS.md rendering with budget gate"
```

### Task 6: Wire `lfg generate [--check]` subcommand

**Files:**
- Modify: `product/scripts/lfg.py`
- Test: `product/tests/test_lfg_generate.py`

- [ ] **Step 1: Write the failing test**

```python
# product/tests/test_lfg_generate.py
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"


def run(args, cwd=ROOT):
    return subprocess.run([sys.executable, str(LFG)] + args, cwd=cwd,
                          capture_output=True, text=True, encoding="utf-8")


def test_generate_writes_agents_md(tmp_path, monkeypatch):
    # Use the real repo as input; write AGENTS.md to a tempfile via --out
    out = tmp_path / "AGENTS.md"
    r = run(["generate", "--out", str(out)])
    assert r.returncode == 0, r.stderr
    text = out.read_text(encoding="utf-8")
    assert text.startswith("---\n")
    assert "doc: AGENTS" in text
    assert "## log-file-maintenance" in text


def test_generate_idempotent(tmp_path):
    out1 = tmp_path / "1.md"
    out2 = tmp_path / "2.md"
    assert run(["generate", "--out", str(out1)]).returncode == 0
    assert run(["generate", "--out", str(out2)]).returncode == 0
    assert out1.read_bytes() == out2.read_bytes()


def test_generate_check_passes_when_committed_matches(tmp_path):
    # Run generate to write product/AGENTS.md (or it already exists). Then
    # --check should be zero-diff.
    r = run(["generate"])
    assert r.returncode == 0, r.stderr
    r = run(["generate", "--check"])
    assert r.returncode == 0, f"check failed:\n{r.stdout}\n{r.stderr}"


def test_generate_check_fails_on_drift(tmp_path):
    # Mutate the committed file to force a diff.
    target = ROOT / "product/AGENTS.md"
    original = target.read_bytes()
    try:
        target.write_text(original.decode("utf-8") + "\nINJECTED DRIFT\n", encoding="utf-8")
        r = run(["generate", "--check"])
        assert r.returncode != 0
        assert "diff" in (r.stdout + r.stderr).lower() or "drift" in (r.stdout + r.stderr).lower()
    finally:
        target.write_bytes(original)
```

- [ ] **Step 2: Run, see fail**

Expected: `generate` subcommand doesn't exist yet.

- [ ] **Step 3: Read `product/scripts/lfg.py` (lines ~190 onward) to see the existing subparser pattern, then add the `generate` command.**

Add this function near the other `cmd_*` functions in `lfg.py`:

```python
def cmd_generate(args):
    from generator import parse_fragment, render_agents_md, GeneratorError
    rules_dir = Path(__file__).resolve().parent.parent / "rules"
    if not rules_dir.is_dir():
        print(f"ERROR: rules dir not found at {rules_dir}", file=sys.stderr)
        return 2

    fragments = []
    for p in sorted(rules_dir.glob("*.md")):
        try:
            fragments.append(parse_fragment(p))
        except GeneratorError as e:
            print(f"ERROR: {p.name}: {e}", file=sys.stderr)
            return 2

    try:
        rendered = render_agents_md(fragments)
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Default output: product/AGENTS.md, unless --out specified.
    default_out = Path(__file__).resolve().parent.parent / "AGENTS.md"
    out_path = Path(args.out) if getattr(args, "out", None) else default_out

    if getattr(args, "check", False):
        existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        if existing == rendered:
            return 0
        # Print a short diff hint.
        print(f"DRIFT: {out_path} would change after `lfg generate`.", file=sys.stderr)
        print("Run `python product/scripts/lfg.py generate` and commit the result.",
              file=sys.stderr)
        return 1

    # Write with explicit LF + UTF-8, no BOM.
    out_path.write_bytes(rendered.encode("utf-8"))
    tokens = len(rendered) // 4
    print(f"Wrote {out_path} ({tokens} tokens, budget 3000)")
    return 0
```

Then in `main()` where the subparsers are registered, add:

```python
    p_gen = subparsers.add_parser('generate', help='Regenerate AGENTS.md from fragments')
    p_gen.add_argument('--check', action='store_true',
                       help='Exit non-zero if AGENTS.md would change (CI mode)')
    p_gen.add_argument('--out', help='Write to a non-default path (testing)')
    p_gen.set_defaults(func=cmd_generate)
```

(Match the pattern lfg.py uses for other commands.)

If `lfg.py` doesn't already `from pathlib import Path` at module top, add it.

- [ ] **Step 4: Generate the initial `product/AGENTS.md`**

```bash
python product/scripts/lfg.py generate
```

Expected: `Wrote .../product/AGENTS.md (N tokens, budget 3000)` with N ≤ 3000.

- [ ] **Step 5: Run the tests**

```bash
python -m pytest product/tests/test_lfg_generate.py -v
```

Expected: all PASS.

- [ ] **Step 6: Commit**

```bash
git add product/scripts/lfg.py product/AGENTS.md product/tests/test_lfg_generate.py
git commit -m "feat(lfg): add 'generate' and 'generate --check' subcommands; commit initial AGENTS.md"
```

---

## Phase 3 — `lfg prime` (subagent context digest + identity signal)

### Task 7: Primer module

**Files:**
- Create: `product/scripts/primer.py`
- Test: `product/tests/test_primer.py`

- [ ] **Step 1: Write the failing tests**

```python
# product/tests/test_primer.py
import json
import textwrap
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from primer import build_prime, SUBAGENT_MARKER


def write_log(tmp_path, name, text):
    (tmp_path / "logs").mkdir(exist_ok=True)
    p = tmp_path / "logs" / name
    p.write_text(textwrap.dedent(text), encoding="utf-8")
    return p


def test_prime_starts_with_subagent_marker(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n\n## Current Context\n- Version: v1\n")
    write_log(tmp_path, "CHANGELOG.md", "# Changelog\n## [Unreleased]\n### Added\n- Item A.\n")
    out = build_prime(project_root=tmp_path, n=5, as_json=False)
    assert out.split("\n", 1)[0] == SUBAGENT_MARKER


def test_prime_includes_state_and_changelog_entries(tmp_path):
    write_log(tmp_path, "STATE.md",
              "# Current State\n\n## Current Context\n- Version: v1.2.3\n- Phase: testing\n")
    write_log(tmp_path, "CHANGELOG.md", textwrap.dedent("""
        # Changelog
        ## [Unreleased]
        ### Added
        - Most recent entry.
        - Older entry.
    """))
    out = build_prime(project_root=tmp_path, n=2, as_json=False)
    assert "v1.2.3" in out
    assert "Most recent entry" in out
    assert "Older entry" in out


def test_prime_n_limits_changelog_entries(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n")
    lines = "\n".join(f"- Entry {i}." for i in range(10))
    write_log(tmp_path, "CHANGELOG.md",
              f"# Changelog\n## [Unreleased]\n### Added\n{lines}\n")
    out = build_prime(project_root=tmp_path, n=3, as_json=False)
    assert "Entry 0" in out
    assert "Entry 1" in out
    assert "Entry 2" in out
    assert "Entry 3" not in out


def test_prime_json_shape(tmp_path):
    write_log(tmp_path, "STATE.md", "# Current State\n")
    write_log(tmp_path, "CHANGELOG.md", "# Changelog\n## [Unreleased]\n- E.\n")
    out = build_prime(project_root=tmp_path, n=5, as_json=True)
    data = json.loads(out)
    assert data["role"] == "subagent"
    assert data["marker"] == SUBAGENT_MARKER
    assert "state" in data
    assert "changelog_entries" in data
    assert isinstance(data["changelog_entries"], list)


def test_prime_handles_missing_files(tmp_path):
    # No logs/ dir at all
    out = build_prime(project_root=tmp_path, n=5, as_json=False)
    assert SUBAGENT_MARKER in out
    assert "STATE.md not found" in out or "missing" in out.lower()
```

- [ ] **Step 2: Run, see fail**

Expected: `ModuleNotFoundError: No module named 'primer'`.

- [ ] **Step 3: Implement `product/scripts/primer.py`**

```python
"""Subagent context digest builder.

build_prime() reads STATE.md + last N CHANGELOG 'Unreleased' entries and emits
a digest prefixed with the LFG_SUBAGENT_PRIME marker — the role-identity
signal. Any agent whose initial prompt contains this marker IS a subagent and
follows the subagent contract documented in log-file-maintenance.md.

No I/O on canonical files (read-only); no --topic (relevance filtering is
LLM work, not deterministic).
"""
from __future__ import annotations
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any

# Reuse Spec 1's stdlib config parser. Sibling-module import.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_parser import parse_config

SUBAGENT_MARKER = "LFG_SUBAGENT_PRIME"


def _resolve_log_path(project_root: Path, key: str, default_rel: str) -> Path:
    cfg = parse_config(str(project_root / ".logfile-config.yml"))
    path = cfg.get("paths", {}).get(key)
    if path:
        return project_root / path
    return project_root / default_rel


def _read_state(project_root: Path) -> str:
    state = _resolve_log_path(project_root, "state", "logs/STATE.md")
    if not state.exists():
        return f"(STATE.md not found at {state.relative_to(project_root)})"
    return state.read_text(encoding="utf-8")


def _last_n_changelog_entries(project_root: Path, n: int) -> List[str]:
    changelog = _resolve_log_path(project_root, "changelog", "logs/CHANGELOG.md")
    if not changelog.exists():
        return []
    text = changelog.read_text(encoding="utf-8")
    # Find the "## [Unreleased]" section.
    lines = text.splitlines()
    try:
        start = next(i for i, ln in enumerate(lines)
                     if ln.strip().lower().startswith("## [unreleased]"))
    except StopIteration:
        return []
    entries: List[str] = []
    for ln in lines[start + 1:]:
        if ln.strip().startswith("## "):
            break  # next major section
        stripped = ln.lstrip()
        if stripped.startswith("- "):
            entries.append(stripped[2:].rstrip())
            if len(entries) >= n:
                break
    return entries


def build_prime(project_root: Path, n: int = 5, as_json: bool = False) -> str:
    state = _read_state(project_root)
    entries = _last_n_changelog_entries(project_root, n)

    paths_block = {
        "state": str(_resolve_log_path(project_root, "state", "logs/STATE.md").relative_to(project_root)),
        "changelog": str(_resolve_log_path(project_root, "changelog", "logs/CHANGELOG.md").relative_to(project_root)),
        "devlog": str(_resolve_log_path(project_root, "devlog", "logs/DEVLOG.md").relative_to(project_root)),
    }

    if as_json:
        return json.dumps({
            "marker": SUBAGENT_MARKER,
            "role": "subagent",
            "state": state,
            "changelog_entries": entries,
            "paths": paths_block,
        }, indent=2)

    out: List[str] = [SUBAGENT_MARKER, ""]
    out += ["You are a subagent. Follow the subagent contract in log-file-maintenance.md.",
            ""]
    out += ["# STATE.md", "", state.rstrip(), ""]
    out += [f"# Last {len(entries)} CHANGELOG entries", ""]
    if entries:
        out += [f"- {e}" for e in entries]
    else:
        out += ["(no unreleased entries)"]
    out += ["", "# Canonical paths", ""]
    for k, v in paths_block.items():
        out.append(f"- {k}: {v}")
    out.append("")
    return "\n".join(out)
```

- [ ] **Step 4: Run, see pass**

```bash
python -m pytest product/tests/test_primer.py -v
```

Expected: 5 PASS.

- [ ] **Step 5: Commit**

```bash
git add product/scripts/primer.py product/tests/test_primer.py
git commit -m "feat(primer): subagent context digest with LFG_SUBAGENT_PRIME identity marker"
```

### Task 8: Wire `lfg prime` subcommand

**Files:**
- Modify: `product/scripts/lfg.py`

- [ ] **Step 1: Add the command function** (next to `cmd_generate` in `lfg.py`)

```python
def cmd_prime(args):
    from primer import build_prime
    out = build_prime(project_root=Path.cwd(), n=args.n, as_json=args.json)
    print(out)
    return 0
```

- [ ] **Step 2: Register the subparser** (alongside the others in `main()`)

```python
    p_prime = subparsers.add_parser('prime', help='Emit subagent context digest')
    p_prime.add_argument('--n', type=int, default=5,
                         help='Number of CHANGELOG Unreleased entries to include (default 5)')
    p_prime.add_argument('--json', action='store_true', help='JSON output')
    p_prime.set_defaults(func=cmd_prime)
```

- [ ] **Step 3: Smoke**

```bash
python product/scripts/lfg.py prime --n 3 | head -5
```

Expected: first line is `LFG_SUBAGENT_PRIME`.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/lfg.py
git commit -m "feat(lfg): add 'prime' subcommand"
```

---

## Phase 4 — `lfg promote` (staged-write promotion)

### Task 9: Promoter module

**Files:**
- Create: `product/scripts/promoter.py`
- Test: `product/tests/test_promoter.py`

- [ ] **Step 1: Write the failing tests**

```python
# product/tests/test_promoter.py
import textwrap
from datetime import datetime
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from promoter import promote, PromoteError


def _seed(tmp_path):
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "CHANGELOG.md").write_text(textwrap.dedent("""
        # Changelog
        ## [Unreleased]
        ### Added
        - Existing entry.
    """).lstrip(), encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(textwrap.dedent("""
        # Development Log

        ## Daily Log - Newest First

        ### 2026-01-01: prior entry
    """).lstrip(), encoding="utf-8")
    return tmp_path


def _stage(root, subagent_id, changelog=None, devlog=None):
    d = root / ".lfg" / "staged" / subagent_id
    d.mkdir(parents=True)
    if changelog is not None:
        (d / "changelog.md").write_text(changelog, encoding="utf-8")
    if devlog is not None:
        (d / "devlog.md").write_text(devlog, encoding="utf-8")
    return d


def test_promote_appends_changelog_and_clears_staged(tmp_path):
    root = _seed(tmp_path)
    staged = _stage(root, "sub42",
                    changelog="- New entry from subagent. Files: `x.py`. Commit: `pending`")
    promote(root, "sub42")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Existing entry" in cl
    assert "New entry from subagent" in cl
    assert not staged.exists()


def test_promote_appends_devlog(tmp_path):
    root = _seed(tmp_path)
    _stage(root, "sub42",
           devlog="### 2026-05-28: subagent did things\n\nDetails.")
    promote(root, "sub42")
    dl = (root / "logs" / "DEVLOG.md").read_text(encoding="utf-8")
    assert "subagent did things" in dl
    assert "prior entry" in dl  # original preserved


def test_promote_missing_staged_dir_is_noop(tmp_path):
    root = _seed(tmp_path)
    # Should not raise; just print a friendly message.
    promote(root, "nonexistent")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "Existing entry" in cl  # unchanged


def test_promote_writes_audit_trail(tmp_path):
    root = _seed(tmp_path)
    _stage(root, "sub42", changelog="- Entry.")
    promote(root, "sub42")
    audit = (root / ".lfg" / "promoted.log").read_text(encoding="utf-8")
    assert "sub42" in audit
    # ISO 8601-ish date present
    assert datetime.utcnow().strftime("%Y") in audit


def test_promote_routes_entries_to_their_declared_category(tmp_path):
    """Subagent staged entries that declare '### Fixed' must land under the
    canonical CHANGELOG's '### Fixed' subsection, not under whichever '###' is
    first. Code-owl review finding #1.
    """
    root = _seed(tmp_path)
    # Seed already has '### Added'; add '### Fixed' to canonical too.
    cl_path = root / "logs" / "CHANGELOG.md"
    cl_path.write_text(
        "# Changelog\n## [Unreleased]\n### Added\n- Existing add.\n\n### Fixed\n- Existing fix.\n",
        encoding="utf-8",
    )
    _stage(root, "sub99", changelog="### Fixed\n- A new fix from subagent.\n")
    promote(root, "sub99")
    cl = cl_path.read_text(encoding="utf-8")
    # New entry lands under "### Fixed", not under "### Added".
    fixed_block = cl[cl.index("### Fixed"):]
    added_block = cl[cl.index("### Added"):cl.index("### Fixed")]
    assert "A new fix from subagent" in fixed_block
    assert "A new fix from subagent" not in added_block


def test_promote_creates_new_category_when_missing(tmp_path):
    """If the canonical CHANGELOG doesn't have the staged category yet, promote
    adds a new '### <Category>' subsection at the end of [Unreleased].
    """
    root = _seed(tmp_path)
    _stage(root, "sub88", changelog="### Security\n- Closed an auth gap.\n")
    promote(root, "sub88")
    cl = (root / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "### Security" in cl
    assert "Closed an auth gap" in cl


def test_promote_preserves_multiline_devlog_blocks(tmp_path):
    """DEVLOG entries often span multiple paragraphs separated by blank lines —
    the promoter must not strip the interior blanks. Code-owl review finding #2.
    """
    root = _seed(tmp_path)
    entry = (
        "### 2026-05-28: A standard-format entry\n"
        "\n"
        "**Situation:** Setup.\n"
        "\n"
        "**Decision:** Did the thing.\n"
    )
    _stage(root, "subml", devlog=entry)
    promote(root, "subml")
    dl = (root / "logs" / "DEVLOG.md").read_text(encoding="utf-8")
    assert "**Situation:**" in dl
    assert "**Decision:**" in dl
    # Interior blank line between the two **Bold** blocks survived.
    sit = dl.index("**Situation:**")
    dec = dl.index("**Decision:**")
    assert "\n\n" in dl[sit:dec], "interior blank line between paragraphs was stripped"
```

- [ ] **Step 2: Run, see fail.**

- [ ] **Step 3: Implement `product/scripts/promoter.py`**

```python
"""Lead-only verb: promote subagent staged writes into canonical CHANGELOG/DEVLOG.

Reads .lfg/staged/<id>/changelog.md and .lfg/staged/<id>/devlog.md, appends
to canonical (routing CHANGELOG entries to their declared '### <Category>'
subsections), writes an audit line to .lfg/promoted.log, removes the staged
dir. Idempotent — second call on the same id is a no-op.
"""
from __future__ import annotations
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List

# Reuse Spec 1's stdlib config parser instead of duplicating its logic here.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_parser import parse_config


class PromoteError(ValueError):
    pass


def _resolve(project_root: Path, key: str, default_rel: str) -> Path:
    cfg = parse_config(str(project_root / ".logfile-config.yml"))
    path = cfg.get("paths", {}).get(key)
    if path:
        return project_root / path
    return project_root / default_rel


def _split_by_category(staged_text: str) -> Dict[str, List[str]]:
    """Parse the staged changelog into {category: [entry-lines]}. Lines before
    any '### <Category>' header default to 'Added'. Preserves blank lines
    inside a category (they may be intentional formatting)."""
    by_cat: Dict[str, List[str]] = {}
    current = "Added"
    for ln in staged_text.splitlines():
        s = ln.strip()
        if s.startswith("### "):
            current = s[4:].strip()
            continue
        by_cat.setdefault(current, []).append(ln.rstrip())
    # Trim leading/trailing blank lines per category, but keep interior blanks.
    for cat, lines in list(by_cat.items()):
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()
        if not lines:
            del by_cat[cat]
        else:
            by_cat[cat] = lines
    return by_cat


def _append_under_unreleased(changelog_path: Path, new_entries: str) -> None:
    text = changelog_path.read_text(encoding="utf-8") if changelog_path.exists() else "# Changelog\n## [Unreleased]\n"
    lines = text.splitlines()
    try:
        unreleased_i = next(idx for idx, ln in enumerate(lines)
                            if ln.strip().lower().startswith("## [unreleased]"))
    except StopIteration:
        raise PromoteError(f"{changelog_path}: missing '## [Unreleased]' section")

    by_cat = _split_by_category(new_entries)
    if not by_cat:
        return  # nothing to do

    # Find the bounds of the [Unreleased] section.
    section_end = len(lines)
    for j in range(unreleased_i + 1, len(lines)):
        if lines[j].strip().startswith("## "):
            section_end = j
            break

    # For each category, find an existing '### <Category>' header inside the
    # section; if found, append after it. Otherwise add the header + entries
    # at the end of the section.
    out = lines[:]
    # Walk from the end so insertions don't shift earlier indices.
    for cat in reversed(list(by_cat.keys())):
        entries = by_cat[cat]
        header_idx = None
        for j in range(unreleased_i + 1, section_end):
            if out[j].strip().lower() == f"### {cat.lower()}":
                header_idx = j
                break
        if header_idx is not None:
            insert_at = header_idx + 1
            # Skip immediate blanks under the header to land on first entry,
            # then insert before any non-entry content.
            while insert_at < section_end and not out[insert_at].strip():
                insert_at += 1
            out[insert_at:insert_at] = entries
            section_end += len(entries)
        else:
            # Append a new subsection at the end of [Unreleased].
            new_block = [f"### {cat}"] + entries + [""]
            out[section_end:section_end] = new_block
            section_end += len(new_block)

    # Always end with exactly one trailing newline.
    rendered = "\n".join(out).rstrip("\n") + "\n"
    changelog_path.write_text(rendered, encoding="utf-8")


def _append_to_devlog(devlog_path: Path, new_entry: str) -> None:
    text = devlog_path.read_text(encoding="utf-8") if devlog_path.exists() else "# Development Log\n\n## Daily Log - Newest First\n"
    lines = text.splitlines()
    try:
        i = next(idx for idx, ln in enumerate(lines)
                 if ln.strip().lower().startswith("## daily log"))
        insert_at = i + 1
    except StopIteration:
        # Append at end if no Daily Log heading exists.
        insert_at = len(lines)
    new_lines = lines[:insert_at] + [""] + new_entry.rstrip().splitlines() + lines[insert_at:]
    devlog_path.write_text("\n".join(new_lines) + ("\n" if text.endswith("\n") else ""), encoding="utf-8")


def promote(project_root: Path, subagent_id: str) -> int:
    staged_dir = project_root / ".lfg" / "staged" / subagent_id
    if not staged_dir.is_dir():
        print(f"No staged entries for '{subagent_id}' (looked at {staged_dir})")
        return 0

    changelog_src = staged_dir / "changelog.md"
    devlog_src = staged_dir / "devlog.md"
    actions = []

    if changelog_src.exists():
        target = _resolve(project_root, "changelog", "logs/CHANGELOG.md")
        _append_under_unreleased(target, changelog_src.read_text(encoding="utf-8"))
        actions.append(f"CHANGELOG <- {changelog_src.relative_to(project_root)}")
    if devlog_src.exists():
        target = _resolve(project_root, "devlog", "logs/DEVLOG.md")
        _append_to_devlog(target, devlog_src.read_text(encoding="utf-8"))
        actions.append(f"DEVLOG <- {devlog_src.relative_to(project_root)}")

    # Audit trail
    audit = project_root / ".lfg" / "promoted.log"
    audit.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    audit_line = f"{ts}  {subagent_id}  {'; '.join(actions) if actions else 'no-op'}\n"
    with audit.open("a", encoding="utf-8") as f:
        f.write(audit_line)

    # Clear staged dir
    shutil.rmtree(staged_dir)
    print(f"promoted {subagent_id}: {', '.join(actions) if actions else 'no entries to promote'}")
    return 0
```

- [ ] **Step 4: Run, see pass**

```bash
python -m pytest product/tests/test_promoter.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add product/scripts/promoter.py product/tests/test_promoter.py
git commit -m "feat(promoter): promote staged subagent entries into canonical CHANGELOG/DEVLOG"
```

### Task 10: Wire `lfg promote` subcommand

**Files:**
- Modify: `product/scripts/lfg.py`

- [ ] **Step 1: Add command function**

```python
def cmd_promote(args):
    from promoter import promote
    return promote(Path.cwd(), args.subagent_id)
```

- [ ] **Step 2: Register subparser**

```python
    p_prom = subparsers.add_parser('promote', help='Promote a subagent\'s staged entries to canonical logs')
    p_prom.add_argument('subagent_id', help='Subagent id matching .lfg/staged/<id>/')
    p_prom.set_defaults(func=cmd_promote)
```

- [ ] **Step 3: Smoke**

```bash
python product/scripts/lfg.py promote nonexistent
```

Expected: `No staged entries for 'nonexistent' ...`; exit 0.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/lfg.py
git commit -m "feat(lfg): add 'promote' subcommand"
```

---

## Phase 5 — Rule fragment additions

### Task 11: Add subagent contract block to `log-file-maintenance.md`

**Files:**
- Modify: `product/rules/log-file-maintenance.md`

- [ ] **Step 1: Insert this block** immediately before the existing `## 🎯 SUCCESS CRITERIA` section (or at the end if that heading is absent):

```markdown
---

## 🤖 SUBAGENT CONTRACT

**Identity signal:** If your initial context contains the literal string `LFG_SUBAGENT_PRIME`, you are a **subagent**. Follow this contract.

**Reading:**
- Read the primed digest already in your context. Do NOT load the full STATE.md / CHANGELOG.md / DEVLOG.md unless the lead explicitly tells you to.

**Writing — staged, never direct:**
- Never modify `STATE.md`. SESSION END is lead-only (see SESSION END above).
- Never modify `CHANGELOG.md` or `DEVLOG.md` directly.
- When your work warrants a CHANGELOG or DEVLOG entry, write it to:
  - `.lfg/staged/<your-id>/changelog.md` (CHANGELOG entries, one per line, `- Description. Files: \`x\`. Commit: \`pending\``)
  - `.lfg/staged/<your-id>/devlog.md` (DEVLOG entry, fully formatted)
- Tell the lead in your final report: "Staged at `.lfg/staged/<your-id>/`."
- The lead will run `lfg promote <your-id>` to merge into canonical logs.

**Context limits:**
- Do NOT call `lfg prime` yourself. There is no `--topic` flag. If you need more context, ask the lead.
```

(`<your-id>` is whatever id the lead assigned in the dispatch prompt; if absent, use a short slug describing the task.)

- [ ] **Step 2: Verify the marker reference is exact**

```bash
grep -n "LFG_SUBAGENT_PRIME" product/rules/log-file-maintenance.md product/scripts/primer.py
```

Expected: both files have the same literal.

- [ ] **Step 3: Commit**

```bash
git add product/rules/log-file-maintenance.md
git commit -m "feat(rules): subagent contract — LFG_SUBAGENT_PRIME identity + staged writes"
```

### Task 12: Add CHANGELOG self-application rule

**Files:**
- Modify: `product/rules/log-file-maintenance.md`

Editing a fragment changes the fragment + AGENTS.md + (at install time) per-tool files. The CHANGELOG entry should reference only the fragment.

- [ ] **Step 1:** In the `## 🔴 BEFORE EVERY COMMIT` section's CHANGELOG-entry-format guidance, add a bullet near the format example:

```markdown
   - **Fragment edits:** when changing files under `product/rules/`, the CHANGELOG entry references only the fragment path. The regenerated `product/AGENTS.md` and the per-tool rule files at install-time are implicit and need not be listed.
```

- [ ] **Step 2: Commit**

```bash
git add product/rules/log-file-maintenance.md
git commit -m "feat(rules): CHANGELOG self-application rule for fragment edits"
```

### Task 13: Regenerate AGENTS.md (after Tasks 11-12 changed fragments)

- [ ] **Step 1: Regenerate**

```bash
python product/scripts/lfg.py generate
```

Expected: token count printed; under 3000.

- [ ] **Step 2: Verify clean**

```bash
python product/scripts/lfg.py generate --check
```

Expected: exit 0, no output.

- [ ] **Step 3: Commit**

```bash
git add product/AGENTS.md
git commit -m "chore: regenerate AGENTS.md after subagent-contract additions"
```

---

## Phase 6 — Installer + update + templates

### Task 14: Claude project_instructions template

**Files:**
- Create: `product/install-templates/claude/project_instructions.md.tmpl`
- Move from / delete: `product/ai-rules/claude-code/project_instructions.md`

- [ ] **Step 1: Read the existing template content**

```bash
cat product/ai-rules/claude-code/project_instructions.md
```

- [ ] **Step 2: Create the .tmpl** with the same content, replacing literal paths with placeholder tokens. Specifically:
- Replace literal `logs/CHANGELOG.md` → `{{paths.changelog}}`
- Replace literal `logs/DEVLOG.md` → `{{paths.devlog}}`
- Replace literal `logs/STATE.md` → `{{paths.state}}`
- Replace literal `logs/adr/` → `{{paths.adr_dir}}`

Write the result to `product/install-templates/claude/project_instructions.md.tmpl`.

- [ ] **Step 3: Remove the now-templated original**

```bash
git rm product/ai-rules/claude-code/project_instructions.md
```

- [ ] **Step 4: Commit**

```bash
git add product/install-templates/claude/project_instructions.md.tmpl
git commit -m "feat: claude project_instructions becomes templated install artifact"
```

### Task 15: `install.sh` — generate per-tool dirs from fragments at install time

**Files:**
- Modify: `product/scripts/install.sh`

The current installer copies rules from `product/ai-rules/<tool>/`. Change it to:
1. Read each fragment under `product/rules/`.
2. Extract its frontmatter `targets`.
3. For each target, copy the fragment to the appropriate per-tool directory in the user's project.

- [ ] **Step 1: Read the current rules-install section** in `install.sh` to understand the existing structure (the loops that copy `product/ai-rules/$AI_ASSISTANT/*.md`).

- [ ] **Step 2: Replace the augment branch and the claude-code rules loop** with this block. The function reads frontmatter via awk and routes by target:

```bash
# Map AI_ASSISTANT to its rules-dir target name in fragment frontmatter.
case "$AI_ASSISTANT" in
    augment)     RULES_TARGET="augment_rules"; RULES_DEST="$PROJECT_ROOT/.augment/rules" ;;
    claude-code) RULES_TARGET="claude_rules";  RULES_DEST="$PROJECT_ROOT/.claude/rules"  ;;
    *)           rollback_installation "Unknown assistant: $AI_ASSISTANT" ;;
esac

mkdir -p "$RULES_DEST"

# Walk fragments; copy each whose `targets` includes our RULES_TARGET.
for frag in "$SOURCE_ROOT/rules/"*.md; do
    [ -f "$frag" ] || continue
    # Pull the `targets:` line from the YAML frontmatter (between the first two '---' lines).
    targets=$(awk '
        /^---$/{count++; if(count==2)exit; next}
        count==1 && /^targets:/{ sub(/^targets:[[:space:]]*/,""); print; exit }
    ' "$frag")
    case ",$(echo "$targets" | tr -d '[] ')," in
        *",$RULES_TARGET,"*)
            cp "$frag" "$RULES_DEST/$(basename "$frag")"
            CREATED_ITEMS+=("$RULES_DEST/$(basename "$frag")")
            print_success "Installed $(basename "$frag")"
            ;;
    esac
done

# Render Claude project_instructions template (if installing for claude-code).
if [ "$AI_ASSISTANT" = "claude-code" ]; then
    TMPL="$SOURCE_ROOT/install-templates/claude/project_instructions.md.tmpl"
    DEST="$PROJECT_ROOT/.claude/project_instructions.md"
    # Substitute {{paths.X}} tokens. Defaults match Spec 1's canonical.
    sed \
        -e 's|{{paths.changelog}}|logs/CHANGELOG.md|g' \
        -e 's|{{paths.devlog}}|logs/DEVLOG.md|g' \
        -e 's|{{paths.state}}|logs/STATE.md|g' \
        -e 's|{{paths.adr_dir}}|logs/adr/|g' \
        "$TMPL" > "$DEST"
    CREATED_ITEMS+=("$DEST")
    print_success "Rendered .claude/project_instructions.md"
fi

# Drop AGENTS.md at the project root for tools that read it natively.
# Strip CRLF in case the source was checked out on Windows with autocrlf — the
# generator's contract is LF-only, and tools shouldn't see a mixed-line-ending
# file just because of where the user cloned the repo.
if [ -f "$SOURCE_ROOT/AGENTS.md" ]; then
    tr -d '\r' < "$SOURCE_ROOT/AGENTS.md" > "$PROJECT_ROOT/AGENTS.md"
    CREATED_ITEMS+=("$PROJECT_ROOT/AGENTS.md")
    print_success "Installed AGENTS.md at project root"
fi
```

(`SOURCE_ROOT` already points at `product/` in the existing installer; do not change that.)

- [ ] **Step 3: Smoke**

Run a real mock install in a temp dir:

```bash
TMP=$(mktemp -d)
cd "$TMP" && mkdir -p .log-file-genius/product
cp -r /c/Users/clark/Code/log-file-genius/product/* .log-file-genius/product/
mkdir .claude
bash /c/Users/clark/Code/log-file-genius/product/scripts/install.sh \
    --profile solo-developer --ai-assistant claude-code --force
ls .claude/rules/ .claude/project_instructions.md AGENTS.md
```

Expected: rules present; `project_instructions.md` rendered with `logs/...` paths; `AGENTS.md` at root.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/install.sh
git commit -m "feat(install.sh): generate per-tool rules from fragments; render template; drop AGENTS.md"
```

### Task 16: `install.ps1` — mirror

**Files:**
- Modify: `product/scripts/install.ps1`

- [ ] **Step 1: Apply the mirror of Task 15's logic** in PowerShell. Read the existing rules-install section first. Replace with:

```powershell
switch ($AiAssistant) {
    "augment"     { $rulesTarget = "augment_rules"; $rulesDest = Join-Path $ProjectRoot ".augment\rules" }
    "claude-code" { $rulesTarget = "claude_rules";  $rulesDest = Join-Path $ProjectRoot ".claude\rules"  }
    default       { Rollback-Installation "Unknown assistant: $AiAssistant" }
}

if (-not (Test-Path $rulesDest)) { New-Item -ItemType Directory -Path $rulesDest -Force | Out-Null }

Get-ChildItem -Path (Join-Path $SourceRoot "rules") -Filter "*.md" | ForEach-Object {
    $text = Get-Content $_.FullName -Raw
    # Extract frontmatter block
    if ($text -match "(?ms)^---\s*\r?\n(.*?)\r?\n---") {
        $fm = $Matches[1]
        if ($fm -match "(?m)^targets:\s*(.+)$") {
            $targets = ($Matches[1] -replace '\[|\]','' -split ',' | ForEach-Object { $_.Trim() })
            if ($targets -contains $rulesTarget) {
                $dest = Join-Path $rulesDest $_.Name
                Copy-Item -Path $_.FullName -Destination $dest -Force
                $CreatedItems += $dest
                Print-Success "Installed $($_.Name)"
            }
        }
    }
}

if ($AiAssistant -eq "claude-code") {
    $tmpl = Join-Path $SourceRoot "install-templates\claude\project_instructions.md.tmpl"
    $dest = Join-Path $ProjectRoot ".claude\project_instructions.md"
    $rendered = (Get-Content $tmpl -Raw) `
        -replace '\{\{paths\.changelog\}\}','logs/CHANGELOG.md' `
        -replace '\{\{paths\.devlog\}\}','logs/DEVLOG.md' `
        -replace '\{\{paths\.state\}\}','logs/STATE.md' `
        -replace '\{\{paths\.adr_dir\}\}','logs/adr/'
    # Spec requires no BOM. Windows PowerShell 5.1's `Set-Content -Encoding utf8`
    # writes UTF-8 *with* BOM, so use .NET directly with a no-BOM encoding.
    [System.IO.File]::WriteAllText($dest, $rendered, (New-Object System.Text.UTF8Encoding $false))
    $CreatedItems += $dest
    Print-Success "Rendered .claude/project_instructions.md"
}

$agentsSrc = Join-Path $SourceRoot "AGENTS.md"
if (Test-Path $agentsSrc) {
    # Re-emit with LF + no BOM in case the source was checked out CRLF.
    $agentsText = (Get-Content $agentsSrc -Raw) -replace "`r`n", "`n"
    $agentsDest = Join-Path $ProjectRoot "AGENTS.md"
    [System.IO.File]::WriteAllText($agentsDest, $agentsText, (New-Object System.Text.UTF8Encoding $false))
    $CreatedItems += $agentsDest
    Print-Success "Installed AGENTS.md at project root"
}
```

- [ ] **Step 2: Smoke**

```powershell
$TMP = New-TemporaryFile | %{ Remove-Item $_; New-Item -Type Directory $_ }
Push-Location $TMP
New-Item -Type Directory -Path .log-file-genius/product -Force | Out-Null
Copy-Item -Recurse C:\Users\clark\Code\log-file-genius\product\* .log-file-genius\product\
New-Item -Type Directory .claude | Out-Null
powershell -NoProfile -File C:\Users\clark\Code\log-file-genius\product\scripts\install.ps1 -Profile solo-developer -AiAssistant claude-code -Force
Get-ChildItem .claude\rules\, .claude\project_instructions.md, AGENTS.md
Pop-Location
```

- [ ] **Step 3: Commit**

```bash
git add product/scripts/install.ps1
git commit -m "feat(install.ps1): mirror — fragments->per-tool rules, template render, AGENTS.md"
```

### Task 17: `update.sh` + `update.ps1` — same source path

**Files:**
- Modify: `product/scripts/update.sh`
- Modify: `product/scripts/update.ps1`

Update scripts must also source from `product/rules/` (not from any per-tool subdir, which no longer exists). The logic is identical to the installer's new logic.

- [ ] **Step 1: `update.sh` —** replace the rules-update section (the part that currently iterates `$SOURCE_ROOT/product/ai-rules/$AI_ASSISTANT/*.md`) with the same fragment-walking loop from Task 15 (the `for frag in "$SOURCE_ROOT/product/rules/"*.md` block — note the `product/` prefix here, because update.sh's `$SOURCE_ROOT` is the submodule root, not `product/`). Also add the AGENTS.md copy step.

- [ ] **Step 2: `update.ps1` —** mirror, similarly adjusting paths to include `product\rules`.

- [ ] **Step 3: Commit**

```bash
git add product/scripts/update.sh product/scripts/update.ps1
git commit -m "feat(update): source rules from product/rules fragments; copy AGENTS.md"
```

### Task 18: Updated cross-platform smoke tests

**Files:**
- Modify: `product/tests/smoke_install.sh`
- Modify: `product/tests/smoke_install.ps1`

The Spec 1 smoke test must be updated for the new layout (AGENTS.md exists at root; `.claude/rules/log-file-maintenance.md` came from `product/rules/`, not `product/ai-rules/claude-code/`).

- [ ] **Step 1: `smoke_install.sh` —** add these assertions after the existing checks:

```bash
# Spec 2: AGENTS.md must land at project root.
test -f AGENTS.md || { echo "FAIL: AGENTS.md missing at project root"; exit 1; }
head -1 AGENTS.md | grep -q '^---$' || { echo "FAIL: AGENTS.md missing frontmatter"; exit 1; }

# Spec 2: AGENTS.md must be LF + no BOM (generator's documented contract).
if grep -q $'\r' AGENTS.md; then echo "FAIL: AGENTS.md has CRLF line endings"; exit 1; fi
head -c 3 AGENTS.md | grep -q $'\xEF\xBB\xBF' && { echo "FAIL: AGENTS.md has UTF-8 BOM"; exit 1; }

# Spec 2: installed rule must equal the canonical fragment.
diff -q .claude/rules/log-file-maintenance.md \
    "$REPO/product/rules/log-file-maintenance.md" \
    || { echo "FAIL: installed rule != canonical fragment"; exit 1; }
```

Also remove or update the older Spec 1 assertion that compared against `product/ai-rules/claude-code/...`.

- [ ] **Step 2: `smoke_install.ps1` —** apply the mirror changes.

- [ ] **Step 3: Run both**

```bash
bash product/tests/smoke_install.sh
powershell -NoProfile -File product/tests/smoke_install.ps1
```

Expected: both PASS.

- [ ] **Step 4: Commit**

```bash
git add product/tests/smoke_install.sh product/tests/smoke_install.ps1
git commit -m "test(smoke): assert AGENTS.md and canonical fragment match"
```

---

## Phase 7 — CI, cold-read, docs, cleanup

### Task 19: CI runs `lfg generate --check`

**Files:**
- Modify: `.github/workflows/test-installer.yml` (or equivalent)

- [ ] **Step 1: Read the existing workflow** to find an appropriate job to extend.

- [ ] **Step 2: Add a job** (or step in an existing job) that runs the generator check:

```yaml
  generate-check:
    name: Verify AGENTS.md is up to date
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - name: Verify AGENTS.md matches fragments
        run: python product/scripts/lfg.py generate --check
```

- [ ] **Step 3: Commit**

```bash
git add .github/workflows/test-installer.yml
git commit -m "ci: run 'lfg generate --check' on every PR"
```

### Task 20: Cold-read fixture test

**Files:**
- Create: `product/tests/test_cold_read.py`

This is the spec's "surrogate for a cold agent could orient" test. The fixture reads `AGENTS.md`, follows its `related:` frontmatter to STATE/CHANGELOG/DEVLOG, and asserts each is reachable.

- [ ] **Step 1: Write the test**

```python
# product/tests/test_cold_read.py
"""Cold-read: simulate what a fresh agent does when handed AGENTS.md.

Reads AGENTS.md's frontmatter `related:` map and verifies each target file
exists and is non-empty. This is not an LLM test — it's an assertion that
the artifact's stated navigation graph actually leads somewhere.
"""
import re
import shutil
import subprocess
import sys
from pathlib import Path
import tempfile

REPO = Path(__file__).resolve().parents[2]


def _install_into(tmp: Path) -> None:
    (tmp / ".claude").mkdir()
    submodule = tmp / ".log-file-genius" / "product"
    submodule.mkdir(parents=True)
    # Cross-platform copy (don't shell out to `cp`, which is Unix-only).
    for item in (REPO / "product").iterdir():
        target = submodule / item.name
        if item.is_dir():
            shutil.copytree(item, target)
        else:
            shutil.copy2(item, target)
    subprocess.check_call(
        ["bash", str(REPO / "product/scripts/install.sh"),
         "--profile", "solo-developer", "--ai-assistant", "claude-code", "--force"],
        cwd=tmp,
        stdout=subprocess.DEVNULL,
    )


def test_agents_md_related_map_resolves():
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td)
        _install_into(tmp)
        agents = (tmp / "AGENTS.md").read_text(encoding="utf-8")
        # Pull the related: block (lines indented under 'related:').
        m = re.search(r"(?ms)^related:\n((?:  .+\n)+)", agents)
        assert m, "AGENTS.md missing 'related:' frontmatter block"
        targets = []
        for line in m.group(1).splitlines():
            mm = re.match(r"^\s+\w+:\s*(\S+)", line)
            if mm:
                targets.append(mm.group(1))
        assert targets, "no related: entries parsed"
        for rel in targets:
            target = (tmp / rel).resolve()
            assert target.exists(), f"AGENTS.md points at {rel} but it does not exist after install"
            assert target.stat().st_size > 0, f"{rel} is empty"
```

- [ ] **Step 2: Run**

```bash
python -m pytest product/tests/test_cold_read.py -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_cold_read.py
git commit -m "test: cold-read fixture — AGENTS.md related: map resolves on a fresh install"
```

### Task 21: CONTRIBUTING.md acknowledges Python build dep + pre-commit hook

**Files:**
- Modify: `CONTRIBUTING.md`
- Create: `product/scripts/pre-commit-regen` (referenced from CONTRIBUTING)

- [ ] **Step 1: Add a section to `CONTRIBUTING.md`** (before the existing development instructions; tone-match the file):

```markdown
## Build-time dependency: Python 3.11+

LFG remains **zero-dependency at runtime for users** — the installer, validators,
and pre-commit hook are stdlib-only.

For **contributors**, Python 3.11+ is required to regenerate `product/AGENTS.md`
from the canonical fragments in `product/rules/`. After editing any fragment, run:

```bash
python product/scripts/lfg.py generate
```

CI runs `lfg generate --check` on every PR and will fail if `AGENTS.md` is out
of date relative to the fragments. To avoid forgetting, install the pre-commit
hook below.

### Optional: pre-commit auto-regenerate

```bash
cp product/scripts/pre-commit-regen .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

This hook regenerates `product/AGENTS.md` automatically whenever you stage
changes under `product/rules/` and re-adds the updated `AGENTS.md` to the commit.
```

- [ ] **Step 2: Create `product/scripts/pre-commit-regen`**

```bash
#!/usr/bin/env bash
# Auto-regenerate AGENTS.md when fragments are staged.
set -e
if git diff --cached --name-only | grep -q '^product/rules/'; then
    python product/scripts/lfg.py generate
    git add product/AGENTS.md
fi
```

- [ ] **Step 3: Commit**

```bash
git add CONTRIBUTING.md product/scripts/pre-commit-regen
git commit -m "docs: acknowledge Python build-time dep; add pre-commit regen hook"
```

### Task 22: Delete `product/ai-rules/`; update remaining references

**Files:**
- Delete: `product/ai-rules/` (entire directory)
- Modify: any remaining file referencing the old path

- [ ] **Step 1: Audit for remaining references**

```bash
grep -rn "ai-rules" product/ README.md INSTALL.md CONTRIBUTING.md .github/ 2>/dev/null
```

- [ ] **Step 2: For each reference**, update to either `product/rules/` (canonical), `product/install-templates/claude/` (template), or remove if obsolete.

- [ ] **Step 3: Delete the directory**

```bash
git rm -r product/ai-rules
```

- [ ] **Step 4: Re-run the full test battery**

```bash
python -m pytest product/tests/ -q
bash product/tests/smoke_install.sh
powershell -NoProfile -File product/tests/smoke_install.ps1
```

Expected: all green.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "refactor: remove product/ai-rules/ (replaced by product/rules/ canonical)"
```

### Task 23: `log_file_how_to.md` documents the canonical-fragments + generator model

**Files:**
- Modify: `product/docs/log_file_how_to.md`

- [ ] **Step 1: Find the section** describing the AI-rules layout or extension model:

```bash
grep -n "ai-rules\|rules\|fragment\|generate" product/docs/log_file_how_to.md | head
```

- [ ] **Step 2: Add or update a section** explaining: fragments under `product/rules/` are canonical; `AGENTS.md` is generated; per-tool rule directories are generated at install time; the only command contributors need is `python product/scripts/lfg.py generate`. Two paragraphs is enough.

- [ ] **Step 3: Commit**

```bash
git add product/docs/log_file_how_to.md
git commit -m "docs(how-to): document canonical-fragments + generator model"
```

---

## Final verification

- [ ] **Full pytest**

```bash
python -m pytest product/tests/ -v
```

Expected: all PASS, no skips, no warnings.

- [ ] **Cross-platform smoke**

```bash
bash product/tests/smoke_install.sh
powershell -NoProfile -File product/tests/smoke_install.ps1
```

- [ ] **Generator gate (mirrors CI)**

```bash
python product/scripts/lfg.py generate --check
```

Expected: exit 0, no output.

- [ ] **`lfg.py --help` lists all 10 subcommands**

```bash
python product/scripts/lfg.py --help
```

Expected output mentions: `validate`, `lint`, `secrets`, `check-version`, `check-rules`, `status`, `install-hooks`, `generate`, `prime`, `promote`.

- [ ] **No stragglers**

```bash
grep -rn "ai-rules\|starter-packs" product/ README.md INSTALL.md CONTRIBUTING.md 2>/dev/null
```

Expected: no output.

---

## Spec coverage map

- Architecture (canonical fragments; AGENTS.md committed; no install-payload) → Tasks 1, 5-6, 22
- Fragment frontmatter (replaces _index.md) → Task 2
- Fragment content scrub (no tool paths) → Tasks 3, 4
- `lfg generate [--check]` → Tasks 5, 6, 19
- LF/UTF-8/no-BOM/trailing newline → Task 5 (rendering); Task 6 (writer)
- 3000-token budget hard gate → Task 5 (in renderer)
- `lfg prime` + LFG_SUBAGENT_PRIME marker → Tasks 7, 8
- `lfg promote <id>` + staged writes + audit log → Tasks 9, 10
- Subagent contract block in rules → Task 11
- CHANGELOG self-application rule → Task 12
- AGENTS.md content (frontmatter, read-first, commands, index, fragments) → Task 5 (renderer)
- Claude project_instructions template → Task 14
- Installer / update / both platforms → Tasks 15, 16, 17, 18
- Cold-read fixture → Task 20
- CONTRIBUTING.md Python build-dep + pre-commit hook → Task 21
- Tests (10 from spec) → Tasks 4, 5, 6, 7, 9, 18, 20

## Out-of-scope reminders (per spec §Non-goals)

- Graceful work-aware archival → Spec 3
- Tools beyond Claude Code + Augment getting per-tool dirs
- `lfg tokens`, `lfg session-start`, or other CLI verbs
- Multi-agent concurrent coordination (STATE Active Work formalization)
- `lfg prime --topic` (deliberately removed during review)
