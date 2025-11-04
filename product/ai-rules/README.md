# AI Assistant Rules

This directory contains AI assistant rules for different platforms.

## Structure

- **augment/** - Rules for Augment AI assistant
- **claude-code/** - Rules for Claude Code assistant

## Installation

These rules are automatically installed by the Log File Genius installer based on your AI assistant choice.

## Manual Installation

If you need to manually install rules:

### For Augment
```bash
cp -r augment/.augment/rules/* .augment/rules/
```

### For Claude Code
```bash
cp -r claude-code/.claude/rules/* .claude/rules/
cp claude-code/.claude/project_instructions.md .claude/
```

## Rules Included

All platforms include:
- **log-file-maintenance.md** - Core rules for maintaining CHANGELOG, DEVLOG, and other log files
- **status-update.md** - Manual command for getting project status updates
- **update-planning-docs.md** - Manual command for guided log file updates

## Documentation

For more information on how these rules work, see:
- `.log-file-genius/docs/log_file_how_to.md` - Complete guide to the log file system
- `.log-file-genius/templates/` - Template files for all log types

