---
type: Work Plan
doc: WORKPLAN
title: Reliable, Efficient Project Context Across Agents
description: Build order for LFG reliability, ADR discovery, routing, portable startup, freshness, and OKF compatibility.
status: stable
related:
  prd: ./prd.md
  workflow: ../WORKFLOW.md
  state: ../../logs/STATE.md
  decisions: ../../logs/adr/README.md
---

# Workplan: Reliable, Efficient Project Context Across Agents

Date: 2026-09-12
Status: Implementation authorized by the user on 2026-09-12. See [execution evidence](context-execution.md); release gates remain separate.
Baseline: v0.5.0; `main` at `0d622e8`, `development` at `b37826c`. Product content matched across those refs when inspected.

## 1. Outcome and scope

A fresh agent or human should find the current project state, identify the decisions that govern a task, verify whether the context applies to the current checkout, and take the correct next action with little reading.

Preserve LFG's Markdown, Git, and low-dependency approach. Reuse STATE, CHANGELOG, DEVLOG, ADRs, incident reports, their indexes, the rule generator, and existing CLI commands. Python standard-library tooling remains sufficient for the initial producer and navigation features. No model API, vector database, background service, or mandatory plugin is needed.

This plan combines:

- Repairs for the three open reliability issues.
- A compact reading protocol and task-to-context routing, modeled on code-owl's explicit applicability table.
- Reliable discovery of existing ADRs, including by subagents.
- Smaller startup instructions and less repetitive documentation maintenance.
- Additive OKF metadata and a bounded, conformant knowledge bundle.
- Branch-aware handoffs, evidence-based freshness, and useful archival retrieval.
- Safe migration, platform compatibility checks, and outcome-based evaluation.

## 2. Evidence behind the plan

| Observed behavior | Consequence |
|---|---|
| Generated AGENTS navigation lists STATE, CHANGELOG, and DEVLOG but omits the ADR index. | A reader can follow startup instructions and miss architectural constraints. |
| Installers create the ADR directory and template but do not seed its README index; log templates link there. | A fresh installation can contain an incomplete navigation path. |
| `test_cold_read.py` is handed AGENTS.md and checks only its declared destinations. | It does not establish native discovery or task-to-ADR retrieval. |
| Generated LFG AGENTS content measured approximately 4,093 tokens using characters/4. | Maintenance instructions consume substantial context before project knowledge. |
| Claude-specific installation creates `.claude/project_instructions.md`, alongside rule files. | That filename alone does not establish automatic loading in Claude Code. |
| `lfg prime` includes STATE and N Unreleased bullets, with a subagent identity marker. | Relevant ADRs, incidents, and rationale require explicit lead selection elsewhere. |
| Development STATE describes PR #12 as released while Last Session says it awaits merge. | A recent timestamp alone cannot establish internal consistency. |
| Templates generally have `doc` and `related`, but no OKF `type`; several examples have no frontmatter. | Compatibility requires additive metadata and a defined bundle boundary. |

These are inspection findings, not results from running a new cross-agent benchmark. Reconfirm implementation details before editing, especially after upstream changes.

## 3. Design boundaries

1. **One canonical context collection.** Adapters point to shared content. Avoid independently maintained copies of decisions or procedures.
2. **Explicit routing.** Match the task and affected paths against all applicable rows. Each row identifies a destination and the fact or constraint to establish. A miss triggers bounded index/directory search; it does not prove no decision exists.
3. **Deterministic assembly, reader judgment.** The human or lead agent selects relevant records. Tooling validates destinations and assembles excerpts; it does not invent semantic relevance or summarize decisions through a model API.
4. **Preserve existing ownership and authority.** Merge managed blocks, retain project-owned instructions and historical records, and distinguish accepted decisions from proposals or superseded decisions. Repository context informs work; it does not grant permission for external or destructive actions.
5. **Truth before apparent freshness.** A changed date is not verification. Missing evidence stays unknown. A branch mismatch requires reconciliation, not automatic replacement with another branch's state.
6. **No silent budget omissions.** Reduce scope or route through a smaller index when needed. Never silently truncate a governing constraint or claim a partial packet is complete.
7. **Separate representation from discovery.** OKF conformance does not prove that a host loads LFG. Platform support needs both a working entry point and task-level evidence.

## 4. Build sequence

Core dependencies: Phase 0 → 1 → 2A → 3 → 4 → 5 → 6 → 7. Phase 2B is a separate OKF compatibility track that starts after 2A; it does not block core ADR discovery or the first context-improvement release. An OKF index joins the results of 2B and 3. Optional OKF lifecycle features in Phase 5 require 2B; ordinary handoff checks do not.

Phase 8 supplies the release gate for each checkpoint's shipped scope, rather than postponing migration tests and documentation until every feature exists. Capture evaluation fixtures in Phase 0 and reuse them throughout. These are work dependencies, not instructions to run multiple agents.

### Phase 0 — Freeze the contract and capture the baseline

Purpose: Establish measurable success and identify prior decisions affected by this proposal.

- Read the current PRD, two-branch workflow, agent-agnostic design, archival design, and applicable ADRs on `development`.
- Resolve conflicts with earlier decisions about always-loaded fragments, every-commit logging, and narrow priming. Record each affected decision, dependent phase, disposition (accepted revision, rejected change, or bounded experiment), and the authority/evidence supporting that disposition. An experiment records scope, owner, success criteria, and rollback; it does not silently supersede an accepted ADR. Preserve the previous rejection of fuzzy topic filtering and a broad convenience CLI unless separately reconsidered.
- Define a common reading protocol: discover LFG → inspect current state → match task/path routes → read applicable active decisions → reconcile missing or conflicting evidence → proceed.
- Freeze the routing source and schema specified in Phase 2A before its producers or views are implemented. Document the Phase 4 minimum freshness contract: baseline branch/commit, comparison with available checkout evidence, contradiction detection, and explicit unknown status when evidence is missing.
- Create a versioned fixture manifest under the existing test tree using the schema and thresholds in Section 5. Include new installation, brownfield instructions, custom paths, nested working directory, existing override file, unknown task, superseded ADR, missing index, archived lesson, changed branch, delegated task, cross-component matches, and budget overflow.
- Measure current injected instructions, files read, estimated context cost, and known retrieval failures. Separate baseline observations from aspirational targets.

Exit: Protocol, routing schema, compatibility assumptions, fixture oracles/thresholds, and measurements are recorded. Each governing conflict is resolved for the next dependent phase; unresolved decisions block that phase, not unrelated work. Tests distinguish file existence, native loading, retrieval, and actual application of a decision. No new implementation is authorized merely by recording this plan.

### Phase 1 — Repair the existing workflow

Purpose: Make the commands advertised by LFG usable and trustworthy before adding navigation.

- **Issue #13:** Generate an explicit repo-local command invocation, or an explicit-path wrapper; resolve it from generated guidance alone. Support platform differences without requiring aliases or global installation. Explain recovery when the runtime is absent or the submodule is uninitialized.
- **Issue #14:** Align validator and archiver structural expectations. Check actual size independently of whether an archive plan contains actions. Refuse oversized unparsed content with actionable, preservation-safe migration guidance.
- **Issue #15:** Ensure read-only CLI usage leaves a clean consumer submodule clean. Suppress bytecode or provide appropriate distribution ignores, then exercise the installed workflow.
- Reuse existing CLI dispatch, config parsing, archive planning, and install/update test infrastructure.
- Run minimal smoke tests now on macOS/Linux Bash and Windows PowerShell: fresh install without a global executable, generated repo-local invocations from a path containing spaces, validation/refusal exit status, and submodule cleanliness. Exercise missing runtime, an uninitialized submodule, and existing project-owned instructions. Phase 8 expands this matrix; it is not the first platform check.

Exit: Fresh installation without global `lfg` can follow every advertised command on both shell families; malformed archival input cannot produce false success; refusal preserves bytes; normal reads leave the dependency clean. Required platform smoke tests pass before dependent phases start. Preserve all existing brownfield merge protections.

### Phase 2A — Establish the canonical routing record

Purpose: Supply the small data contract needed by ADR discovery, independently of OKF adoption.

- Each ADR owns its route in a compact `## Routing` body section: `Read when` (task-language triggers), `Applies to` (repository-relative path globs, or an explicit project-wide marker), and `Constraint` (one sentence directing the reader to the full decision). All three are required for an active generated route.
- Derive the decision ID and title from the existing ADR heading, and decision status from its existing Status field. A superseded ADR names its successor in a `Superseded by` Markdown link. Do not duplicate status or successor ownership in an index or in OKF lifecycle fields.
- The full ADR remains authoritative; the route is its navigation summary. Changes to scope, decision, status, or successor require checking the route in the same change. Missing/conflicting fields or a supersession cycle produce an unresolved-record report, not a guessed active route.
- Keep curated README prose outside a managed generated region. Existing README-only routes can be migrated into their owning ADRs with a preservation-checked preview; leave ambiguous mappings for review and report incomplete coverage.
- Define deterministic generation: stable ordering by decision ID/path, explicit source links, and no machine-invented constraints. Incidents and requirements remain linked from the general task table; their schemas are not expanded by this ADR contract.

Exit: Fixtures reproduce every generated ADR view from its owning records. Editing an ADR's routing section, status, or successor updates the view; stale generated output is detected. Legacy records without routes remain discoverable through a visibly incomplete index and directory fallback.

### Phase 2B — Establish optional OKF metadata and migration boundaries

Purpose: Make the selected knowledge bundle conformant without making OKF a prerequisite for core routing or requiring new runtime dependencies.

- Choose `logs/` as the initial consumer knowledge-bundle boundary, resolving its actual location through configuration. Projects with scattered custom paths need an explicit compatible root or a documented partial-conformance result; do not silently relocate their files.
- Add descriptive `type` values to concept documents. Retain `doc` and `related`; current recognition and tests depend on them.
- Add a short title and description where they improve routing/index generation. Use explicit, safely quoted YAML scalars for generated values.
- Update templates, generated document headers, seeded indexes, and bundled examples. Inventory every Markdown file inside the chosen bundle, including templates, archives, and README files.
- Reserve `index.md` and `log.md` for OKF's specified structures. Existing README indexes can remain; generate optional OKF navigation once both this track and Phase 3 are complete, using the same canonical records.
- Keep ADR decision status separate from OKF lifecycle status. Do not stamp historical records as verified or accepted during conversion.
- Define a constrained, valid YAML output profile for LFG. Do not advertise the existing config-subset parser as a general OKF/YAML consumer. Full YAML verification may be a development-only check; unsupported existing frontmatter must be preserved and reported.
- Specify a dry-run, idempotent migration: add missing metadata, preserve bodies and custom keys, detect ambiguous/conflicting metadata, and produce a clear report. Scope it to selected knowledge files.
- For migration and managed-view replacement, validate the complete proposed content before mutation; preserve the original bytes in a recoverable backup before replacing an existing file. Write through a temporary file in the same directory and atomically replace the destination. Check the original still matches the inspected version before replacement; a concurrent edit causes refusal.
- Guarantee per-file, not whole-bundle, atomicity: parse, validation, backup, temporary-write, or replacement failure leaves that destination unchanged. An interrupted multi-file run may leave complete replacements alongside untouched files; preserve a recovery record and backups so the operator can restore or resume safely. Never label a partial run complete or regenerate final indexes against an unreported partial migration.
- Add failure-injection fixtures before replacement, during a temporary write, and between files, plus concurrent-edit and backup-failure cases. Assert unchanged destination bytes before a successful replacement, recoverable originals afterward, and a clean resume/second-run result. Apply these write guarantees to Phase 2A route migration and Phase 3 generated views as well; they are shared safety requirements, not an OKF dependency.
- Refresh template manifests/checksums through existing tooling while retaining historical hashes needed for safe identification.

Exit: LFG-produced documents in the declared bundle satisfy minimal OKF v0.2 conformance. Migration fixtures preserve bodies, custom metadata, and links; interruption and write failures satisfy the stated per-file guarantees; originals remain recoverable; a second completed run makes no changes. Any incomplete conversion is explicitly reported. Failure of this track prevents an OKF-conformance claim, not a core discovery release.

### Phase 3 — Make ADRs discoverable through explicit routing

Purpose: Give the reader an inexpensive path from a task to its governing decisions.

- Seed an empty ADR README index on new installs, preserving existing indexes. Validate direct ADR links from startup guidance and log headers.
- Reuse `logs/adr/README.md` as the human-readable decision directory. Add compact routing rows: **read when / affected area → decision link and essential constraint → decision status**.
- Include both task-language triggers and file/directory scope. A task can match multiple rows. Keep a few project-wide constraints visible independently of component matching.
- Generate managed route rows exclusively from the Phase 2A ADR records. Preserve curated prose outside managed regions and detect a stale view before declaring coverage complete.
- Keep an always-consulted top-level manifest in the ADR README: project-wide routes plus each partition's task triggers, path scope, and destination. Derive these rows from canonical records. Partition large collections by component; the manifest must expose every partition and may not silently omit rows to meet a budget.
- Union project-wide routes, all matching path scopes, and every task-language match selected by the reader before loading decisions; deduplicate by decision ID/resolved source path. Path matching is deterministic; semantic task matching remains reader judgment and is exercised against fixture oracles. An unknown task uses the documented fallback instead of treating the first partition as sufficient.
- If the manifest, candidate indexes, or required decisions cannot fit, return an explicit incomplete/overflow result with the known unread destinations and any unchecked scope. No budget-limited result may claim complete coverage. Narrow the task or read in reported batches before planning a dependent change.
- Add optional OKF `index.md` views only after Phase 2B, following its reserved-index structure and using the same records. The ordinary README routing path must work without these views.
- Cover incidents and requirements through the general task-routing table. Reuse existing incident-index machinery where its behavior fits, without forcing all document types into one schema.
- Provide a fallback for absent or unmatched routes: inspect the configured ADR directory, search a small set of task/path terms, follow supersession links, and surface unresolved gaps.

Exit: Fixtures find the applicable ADR without its name being supplied; all matching decisions are consulted; superseded decisions lead to replacements; missing indexes have a usable fallback. A cross-component fixture finds its project-wide and both component decisions; an overflow fixture reports incomplete coverage without silently dropping candidates. No template or empty-state placeholder is presented as an accepted project decision.

### Phase 4 — Shrink startup guidance and connect supported hosts

Purpose: Deliver the shared reading protocol reliably at low context cost.

- Replace the long always-loaded LFG body with a small managed startup block and compact routing pointers. Move detailed maintenance instructions, examples, and manual-command procedures to ordinary on-demand files.
- Generate actual configured destinations, including the ADR index, instead of contradictory hardcoded defaults. Keep only genuinely critical rules in the startup block.
- Ship minimum freshness with discovery: STATE handoffs record the branch and code/evidence commit last checked; startup compares them with the available checkout and flags contradictory Current Context/Last Session statements. Missing, mismatched, or conflicting evidence stays explicitly unresolved until checked; do not present a release or completion claim as current merely because it was found in STATE.
- Define the baseline commit as the commit checked before the handoff update, not the commit containing that update. Apply these checks without automatically rewriting STATE for read-only questions. Phase 5 adds richer ownership and evidence handling; it does not supply the first protection against stale guidance.
- Support native entry points with small adapters: Codex AGENTS.md; Claude CLAUDE.md import or supported rule; Hermes's effective project-context file; Grok Build's trusted project rules. Inspect overrides and duplicate loading before claiming an integration works.
- Preserve and test the existing Augment integration with the same compact protocol. Document Aider's explicit read/configuration path as an opt-in integration rather than assuming native automatic loading.
- Move obsolete LFG-owned always-loaded copies out of automatic discovery only when ownership is established. Preserve user modifications and unrelated rules.
- Add a short managed README pointer for humans and agents browsing a consumer repository. Make it useful without requiring knowledge of the LFG brand or CLI.
- Describe a generic host integration: inject the small reading protocol and provide file/document retrieval. A custom Grok bot or OKF consumer is not assumed to share Grok Build's loader.
- Revise logging rules to capture meaningful changes, decisions, failed approaches, and handoffs. Remove mandatory conversational checklists and automatic commit-amend instructions from the default context. Respect a project's stricter policy where explicitly chosen.
- An optional personal LFG skill/global instruction may aid discovery, but is not required for installed repositories to function.

Exit: Each tested host reaches the same routing content from its documented entry point, including nested launches and existing instructions. Startup contains no unresolved commands or duplicated full rule sets. Changed-branch, missing-baseline, and contradictory-handoff critical fixtures pass before Checkpoint B is releasable. The README fallback works for a human cold read.

### Phase 5 — Extend handoff evidence and ownership

Purpose: Extend the Phase 4 minimum freshness contract with detailed evidence and session ownership.

- Keep shared project facts distinct from session-specific work. Record the branch and commit against which the handoff was checked, next action, relevant verification result, and unresolved blockers.
- Preserve Phase 4's code/evidence-baseline semantics; do not introduce a self-referential commit field.
- At startup compare the recorded baseline with the current checkout, including relevant working-tree changes. A commit difference is a signal to inspect, not automatic proof every statement is stale.
- Reconcile contradictory Current Context and Last Session statements. Separate local Git observations from external release/issue state and record the evidence source when external status is checked.
- Keep the time-based staleness check as a secondary warning. Do not rewrite state for a read-only question or merely to refresh its timestamp.
- When Phase 2B is included, define when optional OKF generation, verification, and lifecycle metadata is maintained. Verification records an actual check; it is not created as a side effect of formatting or installation. Ordinary handoff evidence remains usable without OKF metadata.
- For parallel branches/worktrees, document session ownership and preserve unrelated handoffs. Do not describe STATE as a lock, scheduler, or guarantee against concurrent collisions.

Exit: Changed-branch, dirty-tree, divergent-history, stale-timestamp, and contradictory-handoff fixtures produce accurate distinctions between verified, historical, and unknown context. Unrelated work is never silently overwritten.

### Phase 6 — Carry selected context into delegation and task transitions

Purpose: Preserve relevant decisions across agent boundaries without making every reader restart discovery.

- Extend the existing priming foundation with explicit selections of files, sections, ADRs, and incidents; settle the smallest CLI surface during implementation design.
- Preserve `LFG_SUBAGENT_PRIME` and current staged-write semantics for subagent dispatch. Keep neutral human/lead briefings separate from the identity-setting subagent output.
- Include task objective, selected constraints, provenance links, handoff baseline, and missing-context notices. Existing documents remain authoritative.
- Budget the complete assembled packet. If it cannot fit, report the conflict and ask the caller to narrow scope; do not silently drop a required decision.
- Reroute when work expands into another component or design area. Reuse already loaded, unchanged documents within the session.
- Subagent completion identifies relevant decision IDs and unresolved gaps concisely. The lead verifies proposed log entries before promotion.

Exit: A fresh subagent receives and applies the same governing decisions as its lead, without reading full histories or accidentally assuming lead write authority. An unrelated task receives no irrelevant ADR payload.

### Phase 7 — Preserve durable lessons through archival

Purpose: Keep useful knowledge retrievable after chronological entries move out of the working set.

- Use ADR and incident records for durable decisions and lessons; keep concise discovery rows in their indexes. Avoid a new duplicative lessons database.
- Record conditions behind a failed approach and when it should be reconsidered. Historical failure must not become an unconditional prohibition.
- Maintain explicit supersession relationships and distinguish active constraints from historical rationale.
- Keep archival chronological and deterministic. Review extraction of durable lessons during normal maintenance; do not require an LLM-powered archival step or silently add new retention heuristics.
- Preserve or repair discovery links after archival. Surface any loss of reachability as a validation issue.

Exit: After archive operations, fixtures still recover a governing old decision and a relevant prior failure. Original content remains recoverable, links remain useful, and obsolete decisions do not override current ones.

### Phase 8 — Migrate, evaluate, document, and release

Purpose: Gate each checkpoint release for its implemented scope, then prove the combined workflow once all selected tracks are ready.

- Exercise install → discover → plan → handoff → resume → archive → update in isolated consumer repositories on Bash and PowerShell.
- Cover old LFG versions, uninitialized runtime, missing indexes, malformed metadata, custom paths, modified templates, existing native instructions, nested roots, and repeated migration/update runs.
- Dogfood on `development`. Correct stale project navigation and conflicting state, including development-only guides that still point to obsolete context/ADR locations.
- Compare ordinary repository docs, current LFG, and the new routing approach on the same tasks. Include a human handoff exercise. Report native-loader checks separately from model behavior trials.
- Publish measured outcomes and limits. Replace claims of complete context, zero context loss, guaranteed collision prevention, or universal loading with supported statements.
- Document minimum adoption, default reading flow, how to add a route/ADR, migration and recovery, optional OKF features, and tested host/version support. Keep detailed maintenance instructions out of startup context.
- Implement on branches based on `development`; merge through the development workflow. Promote only distributable changes to `main` using the established release process. Never merge the full development tree into `main`.

Exit: Required regression checks and the Section 5 per-category thresholds pass for every claimed host/platform and shipped feature; token-cost and compatibility reports exist; migration is repeatable; release docs describe actual supported behavior. Untested hosts are marked untested, not supported by inference. Optional-track failures restrict that track's claims and release scope; they do not silently waive the core safety gates.

## 5. Budget and evaluation contract

Initial engineering targets, to validate rather than advertise as measured outcomes:

| Material | Target |
|---|---|
| Effective LFG startup guidance, including adapter overlap | 150–250 estimated tokens |
| STATE | At most 500 estimated tokens |
| Routing/index material required for the task, including top-level manifest | 300–500 estimated tokens |
| Full ADRs, incidents, requirements, procedures | On demand; count in the task's total context cost |

The initial orientation target is approximately 950–1,250 tokens before selected source documents. If essential context exceeds it, report that fact and revise the route or target explicitly. Do not remove essential knowledge to pass a token assertion.

Measure actual injected content and read-tool output when the host exposes them; use clearly labeled characters/4 estimates otherwise. Include repeated reads, imported duplicates, formatting overhead, and unsuccessful searches. File size alone is not the metric.

| Evaluation | Passing evidence |
|---|---|
| Native discovery | Effective host instructions contain the intended LFG entry point. |
| ADR retrieval | Agent finds the governing ADR before proposing a conflicting plan. |
| Decision application | Proposed action preserves the ADR's relevant constraint. |
| Freshness | Agent distinguishes the current checkout from stale or unrelated handoff evidence. |
| Archived lesson | Agent retrieves the prior failure and its applicability conditions. |
| Delegation | Subagent preserves relevant constraints with a bounded briefing. |
| Maintenance burden | Less repeated narration/document churn without losing useful handoff facts. |
| Human usability | Reader can explain the next action and find its rationale without CLI expertise. |

### Fixture oracle and release thresholds

Phase 0 commits a small versioned fixture manifest alongside the existing tests. Each fixture records: fixture/schema version; repository snapshot and working-tree state; host/platform assumptions; task prompt; expected route partitions, source files, and decision IDs; acceptable alternate evidence; required/forbidden actions; critical/noncritical category; maximum discovery reads and tokens; and a scoring method. Expected answers are authored independently of generated routing output. Freeze numerical read/token caps before candidate runs; any revision must be explained and applied to both baseline and candidate.

Required categories are native loading, basic ADR retrieval/application, project-wide plus cross-component matching, unknown-task fallback, supersession, missing index, overflow, freshness, preservation/recovery, delegation, and archived lessons. A category is gated when its feature is shipped; critical discovery, freshness, and preservation categories cannot be postponed beyond Checkpoint B.

- **Deterministic checks:** 100% of applicable schema/link/generation, command invocation, preservation, interruption, and platform smoke fixtures pass. An unsupported platform is excluded from claims, not counted as passing.
- **Critical behavior trials:** Run every applicable safety fixture three times from clean sessions for each claimed host/model combination. All trials must preserve governing constraints, surface incomplete/conflicting evidence, and avoid forbidden actions. One critical failure blocks that compatibility claim until fixed and the affected suite is rerun.
- **Noncritical retrieval and continuity:** At least 90% of trials in each category pass, with three trials per fixture and at least ten trials per category; round the required success count upward. A pass requires the oracle's expected sources/actions and its read/token caps. Report category denominators, every failure, and any human adjudication; aggregate scores cannot hide a failing category.
- **Efficiency and maintenance:** On the same scored task corpus, median discovery tokens must be below the current-LFG baseline and within each fixture's frozen limits; critical correctness must not regress. Use at least five paired maintenance tasks: median logging actions and documentation-only follow-up commits must not exceed baseline, with zero omitted required handoff facts. Record narration tokens separately rather than treating short prose as proof of lower maintenance cost.
- **Human handoff:** Use at least three blinded task/reader trials scored against expected next action, governing decision, and evidence source. All three must find the required rationale without CLI assistance; record reading time without claiming general population performance.

Run deterministic checks in ordinary CI. Keep live model trials explicit and bounded; report host, model, version, trial count, and failures. Passing fixtures is not a guarantee of all future agent behavior.

## 6. Likely implementation surfaces

| Area | Existing surfaces to inspect and reuse |
|---|---|
| Native guidance and command resolution | `product/scripts/generator.py`, `agents_merge.py`, `lfg.py`, `product/rules/`, Claude install template |
| Installation and migration | `install.sh`, `install.ps1`, `update.sh`, `update.ps1`, existing merge/migration helpers and template manifests |
| Context records and indexes | `product/templates/`, `product/examples/`, `product/scripts/incidents.py`, configured consumer ADR/incident indexes |
| Validation and archival | `lint-logs.py`, shell/PowerShell validators, `archive.py`, `migrate_state.py` |
| Briefing and staged writes | `primer.py`, `promoter.py`, existing CLI dispatch |
| Regression infrastructure | `test_cold_read.py`, `test_frontmatter_sync.py`, `test_generator*.py`, `test_primer.py`, archive/config/merge tests, install/update smoke tests |
| User-facing guidance | Root README and INSTALL, product methodology and validation docs; development-only PRD/workflow/navigation |

Inspect callers and reuse helpers before editing. Do not introduce a general YAML parser, a new routing engine, or an additional config file merely because metadata is being added.

## 7. Delivery checkpoints and deferred scope

- **Checkpoint A:** Phases 0–1 — reliable existing workflow and captured baseline.
- **Checkpoint B:** Phases 2A, 3, and 4 plus the scoped Phase 8 gate — direct ADR routing, compact tested discovery, and minimum freshness. This is the first substantial context-improvement release candidate; it cannot ship without critical freshness/preservation checks, but does not wait for Phase 2B.
- **Checkpoint C:** Phases 5–7 plus the scoped Phase 8 gate — richer continuity, selected delegated context, and durable lesson retrieval.
- **Optional OKF checkpoint:** Phase 2B and the Phase 3 OKF view, plus their scoped Phase 8 migration/conformance checks. It may accompany B or C, or ship separately. Claim conformance only for its validated bundle boundary.
- **Checkpoint D:** Phase 8 applied to the combined selected scope — integrated migration, measured outcomes, and distribution release.

Remain deferred: embeddings, model-based relevance ranking, hosted memory, mandatory SDKs/plugins, autonomous verification claims, a multi-agent locking service, broad human-convenience CLI expansion, and full general-purpose OKF ingestion. Optional global skills and additional host adapters follow demonstrated need.

## 8. Sources and compatibility references

- [PRD](./prd.md), [development workflow](../WORKFLOW.md), [ADR index](../../logs/adr/README.md).
- [Spec 2: agent-agnostic core](../../docs/superpowers/specs/2026-05-28-spec2-agent-agnostic-core-design.md), [Spec 3: archival](../../docs/superpowers/specs/2026-05-28-spec3-graceful-archival-design.md), [Spec 4: safe installation](./SPEC-04-brownfield-safe-install-update.md).
- [Issue #13: unresolved local commands](https://github.com/clark-mackey/log-file-genius/issues/13), [#14: false archival success](https://github.com/clark-mackey/log-file-genius/issues/14), [#15: bytecode dirties submodule](https://github.com/clark-mackey/log-file-genius/issues/15).
- Routing precedent: code-owl v1.5.1, Context Routing section, inspected in the author's skills-workbench. The transferable behavior is explicit triggers, all matched references, a fallback, and a completion check; consumers do not need that skill installed.
- [OKF v0.2 specification](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md). Minimal conformance, reserved indexes, and optional lifecycle/verification metadata are separate implementation concerns.
- [Codex instruction discovery](https://learn.chatgpt.com/docs/agent-configuration/agents-md), [Claude project memory](https://code.claude.com/docs/en/memory), [Hermes context files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files), [Grok Build project rules](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/12-project-rules.md), [Augment rules](https://docs.augmentcode.com/cli/rules), [Aider conventions](https://aider.chat/docs/usage/conventions.html).

Platform documentation was checked during the 2026-09-12 assessment. Recheck loading, precedence, and import behavior when implementing each adapter; documentation support alone is not a completed integration test.
