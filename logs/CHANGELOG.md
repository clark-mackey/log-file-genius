# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

ðŸ“‹ **[PRD](../project/specs/prd.md)** - Product requirements and specifications
ðŸ“– **[DEVLOG](DEVLOG.md)** - Development narrative and decision rationale
âš–ï¸ **[ADRs](adr/README.md)** - Architectural decision records

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see DEVLOG.md â†’ Current Context section.

---

## [Unreleased]

### Added

- Epic 10 revised: Agent-agnostic multi-agent support. SESSION END guard clause added to all 4 rule files. PRD Epic 10 rewritten with Stories 10.1-10.3. Files: `product/ai-rules/augment/log-file-maintenance.md`, `product/ai-rules/claude-code/log-file-maintenance.md`, `product/starter-packs/augment/.augment/rules/log-file-maintenance.md`, `product/starter-packs/claude-code/.claude/rules/log-file-maintenance.md`, `project/specs/prd.md`. Commit: `1e45f22`
- Implement Stories 8.6-8.11: Session Handoff, Token Self-Assessment, Entry Verbosity, Cross-References, Stale Context Detection, Archival Summaries. All 4 rule files + 2 templates updated. Files: `product/ai-rules/augment/log-file-maintenance.md`, `product/ai-rules/claude-code/log-file-maintenance.md`, `product/starter-packs/augment/.augment/rules/log-file-maintenance.md`, `product/starter-packs/claude-code/.claude/rules/log-file-maintenance.md`, `product/templates/DEVLOG_template.md`, `product/templates/CHANGELOG_template.md`. Commit: `d2611b7`
- Stories 8.6-8.11: Agent-first gap analysis - 6 new stories for Epic 8: Session Handoff Protocol, Self-Assessed Token Counting, Entry Verbosity Control, Cross-File Navigation Hints, Stale Context Detection, Archival Summary Index. All implementable via rule/template changes only - zero new dependencies. Files: `project/specs/prd.md`. Commit: `4c97104`
- Epic 8: AI Context Optimization (NEW) - Replaced old Epic 8 with 5 mission-aligned stories: Smart Context Summarization (<500 tokens), Token Budget Dashboard, AI-Optimized Document Templates, Intelligent Archival Triggers, Context Relevance Scoring. All features directly help AI agents not get lost and not waste tokens. Files: `project/specs/prd.md`. Commit: `b9a9a38`
- Project navigation guide for autonomous agents - Created `project/README.md` explaining directory structure, source of truth hierarchy, and what files to reference. Files: `project/README.md`. Commit: `9ebb777`

- PRD v0.8 alignment pass: Updated Goals (session continuity, self-regulating budgets, minimal dependencies), Background (trimmed), Current State (Feb 2026, resolved issues removed), Technical Assumptions (fixed zero-deps, Augment-only language, manual-only testing), Next Steps (priority order). Files: `project/specs/prd.md`. Commit: `3801f2a`
- PRD v0.9: Epic 17 REJECTED (scope creep). Lightweight incident format added to DEVLOG template with `ðŸš¨ INCIDENT` prefix, 6-item rubric, structured root-cause/prevention fields. Incident format added to both AI rule files. Files: `project/specs/prd.md`, `product/templates/DEVLOG_template.md`, `product/ai-rules/augment/log-file-maintenance.md`, `product/ai-rules/claude-code/log-file-maintenance.md`. Commit: `f6ab74a`
- Epic spec status updates: EPIC-12 â†’ In Progress (Partial), EPIC-13 â†’ In Progress (Partial), EPIC-15 â†’ DEFERRED. DEFINITION-OF-DONE.md fixed broken ROADMAP link, noted Epic 15 deferral. Files: `project/specs/EPIC-12-security-secrets-detection.md`, `project/specs/EPIC-13-validation-reliability.md`, `project/specs/EPIC-15-governance-review.md`, `project/specs/DEFINITION-OF-DONE.md`. Commit: `e719d03`

- README rewrite: reframed around agent performance. New tagline ("Make your AI agents rip"), problem/solution sections focus on agent behavior not token bloat, "Why It's Genius" leads with performance outcomes. Added shipped features: session continuity, self-regulating budgets, incident learning, safety tooling. Fixed broken emoji, removed stale "incidents" reference, updated token budgets. Files: `README.md`. Commit: `70b7ad6`

- Dogfood update: synced local LFG install to latest product version. AI rules updated from 115â†’213 lines (adds session handoff, token self-assessment, entry verbosity, incident format, cross-references, archival summaries). Fixed stale related_docs paths in config. Files: `.augment/rules/log-file-maintenance.md`, `.logfile-config.yml`. Commit: `ec50460`

- Added llms.txt to guide AI agents on correct installation. Prevents agents from pulling files from development branch or manually copying files. Files: `llms.txt`. Commit: `c804312`
### Fixed

- Scrubbed Skill Flywheel data from product templates and docs. Replaced real project examples (enhance_skill, CSF, Supabase, rate_skill) with generic placeholders in all 4 templates and how-to guide. Files: `product/templates/CHANGELOG_template.md`, `product/templates/DEVLOG_template.md`, `product/templates/ADR_template.md`, `product/templates/STATE_template.md`, `product/docs/log_file_how_to.md`. Commit: `2880379`
- CI: replaced retired `macos-13` runner with `macos-15` in test-installer workflow. Files: `.github/workflows/test-installer.yml`. Commit: `4179209`

### Changed

- LFG Schema Proposal revised with tiered approach - Code-Police review accepted Phase 1 (schema), rejected Phase 2/3 (CLI tools, VS Code). Added tiered metadata: Tier 1 inline for CHANGELOG (~18 tokens), Tier 2 condensed block for DEVLOG decisions (~25 tokens), Tier 3 full block for context only. Human readability preserved. Token overhead reduced 46% vs original proposal. Files: `project/docs/proposals/lfg-schema-proposal.md`. Commit: `cfee835`
- PRD v0.6 Epic List completion - Added Epics 12 (Security), 13 (Validation), 17 (Incident Reports), 19 (Dogfooding - marked complete). Deferred Epic 15 (Governance - team process). Rejected Epic 18 (Modular Installer - developer tooling). Archived EPIC-18/19 specs and QA bug report to `project/archive/`. All epics now aligned with mission: help AI agents not get lost, not waste tokens. Files: `project/specs/prd.md`, `project/archive/specs/*`, `project/archive/qa/*`. Commit: `2820362`
- DEVLOG/README clarity for autonomous agents - Fixed incorrect "Completed" status for Epics 12/13 (they're Planned, not complete). Added clear priority order: Epic 7 first (start with Story 7.2), then Epic 8. Updated project/README.md with same priority guidance. Files: `logs/DEVLOG.md`, `project/README.md`. Commit: `731fd7f`
- Merged main branch product updates into development - Synced latest product/ changes from main (v0.2.0 release, token-usage rule, installer fixes). Files: `README.md`. Commit: `33c7c1a`
- PRD v0.5 MAJOR REFOCUS - Code-police review identified 60% mission drift. Rejected Epics 9, 10, 11 (served developers, not AI agents). Epic 7 refined: reordered stories 7.2â†’7.3â†’7.1â†’7.4â†’7.5, added acceptance criteria for backup mechanisms and performance. Mission test: "Does this reduce tokens OR help AI navigate?" Files: `project/specs/prd.md`. Commit: `b9a9a38`
- Planning files cleanup for autonomous agent clarity - Deleted 8 obsolete files (MIGRATION-PLAN, EPIC-08-11, EPIC-07, 3 ROADMAPs, RULE_IMPROVEMENTS, ai-usage-log). Archived 7 research/context files to `project/archive/`. Fixed cross-references in DEFINITION-OF-DONE.md. Updated DEVLOG Current Objectives to February 2026. Result: 28 planning files â†’ 12 focused files with prd.md as source of truth. Files: `project/specs/*`, `project/archive/*`, `logs/DEVLOG.md`. Commit: `9ebb777`

### Removed

- ~~Epic 10: Claude Code Subagents~~ (REJECTED) - No proven architecture, complexity explosion, 2/10 mission alignment
- ~~Epic 9: CLI Tooling~~ (REJECTED) - Developer convenience, not AI benefit, 3/10 mission alignment
- ~~Epic 11: Advanced Automation~~ (REJECTED) - Zero AI benefit, 1/10 mission alignment
- Obsolete planning files (MIGRATION-PLAN.md, EPIC-08-11, EPIC-07, 3 ROADMAPs, RULE_IMPROVEMENTS.md, ai-usage-log.md) - Superseded by PRD or completed

- Epic 8 revised from "MCP Server & Programmatic API" to "Log Automation & Reliability". Analysis of actual log files revealed entries are too detailed (60-80 tokens/CHANGELOG, 500-1000 tokens/DEVLOG) to auto-generate from commits. New focus: enhanced rules, git hook safety nets, CLI scaffolding. MCP deferred to Future Considerations. Files: `project/specs/prd.md`. Commit: `d20f1fe`
- Dogfooding version sync - Updated project's own LFG configuration from v0.1.0-dev to v0.2.0 to match current release. Updated DEVLOG Current Context with current phase (Log Automation & Reliability). Files: `.logfile-config.yml`, `logs/DEVLOG.md`. Commit: `f6145b5`

### Added

- Code-police analysis report documenting architecture evolution from MCP proposal through git-native simplification to final pragmatic approach. Includes original 10 recommendations with implementation status. Files: `context/code-police-analysis-2026-01.md`. Commit: `d20f1fe`

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

## Archive

**Versions older than 30 days** are archived for token efficiency:
- (No archived versions yet)

---
- [CHANGELOG-v0.2.0-to-v0.2.0.md](archive/CHANGELOG-v0.2.0-to-v0.2.0.md) — versions v0.2.0 through v0.2.0; archived ~10218 tokens, 1 version blocks
