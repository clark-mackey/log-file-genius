#!/usr/bin/env python3
"""Persist evaluator evidence, never private host directories or authentication."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import re
import statistics
import tarfile

HERE = Path(__file__).resolve().parent
p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
a = p.parse_args()
dest = HERE / 'evidence'
dest.mkdir(exist_ok=True)
rows = json.loads((a.base / 'summary.json').read_text())
# Reject credential-shaped values before writing any trace. Paths alone are not
# credentials; private host trees are never included. This is a bounded scan,
# not a guarantee against every possible secret encoding.
credential_patterns = [r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',
                       r'\b(?:sk-[A-Za-z0-9_-]{20,}|gh[pousr]_[A-Za-z0-9]{30,})',
                       r'\beyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}']
for row in rows:
    directory = a.base / 'results' / row['trial']
    for name in ('evidence.json', 'prompt.txt', 'parent-brief-original.txt', 'invocation.json', 'stderr.txt'):
        path = directory / name
        if path.exists() and any(re.search(pattern, path.read_text()) for pattern in credential_patterns):
            raise SystemExit(f'Credential-shaped value found in {row["trial"]}/{name}; export stopped.')
ledger = []
with gzip.open(dest / 'traces.jsonl.gz', 'wt', encoding='utf-8') as zipped:
    for row in rows:
        directory = a.base / 'results' / row['trial']
        path = directory / 'evidence.json'
        evidence = json.loads(path.read_text()) if path.exists() else row
        for name in ('prompt.txt', 'parent-brief-original.txt', 'invocation.json', 'stderr.txt'):
            if (directory / name).exists():
                evidence[name] = (directory / name).read_text()
        if row.get('contamination_hits') or row.get('role_ambiguous'):
            verdict = 'invalid'
        elif row.get('returncode') != 0:
            verdict = 'run-failed-or-not-started'
        elif row['kind'].startswith('native'):
            verdict = 'diagnostic'
        elif row['kind'] == 'behavior' and row.get('read_cap_demonstrably_exceeded'):
            verdict = 'fail-read-budget'
        elif row['kind'] == 'behavior':
            verdict = 'not-passed-unadjudicated-or-unknown'
        else:
            verdict = 'maintenance-or-child-review'
        evidence['gate_result'] = verdict
        zipped.write(json.dumps(evidence) + '\n')
        compact = {k:v for k,v in row.items() if k not in ('source_read_events', 'limitations')}
        compact['gate_result'] = verdict
        ledger.append(compact)
(dest / 'trials.json').write_text(json.dumps(ledger, indent=2)+'\n')

# Exact initial Git/doc snapshots, with runtime reconstructible from recorded refs.
# private-hosts (including authentication symlinks) is never traversed or archived.
with tarfile.open(dest / 'fixtures.tar.gz', 'w:gz') as archive:
    def keep(info):
        if any(part in ('.log-file-genius', '__pycache__') for part in Path(info.name).parts):
            return None
        return info
    archive.add(a.base / 'seeds', arcname='fixtures', filter=keep)
    archive.add(a.base / 'oracles', arcname='initial-machine-oracles')
    archive.add(a.base / 'setup', arcname='installer-output')
    if (a.base / 'batches').exists():
        archive.add(a.base / 'batches', arcname='batch-plans')
    archive.add(a.base / 'protocol.sha256', arcname='initial-protocol.sha256')

def median(values):
    return statistics.median(values) if values and all(v is not None for v in values) else None

# Three-arm comparison requires equivalent task facts and the same actual prompt.
# The initial delegated prompt was role-ambiguous; ordinary owner fixtures omitted
# project instructions. Keep those rows in the ledger, outside matched medians.
comparison = []
for host in ('codex', 'claude'):
    excluded = {'delegated', 'brownfield', 'override'}
    fixtures = sorted({r['fixture'] for r in ledger if r['kind'] == 'behavior' and r['condition'] == 'candidate'} - excluded)
    selected = {}
    for condition in ('candidate', 'baseline', 'ordinary'):
        selected[condition] = [r for r in ledger if r['kind'] == 'behavior' and r['host'] == host and
                               r['condition'] == condition and r['fixture'] in fixtures and r['trial'].endswith('-1') and
                               r.get('returncode') == 0 and not r.get('timed_out') and
                               not r.get('contamination_hits') and not r.get('role_ambiguous') and
                               not r.get('ordinary_owner_instruction_missing')]
    common = set.intersection(*(set(r['fixture'] for r in v) for v in selected.values()))
    for condition, group in selected.items():
        group = [r for r in group if r['fixture'] in common]
        comparison.append({'host': host, 'condition': condition, 'matched_tasks': len(group),
                           'fixtures': sorted(common),
                           'median_discovery_estimated_tokens': median([r.get('discovery_estimated_tokens') for r in group]),
                           'median_tool_output_estimated_tokens': median([r.get('tool_output_estimated_tokens') for r in group]),
                           'median_source_read_lower_bound': median([r.get('source_read_lower_bound') for r in group])})
(dest / 'comparisons.json').write_text(json.dumps(comparison, indent=2)+'\n')

fixtures = json.loads((HERE.parents[2] / 'product/tests/context-fixtures.json').read_text())['fixtures']
categories = []
for host in ('codex', 'claude'):
    for fixture in fixtures:
        name = fixture['id']
        repetitions = range(4,7) if name == 'delegated' or (host == 'codex' and name == 'nested') else range(1,4)
        ids = [f'behavior-{host}-candidate-{name}-{r}' for r in repetitions]
        group = [r for r in ledger if r['trial'] in ids]
        categories.append({'host': host, 'fixture': name, 'required': 3, 'completed': len(group),
                           'passes': 0, 'fail_read_budget': sum(r['gate_result'] == 'fail-read-budget' for r in group),
                           'invalid': sum(r['gate_result'] == 'invalid' for r in group),
                           'trials': ids,
                           'status': 'failed' if any(r['gate_result'].startswith('fail') for r in group) else 'not-passed'})
(dest / 'categories.json').write_text(json.dumps(categories, indent=2)+'\n')

table = ['# Complete attempt ledger', '',
         'Every attempt is retained. “Fail-read-budget” is a necessary-condition failure,',
         'not a claim that all semantic criteria were independently passed. Native rows',
         'are diagnostic; maintenance and child rows require their separate audit.', '',
         '| Trial | Verdict | Read lower bound | Native body / wrapped estimate |',
         '|---|---|---:|---:|']
for row in ledger:
    table.append(f"| {row['trial']} | {row['gate_result']} | {row.get('source_read_lower_bound', 'unknown')} | "
                 f"{row.get('native_instruction_estimated_tokens')} / {row.get('native_wrapped_instruction_estimated_tokens')} |")
(dest / 'LEDGER.md').write_text('\n'.join(table)+'\n')
environment = {'platform': platform.platform(), 'machine': platform.machine(), 'python': platform.python_version(),
               'candidate': 'c2d0dbb4791a41969249c932a3ae398108253106', 'baseline': '7dffd54',
               'human_trials_completed': 0,
               'runtime_copy': 'Exact git-archived product snapshots copied into consumer .log-file-genius; not a registered submodule.',
               'installer_choice': 'claude-code for both native host trials; shared AGENTS permits Codex discovery.',
               'unsupported_hosts': ['Hermes', 'Grok Build', 'custom bots', 'custom OKF consumers'],
               'protocol_sha256': hashlib.sha256((HERE/'PROTOCOL.md').read_bytes()).hexdigest()}
(dest / 'environment.json').write_text(json.dumps(environment, indent=2)+'\n')
(dest / 'README.md').write_text('''# Evaluator-only evidence

This bundle includes expected answers and must not be given to trial agents or
human readers. Distribute only the individual human/reader-0N.zip packages.
Traces preserve outputs, instruction envelopes, prompts, failed diagnostics and
local model identifiers. Authentication directories are excluded. A bounded
credential-pattern scan passed before export; it is not a universal secret audit.

Comparisons use prespecified repetition 1 because controls have one repetition.
Invalid, failed-process and inequivalent owner-instruction rows are excluded as
whole matched triples. Budget failures remain in descriptive cost comparisons:
discarding expensive failures would bias those estimates. These are not passing
task costs or proof of correctness. Candidate repeats 2–3 remain in the full ledger
and critical-category denominators. Corrected cohorts are labeled separately.
''')
hashes = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in sorted(dest.iterdir()) if f.is_file() and f.name != 'SHA256.json'}
(dest / 'SHA256.json').write_text(json.dumps(hashes, indent=2)+'\n')
print(json.dumps({'packaged_attempts': len(ledger), 'comparison_rows': len(comparison), 'human_completed': 0}))
