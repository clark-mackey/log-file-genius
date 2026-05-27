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
- `README.md` (line ~76): the entire "Safety Built In" sentence is undelivered by default — secret detection, log validation, **and** pre-commit hooks all run only via the hook, and the hook is installed only by `install.sh --with-hooks`, **a flag that does not exist in the installer**. Correct the whole sentence to match reality (these are opt-in tools the user must wire manually), and remove the `--with-hooks` reference from the hook's own header comment. Wiring a hook into the installer is deferred to Spec 2.
- **Acceptance:** after `install` then `update` on a temp project, the rule files are byte-identical and match `ai-rules/`, on **both** bash and PowerShell (see Testing).

### B. One canonical token budget
The budget numbers currently live in at least four places: rule files, `project_instructions.md`, `profiles/*.yml`, and **`validate-log-files.sh`/`.ps1` hardcoded thresholds** (8k/10k warn/error CHANGELOG, 12k/15k DEVLOG). Re-stating the canonical numbers in all of them recreates the exact drift that caused the original contradiction.
- **Authoritative source:** `profiles/*.yml` token targets are the single source of truth for tooling. The shell/python validators read from config/profile, not hardcoded constants — remove the hardcoded thresholds in `validate-log-files.sh`/`.ps1` and have them load profile values (with the canonical defaults as the only fallback, defined once).
- Human-facing rule files may still state the numbers inline (an agent reading a rule needs the figure), but they must match the authoritative defaults.
- `ai-rules/claude-code/project_instructions.md`: change "<10k combined" to per-file CHANGELOG <10k / DEVLOG <15k / combined <25k + STATE <500.
- **Guard:** a consistency test (see Testing) parses every budget literal across rule files, profiles, validators, and docs and fails if any disagree — not a one-time grep for the old string.
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
- **Enumerate and convert every path consumer** — the `paths:` block is worthless if only some readers honor it. Known readers: `lfg.py` / `lint-logs.py`, `validate-log-files.sh` (hardcodes `CHANGELOG_PATH="logs/CHANGELOG.md"`), `validate-log-files.ps1`, `validation-report.py`, the pre-commit hook, and the four rule files. Each must resolve paths from `.logfile-config.yml` → `paths` with the same `logs/` fallback. A test asserts no consumer carries a hardcoded path constant.

### E. Framework token diet
- Compress the installed rule set: `log-file-maintenance.md`, `project_instructions.md`, `status-update.md`, `update-planning-docs.md` (both `augment` and `claude-code`).
- Method: merge overlapping sections, cut restated preamble, tighten wording. **No behavior removed.**
- **Objective completeness gate (not human judgment):** before compressing, extract the full set of directives/section headings into a committed checklist artifact (`docs/superpowers/specs/2026-05-27-rule-directives.md` or similar). After compressing, a test greps each compressed rule file for every named directive/heading and fails if any is missing. This replaces the subjective "confirm the same list is present."
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
- **Avoid maintaining two link graphs.** The frontmatter `related:` map is the single source of truth for the cross-link graph; the prose section is a human-readable rendering of the same graph. Since these are static templates (no build step — minimalism), do not duplicate by hand: define the graph once in this spec as a table, populate both representations from it, and add a sync test (see Testing) that fails if a doc's prose links and its frontmatter `related:` keys diverge.
- **Named consumer:** the frontmatter exists so Spec 2's agent-agnostic entry point can parse the doc graph deterministically (no prose scraping). It is not decorative; it is the machine-readable contract Spec 2 will read. If Spec 2 slips, the frontmatter still serves as the authoritative definition the sync test enforces.

### G. Brownfield migration + re-dogfood
- **Migration:** existing installs hold "the now" in DEVLOG (Current Context + Last Session). After this change the rules read/write STATE, orphaning that data. `update.sh`/`.ps1` must detect a DEVLOG "Current Context" / "Last Session" section and either move it into `STATE.md` (preferred) or print a one-time, explicit notice telling the user to move it. Silent orphaning is not acceptable.
- **Re-dogfood this repo:** apply the new model to this repository's own `logs/` — create a root-level `STATE.md`, move the stale DEVLOG Current Context (dated 2026-02-01) into it, and trim DEVLOG accordingly. The product and its own usage drifting apart is what produced several of these defects; keep them in lockstep.

### Bonus correctness: PyYAML → stdlib
- `lint-logs.py`: replace `import yaml` + `yaml.safe_load` with a minimal stdlib parse of the only keys used (`profile`, `paths`, `overrides.token_targets`). The shell validators already extract these via regex, so no behavior change there.
- **Constrain and test the parser.** YAML is deceptively complex; a hand-rolled subset parser must (a) document the supported config subset, (b) be tested against every real `profiles/*.yml` plus a sample with quotes and inline comments, and (c) **fail loudly** on anything outside the subset rather than silently returning wrong values.

## Sequencing

Items C, D, and E all edit the same four rule files; editing them per-work-item invites rework and conflicts. Sequence the implementation **per file, not per work item**: for each rule file, apply the STATE repointing (C), path-config reads (D), and compression (E) in a single pass. Suggested order: (1) profiles/validators as the budget source of truth (B), (2) templates + frontmatter graph (C, F), (3) one editing pass per rule file (C+D+E together), (4) installer `paths:` block + README + delete starter-packs + repoint update (A, D), (5) migration + re-dogfood (G), (6) PyYAML (bonus). Stage as reviewable commits per item.

## Testing

Per project standards (pytest, tests alongside code):
- **pytest** for the stdlib config parser: returns correct `profile`, `paths`, and `overrides.token_targets` for every real `profiles/*.yml`, a config with no `paths:`, and a sample with quotes/inline comments; raises loudly on out-of-subset input.
- **Installer smoke test on BOTH bash and PowerShell** (temp dir): run install then update and assert:
  - `logs/CHANGELOG.md`, `logs/DEVLOG.md`, `logs/STATE.md`, `logs/adr/` exist.
  - `.logfile-config.yml` contains a `paths:` block.
  - Installed rule files are byte-identical after install and after update (no divergence), and identical between the two platforms.
  - Templates carry YAML frontmatter with a `related:` map.
- **Budget consistency test:** parse every token-budget literal across rule files, profiles, validators, and docs; fail on any disagreement.
- **Path-consumer test:** assert no path consumer (validators, report, hook, rules) carries a hardcoded path constant; all resolve from `paths:` with `logs/` fallback.
- **Frontmatter↔prose sync test:** for each template, the prose Related Documents links and the frontmatter `related:` keys must match.
- **Rule-directive completeness test:** each compressed rule file contains every directive/heading from the pre-compression checklist artifact.
- **Brownfield migration test:** seed a temp project with a legacy DEVLOG (Current Context + Last Session, no STATE.md), run `update`, assert the data lands in STATE.md (or a one-time notice is printed) — never silently dropped.
- **Consistency check:** no remaining `docs/planning/` hardcoded paths in `ai-rules/`; no `starter-packs/` references anywhere; no "<10k combined" budget string; no `--with-hooks` reference.

## Risks & mitigations

- **Touching the installers (the historically painful part):** changes are minimal and additive — `update.*` is a one-line `RULES_SRC` change; `install.*` adds a `paths:` block. No control-flow restructure. Windows-syntax drift is contained by running the smoke test on both bash and PowerShell and asserting cross-platform parity.
- **Token-diet over-cutting:** mitigated by the committed directive checklist + completeness test (objective, not judgment).
- **STATE move breaks session continuity guidance:** mitigated by updating SESSION START/END in the rules in the same per-file pass, plus the brownfield migration step and test.
- **Budget/path numbers re-duplicating:** mitigated by a single authoritative source (profiles) and consistency tests that fail on divergence, rather than one-time greps.
- **Frontmatter as dead weight:** mitigated by making it the single source for the link graph (prose rendered from it, sync-tested) and naming Spec 2 as the consumer.
- **Hand-rolled YAML parser fragility:** mitigated by a documented subset, tests against real profiles, and loud failure on out-of-subset input.

## File inventory (touched)

- Delete: `product/starter-packs/**`
- Scripts: `product/scripts/update.sh`, `update.ps1`, `install.sh`, `install.ps1`, `lint-logs.py`, `check-ai-rules.py`, `validate-log-files.sh`, `validate-log-files.ps1`, `validation-report.py`, `pre-commit`
- Rules: `product/ai-rules/{augment,claude-code}/log-file-maintenance.md`, `project_instructions.md` (claude-code), `status-update.md`, `update-planning-docs.md`
- Templates: `product/templates/{CHANGELOG,DEVLOG,STATE,ADR}_template.md`
- Docs: `README.md`, `product/docs/log_file_how_to.md`
- Profiles: `product/profiles/*.yml` (authoritative budget source)
- This repo's own logs (re-dogfood): `logs/DEVLOG.md`, new `STATE.md`
- Artifacts: rule-directive checklist (for the completeness gate)
- Tests: new pytest (parser, budget consistency, path consumers, frontmatter sync, directive completeness, brownfield migration) + cross-platform installer smoke test
