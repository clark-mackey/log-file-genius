#!/usr/bin/env python3
"""Capture Claude's local /context loader records after the model queue drains."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import json
from pathlib import Path
import time
import evaluate

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
a = p.parse_args()
deadline = time.monotonic() + 1800
while True:
    plans = [json.loads(p.read_text()) for p in (a.base / 'batches').glob('*.json')]
    jobs = [job for plan in plans if any(j[5].startswith('maintenance-') for j in plan) for job in plan]
    if jobs:
        names = [f'{j[5]}-{j[1]}-{j[2]}-{j[3]}-{j[4]}' for j in jobs]
        if all(any((a.base / 'results' / n / f).exists() for f in ('result.json','attempt-error.json')) for n in names):
            break
    if time.monotonic() > deadline:
        raise SystemExit('Maintenance queue did not drain; native sweep not started.')
    time.sleep(2)
pending = []
for condition in ('candidate','baseline','ordinary'):
    for fixture in evaluate.TASKS:
        name = f'native-context-claude-{condition}-{fixture}-1'
        if not (a.base / 'results' / name / 'result.json').exists():
            pending.append((a.base,'claude',condition,fixture,1,'native-context'))
def invoke_recorded(job):
    try:
        return evaluate.invoke(*job)
    except Exception as error:
        trial = f'{job[5]}-{job[1]}-{job[2]}-{job[3]}-{job[4]}'
        out = a.base / 'results' / trial
        out.mkdir(parents=True, exist_ok=True)
        (out / 'attempt-error.json').write_text(json.dumps({'trial': trial,
            'host': job[1], 'condition': job[2], 'fixture': job[3], 'kind': job[5],
            'status': repr(error)}, indent=2))

with ThreadPoolExecutor(max_workers=4) as pool:
    for _ in pool.map(invoke_recorded, pending):
        pass
print('Claude local native-loader sweep complete.', flush=True)
