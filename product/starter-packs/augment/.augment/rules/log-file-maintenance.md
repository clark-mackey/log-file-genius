# log-file-maintenance (Always Active - Non-Negotiable)

## ⚠️ CRITICAL: These Rules Are MANDATORY

This rule is ALWAYS active. You MUST follow these guidelines without exception.

---

## 🔴 BEFORE EVERY COMMIT - REQUIRED

**You MUST complete ALL steps before running `git commit`:**

### Step 1: Update CHANGELOG.md (REQUIRED)
1. Open `docs/planning/CHANGELOG.md`
2. Add entry under "Unreleased" in appropriate category (Added/Changed/Fixed/Deprecated/Removed/Security)
3. Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``
4. See `templates/CHANGELOG_template.md` for examples

### Step 2: Update DEVLOG.md (If Milestone/Decision)
**Only if this commit is:** a completed epic, major milestone, architectural decision, or significant problem solved

1. Add entry to `docs/planning/DEVLOG.md` → "Daily Log" section (newest first)
2. Use Situation/Challenge/Decision/Why/Result/Files format (see `templates/DEVLOG_template.md`)
3. Keep entries 150-250 words

### Step 3: Run Validation (OPTIONAL but Recommended)
**If validation script is available:**
```bash
.\scripts\validate-log-files.ps1  # Windows
./scripts/validate-log-files.sh   # Mac/Linux
```
- Validates CHANGELOG/DEVLOG format
- Checks token counts
- Catches common errors before commit
- Can be skipped if not installed

### Step 4: Include Planning Files in Commit
- `git add docs/planning/CHANGELOG.md`
- `git add docs/planning/DEVLOG.md` (if updated)
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
1. Read `docs/planning/DEVLOG.md` → "Current Context" section
2. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 📊 DAILY UPDATES

**Update DEVLOG Current Context when:** version/branch/phase/objectives change, or new risks identified
**Location:** `docs/planning/DEVLOG.md` → "Current Context (Source of Truth)"

---

## 🗄️ ARCHIVAL

**Trigger:** CHANGELOG or DEVLOG >10,000 tokens
**Action:** Archive entries >2 weeks old to `docs/planning/archive/[FILENAME]-YYYY-MM.md`
**Targets:** CHANGELOG <10k, DEVLOG <15k, Combined <25k tokens

---

## 🚫 KEY RULES

- ✅ Update CHANGELOG BEFORE every commit (not after)
- ✅ Include planning files IN same commit as code
- ✅ Write specific entries (not "Updated files")
- ✅ Document WHY in DEVLOG for decisions
- ✅ Proactively update (don't wait for user to ask)

---

## 📚 Reference

Full docs: `docs/log_file_how_to.md` | Templates: `templates/` | Logs: `docs/planning/` | ADRs: `docs/adr/` | Validation: `docs/validation-guide.md`

---

## 🎯 Success = Every commit includes updated CHANGELOG + pre-commit checklist shown + post-commit confirmation

