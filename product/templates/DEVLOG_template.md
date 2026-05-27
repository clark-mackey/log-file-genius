---
doc: DEVLOG
related:
  changelog: ./CHANGELOG.md
  state: ./STATE.md
  adr_index: ./adr/README.md
---

# Development Log

A narrative chronicle of the project journey - the decisions, discoveries, and pivots that shaped the work.

---

## Related Documents

📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes and version history
📈 **[STATE](./STATE.md)** - Current project state (the now)
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** This file tells the story of *why* decisions were made. For current project state and session handoff, read **STATE.md** (the now). For technical details of *what* changed, see CHANGELOG.md.

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

Older entries are archived when the file exceeds its token budget (~15,000 tokens).
Each link includes a brief summary so agents know what's inside without opening the file:
- *No archived entries yet*

---

## Template Guidelines (Remove this section in actual use)

### Entry Formats for Daily Log

**Compact format** (default for routine work, ~50-80 tokens):

```markdown
### YYYY-MM-DD: Title
Why/what in 1-2 sentences. Context or rationale.
Files: `file1.py`, `file2.py`
```

**Standard format** (for major decisions, milestones, ~150-250 tokens):

```markdown
### YYYY-MM-DD: Title - The Core Theme

**The Situation/Problem/Context:** Set the scene (1-2 sentences)

**The Decision/Fix/Solution:** What you did about it (1-3 sentences)

**Why This Matters/The Insight/The Lesson:** The takeaway (1-2 sentences)

**Files Changed:** `file1.py`, `file2.py`
```

**Incident format** (for failures worth learning from, ~80-120 tokens):

```markdown
### YYYY-MM-DD: 🚨 INCIDENT - Short description of what failed

**Root Cause:** Why it happened (1-2 sentences)
**Prevention:** How to stop it recurring (1-2 actions)
**Detection:** How to catch it earlier next time (1 action)
Files: `file1.py`, `file2.py` → CHANGELOG: `v1.2.1`
```

**Incident rubric — always qualifies:**
1. **Security exposure** — secrets, credentials, or PII leaked or nearly leaked
2. **Data loss or corruption** — user data, log history, or config destroyed
3. **Repeated failure** — same error occurs 3+ times across sessions
4. **Silent failure** — something broke but no error was raised or detected
5. **Rule violation with impact** — AI skipped a required step and it caused downstream problems
6. **Regression** — a previously working feature broke due to a change

> **For AI Agents:** Use the `🚨 INCIDENT` prefix so incidents are findable by text search. Not every bug is an incident — only failures where root-cause analysis prevents recurrence. When in doubt, use compact format with a note instead.

**Decision guide:** Security/data/regression → incident. Needs an ADR → standard. Everything else → compact.

### Best Practices for AI Efficiency

1. **Keep daily entries focused** - One main story per day, not multiple mini-stories
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

- **ADR Index:** ~50-100 tokens (grows slowly)
- **Daily entry:** ~150-250 tokens each
- **Entire file:** <15,000 tokens with 14-day archive strategy
- **Archive trigger:** Entries older than 14 days

### Narrative Tips for Token Efficiency

- ✅ "The validation rules were buried at the end of the config, so the AI treated them as optional."
- ❌ "We had built the entire validation system — the linter, the config parser, the error handling. Everything was in place. But when we tested it with a real project, the AI skipped validation entirely. We were confused. We opened the config file and read through every section carefully..."

- ✅ "Moved the retry logic to a shared utility, cutting duplication from 12 call sites to 1."
- ❌ "But then we noticed something frustrating. Every API call had its own retry logic. Some retried 3 times, some 5, some not at all. The timeout values were different everywhere. We spent an hour cataloging every single call site..."

**The difference:** Same story, same insights, 60-70% fewer tokens.

