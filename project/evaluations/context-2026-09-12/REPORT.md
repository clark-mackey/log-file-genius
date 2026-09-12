# Context-discovery evaluation — local runs complete

Follow-up: [targeted fixes and nine development trials](FIXES.md), then
[correctness-first prerelease criteria and validation](PRERELEASE.md). Original acceptance
results below remain tied to their original candidate and are not overwritten.

**Not release-ready.** Every selected candidate critical behavior trial exceeded the
frozen eight-read cap. Maintenance also lost a required pending handoff fact. No main
promotion, release tag or compatibility acceptance follows from this evaluation.
Product runtime and dependencies are unchanged.

Candidate: merged development `c2d0dbb4791a41969249c932a3ae398108253106`.
Baseline: `7dffd54` / v0.5.0. Work is isolated on `codex/context-evaluation`.

## Evidence and denominators

The [complete ledger](evidence/LEDGER.md) retains **209 attempts and diagnostics**:

| Kind | Count | Interpretation |
|---|---:|---|
| Candidate behavior | 87 | Initial 78 plus nine targeted corrections |
| Baseline / ordinary-doc controls | 52 | One repetition per fixture, host and condition |
| Paired maintenance | 20 | Five tasks × two conditions × two hosts |
| Delegated children | 6 | Three fresh parent/child pairs per host |
| Native/setup probes | 5 | Two failed processes; one disabled-loader diagnostic |
| Claude local `/context` diagnostics | 39 | Zero model API turns; not behavior trials |

The selected critical cohort is 78 trials: 13 fixtures × three sessions × two hosts.
All 26 host/fixture categories have **0/3 passes and 3/3 read-budget failures**.
[Category records](evidence/categories.json) identify every selected trial. Necessary
budget failures establish non-passage; they do not imply every semantic criterion
was independently adjudicated or passed. Full semantic certification remains open.
Noncritical categories were not created by relabeling these critical fixtures; their
separate ten-trial denominators and 90% threshold remain unmet.

The initial six delegated prompts said “new implementer,” leaving subagent ownership
ambiguous. Corrected repetitions 4–6 explicitly name the role. One nested Codex trial
exposed other consumer paths; all three nested Codex repetitions were replaced with
private-parent trials. Invalid originals remain in the ledger. These corrections are
complete; an unchanged full rerun is unnecessary.

## Native loading and cost

Local platform: macOS arm64, Python 3.14.6. Scored hosts: Codex CLI 0.149.1 with selected
`gpt-5.5`, and Claude Code 2.1.269 with observed `claude-opus-5` responses. Codex records
model selection, not an independently exposed backend checkpoint. Its configured
Astra model was rejected by this CLI; no Astra claim is made. An isolated Claude config
failed authentication; another probe disabled native loading through setting sources.
Corrected Claude trials used project/local sources and existing authentication.

Codex rollouts expose instruction text and its actual host message envelope. The
fresh candidate diagnostic measured **233 estimated tokens in the body, 269 with the
envelope**, above the 250 startup cap. Estimates are `ceil(characters / 4)`, not
exact tokenizer counts. Paths and project-owned text can change the envelope size;
brownfield owner instructions are not all attributable to LFG.

Claude local `/context` records directly establish loaded memory files: fresh candidate
loads CLAUDE.md and AGENTS.md; ordinary fresh loads none. The host reports 356 memory
tokens for that candidate diagnostic. This supports native file selection but does
not expose injected bytes or implement the frozen characters/4 estimator. Claude total
discovery estimates remain unknown. Provider usage and narration are recorded separately.

The descriptive comparison uses ten matched tasks per host, prespecified candidate
repetition 1 and corresponding controls. Delegation is excluded for role ambiguity;
brownfield and override are excluded because cached ordinary fixtures omitted owner
instructions. The generator is corrected for future runs; historical controls are not
retroactively repaired. Invalid/process-failed rows are excluded as whole triples.
Budget failures remain in cost comparisons to avoid survivorship bias. These are
**not costs of passing tasks** or proof of correctness-equivalent efficiency.

| Host / condition | Median discovery estimate | Median tool-output estimate | Median read lower bound |
|---|---:|---:|---:|
| Codex candidate | 4,058.5 | 3,789.5 | 14.5 |
| Codex baseline | 8,698 | 4,550 | 14.5 |
| Codex ordinary docs | 1,566 | 1,544 | 11 |
| Claude candidate | Unknown | 4,972 | 13.5 |
| Claude baseline | Unknown | 6,365.5 | 14 |
| Claude ordinary docs | Unknown | 993 | 10 |

Candidate cost improved over current LFG; ordinary docs were cheaper. Duplicate reads,
failed searches and tool-return envelopes count. Explicit read operands provide
conservative lower bounds; opaque shell reads stay unknown.
[Comparison data](evidence/comparisons.json) retain the matched task set.

## Maintenance and delegation

The [maintenance audit](MAINTENANCE.md) covers all five pairs per host. Median logging
actions were Codex 2 vs baseline 2, and Claude 3 vs baseline 5. Claude candidate median
documentation-only follow-ups were 0 vs baseline 1. Codex commit attempts were blocked
by the native sandbox; its commit metric is unavailable rather than zero.

The zero-lost-facts requirement failed: `maintenance-lesson-codex-candidate-fresh-1`
replaced the pending amount-fix handoff with retry work and omitted the amount task.
Both candidate branch handoffs reconciled the current branch and failing check.
Question trials in both conditions made no log changes.

All six actual children changed only tracked `api/receipt.py` to return the amount
unchanged, produced successful check evidence, and left canonical logs untouched.
Claude children wrote ignored staging artifacts; one used a generic handback file
instead of promoter-ready filenames. Codex children returned prose without LFG staged
artifacts. One Claude handback included an inconsistent old commit reference. These
are bounded successes, not full delegation certification. Sessions were separate
CLI processes, not a test of either host's built-in Agent tool. Parent briefs were
relayed unchanged except mechanical absolute-path rebasing.

## Scope, reproducibility and remaining work

Fixtures are small synthetic Python consumers. Exact product snapshots were copied
under `.log-file-genius`, not installed as registered Git submodules. Installer choice
was `claude-code` for both hosts; Codex used shared AGENTS discovery. These are
post-install behavior trials, not agents performing real project adoption. Overflow
decisions include absent component directories, limiting realism. Native read-only
execution did not enforce filesystem secrecy; known cross-trial exposure was invalidated.

The [evaluator-only bundle](evidence/README.md) contains compressed traces, exact initial
synthetic fixtures, oracle snapshots, final maintenance artifacts, ledger, and
[SHA-256 hashes](evidence/SHA256.json). Authentication directories are excluded; a bounded
credential-pattern scan runs before trace export. Do not give this answer-bearing
bundle to trial participants.

Reproduction: [protocol](PROTOCOL.md), [oracle](ORACLE.md), [runner](evaluate.py),
[scheduler](batch.py), [collector](collect.py), [maintenance extraction](audit_maintenance.py),
[packager](package_evidence.py). Eight measurement/fixture regression checks pass.
[Terra code-owl review](REVIEW.md) records evaluator corrections and limitations.
Existing deterministic product/CI evidence remains in the
[execution record](../../specs/context-execution.md); these evaluator-only changes do
not constitute new product test results.

Fix startup/read-budget behavior and preservation of pending handoff facts before
rerunning affected suites. A targeted commit-capable Codex maintenance cohort can
measure its missing commit-effort result. Full semantic adjudication, noncritical
denominators, Claude injected-byte measurement, and untested host/platform claims
remain separate gates. Hermes, Grok Build, custom bots and OKF consumers were not
behaviorally tested; generated adapters do not establish support.

Three real-reader packages are ready: [reader 1](human/reader-01.zip),
[reader 2](human/reader-02.zip), [reader 3](human/reader-03.zip).
**0/3 readers have participated.** Give each person only their zip and follow the
[facilitator instructions](human/FACILITATOR.md); answer keys stay private until responses
lock. No human answers or timings were simulated. These external trials remain required.
