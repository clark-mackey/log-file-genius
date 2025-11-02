# Validation Examples

This directory contains example CHANGELOG and DEVLOG files for testing the validation system.

---

## Files

### Valid Examples

- **`valid-changelog.md`** - Properly formatted CHANGELOG
  - Has `## [Unreleased]` section
  - Has proper categories (Added, Changed, Fixed)
  - Uses YYYY-MM-DD date format
  - Includes file references and commit hashes

- **`valid-devlog.md`** - Properly formatted DEVLOG
  - Has `## Current Context (Source of Truth)` section
  - Has `## Daily Log - Newest First` section
  - Has all required fields (Current Version, Active Branch, Phase)
  - Uses `### YYYY-MM-DD: Title` format for entries
  - Includes proper entry structure (Situation, Challenge, Decision, Why, Result)

### Invalid Examples

- **`invalid-changelog.md`** - CHANGELOG with common errors
  - Missing `## [Unreleased]` section
  - Invalid date formats (MM-DD-YYYY, Month DD, YYYY)
  - Missing file references

- **`invalid-devlog.md`** - DEVLOG with common errors
  - Wrong section names
  - Missing required fields
  - Invalid entry date formats
  - Missing entry structure

---

## Testing Validation

### Test with Valid Files

**PowerShell:**
```powershell
# Copy valid file to test location
Copy-Item examples/validation/valid-changelog.md docs/planning/CHANGELOG.md

# Run validation (should pass)
.\scripts\validate-log-files.ps1 -Changelog -Verbose
```

**Expected output:**
```
[OK] CHANGELOG validation: PASSED
```

### Test with Invalid Files

**PowerShell:**
```powershell
# Copy invalid file to test location
Copy-Item examples/validation/invalid-changelog.md docs/planning/CHANGELOG.md

# Run validation (should fail)
.\scripts\validate-log-files.ps1 -Changelog -Verbose
```

**Expected output:**
```
[X] CHANGELOG validation: ERROR - 3 issue(s) found
  - Missing '## [Unreleased]' section
  - Invalid date format found
```

---

## Common Validation Errors

### CHANGELOG Errors

1. **Missing Unreleased section**
   - Error: `Missing '## [Unreleased]' section`
   - Fix: Add `## [Unreleased]` section at top

2. **Missing categories**
   - Error: `Missing at least one category`
   - Fix: Add at least one category (Added, Changed, Fixed, etc.)

3. **Invalid date format**
   - Error: `Invalid date format found`
   - Fix: Use YYYY-MM-DD format (e.g., `2025-10-31`)

### DEVLOG Errors

1. **Missing Current Context**
   - Error: `Missing 'Current Context' section`
   - Fix: Add `## Current Context (Source of Truth)` section

2. **Missing Daily Log**
   - Error: `Missing 'Daily Log' section`
   - Fix: Add `## Daily Log - Newest First` section

3. **Missing required fields**
   - Error: `Missing required field: Version`
   - Fix: Add all required fields (Current Version, Active Branch, Phase)

4. **Invalid entry date**
   - Error: `Invalid entry date format`
   - Fix: Use `### YYYY-MM-DD: Title` format

---

## Restoring Original Files

After testing, restore your original files:

```powershell
# Restore from git
git checkout docs/planning/CHANGELOG.md
git checkout docs/planning/DEVLOG.md
```

---

## Related Documentation

- **[Validation Guide](../../docs/validation-guide.md)** - Complete validation documentation
- **[Validation Architecture](../../docs/validation-architecture.md)** - Technical design
- **[CHANGELOG Template](../../templates/CHANGELOG_template.md)** - Template with examples
- **[DEVLOG Template](../../templates/DEVLOG_template.md)** - Template with examples

