# log-file-maintenance (Always Active - Non-Negotiable)

## ⚠️ CRITICAL: These Rules Are MANDATORY

This rule is ALWAYS active. You MUST follow these guidelines without exception.

---

## 🔴 BEFORE EVERY COMMIT - REQUIRED

**You MUST complete ALL steps before running `git commit`:**

**IMPORTANT:** Read `.logfile-config.yml` to determine log file locations. If config not found, use defaults below.

### Step 1: Update CHANGELOG.md (REQUIRED)
1. Read `.logfile-config.yml` → `paths.changelog` to find CHANGELOG location
   - Default: `docs/planning/CHANGELOG.md` or `project/planning/CHANGELOG.md`
2. Add entry under "Unreleased" in appropriate category (Added/Changed/Fixed/Deprecated/Removed/Security)
3. Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``
4. See `log-file-genius/templates/CHANGELOG_template.md` for examples

### Step 2: Update DEVLOG.md (If Milestone/Decision)
**Only if this commit is:** a completed epic, major milestone, architectural decision, or significant problem solved

1. Read `.logfile-config.yml` → `paths.devlog` to find DEVLOG location
   - Default: `docs/planning/DEVLOG.md` or `project/planning/DEVLOG.md`
2. Add entry to DEVLOG → "Daily Log" section (newest first)
3. Use Situation/Challenge/Decision/Why/Result/Files format (see `log-file-genius/templates/DEVLOG_template.md`)
4. Keep entries 150-250 words

### Step 3: Run Validation (OPTIONAL but Recommended)
**If validation script is available:**
```bash
.\log-file-genius\scripts\validate-log-files.ps1  # Windows
./log-file-genius/scripts/validate-log-files.sh   # Mac/Linux
```
- Validates CHANGELOG/DEVLOG format
- Checks token counts against profile limits (reads `.logfile-config.yml`)
- Applies profile-specific strictness settings
- Catches common errors before commit
- Can be skipped if not installed

**Note:** Validation scripts are profile-aware. If `.logfile-config.yml` exists, they will use profile-specific token targets and validation strictness.

### Step 4: Include Planning Files in Commit
- `git add [path from .logfile-config.yml]` (e.g., `git add docs/planning/CHANGELOG.md`)
- `git add [DEVLOG path]` (if updated)
- Planning files MUST be in the SAME commit as code changes

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

## 📋 AFTER EVERY COMMIT - VERIFICATION

**Confirm to user:**
```
✅ Commit: [hash]
✅ CHANGELOG: [entry added]
✅ DEVLOG: [yes/no - reason]
```

---

## 🔄 SESSION START - READ CONTEXT

**At start of EVERY session:**
1. Read `.logfile-config.yml` → `paths.devlog` to find DEVLOG location
2. Read DEVLOG → "Current Context" section
3. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 📊 DAILY UPDATES

**Update DEVLOG Current Context when:** version/branch/phase/objectives change, or new risks identified
**Location:** Read from `.logfile-config.yml` → `paths.devlog` → "Current Context (Source of Truth)"

---

## 🗄️ ARCHIVAL

**Trigger:** Token count exceeds limits (run validation to check)
- CHANGELOG > 10,000 tokens
- DEVLOG > 15,000 tokens
- Combined > 25,000 tokens

**Action:** Archive OLDEST entries first (regardless of date) until under budget
1. Run validation to check current token counts
2. Note which file exceeds limit and by how much
3. Move oldest version section (CHANGELOG) or oldest entries (DEVLOG) to archive folder
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

**See:** `product/docs/profile-selection-guide.md` for details

---

## 🚫 KEY RULES

- ✅ Read `.logfile-config.yml` to find log file locations
- ✅ Update CHANGELOG BEFORE every commit (not after)
- ✅ Include planning files IN same commit as code
- ✅ Write specific entries (not "Updated files")
- ✅ Document WHY in DEVLOG for decisions
- ✅ Proactively update (don't wait for user to ask)

---

## 📚 Reference

Full docs: `.log-file-genius/product/docs/log_file_how_to.md` | Templates: `log-file-genius/templates/` | Config: `.logfile-config.yml` | Validation: `.log-file-genius/product/docs/validation-guide.md`

---

## 🎯 Success = Every commit includes updated CHANGELOG + pre-commit checklist shown + post-commit confirmation
