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
