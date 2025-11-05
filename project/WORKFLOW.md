# Development Workflow Guide

**Last Updated:** 2025-11-05
**Related:** ADR-009 (Two-Branch Strategy)

---

## ⚠️ CRITICAL: Two-Branch Strategy Rules

**NEVER** use `git merge development` when on main branch!

**ALWAYS** use selective merge to copy ONLY distributable files:
```bash
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/
```

Violating this rule will copy `/project` files to main branch, breaking the distribution model.

---

## Branch Structure

### `main` branch (Distribution)
- **Purpose:** Clean template for end users
- **Contains:** **ONLY** `product/` directory (no `/project`)
- **Used by:** GitHub Template button, git submodule installations
- **Updates:** Selective merge from `development` when ready to release
- **`.gitignore`:** Contains `/project/` to prevent accidental inclusion

### `development` branch (Development)
- **Purpose:** Active development work
- **Contains:** Both `product/` and `project/` directories
- **Used by:** Daily development work
- **Updates:** All commits go here first
- **`.gitignore`:** Does NOT exclude `/project/` (tracked in git)

---

## Daily Workflow

### Working on Features

```bash
# Make sure you're on development branch
git checkout development

# Make changes to product/ or project/
# ... edit files ...

# Commit changes
git add .
git commit -m "Your commit message"

# Push to GitHub
git push origin development
```

### Updating Planning Documents

```bash
# Already on development branch
git checkout development

# Update DEVLOG, CHANGELOG, specs, ADRs, etc.
# ... edit files in project/ ...

# Commit
git add project/
git commit -m "Update roadmap and planning docs"

# Push
git push origin development
```

---

## Release Workflow

### ⚠️ CRITICAL: Selective Merge Only!

**When Ready to Release Product Changes:**

**Prerequisites:**
- New features are complete and tested
- Documentation is updated
- CHANGELOG.md updated on development branch
- Ready for users to access via template

**Step-by-Step Release Process:**

```bash
# 1. Make sure development is clean and pushed
git checkout development
git status  # Should be clean
git push origin development

# 2. Switch to main branch
git checkout main

# 3. SELECTIVE MERGE - Copy ONLY distributable files from development
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/

# 4. Verify what changed
git status
git diff --cached

# 5. Commit the release
git commit -m "Release: [describe changes]

- Feature 1
- Feature 2
- Bug fix 3"

# 6. Tag the release (optional but recommended)
git tag -a v0.2.0 -m "Release v0.2.0: [description]"

# 7. Push to GitHub
git push origin main
git push origin --tags

# 8. Switch back to development
git checkout development
```

### ❌ NEVER DO THIS

**DO NOT use `git merge development` on main branch!**

```bash
# ❌ WRONG - This will copy /project to main!
git checkout main
git merge development  # ❌ DON'T DO THIS!
```

**Why this is wrong:**
- Copies `/project` directory to main branch
- Breaks the two-branch strategy (ADR-009)
- Users get development files when installing via git submodule
- Defeats the purpose of clean distribution

**If you accidentally did this:**
1. See "Troubleshooting" section below for recovery steps
2. You'll need to remove `/project` from main and force-push

---

## Common Scenarios

### Scenario 1: Add New Template to Product

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
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/
git commit -m "Release: Add new template for X"
git push origin main
```

### Scenario 2: Update Epic Specs

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

### Scenario 3: Update Both Product and Project

```bash
# On development branch
git checkout development

# Update product docs and project planning
# ... edit product/docs/log_file_how_to.md ...
# ... edit project/planning/DEVLOG.md ...

# Commit everything to development
git add product/ project/
git commit -m "Update docs and planning"
git push origin development

# When ready to release product changes
git checkout main
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/
git commit -m "Release: Update log file documentation"
git push origin main
```

---

## Branch Comparison

### What's in Each Branch

**`development` branch:**
```
log-file-genius/
├── product/              ✅ Distributable content
│   ├── docs/
│   ├── examples/
│   ├── profiles/
│   ├── scripts/
│   ├── starter-packs/
│   └── templates/
├── project/              ✅ Development files
│   ├── adr/
│   ├── planning/
│   └── specs/
├── .gitignore
├── LICENSE
└── README.md
```

**`main` branch:**
```
log-file-genius/
├── product/              ✅ Distributable content
│   ├── docs/
│   ├── examples/
│   ├── profiles/
│   ├── scripts/
│   ├── starter-packs/
│   └── templates/
├── .gitignore
├── LICENSE
└── README.md
```

---

## GitHub Template Button

### How It Works

When users click "Use this template" on GitHub:
1. GitHub uses the `main` branch
2. Copies only `product/` directory (and root files)
3. User gets clean template without `project/` directory
4. User starts fresh with just the product

### Verification

To verify template works correctly:
1. Go to: https://github.com/clark-mackey/log-file-genius
2. Click "Use this template"
3. Create test repository
4. Verify it only has `product/` directory (no `project/`)

---

## Tips & Best Practices

### Always Work on Development

- ✅ **DO:** Make all commits to `development` first
- ❌ **DON'T:** Commit directly to `main` (except for merges)

### Merge to Main Intentionally

- ✅ **DO:** Merge to `main` when ready to release
- ❌ **DON'T:** Merge every commit to `main`

### Keep Main Clean

- ✅ **DO:** Only merge `product/` changes to `main`
- ❌ **DON'T:** Merge `project/` to `main` (defeats the purpose)

### Use Descriptive Commit Messages

- ✅ **DO:** "Add security detection script to Epic 12"
- ❌ **DON'T:** "Update files"

---

## Troubleshooting

### "I accidentally merged development into main" (CRITICAL)

**Problem:** You ran `git merge development` on main branch, now `/project` is in main.

**Solution:** Remove `/project` from main and force-push

```bash
# 1. Make sure you're on main
git checkout main

# 2. Remove all /project files
git rm -r project/

# 3. Update .gitignore to exclude /project
# Edit .gitignore and add: /project/

# 4. Commit the fix
git add .gitignore
git commit -m "fix: Remove /project directory from main branch per ADR-009

- Removed all /project files from main branch (development files only)
- Added /project/ to .gitignore on main branch
- Main branch now contains ONLY /product directory for distribution"

# 5. Force-push to GitHub (this rewrites history)
git push origin main --force-with-lease

# 6. Switch back to development
git checkout development

# 7. Update CHANGELOG.md on development to document the fix
# Then commit and push development
```

**Prevention:** Always use selective checkout instead of `git merge development`:
```bash
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/
```

### "I'm on main branch and can't see project/ files"

**Solution:** Switch to `development` branch
```bash
git checkout development
```

**Note:** This is expected! Main branch should NOT have `/project` files.

### "I accidentally committed to main"

**Solution:** Cherry-pick to development, reset main
```bash
# Save the commit hash
git log  # Copy the commit hash

# Switch to development
git checkout development

# Cherry-pick the commit
git cherry-pick <commit-hash>

# Switch back to main and reset
git checkout main
git reset --hard origin/main
```

### "I want to see what's different between branches"

**Solution:** Compare branches
```bash
# See files only in development
git diff main..development --name-only

# See all differences
git diff main..development
```

### "How do I verify main branch is clean?"

**Solution:** Check that main has NO /project files
```bash
# List all files in main branch
git ls-tree -r --name-only main | grep "^project/"

# Should return NOTHING (empty output)
# If it returns files, you need to clean main branch (see above)
```

---

## Quick Reference

### ✅ Correct Release Process (Copy This!)

```bash
# 1. Make sure development is clean
git checkout development
git status
git push origin development

# 2. Switch to main
git checkout main

# 3. SELECTIVE MERGE - Copy ONLY distributable files
git checkout development -- product/
git checkout development -- .augment/rules/
git checkout development -- .claude/

# 4. Commit and push
git commit -m "Release: [description]"
git push origin main

# 5. Switch back to development
git checkout development
```

### ❌ Wrong Release Process (Never Do This!)

```bash
# ❌ WRONG - Don't use git merge!
git checkout main
git merge development  # ❌ This copies /project to main!
```

### Common Commands

```bash
# Switch to development (daily work)
git checkout development

# Switch to main (releases only)
git checkout main

# See current branch
git branch

# See all branches (local and remote)
git branch -a

# Verify main is clean (should return nothing)
git ls-tree -r --name-only main | grep "^project/"
```

---

## Related Documents

- **ADR-009:** Two-Branch Strategy for Version Control
- **ADR-008:** Product/Project Directory Separation
- **DEVLOG:** Current Context section (always on development branch)
- **CHANGELOG:** Version history (always on development branch)
