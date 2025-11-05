# Development Log

A narrative chronicle of the project journey - the decisions, discoveries, and pivots that shaped the work.

---

## Related Documents

📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
📈 **[STATE](./STATE.md)** - Current project state and metrics

> **For AI Agents:** This file tells the story of *why* decisions were made. Before starting work, read **Current Context** section. For technical details of *what* changed, see CHANGELOG.md.

---

## Current Context (Source of Truth)

**Last Updated:** [Current Date]

### Project State
- **Project:** [Your Project Name]
- **Current Version:** v0.1.0-dev
- **Active Branch:** `main`
- **Phase:** Initial setup

### Current Objectives
- [ ] Set up initial project structure
- [ ] Configure development environment
- [ ] Document architectural decisions

### Known Risks & Blockers
- None yet

---

## Daily Log - Newest First

### 2025-11-05: Setting Up Log File Genius

**The Situation:** Starting a new project and needed a structured way to document decisions, track changes, and maintain context for AI assistants.

**The Challenge:** How do we keep development history organized without creating overhead that slows down progress?

**The Decision:** Adopted Log File Genius methodology with CHANGELOG for technical changes, DEVLOG for decision narratives, and STATE for current project status.

**Why This Matters:** Having structured logs means AI assistants can understand project context without lengthy explanations. It also creates a searchable history of why decisions were made.

**The Implementation:** Ran the installer, configured for solo-developer profile, set up initial log files.

**The Result:** Clear structure for documenting work. AI assistants can now read context from logs instead of asking repetitive questions.

**Files Changed:** `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/STATE.md`, `.logfile-config.yml`

---

### [Date]: [Brief Title - What You Accomplished]

**The Situation:** [What was happening? What context led to this work?]

**The Challenge:** [What problem needed solving? What question needed answering?]

**The Decision:** [What did you decide to do? What approach did you take?]

**Why This Matters:** [Why was this important? What would have happened if you chose differently?]

**The Implementation:** [How did you implement it? What were the key steps?]

**The Result:** [What was the outcome? Did it work as expected?]

**Files Changed:** [List the main files that were modified]

---

### [Date]: [Another Entry Title]

**The Problem:** [Describe the problem you encountered]

**The Investigation:** [What did you try? What did you discover?]

**The Solution:** [How did you solve it?]

**The Lesson:** [What did you learn? What would you do differently next time?]

**Files Changed:** [List the files]

---

## Archive

**Entries older than 14 days** are archived for token efficiency:
- [DEVLOG-2025-10-W3.md](../archive/DEVLOG-2025-10-W3.md) - Week of Oct 20-26
- [DEVLOG-2025-10-W2.md](../archive/DEVLOG-2025-10-W2.md) - Week of Oct 13-19
- [DEVLOG-2025-10-W1.md](../archive/DEVLOG-2025-10-W1.md) - Week of Oct 6-12

---

## Template Guidelines (Remove this section in actual use)

### Entry Format for Daily Log

Each entry should tell a story with this structure:

```markdown
### YYYY-MM-DD: Title - The Core Theme

**The Situation/Problem/Context:** Set the scene (1-2 sentences)

**The Challenge/Investigation/Realization:** What you discovered (1-3 sentences)

**The Decision/Fix/Solution:** What you did about it (1-3 sentences)

**Why This Matters/The Insight/The Lesson:** The takeaway (1-2 sentences)

**The Result/Impact/Outcome:** What happened (1 sentence)

**Files Changed:** `file1.py`, `file2.py`

**Shipped:** vX.Y.Z (if applicable)
```

### Best Practices for AI Efficiency

1. **Current Context is sacred** - Update it weekly or when major changes occur
2. **Keep daily entries focused** - One main story per day, not multiple mini-stories
3. **Use ADRs for decisions** - Link to them, don't duplicate the full rationale
4. **Archive aggressively** - Move entries >14 days to `/archive/DEVLOG-YYYY-MM-Wn.md`
5. **Link to files** - Help AI locate relevant code
6. **Preserve the narrative** - This is a story, not a bullet list
7. **But be concise** - Aim for 150-250 words per entry, not 500+

### What Belongs in DEVLOG vs CHANGELOG

**DEVLOG (this file):**
- Why decisions were made
- What you discovered/learned
- Context and rationale
- The story arc of the project
- Challenges and how you solved them

**CHANGELOG:**
- What changed (facts only)
- Version numbers
- File paths
- PR/issue links
- One-line descriptions

**ADRs (separate files):**
- Architectural decisions with long-term impact
- Tradeoffs and alternatives considered
- Formal decision records

### Token Efficiency Targets

- **Current Context section:** ~500-800 tokens (updated weekly)
- **ADR Index:** ~50-100 tokens (grows slowly)
- **Daily entry:** ~150-250 tokens each
- **Entire file:** <15,000 tokens with 14-day archive strategy
- **Archive trigger:** Entries older than 14 days

### Narrative Tips for Token Efficiency

- ✅ "The feedback instructions were buried at the end, so Claude treated them as optional."
- ❌ "We had built the entire feedback infrastructure - the `rate_skill` tool, the Supabase database, the authentication system. Everything was in place. But when we tested it with a real skill, Claude never asked for feedback. We were confused and frustrated. We downloaded the skill ZIP file and examined the SKILL.md file carefully..."

- ✅ "Added explicit 'IMMEDIATELY' instruction, cutting response time from 5-7 seconds to <1 second."
- ❌ "But then we noticed something frustrating. When the user typed '5' to rate the output, Claude took 5-7 seconds to respond. We could see it in the UI: 'Thinking about the significance of the number 5...' What?! Claude was overthinking a simple rating!"

**The difference:** Same story, same insights, 60-70% fewer tokens.

