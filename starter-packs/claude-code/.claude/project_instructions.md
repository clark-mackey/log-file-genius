# Log File Genius - Claude Code Project Instructions

This project uses the **Log File Genius** system - a token-efficient documentation methodology for AI-assisted development.

## Core Principles

1. **Maintain the Five-Document System:**
   - **PRD** (`docs/prd.md`) - What we're building and why
   - **CHANGELOG** (`docs/planning/CHANGELOG.md`) - What changed (facts)
   - **DEVLOG** (`docs/planning/DEVLOG.md`) - Why it changed (narrative)
   - **STATE** (`docs/planning/STATE.md`) - What's happening now (optional)
   - **ADRs** (`docs/adr/*.md`) - How we decided (architectural decisions)

2. **Token Efficiency:**
   - Keep CHANGELOG + DEVLOG + STATE under 10,000 tokens combined
   - Use single-line entries in CHANGELOG
   - Use structured format (Situation/Challenge/Decision/Impact/Files) in DEVLOG
   - Archive old entries when files exceed token budgets

3. **Always-Active Rules:**
   - Follow the log file maintenance rules in `.claude/rules/log-file-maintenance.md`
   - Update CHANGELOG after every commit
   - Update DEVLOG after milestones/decisions
   - Read DEVLOG Current Context before starting work

## Available Commands

When the user invokes these commands, follow the corresponding rule file:

- **"status update"** → See `.claude/rules/status-update.md`
- **"update planning docs"** → See `.claude/rules/update-planning-docs.md`

## Quick Reference

- **Full methodology:** `docs/log_file_how_to.md`
- **Templates:** `templates/` directory
- **Examples:** `examples/` directory
- **Working logs:** `docs/planning/` directory
- **ADRs:** `docs/adr/` directory

## Important Notes

- This project dogfoods its own log file system
- Templates in `templates/` are for distribution (don't edit with project-specific content)
- Working logs in `docs/planning/` are this project's actual logs
- Always check `docs/log_file_how_to.md` for detailed guidance on entry formats

