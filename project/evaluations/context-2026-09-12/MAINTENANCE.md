# Maintenance and child audit

Five paired tasks ran on each host. One successful tool invocation writing canonical
logging content counts as one action, including the incident-index generator. A
multi-file patch is one action; repeated edits count again. Git operations and scratch
verification are separate. Exact operation lists and file-write counts are retained
in [maintenance.json](evidence/maintenance.json). This is retrospective trace
adjudication, not a relaxed acceptance threshold. Tool batching limits cross-host comparison.

| Task | Codex candidate / baseline actions | Claude candidate / baseline actions | Claude candidate / baseline doc follow-ups |
|---|---:|---:|---:|
| Code change | 2 / 3 | 3 / 3 | 0 / 0 |
| Read-only question | 0 / 0 | 0 / 0 | 0 / 0 |
| Failed check | 1 / 1 | 2 / 5 | 0 / 1 |
| Branch handoff | 2 / 2 | 3 / 7 | 0 / 1 |
| Durable lesson | 2 / 2 | 4 / 8 | 0 / 1 |
| Median | 2 / 2 | 3 / 5 | 0 / 1 |

For documentation tasks, the first documentation commit is the primary requested
artifact. Later hash-correction commits are follow-ups. Claude baseline failure,
branch and lesson tasks each produced one; candidate tasks did not. Codex
`.git/index.lock` refusals leave its commit-effort metric unavailable. Failed commit
attempts remain in traces and are not interpreted as zero effort.

## Required facts and scope

- Change: all four runs made the identity-return fix and ran the successful check.
  Candidate STATE retained branch, pre-handoff checkout, next action, result and
  blockers. Code and handoff were edited together; a recorded pre-change commit does
  not independently prove the final dirty-tree test outcome. Traces and diffs supply
  that distinction. No release verification is claimed.
- Question: all four left logs unchanged and distinguished the integer-unit decision
  from the implementation's float conversion.
- Failed check: all four retained the failed assertion and concrete amount fix as next
  action. No application fix was silently made in this documentation task.
- Branch handoff: both candidates recorded `different-work`, the changed code baseline,
  and failing current check. Codex baseline retained old `work` baseline fields despite
  describing the mismatch elsewhere; its structured and narrative state disagree.
  Claude baseline documented the actual checkout.
- Lesson: all four recorded duplicate receipts, new-versus-original identifier behavior
  and local-only evidence. Claude candidate distinguished the inferred deduplication
  mechanism from the observation. **Codex candidate dropped the prior pending amount
  fix and blocker from STATE**, replacing them with retry coverage. This fails zero
  omitted facts. It also paired retry work with `check.py`, which only checks amounts.
  Codex baseline weakened the amount item to “may still be pending”; Claude retained
  it explicitly. Improvements elsewhere cannot erase the candidate failure.

Final STATE, modified artifacts, staged child files, diffs, commit paths and handbacks
are persisted in the JSON audit. Full command/output evidence is in the compressed
traces. A model's claim of completeness does not supply missing evidence.

## Delegated children

Six fresh children received parent briefs with roots mechanically rebased. All six
made the identity-return change, ran checks successfully and avoided canonical log
writes. All tracked diffs contain only `api/receipt.py`.

Claude children 4 and 6 wrote promoter-compatible changelog/devlog staging files.
Child 5 wrote generic `handback.md`; that is not evidence of successful promotion.
Child 4 proposed the correct seed commit but subsequently mentioned an inconsistent
old hash. Codex children produced no LFG staged files; child 6 attempted Git staging
and was blocked. No child committed or promoted logs. These observations establish
bounded child execution, not full delegation-gate passage or built-in subagent support.
