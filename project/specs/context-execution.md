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
- At the initial execution checkpoint, [PR #16](https://github.com/clark-mackey/log-file-genius/pull/16) was a draft against
  development. Candidate commit `882090c` passed the [six-job context matrix](https://github.com/clark-mackey/log-file-genius/actions/runs/34703104234):
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

## 2026-09-16 promotion and portability follow-up

PR #16 has merged into development. On explicit user request, the product was
selectively promoted through [PR #17](https://github.com/clark-mackey/log-file-genius/pull/17),
merged into main at `8672f14` on 2026-09-16 UTC. Its 12 CI checks passed. The user
authorized the administrator override for the required-review rule. Main stayed
product/public-docs only, at v0.6.0-dev, with no release tag. This authorization did
not complete the behavioral gates above; their unmeasured results remain unknown.

The user then prioritized `.agents`/`.claude`, Google OKF and Claude/Codex/Pi/Warp/
Orca/Hermes compatibility. [PR #18](https://github.com/clark-mackey/log-file-genius/pull/18)
fixes setup entry points and updates public docs; development source baseline is
`7c3693f`. No automatic skills installation or broad host certification was added.

Evidence on the public product checkout:

- 274 Python tests passed; the one dogfood test skipped because main has no logs.
- Bash install/update smoke, generator/template checks and normalized manifest
  checksums passed. Tests cover priority files, repeat setup, user skills/settings,
  canonical symlinks and refusal of external symlink destinations.
- Fresh generic install: seven nonreserved bundle files parse with PyYAML and
  contain type metadata; index exists; a repeat metadata migration changes no bytes.
- Claude Code 2.1.273 fresh read-only trial correctly retrieved baseline branch,
  next action and ADR-099 constraint from a disposable fixture with source paths.
- Codex CLI 0.149.1 refused its configured model pending CLI upgrade. Pi 0.85.1
  could not start because its selected provider lacked authentication. These are
  infrastructure blocks, not successful native tests. No model/provider was swapped.
- Warp, Orca and Hermes native sessions were not tested. Primary documentation
  supports the entry conventions; actual loading/behavior remains to be measured.

The one Claude trial is a smoke check only and does not satisfy the multi-session,
model, efficiency, maintenance or blinded-human acceptance gates.


## 2026-09-16 OKF default follow-up

The user confirmed new installations must adopt OKF by default and asked about
converting an existing project such as Schemalyze. Public commit `28ee4f5` updates
PR #18; development code baseline `26db4b5` updates PR #19. ADR-015 records the
amendment to optional-only adoption. Schemalyze was not modified.

Fresh means neither logs nor configuration existed before installation. Bash and
PowerShell invoke the existing metadata producer with an index after context setup.
Existing records/config remain in preservation mode, including with force. Missing
Python blocks new setup before writes; producer errors return failure with an
explicit recovery command. The migration guide covers custom paths, unsupported
YAML, owned indexes, checkpoints, route checks and native retrieval checks.

Public checkout validation: 278 passed, one expected dogfood skip. Development
checkout: 279 passed. Added checks
cover automatic YAML/type/index output, existing log/config preservation, repeat
install preservation, producer refusal and missing-interpreter early exit. Code Owl
reported no new blocker. The existing command-availability interpreter detection is
not a Python-version/usability preflight. Git fixture setup intermittently failed in
local object copying; switching the fixture clone to Git transport (--no-local)
resolved that failure and the full suite passed. No product workaround was added.

Bash syntax, normalized version checksums, generated-file/template hashes and
whitespace checks pass. Native-agent behavioral evidence and limitations from the
previous section are unchanged. CI and PR state should be checked live before merge;
neither PR is authorized to merge by this follow-up.


Windows CI initially exposed a test-only locale mismatch: the new full-YAML check
used Path.read_text's cp1252 default against UTF-8 templates. Public follow-up
`00ee4e4` sets UTF-8 explicitly; installer behavior is unchanged. CI reruns verify
the correction on Windows Python 3.10 and 3.14.


## 2026-09-17 delegated record maintenance

User approved a portable instruction preferring a capable lower-cost subagent for
maintaining project records, with unchanged quality requirements. Public commit
`f7c77ae` updates PR #18; development code baseline `15711d4` updates PR #19.
ADR-015 records the decision. Scope excludes upgrading LFG software.

Startup directs the reader to the full maintenance policy and remains 245/250
estimated tokens. Harness configuration owns model/provider selection; unsupported,
unsuitable or uneconomical delegation falls back to direct execution. The lead
supplies source evidence and rationale, checks completeness/accuracy and promotes
accepted staged drafts. Workers retain formats, OKF metadata, uncertainty, history
and constraints, return missing context, and never delegate recursively.

Markdown and JSON prime packets now carry identical role instructions. Tests verify
neutral readers, worker staging/preservation safeguards and exact retention of long
selected evidence; either serialization refuses insufficient budgets without truncation.
Public suite: 280 passed, one expected no-development-logs skip; development: 281 passed. Code Owl found no
new issues. Generator/template hash, normalized version checksum and whitespace
checks passed. These establish instruction delivery and packet behavior, not measured
cost savings or equal record quality across models; those require paired native trials.
