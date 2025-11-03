# Incident [ID]: [Short title]

**Date:** [YYYY-MM-DD]  
**Severity:** [SEV-1 | SEV-2 | SEV-3 | SEV-4 | SEV-5]  
**Status:** [Open | Mitigated | Resolved | Verified]  
**Owner:** [Name or AI Agent]  
**Systems:** [Service A, Tool B, Component C]  
**Environment:** [Production | Staging | Development | Local]

---

## 1. One-Line Summary

[What failed + why it matters]

**Example:** "Secrets detection script failed to catch API key in DEVLOG, resulting in credential leak to git history."

---

## 2. Hazard Statement

**If** [triggering condition],  
**Then** [failure mode],  
**Causing** [impact to users/system/business].

**Example:**  
**If** the secrets detection regex doesn't match all API key formats,  
**Then** credentials can be committed to CHANGELOG/DEVLOG,  
**Causing** security incidents and potential data breaches.

---

## 3. Root Cause Analysis

### Primary Cause
[The fundamental reason this incident occurred]

**Example:** "Secrets detection script only checked for patterns like `api_key=XXX` but missed `apiKey: "XXX"` format used in YAML examples."

### Contributing Factors
- [Factor 1: e.g., Insufficient test coverage]
- [Factor 2: e.g., No validation in CI/CD]
- [Factor 3: e.g., AI assistant not aware of all secret formats]

---

## 4. Prevent/Detect/Mitigate Changes

### Prevent (Stop it from happening)
- [ ] [Action to prevent recurrence]
- [ ] [Action to prevent recurrence]

### Detect (Catch it early)
- [ ] [Monitoring/alerting to detect similar issues]
- [ ] [Validation to catch before impact]

### Mitigate (Reduce impact if it happens)
- [ ] [Fallback or graceful degradation]
- [ ] [Faster recovery procedure]

**Example:**
### Prevent
- [ ] Expand secrets detection regex to cover YAML, JSON, TOML formats
- [ ] Add test cases for all common secret formats (20+ patterns)

### Detect
- [ ] Add GitHub Actions workflow to run secrets scan on every PR
- [ ] Create dashboard showing secrets scan results over time

### Mitigate
- [ ] Document rollback procedure for leaked secrets
- [ ] Create script to automatically redact secrets from git history

---

## 5. Verification Plan

### Tests
- [ ] [Test case 1: e.g., "Secrets scan catches YAML API keys"]
- [ ] [Test case 2: e.g., "CI/CD fails on secret detection"]

### Alerts/Dashboards
- [ ] [Monitoring setup: e.g., "Alert if secrets scan fails"]
- [ ] [Dashboard: e.g., "Secrets scan pass rate >99%"]

### Thresholds
- **Success Criteria:** [e.g., "Zero secrets leaked in 1000 test commits"]
- **Acceptable Performance:** [e.g., "False positive rate <5%"]
- **Alert Threshold:** [e.g., "Alert if >1 secret detected per week"]

**Example:**
### Tests
- [ ] Test secrets scan with 50 different API key formats
- [ ] Test CI/CD workflow blocks commits with secrets

### Alerts/Dashboards
- [ ] GitHub Actions sends Slack alert on secrets detection
- [ ] Weekly report shows secrets scan pass rate

### Thresholds
- **Success:** Zero secrets leaked in production for 30 days
- **Acceptable:** False positive rate <5% (doesn't block legitimate content)
- **Alert:** Immediate alert if any secret detected in main branch

---

## 6. Action Items

| Action | Owner | Due Date | Status | Link |
|--------|-------|----------|--------|------|
| [Action 1] | [Name] | [YYYY-MM-DD] | [Open/Done] | [GitHub Issue #X] |
| [Action 2] | [Name] | [YYYY-MM-DD] | [Open/Done] | [GitHub Issue #X] |
| [Action 3] | [Name] | [YYYY-MM-DD] | [Open/Done] | [GitHub Issue #X] |

**Example:**
| Action | Owner | Due Date | Status | Link |
|--------|-------|----------|--------|------|
| Expand secrets regex to cover YAML/JSON | Clark | 2025-11-10 | Open | [Issue #5](link) |
| Add 50 test cases for secret formats | AI Agent | 2025-11-12 | Open | [Issue #6](link) |
| Create GitHub Actions workflow | Clark | 2025-11-15 | Open | [Issue #7](link) |
| Document rollback procedure | AI Agent | 2025-11-17 | Open | [Epic 15](link) |

---

## 7. Re-Evaluation Date

**Date:** [YYYY-MM-DD] (typically 30-90 days after resolution)

**Purpose:** Verify that implemented changes are effective and no similar incidents have occurred.

**Checklist:**
- [ ] Review metrics: Have similar incidents occurred?
- [ ] Review tests: Are they still passing?
- [ ] Review alerts: Are they triggering appropriately?
- [ ] Review action items: Are all completed?
- [ ] Update status to "Verified" if all checks pass

**Example:**  
**Date:** 2025-12-15 (30 days after Epic 12 completion)

**Checklist:**
- [ ] Zero secrets leaked in 30 days of production use
- [ ] Secrets scan pass rate >99%
- [ ] All 50 test cases passing
- [ ] GitHub Actions workflow running on every PR
- [ ] Rollback procedure documented and tested

---

## Timeline

| Date | Event | Status |
|------|-------|--------|
| [YYYY-MM-DD] | Incident discovered | - |
| [YYYY-MM-DD] | Incident reported (this document created) | Open |
| [YYYY-MM-DD] | Root cause identified | - |
| [YYYY-MM-DD] | Mitigation deployed | Mitigated |
| [YYYY-MM-DD] | Permanent fix deployed | Resolved |
| [YYYY-MM-DD] | Verification complete | Verified |

---

## Related Documents

- **CHANGELOG:** [Link to CHANGELOG entry documenting the fix]
- **DEVLOG:** [Link to DEVLOG entry explaining the decision]
- **ADR:** [Link to ADR if architectural decision was made]
- **GitHub Issues:** [Links to related issues]
- **Epic:** [Link to epic if part of larger initiative]

---

## Lessons Learned

### What Went Well
- [Positive aspect 1]
- [Positive aspect 2]

### What Could Be Improved
- [Improvement area 1]
- [Improvement area 2]

### Systemic Issues Identified
- [Pattern or systemic issue that this incident revealed]

**Example:**
### What Went Well
- Incident was caught during testing, not in production
- Team responded quickly with temporary mitigation

### What Could Be Improved
- Test coverage should have caught this before manual testing
- Secrets detection should be in CI/CD, not just pre-commit hook

### Systemic Issues Identified
- Lack of comprehensive test suite for security features
- No automated validation in CI/CD pipeline
- AI assistants need better security training/rules

---

## Notes

[Any additional context, links, or information that doesn't fit above categories]

**Example:**
- This incident was discovered during Epic 12 development
- Similar incident occurred in competing repository (link to analysis)
- Red Team Analysis predicted this exact failure mode (link to report)
- Recommended reading: "Secrets in Git History" (link)

