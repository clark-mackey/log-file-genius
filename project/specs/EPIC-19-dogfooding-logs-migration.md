# Epic 19: Dogfooding Migration to /logs/ Structure

**Status:** Proposed
**Priority:** P1 (High - Dogfooding Integrity)
**Effort:** Small (2-3 hours)
**Dependencies:** None
**Related ADR:** ADR-014 (Dogfooding Compliance)

---

## Problem Statement

The Log File Genius project is NOT using its own /logs/ folder structure for dogfooding. This creates:
- **Credibility gap** - "Do as I say, not as I do"
- **Testing gap** - Not experiencing the same UX as users
- **Missing features** - No update tracking, validation doesn't work
- **Documentation mismatch** - AI rules reference /logs/ but we use project/planning/

**Current state:** `project/planning/CHANGELOG.md`, `project/adr/*.md`
**Required state:** `logs/CHANGELOG.md`, `logs/adr/*.md` (per ADR-012)

---

## Goals

1. **Migrate to /logs/ structure** - Move all log files to /logs/ folder
2. **Enable update tracking** - Create .logfile-config.yml
3. **Fix AI rules** - Ensure rules reference correct paths
4. **Update cross-references** - Fix all links in specs, ADRs, workflow docs
5. **Clean up main branch** - Remove leftover project/docs/github-actions-ci.md

---

## Non-Goals

- Changing the structure of project/specs/, project/qa/, project/research/ (these stay)
- Modifying main branch structure (only cleanup of one leftover file)
- Changing the product/ distribution structure

---

## Success Criteria

1. ✅ All log files in `/logs/` directory (CHANGELOG, DEVLOG, ADRs)
2. ✅ `.logfile-config.yml` exists and is valid
3. ✅ Validation scripts run successfully on our own logs
4. ✅ AI rules reference correct paths and work properly
5. ✅ Update tracking detects new versions
6. ✅ All cross-references updated (no broken links)
7. ✅ Main branch cleaned up
8. ✅ Git history preserved (using git mv)

---

## Tasks

### Task 1: Create /logs/ Structure
**Effort:** 15 minutes

**Actions:**
1. Create `logs/` directory in root
2. Create `logs/adr/` subdirectory
3. Move files using `git mv` to preserve history:
   ```bash
   git mv project/planning/CHANGELOG.md logs/CHANGELOG.md
   git mv project/planning/DEVLOG.md logs/DEVLOG.md
   git mv project/adr logs/adr
   ```
4. Delete empty directories:
   ```bash
   git rm -r project/planning
   ```

**Verification:**
- [ ] `logs/CHANGELOG.md` exists
- [ ] `logs/DEVLOG.md` exists
- [ ] `logs/adr/*.md` exists (all ADRs migrated)
- [ ] `project/planning/` directory deleted
- [ ] Git history preserved (check with `git log --follow logs/CHANGELOG.md`)

---

### Task 2: Create .logfile-config.yml
**Effort:** 15 minutes

**Actions:**
1. Copy template from `product/templates/.logfile-config.yml`
2. Customize for this project:
   ```yaml
   version: "0.1.0-dev"
   profile: "solo-developer"
   
   paths:
     changelog: "logs/CHANGELOG.md"
     devlog: "logs/DEVLOG.md"
     state: "logs/STATE.md"
     adr: "logs/adr"
   
   related_docs:
     prd: "project/specs/prd.md"
     architecture: "project/architecture.md"
   ```
3. Commit to development branch

**Verification:**
- [ ] `.logfile-config.yml` exists in root
- [ ] Version matches current version (v0.1.0-dev)
- [ ] Profile is solo-developer
- [ ] Paths point to logs/ directory

---

### Task 3: Update Cross-References
**Effort:** 45 minutes

**Files to update:**

**Specs (project/specs/):**
- [ ] `ROADMAP-REVISED-2025-11.md` - Update any references to planning/
- [ ] `DEFINITION-OF-DONE.md` - Update any references to planning/
- [ ] `ROADMAP-TRACEABILITY.md` - Update any references to planning/
- [ ] `prd.md` - Update any references to planning/
- [ ] All EPIC-*.md files - Update any references to planning/ or adr/

**Workflow:**
- [ ] `project/WORKFLOW.md` - Update all references to planning/ and adr/

**Root docs:**
- [ ] `README.md` - Check for any references to planning/ or adr/
- [ ] `CONTRIBUTING.md` - Check for any references to planning/ or adr/

**AI Rules:**
- [ ] `.augment/rules/project-identity.md` - Update if it references paths

**Search command:**
```bash
# Find all references to old paths
grep -r "project/planning" project/specs/
grep -r "project/adr" project/specs/
grep -r "project/planning" project/WORKFLOW.md
grep -r "project/planning" README.md
```

**Verification:**
- [ ] No broken links in any documentation
- [ ] All references point to logs/ instead of project/planning/
- [ ] All references point to logs/adr/ instead of project/adr/

---

### Task 4: Update AI Rules
**Effort:** 15 minutes

**Actions:**
1. Check `.augment/rules/log-file-maintenance.md` - Should already reference logs/
2. Check `.augment/rules/project-identity.md` - Update if needed
3. Verify rules work correctly with new structure

**Verification:**
- [ ] AI rules reference logs/ paths
- [ ] Rules don't reference project/planning/ or project/adr/
- [ ] Test by asking AI to update CHANGELOG (should work correctly)

---

### Task 5: Test Validation Scripts
**Effort:** 15 minutes

**Actions:**
1. Run validation script:
   ```bash
   .\.log-file-genius\scripts\validate-log-files.ps1  # Windows
   ./.log-file-genius/scripts/validate-log-files.sh   # Mac/Linux
   ```
2. Verify it reads .logfile-config.yml correctly
3. Verify it validates logs/CHANGELOG.md and logs/DEVLOG.md
4. Fix any issues discovered

**Verification:**
- [ ] Validation script runs without errors
- [ ] Script reads .logfile-config.yml
- [ ] Script validates CHANGELOG format
- [ ] Script validates DEVLOG format
- [ ] Script shows token counts

---

### Task 6: Test Update Tracking
**Effort:** 15 minutes

**Actions:**
1. Verify .logfile-config.yml has version field
2. Test update notification (may need to temporarily change version)
3. Verify validation script shows update notification if available

**Verification:**
- [ ] Version tracking works
- [ ] Update notifications appear when new version available
- [ ] Can manually check for updates

---

### Task 7: Clean Up Main Branch
**Effort:** 15 minutes

**Actions:**
1. Switch to main branch
2. Remove `project/docs/github-actions-ci.md` (leftover file)
3. Commit and push
4. Switch back to development branch

**Verification:**
- [ ] Main branch has no project/ directory (except if needed for distribution)
- [ ] Main branch structure is clean (only product/, .augment/, .git-hooks/, .github/)

---

### Task 8: Update CHANGELOG and DEVLOG
**Effort:** 15 minutes

**Actions:**
1. Add entry to logs/CHANGELOG.md (new location):
   ```markdown
   ### Changed
   - Dogfooding migration to /logs/ structure - Migrated development branch to use /logs/ folder structure per ADR-012. Moved CHANGELOG.md, DEVLOG.md, and all ADRs from project/planning/ and project/adr/ to logs/. Created .logfile-config.yml for update tracking and validation. Updated all cross-references in specs, workflow docs, and AI rules. This ensures we dogfood the same structure we distribute to users. Files: `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/adr/*.md`, `.logfile-config.yml`, all cross-references. Commit: `pending`
   ```

2. Add entry to logs/DEVLOG.md (if significant milestone):
   ```markdown
   ## 2025-11-10 - Dogfooding Migration to /logs/ Structure
   
   **Situation:** Discovered we weren't using our own /logs/ folder structure for dogfooding.
   
   **Challenge:** Project used project/planning/ for logs, violating ADR-012. No .logfile-config.yml meant no update tracking or validation.
   
   **Decision:** Migrated development branch to /logs/ structure. Created .logfile-config.yml. Updated all cross-references.
   
   **Why:** Dogfooding integrity is critical. Can't identify UX issues if we don't use our own system. "Do as I say, not as I do" undermines credibility.
   
   **Result:** Now using same structure we distribute. Validation works. Update tracking enabled. All cross-references updated.
   
   **Files:** logs/CHANGELOG.md, logs/DEVLOG.md, logs/adr/*.md, .logfile-config.yml, project/specs/*.md, project/WORKFLOW.md
   ```

**Verification:**
- [ ] CHANGELOG entry added
- [ ] DEVLOG entry added (if milestone)
- [ ] Entries reference correct commit hash

---

## Timeline

**Total effort:** 2-3 hours

**Suggested approach:**
1. Complete all tasks in one session to avoid partial state
2. Test thoroughly before committing
3. Commit all changes together with descriptive message
4. Push to development branch
5. Verify everything works

---

## Risks and Mitigations

**Risk 1: Broken cross-references**
- **Mitigation:** Use grep to find all references before updating
- **Mitigation:** Test all links after migration

**Risk 2: Git history loss**
- **Mitigation:** Use `git mv` instead of manual move
- **Mitigation:** Verify with `git log --follow` after migration

**Risk 3: Validation scripts don't work**
- **Mitigation:** Test validation before committing
- **Mitigation:** Fix any issues discovered during testing

**Risk 4: AI rules reference wrong paths**
- **Mitigation:** Review all AI rules after migration
- **Mitigation:** Test by asking AI to update CHANGELOG

---

## Definition of Done

- [ ] All tasks completed
- [ ] All verification steps passed
- [ ] No broken links in documentation
- [ ] Validation scripts run successfully
- [ ] AI rules work correctly
- [ ] Update tracking works
- [ ] CHANGELOG and DEVLOG updated
- [ ] Changes committed and pushed to development branch
- [ ] Main branch cleaned up
- [ ] This epic marked as complete in DEVLOG

---

## Notes

- This only affects the development branch (per ADR-009)
- Main branch only needs cleanup of one leftover file
- This is a one-time migration with long-term benefits
- Enables us to properly dogfood our own system

