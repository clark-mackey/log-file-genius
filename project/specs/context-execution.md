# Context workplan execution

Started 2026-09-12 from development `7dffd54`, on `codex/context-discovery`.
Authority: user requested execution of the reviewed workplan.

LFG remains Markdown + Git with optional Python standard-library tooling: durable,
low-dependency context for humans and any agent working on ongoing software.

## Contract and decision dispositions

| Prior contract | Disposition | Authority / dependent phase |
|---|---|---|
| Spec 2 always-loaded fragment bodies | Revise: compact startup; procedures on demand | Reviewed workplan + execute request; Phase 4 |
| Every-commit logging and automatic amend | Revise: meaningful changes and handoffs; preserve explicit project rules | Same; Phase 4 |
| Spec 2 STATE + changelog-only prime | Extend with explicit paths/sections and roles | Same; Phase 6 |
| No fuzzy topic selection or broad convenience CLI | Retain; reader chooses semantic matches | Phases 2A, 3, 6 |
| ADR 009 two-branch distribution | Retain; no full development→main merge | Phase 8 |
| Existing ADR history and project-owned instructions | Retain; additive routing, managed views, backups | All phases |

Protocol: discover → STATE → all global/path/task routes → active ADRs → reconcile
unknown or conflicting evidence → act. Budget overflow is incomplete coverage.
ADR routing fields: `Read when`, `Applies to` (repo-relative globs or `project-wide`),
`Constraint`, in `## Routing`; status remains the ADR's existing Status field.
Superseded records require `Superseded by` linking their replacement.
Freshness requires baseline branch + code commit preceding the handoff commit,
checkout comparison, and reconciliation of Current Context / Last Session contradictions.
Read-only questions do not require a state rewrite.

## Baseline evidence

- macOS, Python 3.14; 222 tests passed (3.47 seconds), before candidate edits.
- Existing generated startup: ~4,093 tokens (characters/4 estimate), before duplicate native rules.
- Current discovery omits ADR navigation and fresh installs omit ADR README.
- CLI #13–15 reproduced during the preceding audit; fixtures cover regressions.
- Installed executables: Codex, Claude, Python. PowerShell/Hermes/Grok absent.
- Native loading, model behavior and human retrieval are separate evidence gates;
  no results are inferred from Markdown or unit-test compatibility.

## Implemented checkpoints

| Phase | Delivered | Evidence / remaining boundary |
|---|---|---|
| 0 | Protocol, ADR-015 dispositions, versioned fixture manifest | Source/file baseline measured; historical native injection and behavioral baseline not measured |
| 1 | #13–15 repairs; atomic archival; collision/path/ownership protections | Regression tests and macOS Bash smoke pass; CI adds Linux and Windows |
| 2A | ADR-owned routing, status/replacement validation and deterministic views | Duplicate/placeholder/missing/cyclic routes refuse; curated history preserved |
| 2B | Optional bounded OKF producer, dry run, journaled resume/restore, safe backups | Full YAML parser validated all 27 Markdown files in our logs bundle; advanced input remains an explicit unsupported/partial result |
| 3 | Seeded root manifest, partitions, union selection, fallback and overflow diagnostics | Cross-component/global and stale/overflow fixtures pass; root and selected output both count |
| 4 | Compact managed startup and native pointers; meaningful-change logging | Adapter installation choices tested; actual loader behavior remains a separate gate |
| 5 | Branch/code baseline and checkout comparisons; unknown evidence explicit | Read-only checks; no timestamp-as-verification or whole-tree invalidation for context-only changes |
| 6 | Explicit source/section packets, neutral reader role and retained subagent contract | Missing selections, deduplication, path escape and complete-output budget tests pass |
| 7 | Durable ADR/incident retrieval and archive link relocation | Old decision remains reachable after archive; titled/angle/reference links and fenced examples covered |
| 8 | Dogfood migration, docs, versioned manifests, platform CI workflow | Development candidate only; main release and behavioral claims remain gated below |

## Measured candidate evidence

- Python 3.14 on macOS: **252 tests passed** (15.73 seconds on the final full run).
- Bash: install smoke, update smoke, validator regression and template-acceptance checks passed.
- Full lifecycle uses a real local Git remote: install → discover → selected packet →
  unknown-baseline resume → archive → update. Runs for all seven installer choices.
- Three code-owl review rounds repaired concrete archival, template ownership, restore,
  path containment, setup-error propagation and Markdown-link preservation defects.
- Generated startup: 212 estimated tokens; managed markers/native pointers add overhead.
  The default managed AGENTS block plus CLAUDE import pointer totals 248 estimated
  tokens. This measures produced files, not observed native injection.
  These are characters/4 estimates, not a model tokenizer measurement.
- The current project STATE is about 300 tokens. The root routing manifest plus the
  release-route partition is about 500 tokens; broader task unions can exceed budget
  and must report incomplete coverage. No governing rows are silently discarded.
- Template hashes preserve the 0.3.0/0.4.0/0.5.0 records and add 0.6.0-dev.
- Fresh CLI reads create no Python bytecode in the source installation.
- [PR #16](https://github.com/clark-mackey/log-file-genius/pull/16) merged into
  development at `c2d0dbb4791a41969249c932a3ae398108253106`. Candidate commit `882090c` passed the [six-job context matrix](https://github.com/clark-mackey/log-file-genius/actions/runs/34703104234):
  Linux, macOS and Windows × Python 3.10/3.14, with the full Python suite and
  Bash/PowerShell lifecycle smoke. Installer and log-validation workflows passed too.
- Windows CI exposed CRLF parsing drift, metadata rejecting ordinary CRLF documents,
  and redirected console Unicode failures. Source-byte preservation, CRLF migration
  and UTF-8 CLI output now have regression coverage; code-owl cleared these fixes.
  The second PowerShell smoke invocation now resolves from the workspace root.
- The optional PR-comment step lacked GitHub write permission. It is nonblocking;
  validation still determines the check result, with reports in artifacts/job summary.

## Gates not yet satisfied

The workplan is **not fully accepted for release**. No main promotion or release tag
is justified by the deterministic results alone.

Live evaluation began on `codex/context-evaluation`, isolated from the original
checkout and based on the merged development commit. The [evaluation record](../evaluations/context-2026-09-12/REPORT.md)
tracks native host evidence, all trial attempts, matched controls, maintenance and
the prepared human handoff packages. Native Codex traces already show why generated
file sizes are insufficient: default managed guidance is 233 estimated tokens, but
its observed host instruction envelope is 269. The 250-token startup cap and the
eight-read discovery cap remain unchanged. Early behavior trials exceed these caps;
correct final answers do not erase those failures.

1. Native loader evidence: capture effective injected files/bytes and override/duplicate
   behavior for each claimed host. Installed local CLIs are Codex 0.149.1 and Claude
   Code 2.1.269; their version strings do not count as behavior trials.
2. Model application: three fresh sessions per critical fixture per claimed host/model,
   all passing; noncritical categories need at least ten trials and 90% success.
3. Efficiency comparison: measured loaded bytes, reads and repeated tool output for
   candidate vs baseline vs ordinary docs. File-size reduction alone is not that result.
4. Maintenance: five paired tasks, no missing required facts and no increase in median
   logging actions/documentation-only follow-ups. Policy simplification is not a trial.
5. Human retrieval: three blinded paired readers finding next action, ADR and evidence.
   No human trials have been fabricated or substituted with model answers.

The runtime remains optional stdlib Python. Pytest and PyYAML were installed only in
`/tmp/lfg-execution-venv` for development checks. Original-byte backups and the metadata
recovery journal remain local; `.codegraph/` was not modified or staged.
