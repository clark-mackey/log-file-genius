# AI Context Optimization Research - Methodology

**Research Period:** 2025-11-10 to 2025-11-24 (2 weeks)  
**Epic:** Epic 20  
**Status:** Active  
**Researcher:** Solo developer + AI assistants (self-reported data)

---

## Research Question

**Primary:** Which log files do AI assistants actually use, and which provide the best value per token?

**Secondary:**
- How often is CHANGELOG consulted vs. DEVLOG?
- When CHANGELOG is read, is it actually useful?
- Can we reduce token budget by minimizing/archiving CHANGELOG?
- Should solo-developer profile have different log structure than team profile?

---

## Hypothesis

1. **DEVLOG provides higher value per token than CHANGELOG** for AI assistants working with solo developers
2. **CHANGELOG is rarely consulted** after the initial commit that documents a change
3. **Current Context section in DEVLOG** is read most frequently (every session start)
4. **Solo developers may benefit from minimal CHANGELOG + rich DEVLOG** instead of equal investment in both

---

## Current State (Baseline)

### Token Costs
- **CHANGELOG:** ~8,000 tokens (full history, 155 lines)
- **DEVLOG:** ~21,000 tokens (narrative + current context, 1,359 lines)
- **Combined:** ~29,000 tokens (exceeds 25k target by 16%)

### Current Rules
- AI instructed to read DEVLOG "Current Context" at session start
- AI instructed to update CHANGELOG before every commit
- AI instructed to update DEVLOG for milestones/decisions
- No tracking of which files AI actually reads or finds useful

---

## Research Design

### Approach: Self-Reported Usage Tracking

**Method:** AI assistants log their own usage at end of each session

**Rationale:**
- ✅ Easy to implement (just add a rule)
- ✅ Captures AI's perspective on usefulness
- ✅ Low overhead (one line per session)
- ✅ Can start immediately
- ❌ Relies on AI compliance (may have bias)
- ❌ Subjective "useful" judgment

**Alternative approaches considered:**
- Conversation analysis (more objective, but requires export)
- A/B testing (more rigorous, but takes 4+ weeks)
- Token window instrumentation (most accurate, but not all AIs support)

**Decision:** Start with self-reporting for speed, validate with conversation analysis if results unclear

### Data Collection

**Location:** `logs/ai-usage-log.md`

**Format:**
```
YYYY-MM-DD | Task: [description] | Read: [C/D/A/N] | Useful: [C/D/A/N] | Notes: [optional]
```

**Legend:**
- C = CHANGELOG.md
- D = DEVLOG.md
- A = ADR (with number if specific)
- N = None

**Frequency:** Once per session (at end)

**Duration:** 2 weeks (Nov 10-24, 2025)

**Target:** 10+ sessions minimum for statistical relevance

### Metrics

**Primary Metrics:**

1. **Usage Frequency**
   - How often was each file type read? (count, percentage)
   - Formula: `(sessions where file read) / (total sessions) * 100`

2. **Usefulness Ratio**
   - When read, how often was it useful? (count, percentage)
   - Formula: `(sessions where file useful) / (sessions where file read) * 100`

3. **Token Efficiency**
   - Tokens per useful session
   - Formula: `(file token count) / (sessions where file useful)`

**Secondary Metrics:**

4. **Task Type Patterns**
   - Which tasks require CHANGELOG? (e.g., debugging, version tracking)
   - Which tasks require DEVLOG? (e.g., understanding decisions, context)
   - Which tasks require neither? (e.g., simple edits)

5. **Section Usage**
   - Which sections of DEVLOG are most useful? (Current Context, Daily Log, ADRs)
   - Which sections of CHANGELOG are most useful? (Unreleased, specific versions)

### Analysis

**Tool:** `product/scripts/analyze-ai-usage.py`

**Outputs:**
- Usage frequency report (text + JSON)
- Usefulness ratio report
- Token efficiency comparison
- Recommendations based on thresholds

**Decision Thresholds:**

| Metric | Threshold | Action |
|--------|-----------|--------|
| CHANGELOG read <20% | Archive aggressively (keep last 20 entries) |
| CHANGELOG useful <50% when read | Minimize format (remove verbose descriptions) |
| CHANGELOG efficiency >2x DEVLOG | Reduce CHANGELOG tokens significantly |
| DEVLOG read >80% | Maintain current format |
| DEVLOG useful >80% when read | Excellent signal-to-noise, keep investing |

---

## Expected Outcomes

### Scenario A: CHANGELOG is Low Value
**If:** CHANGELOG read <20%, useful <50% when read

**Recommendation:**
- Minimize CHANGELOG to last 20 entries (~1k tokens)
- Archive everything >30 days old
- Focus tokens on DEVLOG narrative
- **Token savings:** ~7,000 tokens

### Scenario B: CHANGELOG is Moderately Useful
**If:** CHANGELOG read 20-50%, useful 50-80% when read

**Recommendation:**
- Keep CHANGELOG but archive more aggressively
- Reduce entry verbosity (shorter descriptions)
- **Token savings:** ~3,000 tokens

### Scenario C: CHANGELOG is High Value
**If:** CHANGELOG read >50%, useful >80% when read

**Recommendation:**
- Keep current CHANGELOG format
- Investigate why it's so useful
- Consider expanding CHANGELOG, reducing DEVLOG

### Scenario D: Both are Low Value
**If:** Both CHANGELOG and DEVLOG read <30%

**Recommendation:**
- Investigate why AI isn't using logs
- May indicate logs are too verbose or poorly structured
- Consider complete redesign

---

## Limitations & Biases

### Known Limitations

1. **Self-reported data** - AI may over-report compliance with rules
2. **Small sample size** - One developer, 2 weeks, ~10-20 sessions
3. **Novelty effect** - AI may read more during research period
4. **Task variation** - Different tasks may skew results
5. **AI assistant variation** - Different AIs may have different reading patterns

### Mitigation Strategies

1. **Honest reporting encouraged** - Rule explicitly says "be honest, this is research"
2. **Extended duration** - 2 weeks to capture variety of tasks
3. **Validation option** - Can analyze conversation history if results unclear
4. **Multiple metrics** - Don't rely on single metric for decision

### Threats to Validity

**Internal:**
- AI may read files just because rule says to track usage
- "Useful" is subjective and may vary by AI interpretation

**External:**
- Results may not generalize to other solo developers
- Results may not generalize to team environments
- Results may not generalize to different AI assistants

**Mitigation:**
- Document findings as "solo developer with Augment" specific
- Recommend validation with other developers/AIs before broad changes

---

## Timeline

- **Nov 10:** Research begins, tracking rule activated
- **Nov 10-24:** Data collection (2 weeks)
- **Nov 25:** Run analysis script, review findings
- **Nov 26:** Make recommendation for LFG v0.2.0
- **Nov 27:** Archive research files, deactivate tracking rule

---

## Success Criteria

**Minimum viable data:**
- ✅ 10+ sessions logged
- ✅ Variety of task types (features, bugs, docs, planning)
- ✅ Clear usage patterns emerge

**Actionable outcome:**
- ✅ Data-driven recommendation for solo-developer profile
- ✅ Potential token savings identified (target: 5,000+ tokens)
- ✅ Clear decision on CHANGELOG format/archival strategy

**Bonus outcomes:**
- ✅ Insights applicable to team profile
- ✅ Methodology reusable for future research
- ✅ Findings publishable as blog post/case study

---

## Post-Research Actions

### If CHANGELOG is Low Value:

1. Create ADR documenting decision to minimize CHANGELOG for solo-developer profile
2. Update solo-developer profile in `.logfile-config.yml`:
   - `changelog_max_entries: 20`
   - `changelog_archive_days: 30`
   - `changelog_token_target: 1000`
3. Update AI rules to reflect new archival strategy
4. Update templates with minimal CHANGELOG example
5. Document in migration guide for existing users

### If CHANGELOG is High Value:

1. Document why CHANGELOG is valuable (which sections, which tasks)
2. Consider expanding CHANGELOG, reducing DEVLOG
3. Update token targets to reflect actual usage
4. No changes to solo-developer profile

### Regardless of Outcome:

1. Archive research files to `project/research/archive/`
2. Deactivate usage-tracking rule
3. Document findings in DEVLOG
4. Share insights with LFG community (if applicable)

---

## Related Documents

- **Usage Log:** `logs/ai-usage-log.md`
- **Tracking Rule:** `.augment/rules/usage-tracking.md`
- **Analysis Script:** `product/scripts/analyze-ai-usage.py`
- **Epic Spec:** `project/specs/EPIC-20-ai-context-optimization.md` (to be created)

