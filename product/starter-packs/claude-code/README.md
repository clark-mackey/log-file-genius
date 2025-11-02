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

3. **Copy the profile configuration (optional but recommended):**
   ```bash
   # Copy the default profile configuration
   cp starter-packs/claude-code/.logfile-config.yml /path/to/your/project/
   ```

   **Choose your profile:** Edit `.logfile-config.yml` and set your profile:
   - `solo-developer` (default) - Individual developers, flexible
   - `team` - Teams of 2+, consistent documentation
   - `open-source` - Public projects, strict formatting
   - `startup` - MVPs/prototypes, minimal overhead

   See `product/docs/profile-selection-guide.md` for help choosing.

4. **Copy the validation scripts (optional but recommended):**
   ```bash
   # Copy validation scripts (includes both PowerShell and Bash versions)
   cp -r product/starter-packs/claude-code/scripts/ /path/to/your/project/

   # Copy git hook template
   cp -r starter-packs/claude-code/.git-hooks/ /path/to/your/project/

   # Install git hook (optional - enables automatic validation before commits)
   cp .git-hooks/pre-commit .git/hooks/pre-commit
   chmod +x .git/hooks/pre-commit  # Mac/Linux only
   ```

   **Note:** The validation scripts include both `validate-log-files.ps1` (PowerShell for Windows) and `validate-log-files.sh` (Bash for Mac/Linux/WSL). The git hook automatically detects your platform and runs the appropriate script.

5. **Open your project in Claude Code:**
   - Claude Code will automatically detect and load `project_instructions.md`

6. **Start using the system:**
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

### Profile Configuration (Optional but Recommended)
- **`.logfile-config.yml`** - Profile configuration file
  - Choose from 4 predefined profiles (solo-developer, team, open-source, startup)
  - Customize token targets, validation strictness, archival settings
  - See `product/docs/profile-selection-guide.md` for help choosing

### Validation Tools (Optional but Recommended)
- **`product/scripts/validate-log-files.ps1`** - PowerShell validation script (Windows)
- **`product/scripts/validate-log-files.sh`** - Bash validation script (Mac/Linux/WSL)
- **`.git-hooks/pre-commit`** - Git hook template for automatic validation (cross-platform)
- **Profile-aware:** Validation scripts automatically read `.logfile-config.yml` and apply profile settings

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
| **Run validation** | Manually run `.\scripts\validate-log-files.ps1` to check log files |

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

### Adjusting Token Budgets and Validation

**Recommended:** Use the profile system by editing `.logfile-config.yml`:

```yaml
profile: solo-developer

# Override token targets
overrides:
  token_targets:
    changelog_error: 12000  # Increase from default 10,000
    devlog_error: 20000     # Increase from default 15,000
```

**Alternative:** Edit `.claude/rules/log-file-maintenance.md` to adjust token targets (legacy method):

```markdown
## Token Budget Targets

- **CHANGELOG:** <10,000 tokens (adjust as needed)
- **DEVLOG:** <15,000 tokens (adjust as needed)
- **Combined:** <25,000 tokens (adjust as needed)
```

**Note:** The profile system (`.logfile-config.yml`) is the recommended approach as it integrates with validation scripts and provides more flexibility.

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

