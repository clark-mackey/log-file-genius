# ADR-014: Dogfooding Compliance - Migrate Development Branch to /logs/ Structure

**Status:** Proposed
**Date:** 2025-11-10
**Deciders:** Clark Mackey
**Related:** ADR-012 (Single /logs/ Folder), ADR-009 (Two-Branch Strategy), ADR-008 (Product/Project Separation)

---

## Context

**Problem:** The Log File Genius project is NOT using its own /logs/ folder structure for dogfooding.

### Current State (Development Branch)
```
project/
  planning/
    ├── CHANGELOG.md
    └── DEVLOG.md
  adr/
    └── *.md
  specs/
  qa/
  research/
  templates/
```

### Required State (Per ADR-012)
```
logs/
  ├── CHANGELOG.md
  ├── DEVLOG.md
  └── adr/
      └── *.md
project/
  specs/
  qa/
  research/
  templates/
```

### The Dogfooding Failure

**ADR-012 states:** "Consolidate all log files into a single `/logs/` folder in the project root."

**Reality:** This project uses `project/planning/` for CHANGELOG/DEVLOG and `project/adr/` for ADRs.

**Impact:**
1. **Credibility loss** - "Do as I say, not as I do" undermines trust
2. **Testing gap** - Not experiencing the same structure we're distributing
3. **Documentation mismatch** - AI rules reference `/logs/` but we use `project/planning/`
4. **Missing config** - No `.logfile-config.yml` means no update tracking, no validation
5. **Inconsistent experience** - Can't identify UX issues if we're not using our own system

### Additional Issues Discovered

1. **No `.logfile-config.yml`** in root directory
   - No version tracking
   - No update notifications
   - No profile configuration
   - Validation scripts won't work properly

2. **Main branch has leftover file**
   - `project/docs/github-actions-ci.md` exists in main (violates ADR-009)
   - Should be cleaned up

3. **AI rules point to wrong paths**
   - `.augment/rules/log-file-maintenance.md` references `logs/` paths
   - But actual files are in `project/planning/`
   - This means the rules don't work correctly for this project

---

## Decision

**Migrate the development branch to use the /logs/ folder structure that we require from users.**

### Migration Plan

**Phase 1: Create /logs/ structure**
```
logs/
  ├── CHANGELOG.md          (from project/planning/CHANGELOG.md)
  ├── DEVLOG.md             (from project/planning/DEVLOG.md)
  └── adr/
      └── *.md              (from project/adr/*.md)
```

**Phase 2: Update configuration**
- Create `.logfile-config.yml` with:
  - Version: v0.1.0-dev
  - Profile: solo-developer
  - Paths: logs/ (default)
  - Update tracking enabled

**Phase 3: Update cross-references**
- All specs in `project/specs/` that reference `project/planning/` → `logs/`
- All ADRs that reference `project/planning/` → `logs/`
- WORKFLOW.md references
- README.md references (if any)

**Phase 4: Clean up**
- Delete empty `project/planning/` directory
- Delete empty `project/adr/` directory
- Clean up `project/docs/github-actions-ci.md` from main branch

**Phase 5: Verify**
- Run validation scripts to ensure they work
- Test AI rules to ensure they reference correct paths
- Verify update tracking works

### What Stays in project/

These directories remain in `project/` because they're development meta-files, not logs:
- `project/specs/` - Epic specifications, roadmaps, PRD
- `project/qa/` - QA reports, bug reports
- `project/research/` - Research documents
- `project/templates/` - WIP templates not ready for distribution
- `project/docs/` - Development documentation

---

## Consequences

### Positive

1. **Dogfooding integrity** - We use the same structure we distribute
2. **Better testing** - Experience the same UX as our users
3. **Credibility** - "We use our own system" is a powerful statement
4. **Update tracking** - `.logfile-config.yml` enables version notifications
5. **Validation works** - Scripts can actually validate our own logs
6. **Consistent AI rules** - Rules work the same for us and users
7. **Documentation accuracy** - Examples match reality

### Negative

1. **Migration effort** - ~2-3 hours to migrate and update all references
2. **Git history** - File moves create noise in git history (acceptable)
3. **Breaking change for development** - Anyone else working on this needs to pull changes

### Neutral

1. **Only affects development branch** - Main branch unchanged (per ADR-009)
2. **One-time cost** - Migration happens once, benefits persist

---

## Alternatives Considered

### Alternative 1: Keep current structure (project/planning/)
**Rejected because:**
- Violates our own ADR-012
- Creates dogfooding failure
- Can't test our own system properly
- Undermines credibility
- Missing update tracking and validation

### Alternative 2: Use different structure for dogfooding
**Rejected because:**
- Defeats the purpose of dogfooding
- Can't identify UX issues if we use different structure
- Creates confusion ("Why don't you use your own system?")

### Alternative 3: Wait until v1.0 to migrate
**Rejected because:**
- We're already distributing the /logs/ structure to users
- Delaying increases technical debt
- Better to migrate now while project is small

---

## Implementation Notes

### Migration Checklist

**Files to move:**
- [ ] `project/planning/CHANGELOG.md` → `logs/CHANGELOG.md`
- [ ] `project/planning/DEVLOG.md` → `logs/DEVLOG.md`
- [ ] `project/adr/*.md` → `logs/adr/*.md`

**Files to create:**
- [ ] `.logfile-config.yml` (root directory)

**Files to update (cross-references):**
- [ ] All files in `project/specs/` that reference planning/adr paths
- [ ] `project/WORKFLOW.md`
- [ ] `README.md` (if applicable)
- [ ] `.augment/rules/project-identity.md` (if it references paths)

**Files to delete:**
- [ ] `project/planning/` directory (after migration)
- [ ] `project/adr/` directory (after migration)
- [ ] `project/docs/github-actions-ci.md` from main branch

**Verification:**
- [ ] Run `validate-log-files.ps1` to ensure it works
- [ ] Test AI rules to ensure they reference correct paths
- [ ] Verify `.logfile-config.yml` is read correctly
- [ ] Check update tracking works

### Git Strategy

**Option 1: git mv (preserves history)**
```bash
git mv project/planning/CHANGELOG.md logs/CHANGELOG.md
git mv project/planning/DEVLOG.md logs/DEVLOG.md
git mv project/adr logs/adr
```

**Option 2: Manual move + commit message**
- Move files manually
- Commit with detailed message explaining migration
- Git will detect renames if >50% similarity

**Recommendation:** Use `git mv` to preserve history.

---

## Related Work

- **Epic 19:** Dogfooding Migration to /logs/ Structure (implementation tasks)
- **ADR-012:** Single /logs/ Folder for All Log Files (the standard we're adopting)
- **ADR-009:** Two-Branch Strategy (explains why only development branch affected)

---

## Success Criteria

1. ✅ All log files in `/logs/` directory
2. ✅ `.logfile-config.yml` exists and is valid
3. ✅ Validation scripts run successfully
4. ✅ AI rules reference correct paths
5. ✅ Update tracking works
6. ✅ All cross-references updated
7. ✅ No broken links in documentation
8. ✅ Main branch cleaned up (no project/docs/github-actions-ci.md)

