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

**For product/ changes:**
```bash
# Work on development branch
git checkout development
# Make changes to product/
git add product/
git commit -m "Add new feature"
git push origin development

# When ready to release
git checkout main
git merge development -- product/  # Only merge product/ directory
git push origin main
```

**For project/ changes:**
```bash
# Work on development branch
git checkout development
# Make changes to project/
git add project/
git commit -m "Update roadmap"
git push origin development
# No need to merge to main (project/ not in main)
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

