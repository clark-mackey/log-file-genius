---
fragment: status-update
order: 20
targets: agents_md, claude_rules, augment_rules
summary: "@status update" command — concise project state summary.
type: "manual"
---

# status-update (Manual Command)

## Trigger

When the user says **"@status update"** or **"status update"**, execute this command.

---

## What to Do

Provide a concise 3-5 bullet point summary of the project's current state and next steps.

### Step 1: Read These Files (in parallel)

Read paths from `.logfile-config.yml` → `paths` (fallback `logs/`):
- **STATE** → "Current Context" + "Last Session" sections (current state)
- **CHANGELOG** → "Unreleased" section
- **ADR README** → Recent ADRs (if any)

### Step 2: Extract Key Information
- **Current version** (from STATE Current Context)
- **Active branch** (from STATE Current Context)
- **Active phase** (from STATE Current Context)
- **Recent changes** (from CHANGELOG Unreleased - last 3-5 entries)
- **Current objectives** (from STATE Current Context - unchecked items)
- **Known risks/blockers** (from STATE Current Context)

### Step 3: Format the Output

Use this exact format:

```markdown
📍 **Status Update - [Project Name]**

**Current State:**
- **Version:** [version]
- **Phase:** [phase] - [brief description]
- **Branch:** [branch name]

**Recent Progress:**
- ✅ [Recent accomplishment 1]
- ✅ [Recent accomplishment 2]
- ✅ [Recent accomplishment 3]

**Next Up:**
- [Next objective 1]
- [Next objective 2]
- [Next objective 3]

**Risks/Blockers:**
- [Risk/blocker 1, or "None currently"]
```

---

## Example Output

```markdown
📍 **Status Update - Log File Genius**

**Current State:**
- **Version:** v0.1.0-dev (pre-release)
- **Phase:** Foundation - Repository structure complete, ready for launch
- **Branch:** main

**Recent Progress:**
- ✅ Created README.md with quick start and migration guide
- ✅ Added CONTRIBUTING.md for community engagement
- ✅ Moved Augment rules into starter pack for better distribution

**Next Up:**
- Set up GitHub repository features (About, Topics, Template button)
- Create issue templates for bug reports and feature requests
- Consider GitHub Pages for documentation hosting

**Risks/Blockers:**
- None currently
```

---

## Tips

- Keep it concise (3-5 bullets per section)
- Focus on actionable information
- Highlight what's changed recently
- Be specific about next steps
- Update if planning files are out of sync

