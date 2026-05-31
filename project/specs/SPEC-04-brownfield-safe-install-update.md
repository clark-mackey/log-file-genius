# Spec 4: Brownfield-Safe Install & Update

**Status:** Approved (design); planning next.
**Target release:** v0.4.0
**Author:** Claude Code (controller)
**Approved by:** Clark Mackey, 2026-05-31
**Revisions:** 2026-05-31 — applied code-owl plan-review mitigations (10 blockers/risks + 4 nits + 1 factual correction).

---

## Motivation

The first real brownfield migration test (FFAI, v0.2.0 → v0.3.0) surfaced
five concrete defects in the install/update flow. One is a data-loss risk;
the others range from functional bugs to first-impression friction for
upgrading users.

| # | Issue | Severity | Source |
|---|---|---|---|
| 1 | `install.{sh,ps1}` silently overwrites the user's existing root `AGENTS.md` (e.g., Codex users). `update.{sh,ps1}` prompts but a "y" answer still loses user content (no merge — full replacement). Either path = data loss. | **P0 — data loss** | FFAI migration |
| 2 | Validator's version-check message prints the comparison backwards ("update available: v0.2.0 (you have v0.3.0)") | P1 — bug | FFAI migration |
| 3 | Installer creates a root `templates/` dir that duplicates content many users already have under their own template folders (e.g., `_templates/`) | P1 — friction | FFAI migration |
| 4 | v0.3.0's stricter STATE.md rules flag pre-existing content on first run after upgrade; no tool to bring it into compliance | P2 — UX | FFAI migration |
| 5 | Once a user manually restores their AGENTS.md (workaround for #1), future fragment updates no longer propagate — no merge mechanism | P0 — corollary of #1 | FFAI migration |

#1 and #5 are the same defect viewed from two angles: there is no way to
co-exist with a user-owned AGENTS.md.

---

## Goals

- **No more clobbering user-owned AGENTS.md.** Updates must be safe on every project.
- **Single canonical AGENTS.md.** Don't fragment the world into AGENTS.md +
  AGENTS-lfg.md + per-tool variants; agent-agnostic single-file UX from Spec 2 must hold.
- **Deterministic, previewable migrations.** Same ethos as `lfg archive`:
  brownfield upgrades get a `--dry-run` + apply CLI verb, not silent rewrites.
- **Bugs out, polish in.** Ship the version-check direction fix, kill the
  redundant root `templates/`, and add a brownfield STATE migration helper.

## Non-goals

- Append-marker pattern for `.logfile-config.yml` (different problem — profile
  schema, not generated content; revisit if it bites in the wild).
- Reworking the validator UX beyond the version-check fix.
- Per-tool AGENTS.md variants (still one canonical file).

---

## Design

### 1. Managed-block AGENTS.md (P0 — fixes #1 and #5)

**Marker format (regex-tightened per code-owl):**

```
<!-- LFG:BEGIN v0.4.0 — DO NOT EDIT BETWEEN THESE MARKERS -->
<generated content from product/rules/ fragments>
<!-- LFG:END -->
```

- Markers are HTML comments — invisible in rendered markdown.
- **BEGIN-marker regex (strict):** `<!--\s*LFG:BEGIN\s+v(\S+)\s*(?:—[^>]*)?-->`
  — the literal `v<version>` is required. A user comment starting `<!-- LFG:BEGIN
  something-else -->` (no `v`) does NOT match and is left alone.
- **END-marker:** literal `<!-- LFG:END -->`.
- **Forward-compatibility:** if the captured version on a BEGIN marker
  parses to a value *greater than* the running LFG version, the merge
  REFUSES with a clear error ("AGENTS.md was managed by a newer LFG. Upgrade
  the submodule or pass `--force-downgrade`."). Prevents v0.4 from
  silently overwriting a future v0.5 block.

**Encoding & atomicity policy (applies to merge + migrate-state + everything that writes a tracked file):**

- **Read** with `encoding="utf-8-sig"` (transparently strips UTF-8 BOM if present).
- **Normalize line endings on read:** `content.replace("\r\n", "\n").replace("\r", "\n")`.
  Marker regexes operate on normalized content only.
- **Write LF, no BOM:** Python writes `open(path, "w", encoding="utf-8", newline="\n")`.
  PowerShell writes via `[IO.File]::WriteAllText(path, content, UTF8Encoding($false))`
  (same pattern Spec 2 established for installer/updater).
- **Atomic write:** write to `<path>.lfg-tmp`, fsync, then `os.replace(tmp, path)`.
  Crash mid-write leaves the original intact. `migrate_state.apply` writes
  both STATE.md and DEVLOG.md to tmp paths, then performs both renames; if
  the DEVLOG rename fails, the STATE rename is rolled back (rename `<state>.lfg-tmp`
  away is not needed since we replace at the end — but we MUST stage DEVLOG
  first so a STATE write doesn't land without its snapshot).

**Generator changes (`product/scripts/generator.py`):**

- Introduce a private primitive `render_canonical_body() → str` that emits
  the canonical content (frontmatter + intro + section index + all fragment
  bodies) — i.e., exactly what `product/AGENTS.md` contains today minus the
  enclosing markers.
- `render_full() → str` — alias for `render_canonical_body()`. Used to emit
  the in-repo `product/AGENTS.md` (no markers — that file *is* fully LFG-owned).
- `render_block() → str` — wraps `render_canonical_body()` in BEGIN/END markers.
  Used by the install/update merge.
- Unit test asserts `render_block().strip_markers() == render_full()` (concrete
  string equality between the body of the block and the full output).

**New module `product/scripts/agents_merge.py`:**

```python
import re

LFG_BEGIN_RE  = re.compile(r"<!--\s*LFG:BEGIN\s+v(?P<ver>\S+)\s*(?:—[^>]*)?-->")
LFG_END_LIT   = "<!-- LFG:END -->"

def merge_into_existing(existing: str | None, block: str, running_version: str,
                        allow_wrap: bool = True) -> str:
    """
    Return the new AGENTS.md content.

    - existing is None or "" → return block (fresh install).
    - existing has BEGIN+END markers:
        - If captured version > running_version → raise ForwardVersionError.
        - Else replace the interior with the running block; keep surrounding content.
    - existing has no markers + looks_like_lfg(content) and allow_wrap →
        wrap the entire existing content in markers, then replace interior
        with block. Handles users whose pristine AGENTS.md was clobbered
        in 0.2→0.3 and manually restored.
    - existing has no markers + doesn't look like LFG (or allow_wrap=False) →
        prepend block at top, keep user content below.

    `--no-wrap` on the CLI sets allow_wrap=False (escape hatch for the rare
    false-positive case where user content happens to look LFG-ish).
    """
    ...

def looks_like_lfg(content: str) -> bool:
    """
    Fingerprint check, re-derived against v0.1/v0.2/v0.3 AGENTS.md so it
    catches historical brownfields.

    TRUE if EITHER of these strong signals is present (single signal suffices,
    because each is distinctive enough):

      - YAML frontmatter `doc: AGENTS` at the top of file (stable since
        Spec 2; the doc-key value never appears in user content).
      - HTML comment `<!-- Generated by Log File Genius` anywhere
        (legacy footer present in v0.1 / v0.2 AGENTS.md — we'll ensure
        v0.4's render_block emits this inside the BEGIN comment line so
        future versions also match here).

    OR ≥2 of these supporting signals appear together:

      - 'Log File Genius' in the first 200 chars (doc header)
      - '🔴 BEFORE EVERY COMMIT'  (commit checklist heading, stable across versions)
      - 'CHANGELOG.md' AND 'DEVLOG.md' AND 'STATE.md' all mentioned (the 5-doc system signature)
      - '⛔ MANDATORY RULE'  (commit rule heading, stable across versions)

    The strong-signals list is what catches pre-Spec-2 brownfields whose
    AGENTS.md predates LFG_SUBAGENT_PRIME / SUBAGENT CONTRACT.

    Implementation note: re-verify the chosen signal set against
    `git show v0.1.0:product/AGENTS.md`, `git show v0.2.0:product/AGENTS.md`,
    and current HEAD before locking the heuristic in code. The implementer
    MUST diff all three and confirm both strong-signals match in all three.
    """
    ...
```

**Installer + updater changes:**

- `install.{sh,ps1}`: silent-overwrite of AGENTS.md is replaced by a call
  to a new Python entrypoint `python product/scripts/lfg.py merge-agents-md
  --to <project-root>/AGENTS.md [--no-wrap]`. The entrypoint owns read,
  merge, atomic write.
- `update.{sh,ps1}`: the existing `prompt_update` call for AGENTS.md
  (currently at `update.sh:245`) is **replaced**, not augmented, by the
  same merge entrypoint. Rationale: a "y" answer at the prompt today
  causes content loss (full overwrite); the merge is strictly safer.
  - **Idempotency short-circuit:** the entrypoint computes the new
    content first and, if it matches the existing file byte-for-byte,
    skips the write entirely (no prompt, no churn, clean re-run).
- New CLI flag `--no-wrap` on the merge entrypoint disables the
  "wrap existing LFG-like content" path; the block is always prepended.
- `--force-downgrade` on the merge entrypoint allows a v0.4 install to
  replace a v0.5+-managed block (rare; for downgrades).

### 2. `lfg migrate-state` CLI verb (P2 — fixes #4)

Mirrors `archive.py`'s plan/apply pattern from Spec 3:

**New module `product/scripts/migrate_state.py`:**

- `parse_state(content) → list[Section]` — tokenizes by `##` headings, captures
  token counts per section.
- `MigratePlan` dataclass: `keep`, `archive_to_devlog`, `drop`, `target_tokens`.
- `build_plan(state, config) → MigratePlan`:
  - **keep:** Current Context, Last Session, In Progress (the v0.3.0 spec)
    if individually under budget. If a kept section is itself over budget,
    truncate to the most-recent content and note the truncation.
  - **archive_to_devlog:** any section not in the v0.3.0 spec but containing
    user content worth preserving. Bundled into a single one-time DEVLOG
    entry `### YYYY-MM-DD: STATE snapshot pre-v0.4.0 migration` with the
    raw sections embedded.
  - **drop:** known v0.2.0-only section types with no semantic value
    (empty placeholders, etc.).
- `apply(plan, state_path, devlog_path)` — writes new STATE.md, appends
  DEVLOG entry. Uses the atomic-write + encoding policy from §1. Idempotent
  via **two guards** (either trips refusal):
  1. STATE.md already passes v0.3.0 validation cleanly.
  2. DEVLOG.md already contains a heading matching
     `^### \d{4}-\d{2}-\d{2}: STATE snapshot pre-v0.4.0 migration$`.
  The second guard handles the case where a user runs migrate, then edits
  STATE back into non-compliance — re-running migrate would otherwise
  re-archive sections that no longer exist. Hard one-shot.
- **DEVLOG insertion position:** the snapshot entry is appended at the
  END of the `## Daily Log` section (oldest position), NOT prepended.
  Rationale: DEVLOG is newest-first; prepending displaces today's actual
  entry. The snapshot is historical context, not today's work.
- **Validator integration prerequisite:** §1 of this spec relies on
  `lfg validate` returning a distinct exit code (or `--file STATE.md`
  flag) so `update.{sh,ps1}` can detect STATE-specific failures without
  false-positive on unrelated issues. Confirm this granularity exists in
  current `lfg.py`; if not, this spec adds it as a sub-task (small —
  `lfg validate --file <name>` returning non-zero only for that file).

**CLI surface:**

```
lfg migrate-state --dry-run     # preview plan
lfg migrate-state               # interactive confirm + apply
lfg migrate-state --force       # apply without prompt
```

**Update integration:** `update.{sh,ps1}` runs `lfg validate` post-update.
If STATE.md fails validation specifically (not other files), it prints a
single advisory line: `STATE.md needs migration to v0.4.0 spec. Preview with: lfg migrate-state --dry-run`.
No prompt, no auto-run — keeps update.sh non-interactive.

### 3. Stop installing root `templates/` (P1 — fixes #3)

- **install.{sh,ps1}:** delete the block that copies `product/templates/*`
  to project-root `templates/`. Templates live in
  `.log-file-genius/product/templates/` only.
- **update.{sh,ps1}:** detect existing root `templates/` whose file
  contents match (by SHA-256) any LFG-shipped template. Source of truth:
  a new `product/scripts/known_template_hashes.json`, checked into the
  repo and updated each release with the SHA-256 of every file under
  `product/templates/` for the current AND most-recent prior version.
  Generated by a helper (`python product/scripts/update_template_hashes.py`)
  run by release tooling; CI verifies the JSON is up to date for the
  current version (so contributors can't forget to regen).
  - If a root-templates file's hash is in the JSON → LFG-installed, move
    to `.log-file-genius/.backups/templates-<unixtime>/`.
  - If hash not in the JSON → user-authored (or user-modified), leave
    untouched.
  - Print a clear "moved N LFG-installed templates to backups" message,
    or "kept root templates/ (contents don't match LFG-shipped versions)".
- **Docs:** README, INSTALL, log-file-how-to all updated to point at
  `.log-file-genius/product/templates/` as the canonical reference path.

### 4. Validator version-check direction fix (P1 — fixes #2)

- Locate the comparison (likely `product/scripts/check-version.py` or
  inline in `validate-log-files.{sh,ps1}`).
- Flip the comparator so that "you have v0.4.0, latest is v0.3.0" reports
  "you are ahead of latest" (not "update available"), and the converse
  reports "update available."
- Add `test_check_version.py` with explicit cases for ahead / behind / equal
  / dev-snapshot strings, pinning the direction so it can't regress.

### 5. Documentation

- `product/docs/log_file_how_to.md` — new short "Updating Log File Genius"
  section explaining the managed-block AGENTS.md, the `lfg migrate-state`
  verb, and where templates live.
- `README.md` + `INSTALL.md` — point upgraders at the new migration verb;
  remove any mention of root `templates/`.
- `CONTRIBUTING.md` — note for contributors that AGENTS.md content is
  emitted both ways (`render_full` for `product/AGENTS.md`, `render_block`
  for installed targets); changes to fragments must regen both.

---

## Test plan

Following Spec 3's pattern (one focused test module per component):

| Module | Coverage |
|---|---|
| `test_agents_merge.py` | markers found / markers missing + LFG fingerprint / markers missing + user content / idempotency (re-run is byte-identical) / no-op on fresh project / `looks_like_lfg` true & false cases / **fixtures from `git show v0.1.0:product/AGENTS.md`, `git show v0.2.0:product/AGENTS.md`, current HEAD** — assert each fingerprints as LFG / **CRLF + UTF-8 BOM input** simulating Notepad-edited file — assert markers still detected, output normalized to LF no-BOM / **forward-version refusal** — existing marker captures `v99.0.0`, merge raises ForwardVersionError / `--no-wrap` flag bypasses auto-wrap path / `--force-downgrade` overrides forward-version refusal / **atomicity** — simulate IOError mid-write, assert original file intact |
| `test_generator_round_trip.py` | (new) `render_block().split_markers().body == render_full()` byte-for-byte; `render_canonical_body()` primitive returns identical content in both code paths |
| `test_migrate_state.py` | parse / build_plan keeps current sections / archives over-budget / drops known-empty / **refuses if STATE compliant** / **refuses if DEVLOG already has snapshot entry** (second guard) / idempotency / DEVLOG snapshot entry round-trips through validator / snapshot inserted at end of Daily Log (not top) / atomic write — DEVLOG failure rolls back STATE |
| `test_lfg_migrate_state.py` | CLI dry-run prints plan but writes nothing / `--force` skips prompt / refusal on compliant STATE / refusal on already-migrated state (second guard hit) |
| `test_install_smoke.{sh,ps1}` | (updated) assert NO root `templates/` created / assert AGENTS.md merge preserves user content above markers / assert idempotent on repeat install / assert UTF-8 no-BOM + LF in written AGENTS.md (PowerShell encoding regression) |
| `test_update_smoke.{sh,ps1}` | (updated) clobbered-then-restored AGENTS.md → update wraps it / user-owned AGENTS.md → update prepends block above / marker-wrapped AGENTS.md → update only rewrites interior / Notepad-style CRLF+BOM AGENTS.md → markers detected, output normalized / repeated update is byte-identical no-op (no prompt) |
| `test_check_version.py` | (new) comparator direction pinned for ahead / behind / equal / dev-snapshot / pre-release suffix (`-rc.1`) / build metadata (`+local.abc123`) |
| `test_known_template_hashes.py` | (new) JSON manifest contains a hash for every file in `product/templates/` at HEAD; CI gate would catch a forgotten regen |

Existing 80-test suite must continue to pass.

---

## Release packaging

**v0.4.0** (not v0.3.1). Rationale:
- `lfg migrate-state` is a real new CLI verb (feature, not just bugfix).
- The AGENTS.md merge change introduces a marker format that becomes a
  documented part of the distributable's contract — worth a minor bump.
- Lets the release notes tell a coherent "brownfield safety" story
  instead of mixing a hotfix and a feature.

CHANGELOG categories:
- **Added:** `lfg migrate-state` subcommand; `lfg merge-agents-md` entrypoint; managed-block format (BEGIN/END markers with version capture and forward-compat refusal) for installed AGENTS.md; `--no-wrap` and `--force-downgrade` flags on merge entrypoint; `known_template_hashes.json` shipped manifest; `lfg validate --file <name>` granular exit codes (if not already present).
- **Changed:** `install.{sh,ps1}` and `update.{sh,ps1}` no longer overwrite existing AGENTS.md (merge instead, with idempotency short-circuit); `update.{sh,ps1}` `prompt_update` for AGENTS.md REPLACED by merge call; templates no longer copied to project root — live in `.log-file-genius/product/templates/` only; root `templates/` from prior versions auto-moved to backups on update when SHA-256 matches shipped templates; generator refactored into `render_canonical_body()` primitive + `render_full()` / `render_block()` wrappers; all file writes use atomic tmp+rename pattern and UTF-8 LF no-BOM policy.
- **Fixed:** Version-check comparison direction in validators (handles ahead/behind/equal/pre-release/build-metadata).

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Fingerprint false-negative — a heavily customized LFG-generated AGENTS.md isn't detected, so v0.4.0 prepends a fresh block above the user's stale LFG content (duplication). | Fingerprint redesigned against v0.1/v0.2/v0.3 fixtures (see §1 — `looks_like_lfg`). Strong signals (frontmatter `doc: AGENTS`, generation footer) match all three historical versions in a unit test. Plus: documented cleanup story; user can manually wrap stale content in markers to dedupe. |
| Fingerprint false-positive — a user-authored AGENTS.md happens to share content with LFG (e.g., a code example referencing LFG) and gets wrapped wholesale. | Strong-signals require LFG-distinctive markers that don't appear in idle user content. `--no-wrap` flag on the merge entrypoint (and `merge-agents-md` CLI) bypasses auto-wrap entirely for the rare false-positive. |
| Marker syntax conflict — a user comment like `<!-- LFG:BEGIN something else -->` exists in user content. | BEGIN regex requires literal `v<version>` immediately after `LFG:BEGIN`. A comment without `v` won't match — left alone. |
| Forward-version overwrite — a v0.4 install runs against an AGENTS.md managed by a future v0.5+ LFG that changed the block schema. | Merge captures the version from the BEGIN marker; if > running version, raises `ForwardVersionError` and refuses to write. User overrides with `--force-downgrade`. |
| Crash mid-write — script crashes during AGENTS.md or STATE.md rewrite. | Atomic write: tmp file + fsync + `os.replace`. Original file intact on any crash. `migrate_state.apply` stages both DEVLOG and STATE writes before any rename. |
| Encoding drift — CRLF/BOM AGENTS.md (Windows Notepad edits) causes marker mismatch or PowerShell writes UTF-16 LE BOM by default. | Read with `utf-8-sig`, normalize line endings on read; Python writes UTF-8 LF no-BOM; PowerShell uses `[IO.File]::WriteAllText` with `UTF8Encoding($false)`. Smoke tests include a CRLF+BOM input fixture. |
| `lfg migrate-state` mangles a user's painstakingly-curated STATE.md, OR re-runs after user edits over-archive. | `--dry-run` default story; archives over-budget content to DEVLOG (lossless) rather than dropping; **two idempotency guards** (already-compliant STATE OR existing snapshot DEVLOG entry) make the verb strictly one-shot. |
| Root `templates/` cleanup misidentifies user templates as LFG-distributed. | SHA-256 match against shipped `known_template_hashes.json` (committed, CI-gated). Hash mismatch → leave untouched. Manifest covers current + most-recent prior version. |
| Marker format becomes load-bearing for downstream tools and we can't change it later. | Markers documented in CONTRIBUTING; version token inside the BEGIN marker gives us forward-compat semantics (future LFG can read the version and decide); strict regex (`v<version>` required) makes it impossible to accidentally match unrelated comments. |

---

## Dogfood plan

Per Spec 1/2/3 pattern. Two dogfood scenarios before tagging v0.4.0:

1. **Brownfield simulation (the path users actually take):** in a fresh
   tmp dir, install LFG at tag `v0.2.0`, generate the v0.2.0 AGENTS.md +
   STATE.md, then update to HEAD. Confirm:
   - The v0.2.0 AGENTS.md (no markers, doesn't match Spec-2-era
     fingerprints) gets correctly wrapped via `looks_like_lfg`'s
     strong-signals path, content preserved.
   - `lfg migrate-state --dry-run` produces a sensible plan; `apply`
     succeeds; second run refuses (guard 2).
   - No root `templates/` after update.
2. **This repo's own state:** run `lfg migrate-state --dry-run` against
   this repo's STATE.md (likely a no-op since we already conform). If
   it does fire, accept the plan or note why we skip. AGENTS.md merge
   doesn't apply here — this repo's `product/AGENTS.md` is `render_full`
   output by definition and never carries markers.

Both dogfoods must pass; the full 80+test suite + bash/PowerShell smoke
must remain green.
