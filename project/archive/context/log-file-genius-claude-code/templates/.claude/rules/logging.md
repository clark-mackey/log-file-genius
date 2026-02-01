---
paths: logs/**/*.md
---

# Log File Rules

## Token Budgets (STRICT)
- CHANGELOG.md: ~2,000 tokens max
- DEVLOG.md: ~3,000 tokens max  
- STATE.md: <500 tokens max
- Individual ADRs: ~1,000 tokens max

## Separation of Concerns
- **CHANGELOG**: Facts only (files, versions, what)
- **DEVLOG**: Narrative only (reasoning, why, decisions)
- **STATE**: Current context only (agent, task, blockers)
- **ADRs**: Significant decisions with alternatives

## Formatting
- Use ISO dates: YYYY-MM-DD
- Use relative file paths from project root
- Include bidirectional links between related entries

## Archiving
When a log exceeds its budget:
1. Move older entries to `logs/archive/[filename]-[date].md`
2. Keep most recent entries in main file
3. Add archive reference link at bottom of main file

## Multi-Agent Coordination
- Always read STATE.md before starting work
- Always update STATE.md when:
  - Starting a new task
  - Completing a task
  - Encountering a blocker
  - Handing off to another agent
