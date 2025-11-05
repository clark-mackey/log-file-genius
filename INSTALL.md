# Installation Guide

**Quick installation guide for Log File Genius - a token-efficient documentation system for AI-assisted development.**

---

## Prerequisites

- Git installed
- A project with git initialized (`git init`)
- An AI coding assistant (Augment Code, Claude Code, Cursor, etc.)

---

## One-Command Installation

### Bash/Mac/Linux

```bash
git submodule add -b main \
  https://github.com/clark-mackey/log-file-genius.git \
  .log-file-genius && \
  ./.log-file-genius/product/scripts/install.sh
```

### PowerShell/Windows

```powershell
git submodule add -b main `
  https://github.com/clark-mackey/log-file-genius.git `
  .log-file-genius; `
  .\.log-file-genius\product\scripts\install.ps1
```

---

## What the Installer Does

The installer will:

1. **Detect your AI assistant** - Automatically detects Augment Code, Claude Code, or prompts for manual selection
2. **Prompt for profile** - Choose from: solo-developer, team, open-source, or startup
3. **Create folder structure** - Creates `logs/`, `logs/adr/`, `logs/incidents/`
4. **Install templates** - Copies CHANGELOG, DEVLOG, STATE, and ADR templates to `logs/`
5. **Install AI rules** - Copies AI assistant rules to `.augment/rules/` or `.claude/rules/`
6. **Create config file** - Generates `.logfile-config.yml` with your profile settings
7. **Validate installation** - Checks that all required files exist

---

## What Gets Installed

### Visible Files
- `logs/CHANGELOG.md` - Technical change log (what changed, when, where)
- `logs/DEVLOG.md` - Development narrative (why changes were made, decisions, context)
- `logs/STATE.md` - Current project state (active agent, current task)
- `logs/adr/TEMPLATE.md` - Architecture Decision Record template
- `.logfile-config.yml` - Profile configuration and settings

### AI Assistant Rules
- `.augment/rules/log-file-maintenance.md` (for Augment Code)
- `.claude/rules/log-file-maintenance.md` (for Claude Code)
- Additional AI-specific rules and instructions

### Hidden Source Repository
- `.log-file-genius/` - Git submodule containing templates, scripts, and documentation (for updates)

---

## Installation Options

### Force Reinstall

If you need to reinstall or update:

```bash
# Bash/Mac/Linux
./.log-file-genius/product/scripts/install.sh --force

# PowerShell/Windows
.\.log-file-genius\product\scripts\install.ps1 -Force
```

The `--force` flag will:
- Overwrite existing log files (backup first!)
- Reinstall AI rules
- Regenerate config file

### Profile Selection

During installation, you'll be prompted to choose a profile:

- **solo-developer** (default) - Flexible, minimal overhead, DEVLOG optional
- **team** - Stricter validation, required DEVLOG for significant changes
- **open-source** - Strict formatting, public-facing documentation standards
- **startup** - Minimal overhead, fast iteration, DEVLOG optional

See `.log-file-genius/product/docs/profile-selection-guide.md` for detailed comparison.

---

## Verification

After installation, verify everything is working:

```bash
# Bash/Mac/Linux
./.log-file-genius/product/scripts/validate-log-files.sh

# PowerShell/Windows
.\.log-file-genius\product\scripts\validate-log-files.ps1
```

Expected output:
```
[OK] CHANGELOG validation passed
[OK] DEVLOG validation passed
[OK] Token counts within limits
```

---

## Next Steps: Document the Installation

After installation completes, **copy and paste this prompt to your AI assistant:**

```
I just installed Log File Genius. Please:
1. Update CHANGELOG.md with what was installed
2. Update DEVLOG.md with why we installed it
3. Create an ADR documenting the architectural decision
   to adopt Log File Genius for project documentation
```

**This will:**
- Show you how the system works
- Create your first log entries
- Document the architectural decision
- Validate that AI rules are working correctly

---

## Troubleshooting

### "No rules files found" in AI assistant

**Cause:** The installer didn't run, or AI rules weren't copied.

**Fix:**
```bash
# Re-run installer
./.log-file-genius/product/scripts/install.sh --force
```

### "Template not found" errors

**Cause:** Git submodule not initialized or incomplete.

**Fix:**
```bash
# Initialize and update submodule
git submodule update --init --recursive
```

### "Permission denied" on Windows

**Cause:** PowerShell execution policy blocking scripts.

**Fix:**
```powershell
# Allow script execution (run as Administrator)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Then re-run installer
.\.log-file-genius\product\scripts\install.ps1
```

### Validation fails after installation

**Cause:** Log files not created or in wrong location.

**Fix:**
```bash
# Check what was created
ls -la logs/

# Re-run installer with force flag
./.log-file-genius/product/scripts/install.sh --force
```

---

## Updating Log File Genius

To update to the latest version:

```bash
# Update the submodule
cd .log-file-genius && git pull && cd ..

# Re-run installer (preserves customizations)
./.log-file-genius/product/scripts/install.sh --force
```

---

## Uninstalling

To remove Log File Genius:

```bash
# Remove installed files
rm -rf logs/ .augment/rules/ .claude/rules/ .logfile-config.yml

# Remove submodule
git submodule deinit -f .log-file-genius
git rm -f .log-file-genius
rm -rf .git/modules/.log-file-genius
```

---

## Additional Resources

- **Full Documentation:** `.log-file-genius/product/docs/log_file_how_to.md`
- **Profile Guide:** `.log-file-genius/product/docs/profile-selection-guide.md`
- **Validation Guide:** `.log-file-genius/product/docs/validation-guide.md`
- **Migration Guide:** `.log-file-genius/product/docs/MIGRATION_GUIDE.md`
- **GitHub Repository:** https://github.com/clark-mackey/log-file-genius

---

## Support

- **Report bugs:** https://github.com/clark-mackey/log-file-genius/issues
- **Request features:** https://github.com/clark-mackey/log-file-genius/issues
- **Discussions:** https://github.com/clark-mackey/log-file-genius/discussions

---

**Installation complete? Don't forget to document it with your AI assistant using the prompt above!**

