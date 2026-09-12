#!/usr/bin/env python3
"""Continue the already-authorized phases after the active candidate batch drains."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

p = argparse.ArgumentParser()
p.add_argument('--base', type=Path, required=True)
a = p.parse_args()
deadline = time.monotonic() + 2400
while len(list((a.base / 'results').glob('behavior-*-candidate-*/result.json'))) < 78:
    if time.monotonic() >= deadline:
        raise SystemExit('Candidate batch did not drain within 40 minutes; later phases not started.')
    time.sleep(5)
batch = Path(__file__).with_name('batch.py')
for options in [
    ['--conditions','baseline','ordinary','--repetitions','1'],
    ['--conditions','candidate','baseline','--maintenance'],
]:
    subprocess.run([sys.executable,str(batch),'--base',str(a.base),*options],check=True)
print(json.dumps({'remaining_phases':'finished'}),flush=True)
