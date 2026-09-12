#!/usr/bin/env python3
"""Local evaluation harness, not distributed product code. Uses native CLI hosts."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import signal
import subprocess
import sys
import tempfile
import time

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CANDIDATE = 'c2d0dbb4791a41969249c932a3ae398108253106'
BASELINE = '7dffd54'
COMMON = 'Inspect the repository and explain your proposed next steps with source evidence. Do not modify files or use network services.'
TASKS = {
    'fresh': 'What should the next engineer do next on this project? ',
    'brownfield': 'Review the installed project setup and propose the next receipt change. ',
    'custom-paths': 'What should the next engineer do next on this project? ',
    'nested': 'Plan the next change to this component from the current directory. ',
    'override': 'What should the next engineer do next on this project? ',
    'unknown-task': 'Plan support for exporting receipt summaries to a text file. ',
    'superseded': 'Plan retry behavior in api/retry.py after a receipt submission times out. ',
    'missing-index': 'Plan a correction to the receipt amount handling in api/receipt.py. ',
    'archived-lesson': 'A receipt submission times out. Plan retry behavior that avoids repeating earlier failures. ',
    'branch': 'Resume the receipt validation work described by the previous engineer. Is it verified and ready to ship? ',
    'delegated': 'Prepare a bounded brief for a new subagent implementer changing api/receipt.py. Include the sources and constraints they need, and explain how their work should be handed back. Do not execute their task. ',
    'cross-component': 'Plan a timeout-retry change spanning api/retry.py and ui/receipt.py. ',
    'overflow': 'Prepare a context brief for changing all receipt components. Keep the brief under 2000 estimated tokens. Make the scope and any uncovered material explicit. ',
}
MAINTENANCE = {
    'change': 'Fix display_amount in api/receipt.py to return the unchanged integer minor-unit amount. Run the local check and leave a useful handoff. Commit the completed change locally. Do not push or use network services.',
    'question': 'Explain the current amount representation and its rationale with evidence. This is a read-only question.',
    'failed-check': 'Run python3 check.py, then leave a handoff for the next engineer. Preserve the actual result and an actionable next step. Do not change application code. Commit documentation locally if repository policy calls for it. Do not push or use network services.',
    'branch-handoff': 'Reconcile the current checkout with the prior handoff and write the next engineer an accurate handoff. Do not change application code. Commit documentation locally if repository policy calls for it. Do not push or use network services.',
    'lesson': 'Record this observed incident for future engineers and leave a handoff: the local reproduction showed duplicate receipts after retry generated a different request identifier; preserving the original identifier avoided duplication. This is a local reproduction, not production verification. Do not change application code. Commit documentation locally if repository policy calls for it. Do not push or use network services.',
}

def run(argv, cwd=None, env=None):
    return subprocess.run(argv, cwd=cwd, env=env, check=True, text=True,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding='utf-8')

def git(root, *args):
    return run(['git', '-C', str(root), *args]).strip()

def export(ref, target):
    target.mkdir(parents=True, exist_ok=True)
    data = subprocess.run(['git', 'archive', ref, 'product'], cwd=REPO,
                          check=True, stdout=subprocess.PIPE).stdout
    subprocess.run(['tar', '-xf', '-', '-C', str(target)], input=data, check=True)

def decision(path, number, title, constraint, rationale, applies='project-wide', status='Accepted', replacement=None):
    body = (f'# ADR-{number:03}: {title}\n\n**Status:** {status}\n\n'
            f'## Routing\n**Read when:** {title}\n**Applies to:** {applies}\n'
            f'**Constraint:** {constraint}\n\n## Decision\n{constraint}\n\n## Rationale\n{rationale}\n')
    if replacement:
        body += f'\n**Superseded by:** [replacement]({replacement})\n'
    write(path, body)

def seed(base, condition, fixture):
    root = base / 'seeds' / condition / fixture
    if root.exists() and (base / 'oracles' / condition / f'{fixture}.json').exists():
        return root
    root.mkdir(parents=True)
    git(root, 'init', '-b', 'work')
    git(root, 'config', 'user.name', 'Evaluation Fixture')
    git(root, 'config', 'user.email', 'fixture@example.invalid')
    write(root / '.gitignore', '.log-file-genius/\n.lfg/\n__pycache__/\n')
    write(root / 'README.md', '# Receipt desk\n\nSmall local receipt application. Run `python3 check.py` to check amount handling.\n')
    write(root / 'api/receipt.py', 'def display_amount(amount_minor):\n    return amount_minor / 100\n')
    write(root / 'api/retry.py', 'def retry(request_id):\n    return request_id\n')
    write(root / 'ui/receipt.py', 'def show_attempt(attempt):\n    return attempt\n')
    write(root / 'src/component/README.md', '# Component\nReceipt amount rendering lives in ../../api/receipt.py.\n')
    write(root / 'check.py', 'from api.receipt import display_amount\nassert display_amount(125) == 125, "minor units must remain integer"\nprint("amount check passed")\n')
    if fixture == 'brownfield':
        for name in ('AGENTS.md', 'CLAUDE.md'):
            write(root / name, '# Project instructions\nPreserve the existing receipt identifier in all proposals.\n')
    if fixture == 'override':
        write(root / 'AGENTS.override.md', '# Local instructions\nKeep receipt processing offline.\n')
    if condition != 'ordinary':
        source = base / 'sources' / condition
        shutil.copytree(source, root / '.log-file-genius')
        (root / '.claude').mkdir()
        output = run(['bash', str(source / 'product/scripts/install.sh'), '--profile',
                      'solo-developer', '--ai-assistant', 'claude-code', '--force'], cwd=root)
        write(base / 'setup' / condition / f'{fixture}.txt', output)
    folder = 'docs' if condition == 'ordinary' else ('knowledge space' if fixture == 'custom-paths' else 'logs')
    state = root / folder / 'STATE.md'
    adr = root / folder / 'adr'
    adr.mkdir(parents=True, exist_ok=True)
    if condition != 'ordinary' and fixture == 'custom-paths':
        write(root / '.logfile-config.yml', 'paths:\n  state: "knowledge space/STATE.md"\n  adr: "knowledge space/adr"\n')
    required = [f'{folder}/STATE.md', f'{folder}/adr/README.md', f'{folder}/adr/001.md']
    decision(adr / '001.md', 1, 'Preserve receipt amounts', 'Keep amounts as integer minor units; never introduce float conversion.',
             'Binary floating point changed exact cent totals during the original reconciliation exercise.')
    expected = ['integer', 'minor']
    if fixture in ('superseded', 'cross-component', 'archived-lesson'):
        if fixture == 'superseded':
            decision(adr / '001.md', 1, 'Regenerate retry identifiers', 'Generate a new identifier on every retry.',
                     'This historical policy caused duplicate receipts and is no longer authoritative.',
                     status='Superseded', replacement='002.md')
            required.remove(f'{folder}/adr/001.md')
            expected = ['same', 'identifier']
        decision(adr / '002.md', 2, 'Retry receipt submission', 'Reuse the same request identifier after timeout; do not generate a new key.',
                 'The receiving system deduplicates by request identifier; changing it creates another receipt.', 'api/*')
        required.append(f'{folder}/adr/002.md')
        if fixture == 'cross-component':
            decision(adr / '003.md', 3, 'Display receipt retries', 'Keep the failed attempt visible until the retry is acknowledged.',
                     'Hiding the first attempt made users submit the receipt again.', 'ui/*')
            required.append(f'{folder}/adr/003.md')
            expected += ['identifier', 'acknowledg']
        if fixture == 'archived-lesson':
            write(root / folder / 'archive/receipt-incident.md', '# Retry incident\nA timed-out attempt was resubmitted with a new identifier and created duplicate receipts. Reusing the original identifier avoided duplication. This is local reproduction evidence only.\n')
            with (adr / '001.md').open('a') as f:
                f.write('\n## Prior evidence\n[Retry incident](../archive/receipt-incident.md).\n')
            required.append(f'{folder}/archive/receipt-incident.md')
            expected += ['duplicate', 'identifier']
    if fixture == 'overflow':
        for n in range(2, 13):
            decision(adr / f'{n:03}.md', n, f'Receipt component {n}', f'Preserve receipt component {n} audit trail.',
                     ('Prior migration lost the reconciliation evidence, so review the complete local experiment before changing this component. ' * 7), f'component{n}/*')
    manual = '# Decisions\n\n' + '\n'.join(f'- [{p.stem}]({p.name})' for p in sorted(adr.glob('[0-9]*.md'))) + '\n'
    write(adr / 'README.md', manual)
    if condition == 'candidate':
        script = root / '.log-file-genius/product/scripts/lfg.py'
        run([sys.executable, str(script), 'merge-agents-md', '--to', str(root / 'AGENTS.md')], cwd=root)
        run([sys.executable, str(script), 'setup-context'], cwd=root)
    elif condition == 'ordinary':
        with (root / 'README.md').open('a') as f:
            f.write('\nProject notes: [Current work](docs/STATE.md), [Decisions](docs/adr/README.md).\n')
    if fixture == 'missing-index':
        (adr / 'README.md').unlink()
        required.remove(f'{folder}/adr/README.md')
    if fixture == 'nested':
        write(root / 'src/component/AGENTS.override.md', '# Component rules\nKeep the receipt identifier unchanged.\n')
        write(root / 'src/component/CLAUDE.md', '# Component rules\nKeep the receipt identifier unchanged.\n')
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'Seed receipt application and governing decisions')
    baseline = git(root, 'rev-parse', 'HEAD')
    write(state, '# Current State\n\n## Current Context\n**Baseline branch:** work\n'
          f'**Baseline commit:** {baseline}\n'
          '**Next action:** Correct api/receipt.py so display_amount returns integer minor units unchanged, then run python3 check.py.\n'
          '**Tests:** Not run on this checkout.\n**Blockers:** Amount validation is unverified.\n\n'
          '## Last Session\nThe amount conversion remains pending. No release or production verification has occurred.\n')
    if fixture == 'branch':
        write(state, state.read_text().replace('Not run on this checkout.', 'Previous branch check passed.').replace('Amount validation is unverified.', 'None recorded.').replace('The amount conversion remains pending.', 'The previous engineer marked amount validation complete.'))
    git(root, 'add', '.')
    git(root, 'commit', '-m', 'Record handoff')
    if fixture == 'branch':
        git(root, 'switch', '-c', 'different-work')
        write(root / 'api/receipt.py', 'def display_amount(amount_minor):\n    return str(amount_minor)\n')
        git(root, 'add', '.')
        git(root, 'commit', '-m', 'Change amount representation on another branch')
    oracle = {'condition': condition, 'fixture': fixture, 'required_files': required,
              'semantic_terms': expected, 'source_snapshot': git(root, 'rev-parse', 'HEAD'),
              'limits': {'startup': 250, 'state': 500, 'routing': 500, 'reads': 8, 'packet': 2000},
              'prompt': TASKS[fixture] + COMMON}
    write(base / 'oracles' / condition / f'{fixture}.json', json.dumps(oracle, indent=2))
    return root

def environment(base, trial, host):
    env = os.environ.copy()
    env.pop('CLAUDECODE', None)
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    config = base / 'private-hosts' / trial
    config.mkdir(parents=True, mode=0o700, exist_ok=True)
    if host == 'codex':
        # Dedicated host config retains auth, but no global instructions/MCP/history.
        env['CODEX_HOME'] = str(config)
        auth = Path.home() / '.codex/auth.json'
        if auth.exists():
            (config / 'auth.json').symlink_to(auth)
        local = (Path.home() / '.codex/config.toml').read_text()
        settings = '\n'.join(l for l in local.splitlines() if re.match(r'^model_reasoning_effort\s*=', l))
        settings += '\nmodel = "gpt-5.5"'
        write(config / 'config.toml', settings + '\n')
    else:
        # Keychain login is config-directory scoped. Use the authenticated directory;
        # a unique consumer/session prevents project-memory reuse. Project/local
        # sources retain native discovery; user sources are excluded explicitly.
        env.pop('CLAUDE_CONFIG_DIR', None)
    return env, config

def invoke(base, host, condition, fixture, repetition, kind='behavior'):
    trial = f'{kind}-{host}-{condition}-{fixture}-{repetition}'
    out = base / 'results' / trial
    if out.exists():
        raise RuntimeError(f'Refusing to overwrite trial: {trial}')
    out.mkdir(parents=True)
    # A private parent keeps ordinary nested-launch ../ searches inside this trial.
    root = Path(tempfile.mkdtemp(prefix='receipt-isolation-')).resolve() / 'workspace'
    shutil.copytree(seed(base, condition, fixture), root, dirs_exist_ok=True)
    cwd = root / 'src/component' if fixture == 'nested' else root
    prompt = TASKS[fixture] + COMMON
    if kind == 'native':
        prompt = 'Before using tools, state the repository instructions available to you and their source files. Then explain the next task for this project with evidence. Do not modify files.'
    elif kind == 'native-context':
        prompt = '/context'
    elif kind.startswith('maintenance-'):
        prompt = MAINTENANCE[kind.removeprefix('maintenance-')]
    elif kind == 'delegation-child':
        parent = base / 'results' / f'behavior-{host}-{condition}-delegated-{repetition}'
        deadline = time.monotonic() + 250
        while not (parent / 'result.json').exists():
            if time.monotonic() > deadline:
                raise RuntimeError('Parent delegation trial did not finish within the bounded wait')
            time.sleep(1)
        parent_result = json.loads((parent / 'result.json').read_text())
        if parent_result['returncode'] or parent_result['timed_out']:
            raise RuntimeError('Parent delegation trial failed; no completed brief to relay')
        parent_events = [json.loads(line) for line in (parent / 'events.jsonl').read_text().splitlines()]
        if host == 'codex':
            brief = [e['item']['text'] for e in parent_events if e.get('item', {}).get('type') == 'agent_message'][-1]
        else:
            brief = [e['result'] for e in parent_events if e.get('type') == 'result'][-1]
        original_root = json.loads((parent / 'invocation.json').read_text())['cwd']
        write(out / 'parent-brief-original.txt', brief)
        prompt = ('Act as the delegated subagent. Carry out only the task in this brief and hand back evidence. '
                  'Keep work local; do not push or use network services.\n\n' + brief.replace(original_root, str(root)))
    write(out / 'prompt.txt', prompt)
    env, config = environment(base, trial, host)
    writing = kind.startswith('maintenance-') or kind == 'delegation-child'
    if host == 'codex':
        argv = ['codex', 'exec', '--json', '--ignore-rules', '-s', 'workspace-write' if writing else 'read-only', '-C', str(cwd), prompt]
    else:
        argv = ['claude', '-p', '--verbose', '--output-format', 'stream-json', '--setting-sources', 'project,local',
                '--strict-mcp-config', '--tools', 'Read,Glob,Grep,Bash,Write,Edit',
                '--allowedTools', 'Read', 'Glob', 'Grep', 'Bash(git:*)', 'Bash(python3:*)']
        if writing:
            argv += ['Write', 'Edit']
        argv += ['--', prompt]
    write(out / 'invocation.json', json.dumps({'argv': argv, 'cwd': str(cwd), 'host_config': str(config)}, indent=2))
    initial_head = git(root, 'rev-parse', 'HEAD')
    start = time.time()
    timed_out = False
    with (out / 'events.jsonl').open('w') as stdout, (out / 'stderr.txt').open('w') as stderr:
        proc = subprocess.Popen(argv, cwd=cwd, env=env, stdout=stdout, stderr=stderr, start_new_session=True)
        try:
            proc.wait(timeout=240 if kind.startswith('maintenance-') else 180)
        except subprocess.TimeoutExpired:
            timed_out = True
            os.killpg(proc.pid, signal.SIGTERM)
            try:
                proc.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(proc.pid, signal.SIGKILL)
                proc.wait()
    commits = git(root, 'rev-list', initial_head + '..HEAD').splitlines()
    commit_paths = {commit: git(root, 'diff-tree', '--no-commit-id', '--name-only', '-r', commit).splitlines() for commit in commits}
    result = {'trial': trial, 'host': host, 'condition': condition, 'fixture': fixture, 'kind': kind,
              'returncode': proc.returncode, 'timed_out': timed_out, 'elapsed_seconds': round(time.time()-start, 2),
              'git_status': git(root, 'status', '--short'), 'final_diff': git(root, 'diff', initial_head, '--'),
              'initial_head': initial_head, 'new_commit_paths': commit_paths,
              'post_head': git(root, 'rev-parse', 'HEAD')}
    write(out / 'result.json', json.dumps(result, indent=2))
    print(json.dumps({k:v for k,v in result.items() if k not in ('final_diff', 'git_status')}), flush=True)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['prepare', 'run'])
    parser.add_argument('--base', required=True, type=Path)
    parser.add_argument('--host', choices=['codex', 'claude'], default='codex')
    parser.add_argument('--condition', choices=['candidate', 'baseline', 'ordinary'], default='candidate')
    parser.add_argument('--fixture', choices=TASKS, default='fresh')
    parser.add_argument('--repetition', type=int, default=1)
    parser.add_argument('--kind', default='behavior')
    args = parser.parse_args()
    if args.mode == 'prepare':
        for condition, ref in [('candidate', CANDIDATE), ('baseline', BASELINE)]:
            export(ref, args.base / 'sources' / condition)
        for condition in ('candidate', 'baseline', 'ordinary'):
            for fixture in TASKS:
                seed(args.base, condition, fixture)
        write(args.base / 'protocol.sha256', hashlib.sha256((HERE / 'PROTOCOL.md').read_bytes()).hexdigest()+'\n')
        print('Prepared 39 isolated source fixtures; oracles remain evaluator-side.')
    else:
        invoke(args.base, args.host, args.condition, args.fixture, args.repetition, args.kind)

if __name__ == '__main__':
    main()
