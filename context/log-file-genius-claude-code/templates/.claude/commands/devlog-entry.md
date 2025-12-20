# Add DEVLOG Entry

Add a narrative entry to the DEVLOG following Log File Genius conventions.

## Instructions

1. Read `logs/STATE.md` to understand current context
2. Read the last 3 entries in `logs/DEVLOG.md` for continuity
3. Create a new entry with this structure:

```markdown
## [DATE] - [Brief Title]

**Context:** [What prompted this work]

**Narrative:** [The story - why decisions were made, what was learned, reasoning]

**Related:** 
- CHANGELOG: [link to related changelog entry if applicable]
- ADR: [link to related ADR if applicable]
```

## Token Budget
- Keep entry under 500 tokens
- Focus on WHY, not WHAT (facts go in CHANGELOG)
- Capture reasoning that would be lost otherwise

## Quality Checklist
- [ ] Entry explains reasoning, not just actions
- [ ] Bidirectional links added if related entries exist
- [ ] Token budget respected
- [ ] Entry provides value for future context

$ARGUMENTS contains any additional context for this entry.
