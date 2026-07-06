# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## Related Documents

📋 **[PRD](../project/specs/prd.md)** - Product requirements and specifications
📖 **[DEVLOG](DEVLOG.md)** - Development narrative and decision rationale
⚖️ **[ADRs](adr/README.md)** - Architectural decision records

> **For AI Agents:** This file is a concise technical record of changes. For context on *why* decisions were made, see DEVLOG.md. For current project state, see [STATE.md](STATE.md).

---

## [Unreleased]

### Fixed

- Dogfood repair: rebuilt this CHANGELOG with v0.3.0–v0.5.0 version blocks (entries had pooled in `[Unreleased]` since February), fixed mojibake emoji (UTF-8 read as cp1252), repointed stale "current state → DEVLOG" header note at STATE.md, removed leftover template-guidelines section. STATE.md and DEVLOG brought current. Files: `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/STATE.md`.

### Added

- Dogfood Spec 5: filed first standalone incident report (stale-logs dogfooding failure) and generated `logs/incidents/README.md` index via `lfg incidents-index`. Files: `logs/incidents/2026-07-05-dogfood-logs-went-stale.md`, `logs/incidents/README.md`.

## [0.5.0] - 2026-07-05

Spec 5 — first-class incident reports. Promoted to `main` via [PR #12](https://github.com/clark-mackey/log-file-genius/pull/12).

### Added

- INCIDENT_template.md — lightweight, ADR-style standalone incident report (frontmatter linking; Summary/Timeline/Root Cause/Resolution/Prevention/Detection/Files; word severities). Files: `product/templates/INCIDENT_template.md`. Commit: `63be463`
- `incidents.py` tolerant parser + index builder; `lfg incidents-index` CLI verb; installer seeds template + index, un-orphaning `logs/incidents/`. Backward-compatible with pre-existing date-prefixed reports. Files: `product/scripts/incidents.py`, `product/scripts/lfg.py`, `product/scripts/install.sh`, `product/scripts/install.ps1`. Commit: `63be463`, `6b77a73`
- Escalation note in maintenance rule + DEVLOG template: inline `🚨 INCIDENT` entry stays the default; rubric-flagged incidents also get a standalone report. AGENTS.md regenerated. Files: `product/rules/log-file-maintenance.md`, `product/templates/DEVLOG_template.md`, `product/AGENTS.md`. Commit: `71d46d7`
- README: human-dev-team problem/solution section; tagline retune + `lfg install-hooks` surfaced. Files: `README.md`. Commit: `17838c9`, `173e0c4`

### Fixed

- check-version: normalize BOM + line endings before checksum so baselines pass on every platform. Files: `product/scripts/check-version.py`. Commit: `5a262a0`
- Template-hash manifest: normalize BOM + CRLF/CR→LF before hashing (same policy); manifest rebuilt on normalized basis (0.3.0 from tag, 0.4.0 from shipped main, 0.5.0 from HEAD). Files: `product/scripts/update_template_hashes.py`, `product/scripts/known_template_hashes.json`. Commit: `0e78913`
- `lfg validate`: forward `--changelog`/`--devlog` (not `-only` variants) to lint-logs. Files: `product/scripts/lfg.py`. Commit: `f451aef`
- Config template version reconciled to 0.5.0 after Spec 5 merge; doc paths corrected. Files: `product/templates/.logfile-config.yml`. Commit: `bd1a49b`, `dc04e95`

### Changed

- How-to accuracy pass for v0.4.0: replaced phantom script references with real `lfg` CLI verbs. Files: `product/docs/log_file_how_to.md`. Commit: `15c1925`

## [0.4.0] - 2026-06-01

Spec 4 — brownfield-safe install & update. Promoted via PR #8.

### Added

- Managed-block AGENTS.md merge engine + `lfg merge-agents-md` (BEGIN/END markers, version capture, forward-compat refusal, `--no-wrap`, `--force-downgrade`). Files: `product/scripts/agents_merge.py`, `product/scripts/lfg.py`. Commit: `1290f34`, `32dafd1`
- SHA-256 template manifest (`known_template_hashes.json`) + `update_template_hashes.py` with `--check` CI gate and `--match-dir` recognition of LFG-shipped files. Files: `product/scripts/update_template_hashes.py`. Commit: `5177646`
- `lfg migrate-state`: brownfield STATE.md migration module + subcommand + post-update advisory. Files: `product/scripts/migrate_state.py`, `product/scripts/lfg.py`. Commit: `4fc880e`, `fe0c66a`
- `lfg validate --state-only` granular validation. Files: `product/scripts/lfg.py`. Commit: `c20cd5a`
- Cross-platform install/update merge + template smoke coverage. Files: `product/tests/smoke_install.sh`, `product/tests/smoke_install.ps1`. Commit: `572da0a`

### Changed

- Install/update merge AGENTS.md instead of clobbering; update backs up LFG-installed root templates and stops copying templates to project root. Files: `product/scripts/install.sh`, `product/scripts/install.ps1`, `product/scripts/update.sh`, `product/scripts/update.ps1`. Commit: `8ce5bb0`, `d884c5e`, `5177646`

### Fixed

- Validators: corrected backwards version-check + stale hardcoded latest version. Files: `product/scripts/validate-log-files.sh`, `product/scripts/validate-log-files.ps1`. Commit: `31ca4c9`
- Merge idempotency compares raw bytes so BOM/CRLF gets normalized; original backed up before lossy wrap-replace of AGENTS.md. Files: `product/scripts/agents_merge.py`. Commit: `691f9eb`, `9dcb4de`

## [0.3.0] - 2026-05-29

Specs 1–3, released together: consistency & correctness (PR #5), agent-agnostic core (PR #6), graceful work-aware archival (PR #7).

### Added

- Spec 2: canonical `product/rules/` fragments with YAML frontmatter; `lfg generate` renders AGENTS.md (budget-gated) + per-tool rule files; `lfg generate --check` CI drift gate. Files: `product/rules/*`, `product/scripts/generator.py`, `product/scripts/lfg.py`. Commit: `7f4cedc`, `0845476`, `ec49110`, `0874b31`
- Spec 2: subagent contract — `lfg prime` context digest with `LFG_SUBAGENT_PRIME` identity marker; `lfg promote` category-aware staged-entry promotion with audit log. Files: `product/scripts/primer.py`, `product/scripts/promoter.py`. Commit: `d32d4ca`, `6c4728b`
- Spec 3: `lfg archive` — deterministic, work-aware archival (CHANGELOG version-block, DEVLOG fit-the-budget); protects `[Unreleased]`, STATE, ADRs; `--dry-run` preview, `--force` apply. Files: `product/scripts/archive.py`, `product/scripts/lfg.py`. Commit: `80afada`–`5d2b002`
- llms.txt guiding AI agents to correct installation. Files: `llms.txt`. Commit: `42b9b95`

### Changed

- Spec 1: stdlib YAML-subset config parser (dropped PyYAML); validators + installer read a single `.logfile-config.yml` `paths:`/`token_targets:` block. Files: `product/scripts/config_parser.py`, `product/scripts/lint-logs.py`, `product/scripts/validate-log-files.sh`, `product/scripts/validate-log-files.ps1`. Commit: `73889fa`, `6e55990`, `9a28b93`, `ed36213`
- Spec 1: STATE.md owns "the now" (DEVLOG trimmed to narrative); `logs/` path standardization; frontmatter link graph across all templates; token diet on rule files. Files: `product/templates/*`, `product/ai-rules/*`. Commit: `a9363b2`, `059cfe4`, `417e0c8`
- Spec 1: removed `starter-packs/` (fixed install≠update downgrade bug); update scripts migrate legacy DEVLOG context into STATE.md. Files: `product/scripts/update.sh`, `product/scripts/update.ps1`. Commit: `7f604b7`, `d32057f`
- Spec 3: profiles' `archival:` block slimmed to `keep_fraction` only; rules ARCHIVAL section points at `lfg archive`. Files: `product/profiles/*.yml`, `product/rules/log-file-maintenance.md`. Commit: `3e26e80`, `68ab268`
- PRD v0.5–v0.9 planning arc: major refocus (rejected Epics 9/10/11 for mission drift), Epic list completion (12/13/17/19 added, 15 deferred, 18 rejected), Stories 8.6–8.11 agent-first features implemented, Epic 10 revised to agent-agnostic multi-agent support (SESSION END guard), Epic 17 rejected in favor of lightweight `🚨 INCIDENT` DEVLOG format. Files: `project/specs/prd.md`, `product/templates/DEVLOG_template.md`, rule files. Commit: `7782a6c`, `2820362`, `5148e2a`, `1643aae`, `1549a6e`
- README rewritten around agent performance, not documentation efficiency. Files: `README.md`. Commit: `8f20e71`

### Fixed

- Scrubbed Skill Flywheel data from product templates and docs (replaced real project examples with generic placeholders). Files: `product/templates/*`, `product/docs/log_file_how_to.md`. Commit: `20764b1`
- CI: replaced retired `macos-13` runner with `macos-15`. Files: `.github/workflows/test-installer.yml`. Commit: `4179209`
- Validators: exit 0 on warnings in default mode (CI regression); config parser handles BOM + decode errors as ConfigError. Commit: `e2bd212`, `9d8d886`

---

## Archive

**Versions older than 30 days** are archived for token efficiency:

- [CHANGELOG-v0.2.0-to-v0.2.0.md](archive/CHANGELOG-v0.2.0-to-v0.2.0.md) — versions v0.2.0 through v0.2.0; archived ~10218 tokens, 1 version blocks
