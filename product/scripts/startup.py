"""Compact shared startup protocol and preservation-aware native pointers."""
import os
from pathlib import Path
from context_paths import context_paths
from safe_write import replace


def render(root=None):
    if root is None:
        paths = dict(state='logs/STATE.md', adr_dir='logs/adr')
        runtime = '.log-file-genius/product/scripts/lfg.py'
    else:
        paths = {k: v.relative_to(root).as_posix() for k, v in context_paths(root).items()}
        source = Path(__file__).resolve().with_name('lfg.py')
        runtime = source.relative_to(root).as_posix() if source.is_relative_to(root) else '.log-file-genius/product/scripts/lfg.py'
    return ("---\ndoc: AGENTS\ntype: Agent Instructions\nrelated:\n"
            f"  state: {paths['state']}\n  adr_index: {paths['adr_dir']}/README.md\n---\n\n# LFG context\n\n"
            f"Read `{paths['state']}` then `{paths['adr_dir']}/README.md`. Union global, path and task matches; "
            "read active ADRs, follow replacements. Missing/stale index or no match: search ADR sources. "
            "Report unread scope; never assume coverage.\n\n"
            "Compare STATE baseline branch/commit with Git and reconcile Current Context/Last Session contradictions. "
            "Missing evidence is unknown. Log meaningful changes/handoffs; read-only questions need no rewrite. "
            "Subagents stage; lead promotes. Follow project instructions.\n\n"
            f"Repo-root CLI: `python3 \"{runtime}\" --help` (Windows: `python`). "
            "No Python: read Markdown. Missing submodule: `git submodule update --init`. "
            "Procedures: `" + str(Path(runtime).parent.parent.as_posix()) + "/docs/context-guide.md`.\n")


def pointer(path, target, label='LFG:POINTER'):
    old = path.read_bytes() if path.exists() else None
    text = old.decode('utf-8') if old else ''
    begin, end = f'<!-- {label}:BEGIN -->', f'<!-- {label}:END -->'
    block = f'{begin}\n{target}\n{end}'
    if begin in text or end in text:
        if text.count(begin) != 1 or text.count(end) != 1 or text.index(begin) > text.index(end):
            raise ValueError(f'Malformed pointer: {path}')
        text = text[:text.index(begin)] + block + text[text.index(end) + len(end):]
    else:
        text = text.rstrip() + ('\n\n' if text else '') + block + '\n'
    replace(path, text, old)


def install(root):
    """Add native entry points. Full rule removal requires proven shipped bytes."""
    import hashlib
    import json
    root = Path(root).resolve()
    paths = context_paths(root)
    paths['adr_dir'].mkdir(parents=True, exist_ok=True)
    from routing import run
    code, message = run(root, write=True)
    if code:
        raise ValueError(message)
    notices = []
    pointer(root / 'README.md', 'Project context: [STATE](' + paths['state'].relative_to(root).as_posix() +
            '), [decisions](' + paths['adr_dir'].relative_to(root).as_posix() + '/README.md).')
    if (root / '.claude').exists() or (root / 'CLAUDE.md').exists():
        pointer(root / 'CLAUDE.md', '@AGENTS.md')
    # A higher-priority override must point back to the canonical protocol.
    for relative in ('AGENTS.override.md', '.hermes/AGENTS.md', '.hermes/AGENTS.override.md'):
        path = root / relative
        if path.exists():
            dest = os.path.relpath(root / 'AGENTS.md', path.parent).replace(os.sep, '/')
            pointer(path, f'Read [{dest}]({dest}) for LFG context before task work.')
    manifest = Path(__file__).with_name('known_rule_hashes.json')
    known = set(json.loads(manifest.read_text()).values()) if manifest.exists() else set()
    for directory in (root / '.claude/rules', root / '.augment/rules'):
        for path in sorted(directory.glob('*.md')):
            old = path.read_bytes()
            normalized = old.decode('utf-8-sig').replace('\r\n', '\n').replace('\r', '\n')
            if hashlib.sha256(normalized.encode()).hexdigest() in known:
                # Move exact shipped content outside autoload, preserving bytes.
                import uuid
                target = root / '.lfg/retired-rules' / directory.parent.name / (path.name + '.' + uuid.uuid4().hex)
                target.parent.mkdir(parents=True, exist_ok=True)
                # Rename preserves the actual bytes at the instant of movement, even
                # if an editor changed them after the hash check. Never compare/unlink.
                path.rename(target)
                if target.read_bytes() != old:
                    try:
                        os.link(target, path)  # exclusive creation; never overwrite a new source
                    except FileExistsError:
                        pass
                    notices.append(f'Concurrent rule edit preserved at {target}; inspect before continuing.')
            elif 'fragment:' in normalized:
                notices.append(f'Preserved modified rule; inspect duplicate autoload: {path.relative_to(root)}')
    notices.append('Inspect nested/host overrides and duplicate native loading before claiming support.')
    return notices
