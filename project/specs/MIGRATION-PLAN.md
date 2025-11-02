# Migration Plan: Product/Project Directory Separation

**Epic:** Architectural Clarity Refactoring
**ADR:** [ADR-008: Product/Project Directory Separation](adr/008-product-project-directory-separation.md)
**Status:** Planning Complete - Ready for Execution
**Date:** 2025-11-02

---

## Overview

This migration restructures the Log File Genius repository to eliminate AI agent confusion between "the product we're building" and "the project building it" by creating clear `product/` and `project/` directories.

---

## Pre-Migration Checklist

- [x] ADR-008 created and accepted
- [x] `.project-identity.yaml` created
- [x] Migration plan documented
- [ ] Feature branch created (`refactor/product-project-separation`)
- [ ] All current work committed to `main`
- [ ] Backup of current state created

---

## File Mapping

### Product Files (Distributable Content)

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `templates/` | `product/templates/` | Clean templates for users |
| `docs/log_file_how_to.md` | `product/docs/log_file_how_to.md` | How-to guide |
| `docs/ADR_how_to.md` | `product/docs/ADR_how_to.md` | ADR guide |
| `docs/validation-guide.md` | `product/docs/validation-guide.md` | Validation guide |
| `docs/validation-architecture.md` | `product/docs/validation-architecture.md` | Validation architecture |
| `examples/` | `product/examples/` | Sample projects |
| `starter-packs/` | `product/starter-packs/` | Pre-configured setups |

### Project Files (Our Development)

| Current Location | New Location | Notes |
|-----------------|--------------|-------|
| `docs/planning/CHANGELOG.md` | `project/planning/CHANGELOG.md` | Our changelog |
| `docs/planning/DEVLOG.md` | `project/planning/DEVLOG.md` | Our devlog |
| `docs/planning/STATE.md` | `project/planning/STATE.md` | Our state (if exists) |
| `docs/planning/archive/` | `project/planning/archive/` | Archived logs |
| `docs/adr/` | `project/adr/` | Our ADRs |
| `docs/prd.md` | `project/specs/prd.md` | Our PRD |
| `docs/EPIC-*.md` | `project/specs/EPIC-*.md` | Our epic files |

### Root Files (Stay at Root)

| File | Action | Notes |
|------|--------|-------|
| `.project-identity.yaml` | Already created | New file |
| `README.md` | Update references | Update paths |
| `.gitignore` | No change | Already correct |
| `LICENSE` | No change | Stays at root |
| `.augment/` | Update rules | Update file paths |
| `.claude/` | Update rules | Update file paths |
| `scripts/` | Update paths | Update validation scripts |
| `.git-hooks/` | Update paths | Update hook scripts |

---

## Migration Steps

### Phase 1: Preparation (Story 1 - Complete)

- [x] Create ADR-008
- [x] Create `.project-identity.yaml`
- [x] Document migration plan
- [x] Update ADR README

### Phase 2: Directory Restructure (Story 2)

**Step 1: Create feature branch**
```bash
git checkout -b refactor/product-project-separation
```

**Step 2: Create new directory structure**
```bash
mkdir -p product/templates
mkdir -p product/docs
mkdir -p product/examples
mkdir -p product/starter-packs
mkdir -p project/planning
mkdir -p project/planning/archive
mkdir -p project/adr
mkdir -p project/specs
```

**Step 3: Move product files**
```bash
# Templates
git mv templates/* product/templates/

# Documentation
git mv docs/log_file_how_to.md product/docs/
git mv docs/ADR_how_to.md product/docs/
git mv docs/validation-guide.md product/docs/
git mv docs/validation-architecture.md product/docs/

# Examples
git mv examples/* product/examples/

# Starter packs
git mv starter-packs/* product/starter-packs/
```

**Step 4: Move project files**
```bash
# Planning
git mv docs/planning/CHANGELOG.md project/planning/
git mv docs/planning/DEVLOG.md project/planning/
git mv docs/planning/archive/* project/planning/archive/

# ADRs
git mv docs/adr/* project/adr/

# Specs
git mv docs/prd.md project/specs/
git mv docs/EPIC-*.md project/specs/ 2>/dev/null || true
```

**Step 5: Clean up empty directories**
```bash
rmdir templates
rmdir examples
rmdir starter-packs
rmdir docs/planning/archive
rmdir docs/planning
rmdir docs/adr
rmdir docs
```

**Step 6: Commit the moves**
```bash
git add -A
git commit -m "refactor: Separate product/ and project/ directories (ADR-008)

- Move distributable content to product/
- Move development files to project/
- Preserve Git history with git mv
- See ADR-008 for rationale"
```

### Phase 3: Update References (Story 2 continued)

**Files requiring path updates:**

1. **README.md**
   - Update all path references
   - Update quick start instructions
   - Update directory structure diagram

2. **Augment Rules** (`.augment/rules/*.md`)
   - `log-file-maintenance.md` - Update CHANGELOG/DEVLOG paths
   - `status-update.md` - Update DEVLOG path
   - `update-planning-docs.md` - Update all paths
   - `log-file-confusion-guard.md` - Update to reference new structure
   - `avoid-log-file-confusion.md` - Update to reference new structure

3. **Claude Code Rules** (`.claude/rules/*.md`)
   - Same updates as Augment rules

4. **Documentation Cross-References**
   - `product/docs/log_file_how_to.md` - Update example paths
   - `product/docs/ADR_how_to.md` - Update template paths
   - `project/adr/README.md` - Update template and doc paths
   - All ADR files - Update cross-reference paths

5. **Starter Packs**
   - `product/starter-packs/augment/README.md` - Update paths
   - `product/starter-packs/claude-code/README.md` - Update paths
   - Rules within starter packs - Update paths

### Phase 4: Update Tooling (Story 3)

**Validation Scripts:**
- `scripts/validate-log-files.ps1` - Update CHANGELOG/DEVLOG paths
- `scripts/validate-log-files.sh` - Update CHANGELOG/DEVLOG paths

**Git Hooks:**
- `.git-hooks/pre-commit` - Update validation script paths

**Starter Pack Scripts:**
- `product/starter-packs/augment/scripts/*.ps1` - Update paths
- `product/starter-packs/augment/scripts/*.sh` - Update paths
- `product/starter-packs/claude-code/scripts/*.ps1` - Update paths
- `product/starter-packs/claude-code/scripts/*.sh` - Update paths

---

## Validation Checklist

After migration, verify:

- [ ] All files moved successfully (no orphaned files)
- [ ] Git history preserved (check with `git log --follow`)
- [ ] Zero broken links (run link checker)
- [ ] All validation scripts pass
  - [ ] `.\scripts\validate-log-files.ps1`
  - [ ] `./scripts/validate-log-files.sh`
- [ ] All Augment rules load correctly
- [ ] All Claude Code rules load correctly
- [ ] README accurately reflects new structure
- [ ] All cross-references updated
- [ ] Starter packs reference correct paths
- [ ] AI agent confusion test scenarios pass:
  - [ ] "Update the logs" → Updates `project/planning/`
  - [ ] "Show example CHANGELOG" → Shows `product/templates/`
  - [ ] "What's next?" → Reads `project/specs/prd.md` + `project/planning/DEVLOG.md`
  - [ ] "@status update" → Reads `project/planning/DEVLOG.md`
  - [ ] "Improve template" → Edits `product/templates/`

---

## Rollback Plan

If critical issues arise:

1. **Before merge to main:**
   ```bash
   git checkout main
   git branch -D refactor/product-project-separation
   ```

2. **After merge to main:**
   ```bash
   git revert <merge-commit-hash>
   ```

3. **Nuclear option (if history is corrupted):**
   - Restore from backup
   - Cherry-pick individual fixes

---

## Success Criteria

Migration is successful when:

- ✅ All files in new `product/` and `project/` structure
- ✅ `.project-identity.yaml` created and referenced by rules
- ✅ Zero broken cross-references (verified with link checker)
- ✅ All Augment/Claude Code rules updated and tested
- ✅ All validation scripts passing
- ✅ All git hooks working
- ✅ All starter packs updated
- ✅ Documentation updated (README, ADR, migration guide)
- ✅ AI agent confusion test scenarios pass (5 test cases)
- ✅ No regression in existing functionality

---

## Post-Migration Tasks

After successful migration:

1. Update CHANGELOG with migration entry
2. Update DEVLOG with migration narrative
3. Create GitHub release notes explaining the change
4. Update any external documentation or blog posts
5. Monitor for confusion incidents (target: zero)

---

## Notes

- This is a **breaking change** for anyone who has cloned the repo
- Git history is preserved via `git mv`
- Feature branch allows safe experimentation
- Link checker is critical for validation
- AI agent test scenarios are the ultimate validation

---

