# Log File Validation Guide

**Version:** 1.0  
**Last Updated:** 2025-10-31

---

## Overview

The Log File Genius validation system automatically checks your CHANGELOG and DEVLOG files for proper format, completeness, and token limits. This guide explains how to use the validation tools and fix common errors.

---

## Quick Start

### Running Validation Manually

**Windows (PowerShell):**
```powershell
.\scripts\validate-log-files.ps1
```

**Mac/Linux (Bash):**
```bash
./product/scripts/validate-log-files.sh
```

### Installing Git Pre-Commit Hook

**Automatic validation before every commit:**

```bash
# Copy the hook template
cp .git-hooks/pre-commit .git/hooks/pre-commit

# Make it executable (Mac/Linux only)
chmod +x .git/hooks/pre-commit
```

Once installed, validation runs automatically before each commit. To bypass (use sparingly):
```bash
git commit --no-verify
```

---

## Validation Checks

### 1. CHANGELOG Validation

**What it checks:**
- ✅ File exists at `docs/planning/CHANGELOG.md`
- ✅ Has `## [Unreleased]` section
- ✅ Has at least one category (Added, Changed, Fixed, Deprecated, Removed, Security)
- ✅ Release dates are in YYYY-MM-DD format

**Common errors and fixes:**

#### Error: Missing "Unreleased" section
```
❌ CHANGELOG Error: Missing "Unreleased" section
```

**Fix:** Add this section to your CHANGELOG:
```markdown
## [Unreleased]

### Added
- Your changes here
```

#### Error: Missing categories
```
❌ CHANGELOG Error: Missing at least one category
```

**Fix:** Add at least one category under `[Unreleased]`:
```markdown
## [Unreleased]

### Added
- New feature description

### Changed
- Modified feature description

### Fixed
- Bug fix description
```

#### Error: Invalid date format
```
❌ CHANGELOG Error: Invalid date format found
   Found: ## [1.0.0] - 10-31-2025
   Expected: ## [1.0.0] - 2025-10-31
```

**Fix:** Use YYYY-MM-DD format:
```markdown
## [1.0.0] - 2025-10-31
```

---

### 2. DEVLOG Validation

**What it checks:**
- ✅ File exists at `docs/planning/DEVLOG.md`
- ✅ Has `## Current Context` section
- ✅ Has `## Daily Log` section
- ✅ Current Context has required fields (Version, Active Branch, Phase)
- ✅ Entry dates are in `### YYYY-MM-DD: Title` format

**Common errors and fixes:**

#### Error: Missing Current Context section
```
❌ DEVLOG Error: Missing "Current Context" section
```

**Fix:** Add this section to your DEVLOG:
```markdown
## Current Context (Source of Truth)

- **Current Version:** v0.1.0-dev
- **Active Branch:** `main`
- **Phase:** Development
```

#### Error: Missing required fields
```
❌ DEVLOG Error: Missing required field in Current Context: Version
```

**Fix:** Ensure all required fields are present:
```markdown
## Current Context (Source of Truth)

- **Current Version:** v0.1.0-dev
- **Active Branch:** `main`
- **Phase:** Development
```

#### Error: Invalid entry date format
```
❌ DEVLOG Error: Invalid entry date format
   Found: ### 10-31-2025: My Entry
   Expected: ### 2025-10-31: My Entry
```

**Fix:** Use YYYY-MM-DD format for entry dates:
```markdown
### 2025-10-31: My Entry Title
```

---

### 3. Token Count Validation

**What it checks:**
- ⚠️ Warns at 80% of token targets
- ❌ Errors at 100% of token targets

**Token Targets:**
| File | Warning (80%) | Error (100%) |
|------|---------------|--------------|
| CHANGELOG | 8,000 tokens | 10,000 tokens |
| DEVLOG | 12,000 tokens | 15,000 tokens |
| Combined | 20,000 tokens | 25,000 tokens |

**Common warnings and fixes:**

#### Warning: Approaching token limit
```
⚠️  Token Warning: CHANGELOG approaching limit
   Current: 8,500 tokens (85% of 10,000 target)
   Recommendation: Consider archiving entries older than 30 days
```

**Fix:** Archive old entries to reduce token count:

1. Create archive file: `docs/planning/archive/CHANGELOG-2025-10.md`
2. Move entries older than 30 days to archive
3. Update main CHANGELOG to reference archive

See [Archival Strategy](#archival-strategy) below for details.

#### Error: Token limit exceeded
```
❌ Token Error: Combined at 26,000 tokens (104% of 25,000 target)
   Recommendation: Archive entries immediately
```

**Fix:** Archive old entries immediately (required before commit).

---

## Command-Line Options

### Run Specific Validations

**CHANGELOG only:**
```powershell
.\scripts\validate-log-files.ps1 -Changelog
```

**DEVLOG only:**
```powershell
.\scripts\validate-log-files.ps1 -Devlog
```

**Token counts only:**
```powershell
.\scripts\validate-log-files.ps1 -Tokens
```

### Verbose Output

**Show detailed diagnostics:**
```powershell
.\scripts\validate-log-files.ps1 -Verbose
```

This shows:
- Specific line numbers for errors
- All invalid entries found
- Detailed token breakdowns
- Archival recommendations

---

## Exit Codes

The validation script uses standard exit codes:

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | All validations passed |
| 1 | Warning | Non-blocking warnings present (commit allowed) |
| 2 | Error | Blocking errors present (commit blocked) |

---

## Archival Strategy

When token counts approach limits, archive old entries:

### Step 1: Create Archive File

```bash
# Create archive directory if needed
mkdir -p docs/planning/archive

# Create archive file with year-month
touch docs/planning/archive/CHANGELOG-2025-10.md
```

### Step 2: Move Old Entries

Move entries older than 30 days from main file to archive:

**From `docs/planning/CHANGELOG.md`:**
```markdown
## [1.0.0] - 2025-09-15
### Added
- Old feature
```

**To `docs/planning/archive/CHANGELOG-2025-09.md`:**
```markdown
# CHANGELOG Archive - September 2025

## [1.0.0] - 2025-09-15
### Added
- Old feature
```

### Step 3: Update Main File

Add reference to archive in main file:
```markdown
## Archived Versions

For older versions, see:
- [September 2025](archive/CHANGELOG-2025-09.md)
- [August 2025](archive/CHANGELOG-2025-08.md)
```

---

## Troubleshooting

### Validation script not found

**Error:**
```
[!] Warning: No validation script found
```

**Fix:** Ensure you're in the repository root and the script exists:
```bash
ls product/scripts/validate-log-files.ps1  # Windows
ls product/scripts/validate-log-files.sh   # Mac/Linux
```

### Permission denied (Mac/Linux)

**Error:**
```
bash: ./product/scripts/validate-log-files.sh: Permission denied
```

**Fix:** Make the script executable:
```bash
chmod +x product/scripts/validate-log-files.sh
```

### PowerShell execution policy (Windows)

**Error:**
```
cannot be loaded because running scripts is disabled
```

**Fix:** Allow script execution (run as Administrator):
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

---

## Best Practices

1. **Run validation before committing:** Catch errors early
2. **Use verbose mode for debugging:** `.\scripts\validate-log-files.ps1 -Verbose`
3. **Archive proactively:** Don't wait for errors, archive at 80% warning
4. **Keep entries concise:** Shorter entries = more headroom before archival
5. **Use git hook:** Automate validation to never forget

---

## Related Documentation

- **[Validation Architecture](validation-architecture.md)** - Technical design and implementation details
- **[Log File How-To](log_file_how_to.md)** - Complete guide to using the log file system
- **[CHANGELOG Template](../templates/CHANGELOG_template.md)** - Template with examples
- **[DEVLOG Template](../templates/DEVLOG_template.md)** - Template with examples

---

## Support

If you encounter issues not covered in this guide:

1. Check the [validation architecture](validation-architecture.md) for technical details
2. Review [examples](../examples/validation/) for valid/invalid samples
3. Open an issue on GitHub with validation output and file contents

