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
