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
Compare STATE's `**Baseline branch:**`/`**Baseline commit:**` with Git. Reconcile
Current Context and Last Session contradictions; missing evidence remains unknown.
Dates alone prove nothing.

## SESSION END

At a meaningful handoff, record the baseline branch and code commit (before the
handoff commit) under the exact labels `**Baseline branch:**` and
`**Baseline commit:**`, plus next action, tests/outcomes and blockers in STATE.
Keep it under 500 estimated tokens. Read-only questions require no rewrite.
Keep session/worktree-specific scratch separate; preserve another task's ownership
and facts.
Compare the old and new handoff before saving. Carry forward unresolved tasks and
blockers and pending verification until resolved with evidence or explicitly cancelled,
including work outside this session's task. Add new incident work without replacing pending fixes. Associate
tests with the task they verify; shorten wording rather than dropping open work.

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

## SUBAGENT CONTRACT

`LFG_SUBAGENT_PRIME` identifies a subagent. Subagents write staging entries under
`.lfg/staged/<id>/`, not canonical STATE/CHANGELOG/DEVLOG. Return consulted ADR IDs,
tests/outcomes and unresolved scope. The lead reviews evidence and promotes accepted
entries with the repository-local CLI. A neutral reader packet assigns no subagent role.

## TEMPLATES AND SUCCESS CRITERIA

Use product/templates as examples, resolve configured paths, and validate meaningful
changes. Completion means facts/evidence recorded, governing decisions applied, and
missing or unread scope reported. See [context guide](../docs/context-guide.md).
