# Status Update Command

When the user says "status update", analyze these files and provide a brief summary (3-5 bullet points) of where we are and what's next.

## Files to Analyze

- **PRD:** `docs/prd.md` (comprehensive product requirements)
- **CHANGELOG:** `docs/planning/CHANGELOG.md` (technical changes and version history)
- **DEVLOG:** `docs/planning/DEVLOG.md` (development narrative and current context)
- **ADRs:** `docs/adr/README.md` (architectural decisions index)

## Focus Areas

- **Current version** (from DEVLOG Current Context)
- **Active phase** (from DEVLOG Current Context)
- **Recent changes** (from CHANGELOG Unreleased section)
- **Next priorities** (from DEVLOG Current Objectives)
- **Known risks/blockers** (from DEVLOG Current Context)

## Output Format

Provide a concise summary like:

```
📍 **Status Update - [Project Name]**

**Current State:**
- Version: v0.1.0-dev
- Phase: Foundation - [Brief description]

**Recent Progress:**
- ✅ [Completed item 1]
- ✅ [Completed item 2]
- ✅ [Completed item 3]

**Next Up:**
- [Next priority 1]
- [Next priority 2]
- [Next priority 3]

**Risks/Blockers:**
- [Blocker or "None currently"]
```

