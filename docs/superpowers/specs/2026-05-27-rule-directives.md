# Rule Directive Checklist (pre-compression snapshot)

Captured before the Phase 4 token diet (T10/T11). Every directive/section below
MUST still be present after compression. Enforced by
`product/tests/test_rule_directives.py`. This is the objective completeness gate
that replaces subjective "did we keep everything?" judgment.

## log-file-maintenance.md (claude-code AND augment — identical structure)

Required section headings (must all remain):
- MANDATORY RULE - NO EXCEPTIONS
- BEFORE EVERY COMMIT
- AFTER EVERY COMMIT
- FAILURE DETECTION & SELF-CORRECTION
- SESSION START
- SESSION END
- TOKEN SELF-ASSESSMENT
- ENTRY VERBOSITY
- CROSS-REFERENCES
- ARCHIVAL
- TEMPLATES
- SUCCESS CRITERIA

Required behaviors within those sections (must survive compression):
- BEFORE EVERY COMMIT: update CHANGELOG (Unreleased + category), update STATE/DEVLOG
  when applicable, stage log files, show pre-commit checklist.
- AFTER EVERY COMMIT: self-checks + show verification.
- FAILURE DETECTION: stop, tell user, fix, verify, resume.
- SESSION START: read STATE (Current Context + Last Session) [CHANGED from DEVLOG],
  staleness check (>7 days), acknowledge.
- SESSION END: write STATE Last Session handoff [CHANGED from DEVLOG]; subagent skip clause.
- TOKEN SELF-ASSESSMENT: ~4 chars/token heuristic; budgets CHANGELOG <10k / DEVLOG
  <15k / combined <25k.
- ENTRY VERBOSITY: three formats — compact, incident (🚨 INCIDENT + rubric), standard;
  decision guide.
- CROSS-REFERENCES: navigation hints between files.
- ARCHIVAL: token-limit triggers; archive oldest first; summary line.
- TEMPLATES: read-only reference.
- SUCCESS CRITERIA: every commit includes CHANGELOG + checklist + verification.

## status-update.md (claude-code AND augment)

- Trigger phrase ("status update")
- Step 1: read source files (now via config paths; STATE for current state)
- Step 2: extract key info
- Step 3: format output (the status block)
- Example output + Tips

## update-planning-docs.md (claude-code AND augment)

- Trigger phrase ("update planning docs")
- Step 1: ask what needs updating (menu)
- Step 2: options — Update CHANGELOG, Update DEVLOG, Update STATE (Current Context +
  Last Session) [CHANGED from "Update DEVLOG Current Context"], Create ADR, All
- Step 3: offer to commit
- Key Files Reference (now config-driven, logs/ fallback)
- Tips

## Notes on intended changes (NOT removals)

These are deliberate edits, not directive losses:
- SESSION START/END now read/write STATE instead of DEVLOG Current Context.
- All hardcoded `docs/planning/` paths become config reads with `logs/` fallback.
- update-planning-docs Option 3 retargets to STATE.
- project_instructions.md (claude-code only): budgets corrected to 10k/15k/25k +
  STATE <500; default paths → logs/.
