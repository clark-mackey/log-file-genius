# Epic 13: Validation & Reliability System

**Status:** Not Started  
**Priority:** P0 - CRITICAL (Proves the system works)  
**Estimated Effort:** 2 weeks  
**Dependencies:** Epic 7 (Verification System - builds on existing validation)  
**Source:** Red Team Analysis (context/research/Red Team Analysis_ (REVISED) (1).md)

---

## Epic Goal

Verify that AI assistants reliably maintain logs correctly, with automated validation, self-assessment, and CI/CD integration.

**Problem Statement:** AI assistants are not deterministic. Without validation, the system will silently fail - Claude might forget to update CHANGELOG, Augment might hallucinate incorrect entries, or files might not be committed. Users will discover weeks later that their logs have gaps or errors.

**Inspiration:** Red Team Analysis identified this as "Critical Failure #2" - AI reliability is unproven without validation.

---

## Success Criteria

- [ ] Every commit triggers automated validation
- [ ] AI assistants self-verify their work after commits
- [ ] CI/CD catches validation failures before merge
- [ ] Clear error messages with fix suggestions
- [ ] 95%+ of commits pass validation on first try
- [ ] Validation works across all supported AI assistants (Claude, Augment, Cursor, Copilot)

---

## Task List

### Task 13.1: Build Log Linter (lint-logs.py)
- [ ] Create `product/scripts/lint-logs.py`
- [ ] Validate CHANGELOG format:
  - Frontmatter exists and is correct
  - Entries follow "- Description. Files: `path`. Commit: `hash`" format
  - Dates are in correct format
  - No duplicate entries
- [ ] Validate DEVLOG format:
  - Frontmatter exists
  - Entries follow Situation/Challenge/Decision/Why/Result format
  - Cross-links are valid (no broken links)
  - Dates are consistent
- [ ] Validate token budgets:
  - CHANGELOG < profile target
  - DEVLOG < profile target
  - Combined < profile target
- [ ] Return clear error messages with line numbers and fix suggestions

### Task 13.2: Add Post-Commit Verification to AI Rules
- [ ] Update `log-file-maintenance.md` with post-commit verification section
- [ ] AI must verify after every commit:
  - Read git diff of CHANGELOG.md
  - Verify entry matches actual code changes
  - Confirm files changed match CHANGELOG entry
  - Self-assess accuracy
- [ ] Add verification checklist format:
  ```
  ✅ Commit: [hash]
  ✅ CHANGELOG entry: [quote entry]
  ✅ Files changed: [list files]
  ✅ Entry accuracy: [self-assessment]
  ✅ DEVLOG updated: [yes/no - reason]
  ```
- [ ] Update both starter packs with verification rules

### Task 13.3: Create GitHub Actions Workflow
- [ ] Create `.github/workflows/validate-logs.yml`
- [ ] Run on every pull request
- [ ] Execute validation steps:
  - Run `lint-logs.py`
  - Run `detect-secrets.sh` (from Epic 12)
  - Check token budgets
  - Validate cross-links
- [ ] Post validation results as PR comment
- [ ] Block merge if validation fails (configurable)

### Task 13.4: Add Validation Dashboard/Report
- [ ] Create `product/scripts/validation-report.py`
- [ ] Generate validation report:
  - Overall health score
  - Token budget status
  - Recent validation failures
  - Trends over time
- [ ] Output as Markdown or HTML
- [ ] Integrate with GitHub Actions (post as PR comment)

### Task 13.5: Create Validation Examples
- [ ] Create `product/examples/validation/` directory
- [ ] Add valid CHANGELOG example
- [ ] Add invalid CHANGELOG examples (missing commit hash, wrong format, etc.)
- [ ] Add valid DEVLOG example
- [ ] Add invalid DEVLOG examples (missing sections, broken links, etc.)
- [ ] Add test cases for linter

### Task 13.6: Update Validation Guide
- [ ] Update `product/docs/validation-guide.md`
- [ ] Add linter documentation
- [ ] Add post-commit verification guide
- [ ] Add GitHub Actions setup instructions
- [ ] Add troubleshooting section
- [ ] Add examples of common validation errors and fixes

### Task 13.7: Add Self-Assessment Prompts for AI
- [ ] Create self-assessment questions for AI:
  - "Did I update CHANGELOG.md?"
  - "Does the entry match the code changes?"
  - "Did I include the planning files in the commit?"
  - "Are the file paths correct?"
  - "Did I update DEVLOG if this was a milestone?"
- [ ] Add to AI rules as mandatory checklist
- [ ] Test with different AI assistants

### Task 13.8: Create Validation Metrics
- [ ] Track validation metrics:
  - Validation pass rate
  - Common validation errors
  - Time to fix validation errors
  - Token budget trends
- [ ] Create metrics dashboard (optional)
- [ ] Document metrics in validation guide

### Task 13.9: Update Starter Packs
- [ ] Add `lint-logs.py` to both starter packs
- [ ] Add GitHub Actions workflow to both starter packs
- [ ] Update pre-commit hooks to run linter
- [ ] Update READMEs with validation setup
- [ ] Add validation examples

### Task 13.10: Test Validation System
- [ ] Test with all supported AI assistants (Claude, Augment, Cursor, Copilot)
- [ ] Test with intentionally broken logs
- [ ] Test GitHub Actions workflow
- [ ] Test self-assessment prompts
- [ ] Measure validation pass rate
- [ ] Document test results

---

## Deliverables

1. **Linter:**
   - `product/scripts/lint-logs.py`
   - `product/scripts/validation-report.py`

2. **GitHub Actions:**
   - `.github/workflows/validate-logs.yml`

3. **AI Rules:**
   - Updated `log-file-maintenance.md` with post-commit verification
   - Self-assessment checklist

4. **Documentation:**
   - Updated `product/docs/validation-guide.md`
   - Troubleshooting guide

5. **Examples:**
   - `product/examples/validation/` with valid/invalid examples

6. **Starter Pack Integration:**
   - Linter and workflows in both starter packs
   - Updated READMEs

---

## Technical Notes

### Validation Checks

**CHANGELOG Validation:**
- Frontmatter exists (version, date)
- Entries follow format: `- Description. Files: \`path\`. Commit: \`hash\``
- Commit hashes are valid (7+ characters)
- File paths exist in repository
- No duplicate entries
- Dates are in YYYY-MM-DD format
- Token count < profile target

**DEVLOG Validation:**
- Frontmatter exists (Current Context section)
- Entries follow Situation/Challenge/Decision/Why/Result format
- Cross-links are valid (no 404s)
- Dates are consistent
- Token count < profile target
- Combined CHANGELOG + DEVLOG < profile target

**Cross-Link Validation:**
- Links to CHANGELOG entries exist
- Links to DEVLOG entries exist
- Links to ADRs exist
- External links are valid (optional, can be slow)

### Self-Assessment Checklist

AI assistants must answer these questions after every commit:

1. ✅ Did I update CHANGELOG.md? (yes/no)
2. ✅ Does the CHANGELOG entry match the code changes? (yes/no/unsure)
3. ✅ Did I include planning files in the commit? (yes/no)
4. ✅ Are the file paths in the CHANGELOG entry correct? (yes/no)
5. ✅ Did I update DEVLOG if this was a milestone? (yes/no/not-applicable)
6. ✅ Did I run validation? (yes/no)

If any answer is "no" or "unsure", AI must fix before proceeding.

---

## Testing Strategy

1. **Linter Testing:** Test with 50+ valid/invalid log examples
2. **AI Testing:** Test with Claude, Augment, Cursor, Copilot
3. **Integration Testing:** Test GitHub Actions workflow
4. **Self-Assessment Testing:** Verify AI follows checklist
5. **Metrics Testing:** Track validation pass rate over 100 commits

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| AI ignores self-assessment checklist | Critical | Make it mandatory, test extensively, improve prompts |
| Linter has false positives | Medium | Improve patterns, allow overrides, gather feedback |
| GitHub Actions too slow | Low | Optimize validation, cache dependencies |
| Validation too strict for users | Medium | Make configurable via profiles, provide clear errors |

---

## Dependencies

- Epic 7 (Verification System) - Builds on existing validation scripts
- Epic 8 (Profile System) - Uses profile-specific token targets
- Epic 12 (Security) - Integrates secrets detection into validation

---

## Notes

**Why This is P0 Critical:**

From Red Team Analysis:
> "Without validation, this system will silently fail. Users will discover weeks later that their CHANGELOG has gaps or incorrect entries."

This epic proves that the AI-maintained log system actually works reliably. Without it, users can't trust the system.

**Target Users:**
- Solo developers who need reliable documentation
- Teams who need consistent logs across developers
- Anyone who wants to validate before sharing with others

**Success Metric:**
95%+ validation pass rate after 100 commits with AI assistants.

