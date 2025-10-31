# Augment Starter Pack

Get up and running with Log File Genius in Augment in under 2 minutes.

## Quick Setup

1. **Copy the `.augment/` directory to your project root:**
   ```bash
   cp -r .augment/ /path/to/your/project/
   ```

2. **Open your project in Augment:**
   - Augment will automatically detect and load the rules from `.augment/rules/`

3. **Start using the system:**
   - Make a code change
   - Commit it
   - Augment will automatically update your CHANGELOG (if the rule is active)

## What's Included

### Core Files
- **`.augment/rules/log-file-maintenance.md`** - Always-active maintenance rules
- **`.augment/rules/status-update.md`** - Status update command
- **`.augment/rules/update-planning-docs.md`** - Documentation update command

### Templates
All the standard Log File Genius templates are available in the `templates/` directory:
- `CHANGELOG_template.md`
- `DEVLOG_template.md`
- `STATE_template.md`
- `ADR_template.md`

## Available Commands

Once set up, you can use these commands with Augment:

| Command | What It Does |
|---------|--------------|
| **"@status update"** | Provides a 3-5 bullet point summary of project status |
| **"@update planning docs"** | Guides you through updating CHANGELOG, DEVLOG, or PRD |

## Customization

### Adding Custom Rules

1. Create a new file in `.augment/rules/`:
   ```bash
   touch .augment/rules/my-custom-rule.md
   ```

2. Add your rule content following this format:
   ```markdown
   # My Custom Rule
   
   When the user says "trigger phrase", do this:
   
   1. Step 1
   2. Step 2
   3. Step 3
   ```

3. Augment will automatically load the new rule on next session

### Adjusting Token Budgets

Edit `.augment/rules/log-file-maintenance.md` to adjust token targets:

```markdown
## Token Budget Targets

- **CHANGELOG:** <10,000 tokens (adjust as needed)
- **DEVLOG:** <15,000 tokens (adjust as needed)
- **Combined:** <25,000 tokens (adjust as needed)
```

### Making Rules Always-On vs Manual

By default, `log-file-maintenance.md` is always active. To make it manual:

1. Rename the file to indicate manual trigger (e.g., `manual-log-file-maintenance.md`)
2. Update your workflow to explicitly invoke it when needed

## Troubleshooting

### Augment isn't loading the rules
- Make sure `.augment/rules/` directory exists in your project root
- Verify rule files have `.md` extension
- Try restarting Augment or reloading the project
- Check that the files aren't corrupted or empty

### Rules aren't being followed
- Verify the rule files exist in `.augment/rules/`
- Make sure you're using the exact command phrases (e.g., "@status update")
- Check if the rule is set to always-on or manual trigger
- Review the rule content for any syntax errors

### Token budgets are being exceeded
- Run the archival process (see `docs/log_file_how_to.md`)
- Adjust token targets in `log-file-maintenance.md`
- Consider condensing older entries
- Archive entries older than 30 days

### Augment is updating the wrong files
- Verify file paths in the rules match your project structure
- Check that you have the correct directory structure:
  - `docs/planning/CHANGELOG.md`
  - `docs/planning/DEVLOG.md`
  - `docs/adr/README.md`
- Update paths in rules if your structure differs

## Advanced Configuration

### Multi-Agent Coordination

If you're using multiple AI agents (Augment + Claude Code, etc.):

1. Enable `STATE.md` for real-time coordination
2. Update `STATE.md` at the start/end of each work session
3. Have each agent check `STATE.md` before starting work
4. Use the handoff protocol in `docs/log_file_how_to.md`

### Custom File Paths

If your project uses different paths:

1. Edit each rule file in `.augment/rules/`
2. Update file path references to match your structure
3. Test with a small change to verify paths are correct

Example path customization:
```markdown
# Before (default)
Update `docs/planning/CHANGELOG.md`

# After (custom)
Update `documentation/logs/CHANGELOG.md`
```

## Next Steps

1. **Read the full methodology:** `docs/log_file_how_to.md`
2. **Check out examples:** `examples/` directory
3. **Customize for your workflow:** Adjust rules and token budgets as needed
4. **Join the community:** Share your experience in GitHub Discussions

## Support

- 🐛 [Report issues](https://github.com/clark-mackey/log-file-genius/issues)
- 💬 [Join discussions](https://github.com/clark-mackey/log-file-genius/discussions)
- 📖 [Read the docs](https://github.com/clark-mackey/log-file-genius)

## Tips for Success

### Best Practices
- **Commit frequently** - Smaller, focused commits make better CHANGELOG entries
- **Update STATE.md regularly** - Especially in multi-agent environments
- **Archive monthly** - Keep token budgets under control
- **Review before archiving** - Make sure important context is preserved

### Common Patterns
- **After each commit:** Let Augment update CHANGELOG automatically
- **After major decisions:** Manually update DEVLOG with context
- **Before switching agents:** Update STATE.md with current status
- **Weekly:** Review token budgets and archive if needed

### Integration with Git Workflow
```bash
# Make changes
git add .
git commit -m "Add feature X"

# Augment automatically updates CHANGELOG

# For significant changes, also update DEVLOG
# Ask Augment: "@update planning docs"

# Push changes
git push
```

---

**Status:** ✅ Available (v1.0)

**Tested with:** Augment v3.x

**Last Updated:** October 2025

