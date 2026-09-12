#!/usr/bin/env python3
"""Bounded native sessions; each run remains a distinct independent trial."""
import argparse
from concurrent.futures import ThreadPoolExecutor, wait, FIRST_COMPLETED
from collections import deque
import json
from pathlib import Path
import time
import evaluate

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
p.add_argument('--conditions', nargs='+', default=['candidate'])
p.add_argument('--hosts', nargs='+', default=['codex', 'claude'])
p.add_argument('--fixtures', nargs='+', default=list(evaluate.TASKS))
p.add_argument('--repetitions', type=int, default=3)
p.add_argument('--maintenance', action='store_true')
a = p.parse_args()
jobs = []
for host in a.hosts:
    for condition in a.conditions:
        if a.maintenance:
            if host == 'claude' and condition == 'candidate':
                jobs.append((a.base, host, condition, 'fresh', 1, 'native-context'))
            for task in evaluate.MAINTENANCE:
                fixture = 'branch' if task == 'branch-handoff' else 'fresh'
                jobs.append((a.base, host, condition, fixture, 1, 'maintenance-' + task))
            if condition == 'candidate':
                if host == 'codex':
                    for repetition in range(4, 7):
                        jobs.append((a.base, host, condition, 'nested', repetition, 'behavior'))
                for repetition in range(4, 7):
                    jobs.append((a.base, host, condition, 'delegated', repetition, 'behavior'))
                for repetition in range(4, 7):
                    jobs.append((a.base, host, condition, 'delegated', repetition, 'delegation-child'))
        else:
            for fixture in a.fixtures:
                for repetition in range(1, a.repetitions + 1):
                    jobs.append((a.base, host, condition, fixture, repetition, 'behavior'))
print(json.dumps({'planned_trials': len(jobs), 'workers': 4}), flush=True)
batch_id = str(time.time_ns())
plan = a.base / 'batches' / f'{batch_id}.json'
plan.parent.mkdir(exist_ok=True)
plan.write_text(json.dumps([list(map(str, j)) for j in jobs], indent=2))
queue = deque(jobs)
infra_failures = {}

def trial_name(job):
    _, host, condition, fixture, repetition, kind = job
    return f'{kind}-{host}-{condition}-{fixture}-{repetition}'

def record_error(job, reason):
    trial = trial_name(job)
    out = a.base / 'results' / trial
    out.mkdir(exist_ok=True, parents=True)
    (out / 'attempt-error.json').write_text(json.dumps({'trial': trial, 'host': job[1],
        'condition': job[2], 'fixture': job[3], 'kind': job[5], 'status': reason}, indent=2))
    print(json.dumps({'trial': trial, 'attempt_error': reason}), flush=True)

with ThreadPoolExecutor(max_workers=4) as pool:
    active = {}
    while queue or active:
        while queue and len(active) < 4:
            job = queue.popleft()
            if infra_failures.get(job[1], 0) >= 2:
                record_error(job, 'not-started: repeated host infrastructure failure')
            else:
                active[pool.submit(evaluate.invoke, *job)] = job
        if not active:
            continue
        done, _ = wait(active, return_when=FIRST_COMPLETED)
        for future in done:
            job = active.pop(future)
            try:
                future.result()
                trial_dir = a.base / 'results' / trial_name(job)
                output = (trial_dir / 'events.jsonl').read_text() + (trial_dir / 'stderr.txt').read_text()
                result = json.loads((trial_dir / 'result.json').read_text())
                if result['timed_out'] or result['returncode'] != 0 or any(s in output for s in ('authentication_failed', 'usage limit', 'requires a newer version', 'Not logged in')):
                    infra_failures[job[1]] = infra_failures.get(job[1], 0) + 1
                else:
                    infra_failures[job[1]] = 0
            except Exception as error:
                record_error(job, repr(error))
                infra_failures[job[1]] = infra_failures.get(job[1], 0) + 1
