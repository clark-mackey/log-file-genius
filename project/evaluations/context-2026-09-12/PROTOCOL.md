# Live context evaluation — frozen extension, 2026-09-12

Candidate: c2d0dbb4791a41969249c932a3ae398108253106. Baseline: 7dffd54
(v0.5.0). Ordinary-docs control uses the same task facts and source bodies, with
README navigation and no LFG/native adapter. No release authorization.

The original manifest has category descriptions, not executable task prompts or
complete semantic answer keys. This extension concretizes those descriptions
before live trials. It does not change its limits or success thresholds. All 13
original fixtures default to critical. Noncritical continuity categories need
separate denominators of at least ten; critical trials are not relabeled to fill them.

Consumer fixtures live outside this checkout and contain no evaluator report,
oracle, transcript, previous conversation, or expected-answer file. Each invocation
is a new CLI process/session and a new copy of a seeded consumer Git repository.
Use native discovery; never inject AGENTS/CLAUDE/ADR contents in the user prompt.
Preserve ordinary native host behavior, recording any unavoidable global context.
Use available local models, record resolved names, and do not pool different models.
Initial native probes established that Codex 0.149.1 rejects the configured gpt-6-astra.
Before scored trials, the Codex population was explicitly narrowed to locally advertised
gpt-5.5; Claude retains its resolved default claude-opus-5. Failed probes remain recorded.
Initial native probes are diagnostic and do not count toward behavior denominators.
Claude needs project/local setting sources for native loading; an empty source list
disabled that loading in a diagnostic probe and is not used for scored trials.
Native read-only mode does not hide the whole host filesystem. Trace contamination
audit is mandatory; cross-trial/evaluator reads invalidate a trial. A private parent
directory was added after an initial nested probe searched above its repository.
The initial delegated prompt said "new implementer", which did not identify a subagent.
Those six candidate trials remain diagnostic/invalid for the delegation role gate.
Role-explicit repetitions 4–6 say "new subagent implementer" and precede fresh child
sessions. They add no discovery path, decision name or answer-key constraint.

Score each critical fixture three times per available host/model. Record all
attempts, including timeouts, permission refusals and infrastructure errors. These
are not passes. Stop a host after a repeated infrastructure failure; do not spend
the remaining corpus on a broken host. A behavioral failure does not erase later
evidence. Keep each invocation bounded to 180 seconds (maintenance: 240).

Tasks concern a small receipt application. The global decision preserves integer
minor-unit amounts; a retry decision preserves the same idempotency key; a UI
decision preserves the failed attempt until acknowledgement. Archived rationale
describes a duplicate receipt caused by discarding the original identifier.
Supersession replaces a regenerate-key policy with the same-key policy. Branch
fixtures contain a stale verification claim contradicted by the checkout.
Oracle source IDs and paths remain exclusively evaluator-side.

Limits remain startup 250, STATE 500, routing 500, discovery reads 8, selected
packet 2000 estimated tokens. Use ceil(characters/4), counting repeated outputs,
failed searches and native duplicate injections when observable. A combined tool
call does not make multiple source reads one read. Exact native bytes not exposed
by a host remain unknown; model self-report and files on disk are not injection
proof. Provider total input/output usage is separate from discovery estimates.
Unknown measurements cannot satisfy a gated metric.

Five independent paired maintenance tasks cover meaningful code change, read-only
question, failed verification, branch reconciliation and durable lesson handoff.
Compare logging write actions and documentation-only follow-up commits, missing
required facts, and narration separately. No fabricated commits or human actions.

Three human exercises use opaque package labels, counterbalanced condition order,
an evaluator-only key, a reader prompt with no ADR/path hints, and blank response
forms. Actual readers and timing are required; preparation is not completion.
