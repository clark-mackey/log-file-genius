# log-file-maintenance (Always Active - Non-Negotiable)

## ⛔ MANDATORY RULE - NO EXCEPTIONS

This rule is ALWAYS active. Violations require immediate self-correction.

---

## 🔴 BEFORE EVERY COMMIT

**⛔ STOP - DO NOT run `git commit` until ALL steps complete:**

1. **Update CHANGELOG.md** → `logs/CHANGELOG.md`
   - Add entry under "Unreleased" → category (Added/Changed/Fixed/Deprecated/Removed/Security)
   - Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``

2. **Update DEVLOG.md** (if milestone/decision)
   - Only for: completed epics, major milestones, architectural decisions
   - Add to `logs/DEVLOG.md` → "Daily Log" section (newest first)

3. **Stage log files**
   - `git add logs/CHANGELOG.md`
   - `git add logs/DEVLOG.md` (if updated)

4. **Show checklist to user:**
   ```
   ✅ Pre-Commit Checklist:
   - [ ] CHANGELOG.md updated
   - [ ] DEVLOG.md updated (if milestone)
   - [ ] Log files staged
   - [ ] Ready to commit
   ```

**⛔ If ANY box unchecked → FIX BEFORE PROCEEDING**

---

## 📋 AFTER EVERY COMMIT

**⛔ STOP - DO NOT proceed to next task until verification complete:**

1. **Self-check:** Did I update CHANGELOG? (yes/no)
2. **Self-check:** Does entry match actual changes? (yes/no/unsure)
3. **Self-check:** Did I include log files in commit? (yes/no)

**If ANY answer is "no" or "unsure" → IMMEDIATELY FIX:**
- Amend commit: `git commit --amend`
- Correct the entry
- Explain to user what was wrong

4. **Show verification to user:**
   ```
   ✅ Commit: [hash]
   ✅ CHANGELOG: [entry added]
   ✅ DEVLOG: [yes/no - reason]
   ```

---

## 🚨 FAILURE DETECTION & SELF-CORRECTION

**If you detect you violated this rule (at any point):**

1. ⛔ **STOP** current task immediately
2. 📢 **TELL** user: "I detected I missed updating [CHANGELOG/DEVLOG]. Fixing now."
3. 🔧 **FIX** the violation (amend commit or add new commit)
4. ✅ **VERIFY** the fix is correct
5. 📋 **RESUME** original task

**Common violations to self-detect:**
- Committed without updating CHANGELOG
- CHANGELOG entry doesn't match actual files changed
- Forgot to stage log files
- Made multiple commits without CHANGELOG entries

---

## 🔄 SESSION START

**At start of EVERY session:**
1. Read `logs/DEVLOG.md` → "Current Context" section
2. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 🗄️ ARCHIVAL (When Token Limits Exceeded)

**Triggers:** CHANGELOG >10k tokens | DEVLOG >15k tokens | Combined >25k tokens

**Action:** Archive OLDEST entries first until under budget
1. Move oldest entries to `logs/archive/[FILENAME]-YYYY-MM.md`
2. Re-run validation to confirm

**Key:** Archive by TOKEN COUNT, not date. Recent entries may need archiving if over budget.

---

## 📝 TEMPLATES

Templates in `product/templates/` are **READ-ONLY REFERENCE**.
- ✅ Read to understand structure
- ✅ Create new files in `logs/`
- ❌ Never copy example entries
- ❌ Never edit template files

---

## 🎯 SUCCESS CRITERIA

Every commit MUST include:
1. ✅ Updated CHANGELOG.md
2. ✅ Pre-commit checklist shown to user
3. ✅ Post-commit verification shown to user
4. ✅ Self-correction if any violation detected
