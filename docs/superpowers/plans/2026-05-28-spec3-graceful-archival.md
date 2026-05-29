# LFG Spec 3 — Graceful Work-Aware Archival Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the LLM-driven "archive oldest entries by token count" rule with a deterministic `lfg archive` CLI verb that protects in-flight work (CHANGELOG's `[Unreleased]`, DEVLOG's recent entries) and requires explicit confirmation before moving anything.

**Architecture:** A pure-Python `archive.py` module parses CHANGELOG and DEVLOG, builds an `ArchivePlan` (sequence of `ArchiveAction`s with source slices, destination paths, summary lines), and exposes `apply()` for execution. `lfg.py` wires it as the `archive` subcommand with `--dry-run` (default preview), `--force` (skip prompt), and per-file scoping flags. Pure-function planner + I/O-side `apply()` mirrors Spec 2's generator pattern.

**Tech Stack:** Python 3.11+ (stdlib only — no new deps), Markdown with YAML frontmatter, pytest. Reuses Spec 1's `config_parser` for `.logfile-config.yml` lookup.

**Source spec:** `docs/superpowers/specs/2026-05-28-spec3-graceful-archival-design.md`

---

## Design decisions baked in (from approved spec)

1. **Deterministic CLI verb** (`lfg archive`), not LLM-driven.
2. **Work-aware signals** are file-specific from existing structure:
   - CHANGELOG: `## [Unreleased]` is always protected.
   - DEVLOG: fit-the-budget — newest entries summing to `keep_fraction * budget` are protected.
   - STATE / ADRs: never archive.
3. **One configurable knob**: `keep_fraction` (default 0.8), exposed via `.logfile-config.yml` / profile, **not** as a CLI flag.
4. **Archive filenames** are self-documenting ranges:
   - `logs/archive/CHANGELOG-v<earliest>-to-v<latest>.md`
   - `logs/archive/DEVLOG-<earliest-date>-to-<latest-date>.md`
5. **Default behavior** is `--dry-run` preview + prompt; `--force` skips the prompt.
6. **Refusal-only** edge cases — no `--force-include-unreleased` escape hatch. If `[Unreleased]` exceeds budget alone, exit 2; user must trim manually.
7. **Combined-budget overflow** handled by decrementing `keep_fraction` for DEVLOG (floor 0.3); CHANGELOG isn't touched further.

## Canonical constants (single set, must match exactly)

```python
DEFAULT_KEEP_FRACTION = 0.8       # default if no profile override
COMBINED_KEEP_FRACTION_FLOOR = 0.3  # don't archive DEVLOG below this
# Token budgets come from .logfile-config.yml `token_targets:` block (Spec 1):
#   changelog: 10000, devlog: 15000, combined: 25000
```

## File structure

- **`product/scripts/archive.py`** — new pure module. Parses CHANGELOG/DEVLOG, builds `ArchivePlan`, applies it. Reuses `config_parser`.
- **`product/scripts/lfg.py`** — modified. Adds `cmd_archive(args)` + subparser registration (consistent with `cmd_generate`/`cmd_prime`/`cmd_promote`).
- **`product/scripts/lint-logs.py`** — modified. One-line hint update in the over-budget messages.
- **`product/scripts/validate-log-files.sh`** + **`validate-log-files.ps1`** — modified. Same hint update.
- **`product/rules/log-file-maintenance.md`** — modified. Shrink the `🗄️ ARCHIVAL` section to a one-sentence pointer at `lfg archive`.
- **`product/profiles/*.yml`** — modified. Reduce `archival:` block to a single key (`keep_fraction`).
- **`product/AGENTS.md`** — regenerated after the fragment change.
- **`product/docs/log_file_how_to.md`** — modified. Document the deterministic archival workflow.
- **`product/tests/test_archive.py`** — new. All 11 tests from the spec.

---

## Phase 1 — Pure planner (archive.py)

### Task 1: Scaffold archive.py with dataclasses + token estimator + CHANGELOG parser

**Files:**
- Create: `product/scripts/archive.py`
- Test: `product/tests/test_archive.py`

- [ ] **Step 1: Write the failing test**

```python
# product/tests/test_archive.py
import textwrap
from pathlib import Path
import pytest
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from archive import (
    parse_changelog, ArchivePlan, ArchiveAction, _estimate_tokens,
    DEFAULT_KEEP_FRACTION, COMBINED_KEEP_FRACTION_FLOOR,
)


def test_constants_match_spec():
    assert DEFAULT_KEEP_FRACTION == 0.8
    assert COMBINED_KEEP_FRACTION_FLOOR == 0.3


def test_estimate_tokens_is_chars_div_4():
    assert _estimate_tokens("") == 0
    assert _estimate_tokens("a" * 8) == 2
    assert _estimate_tokens("a" * 100) == 25


def test_parse_changelog_separates_sections():
    text = textwrap.dedent("""\
        ---
        doc: CHANGELOG
        ---

        # Changelog

        ## [Unreleased]

        ### Added
        - In-flight work A.

        ## [0.2.0] - 2026-05-01

        ### Added
        - Spec 2 shipped.

        ## [0.1.0] - 2026-04-01

        ### Added
        - Spec 1 shipped.
    """)
    parsed = parse_changelog(text)
    assert parsed["header"].startswith("---\ndoc: CHANGELOG\n---")
    assert "[Unreleased]" in parsed["unreleased"]
    assert "In-flight work A" in parsed["unreleased"]
    assert len(parsed["versions"]) == 2
    assert parsed["versions"][0]["version"] == "0.2.0"
    assert "Spec 2 shipped" in parsed["versions"][0]["content"]
    assert parsed["versions"][1]["version"] == "0.1.0"
    assert parsed["archive_section"] == ""  # no Archive section yet


def test_parse_changelog_preserves_archive_section():
    text = textwrap.dedent("""\
        # Changelog

        ## [Unreleased]
        - x

        ## [0.1.0] - 2026-04-01
        - old

        ## Archive

        - [CHANGELOG-v0.0.1-to-v0.0.9.md](archive/CHANGELOG-v0.0.1-to-v0.0.9.md) — early versions
    """)
    parsed = parse_changelog(text)
    assert "## Archive" in parsed["archive_section"]
    assert "CHANGELOG-v0.0.1-to-v0.0.9.md" in parsed["archive_section"]


def test_parse_changelog_no_unreleased_raises():
    text = "# Changelog\n\n## [0.1.0] - 2026-04-01\n- old\n"
    with pytest.raises(ValueError, match="missing.*Unreleased"):
        parse_changelog(text)
```

- [ ] **Step 2: Run, see fail**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: `ModuleNotFoundError: No module named 'archive'`.

- [ ] **Step 3: Implement archive.py (scaffold + CHANGELOG parser)**

```python
"""Graceful work-aware archival for LFG CHANGELOG and DEVLOG.

Pure-planning module: parse_changelog / parse_devlog parse the source; build_plan
returns an ArchivePlan (sequence of ArchiveAction); apply(plan) does the I/O.
No I/O in the planner — same testability pattern as Spec 2's generator.py.

The two work-aware signals:
  - CHANGELOG: protect ## [Unreleased]; archive released version blocks.
  - DEVLOG: fit-the-budget — keep newest entries summing to keep_fraction * budget,
    archive the rest.
STATE and ADRs never archive.
"""
from __future__ import annotations
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Reuse Spec 1's stdlib config parser. Sibling-module import (Spec 2 pattern).
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_parser import parse_config

DEFAULT_KEEP_FRACTION = 0.8
COMBINED_KEEP_FRACTION_FLOOR = 0.3


class ArchiveError(ValueError):
    pass


@dataclass
class ArchiveAction:
    """One file's-worth of archive movement."""
    source_path: Path
    archive_path: Path
    moved_content: str          # what goes INTO the archive file (minus header)
    summary_line: str           # the bullet to append to source's ## Archive
    tokens_before: int
    tokens_after: int


@dataclass
class ArchivePlan:
    actions: List[ArchiveAction] = field(default_factory=list)
    refusal_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.actions and not self.refusal_reasons

    def to_human(self) -> str:
        """Human-readable dry-run summary."""
        if not self.actions and not self.refusal_reasons:
            return "Nothing to archive — all log files within budget."
        out: List[str] = []
        for r in self.refusal_reasons:
            out.append(f"REFUSED: {r}")
        for a in self.actions:
            out.append(
                f"Move from {a.source_path.name} -> {a.archive_path}\n"
                f"  Tokens: {a.tokens_before} -> {a.tokens_after}\n"
                f"  Summary: {a.summary_line}"
            )
        for w in self.warnings:
            out.append(f"WARNING: {w}")
        return "\n\n".join(out)


def _estimate_tokens(text: str) -> int:
    """Match Spec 1's canonical chars/4 heuristic."""
    return len(text) // 4


# ----- CHANGELOG parser -----

# A "## [X.Y.Z] - date" or "## [X.Y.Z] — date" version header.
_VERSION_RE = re.compile(r"^##\s+\[(?P<ver>[^\]]+)\]\s*[\-–—]?\s*(?P<date>\S*)\s*$")
_UNRELEASED_RE = re.compile(r"^##\s+\[Unreleased\]\s*$", re.IGNORECASE)
_ARCHIVE_HEADER_RE = re.compile(r"^##\s+Archive\s*$", re.IGNORECASE)


def parse_changelog(text: str) -> Dict[str, Any]:
    """Parse a Keep-a-Changelog CHANGELOG into structured sections.

    Returns {header, unreleased, versions, archive_section} where:
      - header: everything before the [Unreleased] section.
      - unreleased: the [Unreleased] section (heading + content, exclusive of next ##).
      - versions: list of {'version': str, 'header_line': str, 'content': str},
        ordered as they appear in the file (newest first by convention).
      - archive_section: the ## Archive heading + content if present, else "".

    Raises ArchiveError if no [Unreleased] section exists (Spec 3 requires
    Keep-a-Changelog format; a clean refusal is better than silent destruction).
    """
    lines = text.splitlines(keepends=True)
    n = len(lines)

    # Locate [Unreleased] heading.
    u_start = next(
        (i for i, ln in enumerate(lines) if _UNRELEASED_RE.match(ln)),
        None,
    )
    if u_start is None:
        raise ArchiveError(
            "CHANGELOG missing '## [Unreleased]' section "
            "(Keep-a-Changelog format required for archival)"
        )

    header = "".join(lines[:u_start])

    # Find end of [Unreleased] (next ## heading).
    next_h = next(
        (i for i in range(u_start + 1, n) if lines[i].startswith("## ")),
        n,
    )
    unreleased = "".join(lines[u_start:next_h])

    # Walk version + Archive sections.
    versions: List[Dict[str, str]] = []
    archive_section = ""
    i = next_h
    while i < n:
        m = _VERSION_RE.match(lines[i])
        if m:
            v_start = i
            v_end = next(
                (j for j in range(i + 1, n) if lines[j].startswith("## ")),
                n,
            )
            versions.append({
                "version": m.group("ver"),
                "header_line": lines[v_start],
                "content": "".join(lines[v_start:v_end]),
            })
            i = v_end
            continue
        if _ARCHIVE_HEADER_RE.match(lines[i]):
            a_end = next(
                (j for j in range(i + 1, n) if lines[j].startswith("## ")),
                n,
            )
            archive_section = "".join(lines[i:a_end])
            i = a_end
            continue
        i += 1

    return {
        "header": header,
        "unreleased": unreleased,
        "versions": versions,
        "archive_section": archive_section,
    }
```

- [ ] **Step 4: Run tests, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): scaffold + CHANGELOG parser (Spec 3 T1)"
```

### Task 2: DEVLOG parser

**Files:**
- Modify: `product/scripts/archive.py` (add `parse_devlog`)
- Modify: `product/tests/test_archive.py` (add tests)

- [ ] **Step 1: Add failing tests** (append to `test_archive.py`)

```python
from archive import parse_devlog


def test_parse_devlog_separates_entries_in_file_order():
    text = textwrap.dedent("""\
        ---
        doc: DEVLOG
        ---

        # Development Log

        ## Daily Log - Newest First

        ### 2026-05-28: Spec 3 design

        Newest entry content.

        ### 2026-05-27: Spec 2 shipped

        Middle entry.

        ### 2025-12-01: Late-2025 work

        Oldest entry.
    """)
    parsed = parse_devlog(text)
    assert "# Development Log" in parsed["header"]
    assert "## Daily Log" in parsed["daily_log_heading"]
    assert len(parsed["entries"]) == 3
    assert parsed["entries"][0]["date"] == "2026-05-28"
    assert "Newest entry" in parsed["entries"][0]["content"]
    assert parsed["entries"][1]["date"] == "2026-05-27"
    assert parsed["entries"][2]["date"] == "2025-12-01"
    assert parsed["archive_section"] == ""


def test_parse_devlog_preserves_archive_section():
    text = textwrap.dedent("""\
        # Development Log
        ## Daily Log - Newest First

        ### 2026-05-28: x
        a

        ## Archive

        - [DEVLOG-2025-10.md](archive/DEVLOG-2025-10.md) - early
    """)
    parsed = parse_devlog(text)
    assert "DEVLOG-2025-10.md" in parsed["archive_section"]


def test_parse_devlog_no_daily_log_heading_raises():
    text = "# Development Log\n\n### 2026-05-28: orphan entry\n"
    with pytest.raises(ArchiveError, match="missing.*Daily Log"):
        parse_devlog(text)


def test_parse_devlog_no_entries_empty_list():
    text = textwrap.dedent("""\
        # Development Log

        ## Daily Log - Newest First

        (no entries yet)
    """)
    parsed = parse_devlog(text)
    assert parsed["entries"] == []
```

Add `from archive import ArchiveError` to the existing test imports.

- [ ] **Step 2: Add `parse_devlog`** to `archive.py` (after `parse_changelog`)

```python
# ----- DEVLOG parser -----

_DAILY_LOG_RE = re.compile(r"^##\s+Daily Log\b", re.IGNORECASE)
_DEVLOG_ENTRY_RE = re.compile(
    r"^###\s+(?P<date>\d{4}-\d{2}-\d{2})\s*:?\s*(?P<title>.*?)\s*$"
)


def parse_devlog(text: str) -> Dict[str, Any]:
    """Parse a DEVLOG into header / daily-log heading / entries / archive section.

    Returns {header, daily_log_heading, entries, archive_section} where:
      - header: everything before "## Daily Log".
      - daily_log_heading: the "## Daily Log..." line itself.
      - entries: list of {'date': 'YYYY-MM-DD', 'title': str, 'content': str},
        in file order (newest-first by convention).
      - archive_section: "## Archive" + content if present, else "".

    Raises ArchiveError if no "## Daily Log" heading.
    """
    lines = text.splitlines(keepends=True)
    n = len(lines)

    dl_idx = next((i for i, ln in enumerate(lines) if _DAILY_LOG_RE.match(ln)), None)
    if dl_idx is None:
        raise ArchiveError("DEVLOG missing '## Daily Log' heading")

    header = "".join(lines[:dl_idx])
    daily_log_heading = lines[dl_idx]

    # Locate Archive section if any.
    arch_idx = next(
        (i for i in range(dl_idx + 1, n) if _ARCHIVE_HEADER_RE.match(lines[i])),
        n,
    )
    archive_section = "".join(lines[arch_idx:n]) if arch_idx < n else ""

    # Walk entries within [dl_idx+1, arch_idx).
    entries: List[Dict[str, str]] = []
    i = dl_idx + 1
    while i < arch_idx:
        m = _DEVLOG_ENTRY_RE.match(lines[i])
        if m:
            e_start = i
            e_end = next(
                (j for j in range(i + 1, arch_idx)
                 if _DEVLOG_ENTRY_RE.match(lines[j]) or lines[j].startswith("## ")),
                arch_idx,
            )
            entries.append({
                "date": m.group("date"),
                "title": m.group("title").strip(),
                "content": "".join(lines[e_start:e_end]),
            })
            i = e_end
            continue
        i += 1

    return {
        "header": header,
        "daily_log_heading": daily_log_heading,
        "entries": entries,
        "archive_section": archive_section,
    }
```

- [ ] **Step 3: Run, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 8 tests PASS.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): DEVLOG parser (Spec 3 T2)"
```

### Task 3: CHANGELOG plan builder

**Files:**
- Modify: `product/scripts/archive.py` (add `_plan_changelog`)
- Modify: `product/tests/test_archive.py` (add tests)

- [ ] **Step 1: Add failing tests**

```python
from archive import _plan_changelog


def _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500):
    """Build a CHANGELOG with controlled token counts."""
    unreleased_body = "- " + ("x" * (unreleased_tokens * 4 - 2)) + "\n"
    versions = ""
    for i in range(version_count, 0, -1):  # newest first: v0.5 down to v0.1
        body = "- " + ("x" * (version_tokens * 4 - 2)) + "\n"
        versions += f"## [0.{i}.0] - 2026-0{i}-01\n\n{body}\n"
    return f"# Changelog\n\n## [Unreleased]\n\n{unreleased_body}\n{versions}"


def test_plan_changelog_archives_oldest_versions_until_under_budget(tmp_path):
    # Budget 10000; unreleased=200; 5 versions x 2500 tokens = 12700 total + headers.
    text = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert not refusals
    assert len(actions) == 1
    action = actions[0]
    # 0.8 * 10000 = 8000 target. Unreleased ~200. Need to remove at least 4700 from 12500 of versions.
    # Oldest first: 0.1.0 (2500), 0.2.0 (2500) = 5000 removed → 7500 versions remain.
    assert action.tokens_after <= 8000
    assert "v0.1.0" in str(action.archive_path) or "0.1.0" in str(action.archive_path)
    # Archive content contains oldest blocks.
    assert "[0.1.0]" in action.moved_content


def test_plan_changelog_refuses_when_unreleased_alone_over_budget(tmp_path):
    # Unreleased alone = 11000 tokens; budget = 10000.
    text = _make_changelog(unreleased_tokens=11_000, version_count=2, version_tokens=500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert actions == []
    assert any("Unreleased" in r for r in refusals)


def test_plan_changelog_no_action_when_already_under_budget(tmp_path):
    text = _make_changelog(unreleased_tokens=100, version_count=2, version_tokens=500)
    src = tmp_path / "CHANGELOG.md"
    actions, refusals, warnings = _plan_changelog(
        text=text, source_path=src, budget=10_000, keep_fraction=0.8,
    )
    assert actions == []
    assert refusals == []
```

- [ ] **Step 2: Add `_plan_changelog`** to `archive.py`

```python
# ----- CHANGELOG plan builder -----

def _plan_changelog(
    *,
    text: str,
    source_path: Path,
    budget: int,
    keep_fraction: float,
) -> Tuple[List[ArchiveAction], List[str], List[str]]:
    """Return (actions, refusal_reasons, warnings) for CHANGELOG archival."""
    parsed = parse_changelog(text)
    target = int(budget * keep_fraction)

    current_tokens = _estimate_tokens(text)
    if current_tokens <= target:
        return [], [], []

    protected = (
        _estimate_tokens(parsed["header"])
        + _estimate_tokens(parsed["unreleased"])
        + _estimate_tokens(parsed["archive_section"])
    )
    if protected > budget:
        return [], [
            f"CHANGELOG protected sections (header + [Unreleased] + Archive) "
            f"already total {protected} tokens, over budget {budget}. "
            f"Trim [Unreleased] before archiving."
        ], []

    # Walk versions OLDEST first. The parser keeps file-order (newest first by
    # convention), so reverse.
    versions = parsed["versions"]
    versions_by_age = list(reversed(versions))  # oldest first

    to_archive: List[Dict[str, str]] = []
    remaining_versions = list(versions)  # mutable copy
    # Need to bring total down to <= target. Removing oldest first.
    running_total = current_tokens
    for v in versions_by_age:
        if running_total <= target:
            break
        v_tokens = _estimate_tokens(v["content"])
        to_archive.append(v)
        remaining_versions.remove(v)
        running_total -= v_tokens

    if not to_archive:
        return [], [], []

    # Oldest-first ordering for the archive file content.
    to_archive_oldest_first = to_archive  # already oldest-first
    archive_content = "".join(v["content"] for v in to_archive_oldest_first)

    earliest = to_archive_oldest_first[0]["version"]
    latest = to_archive_oldest_first[-1]["version"]
    archive_name = f"CHANGELOG-v{earliest}-to-v{latest}.md"
    archive_path = source_path.parent / "archive" / archive_name

    summary_line = (
        f"- [{archive_name}](archive/{archive_name}) — "
        f"versions v{earliest} through v{latest}; archived "
        f"~{_estimate_tokens(archive_content)} tokens, {len(to_archive)} version blocks"
    )

    return [
        ArchiveAction(
            source_path=source_path,
            archive_path=archive_path,
            moved_content=archive_content,
            summary_line=summary_line,
            tokens_before=current_tokens,
            tokens_after=running_total,
        )
    ], [], []
```

- [ ] **Step 3: Run, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 11 PASS.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): CHANGELOG plan builder + refusal on oversize Unreleased (Spec 3 T3)"
```

### Task 4: DEVLOG fit-the-budget plan builder

**Files:**
- Modify: `product/scripts/archive.py`
- Modify: `product/tests/test_archive.py`

- [ ] **Step 1: Add failing tests**

```python
from archive import _plan_devlog


def _make_devlog(entry_token_sizes: List[int]):
    """Build a DEVLOG; entry_token_sizes[i] in tokens for the i-th entry (newest first)."""
    header = "# Development Log\n\n## Daily Log - Newest First\n\n"
    entries = []
    base_date = 28
    for i, t in enumerate(entry_token_sizes):
        # date counts down from 2026-05-28
        date = f"2026-05-{base_date - i:02d}"
        body = "x" * (t * 4)
        entries.append(f"### {date}: entry {i}\n\n{body}\n\n")
    return header + "".join(entries)


def test_plan_devlog_keeps_newest_entries_fitting_keep_fraction(tmp_path):
    # Budget 15000, keep_fraction 0.8 → target 12000.
    # 5 entries x 3000 tokens each = 15000 total + headers.
    # Newest 4 (12000) fit; 5th must archive.
    text = _make_devlog([3000] * 5)
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    assert refusals == []
    assert len(actions) == 1
    # Oldest entry (entry 4 → 2026-05-24) was archived.
    assert "2026-05-24" in actions[0].moved_content
    # Newest (entry 0 → 2026-05-28) was NOT.
    assert "2026-05-28" not in actions[0].moved_content


def test_plan_devlog_no_action_when_under_budget(tmp_path):
    text = _make_devlog([1000] * 3)  # 3000 tokens total
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    assert actions == [] and refusals == []


def test_plan_devlog_warns_when_single_newest_oversize(tmp_path):
    # Budget 15000, keep_fraction 0.8 → target 12000.
    # Newest entry alone is 13000 tokens (> 12000) — it stays, warning emitted.
    text = _make_devlog([13000, 1000, 1000])
    src = tmp_path / "DEVLOG.md"
    actions, refusals, warnings = _plan_devlog(
        text=text, source_path=src, budget=15_000, keep_fraction=0.8,
    )
    # The newest stays. Older entries may still archive if they push over.
    if actions:
        assert "2026-05-28" not in actions[0].moved_content  # newest preserved
    assert any("newest" in w.lower() and "oversize" in w.lower() for w in warnings)
```

- [ ] **Step 2: Add `_plan_devlog`** to `archive.py`

```python
# ----- DEVLOG plan builder -----

def _plan_devlog(
    *,
    text: str,
    source_path: Path,
    budget: int,
    keep_fraction: float,
) -> Tuple[List[ArchiveAction], List[str], List[str]]:
    """Return (actions, refusal_reasons, warnings) for DEVLOG archival."""
    parsed = parse_devlog(text)
    target = int(budget * keep_fraction)

    current_tokens = _estimate_tokens(text)
    if current_tokens <= target:
        return [], [], []

    entries = parsed["entries"]  # newest-first in file order
    if not entries:
        return [], [], []

    # Fit-the-budget walk: accumulate newest-first; archive remainder.
    protected_overhead = (
        _estimate_tokens(parsed["header"])
        + _estimate_tokens(parsed["daily_log_heading"])
        + _estimate_tokens(parsed["archive_section"])
    )

    warnings: List[str] = []
    keep_cutoff = 0  # index up to which entries are kept (exclusive)
    cumulative = protected_overhead
    newest_tokens = _estimate_tokens(entries[0]["content"])
    if newest_tokens > target - protected_overhead:
        warnings.append(
            f"Newest DEVLOG entry ({entries[0]['date']}) is {newest_tokens} tokens, "
            f"oversize for keep_fraction*budget = {target}. It stays; consider trimming."
        )
        # Force-keep the newest entry even though it blows the budget.
        cumulative += newest_tokens
        keep_cutoff = 1

    for i in range(keep_cutoff, len(entries)):
        e_tokens = _estimate_tokens(entries[i]["content"])
        if cumulative + e_tokens > target:
            break
        cumulative += e_tokens
        keep_cutoff = i + 1

    if keep_cutoff >= len(entries):
        return [], [], warnings

    to_archive = entries[keep_cutoff:]  # oldest part
    # Sort to_archive oldest-first for the archive file (entries are newest-first).
    to_archive_oldest_first = list(reversed(to_archive))
    archive_content = "".join(e["content"] for e in to_archive_oldest_first)

    earliest_date = to_archive_oldest_first[0]["date"]
    latest_date = to_archive_oldest_first[-1]["date"]
    archive_name = f"DEVLOG-{earliest_date}-to-{latest_date}.md"
    archive_path = source_path.parent / "archive" / archive_name

    summary_line = (
        f"- [{archive_name}](archive/{archive_name}) — "
        f"entries {earliest_date} through {latest_date}; archived "
        f"~{_estimate_tokens(archive_content)} tokens, {len(to_archive)} entries"
    )

    after_tokens = cumulative  # the new total = protected + kept entries
    return [
        ArchiveAction(
            source_path=source_path,
            archive_path=archive_path,
            moved_content=archive_content,
            summary_line=summary_line,
            tokens_before=current_tokens,
            tokens_after=after_tokens,
        )
    ], [], warnings
```

- [ ] **Step 3: Run, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 14 PASS.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): DEVLOG fit-the-budget plan builder + newest-oversize warning (Spec 3 T4)"
```

### Task 5: Public `build_plan` + combined-overflow algorithm

**Files:**
- Modify: `product/scripts/archive.py`
- Modify: `product/tests/test_archive.py`

- [ ] **Step 1: Add failing tests**

```python
from archive import build_plan


def _write_minimal_config_and_logs(tmp_path,
                                    changelog_text: Optional[str] = None,
                                    devlog_text: Optional[str] = None):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 10000
          devlog: 15000
          combined: 25000
        archival:
          keep_fraction: 0.8
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir(exist_ok=True)
    if changelog_text:
        (tmp_path / "logs" / "CHANGELOG.md").write_text(changelog_text, encoding="utf-8")
    if devlog_text:
        (tmp_path / "logs" / "DEVLOG.md").write_text(devlog_text, encoding="utf-8")


def test_build_plan_reads_config_paths_and_budgets(tmp_path):
    _write_minimal_config_and_logs(
        tmp_path,
        changelog_text=_make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500),
        devlog_text=_make_devlog([1000] * 3),
    )
    plan = build_plan(tmp_path)
    # Only CHANGELOG over budget; DEVLOG fits.
    assert len(plan.actions) == 1
    assert "CHANGELOG" in plan.actions[0].source_path.name


def test_build_plan_combined_overflow_archives_more_devlog(tmp_path):
    # Individual files fit, combined overshoots → archive more DEVLOG.
    # CHANGELOG: 8000 tokens (under 10000).
    # DEVLOG: 12000 tokens (under 15000). Combined ~20000 — under 25000 actually.
    # Push combined over 25k: DEVLOG 18000 (over 15000 alone), CHANGELOG 8000.
    # First-pass: archive DEVLOG to 12000. Combined = 20000 — under.
    # That doesn't exercise the loop. Different shape:
    # CHANGELOG 9500 (just under 10000), DEVLOG 14500 (just under 15000). Combined = 24000 — under.
    # Make combined > 25000 with both individually fitting:
    # CHANGELOG 9500, DEVLOG 14900 → combined 24400. Still under.
    # The combined budget is 25000 — if both individually fit, combined automatically <= 25000? No:
    # CHANGELOG 9999 + DEVLOG 14999 = 24998. Under 25000.
    # Combined can only exceed when one is over.
    # Re-reading spec: "if both files are under their individual budgets but their combined still
    # exceeds 25k" — this would require sum to exceed 25000 with each under their own. With
    # budgets 10000+15000 = 25000, it's literally impossible to BOTH be under and combined over.
    # So the combined loop only kicks in when CHANGELOG individually fits but DEVLOG individually
    # is JUST under its 15k while combined exceeds 25k.
    # CHANGELOG 9000, DEVLOG 14900 = 23900. Still under 25000.
    # CHANGELOG 9999, DEVLOG 14999 = 24998. Just under.
    # I.e., with default budgets, combined-loop is dead code. Test for the explicit case:
    text_cl = _make_changelog(unreleased_tokens=200, version_count=3, version_tokens=2000)
    text_dl = _make_devlog([4000] * 4)  # 16000 — over 15000
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl, devlog_text=text_dl)
    plan = build_plan(tmp_path)
    # First-pass DEVLOG archival should fire because DEVLOG alone is over budget.
    devlog_actions = [a for a in plan.actions if "DEVLOG" in a.source_path.name]
    assert len(devlog_actions) == 1


def test_build_plan_no_action_when_all_under_budget(tmp_path):
    _write_minimal_config_and_logs(
        tmp_path,
        changelog_text=_make_changelog(100, 1, 100),
        devlog_text=_make_devlog([100]),
    )
    plan = build_plan(tmp_path)
    assert plan.is_empty()
```

- [ ] **Step 2: Add `build_plan`** to `archive.py`

```python
def build_plan(
    project_root: Path,
    *,
    keep_fraction: Optional[float] = None,
    include_changelog: bool = True,
    include_devlog: bool = True,
) -> ArchivePlan:
    """Top-level: read config, parse files, build plan.

    keep_fraction defaults to .logfile-config.yml -> archival.keep_fraction,
    or DEFAULT_KEEP_FRACTION (0.8) if unset.
    """
    cfg = parse_config(str(project_root / ".logfile-config.yml"))
    paths = cfg.get("paths", {})
    targets = cfg.get("token_targets", {})
    archival_cfg = cfg.get("archival", {})

    if keep_fraction is None:
        kf_raw = archival_cfg.get("keep_fraction")
        try:
            keep_fraction = float(kf_raw) if kf_raw is not None else DEFAULT_KEEP_FRACTION
        except (TypeError, ValueError):
            keep_fraction = DEFAULT_KEEP_FRACTION

    changelog_path = project_root / paths.get("changelog", "logs/CHANGELOG.md")
    devlog_path = project_root / paths.get("devlog", "logs/DEVLOG.md")
    changelog_budget = int(targets.get("changelog", 10_000))
    devlog_budget = int(targets.get("devlog", 15_000))
    combined_budget = int(targets.get("combined", 25_000))

    plan = ArchivePlan()

    if include_changelog and changelog_path.exists():
        try:
            actions, refusals, warns = _plan_changelog(
                text=changelog_path.read_text(encoding="utf-8"),
                source_path=changelog_path,
                budget=changelog_budget,
                keep_fraction=keep_fraction,
            )
            plan.actions.extend(actions)
            plan.refusal_reasons.extend(refusals)
            plan.warnings.extend(warns)
        except ArchiveError as e:
            plan.refusal_reasons.append(f"CHANGELOG: {e}")

    if include_devlog and devlog_path.exists():
        try:
            actions, refusals, warns = _plan_devlog(
                text=devlog_path.read_text(encoding="utf-8"),
                source_path=devlog_path,
                budget=devlog_budget,
                keep_fraction=keep_fraction,
            )
            plan.actions.extend(actions)
            plan.refusal_reasons.extend(refusals)
            plan.warnings.extend(warns)
        except ArchiveError as e:
            plan.refusal_reasons.append(f"DEVLOG: {e}")

    # Combined-budget overflow loop (DEVLOG only).
    def _projected_combined() -> int:
        # Compute tokens after applying current plan actions.
        cl_tokens = _estimate_tokens(changelog_path.read_text(encoding="utf-8")) \
                    if changelog_path.exists() else 0
        dl_tokens = _estimate_tokens(devlog_path.read_text(encoding="utf-8")) \
                    if devlog_path.exists() else 0
        for a in plan.actions:
            if a.source_path == changelog_path:
                cl_tokens = a.tokens_after
            elif a.source_path == devlog_path:
                dl_tokens = a.tokens_after
        return cl_tokens + dl_tokens

    current_kf = keep_fraction
    while (
        include_devlog
        and devlog_path.exists()
        and _projected_combined() > combined_budget
        and current_kf > COMBINED_KEEP_FRACTION_FLOOR
    ):
        current_kf = round(current_kf - 0.05, 2)
        # Drop any existing DEVLOG action and replan with tighter keep_fraction.
        plan.actions = [a for a in plan.actions if a.source_path != devlog_path]
        try:
            actions, refusals, warns = _plan_devlog(
                text=devlog_path.read_text(encoding="utf-8"),
                source_path=devlog_path,
                budget=devlog_budget,
                keep_fraction=current_kf,
            )
            plan.actions.extend(actions)
            for w in warns:
                if w not in plan.warnings:
                    plan.warnings.append(w)
        except ArchiveError as e:
            plan.refusal_reasons.append(f"DEVLOG (combined-overflow pass): {e}")
            break

    if _projected_combined() > combined_budget:
        plan.refusal_reasons.append(
            f"Combined still exceeds {combined_budget} tokens after archiving "
            f"DEVLOG down to keep_fraction floor ({COMBINED_KEEP_FRACTION_FLOOR}). "
            f"Trim CHANGELOG [Unreleased] or DEVLOG newest entries manually."
        )

    return plan
```

- [ ] **Step 3: Run, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 17 PASS.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): public build_plan + combined-overflow loop (Spec 3 T5)"
```

### Task 6: `apply()` — write archive files + rewrite source

**Files:**
- Modify: `product/scripts/archive.py`
- Modify: `product/tests/test_archive.py`

- [ ] **Step 1: Add failing tests**

```python
from archive import apply


def test_apply_writes_archive_and_rewrites_source(tmp_path):
    text_cl = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl)

    plan = build_plan(tmp_path, include_devlog=False)
    assert len(plan.actions) == 1
    action = plan.actions[0]

    apply(plan)

    # Archive file exists with the moved content.
    assert action.archive_path.exists()
    archived = action.archive_path.read_text(encoding="utf-8")
    assert "[0.1.0]" in archived  # oldest version was moved

    # Source no longer contains that oldest version.
    new_source = action.source_path.read_text(encoding="utf-8")
    assert "[0.1.0]" not in new_source

    # Source [Unreleased] preserved.
    assert "## [Unreleased]" in new_source

    # Source has a ## Archive section with the summary line.
    assert "## Archive" in new_source
    assert "CHANGELOG-v0.1.0-to-" in new_source


def test_apply_appends_to_existing_archive_section(tmp_path):
    # Pre-existing Archive section should be appended to, not duplicated.
    initial = textwrap.dedent("""\
        # Changelog

        ## [Unreleased]
        - x

        ## [0.3.0] - 2026-03-01
        """) + ("- " + "x" * 9996 + "\n") + textwrap.dedent("""

        ## [0.2.0] - 2026-02-01
        """) + ("- " + "x" * 9996 + "\n") + textwrap.dedent("""

        ## Archive

        - [CHANGELOG-v0.0.1-to-v0.1.0.md](archive/CHANGELOG-v0.0.1-to-v0.1.0.md) — old
        """)
    _write_minimal_config_and_logs(tmp_path, changelog_text=initial)

    plan = build_plan(tmp_path, include_devlog=False)
    apply(plan)

    src_text = (tmp_path / "logs" / "CHANGELOG.md").read_text(encoding="utf-8")
    # Both archive lines should be present.
    assert "CHANGELOG-v0.0.1-to-v0.1.0.md" in src_text
    # The Archive header should appear exactly once.
    assert src_text.count("## Archive") == 1


def test_apply_creates_archive_dir_if_missing(tmp_path):
    text_cl = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl)
    # Confirm no archive dir initially.
    assert not (tmp_path / "logs" / "archive").exists()

    plan = build_plan(tmp_path, include_devlog=False)
    apply(plan)

    assert (tmp_path / "logs" / "archive").is_dir()
```

- [ ] **Step 2: Add `apply`** to `archive.py`

```python
def _strip_section_with_header(text: str, section_header_re: re.Pattern) -> Tuple[str, str]:
    """Split text into (without_section, section_text)."""
    lines = text.splitlines(keepends=True)
    n = len(lines)
    start = next((i for i, ln in enumerate(lines) if section_header_re.match(ln)), None)
    if start is None:
        return text, ""
    end = next(
        (j for j in range(start + 1, n) if lines[j].startswith("## ")),
        n,
    )
    section = "".join(lines[start:end])
    without = "".join(lines[:start] + lines[end:])
    return without, section


def _append_summary_line_to_archive_section(text: str, summary_line: str) -> str:
    """Add summary_line under '## Archive' in text; create the section if missing."""
    without_archive, archive = _strip_section_with_header(text, _ARCHIVE_HEADER_RE)
    if archive:
        # Append within existing section.
        archive_lines = archive.rstrip("\n").splitlines()
        archive_lines.append(summary_line)
        new_archive = "\n".join(archive_lines) + "\n"
    else:
        new_archive = f"## Archive\n\n{summary_line}\n"

    # Place Archive at file end (one trailing newline).
    return without_archive.rstrip("\n") + "\n\n" + new_archive


def _write_archive_file(archive_path: Path, content: str, source_name: str) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"# Archive from {source_name}\n\n"
        f"_Generated by `lfg archive`. Original file: `{source_name}`._\n\n"
    )
    archive_path.write_text(header + content, encoding="utf-8")


def _rewrite_changelog_source(source_path: Path, action: ArchiveAction) -> None:
    """Remove the moved version blocks from the CHANGELOG source + add summary line."""
    text = source_path.read_text(encoding="utf-8")
    new_text = text
    # Remove each moved version block by string-replace of its content. The parser
    # preserved exact content strings, so this is exact.
    # action.moved_content is the concatenation of those blocks; remove blockwise.
    parsed = parse_changelog(text)
    moved_set = {v["content"] for v in parsed["versions"]
                 if v["content"] in action.moved_content}
    for block in moved_set:
        new_text = new_text.replace(block, "")
    # Tidy multiple blank lines.
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    new_text = _append_summary_line_to_archive_section(new_text, action.summary_line)
    source_path.write_text(new_text, encoding="utf-8")


def _rewrite_devlog_source(source_path: Path, action: ArchiveAction) -> None:
    text = source_path.read_text(encoding="utf-8")
    new_text = text
    parsed = parse_devlog(text)
    for e in parsed["entries"]:
        if e["content"] in action.moved_content:
            new_text = new_text.replace(e["content"], "")
    new_text = re.sub(r"\n{3,}", "\n\n", new_text)
    new_text = _append_summary_line_to_archive_section(new_text, action.summary_line)
    source_path.write_text(new_text, encoding="utf-8")


def apply(plan: ArchivePlan) -> None:
    """Execute the plan: write archive files, rewrite source files."""
    if plan.refusal_reasons:
        raise ArchiveError("Plan has refusals; refusing to apply: "
                           + "; ".join(plan.refusal_reasons))
    for action in plan.actions:
        _write_archive_file(action.archive_path, action.moved_content,
                            action.source_path.name)
        if action.source_path.name.upper().startswith("CHANGELOG"):
            _rewrite_changelog_source(action.source_path, action)
        else:
            _rewrite_devlog_source(action.source_path, action)
```

- [ ] **Step 3: Run, see pass**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 20 PASS.

- [ ] **Step 4: Commit**

```bash
git add product/scripts/archive.py product/tests/test_archive.py
git commit -m "feat(archive): apply() — write archives + rewrite sources + Archive section (Spec 3 T6)"
```

### Task 7: Idempotency + state-and-adr rejection

**Files:**
- Modify: `product/tests/test_archive.py`

- [ ] **Step 1: Add failing tests** (these guard against regressions; no new code needed)

```python
def test_apply_is_idempotent(tmp_path):
    """Running build_plan + apply twice → second run is a no-op."""
    text_cl = _make_changelog(unreleased_tokens=200, version_count=5, version_tokens=2500)
    _write_minimal_config_and_logs(tmp_path, changelog_text=text_cl)

    plan1 = build_plan(tmp_path, include_devlog=False)
    apply(plan1)

    plan2 = build_plan(tmp_path, include_devlog=False)
    assert plan2.is_empty(), f"second run should be empty, got {plan2.actions}"


def test_build_plan_dogfood_against_this_repo():
    """Smoke: building a plan against this repo's actual logs doesn't crash and
    produces a reasonable shape (CHANGELOG over budget today; DEVLOG within
    individual budget but maybe pushed by combined-overflow)."""
    repo_root = Path(__file__).resolve().parents[2]
    if not (repo_root / "logs" / "CHANGELOG.md").exists():
        pytest.skip("no logs/CHANGELOG.md to dogfood against")
    plan = build_plan(repo_root)
    # Don't apply — just confirm it builds.
    assert isinstance(plan, ArchivePlan)
    # If there are refusals, they should be intelligible strings.
    for r in plan.refusal_reasons:
        assert isinstance(r, str) and r
```

- [ ] **Step 2: Run**

```bash
python -m pytest product/tests/test_archive.py -v
```

Expected: all 22 PASS. Dogfood test runs against the real `logs/` and either reports a non-empty plan or empty if archival already happened.

- [ ] **Step 3: Commit**

```bash
git add product/tests/test_archive.py
git commit -m "test(archive): idempotency guard + dogfood smoke against this repo (Spec 3 T7)"
```

---

## Phase 2 — CLI wiring (lfg archive)

### Task 8: `cmd_archive` in lfg.py

**Files:**
- Modify: `product/scripts/lfg.py`
- Test: `product/tests/test_lfg_archive.py`

- [ ] **Step 1: Write failing tests**

```python
# product/tests/test_lfg_archive.py
import subprocess
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LFG = ROOT / "product/scripts/lfg.py"


def _run(args, cwd, stdin=""):
    return subprocess.run(
        [sys.executable, str(LFG)] + args,
        cwd=str(cwd), input=stdin, capture_output=True, text=True, encoding="utf-8",
    )


def _seed_oversize_changelog(tmp_path):
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
          devlog: logs/DEVLOG.md
        token_targets:
          changelog: 10000
          devlog: 15000
          combined: 25000
        archival:
          keep_fraction: 0.8
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir()
    body = "## [Unreleased]\n- x\n"
    for i in range(5, 0, -1):
        body += f"\n## [0.{i}.0] - 2026-0{i}-01\n- " + ("x" * 9998) + "\n"
    (tmp_path / "logs" / "CHANGELOG.md").write_text(f"# Changelog\n\n{body}", encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text(
        "# Development Log\n\n## Daily Log\n\n### 2026-05-28: x\n- y\n", encoding="utf-8")


def test_archive_dry_run_writes_nothing(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--dry-run"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Move from CHANGELOG.md" in r.stdout
    # No archive file created.
    assert not (tmp_path / "logs" / "archive").exists()


def test_archive_force_skips_prompt_and_applies(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--force"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert (tmp_path / "logs" / "archive").is_dir()
    # Some CHANGELOG-* file in archive.
    assert any(p.name.startswith("CHANGELOG-v") for p in (tmp_path / "logs" / "archive").iterdir())


def test_archive_state_and_adr_rejected(tmp_path):
    _seed_oversize_changelog(tmp_path)
    r = _run(["archive", "--state"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "STATE" in (r.stdout + r.stderr)
    assert "don't archive" in (r.stdout + r.stderr).lower()

    r = _run(["archive", "--adr"], cwd=tmp_path)
    assert r.returncode == 2, r.stdout + r.stderr
    assert "ADR" in (r.stdout + r.stderr)


def test_archive_no_action_when_under_budget(tmp_path):
    """Empty plan exits 0 with a friendly message."""
    (tmp_path / ".logfile-config.yml").write_text(textwrap.dedent("""
        paths:
          changelog: logs/CHANGELOG.md
        token_targets:
          changelog: 10000
        archival:
          keep_fraction: 0.8
    """), encoding="utf-8")
    (tmp_path / "logs").mkdir()
    (tmp_path / "logs" / "CHANGELOG.md").write_text("# Changelog\n\n## [Unreleased]\n- tiny\n", encoding="utf-8")
    (tmp_path / "logs" / "DEVLOG.md").write_text("# Development Log\n\n## Daily Log\n", encoding="utf-8")
    r = _run(["archive", "--dry-run"], cwd=tmp_path)
    assert r.returncode == 0, r.stderr
    assert "Nothing to archive" in r.stdout
```

- [ ] **Step 2: Run, see fail**

Expected: subcommand `archive` not registered.

- [ ] **Step 3: Add `cmd_archive` + subparser in `lfg.py`**

Find the existing `cmd_promote` definition; insert `cmd_archive` after it:

```python
def cmd_archive(args):
    """Build an ArchivePlan and (if not --dry-run) apply it after confirmation."""
    if args.state or args.adr:
        if args.state:
            print("STATE doesn't archive — STATE is a snapshot, not a ledger. "
                  "Trim or overwrite it directly. See product/docs/log_file_how_to.md.",
                  file=sys.stderr)
        if args.adr:
            print("ADRs don't archive — they remain referenceable forever. "
                  "See product/docs/log_file_how_to.md.", file=sys.stderr)
        return 2

    from archive import build_plan, apply, ArchiveError
    include_changelog = not args.devlog or args.changelog
    include_devlog = not args.changelog or args.devlog
    if args.changelog and not args.devlog:
        include_devlog = False
    if args.devlog and not args.changelog:
        include_changelog = False

    plan = build_plan(
        project_root=Path.cwd(),
        include_changelog=include_changelog,
        include_devlog=include_devlog,
    )

    # Stream the human-readable plan to stdout (UTF-8 bytes — matches cmd_prime).
    sys.stdout.buffer.write(plan.to_human().encode("utf-8"))
    sys.stdout.buffer.write(b"\n")

    if plan.refusal_reasons and not plan.actions:
        return 2

    if args.dry_run or plan.is_empty():
        return 0

    if not args.force:
        try:
            reply = input("Apply this archive plan? [y/N] ").strip().lower()
        except EOFError:
            reply = ""
        if reply not in ("y", "yes"):
            print("Aborted.", file=sys.stderr)
            return 1

    try:
        apply(plan)
    except ArchiveError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    print(f"Applied {len(plan.actions)} archive action(s).")
    return 0
```

Add subparser registration alongside `p_prom`:

```python
    # archive command
    p_arch = subparsers.add_parser(
        'archive',
        help="Archive old CHANGELOG version blocks and DEVLOG entries (deterministic, work-aware)")
    p_arch.add_argument('--dry-run', action='store_true',
                        help='Show the plan but write nothing (default if no flag)')
    p_arch.add_argument('--force', action='store_true',
                        help='Skip the confirmation prompt')
    p_arch.add_argument('--changelog', action='store_true',
                        help='Scope to CHANGELOG only')
    p_arch.add_argument('--devlog', action='store_true',
                        help='Scope to DEVLOG only')
    p_arch.add_argument('--state', action='store_true',
                        help='(rejected) STATE does not archive')
    p_arch.add_argument('--adr', action='store_true',
                        help='(rejected) ADRs do not archive')
```

Add to the dispatch dict:

```python
        'archive': cmd_archive,
```

- [ ] **Step 4: Run, see pass**

```bash
python -m pytest product/tests/test_lfg_archive.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Full suite**

```bash
python -m pytest product/tests/ -q
```

Expected: full pass (Spec 2's 53 + the new Spec 3 tests). If a Spec 2 test fails, do NOT modify it — report DONE_WITH_CONCERNS.

- [ ] **Step 6: Commit**

```bash
git add product/scripts/lfg.py product/tests/test_lfg_archive.py
git commit -m "feat(lfg): add 'archive' subcommand (dry-run + force + per-file + state/adr rejection)"
```

---

## Phase 3 — Rule + hint updates

### Task 9: Shrink ARCHIVAL section in `log-file-maintenance.md`

**Files:**
- Modify: `product/rules/log-file-maintenance.md`

- [ ] **Step 1: Find the current ARCHIVAL section**

```bash
grep -nE '^##.*ARCHIV' product/rules/log-file-maintenance.md
```

- [ ] **Step 2: Replace the section** (the `## 🗄️ ARCHIVAL ...` block) with this single-paragraph version:

```markdown
## 🗄️ ARCHIVAL (When Token Limits Exceeded)

When validators flag overage, **do not move entries by hand**. Run `lfg archive --dry-run` to see a graceful, work-aware archival plan, review it, then `lfg archive` to apply. Spec 3 protects `[Unreleased]` in CHANGELOG and the most recent DEVLOG entries (fit-the-budget; keeps the newest set summing to 80% of budget). STATE and ADRs never archive. See `product/docs/log_file_how_to.md` for the full rule.
```

- [ ] **Step 3: Verify the fragment still satisfies test_rule_directives.py**

```bash
python -m pytest product/tests/test_rule_directives.py -v
```

Expected: all PASS. The directive heading `ARCHIVAL` is still present.

- [ ] **Step 4: Commit**

```bash
git add product/rules/log-file-maintenance.md
git commit -m "feat(rules): shrink ARCHIVAL section — point at lfg archive (Spec 3 T9)"
```

### Task 10: Update over-budget hints in validators

**Files:**
- Modify: `product/scripts/lint-logs.py` (over-budget hint strings)
- Modify: `product/scripts/validate-log-files.sh` (over-budget hint lines ~404-406)
- Modify: `product/scripts/validate-log-files.ps1` (matching block)

- [ ] **Step 1: lint-logs.py — update both CHANGELOG and DEVLOG hint strings**

```bash
grep -n "Archive old entries to logs/archive" product/scripts/lint-logs.py
```

Replace each occurrence's suggestion text. CHANGELOG hint becomes:

```python
                           "Run `lfg archive --dry-run` to preview an archival plan")
```

DEVLOG hint becomes the same.

- [ ] **Step 2: validate-log-files.sh — replace the two-line hint**

```bash
grep -n "Move oldest" product/scripts/validate-log-files.sh
```

Replace those echoes with:

```bash
            echo -e "\033[36m  Run \`lfg archive --dry-run\` to see a work-aware archival plan.\033[0m"
```

(One line; remove the two old hint lines.)

- [ ] **Step 3: validate-log-files.ps1 — apply the same change**

```powershell
            Write-Host "  Run ``lfg archive --dry-run`` to see a work-aware archival plan." -ForegroundColor $COLOR_INFO
```

(Replace both equivalent lines if there are two.)

- [ ] **Step 4: Run full validation suite**

```bash
python -m pytest product/tests/ -q
bash product/tests/smoke_install.sh
```

Expected: green.

- [ ] **Step 5: Commit**

```bash
git add product/scripts/lint-logs.py product/scripts/validate-log-files.sh product/scripts/validate-log-files.ps1
git commit -m "fix(validators): point at lfg archive --dry-run in over-budget hints (Spec 3 T10)"
```

### Task 11: Reduce profile `archival:` blocks

**Files:**
- Modify: `product/profiles/solo-developer.yml`
- Modify: `product/profiles/team.yml`
- Modify: `product/profiles/open-source.yml`
- Modify: `product/profiles/startup.yml`

- [ ] **Step 1: Replace the archival block in each profile**

For each profile, replace the existing `archival:` block (multi-line with `changelog_token_limit`, `devlog_token_limit`, `strategy`, etc.) with:

```yaml
# Archival — single knob for `lfg archive` retention.
# keep_fraction: fraction of each file's token budget to retain after archival.
# Default 0.8 (recommended). Lower = more aggressive archival.
archival:
  keep_fraction: 0.8
```

(Pick a per-profile default if you like — `startup.yml` could go 0.7 for tighter retention; the spec recommends 0.8 across the board, so simplest is to use the same.)

- [ ] **Step 2: Verify tests still pass**

```bash
python -m pytest product/tests/test_budget_consistency.py -v
```

Expected: PASS.

- [ ] **Step 3: Commit**

```bash
git add product/profiles/
git commit -m "feat(profiles): reduce archival: block to keep_fraction only (Spec 3 T11)"
```

### Task 12: Regenerate AGENTS.md after rule change

**Files:**
- Modify: `product/AGENTS.md` (via regenerate)

- [ ] **Step 1: Run the generator**

```bash
python product/scripts/lfg.py generate
```

Expected: token count printed; under 4500. If the new shrunken ARCHIVAL section drops total tokens, that's expected.

- [ ] **Step 2: Verify clean**

```bash
python product/scripts/lfg.py generate --check
```

Expected: exit 0.

- [ ] **Step 3: Commit**

```bash
git add product/AGENTS.md
git commit -m "chore: regenerate AGENTS.md after ARCHIVAL section shrink (Spec 3 T12)"
```

### Task 13: Document the deterministic archival workflow in how-to

**Files:**
- Modify: `product/docs/log_file_how_to.md`

- [ ] **Step 1: Find the right section**

```bash
grep -n "archive\|archiv" product/docs/log_file_how_to.md | head
```

- [ ] **Step 2: Replace the existing archival paragraph(s)** with a focused section explaining:

```markdown
### Archival (`lfg archive`)

Archival in LFG is **deterministic and work-aware**. When validators flag overage (CHANGELOG >10k, DEVLOG >15k, combined >25k), don't move entries manually — run:

```bash
python .log-file-genius/product/scripts/lfg.py archive --dry-run
```

The dry-run prints a plan: which version blocks (CHANGELOG) and which old entries (DEVLOG) would move, where they'd land, and what the new token counts would be. Review the plan, then apply with `lfg archive` (it'll prompt for confirmation), or `lfg archive --force` in scripts.

**What's protected:**
- CHANGELOG's `## [Unreleased]` section is **never** archived (it's in-flight work).
- DEVLOG keeps the **newest entries** that fit within 80% of its budget (`keep_fraction` in `archival:` block of `.logfile-config.yml`). Older entries go to the archive.
- STATE.md is a snapshot — it doesn't archive, it gets trimmed/overwritten.
- ADRs are decisions — they never archive.

**Archive files** land in `logs/archive/` with self-documenting names:
- `CHANGELOG-v0.1.0-to-v0.1.5.md` — version range moved.
- `DEVLOG-2025-10-15-to-2025-12-20.md` — entry date range.

Each source file retains a `## Archive` section with one bullet per archive file (relative link + summary).

**If `[Unreleased]` alone exceeds budget**, `lfg archive` refuses with exit 2 — you trim Unreleased manually. There is no `--force-include-unreleased` flag by design.
```

- [ ] **Step 3: Commit**

```bash
git add product/docs/log_file_how_to.md
git commit -m "docs(how-to): document deterministic archival workflow (Spec 3 T13)"
```

---

## Phase 4 — Self-application (dogfood)

### Task 14: Run `lfg archive --dry-run` on this repo

**Files:** none (read-only)

- [ ] **Step 1: Capture the plan**

```bash
python product/scripts/lfg.py archive --dry-run > /tmp/spec3_plan.txt 2>&1
cat /tmp/spec3_plan.txt
```

Expected: a non-empty plan since this repo is over budget (CHANGELOG ~12,806 tokens vs 10,000 target). The plan should:
- Identify CHANGELOG version blocks to archive.
- Either show DEVLOG fits already or include a smaller DEVLOG action.
- Land archive files under `logs/archive/`.

- [ ] **Step 2: Inspect the plan**

Verify by reading `/tmp/spec3_plan.txt`:
- Source path is `logs/CHANGELOG.md` (and possibly `logs/DEVLOG.md`).
- Archive paths use the `CHANGELOG-v<a>-to-v<b>.md` / `DEVLOG-<earliest>-to-<latest>.md` patterns.
- `tokens_after` brings each file under its budget.
- No refusals.

If anything looks off — wrong file targeted, [Unreleased] would be moved, refusals you didn't expect — STOP. Report DONE_WITH_CONCERNS with the plan text; do not apply.

- [ ] **Step 3: No commit** (read-only step). Move to Task 15 once the plan looks correct.

### Task 15: Apply the archive against this repo (with confirmation gate)

**Files:**
- Modify: `logs/CHANGELOG.md` (potentially `logs/DEVLOG.md`)
- Create: `logs/archive/CHANGELOG-v*.md` (potentially `logs/archive/DEVLOG-*.md`)

- [ ] **Step 1: Stop and confirm with the human** before applying. This is the self-application step; if you're a subagent reading this plan, **pause and ask the controller** whether to proceed. This is not a test-environment apply — it modifies the working repo's real logs.

- [ ] **Step 2: After explicit go-ahead, run apply**

```bash
python product/scripts/lfg.py archive --force
```

(`--force` skips the interactive prompt; controller already confirmed in Step 1.)

- [ ] **Step 3: Verify**

```bash
ls -la logs/archive/
python product/scripts/lfg.py validate
```

Expected: archive files present; validator reports CHANGELOG/DEVLOG under budget; no errors.

- [ ] **Step 4: Sanity check** — open `logs/CHANGELOG.md` and confirm `[Unreleased]` survived intact, an `## Archive` section now points at the new file(s), and the file is shorter than before.

- [ ] **Step 5: Commit**

```bash
git add logs/ logs/archive/
git commit -m "chore: dogfood Spec 3 — graceful archival of pre-Spec-2 CHANGELOG/DEVLOG history"
```

---

## Final verification

- [ ] **Full pytest** — should be Spec 2's 53 + Spec 3's new tests:

```bash
python -m pytest product/tests/ -q
```

- [ ] **Smoke tests** still pass:

```bash
bash product/tests/smoke_install.sh
powershell -NoProfile -File product/tests/smoke_install.ps1
```

- [ ] **lfg --help lists all 11 commands**:

```bash
python product/scripts/lfg.py --help | grep -E "^\s+(validate|lint|secrets|check-version|check-rules|status|install-hooks|generate|prime|promote|archive)\b" | wc -l
```

Expected: `11`.

- [ ] **`generate --check`** still clean:

```bash
python product/scripts/lfg.py generate --check
```

- [ ] **No stragglers**:

```bash
grep -rn "Archive old entries to logs/archive\|Archive by TOKEN COUNT" product/ 2>/dev/null
```

Expected: no output (old hint strings removed).

---

## Spec coverage map

- Spec §Decisions: deterministic CLI verb → Task 8
- Spec §Decisions: file-specific signals (Unreleased / fit-the-budget) → Tasks 3 + 4
- Spec §Decisions: one configurable knob (keep_fraction) → Tasks 5 + 11
- Spec §Decisions: self-documenting archive filenames → Tasks 3 + 4 (filename construction)
- Spec §Decisions: default --dry-run + prompt + --force → Task 8
- Spec §Decisions: refusal-only (no --force-include-unreleased) → Task 3 (`_plan_changelog` refusal) + Task 8 (no flag)
- Spec §Decisions: combined-budget overflow algorithm → Task 5 (`build_plan` combined loop)
- Spec §CHANGELOG rules → Task 3
- Spec §DEVLOG rules → Task 4
- Spec §STATE and ADRs (never archive) → Task 8 (`--state`/`--adr` rejection)
- Spec §Components: `archive.py` purity → Tasks 1–7
- Spec §Components: `lfg validate` hint → Task 10
- Spec §Testing: all 11 tests → Tasks 1–8 (each task adds the relevant tests)
- Spec §Self-application → Tasks 14–15
- Spec §Risks (non-Keep-a-Changelog format clean refusal) → Task 3 (`parse_changelog` raises) + Task 5 (refusal aggregation)

## Out-of-scope reminders (per spec §Non-goals)

- No ADR archival
- No STATE rollback / history
- No auto-archival on commit
- No `lfg restore <archive>` verb
- No multi-language fragments
