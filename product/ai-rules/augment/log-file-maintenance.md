# log-file-maintenance (Always Active - Non-Negotiable)

## ⚠️ CRITICAL: These Rules Are MANDATORY

This rule is ALWAYS active. You MUST follow these guidelines without exception.

---

## 🔴 BEFORE EVERY COMMIT - REQUIRED

**You MUST complete ALL steps before running `git commit`:**

### Step 1: Update CHANGELOG.md (REQUIRED)
1. Open `logs/CHANGELOG.md`
2. Add entry under "Unreleased" in appropriate category (Added/Changed/Fixed/Deprecated/Removed/Security)
3. Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``
4. See `.log-file-genius/templates/CHANGELOG_template.md` for examples

### Step 2: Update DEVLOG.md (If Milestone/Decision)
**Only if this commit is:** a completed epic, major milestone, architectural decision, or significant problem solved

1. Add entry to `logs/DEVLOG.md` → "Daily Log" section (newest first)
2. Use Situation/Challenge/Decision/Why/Result/Files format (see `.log-file-genius/templates/DEVLOG_template.md`)
3. Keep entries 150-250 words

### Step 3: Run Validation (OPTIONAL but Recommended)
**If validation script is available:**
```bash
.\.log-file-genius\scripts\validate-log-files.ps1  # Windows
./.log-file-genius/scripts/validate-log-files.sh   # Mac/Linux
```
- Validates CHANGELOG/DEVLOG format
- Checks token counts against profile limits (reads `.logfile-config.yml`)
- Applies profile-specific strictness settings
- Catches common errors before commit
- Can be skipped if not installed

**Note:** Validation scripts are profile-aware. If `.logfile-config.yml` exists, they will use profile-specific token targets and validation strictness.

### Step 4: Include Log Files in Commit
- `git add logs/CHANGELOG.md`
- `git add logs/DEVLOG.md` (if updated)
- `git add logs/adr/*.md` (if ADRs created/updated)
- Log files MUST be in the SAME commit as code changes

### Step 5: Show Pre-Commit Checklist
**Display this to user BEFORE committing:**
```
✅ Pre-Commit Checklist:
- [ ] CHANGELOG.md updated
- [ ] DEVLOG.md updated (if milestone)
- [ ] Validation run (if available)
- [ ] Planning files added to commit
- [ ] Ready to commit
```

---

## 📋 AFTER EVERY COMMIT - VERIFICATION (REQUIRED)

**You MUST verify your work after EVERY commit:**

### Step 1: Self-Assessment Checklist
**Answer these questions honestly:**
1. ✅ Did I update CHANGELOG.md? (yes/no)
2. ✅ Does the CHANGELOG entry match the actual code changes? (yes/no/unsure)
3. ✅ Did I include log files in the commit? (yes/no)
4. ✅ Are the file paths in the CHANGELOG entry correct? (yes/no)
5. ✅ Did I update DEVLOG if this was a milestone? (yes/no/not-applicable)
6. ✅ Did I run validation (if available)? (yes/no)

**If any answer is "no" or "unsure", you MUST fix it immediately before proceeding.**

### Step 2: Verify CHANGELOG Entry Accuracy
1. Run `git diff HEAD~1 logs/CHANGELOG.md` to see what you added
2. Run `git show --name-only HEAD` to see files changed in commit
3. Verify the CHANGELOG entry matches the actual changes
4. Self-assess accuracy: "Entry is accurate" or "Entry needs correction"

### Step 3: Confirm to User
**Display this verification report:**
```
✅ Post-Commit Verification:
✅ Commit: [hash]
✅ CHANGELOG entry: "[quote the entry you added]"
✅ Files changed: [list actual files from git show]
✅ Entry accuracy: [accurate/needs-correction]
✅ DEVLOG updated: [yes/no - reason]
✅ Validation: [passed/warnings/not-run]
```

**If entry is inaccurate, immediately:**
1. Amend the commit with corrected CHANGELOG
2. Re-run verification
3. Apologize to user and explain what was wrong

---

## 🔄 SESSION START - READ CONTEXT

**At start of EVERY session:**
1. Read `logs/DEVLOG.md` → "Current Context" section
2. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 📊 DAILY UPDATES

**Update DEVLOG Current Context when:** version/branch/phase/objectives change, or new risks identified
**Location:** `logs/DEVLOG.md` → "Current Context (Source of Truth)"

---

## 🗄️ ARCHIVAL

**Trigger:** Token count exceeds limits (run validation to check)
- CHANGELOG > 10,000 tokens
- DEVLOG > 15,000 tokens
- Combined > 25,000 tokens

**Action:** Archive OLDEST entries first (regardless of date) until under budget
1. Run validation to check current token counts
2. Note which file exceeds limit and by how much
3. Move oldest version section (CHANGELOG) or oldest entries (DEVLOG) to `logs/archive/[FILENAME]-YYYY-MM.md`
4. Re-run validation to confirm under budget

**Important:** Archive by TOKEN COUNT, not by date. A 2-week-old entry should stay if under budget. A 3-day-old entry may need archiving if over budget.

**Note:** If `.logfile-config.yml` exists, use profile-specific token targets instead of defaults above.

---

## 📋 PROFILE AWARENESS

**If `.logfile-config.yml` exists in project root:**
- Respect profile-specific token targets (may differ from defaults above)
- Respect profile-specific required files (DEVLOG/ADR may be optional in some profiles)
- Respect profile-specific update frequency (some profiles allow less frequent updates)
- Validation scripts automatically apply profile settings

**Profiles:**
- `solo-developer` (default) - Flexible, DEVLOG optional for milestones
- `team` - Stricter, DEVLOG required for significant changes
- `open-source` - Strict formatting, public-facing docs
- `startup` - Minimal overhead, DEVLOG optional

**See:** `.log-file-genius/docs/profile-selection-guide.md` for details

---

## 📝 TEMPLATES ARE READ-ONLY

**CRITICAL:** Templates in `.log-file-genius/templates/` are **REFERENCE ONLY**

**When creating initial log files:**
1. ✅ **READ** the template to understand structure
2. ✅ **CREATE** a new empty file in `logs/`
3. ✅ **WRITE** minimal structure (headers, sections) WITHOUT example content
4. ❌ **NEVER** copy example entries from templates
5. ❌ **NEVER** edit template files

**Example - Creating DEVLOG.md:**
```markdown
# Development Log

## Related Documents
📊 **[CHANGELOG](./CHANGELOG.md)** - Technical changes
📈 **[STATE](./STATE.md)** - Current project state

---

## Current Context (Source of Truth)

**Last Updated:** 2025-11-05

### Project State
- **Project:** My Project
- **Current Version:** v0.1.0-dev
- **Active Branch:** `main`
- **Phase:** Initial setup

### Current Objectives
- [ ] Set up project structure

---

## Daily Log - Newest First

(Entries will be added here as work progresses)
```

**Templates contain example entries to show format - DO NOT copy them to actual log files.**

---

## 🚫 KEY RULES

- ✅ All log files live in `logs/` folder (CHANGELOG, DEVLOG, STATE, adr/, incidents/)
- ✅ Templates are READ-ONLY reference - never edit them
- ✅ Create new empty files, mimic structure, skip example content
- ✅ Update CHANGELOG BEFORE every commit (not after)
- ✅ Include log files IN same commit as code
- ✅ Write specific entries (not "Updated files")
- ✅ Document WHY in DEVLOG for decisions
- ✅ Proactively update (don't wait for user to ask)

---

## 📚 Reference

Full docs: `.log-file-genius/docs/log_file_how_to.md` | Templates: `.log-file-genius/templates/` | Logs: `logs/` | Config: `.logfile-config.yml` | Validation: `.log-file-genius/docs/validation-guide.md`

---

## 🎯 Success = Every commit includes updated CHANGELOG + pre-commit checklist shown + post-commit confirmation
