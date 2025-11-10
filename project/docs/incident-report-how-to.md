# Incident Reports - How To Guide

**Purpose:** Learn how to create, manage, and learn from incident reports in Log File Genius.

**Last Updated:** 2025-11-03  
**Related:** [INCIDENT_REPORT_template.md](../templates/INCIDENT_REPORT_template.md)

---

## What Are Incident Reports?

**Incident Reports catalog the past, but they're really about the future.**

They document:
- **What went wrong** (the incident)
- **Why it went wrong** (root cause)
- **How to prevent it** (systemic improvements)
- **How to verify it's fixed** (validation)

Unlike CHANGELOG (what changed) or DEVLOG (why we decided), Incident Reports focus on **learning from failures** to build more robust systems.

---

## When to Create an Incident Report

### Always Create for:
- **SEV-1/SEV-2 incidents** (security, data loss, system down)
- **Repeated failures** (same issue occurring multiple times)
- **Near misses** (almost caused major impact)
- **Systemic issues** (reveals pattern or architectural flaw)

### Consider Creating for:
- **SEV-3 incidents** (degraded performance, minor bugs)
- **Learning opportunities** (interesting failure modes)
- **Process failures** (AI didn't follow rules, validation missed error)

### Don't Create for:
- **Expected behavior** (not a failure)
- **One-off typos** (no systemic learning)
- **Already documented** (duplicate of existing incident)

---

## Severity Levels

| Severity | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| **SEV-1** | Critical - System unusable or security breach | Immediate | Secrets leaked to git, data loss, system crash |
| **SEV-2** | High - Major feature broken or degraded | <24 hours | Validation failing, AI ignoring rules, broken CI/CD |
| **SEV-3** | Medium - Minor feature broken or workaround exists | <1 week | Formatting errors, broken links, minor bugs |
| **SEV-4** | Low - Cosmetic or nice-to-have | <1 month | Typos, style inconsistencies, minor UX issues |
| **SEV-5** | Trivial - No user impact | Backlog | Documentation improvements, refactoring ideas |

---

## How to Create an Incident Report

### Step 1: Create the File

**Location:** `docs/incidents/INCIDENT-[ID]-[short-slug].md`

**ID Format:** `YYYY-MM-DD-NNN` (date + sequence number)

**Example:** `docs/incidents/INCIDENT-2025-11-03-001-secrets-leaked.md`

### Step 2: Fill Out the Template

Copy from `product/templates/INCIDENT_REPORT_template.md` and fill in:

1. **Header** - Date, severity, status, owner, systems, environment
2. **One-line summary** - What failed + why it matters
3. **Hazard statement** - If X, then Y, causing Z
4. **Root cause** - Primary cause + contributing factors
5. **Prevent/Detect/Mitigate** - 3-7 actionable changes
6. **Verification plan** - Tests, alerts, thresholds
7. **Action items** - Owner, due date, links
8. **Re-evaluation date** - When to check effectiveness

### Step 3: Link to Related Documents

- Create GitHub issues for action items
- Update CHANGELOG with fix entries
- Update DEVLOG if architectural decision made
- Create ADR if systemic change required
- Link to epic if part of larger initiative

### Step 4: Track to Resolution

Update status as you progress:
- **Open** → Incident reported, investigation ongoing
- **Mitigated** → Temporary fix deployed, root cause not addressed
- **Resolved** → Permanent fix deployed, action items complete
- **Verified** → Re-evaluation complete, no recurrence

---

## AI vs. Human Triggered Incidents

### AI-Triggered Incidents

**When AI Should Create:**
- AI detects validation failure (e.g., secrets scan fails)
- AI detects it violated a rule (e.g., forgot to update CHANGELOG)
- AI detects systemic issue (e.g., same error occurring repeatedly)

**AI Responsibilities:**
1. Create incident report with all known information
2. Set status to "Open"
3. Assign to human owner for review
4. Suggest action items based on root cause
5. Alert human that incident was created

**Example AI Prompt:**
```
I detected that I committed a DEVLOG entry without updating CHANGELOG, 
violating the log-file-maintenance rule. I've created an incident report:

docs/incidents/INCIDENT-2025-11-03-002-missed-changelog.md

Please review and assign action items.
```

### Human-Triggered Incidents

**When Human Should Create:**
- Discovers issue that AI didn't catch
- Observes pattern of failures
- Near miss or security concern
- Process improvement opportunity

**Human Responsibilities:**
1. Create incident report (or ask AI to create it)
2. Assign owner (self or team member)
3. Define action items with due dates
4. Track to resolution
5. Conduct re-evaluation

---

## Best Practices

### Writing Effective Incident Reports

**DO:**
- ✅ Be specific and factual (not vague or emotional)
- ✅ Focus on systemic improvements (not blame)
- ✅ Include concrete action items (not "be more careful")
- ✅ Set realistic due dates (not "ASAP")
- ✅ Link to evidence (logs, screenshots, commits)

**DON'T:**
- ❌ Blame individuals (focus on process/system)
- ❌ Use vague language ("sometimes fails" → "fails 30% of time")
- ❌ Skip root cause analysis (don't just fix symptoms)
- ❌ Create action items without owners (assign responsibility)
- ❌ Forget to re-evaluate (verify fixes are effective)

### Example: Good vs. Bad

**❌ Bad Incident Report:**
```
# Incident: Something broke

The AI messed up and didn't update the CHANGELOG. We need to be more careful.

Action items:
- Fix it
- Don't let it happen again
```

**✅ Good Incident Report:**
```
# Incident 2025-11-03-001: AI Skipped CHANGELOG Update

**One-line summary:** AI committed code changes without updating CHANGELOG, 
violating log-file-maintenance rule, resulting in incomplete project history.

**Hazard statement:** If AI skips CHANGELOG updates during long sessions, 
then project history becomes incomplete, causing difficulty tracking changes 
and debugging issues.

**Root cause:** AI context window exceeded 100k tokens, causing it to drop 
the log-file-maintenance rule from active context.

**Prevent:**
- Add post-commit verification to AI rules (self-check)
- Create validation script to detect missing CHANGELOG entries
- Reduce rule file size to fit in smaller context window

**Action items:**
- Add self-verification prompt to log-file-maintenance.md (Clark, Nov 5)
- Create validate-logs.sh script (AI Agent, Nov 7)
- Test with 100 commits to verify 100% compliance (Clark, Nov 10)

**Re-evaluation:** 2025-12-03 (30 days after fix)
```

---

## Integration with Other Documents

### CHANGELOG
- **When:** After incident is resolved
- **What:** Document the fix (not the incident)
- **Example:** `- Fixed: Added post-commit verification to prevent missed CHANGELOG updates. Files: .augment/rules/log-file-maintenance.md. Commit: abc123. Incident: INCIDENT-2025-11-03-001`

### DEVLOG
- **When:** If incident reveals architectural decision or milestone
- **What:** Explain WHY the fix was chosen (not just what)
- **Example:** "Situation: AI was skipping CHANGELOG updates in long sessions. Decision: Added self-verification prompts instead of external validation. Why: Self-verification is faster and doesn't require external tools. Result: 100% compliance in testing."

### ADR
- **When:** If incident requires architectural change
- **What:** Document the decision and alternatives considered
- **Example:** ADR-013: Use Self-Verification Instead of External Validation

### GitHub Issues
- **When:** For each action item
- **What:** Track progress and link back to incident
- **Example:** Issue #10: "Add post-commit verification to log-file-maintenance.md (from INCIDENT-2025-11-03-001)"

---

## Incident Report Lifecycle

```
1. Incident Occurs
   ↓
2. Create Report (AI or Human)
   Status: Open
   ↓
3. Investigate Root Cause
   Update report with findings
   ↓
4. Deploy Temporary Fix (if needed)
   Status: Mitigated
   ↓
5. Create Action Items
   Assign owners, due dates
   ↓
6. Deploy Permanent Fix
   Update CHANGELOG, DEVLOG, ADR
   Status: Resolved
   ↓
7. Re-Evaluate (30-90 days)
   Verify effectiveness
   Status: Verified
   ↓
8. Archive (optional)
   Move to docs/incidents/archive/
```

---

## Metrics to Track

### Incident Metrics
- **Incident count by severity** (trend over time)
- **Time to resolution** (Open → Resolved)
- **Recurrence rate** (same incident happening again)
- **Action item completion rate** (% completed on time)

### Learning Metrics
- **Systemic improvements** (# of process changes from incidents)
- **Prevention effectiveness** (% reduction in similar incidents)
- **Detection improvements** (time to detect incidents decreasing)

### Example Dashboard
```
Last 30 Days:
- Total Incidents: 5 (2 SEV-2, 3 SEV-3)
- Avg Time to Resolution: 3.2 days
- Recurrence Rate: 0% (no repeated incidents)
- Action Items Completed: 12/15 (80%)
- Systemic Improvements: 3 (validation script, AI rules, CI/CD)
```

---

## Examples

See `product/examples/incidents/` for sample incident reports:
- `INCIDENT-2025-11-03-001-secrets-leaked.md` - SEV-1 security incident
- `INCIDENT-2025-11-03-002-validation-failed.md` - SEV-2 reliability incident
- `INCIDENT-2025-11-03-003-formatting-error.md` - SEV-3 minor incident

---

## AI Rules for Incident Reports

### When AI Should Create Incident Reports

```markdown
## 🚨 INCIDENT REPORTING - AI RESPONSIBILITIES

**Create incident report if:**
- You detect you violated a rule (e.g., forgot CHANGELOG)
- Validation script fails (e.g., secrets detected, format error)
- Same error occurs 3+ times (pattern detected)
- User reports a bug or issue

**How to create:**
1. Copy template from product/templates/INCIDENT_REPORT_template.md
2. Create file: docs/incidents/INCIDENT-[YYYY-MM-DD-NNN]-[slug].md
3. Fill in all sections with known information
4. Set status to "Open"
5. Assign to human owner
6. Alert user: "I created incident report [link]. Please review."

**Don't:**
- Don't create duplicate incidents (check existing first)
- Don't assign SEV-1/SEV-2 without human confirmation
- Don't mark as "Resolved" without human verification
```

---

## References

- **Template:** [INCIDENT_REPORT_template.md](../templates/INCIDENT_REPORT_template.md)
- **Examples:** `product/examples/incidents/`
- **CHANGELOG:** [../../logs/CHANGELOG.md](../../logs/CHANGELOG.md)
- **DEVLOG:** [../../logs/DEVLOG.md](../../logs/DEVLOG.md)
- **ADR How-To:** [ADR_how_to.md](ADR_how_to.md)

