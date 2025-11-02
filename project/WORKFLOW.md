# Development Workflow Guide

**Last Updated:** 2025-11-02  
**Related:** ADR-009 (Two-Branch Strategy)

---

## Branch Structure

### `main` branch (Distribution)
- **Purpose:** Clean template for end users
- **Contains:** Only `product/` directory
- **Used by:** GitHub Template button
- **Updates:** Merge from `development` when ready to release

### `development` branch (Development)
- **Purpose:** Active development work
- **Contains:** Both `product/` and `project/` directories
- **Used by:** Daily development work
- **Updates:** All commits go here first

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

### When Ready to Release Product Changes

**Only merge `product/` changes to `main` when:**
- New features are complete and tested
- Documentation is updated
- Ready for users to access via template

```bash
# Switch to main branch
git checkout main

# Merge only product/ directory from development
git checkout development -- product/

# Commit the merge
git commit -m "Release: [describe changes]"

# Tag the release (optional)
git tag -a v0.2.0 -m "Release v0.2.0: [description]"

# Push to GitHub
git push origin main
git push origin --tags
```

### Alternative: Merge Entire Development Branch

If you want to merge everything (not recommended, keeps main clean):

```bash
git checkout main
git merge development
git push origin main
```

**Note:** This would add `project/` to main branch, which defeats the purpose of the two-branch strategy.

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
git checkout development -- product/templates/new-template.md
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
git checkout development -- product/docs/log_file_how_to.md
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

### "I'm on main branch and can't see project/ files"

**Solution:** Switch to `development` branch
```bash
git checkout development
```

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

---

## Quick Reference

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

# Merge product/ from development to main
git checkout main
git checkout development -- product/
git commit -m "Release: [description]"
git push origin main
```

---

## Related Documents

- **ADR-009:** Two-Branch Strategy for Version Control
- **ADR-008:** Product/Project Directory Separation
- **DEVLOG:** Current Context section (always on development branch)
- **CHANGELOG:** Version history (always on development branch)

