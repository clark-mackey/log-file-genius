---
type: "manual"
---

# avoid-log-file-confusion (Manual)

**Trigger this rule when:**
- About to edit any .md file in the project
- User asks to "update logs" or "show examples"
- Starting work on documentation or templates
- First time in a new conversation thread

---

# Avoid Log File Confusion

## The Meta-Problem

This project teaches people how to use log files AND uses log files itself (dogfooding). This creates confusion risk between:
- **Template files** (clean examples for users)
- **Working logs** (this project's actual logs)
- **Documentation** (guides and how-tos)
- **Future examples** (demonstration files)

## Critical Rules

### 1. File Path Distinctions - MEMORIZE THESE

**WORKING LOGS (This Project's Real Logs):**
- `docs/planning/CHANGELOG.md` - This project's actual changelog
- `docs/planning/DEVLOG.md` - This project's actual development log
- `docs/adr/*.md` - This project's actual architectural decisions

**TEMPLATES (Clean Examples for Distribution):**
- `templates/CHANGELOG_template.md` - Template for users to copy
- `templates/DEVLOG_template.md` - Template for users to copy
- `templates/ADR_template.md` - Template for users to copy

**DOCUMENTATION (Guides):**
- `docs/log_file_how_to.md` - System documentation
- `docs/ADR_how_to.md` - ADR guide

**SOURCE MATERIAL (Read-Only):**
- `context/original-method-v3/*.md` - Original method files (DO NOT EDIT)

### 2. Update Rules - Which Files to Edit

**ALWAYS update these when working on this project:**
- ✅ `docs/planning/CHANGELOG.md` (working log)
- ✅ `docs/planning/DEVLOG.md` (working log)
- ✅ `docs/adr/*.md` (working ADRs)

**NEVER update these unless explicitly creating/improving templates:**
- ❌ `templates/*.md` (templates should stay clean and generic)
- ❌ `context/original-method-v3/*.md` (source material is read-only)

### 3. Example Rules - What to Show Users

**When user asks for "example log files" or "show me a sample":**
- ✅ Show: `templates/*.md` (clean, generic templates)
- ✅ Show: Future example files in `/examples` directory (when created)
- ❌ DO NOT show: `docs/planning/*.md` (contains real project details)

**Exception:** If user specifically asks "show me THIS project's logs" or "status update", then show working logs.

### 4. Privacy Protection

**Working logs may contain:**
- Real decisions and rationale
- Actual project timeline and progress
- Specific implementation details
- Future plans and risks

**These should NOT be shared as "examples" - use templates instead.**

### 5. Template Preservation

**Templates must remain:**
- Generic (no project-specific details)
- Clean (no real entries, just format examples)
- Instructional (include inline guidelines)

**If templates need improvement, that's a deliberate task, not routine maintenance.**

## Quick Decision Tree

```
User asks: "Show me an example CHANGELOG"
→ Show: templates/CHANGELOG_template.md

User asks: "What's our current status?"
→ Show: docs/planning/DEVLOG.md (Current Context section)

User asks: "Update the logs with this change"
→ Update: docs/planning/CHANGELOG.md and docs/planning/DEVLOG.md

User asks: "Improve the template"
→ Update: templates/*.md (deliberate template improvement)

User asks: "Create example log files"
→ Create: New files in /examples directory (future feature)
```

## Safety Checklist

Before editing ANY .md file, ask:
1. Is this a template or a working log?
2. Am I updating the right file for this task?
3. Should this information be in examples or working logs?
4. Am I preserving the distinction between templates and real logs?