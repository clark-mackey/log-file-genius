# Validation Architecture

**Version:** 1.0  
**Status:** Design  
**Date:** 2025-10-31

---

## Overview

The Log File Genius validation system provides automated checks for CHANGELOG and DEVLOG format, completeness, and token limits. The system is designed to be:

- **Lightweight:** Simple shell scripts, no complex dependencies
- **Modular:** Each validation can run independently
- **Optional:** Users can skip validation if desired
- **Cross-platform:** Works on Windows (PowerShell), Mac, and Linux (Bash)
- **Helpful:** Clear error messages with actionable fix suggestions

---

## Architecture

```
scripts/
├── validate-log-files.sh (or .ps1)    # Master validation script
├── validate-changelog.sh (or .ps1)    # CHANGELOG format validation
├── validate-devlog.sh (or .ps1)       # DEVLOG format validation
└── validate-tokens.sh (or .ps1)       # Token count validation

.git-hooks/
└── pre-commit                          # Optional git hook template

docs/
└── validation-guide.md                 # User documentation
```

---

## Validation Rules

### CHANGELOG Validation

**Required Structure:**
- File must exist at `docs/planning/CHANGELOG.md`
- Must have "## [Unreleased]" section
- Must have at least one category: Added, Changed, Fixed, Deprecated, Removed, Security

**Entry Format:**
- Pattern: `- Description. Files: \`path/to/file\`. Commit: \`hash\``
- Description must be present and non-empty
- Files reference is optional but recommended
- Commit hash is optional but recommended

**Date Format:**
- Release dates must be in YYYY-MM-DD format
- Example: `## [1.0.0] - 2025-10-31`

**Exit Codes:**
- 0: All checks passed
- 1: Format errors found
- 2: File not found

### DEVLOG Validation

**Required Structure:**
- File must exist at `docs/planning/DEVLOG.md`
- Must have "## Current Context (Source of Truth)" section
- Must have "## Daily Log - Newest First" section

**Current Context Requirements:**
- Must have "Version" field
- Must have "Active Branch" field
- Must have "Phase" field

**Entry Format:**
- Must have date in format: `### YYYY-MM-DD: Title`
- Must have at least one of: "Situation", "Challenge", "Decision", "Why", "Result"
- Files section is optional but recommended

**Exit Codes:**
- 0: All checks passed
- 1: Format errors found
- 2: File not found

### Token Count Validation

**Token Calculation:**
- Simple estimate: `word_count * 1.3`
- More accurate (optional): Use tiktoken library (requires Python)

**Thresholds:**

| File | Warning (80%) | Error (100%) | Action |
|------|---------------|--------------|--------|
| CHANGELOG | 8,000 tokens | 10,000 tokens | Suggest archival |
| DEVLOG | 12,000 tokens | 15,000 tokens | Suggest archival |
| Combined | 20,000 tokens | 25,000 tokens | Require archival |

**Exit Codes:**
- 0: All checks passed (under warning threshold)
- 1: Warning threshold exceeded (80-99%)
- 2: Error threshold exceeded (100%+)

---

## Master Validation Script

**Purpose:** Run all validations and aggregate results

**Usage:**
```bash
# Run all validations
./scripts/validate-log-files.sh

# Run with verbose output
./scripts/validate-log-files.sh --verbose

# Run specific validation only
./scripts/validate-log-files.sh --changelog
./scripts/validate-log-files.sh --devlog
./scripts/validate-log-files.sh --tokens
```

**Output Format:**
```
✅ CHANGELOG validation: PASSED
✅ DEVLOG validation: PASSED
⚠️  Token count validation: WARNING (CHANGELOG at 85% of target)

Summary: 2 passed, 1 warning, 0 errors
```

**Exit Codes:**
- 0: All validations passed
- 1: Warnings present (non-blocking)
- 2: Errors present (blocking)

---

## Git Pre-Commit Hook

**Purpose:** Automatically run validation before commits

**Installation:**
```bash
# Copy template to .git/hooks/
cp .git-hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

**Behavior:**
- Runs master validation script
- Blocks commit if errors found (exit code 2)
- Allows commit if only warnings (exit code 1)
- Allows bypass with `git commit --no-verify`

**Hook Template:**
```bash
#!/bin/bash
# Pre-commit hook for Log File Genius validation

echo "Running log file validation..."
./scripts/validate-log-files.sh

EXIT_CODE=$?

if [ $EXIT_CODE -eq 2 ]; then
    echo ""
    echo "❌ Validation failed. Please fix errors before committing."
    echo "   To bypass validation, use: git commit --no-verify"
    exit 1
elif [ $EXIT_CODE -eq 1 ]; then
    echo ""
    echo "⚠️  Validation warnings present. Commit allowed."
fi

exit 0
```

---

## Error Messages

**Design Principles:**
- Clear and specific (not generic)
- Actionable (tell user how to fix)
- Contextual (show line numbers and examples)
- Helpful (suggest common solutions)

**Example Error Messages:**

```
❌ CHANGELOG Error: Missing "Unreleased" section
   Location: docs/planning/CHANGELOG.md
   Expected: ## [Unreleased]
   Fix: Add "## [Unreleased]" section at line 10

❌ DEVLOG Error: Invalid date format
   Location: docs/planning/DEVLOG.md:45
   Found: ### 10-31-2025: My Entry
   Expected: ### 2025-10-31: My Entry
   Fix: Use YYYY-MM-DD format for dates

⚠️  Token Warning: CHANGELOG approaching limit
   Current: 8,500 tokens (85% of 10,000 target)
   Recommendation: Consider archiving entries older than 30 days
   See: docs/log_file_how_to.md#archival-strategy
```

---

## Cross-Platform Implementation

**Option 1: Dual Scripts (Recommended for v1)**
- Provide both `.sh` (Unix/Mac/WSL) and `.ps1` (Windows PowerShell)
- Users choose based on their platform
- Simpler, no dependencies

**Option 2: Single Script (Future)**
- Use Node.js or Python for cross-platform compatibility
- Requires runtime dependency
- More complex but unified

**Decision:** Start with Option 1 (dual scripts) for simplicity

---

## Profile Integration

**Future Enhancement:** Validation strictness based on profile

| Profile | CHANGELOG Required | DEVLOG Required | Token Strictness |
|---------|-------------------|-----------------|------------------|
| Solo Developer | Yes | Milestones only | Warnings only |
| Team | Yes | Significant changes | Errors |
| Open Source | Yes | Optional | Strict format |
| Startup/MVP | Yes | No | Minimal |

**Implementation:** Read from `config.yml` (Epic 8)

---

## Testing Strategy

1. **Unit Tests:** Test each validation script with valid/invalid inputs
2. **Integration Tests:** Test master script with various file combinations
3. **Hook Tests:** Test git hook installation and execution
4. **Cross-Platform Tests:** Test on Windows, Mac, Linux
5. **User Tests:** Early adopters test validation workflow

**Test Files:**
- `examples/validation/valid-changelog.md`
- `examples/validation/invalid-changelog.md`
- `examples/validation/valid-devlog.md`
- `examples/validation/invalid-devlog.md`
- `examples/validation/over-token-limit.md`

---

## Implementation Order

1. **Phase 1:** Master validation script (basic structure)
2. **Phase 2:** CHANGELOG validation (format checks)
3. **Phase 3:** DEVLOG validation (format checks)
4. **Phase 4:** Token count validation (simple estimate)
5. **Phase 5:** Git pre-commit hook
6. **Phase 6:** Documentation and examples
7. **Phase 7:** Starter pack integration

---

## Success Metrics

- [ ] Validation scripts created and tested
- [ ] Git hook template available
- [ ] Documentation complete
- [ ] 90%+ of commits pass validation on first try (after adoption)
- [ ] Users report validation is helpful, not annoying

---

## Future Enhancements

- **Auto-fix:** `--fix` flag to automatically fix simple issues
- **CI/CD Integration:** GitHub Action for validation
- **VS Code Extension:** Real-time validation in editor
- **Exact Token Counting:** Use tiktoken for accurate counts
- **Custom Rules:** Allow users to define custom validation rules

