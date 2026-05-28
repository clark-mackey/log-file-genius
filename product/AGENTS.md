---
doc: AGENTS
related:
  state: ./logs/STATE.md
  changelog: ./logs/CHANGELOG.md
  devlog: ./logs/DEVLOG.md
---

# Log File Genius — AGENTS guidance

**Read this first.** This project uses Log File Genius. To orient cold:

- `logs/STATE.md` — the now (current context + last session)
- `logs/CHANGELOG.md` Unreleased — recent changes
- `logs/DEVLOG.md` Daily Log — why decisions were made

## Available commands

- `lfg validate` — validate log files (format + token budget)
- `lfg prime [--n N]` — emit a subagent context digest (the lead pastes this into a subagent prompt to establish role + give context)
- `lfg promote <id>` — lead-only; promote a subagent's staged entries to canonical CHANGELOG/DEVLOG
- `lfg status` — quick project status
- `lfg generate` — regenerate AGENTS.md from product/rules/ fragments (LFG contributors)

## Sections

- **log-file-maintenance** — Always-active rules for log maintenance (commits, sessions, archival, formats).
- **status-update** — "@status update" command — concise project state summary.
- **update-planning-docs** — "@update planning docs" command — guided CHANGELOG/DEVLOG/ADR/STATE updates.
- **token-usage** — "@token usage" command — report context-window usage and component token costs.

## log-file-maintenance

# log-file-maintenance (Always Active - Non-Negotiable)

## ⛔ MANDATORY RULE - NO EXCEPTIONS

This rule is ALWAYS active. Violations require immediate self-correction.

---

## 🔴 BEFORE EVERY COMMIT

**⛔ STOP - DO NOT run `git commit` until ALL steps complete:**

1. **Update CHANGELOG.md** — read `.logfile-config.yml` → `paths.changelog` (fallback `logs/CHANGELOG.md`)
   - Add entry under "Unreleased" → category (Added/Changed/Fixed/Deprecated/Removed/Security)
   - Format: `- Description. Files: \`path/to/file\`. Commit: \`hash\``
   - **Fragment edits:** when changing files under `product/rules/`, the CHANGELOG entry references only the fragment path. The regenerated `product/AGENTS.md` and the per-tool rule files at install-time are implicit and need not be listed.

2. **Update DEVLOG.md** (if milestone/decision) — read `.logfile-config.yml` → `paths.devlog` (fallback `logs/DEVLOG.md`)
   - Only for: completed epics, major milestones, architectural decisions
   - Add to "Daily Log" section (newest first)

3. **Stage log files**
   - `git add <changelog-path>`
   - `git add <devlog-path>` (if updated)

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
- Correct the entry; explain to user what was wrong

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
1. Read `.logfile-config.yml` → `paths.state` (fallback `logs/STATE.md`)
2. Read STATE → "Current Context" + "Last Session" sections
3. **Staleness check:** If STATE's `Last Updated` is >7 days old, update STATE BEFORE other work
   - Tell user: "STATE is X days old. Updating before proceeding."
   - Update: version, phase, objectives, recent changes; set new `Last Updated` date
4. Acknowledge: "Context read. Version [x], Phase [y], Objectives: [z]"

---

## 🔚 SESSION END

**⚠️ Multi-agent:** If you are a subagent or teammate (not the lead/primary agent), skip this section. Only the primary agent writes session handoffs.

**Before ending a session, write a handoff note:**

1. Update STATE → "Last Session" section (overwrite previous) — path from `.logfile-config.yml` → `paths.state` (fallback `logs/STATE.md`)
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
- 1 DEVLOG incident entry ≈ 80-120 tokens
- 1 DEVLOG standard entry ≈ 150-250 tokens

**Budgets:**
- CHANGELOG: <10,000 tokens
- DEVLOG: <15,000 tokens
- Combined: <25,000 tokens

**Before writing:** Estimate entry size. If file is near budget, archive oldest entries first.

---

## ✏️ ENTRY VERBOSITY

**Three DEVLOG entry formats:**

**Compact format** (default for routine work, ~50-80 tokens):
```
### YYYY-MM-DD: Title
Why/what in 1-2 sentences. Context or rationale.
Files: `file1.py`, `file2.py`
```

**Incident format** (for failures worth learning from, ~80-120 tokens):
```
### YYYY-MM-DD: 🚨 INCIDENT - What failed
**Root Cause:** Why it happened (1-2 sentences)
**Prevention:** How to stop it recurring (1-2 actions)
**Detection:** How to catch it earlier next time (1 action)
Files: `file1.py`, `file2.py` → CHANGELOG: `v1.2.1`
```

**Incident rubric — always qualifies:** security exposure, data loss/corruption, repeated failure (3+), silent failure, rule violation with impact, regression.

**Standard format** (for major decisions, milestones, ~150-250 tokens):
```
### YYYY-MM-DD: Title
**The Situation:** ...
**The Decision:** ...
**Why This Matters:** ...
**Files Changed:** ...
```

**Decision guide:** Security/data/regression → incident. Needs an ADR → standard. Everything else → compact.

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
1. Move oldest entries to `logs/archive/[FILENAME]-YYYY-MM.md`
2. Add summary line to the Archive section of the source file:
   `- [FILENAME-YYYY-MM.md](archive/FILENAME-YYYY-MM.md) - Brief description of contents`
3. Re-run validation to confirm

**Key:** Archive by TOKEN COUNT, not date. Recent entries may need archiving if over budget.

---

## 📝 TEMPLATES

Templates in `.log-file-genius/product/templates/` are **READ-ONLY REFERENCE**.
- ✅ Read to understand structure
- ✅ Create new files in `logs/`
- ❌ Never copy example entries
- ❌ Never edit template files

---

## 🤖 SUBAGENT CONTRACT

**Identity:** Context contains `LFG_SUBAGENT_PRIME` → you are a **subagent**.

**Reading:** Use the primed digest in context. Do NOT load STATE.md / CHANGELOG.md / DEVLOG.md unless the lead says to.

**Writing — staged, never direct:**
- Never write to `STATE.md` (SESSION END is lead-only), `CHANGELOG.md`, or `DEVLOG.md`.
- Stage entries under `.lfg/staged/<your-id>/`:
  - `changelog.md` — `- Description. Files: \`x\`. Commit: \`pending\``
  - `devlog.md` — fully formatted DEVLOG entry
- Report: "Staged at `.lfg/staged/<your-id>/`." Lead runs `lfg promote <your-id>`.

**Context:** Do NOT call `lfg prime`. Ask the lead for more.

---

## 🎯 SUCCESS CRITERIA

Every commit MUST include:
1. ✅ Updated CHANGELOG.md
2. ✅ Pre-commit checklist shown to user
3. ✅ Post-commit verification shown to user
4. ✅ Self-correction if any violation detected

## status-update

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

## update-planning-docs

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

## token-usage

# token-usage

## Trigger
When user says **"@token-usage"**, **"token usage"**, **"context window"**, or **"token cost"**.

---

## Actions

1. When user asks about current AI token/context usage (e.g., "token usage", "context window", "how many tokens"), respond with ONLY this format:

**Tokens: [used]/[total] ([remaining] remaining, [percentage]% used)**

No explanations. No additional text. Just the numbers.

2. When asked about token cost of specific files/code/systems (e.g., "How expensive is CHANGELOG?", "Token cost of Log File Genius?"), analyze the component(s) and runtime dependencies. For each component, report in two paragraphs: (1) token breakdown, (2) dependencies that load when used.

**Note:**
- For systems (e.g., "Log File Genius"), analyze all related files and rules
- For multiple targets, analyze each separately
- Ignore non-AI token references (OAuth, JWT, API tokens)
