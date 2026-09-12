"""Explicit ADR routing. Source records own metadata; views never infer authority."""
from dataclasses import dataclass
import fnmatch
import hashlib
import os
from pathlib import Path
import re
from urllib.parse import quote, unquote
from context_paths import context_paths, tokens
from safe_write import replace

BEGIN = "<!-- LFG:ROUTES:BEGIN -->"
END = "<!-- LFG:ROUTES:END -->"


@dataclass
class Record:
    path: Path
    id: str
    title: str
    status: str
    triggers: str
    applies: list
    constraint: str
    replacement: Path | None
    source_bytes: bytes = b''


def field(text, name):
    values = re.findall(r"^\s*(?:- )?(?:\*\*)?" + re.escape(name) +
                        r":(?:\*\*)?\s*(.*?)\s*$", text, re.M | re.I)
    if len(values) != 1 or not values[0] or '[' in values[0] and name != 'Superseded by':
        raise ValueError(f"Missing, duplicate or placeholder {name}")
    return values[0]


def parse(path):
    source_bytes = path.read_bytes()
    text = source_bytes.decode("utf-8-sig").replace('\r\n', '\n')
    # Example metadata inside fenced code is not part of the record's authority.
    text = re.sub(r'^(`{3,}|~{3,})[^\n]*\n.*?^\1\s*$', '', text, flags=re.M | re.S)
    heading = re.search(r"^#\s+ADR[- ](\d+)\s*:\s*(.+)$", text, re.M)
    if not heading:
        raise ValueError("Missing ADR-NNN: Title heading")
    sections = re.findall(r"^## Routing\s*\n(.*?)(?=^## |\Z)", text, re.M | re.S)
    if len(sections) != 1:
        raise ValueError("Expected one ## Routing section")
    section = sections[0]
    status = field(text, "Status").lower()
    if status not in ("accepted", "proposed", "deprecated", "superseded"):
        raise ValueError(f"Unresolved status: {status}")
    applies = [s.strip().strip('`') for s in field(section, "Applies to").split(',')]
    if any(not s or s.startswith('/') or '..' in s.split('/') or '\\' in s for s in applies):
        raise ValueError("Applies to must use repository-relative globs or project-wide")
    replacement = None
    if status == "superseded":
        link = re.fullmatch(r"\[[^]]+\]\(([^)]+)\)", field(text, "Superseded by"))
        if not link:
            raise ValueError("Superseded by requires one local Markdown link")
        replacement = (path.parent / unquote(link[1])).resolve()
    return Record(path.resolve(), 'ADR-' + heading[1], heading[2], status,
                  field(section, "Read when"), applies, field(section, "Constraint"), replacement, source_bytes)


def collect(root):
    directory = context_paths(root)["adr_dir"]
    records, errors, seen = [], [], set()
    if not directory.is_dir():
        return [], [f"Missing ADR directory: {directory}"]
    for path in sorted(directory.glob("*.md")):
        if path.name.lower() in ("readme.md", "template.md", "index.md", "log.md"):
            continue
        try:
            if not path.resolve().is_relative_to(Path(root).resolve()):
                raise ValueError("Source escapes repository")
            record = parse(path)
            if record.id in seen:
                raise ValueError(f"Duplicate ID {record.id}")
            seen.add(record.id)
            records.append(record)
        except (ValueError, OSError) as exc:
            errors.append(f"{path.name}: {exc}")
    by_path = {r.path: r for r in records}
    for record in records:
        visited, current = set(), record
        while current.replacement:
            if current.path in visited:
                errors.append(f"{record.id}: supersession cycle")
                break
            visited.add(current.path)
            if current.replacement not in by_path:
                errors.append(f"{record.id}: missing/unresolved replacement {current.replacement}")
                break
            current = by_path[current.replacement]
    return sorted(records, key=lambda r: (r.id, str(r.path))), errors


def active(record, records):
    by_path, seen = {r.path: r for r in records}, set()
    while record.replacement:
        if record.path in seen or record.replacement not in by_path:
            return None
        seen.add(record.path)
        record = by_path[record.replacement]
    return record if record.status == 'accepted' else None


def select(records, paths=(), ids=()):
    selected = {}
    for record in records:
        matches = ('project-wide' in record.applies or record.id in ids or
                   any(fnmatch.fnmatchcase(p, glob) for p in paths for glob in record.applies))
        if matches:
            resolved = active(record, records)
            if resolved:
                selected[resolved.path] = resolved
    return sorted(selected.values(), key=lambda r: (r.id, str(r.path)))


def link(path, base):
    return quote(Path(os.path.relpath(path, base)).as_posix(), safe='/.-_')


def cell(value):
    return str(value).replace('|', '\\|').replace('\n', ' ')


def table(records, base):
    lines = ['| Decision / status | Read when | Applies to | Constraint |', '|---|---|---|---|']
    for r in records:
        suffix = f" → [{r.replacement.stem}]({link(r.replacement, base)})" if r.replacement else ''
        lines.append(f"| [{r.id}: {cell(r.title)}]({link(r.path, base)}) ({r.status}){suffix} | "
                     f"{cell(r.triggers)} | {cell(', '.join(r.applies))} | {cell(r.constraint)} |")
    return '\n'.join(lines) + '\n'


def managed(original, body):
    block = BEGIN + '\n' + body + END
    if BEGIN not in original and END not in original:
        return original.rstrip() + '\n\n' + block + '\n'
    if original.count(BEGIN) != 1 or original.count(END) != 1 or original.index(END) < original.index(BEGIN):
        raise ValueError('Malformed routing markers; preserve and repair manually')
    return original[:original.index(BEGIN)] + block + original[original.index(END) + len(END):]


def views(root, records, budget=500):
    directory = context_paths(root)['adr_dir']
    fingerprint = hashlib.sha256(b''.join(r.path.name.encode() + r.source_bytes for r in records)).hexdigest()
    prefix = (f'Source SHA-256: {fingerprint}\n\nRead globals and every path/task match. '
              'Follow replacements; search sources on a miss. Report unread scope.\n\n')
    content = table(records, directory)
    outputs = {}
    if tokens(prefix + content) > budget:
        global_rows = [r for r in records if 'project-wide' in r.applies]
        prefix += table(global_rows, directory) if global_rows else ''
        prefix += '\n| Partition | Read when | Applies to |\n|---|---|---|\n'
        historical = []
        # One partition per ADR keeps bounds deterministic without semantic grouping.
        for r in records:
            if r in global_rows:
                continue
            path = directory / 'routes' / (r.id.lower() + '.md')
            body = '---\ntype: Routing Index\n---\n\n' + BEGIN + '\n' + table([r], path.parent) + END + '\n'
            outputs[path] = body
            replacement = active(r, records)
            if r.status == 'superseded' and replacement and 'project-wide' in replacement.applies:
                historical.append(f'[{r.id}]({link(path, directory)})')
            else:
                prefix += f'| [{r.id}]({link(path, directory)}) | {cell(r.triggers)} | {cell(", ".join(r.applies))} |\n'
        if historical:
            prefix += '\nSuperseded history (follow replacements): ' + ', '.join(historical) + '.\n'
        content = ''
    root_body = prefix + content
    if tokens(root_body) > budget:
        root_body += '\nINCOMPLETE within budget: root manifest exceeds the requested budget. Read in batches; no destinations omitted.\n'
    index = directory / 'README.md'
    original = index.read_text(encoding='utf-8') if index.exists() else '---\ntype: ADR Index\n---\n\n# Architectural decisions\n'
    rendered = managed(original, root_body)
    if tokens(rendered) > budget and 'INCOMPLETE within budget:' not in rendered:
        root_body += '\nINCOMPLETE within budget: full root including curated prose exceeds budget. Read in batches; no destinations omitted.\n'
        rendered = managed(original, root_body)
    outputs[index] = rendered
    return outputs


def run(root, write=False, check=False, paths=(), ids=(), budget=500):
    if budget < 1:
        raise ValueError('budget must be positive')
    records, errors = collect(root)
    unknown = set(ids) - {r.id for r in records}
    errors.extend(f'Unknown selected ADR: {i}' for i in sorted(unknown))
    if errors:
        return 2, 'UNRESOLVED; search source ADRs.\n' + '\n'.join(errors)
    outputs = views(root, records, budget)
    if check or write:
        stale = [p for p, text in outputs.items() if not p.exists() or p.read_text(encoding='utf-8') != text]
        if write:
            if any(r.path.read_bytes() != r.source_bytes for r in records):
                return 2, 'Source ADR changed during generation; regenerate routes.'
            # Partitions first, root last. Failed runs never publish a complete new manifest.
            for path in stale:
                replace(path, outputs[path], path.read_bytes() if path.exists() else None)
        return (1 if check and stale else 0), ('Stale: ' + ', '.join(str(p) for p in stale) if check and stale else 'ADR routes current.')
    chosen = select(records, paths, ids)
    text = table(chosen, root)
    if not paths and not ids or not chosen:
        text += 'Read the root manifest and choose semantic matches; bounded search on no match.\n'
    # Root navigation and selected rows both count, including duplicate globals.
    root_tokens = tokens(outputs[context_paths(root)['adr_dir'] / 'README.md'])
    if tokens(text) + root_tokens > budget:
        return 2, 'INCOMPLETE: narrow scope or read batches. Known unread sources:\n' + '\n'.join(str(r.path.relative_to(root)) for r in chosen)
    return 0, text
