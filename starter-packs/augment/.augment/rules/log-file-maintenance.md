---
type: "always_apply"
---

# log-file-maintenance (Always Active - Non-Negotiable)

## ⚠️ CRITICAL: These Rules Are MANDATORY

This rule is ALWAYS active. You MUST follow these guidelines without exception. Failure to update planning files is a critical error.

---

## 🔴 BEFORE EVERY COMMIT - REQUIRED CHECKLIST

**Before running `git commit`, you MUST complete ALL of these steps:**

### Step 1: Update CHANGELOG.md (REQUIRED)
1. Open `docs/planning/CHANGELOG.md`
2. Add entry in the appropriate category under "Unreleased" section
3. Use format: `- Description. Files: \`path/to/file\`. Commit: \`hash\` (if available)`
4. Categories: Added, Changed, Fixed, Deprecated, Removed, Security

**Example:**
```markdown
### Added
- Augment starter pack with setup guide and rules. Files: `starter-packs/augment/README.md`, `starter-packs/augment/.augment/rules/*`
```

### Step 2: Update DEVLOG.md (If Milestone/Decision)
**Only if this commit represents:**
- A completed epic or major milestone
- An important architectural decision
- A significant change in direction
- A problem solved that required investigation

**Then add entry to:** `docs/planning/DEVLOG.md` → "Daily Log" section (newest first)

**Format:**
```markdown
### YYYY-MM-DD: Title - Brief Description

**The Situation:** What was the context?

**The Challenge:** What problem needed solving?

**The Decision:** What did we decide to do?

**Why This Matters:** Why is this important?

**The Result:** What was the outcome?

**Files Changed:** `path/to/file`
```

**Keep entries:** 150-250 words each

### Step 3: Include Planning Files in Commit
- Add CHANGELOG.md to the commit: `git add docs/planning/CHANGELOG.md`
- Add DEVLOG.md to the commit (if updated): `git add docs/planning/DEVLOG.md`
- Planning files should be committed WITH the code changes, not separately

### Step 4: Verify Before Committing
**Show this checklist to the user BEFORE committing:**

```
✅ Pre-Commit Checklist:
- [ ] CHANGELOG.md updated with entry for this change
- [ ] DEVLOG.md updated (if milestone/decision)
- [ ] Planning files added to commit
- [ ] Commit message is clear and descriptive
- [ ] Ready to commit
```

---

## 📋 AFTER EVERY COMMIT - VERIFICATION

**After committing, confirm to the user:**

```
✅ Commit complete: [commit hash]
✅ CHANGELOG.md updated: [entry added]
✅ DEVLOG.md updated: [yes/no - reason if no]
```

---

## 🔄 SESSION START - ALWAYS READ CONTEXT

**At the start of EVERY work session:**
1. Read `docs/planning/DEVLOG.md` → "Current Context (Source of Truth)" section
2. Note: Current version, active branch, phase, objectives, risks
3. Acknowledge to user: "I've read the current context. We're on [version], [phase], working on [objectives]."

---

## 📊 DAILY UPDATES - WHEN PROJECT STATE CHANGES

**Update DEVLOG Current Context when:**
- Version changes (e.g., v0.1.0 → v0.2.0)
- Branch changes (e.g., main → feature/new-feature)
- Phase changes (e.g., Foundation → Development)
- Objectives change (completed or new ones added)
- New risks/blockers identified

**Location:** `docs/planning/DEVLOG.md` → "Current Context (Source of Truth)" section

---

## 🗄️ ARCHIVAL PROCESS - TOKEN MANAGEMENT

**Trigger:** When CHANGELOG or DEVLOG exceed 10,000 tokens

**Action:**
1. Create archive directory: `docs/planning/archive/` (if doesn't exist)
2. Copy entries older than 2 weeks to archive file
3. Archive naming: `CHANGELOG-YYYY-MM.md` or `DEVLOG-YYYY-MM-Wn.md`
4. Remove archived entries from current file
5. Keep last 2 weeks of entries in current file

**Token Budget Targets:**
- **CHANGELOG:** <10,000 tokens (with archival)
- **DEVLOG:** <15,000 tokens (with archival)
- **Combined:** <25,000 tokens
- **Per entry:** 60-80 tokens (CHANGELOG), 150-250 tokens (DEVLOG)

---

## 🚫 COMMON MISTAKES TO AVOID

❌ **DON'T:** Commit code without updating CHANGELOG
✅ **DO:** Update CHANGELOG BEFORE every commit

❌ **DON'T:** Update planning files in a separate commit
✅ **DO:** Include planning files IN the same commit as code changes

❌ **DON'T:** Write vague CHANGELOG entries like "Updated files"
✅ **DO:** Write specific entries: "Add Augment starter pack with setup guide"

❌ **DON'T:** Skip DEVLOG entries for important decisions
✅ **DO:** Document WHY decisions were made, not just WHAT changed

❌ **DON'T:** Assume the user will update planning files themselves
✅ **DO:** Proactively update planning files as part of your workflow

---

## 📚 Quick Reference

- **Full documentation:** `docs/log_file_how_to.md`
- **Templates:** `templates/` directory
- **Current logs:** `docs/planning/` directory
- **ADRs:** `docs/adr/` directory

---

## 🎯 Success Criteria

**You're following this rule correctly when:**
1. ✅ Every commit includes updated CHANGELOG.md
2. ✅ Milestones/decisions are documented in DEVLOG.md
3. ✅ You show the pre-commit checklist before committing
4. ✅ You confirm what was updated after committing
5. ✅ Planning files are always in sync with code changes

