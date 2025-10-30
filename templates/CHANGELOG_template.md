# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../specs/PRD.md)** - Product requirements and specifications
📖 **[DEVLOG](DEVLOG.md)** - Development narrative and decision rationale
📐 **[Architecture](../docs/architecture.md)** - System architecture and design

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see DEVLOG.md → Current Context section.

---

## [Unreleased] - v0.7.0-dev

### Added
- Feature name - Brief description. Files: `path/to/file.py`. PR: [#1234](link)
- Feature name - Brief description. Files: `path/to/file.py`. PR: [#1235](link)

### Changed
- Feature name - Brief description. Files: `path/to/file.py`. PR: [#1236](link)

### Fixed
- Bug description - Root cause and fix. Files: `path/to/file.py`. PR: [#1237](link)

### Deprecated
- Feature name - Deprecation reason and timeline. Migration: [docs/migrations/feature.md](link)

### Removed
- Feature name - Removal reason. Migration: [docs/migrations/feature.md](link)

---

## [0.6.4] - 2025-10-29

### Added
- Conservative metadata parsing - `enhance_skill` reads body OR metadata; preserves unknown fields. Files: `enhance_skill.py`, `test_frontmatter_compliance.py`. PR: [#1240](link)
- Onboarding guide for existing skills - Documentation for customer migration. Files: `docs/pilot/onboarding-existing-skills.md`. PR: [#1240](link)

### Changed
- Feedback sampling strategy - First use: 100%, subsequent: 20% to reduce user fatigue. Files: `create_skill.py`. PR: [#1241](link)

### Fixed
- YAML description truncation - Removed "..." suffix that broke parsing. Files: `create_skill.py`. PR: [#1242](link)

---

## [0.6.3] - 2025-10-29

### Fixed
- YAML frontmatter compliance - Moved `alias`, `version`, `id` to metadata block per Claude spec. Files: `create_skill.py`, `enhance_skill.py`. PR: [#1235](link)

---

## [0.6.2] - 2025-10-28

### Added
- Skill alias and version persistence - Per-org uniqueness, case-insensitive. Files: `database/schema.sql`, `tools/*.py`. PR: [#1230](link)
- Usage analytics with version/platform tracking - New breakdowns in `get_usage_summary`. Files: `analytics.py`, `database/views.sql`. PR: [#1231](link)
- Governance bundle in packaged skills - Provenance and changelog included. Files: `package_skill.py`. PR: [#1232](link)

### Changed
- Feature flag for DB-dependent features - `CSF_DB_V062_MIGRATED=1` gates new functionality. Files: `config.py`, all tools. PR: [#1233](link)

---

## Archive

**Versions older than 30 days** are archived for token efficiency:
- [CHANGELOG-2025-10.md](../archive/CHANGELOG-2025-10.md) - October 2025 (v0.5.x - v0.6.1)
- [CHANGELOG-2025-09.md](../archive/CHANGELOG-2025-09.md) - September 2025 (v0.3.x - v0.4.x)
- [CHANGELOG-2025-08.md](../archive/CHANGELOG-2025-08.md) - August 2025 (v0.1.x - v0.2.x)

---

## Template Guidelines (Remove this section in actual use)

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

### What NOT to Include

- ❌ Planning updates (put in DEVLOG)
- ❌ Design rationale (put in DEVLOG)
- ❌ Long narratives (put in DEVLOG)
- ❌ Code examples (link to files)
- ❌ Test results (link to CI/PR)
- ❌ "Why This Matters" sections (put in DEVLOG)

### Token Efficiency Target

- **Current entry:** 60-80 tokens
- **Entire file:** <10,000 tokens (with archival strategy)
- **Archive trigger:** Versions older than 30 days

