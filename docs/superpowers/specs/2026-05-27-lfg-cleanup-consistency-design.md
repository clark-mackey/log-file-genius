# LFG Cleanup — Consistency & Correctness (Spec 1 of 3)

**Date:** 2026-05-27
**Status:** Draft for review
**Branch:** `development`

## Context

Log File Genius (LFG) gives AI agents a token-dense view of project history using mostly markdown. The product is several months old and has drifted from its goals in ways that actively confuse the agents it's meant to help. This spec covers **consistency and correctness fixes on the current architecture** — no new capabilities. Two follow-on specs are deferred:

- **Spec 2 — Agent-agnostic redesign:** neutral `AGENTS.md` entry point, a single canonical rules source that generates per-tool adapters, deterministic-command surface, and subagent conventions.
- **Spec 3 — Graceful work-aware archival:** archive by completion, never sever context from in-flight work.

The user chose to do cleanup first, accepting that some of it will be reworked when Spec 2 consolidates the same files. Locking the *shipped* product to a correct, consistent state has standalone value because people may install it today.

## Problems being fixed

1. **Install ≠ update (silent downgrade bug).** `install.*` copy rules from `ai-rules/`; `update.*` copy from `starter-packs/`. The two have diverged, so running the updater downgrades a user's rules to a stale version.
2. **Contradictory token budgets.** `project_instructions.md` says "<10k combined"; `log-file-maintenance.md` says per-file 10k/15k/25k.
3. **STATE is muddled.** Installed as `STATE.md`, but the DEVLOG template duplicates its purpose via "Current Context" + "Last Session."
4. **Broken path story.** Installer writes everything to `logs/`, but the generated config has no `paths:` block, `project_instructions.md` defaults to `docs/planning/`, and `status-update.md` / `update-planning-docs.md` hardcode `docs/planning/`.
5. **Framework bloat.** Installed rule files (~230 lines / ~2k tokens each, several of them) eat the context budget LFG promises to save.
6. **Undeclared dependency.** `lint-logs.py` imports PyYAML with no `requirements.txt` → silent `ImportError` for fresh users.
7. **Frontmatter linking is aspirational.** README advertises "bidirectional frontmatter linking"; templates have none, and prose cross-links are incomplete/asymmetric.

## Decisions (locked with user)

- **Rules source of truth:** `ai-rules/` is canonical. Repoint `update.*` at it and **delete `starter-packs/` entirely.**
- **Token budgets:** CHANGELOG <10k, DEVLOG <15k, combined <25k everywhere. STATE <500 tokens. Profiles may override; these are the defaults.
- **STATE (Option 3):** Keep a dedicated tiny `STATE.md` as the single home for "the now." Remove Current Context + Last Session from the DEVLOG template. The five-document framing stays (PRD, CHANGELOG, DEVLOG, STATE, ADRs).
- **Paths:** Standardize on `logs/`. Installer emits an explicit `paths:` block; all rules/docs read config with a `logs/` fallback.
- **PyYAML:** Remove the dependency; parse the few needed config keys with stdlib. LFG stays zero-dependency.
- **Frontmatter:** Implement real YAML frontmatter with a `related:` map on every installed doc; keep prose Related Documents links; make the cross-link graph complete and symmetric.

## Non-goals (explicitly deferred)

- `AGENTS.md` / agent-agnostic entry point, subagent conventions, deterministic-command surface → Spec 2.
- Graceful archival algorithm → Spec 3.
- Wiring a pre-commit hook into the installer → Spec 2 (the installer never installed one; see A below).

## Work items

### A. Kill starter-packs; unify rules source
- Delete `product/starter-packs/` (all of it).
- `update.sh` / `update.ps1`: change `RULES_SRC` from `product/starter-packs/$assistant` to `product/ai-rules/$assistant`, matching the installer. Verify the copy walk still works for the `ai-rules/` layout.
- `check-ai-rules.py`: remove the starter-packs exclusion comment/logic (line ~204).
- `README.md` (line ~76): the "pre-commit hooks" safety claim is currently undelivered (the installer never installs a hook; the only hook lived in starter-packs). Soften the claim to match reality. Wiring a hook into the installer is deferred to Spec 2.
- **Acceptance:** after `install` then `update` on a temp project, the rule files are byte-identical and match `ai-rules/`.

### B. One canonical token budget
- `ai-rules/claude-code/project_instructions.md` (and the `.claude/` copy if present): change "<10k combined" to per-file 10k/15k/25k + STATE <500.
- Read `product/profiles/*.yml` and `lint-logs.py` token defaults; align any that disagree with the canonical numbers. Profiles keep override capability.
- Confirm `README.md` budget table matches (it already shows CHANGELOG <10k, DEVLOG <15k — verify, don't churn).

### C. STATE Option 3 — single home for "the now"
- **Keep** installer creation of `logs/STATE.md` and its install-validation.
- **Expand `STATE_template.md`** to be the single "now": Current Context fields (version, branch, phase, current objectives, known risks/blockers) + a "Last Session" handoff block (Done / In Progress / Next / Branch+Commit). Keep it under ~500 tokens.
- **Trim `DEVLOG_template.md`:** remove the "Current Context" and "Last Session" sections; DEVLOG keeps only the narrative Daily Log + Archive. Update the "For AI Agents" note to point at STATE for the now, DEVLOG for the why.
- **Repoint the rules** in `ai-rules/{augment,claude-code}/log-file-maintenance.md`:
  - SESSION START: read **STATE** (Current Context + Last Session) instead of DEVLOG Current Context. Keep the staleness check, now against STATE's `Last Updated`.
  - SESSION END: write the handoff to **STATE** "Last Session" instead of DEVLOG.
- Update `project_instructions.md` and `log_file_how_to.md` STATE-vs-DEVLOG role descriptions.

### D. Paths — standardize on `logs/` + explicit config
- `install.sh` / `install.ps1`: write a `paths:` block into the generated `.logfile-config.yml`:
  ```yaml
  paths:
    changelog: logs/CHANGELOG.md
    devlog: logs/DEVLOG.md
    state: logs/STATE.md
    adr_dir: logs/adr/
  ```
- `ai-rules/claude-code/project_instructions.md`: change default paths from `docs/planning/...` to `logs/...`; instruct "read `.logfile-config.yml` → `paths`, fall back to `logs/`."
- `ai-rules/{augment,claude-code}/status-update.md` and `update-planning-docs.md`: replace hardcoded `docs/planning/` references with config-read + `logs/` fallback.

### E. Framework token diet
- Compress the installed rule set: `log-file-maintenance.md`, `project_instructions.md`, `status-update.md`, `update-planning-docs.md` (both `augment` and `claude-code`).
- Method: merge overlapping sections, cut restated preamble, tighten wording. **No behavior removed** — before compressing, list every distinct rule/directive; after, confirm the same list is still present.
- Measure: record token estimate (chars/4) per file before and after; report the reduction.

### F. Frontmatter + cross-link graph
- Add YAML frontmatter to `CHANGELOG_template.md`, `DEVLOG_template.md`, `STATE_template.md`, `ADR_template.md`:
  ```yaml
  ---
  doc: DEVLOG
  related:
    changelog: ./CHANGELOG.md
    state: ./STATE.md
    adr_index: ./adr/README.md
  ---
  ```
  Each doc's `related:` map lists the *other* docs (no self-link). STATE/DEVLOG/CHANGELOG sit at `logs/`; the ADR index is `logs/adr/README.md`. PRD is part of the conceptual five-doc system but is not auto-installed, so it is omitted from the installed `related:` maps.
- Keep the prose "## Related Documents" sections; make them complete and symmetric (CHANGELOG must link STATE + ADR; DEVLOG must link ADR).
- Verify every link target resolves relative to install layout (`logs/`).

### Bonus correctness: PyYAML → stdlib
- `lint-logs.py`: replace `import yaml` + `yaml.safe_load` with a minimal stdlib parse of the only keys used (`profile`, `paths`, `overrides.token_targets`). The shell validators already extract these via regex, so no behavior change there.

## Testing

Per project standards (pytest, tests alongside code):
- **pytest** for `lint-logs.py`: stdlib config parsing returns correct `profile`, `paths`, and token-target overrides for representative configs (with/without `paths:`, with overrides).
- **Installer smoke test** (bash, temp dir): run `install.sh` then `update.sh` and assert:
  - `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/STATE.md`, `logs/adr/` exist.
  - `.logfile-config.yml` contains a `paths:` block.
  - Installed rule files are identical after install and after update (no divergence).
  - Templates carry YAML frontmatter with a `related:` map.
- **Consistency check:** no remaining `docs/planning/` hardcoded paths in `ai-rules/`; no `starter-packs/` references anywhere; no "<10k combined" budget string.

## Risks & mitigations

- **Touching the installers (the historically painful part):** changes are minimal and additive — `update.*` is a one-line `RULES_SRC` change; `install.*` adds a `paths:` block. No control-flow restructure. Windows-syntax drift is contained because we're not rewriting logic.
- **Token-diet over-cutting:** mitigated by the before/after directive-list check.
- **STATE move breaks session continuity guidance:** mitigated by updating SESSION START/END in the rules in the same change and the smoke test.

## File inventory (touched)

- Delete: `product/starter-packs/**`
- Scripts: `product/scripts/update.sh`, `update.ps1`, `install.sh`, `install.ps1`, `lint-logs.py`, `check-ai-rules.py`
- Rules: `product/ai-rules/{augment,claude-code}/log-file-maintenance.md`, `project_instructions.md` (claude-code), `status-update.md`, `update-planning-docs.md`
- Templates: `product/templates/{CHANGELOG,DEVLOG,STATE,ADR}_template.md`
- Docs: `README.md`, `product/docs/log_file_how_to.md`
- Profiles: `product/profiles/*.yml` (only if numbers disagree)
- Tests: new pytest + installer smoke test
