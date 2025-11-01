# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- New feature for user authentication. Files: `src/auth.js`. Commit: `abc123`
- API endpoint for data export. Files: `src/api/export.js`. Commit: `def456`

### Changed
- Updated database schema for better performance. Files: `db/schema.sql`. Commit: `ghi789`

### Fixed
- Bug in login validation. Files: `src/auth.js`. Commit: `jkl012`

---

## [1.0.0] - 2025-10-31

### Added
- Initial release with core features
- User management system
- Data visualization dashboard

### Changed
- Improved error handling across all modules

### Fixed
- Memory leak in background worker
- Race condition in cache invalidation

---

## [0.9.0] - 2025-10-15

### Added
- Beta release for testing
- Basic CRUD operations
- Simple authentication

### Deprecated
- Old API endpoints (will be removed in 2.0.0)

---

## Token Efficiency Targets

- **Per entry:** ~50-100 tokens (concise descriptions)
- **Entire file:** <10,000 tokens (with archival strategy)
- **Archive trigger:** Versions older than 30 days

