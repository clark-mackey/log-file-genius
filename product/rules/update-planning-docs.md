---
fragment: update-planning-docs
order: 30
targets: agents_md, claude_rules, augment_rules
summary: "@update planning docs" command — guided CHANGELOG/DEVLOG/ADR/STATE updates.
type: "manual"
---

# update-planning-docs (Manual Command)

## Trigger

When the user says **"@update planning docs"** or **"update planning docs"**, execute this command.

---

## What to Do

Guide the user through updating CHANGELOG, DEVLOG, or other planning documentation.

### Step 1: Ask What Needs Updating

Present these options:

```
Which planning document(s) need updating?

1. **CHANGELOG** - Add technical change entries
2. **DEVLOG** - Add decision/milestone narrative
3. **STATE (Current Context + Last Session)** - Update project state
4. **ADR** - Create architectural decision record
5. **All of the above** - Comprehensive update

Please specify (1-5):
```

### Step 2: Execute Based on Choice

#### Option 1: Update CHANGELOG

1. Ask: "What changed? (files, features, fixes)"
2. Determine category: Added, Changed, Fixed, Deprecated, Removed, Security
3. Open CHANGELOG (path from `.logfile-config.yml` → `paths.changelog`, default `logs/CHANGELOG.md`)
4. Add entry under "Unreleased" section in appropriate category
5. Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\` (if available)`
6. Show the entry to user for confirmation

**Example:**
```markdown
### Added
- Improved Augment rules with pre-commit checklist. Files: `.augment/rules/log-file-maintenance.md`
```

#### Option 2: Update DEVLOG

1. Ask: "What milestone/decision needs documenting?"
2. Gather information:
   - What was the situation/context?
   - What was the challenge/problem?
   - What decision was made?
   - Why does it matter?
   - What was the result?
   - What files changed?
3. Open DEVLOG (path from `.logfile-config.yml` → `paths.devlog`, default `logs/DEVLOG.md`)
4. Add entry to "Daily Log" section (newest first)
5. Use format: Situation/Challenge/Decision/Why/Result/Files
6. Keep entry 150-250 words
7. Show entry to user for confirmation

**Example:**
```markdown
### 2025-10-31: Improving Augment Rules - Making Automation Actually Work

**The Situation:** The existing log-file-maintenance rule wasn't triggering automatic updates...

**The Challenge:** Rules were passive guidance, not active automation...

**The Decision:** Rewrote rules with explicit pre-commit checklist...

**Why This Matters:** Automatic planning file updates are core to the system...

**The Result:** New rules include mandatory checklists and verification steps...

**Files Changed:** `.augment/rules/log-file-maintenance.md`
```

#### Option 3: Update STATE (Current Context + Last Session)

1. Ask: "What changed in project state?"
   - Version?
   - Branch?
   - Phase?
   - Objectives?
   - Risks/blockers?
2. Read `.logfile-config.yml` → `paths.state` (fallback `logs/STATE.md`)
3. Update "Current Context" and/or "Last Session" sections as needed
4. Show changes to user for confirmation

#### Option 4: Create ADR

1. Ask: "What architectural decision needs documenting?"
2. Get next ADR number from `logs/adr/README.md`
3. Use template from `.log-file-genius/product/templates/ADR_template.md`
4. Create file: `logs/adr/NNN-short-title.md`
5. Fill in: Context, Decision, Consequences, Alternatives
6. Update `logs/adr/README.md` index
7. Show ADR to user for confirmation

#### Option 5: All of the Above

Execute steps 1-4 in sequence, asking for information for each.

---

## Step 3: Offer to Commit

After updating files, ask:

```
Planning files updated. Would you like me to:
1. Commit these changes now
2. Let you review first
3. Include in your next commit
```

---

## Key Files Reference

Read paths from `.logfile-config.yml` → `paths` (fallback `logs/`):
- **CHANGELOG:** `logs/CHANGELOG.md`
- **DEVLOG:** `logs/DEVLOG.md`
- **STATE:** `logs/STATE.md`
- **ADRs:** `logs/adr/` directory
- **Templates:** `.log-file-genius/product/templates/` directory
- **How-to guide:** `.log-file-genius/product/docs/log_file_how_to.md`

---

## Tips

- **Be specific:** Vague entries like "Updated files" aren't helpful
- **Include context:** Explain WHY, not just WHAT
- **Reference files:** Always include file paths
- **Keep it concise:** CHANGELOG = 1 line, DEVLOG = 150-250 words
- **Link commits:** Include commit hashes when available

