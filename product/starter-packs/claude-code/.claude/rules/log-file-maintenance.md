# log-file-maintenance (Always Active - Non-Negotiable)

## ⛔ MANDATORY RULE - NO EXCEPTIONS

This rule is ALWAYS active. Violations require immediate self-correction.

**Path Config:** Read `.logfile-config.yml` → `paths` section for log file locations.

---

## 🔴 BEFORE EVERY COMMIT

**⛔ STOP - DO NOT run `git commit` until ALL steps complete:**

1. **Update CHANGELOG.md** (path from `.logfile-config.yml` → `paths.changelog`)
   - Add entry under "Unreleased" → category (Added/Changed/Fixed/Deprecated/Removed/Security)
   - Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``

2. **Update DEVLOG.md** (if milestone/decision)
   - Only for: completed epics, major milestones, architectural decisions
   - Path from `.logfile-config.yml` → `paths.devlog`

3. **Stage log files**
   - `git add [CHANGELOG path from config]`
   - `git add [DEVLOG path]` (if updated)

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
1. Read `.logfile-config.yml` → `paths.devlog` to find DEVLOG
2. Read DEVLOG → "Last Session" section (if exists) for handoff context
3. Read DEVLOG → "Current Context" section
4. **Staleness check:** If `Last Updated` date is >7 days old, update Current Context BEFORE other work
   - Tell user: "Current Context is X days old. Updating before proceeding."
   - Update: version, phase, objectives, recent changes
   - Set new `Last Updated` date
5. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 🔚 SESSION END

**⚠️ Multi-agent:** If you are a subagent or teammate (not the lead/primary agent), skip this section. Only the primary agent writes session handoffs.

**Before ending a session, write a handoff note:**

1. Update DEVLOG → "Last Session" section (overwrite previous)
2. Format (3 bullets max, <150 tokens):
   ```
   ## Last Session
   - **Done:** [What was completed this session]
   - **In Progress:** [What's partially done, current state]
   - **Next:** [What the next session should start with]
   - **Branch:** `branch-name` | **Last Commit:** `hash`
   ```
3. Stage and commit with other changes (or amend last commit)

---

## 📊 TOKEN SELF-ASSESSMENT

**Heuristic:** ~4 characters = 1 token. Use this to self-regulate without running scripts.

**Quick reference:**
- 1 line (~80 chars) ≈ 20 tokens
- 1 paragraph (~320 chars) ≈ 80 tokens
- 1 CHANGELOG entry ≈ 60-80 tokens
- 1 DEVLOG compact entry ≈ 50-80 tokens
- 1 DEVLOG standard entry ≈ 150-250 tokens

**Budgets:**
- CHANGELOG: <10,000 tokens
- DEVLOG: <15,000 tokens
- Combined: <25,000 tokens

**Before writing:** Estimate entry size. If file is near budget, archive oldest entries first.

---

## ✏️ ENTRY VERBOSITY

**Two DEVLOG entry formats:**

**Compact format** (default for routine work, ~50-80 tokens):
```
### YYYY-MM-DD: Title
Why/what in 1-2 sentences. Context or rationale.
Files: `file1.py`, `file2.py`
```

**Standard format** (for major decisions, incidents, milestones, ~150-250 tokens):
```
### YYYY-MM-DD: Title
**The Situation:** ...
**The Decision:** ...
**Why This Matters:** ...
**Files Changed:** ...
```

**Decision guide:** If it needs an ADR → use standard. Otherwise → compact.

---

## 🔗 CROSS-REFERENCES

**When writing entries that relate across files, add navigation hints:**

- CHANGELOG entry with a DEVLOG decision: append `→ DEVLOG YYYY-MM-DD`
- DEVLOG entry referencing a specific version: append `→ CHANGELOG vX.Y.Z`

**Example:**
```
- Fixed token refresh bug. Files: `src/auth.js`. Commit: `abc123` → DEVLOG 2026-02-06
```

Hints are optional - only add when a cross-reference exists.

---

## 🗄️ ARCHIVAL (When Token Limits Exceeded)

**Triggers:** CHANGELOG >10k tokens | DEVLOG >15k tokens | Combined >25k tokens

**Action:** Archive OLDEST entries first until under budget
1. Move oldest entries to archive folder (see `.logfile-config.yml`)
2. Add summary line to the Archive section of the source file:
   `- [FILENAME-YYYY-MM.md](archive/FILENAME-YYYY-MM.md) - Brief description of contents`
3. Re-run validation to confirm

**Key:** Archive by TOKEN COUNT, not date. Recent entries may need archiving if over budget.

---

## 🎯 SUCCESS CRITERIA

Every commit MUST include:
1. ✅ Updated CHANGELOG.md
2. ✅ Pre-commit checklist shown to user
3. ✅ Post-commit verification shown to user
4. ✅ Self-correction if any violation detected
