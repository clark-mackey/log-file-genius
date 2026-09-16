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
    source_bytes: bytes | None = None
    source_kind: str = ''
    moved_blocks: List[str] = field(default_factory=list)


@dataclass
class ArchivePlan:
    actions: List[ArchiveAction] = field(default_factory=list)
    refusal_reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def is_empty(self) -> bool:
        return not self.actions and not self.refusal_reasons

    def to_human(self) -> str:
        """Human-readable dry-run summary."""
        if not self.actions and not self.refusal_reasons and not self.warnings:
            return "Nothing to archive — selected log files within budget."
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

    # to_archive is already oldest-first.
    archive_content = "".join(v["content"] for v in to_archive)

    earliest = to_archive[0]["version"]
    latest = to_archive[-1]["version"]
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
            moved_blocks=[v['content'] for v in to_archive],
        )
    ], [], []


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


def devlog_structure_issues(text: str) -> List[str]:
    """Identify content archival cannot move without guessing boundaries."""
    lines = text.splitlines()
    start = next((i for i, line in enumerate(lines) if _DAILY_LOG_RE.match(line)), None)
    if start is None:
        return ["missing '## Daily Log' heading"]
    issues = []
    for line in lines[start + 1:]:
        if _ARCHIVE_HEADER_RE.match(line):
            break
        if re.match(r"^#{2,3} ", line) and not _DEVLOG_ENTRY_RE.match(line):
            issues.append(f"unsupported entry heading {line!r}")
    return issues


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

    issues = devlog_structure_issues(text)
    if issues:
        return [], ["DEVLOG: " + "; ".join(issues) +
                    ". Preserve a backup, then migrate entries to '### YYYY-MM-DD: Title'; preview again."], []

    entries = parsed["entries"]  # newest-first in file order
    if not entries:
        return [], [f"DEVLOG has {current_tokens} tokens but no archiveable entries; "
                    "preserve a backup and migrate to dated Daily Log entries."], []

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
    to_archive_oldest_first = sorted(to_archive, key=lambda e: e["date"])
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
            moved_blocks=[e['content'] for e in to_archive_oldest_first],
        )
    ], [], warnings


def build_plan(
    project_root: Path,
    *,
    keep_fraction: Optional[float] = None,
    include_changelog: bool = True,
    include_devlog: bool = True,
) -> ArchivePlan:
    """Top-level planner: read config, parse files, build plan.

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

    from context_paths import context_paths
    try:
        resolved_paths = context_paths(project_root)
    except ValueError as exc:
        return ArchivePlan(refusal_reasons=[str(exc)])
    changelog_path = resolved_paths['changelog']
    devlog_path = resolved_paths['devlog']
    changelog_budget = int(targets.get("changelog", 10_000))
    devlog_budget = int(targets.get("devlog", 15_000))
    combined_budget = int(targets.get("combined", 25_000))

    plan = ArchivePlan()
    snapshots = {p: p.read_bytes() for p in (changelog_path, devlog_path) if p.exists()}

    if include_changelog and changelog_path.exists():
        try:
            actions, refusals, warns = _plan_changelog(
                text=snapshots[changelog_path].decode("utf-8"),
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
                text=snapshots[devlog_path].decode("utf-8"),
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
                text=snapshots[devlog_path].decode("utf-8"),
                source_path=devlog_path,
                budget=devlog_budget,
                keep_fraction=current_kf,
            )
            plan.actions.extend(actions)
            for refusal in refusals:
                if refusal not in plan.refusal_reasons:
                    plan.refusal_reasons.append(refusal)
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

    for enabled, path, budget in ((include_changelog, changelog_path, changelog_budget),
                                  (include_devlog, devlog_path, devlog_budget)):
        if enabled and path.exists() and not any(a.source_path == path for a in plan.actions):
            actual = _estimate_tokens(path.read_text(encoding="utf-8"))
            if actual > budget:
                plan.refusal_reasons.append(f"{path.name}: {actual} tokens exceed budget {budget}; "
                                            "no safe movement available. Preserve a backup before manual migration.")
    for action in plan.actions:
        action.source_bytes = snapshots[action.source_path]
        action.source_kind = 'changelog' if action.source_path == changelog_path else 'devlog'
    return plan


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
        archive_lines = archive.rstrip("\n").splitlines()
        archive_lines.append(summary_line)
        new_archive = "\n".join(archive_lines) + "\n"
    else:
        new_archive = f"## Archive\n\n{summary_line}\n"

    return without_archive.rstrip("\n") + "\n\n" + new_archive


def _write_archive_file(archive_path: Path, content: str, source_name: str) -> None:
    archive_path.parent.mkdir(parents=True, exist_ok=True)
    header = (
        f"---\ntype: Log Archive\n---\n\n# Archive from {source_name}\n\n"
        f"_Original file: `{source_name}`._\n\n"
    )
    from safe_write import replace
    # A move one directory deeper must preserve relative Markdown destinations.
    def destination(target):
        raw = target[1:-1] if target.startswith('<') else target
        if raw.startswith(('/', '#')) or re.match(r'[A-Za-z][\w+.-]*:', raw):
            return target
        return '<../' + raw + '>' if target.startswith('<') else '../' + raw
    def relocate(match):
        return '](' + destination(match[1]) + (match[2] or '') + ')'
    pattern = r'''\]\((<[^>]+>|[^\s)]+)(\s+(?:"[^"]*"|'[^']*'|\([^)]*\)))?\)'''
    lines, fence = [], None
    for line in content.splitlines(keepends=True):
        marker = re.match(r'^\s*(`{3,}|~{3,})', line)
        if marker:
            if fence is None:
                fence = marker[1]
            elif marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not line[marker.end():].strip():
                fence = None
        elif not fence:
            line = re.sub(pattern, relocate, line)
            line = re.sub(r'^(\s{0,3}\[[^]]+\]:\s*)(<[^>]+>|\S+)(.*)$',
                          lambda m: m[1] + destination(m[2]) + m[3], line)
        lines.append(line)
    relocated = ''.join(lines)
    data = (header + relocated).encode('utf-8')
    if archive_path.exists() and archive_path.read_bytes() != data:
        raise ArchiveError(f'Archive collision; existing bytes preserved: {archive_path}')
    replace(archive_path, data, data if archive_path.exists() else None)


def _rewrite_changelog_source(source_path: Path, action: ArchiveAction) -> None:
    """Remove the moved version blocks from the CHANGELOG source + add summary line."""
    text = source_path.read_bytes().decode("utf-8")
    new_text = text
    parsed = parse_changelog(text)
    blocks = action.moved_blocks or [v['content'] for v in parsed['versions'] if v['content'] in action.moved_content]
    for block in blocks:
        new_text = new_text.replace(block, "", 1)
    new_text = _append_summary_line_to_archive_section(new_text, action.summary_line)
    from safe_write import replace
    replace(source_path, new_text, action.source_bytes if action.source_bytes is not None else text.encode('utf-8'))


def _rewrite_devlog_source(source_path: Path, action: ArchiveAction) -> None:
    text = source_path.read_bytes().decode("utf-8")
    new_text = text
    parsed = parse_devlog(text)
    blocks = action.moved_blocks or [e['content'] for e in parsed['entries'] if e['content'] in action.moved_content]
    for block in blocks:
        new_text = new_text.replace(block, "", 1)
    new_text = _append_summary_line_to_archive_section(new_text, action.summary_line)
    from safe_write import replace
    replace(source_path, new_text, action.source_bytes if action.source_bytes is not None else text.encode('utf-8'))


def apply(plan: ArchivePlan) -> None:
    """Execute the plan: write archive files, rewrite source files."""
    if plan.refusal_reasons:
        raise ArchiveError("Plan has refusals; refusing to apply: "
                           + "; ".join(plan.refusal_reasons))
    for action in plan.actions:
        try:
            if action.source_bytes is not None and action.source_path.read_bytes() != action.source_bytes:
                raise ArchiveError(f'Source changed since preview: {action.source_path}')
            _write_archive_file(action.archive_path, action.moved_content, action.source_path.name)
            if action.source_kind == 'changelog' or (not action.source_kind and action.source_path.name.upper().startswith("CHANGELOG")):
                _rewrite_changelog_source(action.source_path, action)
            else:
                _rewrite_devlog_source(action.source_path, action)
        except (OSError, ValueError) as exc:
            raise ArchiveError(f'Incomplete archive; original/backup and archive retained for recovery: {exc}') from exc
