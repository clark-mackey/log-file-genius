---
type: "always_apply"
---

# Log File Confusion Guard (Always On)

**⚠️ META-PROBLEM ALERT:** Log File Genius dogfoods its own log file system. There are multiple layers of log files that serve different purposes.

## Critical File Distinctions

**WORKING LOGS (This Project's Real Logs):**
- `docs/planning/CHANGELOG.md` - THIS project's actual changelog
- `docs/planning/DEVLOG.md` - THIS project's actual development log
- `docs/adr/*.md` - THIS project's actual architectural decisions

**TEMPLATES (Clean Examples for Distribution):**
- `templates/CHANGELOG_template.md` - Template for users to copy
- `templates/DEVLOG_template.md` - Template for users to copy
- `templates/ADR_template.md` - Template for users to copy

**DOCUMENTATION (Guides):**
- `docs/log_file_how_to.md` - System documentation
- `docs/ADR_how_to.md` - ADR guide

**SOURCE MATERIAL (Read-Only):**
- `context/original-method-v3/*.md` - Original method files (DO NOT EDIT)

## Quick Rules

**When updating logs during project work:**
- ✅ Edit: `docs/planning/CHANGELOG.md` and `docs/planning/DEVLOG.md`
- ❌ Don't edit: `templates/*.md` (those are for distribution)

**When user asks for "example log files":**
- ✅ Show: `templates/*.md` (clean, generic templates)
- ❌ Don't show: `docs/planning/*.md` (contains real project details)

**Exception:** If user specifically asks "show me THIS project's logs" or "status update", then show working logs.

## Before Editing ANY .md File

Ask yourself: **Is this a template or a working log?**
- If unsure, invoke `@avoid-log-file-confusion` for full details

---

**See:** `@avoid-log-file-confusion` for comprehensive guidance, decision tree, and safety checklist.

