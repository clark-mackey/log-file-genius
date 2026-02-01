# Log File Genius - Claude Code Support

This package adds native Claude Code support to Log File Genius.

## File Structure

```
log-file-genius-claude-code/
├── templates/
│   ├── CLAUDE.md                      # Project root config
│   └── .claude/
│       ├── commands/
│       │   ├── devlog-entry.md        # /project:devlog-entry
│       │   ├── changelog-entry.md     # /project:changelog-entry
│       │   ├── adr-create.md          # /project:adr-create
│       │   └── state-update.md        # /project:state-update
│       ├── rules/
│       │   ├── logging.md             # Token budgets & formats
│       │   └── handoff-protocol.md    # Multi-agent coordination
│       └── hooks.json                 # Automation hooks
├── scripts/
│   ├── install-claude-code.sh         # Bash installer module
│   └── install-claude-code.ps1        # PowerShell installer module
└── README.md                          # This file
```

## Integration Instructions

### Option 1: Merge into existing installer

1. Copy `templates/` contents to `product/templates/`
2. Add the functions from `scripts/install-claude-code.sh` to `product/scripts/install.sh`
3. Add the functions from `scripts/install-claude-code.ps1` to `product/scripts/install.ps1`
4. Add detection logic to main installer flow

### Option 2: Manual installation

Copy these to your project:
- `templates/CLAUDE.md` → `./CLAUDE.md`
- `templates/.claude/` → `./.claude/`

## What Gets Installed

### CLAUDE.md (Project Root)
Main configuration that Claude Code reads on every session. Contains:
- Token budgets
- File locations
- Workflow instructions
- File references using `@` imports

### Slash Commands
| Command | Purpose |
|---------|---------|
| `/project:devlog-entry` | Add narrative entry to DEVLOG |
| `/project:changelog-entry` | Add factual entry to CHANGELOG |
| `/project:adr-create` | Create new Architecture Decision Record |
| `/project:state-update` | Update STATE.md for handoffs |

### Rules (Conditional)
- `logging.md` - Applies to `logs/**/*.md` files only
- `handoff-protocol.md` - Multi-agent coordination rules

### Hooks
- **SessionStart**: Displays current STATE.md
- **PreToolUse**: Shows state before file modifications
- **PostToolUse**: Prompts for CHANGELOG entry after file changes
- **SessionEnd**: Reminds to update STATE.md

## Usage After Installation

```bash
# Start Claude Code session
claude

# Use slash commands
/project:devlog-entry Implemented new auth flow
/project:changelog-entry
/project:state-update Task complete, ready for review
/project:adr-create Database migration strategy
```

## Compatibility

- Claude Code CLI v1.0+
- Works alongside existing Augment/Cursor/Copilot configurations
- Does not conflict with `.augment/rules/`

## Notes

- `hooks.json` may need adjustment based on your Claude Code version
- Rules use `paths` frontmatter for conditional loading
- CLAUDE.md uses `@` imports for progressive disclosure
