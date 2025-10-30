# log-file-maintenance (Always)

## Log File Maintenance Rules

### Daily Updates

- **CHANGELOG Current Context:** Not applicable (CHANGELOG doesn't have Current Context - that's in DEVLOG)
- **DEVLOG Current Context:** Update when project state changes (version, branch, phase, stack, objectives, ADRs)
  - Location: `docs/planning/DEVLOG.md` → "Current Context (Source of Truth)" section
  - Update: Version, active branch, phase, current objectives, known risks

### After Every Commit

- **CHANGELOG entries:** Add single-line entry in "Unreleased" section
  - Format: `- Feature name - Brief description. Files: \`path/to/file.md\`. PR: [#1234](link)`
  - Categories: Added, Changed, Fixed, Deprecated, Removed, Security
  - Location: `docs/planning/CHANGELOG.md`

### After Milestones/Decisions

- **DEVLOG entries:** Add narrative entry when epics/milestones/decisions complete
  - Format: Situation/Challenge/Decision/Impact/Files structure
  - Location: `docs/planning/DEVLOG.md` → "Daily Log" section
  - Keep entries concise: 150-250 words each

### When Requirements Change

- **PRD:** Update immediately for requirement changes
  - Location: `docs/prd.md` (currently in BMAD context)
  - Update relevant sections: Requirements, Epics, Stories, Success Metrics

### Multi-Agent Workflow

- **Before starting work:** Always read DEVLOG → Current Context section
- **After finishing work:** Update CHANGELOG and DEVLOG with changes made

### Archival Process

- **Trigger:** When CHANGELOG or DEVLOG exceed 10,000 tokens
- **Action:** Copy entries older than 2 weeks to archive files
- **Archive location:** `docs/planning/archive/`
- **Naming:** `CHANGELOG-YYYY-MM.md` or `DEVLOG-YYYY-MM-Wn.md`
- **Keep in current file:** Last 2 weeks of entries

### Token Budget Targets

- **CHANGELOG:** <10,000 tokens (with archival)
- **DEVLOG:** <15,000 tokens (with archival)
- **Combined:** <25,000 tokens
- **Per entry:** 60-80 tokens (CHANGELOG), 150-250 tokens (DEVLOG)

## Quick Reference

**Full documentation:** `docs/log_file_how_to.md`
**Templates:** `templates/` directory
**Current logs:** `docs/planning/` directory
**ADRs:** `docs/adr/` directory

