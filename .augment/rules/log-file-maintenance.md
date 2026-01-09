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
4. See `product/templates/CHANGELOG_template.md` for examples

### Step 2: Update DEVLOG.md (If Milestone/Decision)
**Only if this commit is:** a completed epic, major milestone, architectural decision, or significant problem solved

1. Add entry to `logs/DEVLOG.md` → "Daily Log" section (newest first)
2. Use Situation/Challenge/Decision/Why/Result/Files format (see `product/templates/DEVLOG_template.md`)
3. Keep entries 150-250 words

### Step 3: Run Validation (OPTIONAL but Recommended)
**If validation script is available:**
```bash
.\product\scripts\validate-log-files.ps1  # Windows
./product/scripts/validate-log-files.sh   # Mac/Linux
```
- Validates CHANGELOG/DEVLOG format
- Checks token counts against profile limits (reads `.logfile-config.yml`)
- Applies profile-specific strictness settings
- Catches common errors before commit
- Can be skipped if not installed

**Note:** Validation scripts are profile-aware. If `.logfile-config.yml` exists, they will use profile-specific token targets and validation strictness.

### Step 4: Include Planning Files in Commit
- `git add logs/CHANGELOG.md`
- `git add logs/DEVLOG.md` (if updated)
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
1. Run validation: `.\product\scripts\validate-log-files.ps1 -Verbose`
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

**See:** `product/docs/profile-selection-guide.md` for details

---

## 🚫 KEY RULES

- ✅ Update CHANGELOG BEFORE every commit (not after)
- ✅ Include planning files IN same commit as code
- ✅ Write specific entries (not "Updated files")
- ✅ Document WHY in DEVLOG for decisions
- ✅ Proactively update (don't wait for user to ask)

---

## 📚 Reference

Full docs: `product/docs/log_file_how_to.md` | Templates: `product/templates/` | Logs: `logs/` | ADRs: `logs/adr/` | Validation: `product/docs/validation-guide.md`

---

## 🎯 Success = Every commit includes updated CHANGELOG + pre-commit checklist shown + post-commit confirmation

