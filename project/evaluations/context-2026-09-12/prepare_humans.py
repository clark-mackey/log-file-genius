#!/usr/bin/env python3
"""Prepare documents for real readers; never populate reader answers or timings."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess

HERE = Path(__file__).resolve().parent
parser = argparse.ArgumentParser()
parser.add_argument('--base', type=Path, required=True)
args = parser.parse_args()
destination = HERE / 'human'
if destination.exists():
    raise SystemExit('Refusing to replace existing human materials or reader responses.')
key = []
for reader, fixture, order in [(1, 'fresh', ['candidate','baseline']),
                              (2, 'branch', ['baseline','candidate']),
                              (3, 'archived-lesson', ['candidate','baseline'])]:
    folder = destination / f'reader-{reader:02}'
    folder.mkdir(parents=True)
    for letter, condition in zip(['A','B'], order):
        source = args.base / 'seeds' / condition / fixture
        packet = folder / f'packet-{letter}'
        packet.mkdir()
        for item in ['README.md', 'logs', 'api', 'ui', 'check.py']:
            path = source / item
            if path.is_dir():
                shutil.copytree(path, packet / item)
            elif path.exists():
                shutil.copy2(path, packet / item)
        branch = subprocess.check_output(['git','-C',str(source),'branch','--show-current'],text=True).strip()
        commit = subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
        evidence = f'# Checkout evidence supplied to the reader\n\nBranch: {branch}\nCommit: {commit}\nWorking tree: clean.\nNo checks were executed for this document package. The application source is included.\n'
        (packet / 'checkout-evidence.md').write_text(evidence)
        with (packet / 'README.md').open('a') as f:
            f.write('\n[Checkout evidence](checkout-evidence.md).\n')
        key.append({'reader': reader, 'packet': letter, 'condition': condition, 'fixture': fixture})
    objective = ('The current handoff concerns receipt validation on this checkout.' if reader != 3 else
                 'A receipt submission has timed out. Include a proposed retry plan that avoids repeating earlier failures.')
    (folder / 'START-HERE.md').write_text('''# Reader exercise

You are taking over this small receipt project. Use a text editor or document
viewer. Do not use a CLI or ask an AI assistant for answers. Start in packet A's
README, then repeat independently for packet B. You may follow any document link.

For each packet, identify the next action, the governing decision and its rationale,
the evidence source, and what remains unverified. Record the elapsed reading time.
Do not inspect other readers' packets or evaluator files. Stop after ten minutes per
packet if you cannot find an answer; record what prevented you from finding it.

Record answers in RESPONSE.md. We are testing the documents, not you. Partial or
unsuccessful answers are useful evidence. Do not invent a time or an answer.
''' + '\nTask focus: ' + objective + '\n')
    (folder / 'RESPONSE.md').write_text('''# Reader response — not yet performed

Reader alias:
Date:
Prior familiarity with LFG or this project:

## Packet A

Start time:
End time / elapsed seconds:
Next action:
Governing decision and rationale:
Evidence file/link:
Unverified facts or blockers:
Where navigation failed (if any):

## Packet B

Start time:
End time / elapsed seconds:
Next action:
Governing decision and rationale:
Evidence file/link:
Unverified facts or blockers:
Where navigation failed (if any):

## After both packets

Did the first packet affect how you searched the second?
Which packet was easier to use, and why?
''')
    shutil.make_archive(str(destination / f'reader-{reader:02}'), 'zip', folder)
(destination / 'EVALUATOR-ONLY.json').write_text(json.dumps(key, indent=2)+'\n')
(destination / 'FACILITATOR.md').write_text('''# Facilitator instructions — do not send to readers

Status: PREPARED; zero readers recruited, zero trials completed.

Recruit three real readers. Give each only their numbered zip, without naming the
conditions or showing ORACLE.md. Do not send the whole evaluation directory.
Retain EVALUATOR-ONLY.json privately until responses are locked. Readers 1/3 see
candidate first; reader 2 sees baseline first. Small sample and learning effects
prevent general-population claims. No reader participation is simulated.

Before timing, confirm their editor can follow local Markdown links. Facilitation
may explain editor mechanics but must not reveal paths or answers. Record assistance.
Collect the unedited RESPONSE.md and record reader alias, prior experience and any
withdrawal. Score both packets independently using the evaluator oracle. All three
task/reader trials must identify next action, governing decision and evidence.
Report actual elapsed times and every failure; blank forms are not passes.

Readers 1 and 2: next action is correct api/receipt.py to preserve integer minor units
and run the local check; governing policy is ADR-001. Reader 2 must recognize that
the changed branch and code invalidate earlier verification.

Reader 3: next action is plan timeout retries using the original request identifier,
governed by ADR-002 and supported by the archived duplicate-receipt incident linked
from ADR-001. The amount correction remains a separate recorded pending item, not a
substitute answer to the retry task. Require the timeout applicability and local-only
evidence distinction. An amount-only answer does not pass reader 3's exercise.
''')
print('Prepared 3 blinded reader zip packages; no human participation claimed.')
