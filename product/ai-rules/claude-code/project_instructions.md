# Log File Genius - Claude Code Project Instructions

This project uses the **Log File Genius** system - a token-efficient documentation methodology for AI-assisted development.

## Core Principles

1. **Read Configuration First:**
   - **ALWAYS** read `.logfile-config.yml` to find log file locations
   - Default paths (if config not found):
     - CHANGELOG: `docs/planning/CHANGELOG.md`
     - DEVLOG: `docs/planning/DEVLOG.md`
     - ADR: `docs/adr/`
     - STATE: `docs/STATE.md`

2. **Maintain the Five-Document System:**
   - **PRD** - What we're building and why
   - **CHANGELOG** - What changed (facts)
   - **DEVLOG** - Why it changed (narrative)
   - **STATE** - What's happening now (optional)
   - **ADRs** - How we decided (architectural decisions)

3. **Token Efficiency:**
   - Keep CHANGELOG + DEVLOG + STATE under 10,000 tokens combined
   - Use single-line entries in CHANGELOG
   - Use structured format (Situation/Challenge/Decision/Impact/Files) in DEVLOG
   - Archive old entries when files exceed token budgets

4. **Always-Active Rules:**
   - Follow the log file maintenance rules in `.claude/rules/log-file-maintenance.md`
   - Update CHANGELOG after every commit
   - Update DEVLOG after milestones/decisions
   - Read DEVLOG Current Context before starting work

## Available Commands

When the user invokes these commands, follow the corresponding rule file:

- **"status update"** → See `.claude/rules/status-update.md`
- **"update planning docs"** → See `.claude/rules/update-planning-docs.md`

## Quick Reference

- **Configuration:** `.logfile-config.yml` (log file paths)
- **Full methodology:** `.log-file-genius/product/docs/log_file_how_to.md`
- **Templates:** `log-file-genius/templates/` directory
- **Validation:** `./log-file-genius/scripts/validate-log-files.sh`

## Important Notes

- Always read `.logfile-config.yml` to find log file locations
- Templates in `log-file-genius/templates/` are customizable
- Check `.log-file-genius/product/docs/log_file_how_to.md` for detailed guidance
