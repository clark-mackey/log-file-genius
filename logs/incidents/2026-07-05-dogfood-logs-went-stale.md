---
doc: INCIDENT
related:
  changelog: ../CHANGELOG.md
  devlog: ../DEVLOG.md
  state: ../STATE.md
---

# Incident Report: Own logs went stale for five months while shipping log-maintenance tooling

**Date:** 2026-07-05
**Severity:** Medium
**Status:** Resolved
**Owner:** Claude Code (with Clark)
**Systems:** logs/STATE.md, logs/DEVLOG.md, logs/CHANGELOG.md, project/specs/prd.md

---

## Related Documents

📊 **[CHANGELOG](../CHANGELOG.md)** · 📖 **[DEVLOG](../DEVLOG.md)** · 📈 **[STATE](../STATE.md)**

---

## Summary
The project that sells log hygiene stopped maintaining its own logs: STATE.md said v0.2.0/Spec-1 while the product shipped v0.3.0, v0.4.0, and built v0.5.0; DEVLOG's newest entry was 2026-02-01; CHANGELOG pooled five months of entries in `[Unreleased]` with no version blocks cut, plus mojibake emoji from an encoding round-trip.

## Timeline
- 2026-02-01 — last DEVLOG narrative entry written
- 2026-05-27 — STATE.md last touched (Spec 1 era)
- 2026-05-29 → 2026-06-01 — v0.3.0 and v0.4.0 released; no version blocks cut, STATE not updated
- 2026-06-01 → 2026-07-04 — Spec 5 designed and implemented in a side worktree; logs untouched
- 2026-07-05 — detected during pre-improvement context review; repaired same day

## Root Cause
Spec work happened in isolated git worktrees on feature branches, and sessions ended at "code done" rather than "logs done" — the SESSION END rule was never triggered because sessions rolled directly into the next task. Releases were promoted from `development` to `main` without a release checklist step that cuts a CHANGELOG version block and refreshes STATE. The mojibake came from editing CHANGELOG with a tool that decoded UTF-8 as cp1252 and re-encoded.

## Resolution
Rebuilt CHANGELOG with v0.3.0/v0.4.0/v0.5.0 version blocks derived from git history; rewrote STATE.md to actual current state; added DEVLOG catch-up narrative covering Specs 1–5; fixed mojibake; refreshed PRD Current State section; bumped dogfood config to 0.5.0.

## Prevention
Release promotion now includes cutting the CHANGELOG version block and updating STATE.md in the same session as the version bump (added to STATE.md objectives as a standing rule). Worktree-based spec work must end with a log update on `development` before the worktree is considered done.

## Detection
Story 8.10 staleness rule already covers this (`Last Updated` >7 days → agent must refresh before other work) — it fired correctly at today's session start; the gap was that no session had started from `development`'s logs in five months. `lfg validate` warning on stale STATE (>14 days) exists; running it in CI on `development` pushes would have surfaced this weeks earlier.

## Files
`logs/CHANGELOG.md`, `logs/STATE.md`, `logs/DEVLOG.md`, `project/specs/prd.md`, `.logfile-config.yml` → DEVLOG 2026-07-05
