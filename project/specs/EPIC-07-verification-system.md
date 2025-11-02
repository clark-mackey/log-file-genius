# Epic 7: Verification & Validation System

**Status:** In Progress  
**Priority:** High  
**Estimated Effort:** 1-2 weeks

---

## Goal

Provide automated validation tools that enforce log file format, completeness, and token limits, making the rules enforced rather than suggested.

---

## Task List

- [ ] **Task 7.1:** Design validation architecture
- [ ] **Task 7.2:** Create master validation script (`scripts/validate-log-files.sh` or `.ps1`)
- [ ] **Task 7.3:** Implement CHANGELOG format validation
- [ ] **Task 7.4:** Implement DEVLOG format validation
- [ ] **Task 7.5:** Implement token count validation
- [ ] **Task 7.6:** Create git pre-commit hook template
- [ ] **Task 7.7:** Create validation documentation (`docs/validation-guide.md`)
- [ ] **Task 7.8:** Create validation examples (valid/invalid)
- [ ] **Task 7.9:** Update starter packs with validation scripts
- [ ] **Task 7.10:** Update rules to reference validation

---

## Success Criteria

- [ ] Validation script checks CHANGELOG format, DEVLOG format, and token counts
- [ ] Optional git pre-commit hook available
- [ ] Clear error messages and fix suggestions provided
- [ ] 90%+ of commits pass validation on first try (after adoption)
- [ ] System remains modular and optional

---

## Deliverables

1. **Validation Scripts:** `scripts/validate-log-files.sh` (or .ps1)
2. **Git Hook:** `.git-hooks/pre-commit` template
3. **Documentation:** `docs/validation-guide.md`
4. **Examples:** Valid and invalid examples
5. **Starter Pack Integration:** Scripts in both starter packs

