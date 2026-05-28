---
doc: CHANGELOG
related:
  devlog: ./DEVLOG.md
  state: ./STATE.md
  adr_index: ./adr/README.md
---

# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📖 **[DEVLOG](./DEVLOG.md)** - Development narrative and decision rationale
📈 **[STATE](./STATE.md)** - Current project state (the now)
⚖️ **[ADRs](./adr/README.md)** - Architectural decision records

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see STATE.md.

---

## [Unreleased]

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

## Archive

Older versions are archived when the file exceeds its token budget (~10,000 tokens).
Each link includes a brief summary so agents know what's inside without opening the file:
- *No archived entries yet*

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
7. **Summarize archives** - Each archive link should have a brief description of contents

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

