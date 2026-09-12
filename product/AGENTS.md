---
doc: AGENTS
type: Agent Instructions
related:
  state: logs/STATE.md
  adr_index: logs/adr/README.md
---

# LFG context

Read STATE/index and all active global/path/task ADR matches; follow replacements. Missing/stale index or miss: search ADRs. Report unread scope.

8 source reads, repeats count. Reuse sources/citations; report gaps at limit.
STATE baseline = last checked code commit/branch. Reconcile Git and Current Context/Last Session; missing evidence is unknown.
Keep pending tasks/tests/blockers until resolved with evidence or explicit cancellation. Log changes/handoffs; no read-only rewrite. Subagents stage; lead promotes. Follow project instructions.

Procedures: `.log-file-genius/product/docs/context-guide.md`.
