# Update Notifications

**Version:** 1.0  
**Status:** Active

Learn how Log File Genius notifies you of updates and how to stay current with the latest features and improvements.

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Version Tracking](#version-tracking)
3. [Automatic Update Checks](#automatic-update-checks)
4. [Manual Update Checks](#manual-update-checks)
5. [GitHub Releases](#github-releases)
6. [Migration Guides](#migration-guides)
7. [Update Workflow](#update-workflow)

---

## Overview

Log File Genius uses a multi-layered approach to keep you informed about updates:

1. **Version tracking** in `.logfile-config.yml`
2. **Automatic checks** during validation
3. **Manual check script** for on-demand updates
4. **GitHub Releases** with detailed release notes
5. **Migration guides** for major version changes

---

## Version Tracking

### Configuration File

Your `.logfile-config.yml` includes a version field:

```yaml
# Log File Genius Configuration
log_file_genius_version: "0.2.0"
profile: solo-developer
```

**Purpose:**
- Tracks which version of Log File Genius you're using
- Enables validation scripts to detect outdated versions
- Helps with troubleshooting and support

**When to Update:**
- After applying updates from a new release
- When migrating to a new version
- As part of the migration guide steps

---

## Automatic Update Checks

### During Validation

When you run validation scripts, they automatically check for updates:

```bash
# PowerShell (Windows)
.\product\scripts\validate-log-files.ps1

# Bash (Mac/Linux)
./product/scripts/validate-log-files.sh
```

**Output (if update available):**
```
⚠️  Log File Genius update available: v0.3.0 (you have v0.2.0)
    See: https://github.com/clark-mackey/log-file-genius/releases
```

**Behavior:**
- Non-intrusive warning (doesn't fail validation)
- Shows current vs latest version
- Provides link to release notes
- Only appears if version mismatch detected

**Disable Automatic Checks:**

If you prefer not to see update notifications during validation, you can:

1. **Remove version field** from `.logfile-config.yml` (not recommended)
2. **Comment out version field:**
   ```yaml
   # log_file_genius_version: "0.2.0"
   ```
3. **Ignore the warning** (it won't affect validation results)

---

## Manual Update Checks

### Check-for-Updates Script

Run the dedicated update checker anytime:

```bash
# PowerShell (Windows)
.\product\scripts\check-for-updates.ps1

# Bash (Mac/Linux)
./product/scripts/check-for-updates.sh

# Verbose mode (shows more details)
.\product\scripts\check-for-updates.ps1 -Verbose
./product/scripts/check-for-updates.sh -v
```

**Output (up to date):**
```
🔍 Checking for Log File Genius updates...

📦 Current version: v0.2.0

🌟 Latest version: v0.2.0
   Release: Profile System Release
   Published: 2025-11-02

✅ You're up to date!
```

**Output (update available):**
```
🔍 Checking for Log File Genius updates...

📦 Current version: v0.2.0

🌟 Latest version: v0.3.0
   Release: Skills & Templates Library
   Published: 2025-11-15

🔔 Update available: v0.2.0 → v0.3.0

📝 Release notes:
   https://github.com/clark-mackey/log-file-genius/releases/v0.3.0

Summary:
Added Skills & Templates Library with 10 pre-built templates...

To update:
1. Review release notes: https://github.com/clark-mackey/log-file-genius/releases/v0.3.0
2. Check migration guide (if provided)
3. Update your .logfile-config.yml version to: 0.3.0
4. Pull updated files from the repository
```

**Features:**
- Queries GitHub API for latest release
- Shows release name, date, and summary
- Provides step-by-step update instructions
- Works offline (gracefully fails if no internet)

---

## GitHub Releases

### Watching the Repository

**Get notified automatically:**

1. Go to https://github.com/clark-mackey/log-file-genius
2. Click "Watch" → "Custom" → "Releases"
3. You'll receive notifications for new releases

**Release Format:**

Each release includes:
- **Version number** (e.g., v0.3.0)
- **Release name** (e.g., "Skills & Templates Library")
- **Release notes** (what's new, what changed, what's fixed)
- **Migration guide** (for major versions)
- **Assets** (downloadable files, if applicable)

**Release Cadence:**

- **Major versions** (v1.0.0, v2.0.0): Significant new features or breaking changes
- **Minor versions** (v0.2.0, v0.3.0): New features, no breaking changes
- **Patch versions** (v0.2.1, v0.2.2): Bug fixes, minor improvements

---

## Migration Guides

### When Provided

Migration guides are provided for:
- Major version changes (v1.0 → v2.0)
- Breaking changes
- Significant feature additions requiring configuration

### Format

Migration guides follow a standard template:

1. **Overview** - What changed and why
2. **Pre-Migration Checklist** - Backup and preparation
3. **Step-by-Step Instructions** - Detailed migration steps
4. **Breaking Changes** - What no longer works
5. **New Features** - How to use new capabilities
6. **Troubleshooting** - Common issues and solutions
7. **Post-Migration Checklist** - Verification steps

### Location

- **In releases:** Included in GitHub release notes
- **In repository:** `product/docs/migrations/v[VERSION].md`
- **Template:** `product/templates/MIGRATION_GUIDE_template.md`

---

## Update Workflow

### Recommended Process

**1. Check for Updates (Monthly)**
```bash
./product/scripts/check-for-updates.sh
```

**2. Review Release Notes**
- Read what's new
- Check for breaking changes
- Assess if update is needed

**3. Backup Current State**
```bash
git commit -am "Backup before updating to v0.3.0"
```

**4. Follow Migration Guide**
- Read migration guide (if provided)
- Follow steps in order
- Update `.logfile-config.yml` version

**5. Pull Updated Files**
```bash
# Option A: Git remote (if set up)
git fetch log-file-genius
git checkout log-file-genius/main -- product/

# Option B: Manual download
# Download specific files from GitHub
```

**6. Verify Update**
```bash
# Run validation
./product/scripts/validate-log-files.sh -v

# Check version
grep "log_file_genius_version" .logfile-config.yml
```

**7. Test Workflow**
- Make a test commit
- Verify AI assistant rules work
- Check validation passes

**8. Commit Update**
```bash
git add .logfile-config.yml product/
git commit -m "chore: Update Log File Genius to v0.3.0"
```

---

## Troubleshooting

### Update Check Fails

**Symptom:** `check-for-updates.sh` fails with connection error

**Causes:**
- No internet connection
- GitHub API rate limit exceeded
- Firewall blocking GitHub

**Solution:**
- Check internet connection
- Wait 1 hour (GitHub API rate limit resets)
- Manually visit https://github.com/clark-mackey/log-file-genius/releases

### Version Mismatch After Update

**Symptom:** Validation still shows old version

**Causes:**
- Forgot to update `.logfile-config.yml`
- Config file in wrong location

**Solution:**
```bash
# Update version in config
sed -i 's/log_file_genius_version: "0.2.0"/log_file_genius_version: "0.3.0"/' .logfile-config.yml

# Verify
grep "log_file_genius_version" .logfile-config.yml
```

### AI Assistant Not Recognizing Updates

**Symptom:** AI assistant uses old rules after update

**Causes:**
- Rules files not updated
- AI assistant not restarted

**Solution:**
1. Update rules files from starter packs
2. Restart AI assistant (Augment/Claude Code)
3. Verify rules files are in correct location

---

## Best Practices

**✅ Do:**
- Check for updates monthly
- Read release notes before updating
- Backup before major version updates
- Follow migration guides step-by-step
- Test after updating

**❌ Don't:**
- Skip migration guides
- Update without backing up
- Mix versions (old config + new scripts)
- Ignore breaking changes
- Update during active development

---

## Related Documentation

- **Profile Selection Guide:** `product/docs/profile-selection-guide.md`
- **Validation Guide:** `product/docs/validation-guide.md`
- **Migration Template:** `product/templates/MIGRATION_GUIDE_template.md`
- **GitHub Releases:** https://github.com/clark-mackey/log-file-genius/releases

---

**Questions?** Open an issue: https://github.com/clark-mackey/log-file-genius/issues

