# Log File Genius - Claude Code Configuration

## Overview
This project uses the Log File Genius documentation system for token-efficient AI context management.

## Log File Locations
- `logs/CHANGELOG.md` - Facts only (what changed, files, versions)
- `logs/DEVLOG.md` - Narrative (why it changed, reasoning)
- `logs/STATE.md` - Current agent/task state
- `logs/adr/` - Architecture Decision Records

## Token Budgets
| Document | Budget | Purpose |
|----------|--------|---------|
| CHANGELOG | ~2k tokens | Facts, files, versions |
| DEVLOG | ~3k tokens | Narrative, reasoning |
| STATE | <500 tokens | Current context |
| ADRs | On-demand | Decision records |

## Commands
- Read STATE.md before starting any task
- Update STATE.md when switching tasks or agents
- Add CHANGELOG entry for file changes
- Add DEVLOG entry for significant decisions

## Workflow
1. Check `logs/STATE.md` for current context
2. Review recent `logs/DEVLOG.md` entries if needed
3. Complete task
4. Update logs appropriately
5. Update STATE.md if task complete or handoff needed

## File References
See @logs/STATE.md for current state
See @logs/DEVLOG.md for recent narrative
See @logs/CHANGELOG.md for change history

## Rules
- Never exceed token budgets
- Facts go in CHANGELOG, narrative goes in DEVLOG
- Keep STATE.md current for multi-agent coordination
- Use bidirectional frontmatter links between related entries
- Archive old entries when logs exceed budgets
