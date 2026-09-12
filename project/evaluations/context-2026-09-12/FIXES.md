# Context fixes — development verification

Product changes address the observed instruction gaps without adding a runtime
feature or dependency. Main remains unchanged; release acceptance is still open.

## Cause and change

The original startup retained neither an explicit read budget nor a carry-forward
rule for unresolved work. Fresh traces re-read sources for citations and scanned
unrelated components; a lesson handoff replaced the pending amount fix. Baseline
wording also let Codex advance a code baseline to a documentation-only handoff.

- Startup now carries pending tasks, verification and blockers until evidenced
  resolution or explicit cancellation; the guide requires comparing old/new STATE.
- The baseline is explicitly the last checked code commit/branch; documentation-only
  commits do not advance it, and dirty-tree test evidence is described separately.
- Discovery explicitly allows eight source reads including repeats, reuses existing
  sources/citations and reports gaps at the limit. Governing ADRs cannot be omitted
  to fit the cap; later batches do not reset the cumulative count.
- Detailed CLI/recovery instructions remain on demand in the existing guide. The
  guide specifies locating a nested repository root once and avoiding parent scans.

Five product files changed initially: startup renderer, generated AGENTS, context
guide, maintenance rule and generator tests. No product architecture or dependency
was added. Existing native pointers, configured paths, decision unions, supersession,
ownership and unknown-evidence requirements remain.

## Deterministic checks

The new observed-Codex-wrapper tests failed before the fix at 271/default and
285/custom-path estimated tokens, while the old body-only test passed. Both wrapper
regressions pass with the final startup. The fixture represents a recorded host
format and consumer path length; it does not guarantee a limit for arbitrary owner
instructions, nested overrides or longer paths. All 254 product tests pass. Generated
AGENTS matches its source; diff checks pass. Estimates remain ceil(characters/4).

## First native pilot:12c051e

Seven bounded sessions completed with no process failures or timeouts: Codex lesson
three times, Claude lesson once, fresh discovery on both hosts and custom paths on
Codex. This is a development pilot; original acceptance results remain intact.

All four lesson trials retained the prior amount task, its validation state and
blocker while recording the retry incident as local-only. No application code changed.
However, all three Codex trials advanced the baseline to the preceding documentation
commit. Claude kept the correct code baseline. This led to the explicit baseline
correction, rather than treating fact retention alone as success.

| Discovery | Read lower bound | Native wrapped estimate | Tool-output estimate |
|---|---:|---:|---:|
| Codex fresh | 21 | 242 | 11,450 |
| Codex custom paths | 23 | 248 | 9,441 |
| Claude fresh | 11 | Unknown | 6,162 |

Reuse guidance alone did not solve the read-budget failure. The final startup makes
the existing eight-read limit explicit; it does not relax it. Claude injected bytes
remain unknown. The model/host versions and synthetic-fixture limitations match the
original report. Codex commits remained sandbox-blocked; no zero-effort claim follows.

## Focused final startup check:81edfd1

Both focused sessions completed without process failures or timeouts. The lesson
handoff preserved the original code baseline `5d03b604`, the pending amount fix,
unverified check and blocker, plus the new local-only retry incident. Tracked changes
were confined to logs; the new incident was retained separately. No application code
changed. The local commit was still blocked, so commit effort remains unavailable. The lesson
used at least ten source reads plus two opaque read operations; it demonstrates
preservation, not eight-read maintenance compliance.

Fresh discovery used exactly eight explicit source reads (manual command audit; no
opaque reads), 243 native wrapped estimated tokens and 1,848 tool-output estimated
tokens. It read STATE, index, ADR-001 and relevant application/check files, identified
the integer-return fix, ran the failing check, and listed unread scope at the limit.
Its total discovery estimate is 2,091; this is reported separately from the startup
and packet caps. It noted the different HEAD/baseline but did not inspect the intervening
commit diff, so complete freshness reconciliation is not certified. A later documentation
clarification makes missing-index searches use the remaining budget; the pilot's
startup bytes are identical to the final renderer.

## Evidence and limits

[Fix evidence](fix-evidence/) is evaluator-only and must not go to human participants.
It retains trial traces, prompts, final STATE/incident artifacts, initial synthetic
fixtures and source revisions. Authentication trees are excluded. A bounded scan for
common credential-shaped values precedes export.

Terra code-owl independently reviewed the product changes and first-pilot artifacts.
Its findings added pending verification, explicit code-baseline semantics and a
remaining-budget clarification. Text assertions protect instruction distribution;
they are not proof of model compliance. No full acceptance suite or human trial was
repeated. Three real-reader packages remain prepared with zero participants.


## Status

DONE_WITH_CONCERNS: the focused failures have targeted instruction fixes and bounded
positive development evidence. No 13-fixture, three-repetition acceptance rerun was
performed. Freshness reconciliation, other fixtures/models, Codex commit effort,
Claude injected bytes and real-reader gates remain open. Do not promote a release
based on these nine development trials. Human packages remain unissued; update them
to the final candidate before beginning actual reader trials.

Final Terra audit corroborated the focused facts and identified the maintenance read
count caveat above. No acceptance pass is inferred from successful process completion.
