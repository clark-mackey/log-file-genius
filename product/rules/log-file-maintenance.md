---
fragment: log-file-maintenance
order: 10
targets: agents_md, claude_rules, augment_rules
summary: Always-active rules for log maintenance (commits, sessions, archival, formats).
---

# Log maintenance (on demand)

## Meaningful changes

Record behavior changes in configured CHANGELOG Unreleased. Record rationale,
rejected approaches and milestones in DEVLOG. A coherent change may span several
commits. Keep explicit stricter project policies. No automatic history amendment,
compulsory conversational checklists, or documentation-only follow-up commits.

## SESSION START

Read configured STATE and ADR README. Union global, path, and semantic task routes;
read all applicable active ADRs and follow replacements. Missing index or no match:
search the configured source directory, then report unresolved scope.
Compare baseline branch/code commit with Git. Reconcile Current Context and Last
Session contradictions; missing evidence remains unknown. Dates alone prove nothing.

## SESSION END

At a meaningful handoff, record baseline branch/code commit (before the handoff
commit), next action, tests/outcomes and blockers in STATE. Keep it under 500 estimated
tokens. Read-only questions require no rewrite. Keep session/worktree-specific scratch
separate; preserve another task's ownership and facts.

## ENTRY VERBOSITY AND FORMATS

- CHANGELOG: `- Behavior change and why. Files: path. Evidence: test/result.`
- DEVLOG: `### YYYY-MM-DD: Title`, situation, decision, result and evidence.
- INCIDENT: use the incident template; include trigger, failed approach, conditions,
  resolution, prevention and when to reconsider. Link the incident index.
- ADR: copy the decision template, fill Routing and Status, regenerate routes.

## CROSS-REFERENCES AND ARCHIVAL

Link enduring lessons into ADRs/incidents before chronological log archival. Preserve
source evidence and explicit supersession. Preview archive plans; refusal means inspect
and migrate unsupported sections with a backup. Never silently truncate constraints.
Use configured token targets: STATE 500, CHANGELOG 10000, DEVLOG 15000 by default.

## DELEGATED RECORD MAINTENANCE

When project records need updating, prefer a subagent using the harness's configured
lower-cost model, provided it can handle the task. Respect permitted providers and
project policies. Do not guess model prices, invent model names or switch providers
without authorization. If delegation or model selection is unavailable, no suitable
lower-cost worker is configured, or delegation costs more than direct execution,
perform the work directly. This policy concerns project records, not LFG software upgrades.

Give the worker the relevant changes, decisions and rationale, test results,
unresolved issues, source paths, applicable instructions and existing records.
Provide sufficient context and output budget to preserve substantive detail. Existing
record formats and token targets still apply; preserve detail in linked records when
needed rather than silently dropping facts to fit a budget.

The worker stages drafts under the subagent contract below. Preserve required formats,
OKF metadata, evidence, uncertainty, constraints and history. Do not invent missing
facts or omit important information to reduce cost. Return unresolved questions to
the lead; do not delegate recursively. The lead retains responsibility for decisions
and their rationale, especially ADRs and incident analysis.

The lead checks the draft against supplied evidence and existing records, resolves
omissions or contradictions, runs applicable validation and promotes accepted changes.
If the worker cannot meet these requirements, the lead completes the update. A cheaper
model never lowers the acceptance criteria. Do not log delegation itself as a project
milestone or create updates for otherwise read-only work.

## SUBAGENT CONTRACT

`LFG_SUBAGENT_PRIME` identifies a subagent. Subagents write staging entries under
`.lfg/staged/<id>/`, not canonical STATE/CHANGELOG/DEVLOG. Return consulted ADR IDs,
tests/outcomes and unresolved scope. The lead reviews evidence and promotes accepted
entries with the repository-local CLI. A neutral reader packet assigns no subagent role.

## TEMPLATES AND SUCCESS CRITERIA

Use product/templates as examples, resolve configured paths, and validate meaningful
changes. Completion means facts/evidence recorded, governing decisions applied, and
missing or unread scope reported. See [context guide](../docs/context-guide.md).
