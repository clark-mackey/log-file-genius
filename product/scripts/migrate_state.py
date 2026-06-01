"""Brownfield STATE.md migration to the v0.4.0 spec (Spec 4 §2).

Plan/apply module mirroring archive.py's shape: pure-planning functions
(`parse_state`, `build_plan`) build a `MigratePlan`; `apply(plan, ...)` does the
I/O. No I/O in the planner — same testability pattern as archive.py / generator.

v0.3.0's stricter STATE.md rules flag pre-existing content on first run after an
upgrade, with no tool to bring it into compliance. `lfg migrate-state` is that
tool: it keeps the canonical sections (truncating any that blow the budget),
bundles non-canonical user content into a single one-time DEVLOG snapshot entry,
and drops empty placeholders.

The verb is a hard one-shot, guarded two ways (either trips refusal):
  1. STATE.md already passes v0.3.0 validation cleanly (nothing to migrate).
  2. DEVLOG.md already carries the snapshot entry (already migrated — re-running
     after a user edits STATE back into non-compliance must NOT re-archive
     sections that no longer exist).

Encoding & atomicity policy (Spec 4 §1) is REUSED from agents_merge:
read with utf-8-sig + LF normalization (`read_text_normalized`), write LF/UTF-8/
no-BOM atomically (`atomic_write`). `apply` stages BOTH files to tmp, then renames
DEVLOG first so STATE never lands without its snapshot — see `apply` for the exact
ordering and failure behavior.
"""
from __future__ import annotations

import importlib.util
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

# Sibling-module imports (archive.py pattern). Reuse the encoding/atomicity
# helpers from agents_merge rather than re-implementing them.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Re-exported for the CLI layer (lfg.py calls migrate_state.read_text_normalized
# / .atomic_write). Keep these even if this module's body doesn't reference one.
from agents_merge import read_text_normalized, atomic_write


# Default STATE token budget when config doesn't set token_targets.state.
# Matches lint-logs.py (self.state_target default = 500).
DEFAULT_STATE_TARGET = 500

# The canonical v0.3.0 STATE sections to KEEP. Sourced from Spec 4 §2
# ("keep: Current Context, Last Session, In Progress (the v0.3.0 spec)") and
# corroborated by product/templates/STATE_template.md (Current Context / Last
# Session). Matched case-insensitively against `## <heading>` lines; the
# heading may carry a parenthetical suffix (e.g. "Current Context (Source of
# Truth)").
CANONICAL_SECTIONS = ("Current Context", "Last Session", "In Progress")

# Heading text that is structurally part of the doc but not session content —
# never archived, never dropped, always passed through verbatim in keep order.
# "Related Documents" carries the frontmatter links the validator checks.
STRUCTURAL_SECTIONS = ("Related Documents",)

# The one-shot DEVLOG snapshot heading. The date is filled in by the caller.
SNAPSHOT_TITLE = "STATE snapshot pre-v0.4.0 migration"
# Guard-2 detector: matches the snapshot heading on its own line.
SNAPSHOT_HEADING_RE = re.compile(
    r"^### \d{4}-\d{2}-\d{2}: STATE snapshot pre-v0\.4\.0 migration$",
    re.MULTILINE,
)

# A `## Heading` line (level-2 only — STATE sections are `##`).
_SECTION_RE = re.compile(r"^##\s+(?P<title>.+?)\s*$")
_DAILY_LOG_RE = re.compile(r"^##\s+Daily Log\b", re.IGNORECASE)


class MigrateError(ValueError):
    """Raised when migration cannot or should not proceed (mirrors ArchiveError)."""


def _estimate_tokens(text: str) -> int:
    """Match the canonical chars/4 heuristic (archive.py / lint-logs.py)."""
    return len(text) // 4


@dataclass
class Section:
    """One `## ...` section of STATE.md: heading line + body, with a token count.

    `heading` is the canonical title text (without the leading `## `, e.g.
    "Current Context"). `raw` is the full section as it appeared in the file
    (heading line through to the next `##`), used verbatim when archiving.
    """
    heading: str
    raw: str
    tokens: int

    def matches_canonical(self) -> Optional[str]:
        """Return the canonical name this section maps to, or None.

        Case-insensitive prefix match so "Current Context (Source of Truth)"
        maps to "Current Context".
        """
        low = self.heading.lower()
        for name in CANONICAL_SECTIONS:
            if low == name.lower() or low.startswith(name.lower()):
                return name
        return None

    def is_structural(self) -> bool:
        low = self.heading.lower()
        return any(low.startswith(name.lower()) for name in STRUCTURAL_SECTIONS)

    def has_real_content(self) -> bool:
        """True if the body holds something beyond placeholders/whitespace.

        Placeholder markers from the templates ("*None*", "*No active work*",
        bracketed "[fill me in]" stubs) count as empty.
        """
        body = self.raw
        # Strip the heading line itself.
        body = re.sub(r"^##\s+.*$", "", body, count=1, flags=re.MULTILINE)
        # Remove horizontal-rule separators and bracketed placeholder stubs.
        stripped = body.replace("---", "")
        stripped = re.sub(r"\[[^\]]*\]", "", stripped)        # [placeholder]
        stripped = re.sub(r"\*[^*]*\*", "", stripped)          # *None* / *No ...*
        stripped = re.sub(r"[-*>#`:0-9.()\s]", "", stripped)   # list/quote/punct noise
        return bool(stripped)


@dataclass
class MigratePlan:
    """The result of build_plan; mirrors ArchivePlan (dry-run friendly)."""
    keep: list[Section] = field(default_factory=list)
    archive_to_devlog: list[Section] = field(default_factory=list)
    drop: list[Section] = field(default_factory=list)
    target_tokens: int = DEFAULT_STATE_TARGET
    # Sections whose kept content was truncated to fit budget (heading -> note).
    truncations: list[str] = field(default_factory=list)
    # The frontmatter / preamble before the first `## ` heading (kept verbatim).
    preamble: str = ""

    def is_empty(self) -> bool:
        return not self.archive_to_devlog and not self.drop and not self.truncations

    def to_human(self) -> str:
        """Human-readable dry-run summary (mirrors ArchivePlan.to_human)."""
        out: list[str] = [f"STATE migration plan (target {self.target_tokens} tokens):"]
        if self.keep:
            out.append("KEEP:")
            for s in self.keep:
                out.append(f"  - {s.heading} (~{s.tokens} tokens)")
        for note in self.truncations:
            out.append(f"TRUNCATED: {note}")
        if self.archive_to_devlog:
            out.append("ARCHIVE TO DEVLOG (one snapshot entry):")
            for s in self.archive_to_devlog:
                out.append(f"  - {s.heading} (~{s.tokens} tokens)")
        if self.drop:
            out.append("DROP (empty/placeholder):")
            for s in self.drop:
                out.append(f"  - {s.heading}")
        if self.is_empty():
            out.append("  (nothing to change — STATE already conforms)")
        return "\n".join(out)


def parse_state(content: str) -> list[Section]:
    """Split STATE.md into Sections by `##` headings.

    Everything before the first `## ` heading (frontmatter, title, intro) is the
    preamble and is NOT returned as a Section — callers that need it use
    `split_preamble`. Each Section captures its heading text, the raw span from
    its heading through to the next `##` (exclusive), and a token count.
    """
    _, sections = split_preamble(content)
    return sections


def split_preamble(content: str) -> tuple[str, list[Section]]:
    """Return (preamble, sections). Preamble is text before the first `## `."""
    lines = content.splitlines(keepends=True)
    n = len(lines)

    first = next((i for i, ln in enumerate(lines) if _SECTION_RE.match(ln)), None)
    if first is None:
        return content, []

    preamble = "".join(lines[:first])

    sections: list[Section] = []
    i = first
    while i < n:
        m = _SECTION_RE.match(lines[i])
        if not m:
            i += 1
            continue
        start = i
        end = next((j for j in range(i + 1, n) if _SECTION_RE.match(lines[j])), n)
        raw = "".join(lines[start:end])
        sections.append(
            Section(heading=m.group("title").strip(), raw=raw, tokens=_estimate_tokens(raw))
        )
        i = end
    return preamble, sections


def _truncate_section(section: Section, max_tokens: int) -> tuple[Section, str]:
    """Truncate a section's body to the most-recent content within max_tokens.

    "Most-recent" = keep the heading + the LAST lines that fit, since STATE
    sections list newest activity last (e.g. "Recently Completed" appends).
    Returns (new_section, note). max_tokens includes the heading line.
    """
    lines = section.raw.splitlines(keepends=True)
    heading_line = lines[0] if lines else f"## {section.heading}\n"
    body_lines = lines[1:]

    marker = "_(...older content truncated by `lfg migrate-state`...)_\n"
    # Budget against the assembled string's token count (chars/4 of the whole),
    # not a sum of per-line estimates — per-line integer division underestimates
    # the concatenated total and would overshoot max_tokens. We reserve the
    # heading + marker up front and grow the kept body newest-first.
    fixed_prefix = heading_line + marker  # marker always present once truncated
    kept_rev: list[str] = []
    for ln in reversed(body_lines):
        candidate = fixed_prefix + "".join(reversed(kept_rev + [ln]))
        if _estimate_tokens(candidate) > max_tokens and kept_rev:
            break
        kept_rev.append(ln)
    kept = list(reversed(kept_rev))

    new_raw = heading_line
    if len(kept) < len(body_lines):
        new_raw += marker
    new_raw += "".join(kept)

    note = (
        f"'{section.heading}' was {section.tokens} tokens (over budget); "
        f"truncated to most-recent ~{_estimate_tokens(new_raw)} tokens."
    )
    return Section(heading=section.heading, raw=new_raw, tokens=_estimate_tokens(new_raw)), note


def build_plan(state_content: str, config: dict) -> MigratePlan:
    """Classify every STATE section into keep / archive_to_devlog / drop.

    - keep: canonical v0.3.0 sections (Current Context, Last Session, In
      Progress) and structural sections (Related Documents), in canonical
      order. A kept section over the per-section budget is truncated to the
      most-recent content and the truncation is recorded.
    - archive_to_devlog: non-canonical sections that hold real user content;
      bundled into ONE DEVLOG snapshot entry by `apply`.
    - drop: empty/placeholder sections with no semantic value.

    target_tokens comes from config token_targets.state (default 500).
    """
    targets = config.get("token_targets", {}) if config else {}
    target_tokens = int(targets.get("state", DEFAULT_STATE_TARGET))

    preamble, sections = split_preamble(state_content)
    plan = MigratePlan(target_tokens=target_tokens, preamble=preamble)

    # Per-section budget: a kept section shouldn't, on its own, exceed the whole
    # STATE budget. Truncate any that does.
    per_section_budget = target_tokens

    canonical_found: dict[str, Section] = {}
    structural_keep: list[Section] = []

    for s in sections:
        if s.is_structural():
            structural_keep.append(s)
            continue
        canon = s.matches_canonical()
        if canon is not None:
            # First match wins per canonical name (defends against duplicates).
            canonical_found.setdefault(canon, s)
            continue
        # Non-canonical: archive real content, drop placeholders.
        if s.has_real_content():
            plan.archive_to_devlog.append(s)
        else:
            plan.drop.append(s)

    # Assemble keep in a stable, readable order: structural first, then
    # canonical sections in CANONICAL_SECTIONS order. Apply truncation.
    ordered_keep: list[Section] = list(structural_keep)
    for name in CANONICAL_SECTIONS:
        s = canonical_found.get(name)
        if s is None:
            continue
        if s.tokens > per_section_budget:
            s, note = _truncate_section(s, per_section_budget)
            plan.truncations.append(note)
        ordered_keep.append(s)
    plan.keep = ordered_keep
    return plan


# ----- STATE / DEVLOG rendering -----

def _render_state(plan: MigratePlan) -> str:
    """Compose the new STATE.md from the plan's preamble + kept sections."""
    parts: list[str] = []
    pre = plan.preamble.rstrip("\n")
    if pre:
        parts.append(pre + "\n")
    for s in plan.keep:
        parts.append(s.raw.rstrip("\n") + "\n")
    # Single blank line between blocks; trailing newline.
    return "\n".join(p.rstrip("\n") for p in parts) + "\n"


def _render_snapshot_entry(plan: MigratePlan, today: str) -> str:
    """Render the one-time DEVLOG snapshot entry bundling archive_to_devlog.

    Heading is EXACTLY `### <today>: STATE snapshot pre-v0.4.0 migration`.
    """
    lines = [f"### {today}: {SNAPSHOT_TITLE}", ""]
    lines.append(
        "Sections archived from STATE.md during the v0.4.0 migration "
        "(non-canonical content preserved here for history):"
    )
    lines.append("")
    for s in plan.archive_to_devlog:
        lines.append(s.raw.rstrip("\n"))
        lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def _insert_snapshot_at_end_of_daily_log(devlog: str, snapshot_entry: str) -> str:
    """Insert snapshot_entry at the END of the `## Daily Log` section.

    DEVLOG is newest-first; the snapshot is historical, so it goes at the bottom
    of the Daily Log (oldest position), BEFORE any later `## ` section (e.g.
    `## Archive`). Raises MigrateError if there is no `## Daily Log` heading.
    """
    lines = devlog.splitlines(keepends=True)
    n = len(lines)

    dl_idx = next((i for i, ln in enumerate(lines) if _DAILY_LOG_RE.match(ln)), None)
    if dl_idx is None:
        raise MigrateError("DEVLOG missing '## Daily Log' heading; cannot insert snapshot")

    # End of the Daily Log section = next `## ` heading after it, or EOF.
    end = next((j for j in range(dl_idx + 1, n) if lines[j].startswith("## ")), n)

    before = "".join(lines[:end])
    after = "".join(lines[end:])

    block = before.rstrip("\n") + "\n\n" + snapshot_entry.rstrip("\n") + "\n"
    if after:
        block += "\n" + after.lstrip("\n")
    return block


# ----- apply -----

def _state_is_compliant(state_path: Path, config_path: Path) -> bool:
    """Guard 1: does STATE.md already pass v0.3.0 validation with no errors?

    Reuses lint-logs.py's LogLinter.validate_state (loaded via importlib because
    the module name is hyphenated). Errors-only semantics (matching the
    `lfg validate --file STATE.md` granularity from T8): budget *warnings* do not
    count as needing migration — only structural errors (missing Current Context)
    do. So "compliant" == zero validation errors.
    """
    scripts_dir = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location(
        "_lfg_lint_logs", scripts_dir / "lint-logs.py"
    )
    if spec is None or spec.loader is None:  # pragma: no cover - defensive
        raise MigrateError("could not load lint-logs.py for STATE validation")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    linter = module.LogLinter(config_path=str(config_path))
    # Point the linter at the STATE file we're migrating.
    linter.state_path = str(state_path)
    result = linter.validate_state()
    return result.errors == 0


def apply(
    plan: MigratePlan,
    state_path: str | os.PathLike[str],
    devlog_path: str | os.PathLike[str],
    today: str,
    config_path: Optional[str | os.PathLike[str]] = None,
) -> None:
    """Write the new STATE.md and append the snapshot to DEVLOG, atomically.

    Guards (either trips refusal — hard one-shot):
      1. STATE.md already passes v0.3.0 validation cleanly (errors == 0).
      2. DEVLOG.md already contains the snapshot heading.

    `today` is the YYYY-MM-DD date for the snapshot heading. Following
    archive.py's convention, the pure planner never calls datetime.now(); the
    date is supplied by the CLI layer and threaded through here.

    Atomic two-file ordering & failure behavior:
      1. Render both new contents in memory first (no writes yet).
      2. Stage STATE -> <state>.lfg-tmp and DEVLOG -> <devlog>.lfg-tmp (both
         written and fsynced; neither target touched yet).
      3. os.replace(devlog.tmp, devlog) FIRST — the snapshot lands before STATE
         is rewritten, so STATE is never left pointing at content whose archived
         sections have no home.
      4. os.replace(state.tmp, state) SECOND.
      If step 3 fails: nothing has landed; both tmp files are cleaned up; STATE
      is untouched. If step 4 fails AFTER step 3 succeeded: DEVLOG has the
      snapshot (lossless — sections are preserved there) but STATE keeps its
      original content. Re-running is then blocked by Guard 2, so the user
      finishes the STATE rewrite by hand or restores DEVLOG — we never silently
      lose the archived sections. We attempt to clean the leftover state tmp.
    """
    state_path = Path(state_path)
    devlog_path = Path(devlog_path)
    cfg_path = Path(config_path) if config_path else (state_path.parent.parent / ".logfile-config.yml")

    # --- Guard 1: already compliant AND nothing to do.
    #
    # The validator (lint-logs.validate_state) only ERRORs on a missing
    # `## Current Context` section; a STATE that still carries non-canonical
    # sections to migrate passes it. So "passes validation" alone would refuse
    # exactly the brownfield case this tool exists for. Per the spec's
    # parenthetical ("already passes validation cleanly (nothing to do)"), we
    # treat the operative condition as *nothing to do*: refuse only when the
    # validator is clean AND the plan would make no change (no archive, no drop,
    # no truncation). A non-empty plan always has work to do, so it proceeds.
    if plan.is_empty() and _state_is_compliant(state_path, cfg_path):
        raise MigrateError(
            "STATE.md already passes v0.4.0 validation and the plan is empty — "
            "nothing to migrate."
        )

    # --- Guard 2: DEVLOG already migrated.
    devlog_text = read_text_normalized(devlog_path)
    if SNAPSHOT_HEADING_RE.search(devlog_text):
        raise MigrateError(
            "DEVLOG.md already contains a 'STATE snapshot pre-v0.4.0 migration' "
            "entry — migration is one-shot and has already run."
        )

    # --- Render both new contents up front (pure, no I/O).
    new_state = _render_state(plan)
    if plan.archive_to_devlog:
        snapshot = _render_snapshot_entry(plan, today)
        new_devlog = _insert_snapshot_at_end_of_daily_log(devlog_text, snapshot)
    else:
        # Nothing to archive: STATE-only migration (truncations/drops).
        new_devlog = None

    state_tmp = state_path.with_name(state_path.name + ".lfg-tmp")

    if new_devlog is None:
        # Single-file path: atomic_write already handles tmp+fsync+replace.
        atomic_write(state_path, new_state)
        return

    devlog_tmp = devlog_path.with_name(devlog_path.name + ".lfg-tmp")

    # Stage BOTH tmp files first (write + fsync); replace nothing yet.
    _write_tmp(state_tmp, new_state)
    try:
        _write_tmp(devlog_tmp, new_devlog)
    except BaseException:
        _safe_unlink(state_tmp)
        raise

    # Commit: DEVLOG first (snapshot must land before STATE is rewritten).
    try:
        os.replace(devlog_tmp, devlog_path)
    except BaseException:
        # Nothing landed; clean up both tmp files; STATE untouched.
        _safe_unlink(devlog_tmp)
        _safe_unlink(state_tmp)
        raise

    # DEVLOG committed. Now commit STATE.
    try:
        os.replace(state_tmp, state_path)
    except BaseException:
        # DEVLOG already has the snapshot (lossless); STATE keeps its original.
        # Guard 2 will block a re-run. Clean the leftover STATE tmp and surface.
        _safe_unlink(state_tmp)
        raise


def _write_tmp(tmp: Path, content: str) -> None:
    """Write content to tmp as UTF-8/LF/no-BOM with fsync (no replace)."""
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
        f.flush()
        os.fsync(f.fileno())


def _safe_unlink(path: Path) -> None:
    try:
        path.unlink()
    except OSError:
        pass
