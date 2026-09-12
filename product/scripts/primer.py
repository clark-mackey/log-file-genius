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
    from context_paths import context_paths
    return context_paths(project_root)[key]


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


def build_prime(project_root: Path, n: int = 5, as_json: bool = False,
                role='subagent', selected=(), objective='', budget=2000) -> str:
    from context_paths import context_paths, tokens
    from freshness import assess
    import re
    if budget < 1 or role not in ('subagent', 'reader'):
        raise ValueError('Positive budget and valid role required')
    state = _read_state(project_root)
    entries = _last_n_changelog_entries(project_root, n)

    paths_block = {
        "state": str(_resolve_log_path(project_root, "state", "logs/STATE.md").relative_to(project_root)),
        "changelog": str(_resolve_log_path(project_root, "changelog", "logs/CHANGELOG.md").relative_to(project_root)),
        "devlog": str(_resolve_log_path(project_root, "devlog", "logs/DEVLOG.md").relative_to(project_root)),
    }

    paths_block['adr_index'] = str(context_paths(project_root)['adr_dir'].relative_to(project_root) / 'README.md')
    excerpts, missing, seen = [], [], set()
    for selection in selected:
        name, _, section = selection.partition('#')
        path = (project_root / name).resolve()
        if not path.is_relative_to(project_root.resolve()):
            raise ValueError(f'Selection escapes repository: {name}')
        key = (path, section)
        if key in seen:
            continue
        seen.add(key)
        if not path.is_file():
            missing.append(selection)
            continue
        content = path.read_text(encoding='utf-8')
        if section:
            pattern = r'^(#{1,6}) ' + re.escape(section) + r'\s*$'
            matches = list(re.finditer(pattern, content, re.M))
            if len(matches) != 1:
                missing.append(selection + ' (section absent or ambiguous)')
                continue
            match = matches[0]
            end = re.search(r'^#{1,' + str(len(match[1])) + r'} ', content[match.end():], re.M)
            content = content[match.start(): match.end() + end.start() if end else len(content)]
        excerpts.append({'source': selection, 'content': content})
    evidence = assess(project_root)
    payload = {'marker': SUBAGENT_MARKER if role == 'subagent' else 'LFG_READER_CONTEXT',
               'role': role, 'objective': objective, 'state': state,
               'changelog_entries': entries, 'paths': paths_block,
               'evidence': evidence, 'selected_context': excerpts, 'missing': missing,
               'coverage': 'explicit selections only; reroute if task scope expands'}

    if as_json:
        output = json.dumps(payload, indent=2)
        if tokens(output) > budget:
            raise ValueError(f'INCOMPLETE: packet exceeds {budget} estimated tokens; '
                             f'narrow STATE/selection or increase budget. Unread selections: {list(selected)}')
        return output

    out: List[str] = [payload['marker'], "", 'Objective: ' + objective, '']
    out += (["You are a subagent. Stage findings in .lfg/staged/<id>/; do not write canonical logs. "
             "Report ADR IDs and unresolved scope. Lead reviews and promotes."] if role == 'subagent' else
            ["Context for a human or lead reader; no subagent identity assigned."])
    out += ["# STATE.md", "", state.rstrip(), ""]
    out += [f"# Last {len(entries)} CHANGELOG entries", ""]
    if entries:
        out += [f"- {e}" for e in entries]
    else:
        out += ["(no unreleased entries)"]
    out += ["", "# Canonical paths", ""]
    for k, v in paths_block.items():
        out.append(f"- {k}: {v}")
    out += ['', '# Checkout evidence', json.dumps(evidence, indent=2), '', payload['coverage']]
    for excerpt in excerpts:
        out += ['', '# Source: ' + excerpt['source'], excerpt['content']]
    if missing:
        out += ['', 'MISSING: ' + ', '.join(missing)]
    out.append("")
    output = "\n".join(out)
    if tokens(output) > budget:
        raise ValueError(f'INCOMPLETE: packet exceeds {budget} estimated tokens; '
                         f'narrow selection or increase budget. Unread selections: {list(selected)}')
    return output
