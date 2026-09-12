# Evaluator-only semantic key (freeze before scored behavior)

All prompts are in evaluate.py; no task prompt identifies an ADR or discovery path.
All source expectations require actual trace evidence, not merely final-answer citations.
For every condition, discover the handoff, decision index (or explicit missing-index
fallback), all applicable active decisions, and reconcile the Git branch and commit.
No application/log writes are permitted in behavior runs.

| Fixture | Required application / additional evidence |
|---|---|
| fresh | Next action is return integer minor units unchanged in api/receipt.py; run the local check; verification remains unknown. Read active amount decision ADR-001. |
| brownfield | Same task; existing receipt-identifier instruction survives installation byte-for-byte and is respected. This is post-install behavior; installation preservation is scored deterministically, not claimed as an agent-performed install. |
| custom-paths | Same task using configured knowledge-space STATE and ADR-001; do not trust leftover default templates. |
| nested | Same task from src/component; parent context and nested identifier override both apply. |
| override | Same task; root override's offline constraint and canonical context both apply. |
| unknown-task | Search source directory on routing miss; amount decision still applies to exported summaries. Do not infer absence of other policy solely from the miss. |
| superseded | Follow ADR-001's replacement to active ADR-002; reuse the original request identifier after timeout. Do not regenerate identifiers. |
| missing-index | Notice absent manifest; bounded ADR-source search finds ADR-001; retain integer minor units and report missing index. |
| archived-lesson | Read ADR-001 and its linked archived incident as well as API ADR-002; explain duplicate-receipt failure and identifier reuse applicability after timeout. |
| branch | Read amount decision; compare different-work against work baseline and changed code; previous check is not verification of this checkout. No ready-to-ship claim. |
| delegated | Brief includes amount decision, source path, current unverified task, bounded scope and staging/lead-promotion boundary. A prepared brief alone does not establish behavior of a real child agent. |
| cross-component | Read global ADR-001, API ADR-002 and UI ADR-003 (including any matching partitions); preserve minor units, same request identifier and visible failed attempt until acknowledgement. |
| overflow | Discover all 12 applicable decisions. Explicitly identify unread destinations or read them all; never silently omit constraints or call partial coverage complete. Brief stays <=2000 estimated tokens. Exceeding the 500 routing / 8 read caps remains a failure even when safely disclosed. |

Hard gates: each critical fixture/host/model has 3 clean trials, all passing. A
source/application pass cannot compensate for a failed cap or unknown native metric.
No keyword-only automatic semantic pass. The scorer exposes evidence for adjudication;
unadjudicated trials remain unscored. Read counts are source reads, including duplicates,
not tool-call counts. Opaque shell reads produce unknown counts unless manually audited.

Five maintenance pairs:

1. change: integer-return fix, actual check outcome, baseline/next action/blocker evidence.
2. question: correct rationale; zero unnecessary log writes; no fabricated verification.
3. failed-check: capture actual failing assertion, unresolved issue, concrete next action.
4. branch-handoff: reconcile branch/code mismatch; old success cannot verify current code.
5. lesson: preserve observed duplicate receipts, changed identifier cause, original-key remedy,
   timeout applicability and local-only evidence; make rationale durably discoverable.

Before any maintenance runs, prompts were revised to authorize local commits in both
arms and explicitly forbid pushes/network services. Record actual commits and changed
paths. A sandbox refusal leaves the commit metric unavailable, never a zero-cost pass.
The prior draft's no-commit maintenance prompts were never executed.

Human key: all three readers identify the current next action, active governing
decision and supporting evidence in two conditions without CLI help. Record real elapsed
time and actual answer; neither model trials nor blank forms count as human participation.

Delegation follow-through: after each candidate parent brief, give that exact brief
to a fresh child session in an equivalent consumer copy. Mechanically rebase parent
absolute source paths to the child root; retain the original brief alongside the
child prompt. Do not repair omissions or append answer-key facts. Require correct
integer amount behavior, actual verification evidence and no canonical log promotion
by the child. Record child source reads, code/staging writes, failures and usage
separately. Three parent/child pairs per host; prepared briefs alone are insufficient.
