# Spec 5: First-Class Incident Reports

**Status:** Approved (design); planning next.
**Target release:** v0.5.0
**Author:** Claude Code (controller)
**Approved by:** Clark Mackey, 2026-06-01

---

## Motivation

LFG's incident model today is the lightweight inline DEVLOG entry
(`### YYYY-MM-DD: 🚨 INCIDENT - …`), the deliberate replacement for the
rejected Epic 17 (standalone incident-report documents with SEV levels,
hazard statements, 210-line template). But:

1. The installer still `mkdir`s an **orphaned** `logs/incidents/` directory
   that nothing in the current model uses — a vestige of the rejected Epic 17.
2. Real users (e.g. the `schema writer 2` project — 5 incident reports
   spanning Nov 2025 → May 2026) **do** keep standalone incident reports and
   find them valuable for big incidents.

Rather than delete the orphan, this spec **re-scopes Epic 17 in a lighter
form**: standalone incident reports become first-class, modeled exactly on
ADRs — a lightweight DEVLOG `🚨 INCIDENT` entry (still the default) that links
out to a detailed standalone report in `logs/incidents/` when the incident
warrants it. Detail loaded on-demand; the log stays budget-friendly.

This was validated against the `schema writer 2` incident files before
design lock — see "Compatibility (validated against real data)" below.

## Goals

- Standalone incident reports as a first-class, ADR-parallel artifact.
- The inline `🚨 INCIDENT` DEVLOG entry remains the **default**; standalone is
  the *escalation* for incidents the rubric flags as worth detailed analysis.
- **Backward-compatible:** anyone with pre-existing date-prefixed incident
  reports can run `lfg incidents index` and get a navigable README with **zero
  edits to their existing files**.
- Un-orphan the `logs/incidents/` directory the installer already creates.

## Non-goals

- `lfg incidents new` scaffolding verb (YAGNI — index-only chosen).
- Severity in filenames (re-classification would force renames).
- SEV/hazard-statement/postmortem heaviness (that was the rejected Epic 17).
- Incident reports joining the full 5-doc bidirectional navigation matrix
  (they link to DEVLOG and are linked from it; that's enough — same as how
  individual ADRs aren't in every other doc's frontmatter).
- Token-budgeting or format-linting `logs/incidents/` (on-demand, like ADRs).

---

## Compatibility (validated against real data)

Prototyped the tolerant parser against the 5 real incident files in
`C:\Users\clark\Code\schema writer 2\logs\incidents` (created across multiple
prior versions). All 5 parsed into correct index rows with no reformatting.
Findings that shape the parser:

| Field | Real-world variance observed | Parser rule |
|---|---|---|
| **Date** | Header dates are human-formatted (`November 19, 2025`) and inconsistently labeled (`**Date:**` vs `**Date Discovered:**`). Filenames are uniformly `YYYY-MM-DD-slug.md`. | **Filename `YYYY-MM-DD` prefix is authoritative.** Fall back to header `Date`/`Date Discovered` only if the filename has no date prefix. |
| **Title** | All use `# Incident Report: <title>` (not `# Incident:`). | Take the first `# ` heading; strip a leading `Incident Report:` or `Incident:` label. |
| **Severity** | Word-based (`Medium`, `High`), not `SEV-N`. | Free-text; display as-is. |
| **Status** | Free-text, sometimes long with em-dashes/parentheticals (`Open — origin narrowed to … ; fix not yet implemented`). | Free-text; truncate to first clause (split on ` — `, `;`, ` (`) then cap length for the table cell. |
| **Extra fields** | `Incident ID:`, `Reporter:`, `Responder:`, `Affected Page:`, `Duration of Silent Failure:`. | Ignored for indexing; preserved in the file. |
| **Encoding** | Mixed; may carry BOM / trailing hard-break spaces / em-dashes. | Read `utf-8-sig`; strip trailing whitespace per line; write index UTF-8/LF. |

---

## Design

### 1. Lightweight incident template — `product/templates/INCIDENT_template.md` (new)

Mirrors `ADR_template.md`'s frontmatter pattern; uses the prevalent real-world
heading convention so new reports stay visually consistent with existing ones:

```markdown
---
doc: INCIDENT
related:
  changelog: ../CHANGELOG.md
  devlog: ../DEVLOG.md
  state: ../STATE.md
---

# Incident Report: [Short title]

**Date:** YYYY-MM-DD
**Severity:** [Low | Medium | High | Critical]
**Status:** [Open | Mitigated | Resolved]
**Owner:** [Name or AI agent]
**Systems:** [Affected components]

---

## Related Documents

📊 **[CHANGELOG](../CHANGELOG.md)** · 📖 **[DEVLOG](../DEVLOG.md)** · 📈 **[STATE](../STATE.md)**

---

## Summary
One line: what failed and why it matters.

## Timeline
- HH:MM — detected … HH:MM — mitigated … HH:MM — resolved

## Root Cause
Why it happened.

## Resolution
What fixed it (or current mitigation if still open).

## Prevention
How recurrence is prevented.

## Detection
How this is caught earlier next time.

## Files
`path/a`, `path/b` → DEVLOG YYYY-MM-DD
```

Severity vocabulary is words (Low/Medium/High/Critical) to match observed
usage; the parser does not enforce a vocabulary.

### 2. `incidents.py` module (new, stdlib, pure parse + render)

```python
@dataclass
class IncidentMeta:
    path: Path
    date: str          # YYYY-MM-DD (filename-authoritative)
    title: str         # prefix-stripped
    severity: str      # free-text or "—"
    status: str        # free-text or "—" (full, untruncated)

def parse_incident(path: Path) -> IncidentMeta: ...
def build_index(incidents_dir: Path) -> str:    # returns README.md content
    ...
```

- `parse_incident`: read `utf-8-sig`; **date** from filename `YYYY-MM-DD`
  prefix (authoritative). If the filename has no date prefix, fall back to the
  header `**Date:**`/`**Date Discovered:**` value and **parse common human
  formats to ISO** (`November 19, 2025` → `2025-11-19`); if it can't be parsed
  to ISO, mark the record **undated** (sort key sorts it last; display the raw
  string in the cell). Never mix a human-formatted string into the ISO sort
  key. **title** from first `# ` heading minus `Incident Report:`/`Incident:`;
  **if there's no `# ` heading, fall back to the filename slug** (date prefix
  stripped, hyphens → spaces, title-cased). severity/status via tolerant
  `^\*\*<label>:\*\*\s*(.+?)\s*$` regex; missing → `"—"`.
- `build_index`: glob `*.md`, **skip `README.md` and `TEMPLATE.md`**
  (case-insensitive), sort **newest-first by the tuple `(iso_date, filename)`**
  — Python's stable sort makes duplicate dates deterministic; undated records
  sort last under a sentinel. Render a markdown table:
  `| Date | Severity | Status | Incident |` where Incident is a
  `[title](./file.md)` link and Status is truncated for the cell (full text
  stays in the file). Include a short header + a generated-marker comment
  (`<!-- LFG:INCIDENTS-INDEX generated by lfg incidents-index -->`) so re-runs
  are diff-stable and the writer can detect its own prior output.
- The `—` em-dash for missing fields only ever lands in the README **file**
  (written UTF-8/LF), never in `print()`/stdout (which stays ASCII for
  Windows cp1252 safety).
- Index README carries the same `doc:`/related frontmatter style for
  navigation consistency (links to ../CHANGELOG, ../DEVLOG, ../STATE).
- Empty dir → an index with a "No incidents recorded yet." placeholder.

### 3. `lfg incidents-index` subcommand (lfg.py)

```
lfg incidents-index [--dir <path>]
```

- **Flat verb**, not a nested `incidents` subcommand-group. lfg.py dispatches
  via a flat `handlers` dict keyed on `args.command` (one `add_parser` per
  verb); a nested group would need a second `add_subparsers` + re-dispatch
  branch that no other verb uses, to support exactly one action. The
  `incidents new` scaffold is already a non-goal, so YAGNI → ship
  `cmd_incidents_index` as one flat handler matching every existing verb. If a
  second incidents action ever lands, refactor to a group then.
- Resolves the incidents dir from `.logfile-config.yml` → `paths.incidents_dir`
  (fallback `logs/incidents`); `--dir` overrides. (The installer writes
  `incidents_dir` into the config — see §4 — mirroring the existing `adr_dir`
  key for consistency.)
- Calls `incidents.build_index`, writes `README.md` via atomic UTF-8/LF write
  (reuse `agents_merge.atomic_write`).
- **README-clobber safety (reuse the Spec 4 `.bak` pattern):** if an existing
  `README.md` is present and does **not** contain the
  `<!-- LFG:INCIDENTS-INDEX … -->` generated-marker (i.e. it's a user's
  hand-written README, not our prior output), back it up to the first-free
  `README.md.bak` / `README.md.bak.2` before overwriting, and print the backup
  path. This honors Spec 4's "never lose user content" thesis — there is no
  precedent of LFG overwriting a user file in a logs subdir, so we must not
  start silently. A README that already carries the marker is overwritten in
  place (it's our own output).
- Idempotency short-circuit: if regenerated README == existing bytes, report
  "already up to date", write nothing (no backup).
- Refuses gracefully (exit 0, message) if the incidents dir doesn't exist.
- ASCII-only stdout (Windows cp1252-safe), like cmd_archive/cmd_prime.

### 4. Installer (`install.{sh,ps1}`)

- Keep the `logs/incidents/` directory creation — now **intentional**.
- Copy `product/templates/INCIDENT_template.md` → `logs/incidents/TEMPLATE.md`
  (mirrors `logs/adr/TEMPLATE.md`), via the existing static template-mapping
  block.
- **Seed `logs/incidents/README.md` as a static empty-state placeholder**
  ("No incidents recorded yet." + the generated-marker), written the same way
  the Claude template is rendered (no-BOM `[IO.File]::WriteAllText` on
  PowerShell; plain redirect on bash). **Do NOT run `lfg incidents-index`
  during install** — install.sh's AGENTS.md path is deliberately python-
  optional (degrades gracefully when python is absent) and install.ps1 has no
  python guard; seeding via the CLI would add a python dependency to a
  python-optional path. The placeholder carries the marker, so the first real
  `lfg incidents-index` run overwrites it cleanly (no `.bak`).
- Add `incidents_dir: logs/incidents/` to both installers' `.logfile-config.yml`
  heredocs, mirroring the existing `adr_dir` key, so `--dir`-less CLI runs
  resolve the path from config.

### 5. Rule fragment + DEVLOG template (token-tight)

- `product/rules/log-file-maintenance.md`: in the existing incident section,
  add a SHORT escalation note: inline `🚨 INCIDENT` is the default; when the
  rubric flags a major incident (security exposure, data loss, repeated/silent
  failure, regression), ALSO write a standalone
  `logs/incidents/YYYY-MM-DD-slug.md` from the template, link it from the
  DEVLOG entry (`→ logs/incidents/YYYY-MM-DD-slug.md`), and run
  `lfg incidents index`. Must stay within the AGENTS.md token budget
  (see Risks).
- `product/templates/DEVLOG_template.md`: one line noting an incident entry MAY
  link to a standalone report.
- Regenerate `product/AGENTS.md` via `lfg generate`.

### 6. Documentation

- `product/docs/log_file_how_to.md`: add `logs/incidents/` to the File
  Structure tree; new "Incident Reports" subsection (ADR-parallel: when to
  escalate, naming, the index command, that existing reports are picked up
  automatically).
- `README.md` + `INSTALL.md`: add `lfg incidents index` to the CLI table;
  note `logs/incidents/` (+ TEMPLATE + README) in what-gets-installed.
- `CONTRIBUTING.md`: note the new template requires regenerating
  `known_template_hashes.json`.

### 7. EPIC-17 reconciliation (dev-only)

- `project/specs/EPIC-17-incident-reports-learning.md`: header status
  REJECTED → "RE-SCOPED → Spec 5 (lightweight first-class incident reports)".
- PRD epic list: update the Epic 17 line accordingly.

### 8. Release packaging

**v0.5.0** — new CLI verb (`lfg incidents index`) + new installed artifacts
(`logs/incidents/TEMPLATE.md`, `README.md`, the template). Refresh VERSION.json
checksums; regenerate `known_template_hashes.json` (now includes
`INCIDENT_template.md`) for the new version (manifest merges, preserves 0.3/0.4).

CHANGELOG categories:
- **Added:** `lfg incidents index`; `INCIDENT_template.md`; first-class
  incident reports (ADR-parallel); installer seeds `logs/incidents/`
  TEMPLATE + README.
- **Changed:** `logs/incidents/` is now an intentional managed location (was a
  vestigial empty dir); incident guidance in rules documents the escalation
  pattern.

---

## Test plan

| Module | Coverage |
|---|---|
| `test_incidents.py` | parse: filename-date authoritative; header-date fallback parsed to ISO (`November 19, 2025` → `2025-11-19`); unparseable header date → undated, sorts last; title prefix-stripping (`Incident Report:`, `Incident:`, none) + **no-heading → filename-slug fallback**; free-text severity/status; missing fields → "—"; status truncation; **fixtures mirroring the 5 real `schema writer 2` headers** (human dates, word severities, long em-dash statuses, extra fields) → assert correct rows; BOM + trailing-hard-break tolerance; build_index skips README/TEMPLATE, sorts newest-first by `(iso_date, filename)` with stable duplicate-date order, empty-dir placeholder; idempotency (re-render byte-identical); assert `—`/em-dash only in the written file (UTF-8/LF), never returned for stdout |
| `test_lfg_incidents.py` | CLI: `incidents-index` creates README; idempotent rerun reports up-to-date (no backup); `--dir` override; missing dir → graceful exit 0; ASCII stdout; **user-authored README (no marker) → backed up to README.md.bak before overwrite; marker-bearing README → overwritten in place, no backup** |
| `smoke_install.{sh,ps1}` | installer creates `logs/incidents/` + `TEMPLATE.md` + `README.md`; README has the empty-state placeholder; UTF-8 no-BOM on PowerShell |
| AGENTS.md | `lfg generate --check` clean after fragment edit; token budget not exceeded (or budget consciously bumped — see Risks) |
| `test_known_template_hashes.py` | manifest includes `INCIDENT_template.md` for current version; `--check` passes. **Note for the update task: regenerate the manifest BEFORE any `--match-dir` template cleanup runs**, so a freshly-installed `INCIDENT_template.md`/`TEMPLATE.md` is recognized as LFG-shipped (union-of-versions match) rather than misread as user-authored. |
| validators | confirm `lint-logs` / `lfg validate` do NOT touch `logs/incidents/` (no budgeting/format errors introduced) |

Existing suite (188) must stay green.

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| **AGENTS.md token budget** (gated 4,500; currently 3,980). The rule-fragment escalation note grows it. | Keep the addition to ~2-3 lines. If it exceeds budget, consciously bump `AGENTS_TOKEN_BUDGET` (documented precedent) rather than cramming. Measure in the task that edits the fragment. |
| **Validators accidentally lint `logs/incidents/`** → spurious errors on users' rich reports. | Confirm `lint-logs` only targets the three named files; add a test asserting incident files don't affect `lfg validate`. |
| **Parser too strict** → a real report fails to index. | Tolerant by design (validated against 5 real files); every field optional with "—" fallback; never raises on a parseable-as-text file. A file with no `# ` heading → title falls back to filename slug. |
| **Index clobbers a user's hand-written `logs/incidents/README.md`.** | **Resolved (see §3):** back up a non-marker README to `README.md.bak` (first-free name) before overwriting, reusing the exact Spec 4 pattern — honoring "never lose user content." Marker-bearing READMEs (our own output) overwrite in place. |
| **Status/title truncation hides info.** | Truncate only in the index table cell; the full text stays in the report file. Link goes to the file. |
| **Header-date fallback breaks the ISO sort** (human-formatted dates sort as garbage against ISO). | **Resolved (see §2):** parse common human formats to ISO; unparseable → undated sentinel that sorts last, raw string shown. Sort key is `(iso_date, filename)`, stable for duplicate dates. |

---

## Dogfood plan

After implementation: run `lfg incidents index` against a copy of the
`schema writer 2/logs/incidents` files in a temp dir; confirm the generated
README matches the validated prototype table (5 rows, correct dates/sev/status/
titles, newest-first). Then run it on this repo (no incidents yet → empty-state
README). Full suite + bash/PowerShell smoke green before tagging v0.5.0.
