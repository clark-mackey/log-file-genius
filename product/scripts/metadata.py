"""Optional OKF producer for a conservative YAML subset, not a general consumer.

Unsupported existing YAML is preserved and reported for external validation.
No verification or lifecycle claims are created by metadata migration.
"""
import base64
import json
from pathlib import Path
import re
from urllib.parse import quote
from context_paths import context_paths
from safe_write import replace, retire


def frontmatter(data):
    text = data.decode('utf-8')
    if not text.startswith('---\n'):
        if text.startswith('---') or text.startswith('\ufeff') or '\r' in text:
            raise ValueError('Unsupported frontmatter encoding/delimiter; preserve and normalize explicitly')
        return {}, 0
    end = text.find('\n---\n', 4)
    if end < 0:
        raise ValueError('Unterminated frontmatter')
    values, stack = {}, [(-1, set())]
    previous_indent, previous_mapping = 0, False
    for line in text[4:end].splitlines():
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        match = re.fullmatch(r'( *)([A-Za-z_][\w-]*):(?: +(.*))?', line)
        if not match:
            raise ValueError('Unsupported YAML; use a full YAML validator: ' + line)
        indent, key, value = len(match[1]), match[2], match[3]
        if indent % 2 or indent > previous_indent and (not previous_mapping or indent != previous_indent + 2):
            raise ValueError('Unsupported YAML indentation: ' + line)
        previous_indent, previous_mapping = indent, value is None
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        if key in stack[-1][1]:
            raise ValueError('Duplicate YAML key: ' + key)
        stack[-1][1].add(key)
        if value is None:
            stack.append((indent, set()))
            parsed = None
        elif value.startswith('"'):
            parsed = json.loads(value)
            if not isinstance(parsed, str):
                raise ValueError('Expected string scalar')
        elif value.startswith("'") and value.endswith("'"):
            if not re.fullmatch(r"'(?:[^']|'')*'", value):
                raise ValueError('Unsupported single-quoted YAML scalar')
            parsed = value[1:-1].replace("''", "'")
        else:
            if (': ' in value or re.search(r'[\[\]{}&*!>|#\t]', value) or
                    value.startswith(('-', '?', '@', '`', "'"))):
                raise ValueError('Unsupported YAML scalar: ' + value)
            parsed = value
            if value.lower() in ('null', '~', 'true', 'false', 'yes', 'no', 'on', 'off') or re.fullmatch(r'[+-]?[0-9].*', value):
                parsed = None  # valid scalar, but cannot stand in for a string type
        if indent == 0:
            values[key] = parsed
    return values, end + 5


def migrate(data, path):
    values, end = frontmatter(data)
    if 'type' in values:
        if not isinstance(values['type'], str) or not values['type'].strip():
            raise ValueError('type must be a non-empty string')
        return data
    text = data.decode('utf-8')
    title = re.search(r'^# (.+)$', text[end:], re.M)
    kind = 'Architecture Decision' if re.search(r'^# ADR-', text, re.M) else {
        'STATE': 'Project State', 'CHANGELOG': 'Change Log', 'DEVLOG': 'Development Log',
        'INCIDENT': 'Incident Report'}.get(values.get('doc'), 'Project Reference')
    addition = 'type: ' + json.dumps(kind) + '\n'
    if 'title' not in values and title:
        addition += 'title: ' + json.dumps(title[1], ensure_ascii=False) + '\n'
    result = ('---\n' + addition + text[4:]) if end else ('---\n' + addition + '---\n\n' + text)
    frontmatter(result.encode())
    return result.encode()


def reserved(path, bundle):
    text = path.read_text(encoding='utf-8')
    if path.name == 'index.md':
        if text.startswith('---\n'):
            values, end = frontmatter(text.encode())
            if path.parent != bundle or set(values) != {'okf_version'}:
                raise ValueError('Reserved index allows only root okf_version metadata')
            text = text[end:]
        if not re.search(r'^# ', text, re.M) or any(
                line.strip() and not re.match(r'^(# |[*-] \[|<!--)', line)
                for line in text.splitlines()):
            raise ValueError('Unsupported index structure; expected headings and Markdown link bullets')
    else:
        if text.startswith('---') or not re.search(r'^# ', text, re.M):
            raise ValueError('Reserved log requires a heading and date-grouped bullets, no frontmatter')
        dates = re.findall(r'^## (.+)$', text, re.M)
        from datetime import date
        for value in dates:
            date.fromisoformat(value)
        if dates != sorted(dates, reverse=True):
            raise ValueError('Reserved log dates must be newest first')
        if any(line.strip() and not re.match(r'^(# |## \d{4}-\d{2}-\d{2}$|[*-] )', line) for line in text.splitlines()):
            raise ValueError('Unsupported reserved log body; expected date headings and flat bullets')


def run(root, bundle=None, write=False, index=False, restore=False):
    root = Path(root).resolve()
    bundle = (root / bundle).resolve() if bundle else context_paths(root)['state'].parent
    if not bundle.is_relative_to(root) or not bundle.is_dir():
        raise ValueError('Bundle must be an existing directory inside the repository')
    journal = root / '.lfg/metadata-migration.json'
    if not journal.resolve().is_relative_to(root):
        raise ValueError('Recovery journal escapes repository')
    if journal.exists():
        saved = json.loads(journal.read_text())
        for item in saved.get('files', []):
            path = (root / item['path']).resolve()
            if not path.is_relative_to(root) or Path(root / item['path']).is_symlink():
                raise ValueError('Recovery target escapes repository or is a symlink')
    if restore:
        record = json.loads(journal.read_text())
        for item in reversed(record['files']):
            path = root / item['path']
            before = base64.b64decode(item['before']) if item['before'] is not None else None
            after = base64.b64decode(item['after'])
            current = path.read_bytes() if path.exists() else None
            if current == before:
                continue
            if current != after:
                raise ValueError(f'Concurrent change; cannot restore {path}')
            if before is None:
                retire(path, after)
            else:
                replace(path, before, after)
        record['status'] = 'restored'
        replace(journal, json.dumps(record, indent=2) + '\n', journal.read_bytes())
        return 0, 'Restored original bytes.'
    errors, changes, inventory = [], [], []
    for path in sorted(bundle.rglob('*.md')):
        try:
            if not path.resolve().is_relative_to(bundle) or path.is_symlink():
                raise ValueError('Symlink or escaped bundle source')
            if path.name in ('index.md', 'log.md'):
                reserved(path, bundle)
                continue
            before = path.read_bytes()
            after = migrate(before, path)
            inventory.append(path)
            if after != before:
                changes.append((path, before, after))
        except (ValueError, OSError) as exc:
            errors.append(f'{path.relative_to(root)}: {exc}')
    if errors:
        return 2, 'PARTIAL / unsupported; no files changed:\n' + '\n'.join(errors)
    if index:
        path = bundle / 'index.md'
        before = path.read_bytes() if path.exists() else None
        marker = '<!-- LFG:OKF:INDEX -->'
        if before is not None and marker not in before.decode():
            raise ValueError('Existing user-owned index preserved; generate manually or move explicitly')
        after = ('---\nokf_version: "0.2"\n---\n\n' + marker + '\n# Project knowledge\n' +
                 '\n'.join('* [' + p.stem.replace('[', '').replace(']', '') + '](' +
                           quote(p.relative_to(bundle).as_posix(), safe='/.-_') + ')' for p in inventory) + '\n').encode()
        if before != after:
            changes.append((path, before, after))
    if not write:
        return 0, 'Dry run; ' + str(len(changes)) + ' file(s) would change:\n' + '\n'.join(str(p.relative_to(root)) for p, _, _ in changes)
    if journal.exists():
        previous = json.loads(journal.read_text())
        if previous.get('status') == 'in-progress':
            # Resume the original frozen plan; never regenerate it from partially migrated inputs.
            if previous.get('bundle') != str(bundle.relative_to(root)):
                raise ValueError('Different bundle has an incomplete migration; restore/resume it first')
            changes = [(root / item['path'], base64.b64decode(item['before']) if item['before'] is not None else None,
                        base64.b64decode(item['after'])) for item in previous['files']]
            record = previous
        else:
            record = None
    else:
        record = None
    if not changes:
        return 0, 'Metadata already current; no verification claims added.'
    if record is None:
        record = {'status': 'in-progress', 'bundle': str(bundle.relative_to(root)), 'files': [
            {'path': str(p.relative_to(root)), 'before': base64.b64encode(before).decode() if before is not None else None,
             'after': base64.b64encode(after).decode()} for p, before, after in changes]}
        replace(journal, json.dumps(record, indent=2) + '\n', journal.read_bytes() if journal.exists() else None)
    for path, before, after in changes:
        current = path.read_bytes() if path.exists() else None
        if current == after:
            continue
        replace(path, after, before)
    record['status'] = 'complete'
    replace(journal, json.dumps(record, indent=2) + '\n', journal.read_bytes())
    outside = [str(p.relative_to(root)) for p in context_paths(root).values() if not p.is_relative_to(bundle)]
    return (1 if outside else 0), ('Metadata migrated; no verification claims added.' +
                                  (' PARTIAL configured context outside bundle: ' + ', '.join(outside) if outside else ''))
