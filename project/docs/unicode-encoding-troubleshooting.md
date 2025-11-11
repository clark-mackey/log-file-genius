# Unicode & Encoding Best Practices

**Purpose:** Prevent encoding issues that can break CI/CD pipelines and cross-platform compatibility.

---

## The Problem

Unicode characters (like `→`, `•`, `✓`, `⚠`) can cause issues in:
- **GitHub Actions workflows** - JSON parsing failures
- **PowerShell scripts** - Character encoding errors
- **Cross-platform compatibility** - Different terminal rendering
- **Git operations** - Line ending and encoding conflicts

### Real Example

In November 2025, we discovered that DEVLOG.md contained **double-encoded Unicode arrows** (`â†'` instead of `→`). This caused:
- GitHub Actions validation workflow to fail
- JSON parsing errors in CI environment
- Exit code 1 with no clear error message

**Root cause:** The Unicode arrow `→` (U+2192, bytes `e28692`) got corrupted to `â†'` (bytes `c3a2e280a0e28099`) through double-encoding.

---

## Prevention Strategy

### 1. Use ASCII Alternatives

**Instead of Unicode, use ASCII:**

| ❌ Unicode | ✅ ASCII | Use Case |
|-----------|---------|----------|
| `→` | `->` | Arrows, navigation |
| `←` | `<-` | Back references |
| `↑` | `^` | Upward direction |
| `↓` | `v` | Downward direction |
| `•` | `-` | Bullet points |
| `✓` | `[OK]` | Success indicators |
| `✗` | `[X]` | Failure indicators |
| `⚠` | `[WARNING]` | Warnings |
| `ℹ` | `[INFO]` | Information |

**Exception:** Unicode is acceptable in:
- User-facing documentation (README.md navigation)
- Examples and tutorials
- Content that won't be parsed by scripts

### 2. Regular Scanning

Run the Unicode checker before committing:

**PowerShell:**
```powershell
.\product\scripts\check-unicode.ps1
```

**Bash:**
```bash
./product/scripts/check-unicode.sh
```

**To auto-fix:**
```powershell
.\product\scripts\check-unicode.ps1 -Fix
```

```bash
./product/scripts/check-unicode.sh --fix
```

### 3. Git Hooks (Optional)

Add a pre-commit hook to automatically check for Unicode:

**`.git/hooks/pre-commit`:**
```bash
#!/bin/bash
# Check for problematic Unicode characters

if ./product/scripts/check-unicode.sh; then
    exit 0
else
    echo ""
    echo "Unicode characters found! Run with --fix to replace them."
    echo "Or commit with --no-verify to skip this check."
    exit 1
fi
```

Make it executable:
```bash
chmod +x .git/hooks/pre-commit
```

### 4. Editor Configuration

**VS Code** - Add to `.vscode/settings.json`:
```json
{
  "files.encoding": "utf8",
  "files.eol": "\n",
  "files.insertFinalNewline": true,
  "files.trimTrailingWhitespace": true
}
```

**EditorConfig** - Add to `.editorconfig`:
```ini
[*.{md,txt,yml,yaml}]
charset = utf-8
end_of_line = lf
insert_final_newline = true
trim_trailing_whitespace = true
```

---

## Fixing Encoding Issues

### Symptoms

- GitHub Actions fails with "Process completed with exit code 1"
- JSON parsing errors in CI
- Strange characters like `â†'`, `â€¢`, `âœ"` in files
- PowerShell script errors about unexpected characters

### Diagnosis

**Check for double-encoded characters:**
```bash
# Search for common double-encoded patterns
git grep -n "â†\|â€\|âœ" -- "*.md"
```

**Check file encoding:**
```bash
file -bi logs/DEVLOG.md
# Should show: text/plain; charset=utf-8
```

**Check for Unicode characters:**
```bash
./product/scripts/check-unicode.sh
```

### Fix

**Option 1: Use the checker script**
```bash
./product/scripts/check-unicode.sh --fix
```

**Option 2: Manual replacement**
```python
# Python script to fix double-encoded characters
with open('logs/DEVLOG.md', 'rb') as f:
    content = f.read()

# Replace corrupted arrow
content = content.replace(b'\xc3\xa2\xe2\x80\xa0\xe2\x80\x99', b'->')

with open('logs/DEVLOG.md', 'wb') as f:
    f.write(content)
```

**Option 3: Git restore and re-edit**
```bash
# Restore from last good commit
git restore logs/DEVLOG.md

# Re-apply changes using ASCII characters
```

---

## CI/CD Integration

### GitHub Actions

Add Unicode check to validation workflow:

```yaml
- name: Check for problematic Unicode
  run: |
    chmod +x product/scripts/check-unicode.sh
    ./product/scripts/check-unicode.sh
```

### Pre-commit CI

Add to `.github/workflows/pre-commit.yml`:

```yaml
name: Pre-commit Checks
on: [push, pull_request]

jobs:
  unicode-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Check Unicode
        run: ./product/scripts/check-unicode.sh
```

---

## When Unicode is OK

**Acceptable use cases:**
1. **User-facing documentation** - README navigation, marketing content
2. **Examples and tutorials** - Showing real-world usage
3. **Comments in code** - Not parsed by scripts
4. **Intentional formatting** - When visual clarity is critical

**Not acceptable:**
1. **Log files** (CHANGELOG, DEVLOG, ADRs) - Parsed by scripts
2. **Configuration files** (YAML, JSON) - Parsed by tools
3. **Scripts** (PowerShell, Bash) - Execution issues
4. **CI/CD workflows** - Parsing failures

---

## Troubleshooting

### PowerShell Can't Read File

**Error:** "Unexpected token ')' in expression or statement"

**Fix:** Ensure UTF-8 encoding with BOM for PowerShell 5.1:
```powershell
$content = Get-Content file.ps1 -Raw
$content | Out-File file.ps1 -Encoding UTF8
```

### Git Shows File as Changed (No Visible Diff)

**Cause:** Line ending or encoding change

**Fix:**
```bash
# Normalize line endings
git add --renormalize .
```

### Bash Script Fails on Windows

**Cause:** CRLF line endings

**Fix:**
```bash
# Convert to LF
dos2unix product/scripts/*.sh
```

Or in Git:
```bash
git config core.autocrlf input
```

---

## Summary

✅ **DO:**
- Use ASCII alternatives for arrows, bullets, symbols
- Run `check-unicode.sh` before committing
- Use UTF-8 encoding with LF line endings
- Test scripts on both Windows and Linux

❌ **DON'T:**
- Use Unicode in log files (CHANGELOG, DEVLOG, ADRs)
- Use Unicode in scripts or configuration files
- Mix line endings (CRLF/LF) in the same file
- Assume Unicode will work across all platforms

---

**Related:**
- [Validation Guide](validation-guide.md) - How validation scripts work
- [Installer Testing Guide](installer-testing-guide.md) - Cross-platform testing
- [Log File How-To](log_file_how_to.md) - Log file best practices

