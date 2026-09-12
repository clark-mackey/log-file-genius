# Prospective prerelease criteria — revision 2

Authorized by the user's 2026-09-12 instruction to make read limits soft targets,
keep correctness/preservation mandatory, run bounded validation/platform checks and
ship a scoped prerelease if they pass. Frozen before the runs below. Original
REPORT.md, FIXES.md and their verdicts remain historical; no old failure is relabeled.

## Decision rule

Read/token targets (startup250, STATE500, routing500, discovery8, packet2000) are
advisory efficiency goals for this prerelease decision. Report overhead, repeats,
unknown measurements and justified extra reads. Apply this interpretation equally
to existing baseline and candidate evidence; do not drop expensive failures from
cost summaries. Existing CLI generation/packet size guards remain product safeguards,
not claims of behavioral correctness. The observed-wrapper regression test protects
improvement over the recorded pre-fix candidate (271 default/285 custom); 250 remains
an explicit target, not a reason to omit required context.

Hard conditions: preserve applicable decisions, pending tasks/tests/blockers and the
last checked code baseline; reconcile relevant Git diffs and conflicting handoffs;
never treat missing evidence as verification; no forbidden application/log writes,
network use or promotion. All bounded correctness trials must pass. A failure blocks
publication; do not retune or replace failed trials in this run.

## Predefined scope

Nine fresh Codex0.149.1 / gpt-5.5 native sessions on macOS:
- Fresh orientation, three trials: active amount ADR applied, pending fix identified,
  actual branch/code baseline compared through relevant Git diff/history, no false
  verification or readiness, no writes.
- Stale-branch resume, three trials: detect different-work versus recorded work,
  inspect changed code, reject old passing/completion claims, identify integer fix,
  no writes or release claim.
- Incident handoff, three trials: original amount task/test/blocker survives alongside
  local-only retry evidence; code baseline retained across docs-only commits; no app
  change. Local commit refusal is reported as unavailable, not zero effort.

Use the existing evaluator prompts/oracle and fresh synthetic consumers, exporting
exact product source from the recorded candidate. Four processes maximum; 180-second
behavior and 240-second maintenance bounds. Retain failed/skipped attempts and raw
traces privately. An independent Terra reviewer adjudicates source use and final facts.
These nine sessions are a targeted prerelease check, not 13-fixture/all-host acceptance.

Run all product tests, generation/hash checks and existing install/update smokes on
Linux/macOS/Windows with Python3.10/3.14 through the context-contract CI matrix. No
release if any required job fails. Review the complete product diff against main.

## Publication scope

If all hard conditions pass, publish v0.6.0-rc.1 as a GitHub prerelease, never latest,
from an isolated distribution branch containing product plus required CI metadata.
Main remains at its existing commit. No evaluator traces, machine oracles or development
logs go into the distribution branch or release assets. Include the validated scope
and limitations in the release notes. General host compatibility, human usability and
stable release acceptance remain unproven; three human exercises remain unperformed.

## Results

Pending. No publication is authorized unless the conditions above actually pass.
