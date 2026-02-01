# Project Directory - AI Agent Navigation Guide

> **For Autonomous Agents:** This guide helps you understand the project structure and find what you need quickly.

## 🎯 Mission Statement

**"Help AI agents not get lost, not waste tokens"** - Measure every feature against this standard.

## 📁 Directory Structure

```
log-file-genius/
├── product/          # DISTRIBUTION - What users install
│   ├── scripts/      # Installation and utility scripts
│   ├── templates/    # Log file templates (CHANGELOG, DEVLOG, etc.)
│   ├── rules/        # AI assistant rules (.augment-rules, .cursorrules, etc.)
│   └── examples/     # Example implementations
│
├── project/          # DEVELOPMENT - Planning and specs (this directory)
│   ├── specs/        # Requirements and epic specifications
│   ├── adr/          # Architecture Decision Records
│   ├── docs/         # How-to guides and troubleshooting
│   ├── templates/    # WIP templates (move to product/ when complete)
│   ├── qa/           # Bug reports and testing
│   └── archive/      # Historical research and analysis (reference only)
│
└── logs/             # ACTIVE LOGS - Project's own documentation
    ├── CHANGELOG.md  # What changed and when
    ├── DEVLOG.md     # Why decisions were made
    └── archive/      # Archived log entries
```

## 📚 Source of Truth

| Need | File |
|------|------|
| **All requirements, epics, stories** | `project/specs/prd.md` |
| **What changed recently** | `logs/CHANGELOG.md` |
| **Current objectives & context** | `logs/DEVLOG.md` → "Current Context" section |
| **Architecture decisions** | `project/adr/*.md` |
| **Git workflow** | `project/WORKFLOW.md` |

## ⚠️ Important Notes

1. **prd.md is the source of truth** - All epic details are there. Individual EPIC-*.md files are detailed specs for specific epics.

2. **Archived files are READ-ONLY reference** - Files in `project/archive/` are historical. Don't treat them as current requirements.

3. **Two-branch strategy:**
   - `main` branch: Only `product/` directory (for distribution)
   - `development` branch: Both `product/` and `project/` (for work)

4. **Log file maintenance rule:** Before every commit, update `logs/CHANGELOG.md`. See `.augment/rules/log-file-maintenance.md`.

5. **Mission alignment:** Features must either (a) reduce tokens or (b) help AI agents navigate. Reject features that only serve human developers.

## 🚫 Rejected Ideas (Do Not Implement)

The following were rejected for mission drift (serving developers, not AI agents):
- Epic 9: CLI Tooling
- Epic 10: Claude Code Subagent Integration  
- Epic 11: Advanced Automation (git hooks, CI templates)

See `project/specs/prd.md` → "Rejected Ideas" section for details.

## 🔄 Active Epics (February 2026)

- **Epic 7:** Core Reliability & Bug Fixes (Stories 7.1-7.5)
- **Epic 8:** AI Context Optimization (5 stories focused on AI agent benefits)

## 📋 File Quick Reference

### Active Specs
- `project/specs/prd.md` - **START HERE** - All requirements
- `project/specs/DEFINITION-OF-DONE.md` - Completion checklists
- `project/specs/EPIC-12-*.md` through `EPIC-19-*.md` - Detailed epic specs

### Decision Records
- `project/adr/` - Architecture Decision Records (ADR-001 through ADR-011)

### Workflow
- `project/WORKFLOW.md` - Git workflow and branch strategy

