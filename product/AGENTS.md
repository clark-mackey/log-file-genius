---
doc: AGENTS
type: Agent Instructions
related:
  state: logs/STATE.md
  adr_index: logs/adr/README.md
---

# LFG context

Read STATE/index. Union global/path/task matches; read active ADRs, follow replacements. Missing/stale index or no match: search ADR sources. Report unread scope.

Read sources once; reuse unchanged text/citations. Expand for task gaps.
Compare STATE baseline branch/commit with Git; reconcile Current Context/Last Session. Missing evidence is unknown.
Keep pending tasks/blockers until resolved with evidence or explicit cancellation. Log changes/handoffs; no read-only rewrite. Subagents stage; lead promotes. Follow project instructions.

Procedures: `.log-file-genius/product/docs/context-guide.md`.
