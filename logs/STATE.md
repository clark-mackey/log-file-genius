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
**Baseline commit:** c3315cd
**Next action:** Address mandatory freshness reconciliation and canonical baseline-field preservation before any future prerelease attempt. No additional tuning or replacement trials in this run. Refresh human packages before issuing them.
**Tests:** 254 local product tests and generated/version/hash checks pass. Distribution candidate ffc78f7 has the identical product tree; all six Linux/macOS/Windows × Python3.10/3.14 CI jobs and install/update smokes pass. Frozen native validation: 4/9 correctness passes, five failures; all nine completed.
**Blockers:** Four trials omitted required Git comparisons; one made the baseline field unreadable by freshness.py. All-trials-pass gate blocks prerelease. Full acceptance, other-host behavior and three real-reader exercises remain open (zero participants). Codex commit effort and Claude injected-byte measurements remain unavailable.

v0.6.0-rc.1 is an unreleased candidate. Read/token targets are prospectively advisory;
correctness remains mandatory. Startup estimate 245; discovery costs are mixed.
Main remains 0d622e8; no release tag or GitHub Release exists.
[Prerelease evidence](../project/evaluations/context-2026-09-12/PRERELEASE.md).
[Original evaluation](../project/evaluations/context-2026-09-12/REPORT.md).
[Targeted fixes](../project/evaluations/context-2026-09-12/FIXES.md).

## Last Session

Froze revised criteria before nine fresh native sessions. Published only the isolated
product/CI distribution branch codex/context-prerelease for platform validation.
Independent Terra review found five mandatory failures. Recorded every trial without
retuning or replacing failures. Evaluator traces remain outside the public branch.
Earlier development pilots and their limitations remain recorded separately.

## In Progress

This isolated task owns codex/context-evaluation. Preserve unrelated worktree state.
