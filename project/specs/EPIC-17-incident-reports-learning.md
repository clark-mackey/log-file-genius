# Epic 17: Incident Reports & Learning System

**Priority:** P1 - HIGH  
**Estimated Effort:** 3-5 days  
**Dependencies:** Epic 12 (Security), Epic 13 (Validation)  
**Status:** Planned  
**Owner:** TBD

---

## Overview

Create a structured incident reporting system that enables both humans and AI agents to document failures, learn from them, and implement systemic improvements. Incident reports catalog the past but focus on preventing future failures.

---

## Problem Statement

Currently, Log File Genius has:
- ✅ CHANGELOG (what changed)
- ✅ DEVLOG (why we decided)
- ✅ ADRs (architectural decisions)

But lacks:
- ❌ **Incident Reports** (what went wrong + how to prevent it)
- ❌ **Learning system** (capturing lessons from failures)
- ❌ **AI-triggered incident detection** (AI reports its own failures)
- ❌ **Verification framework** (ensuring fixes are effective)

**Result:** Failures are fixed reactively but not systematically prevented. No structured learning from mistakes.

---

## Goals

### Primary Goals
1. **Enable structured incident reporting** for both humans and AI
2. **Capture lessons learned** from failures to prevent recurrence
3. **Integrate with existing documentation** (CHANGELOG, DEVLOG, ADRs)
4. **Support AI-triggered incidents** (AI detects and reports its own failures)

### Success Criteria
- [ ] Incident report template created and documented
- [ ] How-to guide published with examples
- [ ] AI rules updated to create incident reports automatically
- [ ] At least 3 example incidents documented
- [ ] Integration with CHANGELOG/DEVLOG/ADR workflows
- [ ] Verification framework for tracking effectiveness

---

## User Stories

### Story 1: Human Creates Incident Report
**As a** developer,  
**I want to** document a failure with root cause and prevention steps,  
**So that** we can learn from mistakes and prevent recurrence.

**Acceptance Criteria:**
- [x] Template available in `project/templates/INCIDENT_REPORT_template.md`
- [x] How-to guide explains when and how to create reports
- [ ] Example incidents demonstrate best practices
- [ ] Clear severity levels (SEV-1 to SEV-5)
- [ ] Action items tracked with owners and due dates

### Story 2: AI Detects and Reports Incident
**As an** AI assistant,  
**I want to** automatically create incident reports when I detect failures,  
**So that** humans are alerted and systemic improvements can be made.

**Acceptance Criteria:**
- [ ] AI rules define when to create incident reports
- [ ] AI can detect rule violations (e.g., forgot CHANGELOG)
- [ ] AI can detect validation failures (e.g., secrets detected)
- [ ] AI creates report and alerts human owner
- [ ] AI suggests action items based on root cause

### Story 3: Track Incident to Resolution
**As a** project owner,  
**I want to** track incidents from detection to verification,  
**So that** I can ensure fixes are effective and no recurrence.

**Acceptance Criteria:**
- [ ] Clear status progression (Open → Mitigated → Resolved → Verified)
- [ ] Action items linked to GitHub issues
- [ ] Re-evaluation date set for verification
- [ ] Metrics tracked (time to resolution, recurrence rate)
- [ ] Integration with CHANGELOG/DEVLOG for fixes

### Story 4: Learn from Patterns
**As a** developer,  
**I want to** identify patterns across multiple incidents,  
**So that** I can address systemic issues, not just symptoms.

**Acceptance Criteria:**
- [ ] Incidents categorized by type (security, validation, process)
- [ ] Lessons learned section captures insights
- [ ] Systemic issues identified and tracked
- [ ] Metrics show improvement over time
- [ ] Recommendations for process improvements

---

## Technical Design

### File Structure

```
docs/incidents/
├── README.md                           # Index of all incidents
├── INCIDENT-2025-11-03-001-secrets-leaked.md
├── INCIDENT-2025-11-03-002-validation-failed.md
└── archive/                            # Resolved incidents >90 days old
    └── INCIDENT-2025-08-01-001-*.md

project/templates/
└── INCIDENT_REPORT_template.md         # Template (WIP, moves to product/ when Epic 17 complete)

project/docs/
└── incident-report-how-to.md           # How-to guide (WIP, moves to product/ when Epic 17 complete)

product/examples/incidents/
├── INCIDENT-2025-11-03-001-secrets-leaked.md    # SEV-1 example
├── INCIDENT-2025-11-03-002-validation-failed.md # SEV-2 example
└── INCIDENT-2025-11-03-003-formatting-error.md  # SEV-3 example
```

### Incident Report Format

```markdown
# Incident [ID]: [Short title]
Date: [YYYY-MM-DD]  Severity: [SEV-1..5]  Status: [Open|Mitigated|Resolved|Verified]
Owner: [Name]  Systems: [Service A, Tool B]  Env: [Prod|Staging]

1) One-line summary (what failed + why it matters)
2) Hazard statement (If X, then Y, causing Z impact)
3) Primary cause + top contributing factor(s)
4) Prevent/Detect/Mitigate changes (bulleted; 3–7 items)
5) Verification plan (tests/alerts/dashboards + thresholds)
6) Action items (Owner, Due, Link)
7) Re-evaluation date (check effectiveness)
```

### Severity Levels

| Severity | Impact | Response Time | Examples |
|----------|--------|---------------|----------|
| SEV-1 | Critical - Security breach or data loss | Immediate | Secrets leaked, data loss |
| SEV-2 | High - Major feature broken | <24 hours | Validation failing, AI ignoring rules |
| SEV-3 | Medium - Minor feature broken | <1 week | Formatting errors, broken links |
| SEV-4 | Low - Cosmetic issues | <1 month | Typos, style inconsistencies |
| SEV-5 | Trivial - No user impact | Backlog | Documentation improvements |

### Integration Points

**CHANGELOG:**
- Document fixes with link to incident report
- Format: `- Fixed: [description]. Incident: INCIDENT-YYYY-MM-DD-NNN`

**DEVLOG:**
- Explain WHY fix was chosen (if architectural decision)
- Link to incident report for context

**ADR:**
- Create ADR if incident requires architectural change
- Link ADR to incident report

**GitHub Issues:**
- Create issue for each action item
- Link issue to incident report

---

## Tasks

### Task 1: Create Templates and Documentation (1 day)
- [x] Create `project/templates/INCIDENT_REPORT_template.md` (WIP, moves to product/ when complete)
- [x] Create `project/docs/incident-report-how-to.md` (WIP, moves to product/ when complete)
- [ ] Create `docs/incidents/README.md` (index)
- [ ] Update `product/docs/README.md` to reference incident reports

### Task 2: Create Example Incidents (1 day)
- [ ] Create SEV-1 example (secrets leaked)
- [ ] Create SEV-2 example (validation failed)
- [ ] Create SEV-3 example (formatting error)
- [ ] Place in `product/examples/incidents/`

### Task 3: Update AI Rules (1 day)
- [ ] Add incident reporting section to `log-file-maintenance.md`
- [ ] Define when AI should create incidents
- [ ] Define how AI should fill out template
- [ ] Add self-detection prompts (AI checks for rule violations)
- [ ] Test with 10 scenarios (AI creates incidents correctly)

### Task 4: Integration with Existing Workflows (1 day)
- [ ] Update CHANGELOG template to reference incidents
- [ ] Update DEVLOG template to reference incidents
- [ ] Update ADR template to reference incidents
- [ ] Create GitHub issue template for incident action items
- [ ] Document integration in how-to guide

### Task 5: Verification Framework (1 day)
- [ ] Create metrics tracking template
- [ ] Define re-evaluation checklist
- [ ] Create dashboard/report template (optional)
- [ ] Document verification process in how-to guide
- [ ] Test with 3 example incidents

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI creates too many incidents (noise) | Medium | Define clear thresholds, severity levels |
| Incidents not tracked to resolution | High | Add to Definition of Done, track in DEVLOG |
| Duplicate incidents created | Low | AI checks existing incidents before creating |
| Incident reports become stale | Medium | Re-evaluation dates, archival process |
| Too much overhead for small teams | Medium | Keep format simple, make optional for SEV-4/5 |

---

## Success Metrics

### Adoption Metrics
- **Incident reports created:** Target 5+ in first month
- **AI-triggered incidents:** Target 30% of total incidents
- **Action items completed:** Target 90% on time

### Learning Metrics
- **Recurrence rate:** Target <10% (same incident type)
- **Time to resolution:** Target <7 days for SEV-2, <24h for SEV-1
- **Systemic improvements:** Target 3+ process changes from incidents

### Quality Metrics
- **Verification completion:** Target 100% of incidents re-evaluated
- **Action item tracking:** Target 100% linked to GitHub issues
- **Documentation quality:** Target 90% of incidents have clear root cause

---

## Timeline

**Total Effort:** 3-5 days

**Week 1:**
- Day 1: Templates and documentation (Task 1)
- Day 2: Example incidents (Task 2)
- Day 3: AI rules update (Task 3)

**Week 2:**
- Day 4: Integration with workflows (Task 4)
- Day 5: Verification framework (Task 5)

**Recommended Placement:** After Epic 13 (Validation), before or alongside Epic 15 (Governance)

---

## Dependencies

### Requires (Must Complete First)
- **Epic 12 (Security):** Provides examples of SEV-1 incidents (secrets leaked)
- **Epic 13 (Validation):** Provides examples of SEV-2 incidents (validation failed)

### Enables (Unlocks These)
- **Epic 15 (Governance):** Incident reports support human-in-the-loop review
- **Epic 14 (RAG):** Incident reports can be indexed for semantic search
- **Future Epics:** Learning from incidents informs future priorities

### Complements (Works Well With)
- **Epic 15 (Governance):** Both focus on review and learning
- **Dogfooding (Week 6):** Incident reports capture dogfooding issues

---

## Open Questions

1. **Should incidents be public or private?**
   - Recommendation: Public by default (in git), redact sensitive info
   - Rationale: Transparency builds trust, helps community learn

2. **Should AI auto-resolve incidents?**
   - Recommendation: No, always require human verification
   - Rationale: Prevents AI from hiding failures

3. **How to handle incidents across multiple repos?**
   - Recommendation: Each repo has its own incidents, link if related
   - Rationale: Keeps incidents local to project context

4. **Should incidents trigger alerts (Slack, email)?**
   - Recommendation: Optional, configure per severity level
   - Rationale: SEV-1/2 may need immediate attention, SEV-3+ can wait

---

## References

- **Template:** [INCIDENT_REPORT_template.md](../templates/INCIDENT_REPORT_template.md)
- **How-To:** [incident-report-how-to.md](../docs/incident-report-how-to.md)
- **Examples:** `product/examples/incidents/` (to be created)
- **Related Epics:** Epic 12 (Security), Epic 13 (Validation), Epic 15 (Governance)

