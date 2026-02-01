# Multi-Agent Handoff Protocol

## Session Start Checklist
1. Read `logs/STATE.md` first
2. Check for blockers or pending handoffs
3. Review last 2-3 DEVLOG entries if context needed
4. Acknowledge state before proceeding

## Session End Checklist
1. Update STATE.md with:
   - Current task status
   - Any blockers encountered
   - Clear next steps
2. Add DEVLOG entry if significant decisions made
3. Add CHANGELOG entry if files modified
4. Verify bidirectional links

## Handoff Format
When handing off to another agent, STATE.md must include:

```markdown
## Handoff Ready

**From:** [Your identifier]
**To:** [Target agent or "Any"]
**Task:** [What needs to be done]
**Context:** [Essential background]
**Files:** [Key files to review]
**Warnings:** [Gotchas or things to avoid]
```

## Collision Prevention
- Check STATE.md before modifying shared files
- If another agent is "In Progress" on related work, coordinate
- Use file-level locks in STATE.md if needed:

```markdown
## File Locks
- `src/api/auth.ts` - [Agent] - [Reason]
```
