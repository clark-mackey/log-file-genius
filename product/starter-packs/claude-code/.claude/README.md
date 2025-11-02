# Claude Code Configuration for Log File Genius

This directory contains Claude Code-specific project instructions and rules for the Log File Genius system.

## Structure

```
.claude/
├── README.md                           # This file
├── project_instructions.md             # Main project instructions (always loaded)
└── rules/
    ├── log-file-maintenance.md         # Always-active maintenance rules
    ├── status-update.md                # Command: "status update"
    └── update-planning-docs.md         # Command: "update planning docs"
```

## How It Works

### Main Instructions
- **`project_instructions.md`** - Loaded automatically by Claude Code
- Contains core principles, available commands, and quick reference

### Rules Directory
- **`log-file-maintenance.md`** - Always-active rules for maintaining logs
- **`status-update.md`** - Invoked when user says "status update"
- **`update-planning-docs.md`** - Invoked when user says "update planning docs"

## Usage with Claude Code

1. **Automatic Loading:**
   - Claude Code automatically loads `project_instructions.md` when you open this project
   - The maintenance rules are always active

2. **Manual Commands:**
   - Say "status update" to get a project status summary
   - Say "update planning docs" to follow the documentation update process

3. **Customization:**
   - You can add more rules in the `rules/` directory
   - Reference them in `project_instructions.md` under "Available Commands"

## Comparison with Augment

This `.claude/` directory mirrors the `.augment/` directory structure:

| Augment | Claude Code | Purpose |
|---------|-------------|---------|
| `.augment/rules/log-file-maintenance.md` | `.claude/rules/log-file-maintenance.md` | Always-active maintenance rules |
| `.augment/rules/status-update.md` | `.claude/rules/status-update.md` | Status update command |
| `.augment/rules/update-planning-docs.md` | `.claude/rules/update-planning-docs.md` | Documentation update command |

**Note:** Internal rules (avoid-log-file-confusion, correct-project-identity, log-file-confusion-guard) are excluded from the repository via `.gitignore` and should be created locally if needed.

## For Contributors

If you're using Claude Code and want to contribute to this project:

1. The `.claude/` directory is included in the repository
2. Internal/private rules are in `.gitignore` and won't be committed
3. Follow the same log file maintenance practices as described in `docs/log_file_how_to.md`

