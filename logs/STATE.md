---
type: Project State
doc: STATE
related:
  changelog: ./CHANGELOG.md
  devlog: ./DEVLOG.md
  adr_index: ./adr/README.md
---

# Current State

## Current Context

**Baseline branch:** codex/context-evaluation
**Baseline commit:** 81edfd1
**Next action:** Review the targeted context fixes and plan affected acceptance trials before any main promotion. Refresh human packages to the final candidate before issuing them.
**Tests:** 254 local Python tests pass on 2026-09-12; generated AGENTS and diff checks pass. Nine bounded native development trials are retained. Final Codex fresh check: eight source reads, 243 estimated startup tokens. Final lesson handoff preserved pending facts and the code baseline.
**Blockers:** Full critical/noncritical acceptance remains open. Freshness reconciliation was incomplete in the focused discovery trial. Codex commit effort and Claude injected-byte measurements remain unavailable. Three real-reader packages exist; zero readers have participated. No release or main promotion is authorized by these results.

v0.6.0-dev remains a candidate. Earlier six-platform Python/Bash/PowerShell CI evidence
belongs to the pre-fix revision; it does not certify these changes on Windows/Linux.
[Original evaluation](../project/evaluations/context-2026-09-12/REPORT.md).
[Targeted fixes](../project/evaluations/context-2026-09-12/FIXES.md).

## Last Session

Replaced the stale PR-review/unmeasured-evaluation handoff with completed evidence.
Fixed shared handoff/discovery instructions without adding runtime dependencies.
First pilot exposed additional read-budget and baseline gaps; the focused final
startup check addressed those specific symptoms. No full acceptance rerun, human
simulation, push or promotion. Main and the original checkout remain untouched.

## In Progress

This isolated task owns codex/context-evaluation. Preserve unrelated worktree state.
