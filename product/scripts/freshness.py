"""Read-only handoff evidence. Dates never establish verification."""
import re
import subprocess
from context_paths import context_paths


def git(root, *args):
    result = subprocess.run(['git', '-C', str(root), *args], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else None


def assess(root):
    paths = context_paths(root)
    path = paths['state']
    text = path.read_text(encoding='utf-8') if path.exists() else ''
    fields = {}
    for key in ('Baseline branch', 'Baseline commit', 'Next action', 'Tests', 'Blockers'):
        values = re.findall(r'^\*\*' + key + r':\*\*\s*(.+)$', text, re.M)
        fields[key] = values[0].strip() if len(values) == 1 else None
    branch = git(root, 'branch', '--show-current')
    head = git(root, 'rev-parse', 'HEAD')
    issues = []
    baseline = fields['Baseline commit']
    if not branch or not head:
        issues.append('Checkout evidence unavailable or detached; reconcile manually.')
    if not fields['Baseline branch'] or fields['Baseline branch'] != branch:
        issues.append('Missing or different baseline branch.')
    if not baseline or not re.fullmatch(r'[0-9a-f]{7,40}', baseline):
        issues.append('Missing or invalid baseline commit.')
        changes = None
    else:
        resolved = git(root, 'rev-parse', '--verify', baseline + '^{commit}')
        ancestor = subprocess.run(['git', '-C', str(root), 'merge-base', '--is-ancestor', baseline, 'HEAD'], capture_output=True).returncode == 0
        if not resolved or not ancestor:
            issues.append('Baseline is unavailable or not an ancestor of this checkout.')
        changes = git(root, 'diff', '--name-only', baseline, '--') if resolved else None
    changed = changes.splitlines() if changes else []
    def is_context(name):
        candidate = (root / name).resolve()
        return (candidate in (paths['state'], paths['changelog'], paths['devlog']) or
                any(candidate.is_relative_to(paths[k]) for k in ('adr_dir', 'incidents_dir')))
    code_changes = [name for name in changed if not is_context(name)]
    if code_changes:
        issues.append('Files differ from baseline; reconcile affected facts (not necessarily all state).')
    working = git(root, 'status', '--porcelain')
    work_paths = set()
    for args in (('diff', '--name-only'), ('diff', '--cached', '--name-only'), ('ls-files', '--others', '--exclude-standard')):
        output = git(root, *args)
        work_paths.update(output.splitlines() if output else [])
    if working and any(not is_context(name) for name in work_paths):
        issues.append('Working tree differs; inspect relevant changes before trusting handoff.')
    for field in ('Next action', 'Tests', 'Blockers'):
        if not fields[field]:
            issues.append(f'Missing handoff evidence: {field}.')
    sections = re.split(r'^## ', text, flags=re.M)
    current = next((s for s in sections if s.startswith('Current Context')), '')
    last = next((s for s in sections if s.startswith('Last Session')), '')
    # Conservative signal, not a semantic verifier. Reader owns unresolved contradictions.
    if ((re.search(r'\b(released|merged|complete)\b', current, re.I) and
         re.search(r'\b(awaiting|pending|not yet)\b', last, re.I))):
        issues.append('Possible Current Context / Last Session contradiction; compare the named work.')
    if not current or not last:
        issues.append('Missing Current Context or Last Session.')
    return {'status': 'unknown' if issues else 'baseline-matches; reader must reconcile factual claims',
            'branch': branch, 'head': head, 'handoff': fields,
            'changed_paths': code_changes, 'changed_context': [name for name in changed if is_context(name)], 'issues': issues,
            'external_status': 'unknown; check dated external evidence separately'}
