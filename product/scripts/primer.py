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
