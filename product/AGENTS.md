---
doc: AGENTS
type: Agent Instructions
related:
  state: logs/STATE.md
  adr_index: logs/adr/README.md
---

# LFG context

Read `logs/STATE.md` then `logs/adr/README.md`. Union global, path and task matches; read active ADRs, follow replacements. Missing/stale index or no match: search ADR sources. Report unread scope; never assume coverage.

Compare STATE baseline branch/commit with Git and reconcile Current Context/Last Session contradictions. Missing evidence is unknown. Log meaningful changes/handoffs; read-only questions need no rewrite. Record maintenance: follow delegation policy in procedures. Prefer capable lower-cost subagents; otherwise work directly. Subagents stage; lead verifies/promotes. Follow project instructions.

Repo-root CLI: `python3 ".log-file-genius/product/scripts/lfg.py" --help` (Windows: `python`). No Python: read Markdown. Missing submodule: `git submodule update --init`. Procedures: `.log-file-genius/product/docs/context-guide.md`.
