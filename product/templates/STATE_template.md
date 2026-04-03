# Current State

**Last Updated:** [Current Date and Time]
**Updated By:** [Agent Name] ([branch])

---

## Related Documents

📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
📖 **[DEVLOG](./DEVLOG.md)** - Development narrative and decision rationale
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** This file provides at-a-glance status for multi-agent coordination. Read this FIRST before starting work to avoid conflicts and duplicate effort. Update at the START and END of each work session.

---

## Active Work

- *No active work sessions*

---

## Blockers

- *None*

---

## Recently Completed (Last 2-4 Hours)

- *No recent completions*

---

## Next Priorities

1. [First priority task]
2. [Second priority task]

---

## Branch Status

- **main**: [Status]

---

## Token Budget Dashboard (Optional)

- **STATE.md**: ~[X] tokens (target: <500)
- **CHANGELOG**: ~[X] tokens (target: <10,000)
- **DEVLOG**: ~[X] tokens (target: <15,000)
- **Combined logs**: ~[X] tokens (target: <25,000)

---

## Template Guidelines (Remove this section in actual use)

### When to Update STATE.md

**Update at START of work session:**
- Add yourself to "Active Work" section
- Check for blockers that might affect your work
- Verify no conflicts with other agents' active work

**Update DURING work session:**
- Every 30-60 minutes with progress updates
- Immediately when blocked (add to "Blockers" section)
- When completing significant milestones

**Update at END of work session:**
- Move your task from "Active Work" to "Recently Completed"
- Update branch status
- Clear any blockers you resolved

### Best Practices for Multi-Agent Coordination

1. **Read STATE.md FIRST** - Before starting any work
2. **Update immediately** - Don't batch updates, keep it fresh
3. **Be specific** - "Working on login" is vague, "Adding email verification to signup flow" is clear
4. **Include timestamps** - Helps agents understand recency
5. **Archive to CHANGELOG** - Move "Recently Completed" items older than 24 hours to CHANGELOG
6. **Keep it under 500 tokens** - This is a snapshot, not a history

### What Belongs in STATE.md vs DEVLOG vs CHANGELOG

**STATE.md (this file):**
- What's happening RIGHT NOW (last 2-4 hours)
- Who's working on what
- Current blockers
- Immediate next steps
- Branch status

**DEVLOG:**
- Why decisions were made
- Narrative of project evolution
- Lessons learned
- Context for future reference
- Current Context section (updated weekly)

**CHANGELOG:**
- What changed (facts only)
- Version history
- File paths and PR links
- Completed features and fixes

### Token Efficiency Target

- **Target:** <500 tokens (roughly 300-400 words)
- **Update frequency:** Every 30-60 minutes during active work
- **Archive trigger:** Move "Recently Completed" items older than 24 hours to CHANGELOG
- **Freshness:** Should always reflect last 2-4 hours of activity

### Multi-Agent Workflow Example

**Agent starts work:**
1. Reads STATE.md → sees what other agents are working on
2. Adds to "Active Work": "[Agent Name] ([branch]): [Specific task description]"
3. Checks "Blockers" → confirms no conflicts
4. Proceeds with work

**Agent completes work:**
1. Moves task from "Active Work" to "Recently Completed" with timestamp
2. Updates "Branch Status"
3. Updates "Next Priorities" if needed
4. Commits changes to STATE.md

### Example Entry Formats

**Active Work:**
```markdown
- **Agent-1** (feature/login): Adding email verification flow
- **Agent-2** (main): Updating configuration schema
```

**Blockers:**
```markdown
- Config schema migration needs review before merging (blocks Agent-2)
```

**Recently Completed:**
```markdown
- ✅ Email verification flow implemented and tested (Agent-1, 14:30)
- ✅ Config schema updated, tests passing (Agent-2, 15:00)
```

**Branch Status:**
```markdown
- **main**: Clean, all tests passing (last updated: 15:30)
- **feature/login**: 3 commits ahead, tests passing, ready for review
```

