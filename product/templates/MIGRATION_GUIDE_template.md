# Migration Guide: v[OLD_VERSION] → v[NEW_VERSION]

**Release Date:** [YYYY-MM-DD]  
**Release Notes:** [Link to GitHub release]

---

## 📋 Overview

Brief summary of what changed in this release and why users should upgrade.

**Key Changes:**
- Major feature 1
- Major feature 2
- Breaking change (if any)

**Estimated Migration Time:** [X minutes/hours]

---

## ✅ Pre-Migration Checklist

Before starting the migration, ensure you have:

- [ ] Backed up your current log files (CHANGELOG.md, DEVLOG.md, etc.)
- [ ] Committed all pending changes to version control
- [ ] Reviewed the release notes: [Link]
- [ ] Noted your current version: v[OLD_VERSION]

---

## 🔄 Migration Steps

### Step 1: Update Configuration File

**File:** `.logfile-config.yml`

**Change:**
```yaml
# OLD (v[OLD_VERSION])
log_file_genius_version: "[OLD_VERSION]"

# NEW (v[NEW_VERSION])
log_file_genius_version: "[NEW_VERSION]"
```

**Why:** This ensures validation scripts recognize your updated version.

---

### Step 2: [Specific Change 1]

**Files Affected:** `[list of files]`

**What Changed:**
- Description of what changed
- Why it changed
- Impact on existing projects

**Action Required:**
```bash
# Example commands or file changes
cp product/templates/new-file.md project/planning/
```

**Example:**
```yaml
# Before
old_setting: value

# After
new_setting: value
```

---

### Step 3: [Specific Change 2]

**Files Affected:** `[list of files]`

**What Changed:**
- Description

**Action Required:**
- Step-by-step instructions

---

### Step 4: Update Validation Scripts (If Applicable)

**Files:** `product/scripts/validate-log-files.ps1`, `product/scripts/validate-log-files.sh`

**Action:**
```bash
# Pull latest validation scripts
git fetch origin
git checkout origin/main -- product/scripts/validate-log-files.ps1
git checkout origin/main -- product/scripts/validate-log-files.sh
```

**Or manually download:**
- [validate-log-files.ps1](https://raw.githubusercontent.com/clark-mackey/log-file-genius/main/product/scripts/validate-log-files.ps1)
- [validate-log-files.sh](https://raw.githubusercontent.com/clark-mackey/log-file-genius/main/product/scripts/validate-log-files.sh)

---

### Step 5: Update AI Assistant Rules (If Applicable)

**Files:** `.augment/rules/*.md`, `.claude/rules/*.md`

**Action:**
```bash
# Pull latest rules
git checkout origin/main -- .augment/rules/log-file-maintenance.md
# Or copy from starter packs
cp product/starter-packs/augment/.augment/rules/log-file-maintenance.md .augment/rules/
```

---

### Step 6: Verify Migration

**Run validation:**
```bash
# PowerShell (Windows)
.\product\scripts\validate-log-files.ps1 -Verbose

# Bash (Mac/Linux)
./product/scripts/validate-log-files.sh -v
```

**Expected output:**
```
✅ CHANGELOG validation: PASS
✅ DEVLOG validation: PASS
✅ Token count check: PASS
📦 Current version: v[NEW_VERSION]
```

---

## 🚨 Breaking Changes

### [Breaking Change 1] (If Any)

**What Broke:**
- Description of what no longer works

**Why:**
- Rationale for the breaking change

**Migration Path:**
```bash
# Old way
old_command

# New way
new_command
```

**Example:**
```yaml
# Before (v[OLD_VERSION])
old_format: value

# After (v[NEW_VERSION])
new_format: value
```

---

## 🆕 New Features (Optional)

### [New Feature 1]

**What It Does:**
- Description

**How to Use:**
```yaml
# Example configuration
new_feature:
  enabled: true
  setting: value
```

**Documentation:** [Link to docs]

---

## 🐛 Bug Fixes (Optional)

- Fixed: [Description of bug fix]
- Fixed: [Description of bug fix]

---

## 📚 Additional Resources

- **Full Release Notes:** [Link to GitHub release]
- **Documentation:** [Link to updated docs]
- **Profile Selection Guide:** `product/docs/profile-selection-guide.md`
- **Validation Guide:** `product/docs/validation-guide.md`

---

## ❓ Troubleshooting

### Issue: Validation fails after migration

**Solution:**
1. Check that `.logfile-config.yml` version is updated
2. Verify all required files are present
3. Run validation with `-Verbose` flag for details

### Issue: AI assistant not recognizing new rules

**Solution:**
1. Restart your AI assistant (Augment/Claude Code)
2. Verify rules files are in correct location
3. Check that rules reference correct file paths

### Issue: [Common Issue 3]

**Solution:**
- Step-by-step fix

---

## 💬 Need Help?

- **GitHub Issues:** https://github.com/clark-mackey/log-file-genius/issues
- **Discussions:** https://github.com/clark-mackey/log-file-genius/discussions
- **Documentation:** `product/docs/`

---

## ✅ Post-Migration Checklist

After completing the migration:

- [ ] Validation scripts pass without errors
- [ ] `.logfile-config.yml` version updated to v[NEW_VERSION]
- [ ] All new features configured (if applicable)
- [ ] AI assistant rules updated (if applicable)
- [ ] Committed migration changes to version control
- [ ] Tested workflow with a sample commit

---

**Migration Complete!** 🎉

You're now running Log File Genius v[NEW_VERSION].

