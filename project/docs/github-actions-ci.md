# GitHub Actions CI/CD Documentation

## Overview

Log File Genius uses GitHub Actions for automated testing to ensure cross-platform compatibility. The CI pipeline runs on every push and pull request to catch bugs before they reach users.

## Workflows

### Test Installer Workflow (`.github/workflows/test-installer.yml`)

**Triggers:**
- Push to `main` or `development` branches
- Pull requests to `main` or `development` branches

**What It Tests:**

#### 1. Bash Installer (Linux & macOS)
- **Platforms tested:**
  - `ubuntu-latest` - Linux with Bash 4.4+
  - `macos-latest` - Latest macOS with Bash 3.2
  - `macos-13` - Older macOS with Bash 3.2
  
- **Tests performed:**
  - ✅ Bash version detection
  - ✅ Line ending verification (no CRLF in shell scripts)
  - ✅ Installer help command
  - ✅ Full installation with Augment profile
  - ✅ Full installation with Claude Code profile
  - ✅ File creation verification
  - ✅ Validation script execution

#### 2. PowerShell Installer (Windows)
- **Platform tested:**
  - `windows-latest` - Windows Server with PowerShell 5.1+
  
- **Tests performed:**
  - ✅ PowerShell version detection
  - ✅ Installer help command
  - ✅ Full installation with Augment profile
  - ✅ File creation verification
  - ✅ Validation script execution

#### 3. Line Ending Verification
- **Platform tested:**
  - `ubuntu-latest` - Linux
  
- **Tests performed:**
  - ✅ `.gitattributes` file exists
  - ✅ Shell scripts have LF line endings (not CRLF)
  - ✅ `.gitattributes` enforces LF for `*.sh` files

## Why This Matters

### Bash 3.2 Compatibility (macOS)
macOS ships with Bash 3.2 (from 2007) due to GPL licensing. This version:
- ❌ Doesn't support associative arrays (`declare -A`)
- ❌ Doesn't support `&>>` redirect operator
- ✅ Supports indexed arrays
- ✅ Supports parameter expansion (`${var%%:*}`)

**The CI catches:**
- Use of Bash 4.0+ features that break on macOS
- Syntax errors specific to older Bash versions

### Line Ending Issues (CRLF vs LF)
Windows uses CRLF (`\r\n`), Unix/Mac use LF (`\n`). Shell scripts with CRLF fail on Mac/Linux with:
```
bash: $'\r': command not found
```

**The CI catches:**
- CRLF line endings in shell scripts
- Missing or incorrect `.gitattributes` configuration

### Cross-Platform Installation
Different platforms have different:
- File path separators (`/` vs `\`)
- Command availability (`cp` vs `Copy-Item`)
- Shell environments (Bash vs PowerShell)

**The CI catches:**
- Platform-specific bugs in installers
- Missing files or incorrect paths
- Validation failures on fresh installations

## How to Read CI Results

### ✅ All Checks Passed
```
✓ Test Bash Installer on ubuntu-latest
✓ Test Bash Installer on macos-latest
✓ Test Bash Installer on macos-13
✓ Test PowerShell Installer on Windows
✓ Verify Line Endings
```
**Safe to merge!**

### ❌ Check Failed
Click on the failed check to see:
1. **Which platform failed** (e.g., `macos-latest`)
2. **Which step failed** (e.g., "Test installer")
3. **Error message** (e.g., "syntax error: invalid arithmetic operator")

**Example failure:**
```
Test Bash Installer on macos-latest
  ✓ Checkout code
  ✓ Check Bash version
  ✓ Check line endings
  ✗ Test installer help
    Error: install.sh: line 208: syntax error: invalid arithmetic operator
```

This tells you:
- **Platform:** macOS (Bash 3.2)
- **Problem:** Line 208 has Bash 4.0+ syntax
- **Fix:** Use Bash 3.2 compatible syntax

## Local Testing

### Test on macOS (if you have a Mac)
```bash
bash product/scripts/install.sh --help
```

### Test on Linux (using Docker)
```bash
docker run -it --rm -v $(pwd):/workspace ubuntu:latest bash
cd /workspace
bash product/scripts/install.sh --help
```

### Test on Windows (PowerShell)
```powershell
powershell -File product/scripts/install.ps1 -Help
```

### Test line endings
```bash
# Check for CRLF
file product/scripts/*.sh

# Should show: "ASCII text" (LF)
# Should NOT show: "ASCII text, with CRLF line terminators"
```

## Common Issues Caught by CI

### Issue 1: Associative Arrays on macOS
**Error:**
```
install.sh: line 208: syntax error: invalid arithmetic operator
```

**Cause:** Used `declare -A` (Bash 4.0+) on macOS (Bash 3.2)

**Fix:** Use indexed arrays with colon-delimited strings

### Issue 2: CRLF Line Endings
**Error:**
```
bash: $'\r': command not found
install.sh: line 54: syntax error near unexpected token `$'do\r''
```

**Cause:** Shell scripts have Windows line endings (CRLF)

**Fix:** 
1. Convert to LF: `dos2unix product/scripts/*.sh`
2. Ensure `.gitattributes` has: `*.sh text eol=lf`

### Issue 3: Template/Validator Mismatch
**Error:**
```
[X] CHANGELOG validation: ERROR - Missing '## [Unreleased]' section
```

**Cause:** Template has `## [Unreleased] - v0.7.0-dev` but validator expects exact `## [Unreleased]`

**Fix:** Update template to match validator regex

## Workflow Configuration

### Adding New Tests
Edit `.github/workflows/test-installer.yml`:

```yaml
- name: Your new test
  run: |
    # Your test commands here
```

### Testing on Additional Platforms
Add to the matrix:

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest, macos-13, ubuntu-20.04]
```

### Changing Trigger Branches
```yaml
on:
  push:
    branches: [ main, development, feature/* ]
```

## Cost & Limits

**GitHub Actions for public repositories:**
- ✅ **FREE** unlimited minutes
- ✅ Concurrent jobs (up to 20)
- ✅ All platforms (Linux, macOS, Windows)

**GitHub Actions for private repositories:**
- 2,000 minutes/month free
- Linux: 1x multiplier
- macOS: 10x multiplier (200 minutes = 2,000 macOS minutes)
- Windows: 2x multiplier

**Current usage (per run):**
- ~5 minutes total (3 jobs run in parallel)
- ~15 minutes/month (assuming 3 runs/month)

## Best Practices

1. **Run CI before merging** - Never merge if CI is red
2. **Test locally first** - Don't rely on CI to catch basic syntax errors
3. **Keep workflows fast** - Parallel jobs, minimal dependencies
4. **Use fail-fast: false** - See all platform failures, not just the first
5. **Cache dependencies** - If you add package installations, cache them

## Troubleshooting

### CI passes but Mac user reports failure
- User might have modified files locally
- User might have different macOS version
- Ask user to run: `bash --version` and `file install.sh`

### CI fails on macOS but passes locally (Windows)
- You're probably using Bash 4.0+ features
- Test locally with: `docker run -it bash:3.2 bash`
- Or use GitHub Codespaces (has Bash 4.4+)

### Line ending check fails
- Run: `git add --renormalize .`
- Commit and push
- CI should pass on next run

## Future Enhancements

Potential additions to CI:

- [ ] **Shellcheck** - Static analysis for shell scripts
- [ ] **Markdown linting** - Validate template formatting
- [ ] **Token counting** - Verify templates stay under limits
- [ ] **Security scanning** - Check for vulnerabilities
- [ ] **Release automation** - Auto-create releases on version tags
- [ ] **Deployment** - Auto-update documentation site

## References

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Bash 3.2 Manual](https://www.gnu.org/software/bash/manual/bash.html)
- [Git Attributes](https://git-scm.com/docs/gitattributes)

