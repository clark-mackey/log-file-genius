# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../prd.md)** - Product requirements and specifications
📖 **[DEVLOG](DEVLOG.md)** - Development narrative and decision rationale
📐 **[Architecture](../architecture.md)** - System architecture and design (TBD)

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see DEVLOG.md → Current Context section.

---

## [Unreleased] - v0.1.0-dev

### Changed
- Augment rules location - Moved from `.augment/rules/` to `starter-packs/augment/.augment/rules/` for better distribution. Files: `starter-packs/augment/.augment/rules/log-file-maintenance.md`, `starter-packs/augment/.augment/rules/status-update.md`, `starter-packs/augment/.augment/rules/update-planning-docs.md`. Commit: `a93e543`
- .gitignore - Simplified to exclude entire `.augment/` and `.claude/` directories instead of individual files. Files: `.gitignore`. Commit: `a93e543`
- Augment starter pack README - Updated setup instructions to reflect new `.augment/` directory location. Files: `starter-packs/augment/README.md`. Commit: `a93e543`

### Added
- Validation in starter packs (Epic 7) - Added validation scripts and git hooks to both starter packs, updated READMEs with installation instructions, updated log-file-maintenance rule to reference validation. Epic 7 complete! Files: `starter-packs/*/scripts/`, `starter-packs/*/.git-hooks/`, `starter-packs/*/README.md`, `.augment/rules/log-file-maintenance.md`. Commit: `pending`
- Validation examples and documentation (Epic 7) - Created git pre-commit hook, validation guide, and test examples for validation system. Files: `.git-hooks/pre-commit`, `docs/validation-guide.md`, `examples/validation/*.md`. Commit: `9b90dcc`
- Validation system (Epic 7) - Created validation architecture design and PowerShell validation script that checks CHANGELOG/DEVLOG format and token counts. Files: `docs/validation-architecture.md`, `scripts/validate-log-files.ps1`. Commit: `854fa45`
- Agent OS-inspired enhancements - Added 5 new epics (Verification, Profiles, Skills, Workflows, Layered Context) with ADR and task lists. Files: `docs/adr/007-agent-os-inspired-enhancements.md`, `docs/planning/EPIC-07-verification-system.md`, `docs/planning/EPIC-08-11-other-enhancements.md`. Commit: `49e106a`
- README.md - Main repository landing page with quick start, migration guide links, badges, and community section. Files: `README.md`. Commits: `461652a`, `34d6ac8`
- PRD document - Complete product requirements with 6 epics, 30 stories, success metrics (copied from BMAD context, later removed from repo). Files: `docs/prd.md` (local only)
- Template files - CHANGELOG, DEVLOG, ADR templates for distribution. Files: `templates/CHANGELOG_template.md`, `templates/DEVLOG_template.md`, `templates/ADR_template.md`
- STATE.md template - Fifth document for multi-agent coordination with active work, blockers, priorities. Files: `templates/STATE_template.md`
- Templates README - Guide explaining all templates with usage instructions and customization tips. Files: `templates/README.md`
- Working log files - Initialized CHANGELOG and DEVLOG for this project. Files: `docs/planning/CHANGELOG.md`, `docs/planning/DEVLOG.md`
- Documentation files - Comprehensive guides for log file system and ADRs. Files: `docs/log_file_how_to.md`, `docs/ADR_how_to.md`
- Examples directory - Realistic sample project showing 3 weeks of development on Task Management API. Files: `examples/README.md`, `examples/sample-project/CHANGELOG.md`, `examples/sample-project/DEVLOG.md`, `examples/sample-project/STATE.md`, `examples/sample-project/adr/README.md`, `examples/sample-project/adr/001-postgresql-choice.md`
- ADR directory structure - Created ADR index and directory. Files: `docs/adr/README.md`
- Augment rules - Installed 3 rules for log file maintenance. Files: `.augment/rules/update-planning-docs.md`, `.augment/rules/status-update.md`, `.augment/rules/log-file-maintenance.md`
- GitHub repository - Initial commit pushed to clark-mackey/log-file-genius. Commit: `663ab19`
- MIT License - Added permissive open-source license. Files: `LICENSE`
- .gitignore - Excluded internal Augment/Claude rules and context directory. Files: `.gitignore`
- Claude Code integration - Created complete Claude Code setup with project instructions and rules. Files: `.claude/project_instructions.md`, `.claude/README.md`, `.claude/SETUP_SUMMARY.md`, `.claude/rules/log-file-maintenance.md`, `.claude/rules/status-update.md`, `.claude/rules/update-planning-docs.md`
- Claude Code starter pack - Quick setup guide for Claude Code users. Files: `starter-packs/claude-code/README.md`
- Migration Guide - Comprehensive brownfield integration guide with 4 scenarios (fresh start, expand from CHANGELOG, condense verbose docs, complete partial implementation). Files: `docs/MIGRATION_GUIDE.md`. See: PRD Epic 2. Commit: `50cc72b`
- Migration Checklist - Progress tracking checklist for migration with safety reminders and validation criteria. Files: `docs/MIGRATION_CHECKLIST.md`. Commit: `50cc72b`
- CONTRIBUTING.md - Community contribution guidelines with platform support checklist, commit standards, and review process. Files: `CONTRIBUTING.md`. Commit: `39b7194`
- Augment starter pack - Quick setup guide for Augment users with rules, customization tips, and troubleshooting. Files: `starter-packs/augment/README.md`. Commit: `39b7194`

### Modified
- PRD - Updated to reflect 5-document system (added STATE.md), updated token metrics (93% reduction from ~90-110k to ~7-10k tokens), added FR11 for migration guide. Files: `docs/prd.md`
- Documentation - Updated log_file_how_to.md to document five-document system (added STATE.md). Files: `docs/log_file_how_to.md`
- Documentation - Added Context Layers section with 4-layer progressive disclosure strategy (Layer 1: <500 tokens, Layer 2: <2k, Layer 3: <10k, Layer 4: on-demand). Files: `docs/log_file_how_to.md`
- Documentation - Added Examples Directory section explaining how to use examples for learning and reference. Files: `docs/log_file_how_to.md`
- Augment rule - Expanded avoid-log-file-confusion rule with file path distinctions, update rules, example rules, privacy protection, and decision tree. Files: `.augment/rules/avoid-log-file-confusion.md`
- Augment rule - Changed avoid-log-file-confusion from always-on to manual trigger to save tokens. Files: `.augment/rules/avoid-log-file-confusion.md`
- Augment rule - Created condensed always-on guard rule (425 tokens) that references detailed manual rule. Files: `.augment/rules/log-file-confusion-guard.md`
- Project rebrand - Renamed from "log-file-setup" to "log-file-genius" for better branding, memorability, and growth potential. Files: `.augment/rules/correct-project-identity.md`, `.augment/rules/log-file-confusion-guard.md`, `.augment/rules/status-update.md`, `docs/planning/DEVLOG.md`, `docs/adr/README.md`
- README - Added "For Existing Projects" section with migration guide link and scenario overview. Files: `README.md`
- README - Added migration guide to main navigation. Files: `README.md`
- README - Updated Claude Code status from "Coming Soon" to "Available". Files: `README.md`

---

## Archive

**Versions older than 30 days** are archived for token efficiency:
- (No archived versions yet)

---

## Template Guidelines (Remove this section after initial setup)

### Entry Format
```markdown
- **Feature/Change Name** - One-line description. Files: `path/to/file.py`. PR: [#1234](link)
```

### Best Practices for AI Efficiency

1. **One line per change** - Keep it scannable
2. **Always include file paths** - Helps AI locate relevant code
3. **Link to PRs/issues** - Deep context available on demand, not loaded upfront
4. **No code examples** - Link to files instead
5. **No "Why This Matters"** - That belongs in DEVLOG
6. **Archive monthly** - Move versions >30 days old to `/archive/CHANGELOG-YYYY-MM.md`

### Categories (Keep a Changelog Standard)

- **Added** - New features
- **Changed** - Changes to existing functionality
- **Deprecated** - Soon-to-be-removed features
- **Removed** - Removed features
- **Fixed** - Bug fixes
- **Security** - Security fixes

### Token Efficiency Target

- **Current entry:** 60-80 tokens
- **Entire file:** <10,000 tokens (with archival strategy)
- **Archive trigger:** Versions older than 30 days

