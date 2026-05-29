# Spec 3 — Graceful Work-Aware Archival (design)

**Date:** 2026-05-28
**Status:** Approved, awaiting plan
**Branch:** `development`
**Predecessors:**
- [Spec 1 — Consistency & Correctness](2026-05-27-lfg-cleanup-consistency-design.md) — shipped to `main` as PR #5.
- [Spec 2 — Agent-Agnostic Core](2026-05-28-spec2-agent-agnostic-core-design.md) — shipped to `main` as PR #6.

## Context

Specs 1 and 2 hardened the shipped product and made it agent-agnostic. Spec 3 closes the original three-spec roadmap by turning archival from an LLM-driven, blunt "oldest-first by token count" instruction into a **deterministic, work-aware** CLI verb.

The user's original framing when Spec 3 was deferred:

> "enforcing the token limits on the system by actually archiving, in a graceful way (a blindly enforced split on token count can result in context being removed from a large section of work, while that work is underway)"

Today's archival rule (in `log-file-maintenance.md`) instructs the agent to:

```
Triggers: CHANGELOG >10k tokens | DEVLOG >15k tokens | Combined >25k tokens
Action: Archive OLDEST entries first until under budget
Key: Archive by TOKEN COUNT, not date. Recent entries may need archiving if over budget.
```

That "regardless of date" rule is the explicit anti-pattern the user flagged. It can sweep in-flight context into the archive.

This repo is actively over budget right now (CHANGELOG 12,806/10,000; combined 26,029/25,000), so Spec 3 ships against a real dogfood target.

This design incorporates the decisions locked during brainstorming.

## Goals

1. **Deterministic and reviewable.** Archival is a CLI verb (`lfg archive`) with a default `--dry-run` preview; nothing moves without explicit confirmation.
2. **Work-aware.** Use existing structural signals (Keep-a-Changelog's `[Unreleased]`; DEVLOG recency by entry date) to protect in-flight context.
3. **Per-file rules.** CHANGELOG, DEVLOG, STATE, and ADRs each have an appropriate policy. No one-size-fits-all algorithm.
4. **Recoverable.** Archives are plain markdown files in `logs/archive/`; the source file retains an `## Archive` section with links. No data loss; everything stays in-repo.
5. **One knob.** A single `keep_fraction` (default 0.8) controls how much of the budget gets preserved after archival.

## Non-goals

- **ADR archival.** ADRs are decisions; they remain forever.
- **STATE rollback / history.** STATE is a snapshot; trim, don't archive.
- **Auto-archival on commit.** Every move requires explicit user confirmation.
- **`lfg restore <archive>`.** Reversing an archive operation is YAGNI for now.
- **Multi-language fragments.** Spec 2 deferred this; still deferred.

## Decisions (locked with user)

- Archival lives in a **deterministic CLI verb** (`lfg archive`), not in the LLM-driven rule.
- "Active work" signal is **file-specific from existing structure** — CHANGELOG's `[Unreleased]` + DEVLOG's recency window (fit-the-budget).
- DEVLOG retention is **fit-the-budget**: keep the most recent entries that fit within 80% of the budget.
- `keep_fraction` is exposed via `.logfile-config.yml` / profile, **not** as a CLI flag (single knob; profile is the right level).
- Archive filenames use **self-documenting range patterns** (`CHANGELOG-v<a>-to-v<b>.md`, `DEVLOG-<earliest-date>-to-<latest-date>.md`), not the older single-month convention.

## Architecture

```
product/
├── scripts/
│   ├── archive.py            # NEW: pure planning + apply logic
│   └── lfg.py                # MODIFIED: register `archive` subcommand
├── rules/
│   └── log-file-maintenance.md  # MODIFIED: shrink ARCHIVAL section
└── profiles/
    └── *.yml                 # MODIFIED: archival: block reduced to one key
```

The fragment's old "agent decides what's oldest" rule shrinks to one sentence: *"When validators flag overage, run `lfg archive --dry-run`, review the plan, then `lfg archive`."*

The profile's `archival:` block (previously dead) is resurrected with one runtime key:

```yaml
archival:
  keep_fraction: 0.8   # fraction of budget retained after archival
```

Other keys in the old block (`strategy: oldest-first`, `auto_archive_on_error`, `archive_directory`) are removed — superseded by Spec 3's algorithm.

## Components

### `product/scripts/archive.py`

Pure module — parses CHANGELOG and DEVLOG, builds an `ArchivePlan`, and applies it. No I/O until `apply()`. Same testability pattern as Spec 2's `generator.py`.

**Public surface:**

```python
@dataclass
class ArchiveAction:
    source_path: Path        # CHANGELOG or DEVLOG
    archive_path: Path       # logs/archive/<filename>.md
    moved_content: str       # what's moving out of source
    summary_line: str        # the bullet to append to source's `## Archive`
    tokens_before: int
    tokens_after: int

@dataclass
class ArchivePlan:
    actions: List[ArchiveAction]
    refusal_reasons: List[str]  # if Unreleased exceeds budget, etc.
    def is_empty(self) -> bool: ...
    def to_human(self) -> str: ...  # for --dry-run print

def build_plan(
    project_root: Path,
    *,
    keep_fraction: float = 0.8,
    include_changelog: bool = True,
    include_devlog: bool = True,
) -> ArchivePlan: ...

def apply(plan: ArchivePlan) -> None: ...
```

Reuses Spec 1's `config_parser` for `.logfile-config.yml` (path/budget/keep_fraction lookup).

### `product/scripts/lfg.py` — `cmd_archive(args)`

```
lfg archive [--changelog | --devlog | (both default)] [--dry-run] [--force]
```

- **Default** (no flag): build plan, print, prompt `[y/N]`, execute on `y`.
- `--dry-run`: print plan, exit 0, never write.
- `--force`: skip the prompt (still honors work-aware protections).
- `--changelog` / `--devlog`: scope to one file.
- `--state` / `--adr` (rejected): print "STATE/ADRs don't archive — see methodology doc." exit 2.

Exit codes: `0` = success or nothing-to-do, `1` = user declined prompt, `2` = refusal (e.g., `[Unreleased]` exceeds budget), `3` = runtime error.

### `lfg validate` (existing) — pointer update

The current over-budget hint says "Archive old entries to `logs/archive/...`". Update to:

> "Run `lfg archive --dry-run` to see a graceful archival plan."

One line change in `lint-logs.py` and the shell validators.

## File-specific archival rules

### CHANGELOG

**Protected (never archived):**
- File header (title, frontmatter, Related Documents, "based on Keep a Changelog" link).
- The entire `## [Unreleased]` section.
- The `## Archive` section (where prior archives are referenced).

**Archivable:**
- Each released version block (`## [X.Y.Z] — YYYY-MM-DD`), oldest first, until source is under `keep_fraction * budget`.

**Archive file:** `logs/archive/CHANGELOG-v<earliest-moved>-to-v<latest-moved>.md`
- Example: `CHANGELOG-v0.1.0-to-v0.1.5.md`
- Contains the moved version blocks, plus a one-line header documenting source/date.

**Source retains** in its `## Archive` section:
```markdown
- [CHANGELOG-v0.1.0-to-v0.1.5.md](archive/CHANGELOG-v0.1.0-to-v0.1.5.md) — versions v0.1.0 through v0.1.5; archived 2026-05-28 (~8,200 tokens, 12 entries)
```

**Refusal:** if `[Unreleased]` + headers + protected sections already exceed `budget`, refuse with exit 2 and a message: "`[Unreleased]` alone is X tokens, over budget Y. Trim Unreleased before archiving."

### DEVLOG

**Protected (never archived):**
- File header (title, frontmatter, Related Documents, "For AI Agents" note).
- The `## Daily Log` heading and any "For AI Agents" guidance under it.
- The `## Archive` section.

**Archivable:**
- Daily Log entries (`### YYYY-MM-DD: title` blocks), oldest first, after computing a **fit-the-budget retention set**:
  1. Walk entries newest-first.
  2. Sum cumulative tokens (chars/4 heuristic, matching Spec 1's canonical).
  3. Stop adding once cumulative > `keep_fraction * budget`.
  4. All remaining (older) entries go to the archive.

**Archive file:** `logs/archive/DEVLOG-<earliest-date>-to-<latest-date>.md`
- Example: `DEVLOG-2025-10-15-to-2025-12-20.md`
- Date range derived from the entry headers (`### YYYY-MM-DD: ...`).

**Source retains** an Archive section entry in the same format as CHANGELOG.

**Edge case:** if the single newest entry exceeds `keep_fraction * budget`, it stays (we never archive the newest entry) and a warning suggests trimming.

### STATE and ADRs

- **STATE.md** never archives (snapshot semantics).
- **`logs/adr/*.md`** never archives (decisions are forever).
- `lfg archive --state` and `--adr` flags are accepted but reject with exit 2.

## Combined-budget overflow

After per-file archival, if `tokens(CHANGELOG) + tokens(DEVLOG) > combined_budget` (default 25,000), archive **additional** DEVLOG entries (keep_fraction → 0.7 → 0.6 → … in 0.05 decrements) until combined fits under `keep_fraction * combined_budget`. Don't touch CHANGELOG further — its content is more structurally meaningful (versioned facts > daily narrative).

## Testing

All tests live under `product/tests/`:

- **`test_archive_changelog_protects_unreleased`** — seed CHANGELOG with `[Unreleased]` + 5 version blocks pushing over budget; assert plan moves only released blocks.
- **`test_archive_devlog_fits_budget`** — seed 20 dated entries totaling 25k tokens; assert plan keeps newest entries summing ≤ `keep_fraction * 15000`.
- **`test_archive_writes_archive_section_link`** — after `apply()`, source has a new `## Archive` line with a working relative link to the new archive file.
- **`test_archive_dry_run_writes_nothing`** — `--dry-run` produces output, file mtimes unchanged.
- **`test_archive_force_skips_prompt`** — non-interactive flag works without stdin.
- **`test_archive_refuses_when_unreleased_oversize`** — `[Unreleased]` alone > budget → exit 2, no writes, clear message.
- **`test_archive_combined_overage`** — both files individually fit, combined > 25k → algorithm archives more DEVLOG.
- **`test_archive_single_newest_devlog_entry_oversize`** — newest entry alone > 80% budget → it stays, warning emitted.
- **`test_archive_state_and_adr_rejected`** — `--state` / `--adr` → exit 2 with the documented message.
- **`test_archive_dogfood`** — runs `lfg archive --dry-run` against this repo's actual logs; asserts it builds a non-empty, reasonable plan that respects `[Unreleased]` and doesn't list ADRs.
- **`test_archive_idempotent`** — apply once, then re-run; second run is a no-op (source already under budget).

## Self-application (the dogfood case)

This repo's `logs/CHANGELOG.md` is the first real-world target. Spec 3's implementation plan will include a step to run `lfg archive --dry-run` against the repo, capture the plan, and (with user approval) apply it. The plan will move pre-Spec-2 version blocks to `logs/archive/CHANGELOG-v<earliest>-to-v<latest>.md`, leaving Spec 1's CHANGELOG entries (which are the "Unreleased" → about-to-be-released history) in place.

## Risks accepted

- **A user with non-Keep-a-Changelog format** (e.g., no `[Unreleased]` section) gets a clear refusal rather than silent destruction. Documented in CONTRIBUTING / how-to.
- **Token estimates are chars/4 heuristic** (matches Spec 1 canonical). Real tokenization would be slightly different, but the budget is itself a soft target.
- **The `keep_fraction = 0.8` default** may feel aggressive or conservative depending on usage. Single configurable knob; users tune in their profile.
- **The combined-budget loop** (decrementing `keep_fraction` until it fits) could in pathological cases archive almost all of DEVLOG. A floor (`keep_fraction >= 0.3`) prevents the source from collapsing to a single entry; if the floor is reached, refuse with a message.

## File inventory (touched)

- Create: `product/scripts/archive.py`
- Create: `product/tests/test_archive.py` (consolidated test file for all the cases above)
- Modify: `product/scripts/lfg.py` (add `cmd_archive` + subparser)
- Modify: `product/scripts/lint-logs.py` (one-line hint update)
- Modify: `product/scripts/validate-log-files.sh` + `.ps1` (one-line hint update)
- Modify: `product/rules/log-file-maintenance.md` (shrink ARCHIVAL section; regen AGENTS.md after)
- Modify: `product/profiles/*.yml` (reduce `archival:` to one key)
- Modify: `product/docs/log_file_how_to.md` (document the deterministic archival workflow)
- Regenerate: `product/AGENTS.md` (because the rule changed)
