# Context-discovery evaluation — in progress

No release or compatibility acceptance. Candidate source is merged development
`c2d0dbb4791a41969249c932a3ae398108253106`; comparison source is `7dffd54` / v0.5.0.
All work is on isolated branch `codex/context-evaluation`; main and the original
checkout are untouched. Product runtime/dependencies are unchanged.

## Protocol and artifacts

- [Frozen evaluation contract](../../specs/WORKPLAN-context-discovery-and-portability.md)
- [Operational protocol](PROTOCOL.md), [semantic oracle](ORACLE.md)
- [Fixture builder/native runner](evaluate.py), [bounded scheduler](batch.py)
- [Evidence extractor](collect.py), [measurement checks](test_measurements.py)
- [Human facilitator instructions](human/FACILITATOR.md)

Original manifest: 13 critical fixtures. Candidate plan: three fresh sessions per
fixture on each available host, 78 behavior attempts total. Controls: one matched
trial for every fixture/host/condition, 52 attempts, compared against candidate
repetition 1 rather than treating all three repetitions as independent pairs.
Maintenance: five paired tasks per available host, 20 attempts. This bounded corpus
does not replace additional noncritical denominators or the real-reader gate.

## Hosts and measurement boundaries

macOS; Codex CLI 0.149.1 / gpt-5.5; Claude Code 2.1.269 / claude-opus-5.
Resolved models are retained per trial. Codex's configured gpt-6-astra was rejected
by this CLI; the failed diagnostic is retained and no astra compatibility is claimed.
An isolated Claude config lost keychain login, and an empty setting-source list
disabled native instructions. Both evaluator setup failures are retained. Corrected
Claude trials use authenticated configuration with project/local sources enabled.

Codex host rollouts expose the AGENTS instruction body and its actual user-message
envelope. The ordinary fresh candidate body is 233 estimated tokens; with host
formatting it is 269, exceeding the frozen 250 cap. These are ceil(characters/4),
not exact tokenizer counts. Tool-return envelopes, duplicate reads and failed
searches are counted separately. Provider usage is recorded separately as total
input/output usage, not mislabeled discovery tokens.

Claude's fresh diagnostic correctly described the imported project instructions
before tool use, then read the expected sources. This is behavioral corroboration;
its stream does not expose effective injected bytes. Exact native injection and
total discovery estimates remain unknown for Claude. No file-size or self-report
substitution closes that gate.

## Findings established while trials run

- Governing decisions are being found, but both hosts often inspect unrelated files
  and reread sources to obtain line-number citations. The eight-read cap is binding.
- A nested Codex session searched above its consumer root and exposed other trial
  paths. It is invalidated. Subsequent fixtures use a private parent directory.
  Native read-only mode does not enforce total filesystem secrecy; trace audit is
  required, and no claim of OS-enforced isolation is made.
- Initial harness defects were repaired before reporting metrics: invalid setup
  command, disabled Claude native sources, shell-read overcounting, missing native
  formatting overhead, missing failed-attempt ledger and an incomplete human task.
  Six evaluator checks pass. Unknown measurements never become passes.

## Human handoff — prepared, not performed

Three separately packaged, condition-labeled exercises are ready:
[reader 1](human/reader-01.zip), [reader 2](human/reader-02.zip),
[reader 3](human/reader-03.zip). Send each reader only their zip. Keep the
facilitator key and semantic oracle private until responses are locked.

Reader participation: **0 of 3**. Forms and timings are blank. Reader 3 has an
explicit timeout-retry task; its scoring key distinguishes retry work from the
separate amount-correction handoff. Order is counterbalanced, but the small sample
and learning effects prevent general-population claims.

## Remaining work

Finish the active native corpus, matched controls and paired maintenance; retain
every failed/invalid attempt and report category denominators. Audit source reads,
source application, forbidden actions and maintenance facts against the oracle.
Actual delegated-child execution and real human participation remain separate from
prepared briefs/packages. Hermes, Grok Build, custom bots and OKF consumers remain
behaviorally untested. No main promotion, release tag, or external publication.
