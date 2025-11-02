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

### Added
- Two-branch strategy (ADR-009) - Implemented two-branch strategy to restore version control for project/ files while maintaining clean user experience. Main branch contains only product/ (for distribution), development branch contains both product/ and project/ (for work). Both branches public (transparency). Resolves issue where ADR-008 excluded project/ from git, losing version control for planning documents. Created workflow guide documenting daily development and release processes. Files: `project/adr/009-two-branch-strategy.md`, `project/WORKFLOW.md`, `.gitignore`, all project/ files (17 files, 4,487 insertions). Commit: `58ca9f9`
- Epic 12 spec (Security & Secrets Detection) - Created comprehensive epic specification for preventing AI assistants from leaking secrets (passwords, API keys, PII) into git history. Includes 8 tasks covering security rules, SECURITY.md policy, secrets detection scripts, pre-commit hook integration, redaction guide, examples, and starter pack integration. Identified as P0 critical blocker based on Red Team Analysis. Files: `project/specs/EPIC-12-security-secrets-detection.md`. Commit: `58ca9f9`
- Epic 13 spec (Validation & Reliability) - Created comprehensive epic specification for verifying AI assistants reliably maintain logs correctly. Includes 10 tasks covering log linter, post-commit verification, GitHub Actions workflow, validation dashboard, self-assessment prompts, examples, and starter pack integration. Builds on Epic 7 validation system. Identified as P0 critical blocker based on Red Team Analysis. Files: `project/specs/EPIC-13-validation-reliability.md`. Commit: `58ca9f9`
- Epic 15 spec (Governance & Review) - Created simplified epic specification for lightweight review processes focused on solo developers and teams (not full enterprise). Includes 8 tasks covering ADR lifecycle, human-in-the-loop rules, PR review checklist, rollback procedures, conflict resolution guide, examples, and starter pack integration. Identified as P1 high priority. Files: `project/specs/EPIC-15-governance-review.md`. Commit: `58ca9f9`
- Revised roadmap - Created security-first roadmap based on Red Team Analysis and Competing Repositories Analysis. Pauses Epic 9-11 (Skills, Workflows, Layered Context) to focus on critical blockers. Defines 3 phases: Phase 1 (Epic 12-13, weeks 1-4), Phase 2 (Epic 15, week 5), Phase 3 (dogfooding & feedback, week 6). Defers Epic 14 (RAG) and Epic 16 (Enterprise) to later phases. Includes prioritization framework (P0/P1/P2/P3), success metrics, competitive positioning, and risk assessment. Files: `project/specs/ROADMAP-REVISED-2025-11.md`, `project/specs/ROADMAP-SUMMARY.md`. Commit: `58ca9f9`
- Profile system (Epic 8) - Created profile configuration schema and 4 predefined profiles (solo-developer, team, open-source, startup) with customizable token targets, required files, update frequency, validation strictness, and archival thresholds. Integrated with validation scripts to apply profile-specific rules. Created comprehensive profile selection guide with decision tree, comparison table, migration paths, and customization examples. Added profile configuration to both starter packs with setup instructions. Updated AI assistant rules to be profile-aware and respect profile settings. Files: `product/docs/profile-schema.md`, `product/docs/profile-selection-guide.md`, `product/profiles/*.yml`, `product/templates/.logfile-config.yml`, `product/scripts/validate-log-files.ps1`, `product/scripts/validate-log-files.sh`, `product/starter-packs/augment/.logfile-config.yml`, `product/starter-packs/claude-code/.logfile-config.yml`, `product/starter-packs/*/README.md`, `.augment/rules/log-file-maintenance.md`, `product/starter-packs/*/.augment/rules/log-file-maintenance.md`, `product/starter-packs/*/.claude/rules/log-file-maintenance.md`. Commit: `54f2cbd`
- Update notification system - Added version tracking to `.logfile-config.yml`, integrated version checking into validation scripts (warns when updates available), created check-for-updates scripts (PowerShell and Bash) that query GitHub API for latest release, created migration guide template for release documentation, and comprehensive update notifications documentation. Users are now notified of available updates during validation and can manually check for updates anytime. Files: `product/templates/.logfile-config.yml`, `product/starter-packs/*/.logfile-config.yml`, `product/scripts/validate-log-files.ps1`, `product/scripts/validate-log-files.sh`, `product/scripts/check-for-updates.ps1`, `product/scripts/check-for-updates.sh`, `product/templates/MIGRATION_GUIDE_template.md`, `product/docs/update-notifications.md`. Commit: `754bc49`

### Changed
- Strategic roadmap - Analyzed Red Team Analysis and Competing Repositories Analysis research documents. Identified 5 critical failures (security, validation, governance, retrieval, enterprise integration). Created security-first roadmap that pauses Epic 9-11 to focus on P0 blockers (Epic 12-13) and P1 team features (Epic 15). Updated DEVLOG Current Context to reflect new phase (Security & Validation) and objectives. Target: 6 weeks to "shareable with experienced devs" state. Files: `project/planning/DEVLOG.md`, `project/specs/ROADMAP-REVISED-2025-11.md`. Commit: `58ca9f9`
- Epic 8 status - Marked Epic 8 (Profile System) as complete with all 10 tasks finished. Updated task list in spec file and DEVLOG Current Objectives. Added DEVLOG entry documenting completion. Files: `project/specs/EPIC-08-11-other-enhancements.md`, `project/planning/DEVLOG.md`, `project/planning/CHANGELOG.md`. Commit: `58ca9f9`
- **BREAKING:** Directory structure - Separated product/ (distributable content) from project/ (development files) to eliminate AI agent confusion between templates and working logs. All templates, docs, examples, starter-packs moved to product/. All planning, ADRs, specs moved to project/. Updated .gitignore to exclude project/ directory. Files: All files restructured, .gitignore, README.md, all cross-references. Commits: `62adf96`, `05d846a`, `9872d72`, `89f65a1`
- Scripts location - Moved from `scripts/` to `product/scripts/` for proper product/project separation. Updated all references in documentation and starter packs. Files: `scripts/` → `product/scripts/`, `.gitignore`, `product/docs/*.md`, `product/starter-packs/*/README.md`. Commit: `89f65a1`
- Augment rules location - Moved from `.augment/rules/` to `starter-packs/augment/.augment/rules/` for better distribution. Files: `starter-packs/augment/.augment/rules/log-file-maintenance.md`, `starter-packs/augment/.augment/rules/status-update.md`, `starter-packs/augment/.augment/rules/update-planning-docs.md`. Commit: `a93e543`
- .gitignore - Simplified to exclude entire `.augment/` and `.claude/` directories instead of individual files. Files: `.gitignore`. Commit: `a93e543`
- Augment starter pack README - Updated setup instructions to reflect new `.augment/` directory location. Files: `starter-packs/augment/README.md`. Commit: `a93e543`
- Bash validation script (Epic 7) - Created cross-platform Bash version of validation script for Mac/Linux/WSL users, ensuring true cross-platform support. Uses only standard Unix tools (grep, wc, awk). Files: `scripts/validate-log-files.sh`, `starter-packs/*/scripts/validate-log-files.sh`, `starter-packs/*/README.md`. Commit: `pending`
- Validation in starter packs (Epic 7) - Added validation scripts and git hooks to both starter packs, updated READMEs with installation instructions, updated log-file-maintenance rule to reference validation. Files: `starter-packs/*/scripts/`, `starter-packs/*/.git-hooks/`, `starter-packs/*/README.md`, `starter-packs/*/.augment/rules/log-file-maintenance.md`, `starter-packs/*/.claude/rules/log-file-maintenance.md`. Commit: `4abca10`
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

