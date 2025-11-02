# ADR-009: Two-Branch Strategy for Version Control

**Status:** Accepted  
**Date:** 2025-11-02  
**Deciders:** Clark Mackey  
**Supersedes:** Partially modifies ADR-008

---

## Context

ADR-008 (Product/Project Directory Separation) solved AI agent confusion by separating distributable content (`product/`) from development files (`project/`). However, it excluded `project/` from git via `.gitignore`, which created a new problem:

**Problem:** Lost version control, backup, and single source of truth for development files (planning, specs, ADRs, roadmaps).

**User feedback:** "When we split the project/product, I lost use of GitHub as version control and single source of truth for my own project files."

**Requirements:**
1. Version control for all files (product/ and project/)
2. GitHub as single source of truth
3. Clean user experience (template users don't see project/)
4. GitHub Template button works correctly
5. Transparency acceptable (planning process can be public)

---

## Decision

**Implement a two-branch strategy:**

### Branch Structure

**`main` branch (public, for distribution):**
- Contains only `product/` directory
- Used by GitHub Template button
- Clean for end users
- Receives merges from `development` when ready to release

**`development` branch (public, for development):**
- Contains both `product/` and `project/` directories
- Default working branch for development
- Full version control for all files
- Planning process is transparent (public)

### Workflow

**Daily development:**
1. Work on `development` branch
2. Make changes to `product/` and/or `project/`
3. Commit and push to `development` branch

**When ready to release product/ changes:**
1. Merge `product/` changes from `development` to `main`
2. Tag release on `main` branch
3. Users get clean template from `main`

**Git configuration:**
- Remove `/project/` from `.gitignore`
- Set `development` as default branch in GitHub settings (optional)
- Both branches are public (transparency)

---

## Consequences

### Positive

✅ **Full version control:** All files (product/ and project/) are in git  
✅ **GitHub as single source of truth:** No local-only files  
✅ **Clean user experience:** Template users only see product/ (from main branch)  
✅ **Template button works:** Uses main branch, distributes only product/  
✅ **Transparency:** Planning process is visible (open-source best practice)  
✅ **Collaboration ready:** Can share planning with contributors  
✅ **Backup and recovery:** All files backed up to GitHub  
✅ **Change tracking:** Full history for specs, roadmaps, ADRs  

### Negative

⚠️ **Branch management:** Need to remember to merge product/ changes to main  
⚠️ **Planning is public:** Roadmaps, specs, ADRs visible to everyone (acceptable)  
⚠️ **Slightly more complex:** Two branches instead of one  

### Neutral

🔄 **Preserves ADR-008 benefits:** Product/project separation still prevents AI confusion  
🔄 **Industry standard:** Many projects use main/develop branching strategy  

---

## Alternatives Considered

### Alternative 1: Everything in main, use .templateignore
**Rejected:** Users who clone (not template) would see project/, causing confusion

### Alternative 2: Separate private repository for project/
**Rejected:** User wants version control but is okay with public planning (transparency)

### Alternative 3: Keep current setup (project/ excluded from git)
**Rejected:** This is the problem we're solving (no version control for project/)

### Alternative 4: Revert ADR-008 (single directory structure)
**Rejected:** Would bring back AI agent confusion

---

## Implementation Notes

### Initial Setup

1. Remove `/project/` from `.gitignore`
2. Create `development` branch from current `main`
3. Add all `project/` files to `development` branch
4. Commit and push `development` branch
5. Keep `main` branch as-is (only product/)

### Ongoing Workflow

**Daily development (most common):**
```bash
# Work on development branch (default)
git checkout development

# Make changes to product/ or project/
# ... edit files ...

# Commit and push
git add .
git commit -m "Your commit message"
git push origin development
```

**For product/ changes only:**
```bash
# Work on development branch
git checkout development

# Make changes to product/
# ... edit product/docs/log_file_how_to.md ...

# Commit to development
git add product/
git commit -m "Update log file documentation"
git push origin development

# When ready to release to users
git checkout main
git checkout development -- product/
git commit -m "Release: Update log file documentation"
git push origin main

# Switch back to development
git checkout development
```

**For project/ changes only:**
```bash
# Work on development branch
git checkout development

# Make changes to project/
# ... edit project/specs/EPIC-12-security-secrets-detection.md ...

# Commit to development
git add project/
git commit -m "Update Epic 12 task list"
git push origin development

# No need to merge to main (project/ not in main)
```

**For both product/ and project/ changes:**
```bash
# Work on development branch
git checkout development

# Make changes to both directories
# ... edit product/docs/log_file_how_to.md ...
# ... edit project/planning/DEVLOG.md ...

# Commit everything to development
git add product/ project/
git commit -m "Update docs and planning"
git push origin development

# When ready to release product changes
git checkout main
git checkout development -- product/docs/log_file_how_to.md
git commit -m "Release: Update log file documentation"
git push origin main

# Switch back to development
git checkout development
```

### Common Scenarios

**Scenario 1: Add new template to product/**
```bash
# On development branch
git checkout development

# Create new template
# ... create product/templates/new-template.md ...

# Commit to development
git add product/templates/new-template.md
git commit -m "Add new template for X"
git push origin development

# When ready to release
git checkout main
git checkout development -- product/templates/new-template.md
git commit -m "Release: Add new template for X"
git push origin main
git checkout development
```

**Scenario 2: Update epic specs (project/ only)**
```bash
# On development branch
git checkout development

# Update specs
# ... edit project/specs/EPIC-12-security-secrets-detection.md ...

# Commit to development
git add project/specs/
git commit -m "Update Epic 12 task list"
git push origin development

# No need to merge to main (project/ not in main)
```

**Scenario 3: Create new ADR**
```bash
# On development branch
git checkout development

# Create ADR
# ... create project/adr/010-new-decision.md ...

# Update ADR index in DEVLOG
# ... edit project/planning/DEVLOG.md ...

# Commit to development
git add project/adr/ project/planning/
git commit -m "ADR-010: Document new architectural decision"
git push origin development

# No need to merge to main (project/ not in main)
```

**Scenario 4: Update starter pack (product/) and document in DEVLOG (project/)**
```bash
# On development branch
git checkout development

# Update starter pack
# ... edit product/starter-packs/augment/README.md ...

# Document in DEVLOG
# ... edit project/planning/DEVLOG.md ...
# ... edit project/planning/CHANGELOG.md ...

# Commit everything to development
git add product/starter-packs/ project/planning/
git commit -m "Update Augment starter pack with new instructions"
git push origin development

# When ready to release
git checkout main
git checkout development -- product/starter-packs/augment/README.md
git commit -m "Release: Update Augment starter pack"
git push origin main
git checkout development
```

### GitHub Settings

**Repository settings:**
- ✅ Template repository: Enabled
- ✅ Default branch: `development` (for contributors)
- ✅ Branch protection: Optional (can protect main from direct pushes)

**Template behavior:**
- Users click "Use this template" → Gets files from `main` branch
- Only `product/` directory is copied (clean template)

---

## Verification

**Success criteria:**
- [ ] `development` branch has both `product/` and `project/`
- [ ] `main` branch has only `product/`
- [ ] All project/ files are committed to `development`
- [ ] Both branches pushed to GitHub
- [ ] GitHub Template button uses `main` branch
- [ ] Can track changes to specs, roadmaps, ADRs

---

## Related Decisions

- **ADR-008:** Product/Project Directory Separation (still valid, enhanced by this ADR)
- **Future ADR:** May need to document release process (merging to main)

---

## References

- GitHub Template Repositories: https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-template-repository
- Git branching strategies: https://git-scm.com/book/en/v2/Git-Branching-Branching-Workflows
- Open-source transparency: Many successful projects make planning public (e.g., Kubernetes, React)

---

## Notes

**Why transparency is acceptable:**

Many successful open-source projects make their planning process public:
- **Kubernetes:** All KEPs (enhancement proposals) are public
- **React:** RFCs and roadmaps are public
- **VS Code:** Iteration plans and feature requests are public

Benefits of public planning:
- Community can see what's coming
- Contributors can align their work
- Builds trust and transparency
- Enables collaboration

**Why this is better than ADR-008 alone:**

ADR-008 solved AI confusion but went too far by excluding project/ from git entirely. This ADR preserves the benefits (product/project separation) while restoring version control for development files.

