# AI Usage Log - Context Optimization Research

**Research Period:** 2025-11-10 to 2025-11-24 (2 weeks)  
**Purpose:** Measure actual AI usage of CHANGELOG vs DEVLOG to optimize token efficiency  
**Scope:** Development branch only (not distributed to users)

---

## Instructions for AI Assistants

### At End of Each Session:

Add one line to the **Session Log** section below using this format:

```
YYYY-MM-DD | Task: [brief description] | Read: [C/D/A/N] | Useful: [C/D/A/N] | Notes: [optional]
```

**Legend:**
- **C** = CHANGELOG.md
- **D** = DEVLOG.md  
- **A** = ADR (any architectural decision record)
- **N** = None of the above

**Examples:**
```
2025-11-10 | Epic 19 migration | Read: D,A-014 | Useful: D,A-014 | Current Context section was key
2025-11-11 | Bug fix in installer | Read: D | Useful: D | CHANGELOG not needed
2025-11-12 | New feature planning | Read: C,D,A-012 | Useful: D | CHANGELOG read but not useful
2025-11-13 | Quick documentation update | Read: N | Useful: N | No log files needed
```

### What to Track:

**Read:** Which files did you actually open/view during the session?
- Be honest - only list files you actually read
- Include specific ADR numbers if applicable
- Use "N" if you didn't read any log files

**Useful:** Which files actually helped you complete the task?
- A file can be "Read" but not "Useful" (read but didn't help)
- A file should only be "Useful" if it provided information you needed
- Use "N" if none of the log files were useful

**Notes:** Optional context
- Why was a file useful? (e.g., "Current Context section", "Found commit hash")
- Why was a file not useful? (e.g., "Too much history", "Outdated info")
- What information were you looking for?

---

## Session Log

### Week 1 (Nov 10-16, 2025)

2025-11-10 | Epic 19 migration | Read: D,A-014 | Useful: D,A-014 | Current Context + migration decision

### Week 2 (Nov 17-24, 2025)

---

## Analysis Questions (For End of Research Period)

After 2 weeks, analyze the data to answer:

1. **Usage Frequency:**
   - How often was CHANGELOG read? (X/Y sessions = Z%)
   - How often was DEVLOG read? (X/Y sessions = Z%)
   - How often were ADRs read? (X/Y sessions = Z%)

2. **Usefulness Ratio:**
   - When CHANGELOG was read, how often was it useful? (X/Y = Z%)
   - When DEVLOG was read, how often was it useful? (X/Y = Z%)
   - When ADRs were read, how often were they useful? (X/Y = Z%)

3. **Token Efficiency:**
   - CHANGELOG: ~8,000 tokens, used in X% of sessions, useful in Y% → Z tokens per useful session
   - DEVLOG: ~21,000 tokens, used in X% of sessions, useful in Y% → Z tokens per useful session

4. **Patterns:**
   - What types of tasks required CHANGELOG? (e.g., debugging, version tracking)
   - What types of tasks required DEVLOG? (e.g., understanding decisions, current context)
   - What types of tasks required neither? (e.g., simple edits, documentation)

5. **Recommendations:**
   - Should CHANGELOG be minimized/archived more aggressively?
   - Should CHANGELOG be merged into DEVLOG?
   - Should CHANGELOG format change for solo-developer profile?
   - What's the optimal token budget allocation?

---

## Research Methodology

See: `project/research/ai-context-optimization-methodology.md` for full research design.

**Hypothesis:**
- DEVLOG provides higher value per token than CHANGELOG for AI assistants
- CHANGELOG is rarely consulted after initial commit
- Current Context section in DEVLOG is read most frequently
- Solo developers may benefit from different log structure than teams

**Success Criteria:**
- Collect data from 10+ sessions over 2 weeks
- Identify clear usage patterns
- Make data-driven recommendation for solo-developer profile
- Potential token savings of 5,000+ tokens if CHANGELOG can be minimized

---

## Notes

- This is a **research project** - findings may lead to changes in LFG v0.2.0
- Data is **self-reported by AI** - may have bias toward compliance
- Consider validating with conversation analysis if results are unclear
- This log file itself costs ~500 tokens - will be archived after research period

