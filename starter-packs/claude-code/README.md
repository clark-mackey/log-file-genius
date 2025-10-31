# Claude Code Starter Pack

Get up and running with Log File Genius in Claude Code in under 2 minutes.

## Quick Setup

1. **Copy the `.claude/` directory from this starter pack to your project root:**
   ```bash
   # From the log-file-genius repository
   cp -r starter-packs/claude-code/.claude/ /path/to/your/project/
   ```

2. **Copy the templates to your project:**
   ```bash
   cp -r templates/ /path/to/your/project/
   ```

3. **Open your project in Claude Code:**
   - Claude Code will automatically detect and load `project_instructions.md`

4. **Start using the system:**
   - Make a code change
   - Commit it
   - Claude will automatically update your CHANGELOG (if the rule is active)

## What's Included in This Starter Pack

### Claude Code Configuration
- **`.claude/project_instructions.md`** - Main project instructions
- **`.claude/README.md`** - Documentation for the Claude setup
- **`.claude/rules/log-file-maintenance.md`** - Always-active maintenance rules (improved v2.0)
- **`.claude/rules/status-update.md`** - Status update command (improved v2.0)
- **`.claude/rules/update-planning-docs.md`** - Documentation update command (improved v2.0)

### Templates (Copy from main repository)
You'll need to copy the templates from the main `templates/` directory:
- `CHANGELOG_template.md`
- `DEVLOG_template.md`
- `STATE_template.md`
- `ADR_template.md`

## Available Commands

Once set up, you can use these commands with Claude Code:

| Command | What It Does |
|---------|--------------|
| **"status update"** | Provides a 3-5 bullet point summary of project status |
| **"update planning docs"** | Guides you through updating CHANGELOG, DEVLOG, or PRD |

## Customization

### Adding Custom Rules

1. Create a new file in `.claude/rules/`:
   ```bash
   touch .claude/rules/my-custom-rule.md
   ```

2. Add your rule content following this format:
   ```markdown
   # My Custom Rule
   
   When the user says "trigger phrase", do this:
   
   1. Step 1
   2. Step 2
   3. Step 3
   ```

3. Reference it in `.claude/project_instructions.md`:
   ```markdown
   ## Available Commands
   
   - **"trigger phrase"** → See `.claude/rules/my-custom-rule.md`
   ```

### Adjusting Token Budgets

Edit `.claude/rules/log-file-maintenance.md` to adjust token targets:

```markdown
## Token Budget Targets

- **CHANGELOG:** <10,000 tokens (adjust as needed)
- **DEVLOG:** <15,000 tokens (adjust as needed)
- **Combined:** <25,000 tokens (adjust as needed)
```

## Troubleshooting

### Claude Code isn't loading the instructions
- Make sure `.claude/project_instructions.md` exists in your project root
- Try restarting Claude Code
- Check that the file isn't corrupted or empty

### Rules aren't being followed
- Verify the rule files exist in `.claude/rules/`
- Check that they're referenced in `project_instructions.md`
- Make sure you're using the exact command phrases

### Token budgets are being exceeded
- Run the archival process (see `docs/log_file_how_to.md`)
- Adjust token targets in `log-file-maintenance.md`
- Consider condensing older entries

## Next Steps

1. **Read the full methodology:** `docs/log_file_how_to.md`
2. **Check out examples:** `examples/` directory
3. **Customize for your workflow:** Adjust rules and token budgets as needed

## Support

- 🐛 [Report issues](https://github.com/clark-mackey/log-file-genius/issues)
- 💬 [Join discussions](https://github.com/clark-mackey/log-file-genius/discussions)
- 📖 [Read the docs](https://github.com/clark-mackey/log-file-genius)

---

**Status:** ✅ Available (v1.0)

