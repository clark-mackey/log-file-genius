#!/usr/bin/env python3
"""Retain final handoffs and count trace-audited logging operations."""
import argparse
import json
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
a = p.parse_args()
records = []
for directory in sorted((a.base / 'results').iterdir()):
    if not directory.name.startswith(('maintenance-', 'delegation-child-')):
        continue
    e = json.loads((directory / 'evidence.json').read_text())
    invocation = json.loads((directory / 'invocation.json').read_text())
    root = Path(invocation['cwd'])
    operations, files = [], {}
    for number, tool in enumerate(e['tools']):
        targets = []
        if tool['name'] in ('Write', 'Edit') and not tool.get('is_error'):
            targets = [tool['input']['file_path']]
        elif tool['name'] == 'file_change':
            targets = [change['path'] for change in tool['input']]
        relative = [str(Path(path).relative_to(root)) for path in targets if Path(path).is_relative_to(root)]
        logging = [path for path in relative if path.startswith('logs/')]
        if logging:
            operations.append({'tool': number, 'files': logging})
        if tool['name'] in ('Bash', 'shell'):
            command = tool['input'].get('command', '') if isinstance(tool['input'], dict) else tool['input']
            # Both actual candidate lesson traces invoke the successful generator
            # once. Other shell mutations are commits or scratch-code verification.
            if 'python3 ' in command and 'lfg.py' in command and ' incidents-index' in command:
                operations.append({'tool': number, 'files': ['logs/incidents/README.md'], 'method': 'incidents-index'})
        for path in relative:
            if (root / path).is_file():
                files[path] = (root / path).read_text()
    for path in ['logs/STATE.md', *[str(x.relative_to(root)) for x in (root/'.lfg/staged').glob('**/*.md')]]:
        if (root / path).exists():
            files[path] = (root / path).read_text()
    commits = e['new_commit_paths']
    doc_commits = sum(all(path.startswith('logs/') for path in paths) for paths in commits.values())
    # Trace inspection confirms the initial docs-only commit is the primary task
    # artifact for failure/branch/lesson tasks; later commits correct hash references.
    followups = max(0, doc_commits - (1 if e['kind'] in ('maintenance-failed-check', 'maintenance-branch-handoff', 'maintenance-lesson') else 0))
    records.append({'trial': e['trial'], 'host': e['host'], 'condition': e['condition'], 'kind': e['kind'],
        'logging_operations': operations, 'logging_action_count': len(operations),
        'logging_file_write_count': sum(len(x['files']) for x in operations),
        'documentation_only_followups': followups if e['host']=='claude' else None,
        'commit_paths': commits, 'final_files': files, 'final_diff': e['final_diff'],
        'final_message': e['messages'][-1] if e['messages'] else '',
        'identity_return_diagnostic': e['final_code_simple_identity_return']})
dest = Path(__file__).resolve().parent / 'evidence'
dest.mkdir(exist_ok=True)
(dest/'maintenance.json').write_text(json.dumps(records, indent=2)+'\n')
print(json.dumps({'audited_records': len(records)}))
