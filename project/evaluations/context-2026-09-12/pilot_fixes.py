#!/usr/bin/env python3
"""Bounded development pilot; never replaces the frozen acceptance corpus."""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from collections import deque
import json
from pathlib import Path
import evaluate
from collect import collect

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
p.add_argument('--candidate', required=True)
p.add_argument('--focused', action='store_true', help='Only Codex lesson and fresh discovery')
a = p.parse_args()
if (a.base / 'results').exists():
    raise SystemExit('Use a fresh base; pilot evidence must not be overwritten.')
a.candidate = evaluate.git(evaluate.REPO, 'rev-parse', a.candidate)
evaluate.export(a.candidate, a.base / 'sources/candidate')
for fixture in ('fresh', 'custom-paths'):
    evaluate.seed(a.base, 'candidate', fixture)
jobs = deque([('codex','fresh',1,'maintenance-lesson'), ('codex','fresh',1,'behavior')] if a.focused else
             [('codex','fresh',n,'maintenance-lesson') for n in range(1,4)] +
             [('claude','fresh',1,'maintenance-lesson'),
              ('codex','fresh',1,'behavior'), ('claude','fresh',1,'behavior'),
              ('codex','custom-paths',1,'behavior')])
plan = {'candidate': a.candidate, 'scope': 'development pilot; not acceptance',
        'jobs': list(jobs), 'original_caps_unchanged': True}
evaluate.write(a.base/'plan.json', json.dumps(plan, indent=2))
failures = {}
with ThreadPoolExecutor(max_workers=4) as pool:
    active = {}
    while jobs or active:
        while jobs and len(active) < 4:
            job = jobs.popleft()
            host, fixture, repetition, kind = job
            name = f'{kind}-{host}-candidate-{fixture}-{repetition}'
            if failures.get(host, 0) >= 2:
                evaluate.write(a.base/'results'/name/'attempt-error.json', json.dumps({'trial':name,'status':'not-started: repeated host failure'}))
                continue
            active[pool.submit(evaluate.invoke, a.base, host, 'candidate', fixture, repetition, kind)] = (host, name)
        if not active:
            continue
        done, _ = wait(active, return_when=FIRST_COMPLETED)
        for future in done:
            host, name = active.pop(future)
            try:
                future.result()
                result = json.loads((a.base/'results'/name/'result.json').read_text())
                failed = result['returncode'] != 0 or result['timed_out']
                failures[host] = failures.get(host,0)+1 if failed else 0
            except Exception as error:
                failures[host] = failures.get(host,0)+1
                evaluate.write(a.base/'results'/name/'attempt-error.json', json.dumps({'trial':name,'status':repr(error)}))
rows = [collect(a.base, p.parent) for p in sorted((a.base/'results').glob('*/result.json'))]
evaluate.write(a.base/'summary.json',json.dumps(rows,indent=2))
print(json.dumps({'completed':len(rows),'planned':len(plan['jobs']),'scope':'development pilot'}))
