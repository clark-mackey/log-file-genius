# Finding and maintaining project context

LFG is Markdown and Git, with optional Python tooling. It helps a human or agent
find current work, governing decisions, and the evidence behind them. It does not
guarantee that every host loads those files or that every model applies them correctly.

## Start with the task

Read the configured STATE and ADR README. The README is always the root routing
manifest, even when it links to partitions. Match all project-wide rows, affected
paths, and semantic task triggers. Union matches; read each active ADR once. Follow
replacement links. Reader judgment selects semantic matches; LFG does no fuzzy ranking.
On task expansion, revisit the manifest. Reuse unchanged records already read.

On a missing or stale index, search the configured ADR directory using one or two
literal terms for the task and affected components. Inspect candidate status and
replacement links. Bound the initial search to eight reads; if unresolved, report
the unchecked scope and continue in explicit batches before claiming coverage.
Use every matching task route below. Resolve log locations through configuration;
project requirements keep their existing location and schema.

| Task | Read |
|---|---|
| Resume or hand off work | STATE, then its evidence links |
| Plan or change behavior | ADR root manifest and all matching active decisions |
| Investigate a failure or retry an approach | Incident README and matching incident reports |
| Check intended behavior or acceptance | Project README's requirements/specification links; report missing links |
| Recover past implementation reasoning | Selected DEVLOG entries and their archive links |

The source records govern; indexes only help locate them.

Use `.logfile-config.yml` paths; older `paths.adr` remains supported. Commands below
run from the consumer repository root. On Windows use `python` instead of `python3`.
For LFG contributors, replace `.log-file-genius/product/` with `product/`.

```sh
python3 .log-file-genius/product/scripts/lfg.py routes --check
python3 .log-file-genius/product/scripts/lfg.py routes --write
python3 .log-file-genius/product/scripts/lfg.py routes --path src/api/auth.py --select ADR-003
python3 .log-file-genius/product/scripts/lfg.py freshness
```

No Python: read Markdown directly. Missing runtime file in a submodule installation:
run `git submodule update --init` from the repository root. An absent source checkout
requires reinstalling LFG; a CLI alias or global package is never required.

## Write a routed decision

Keep ID/title in `# ADR-NNN: Title` and one `**Status:**` field. Status is Proposed,
Accepted, Deprecated or Superseded. Add this body section to the owning ADR:

```markdown
## Routing

**Read when:** Changing authentication or session handling
**Applies to:** src/auth/*, tests/auth/*
**Constraint:** Sessions must expire server-side before credentials can be reused.
```

Use `project-wide` for global constraints. Globs use case-sensitive repository-relative
POSIX paths; `*` can span directories. Commas separate globs. For Superseded status,
add `**Superseded by:** [ADR-004](004-new-decision.md)`. Never overwrite historical
rationale. Missing metadata, duplicate IDs, and cycles block view generation.
Migrate README-only routes into the source ADR explicitly; preserve original notes
until their meaning and authority are resolved. Running routes never invents metadata.

## Handoffs and evidence

STATE is a small shared snapshot, normally at most 500 estimated tokens. Record
baseline branch and code commit before committing the handoff itself, next action,
tests with outcomes, and blockers. Keep task-local scratch and ownership in the
session/worktree; avoid replacing another active task's state.

Compare the current checkout with that baseline. Code differences call for checking
affected claims, not declaring all history false. Reconcile Current Context and Last
Session contradictions. Local Git cannot prove a PR was merged or a deploy succeeded:
record a dated external source for those claims. A changed timestamp is not verification.
The freshness command flags evidence gaps and a limited contradiction pattern; a
reader must check the actual facts. Read-only questions need no state rewrite.

Log meaningful behavior changes, decisions, lessons and handoffs. Small intermediate
commits may share a coherent entry. Do not require repetitive user-facing checklists,
documentation-only follow-up commits, or automatic amendment of history. Explicit
stricter project instructions still apply. See [maintenance](../rules/log-file-maintenance.md).

## Delegating record maintenance

For updates to STATE, CHANGELOG, DEVLOG, ADRs and incidents, follow the
[delegated record maintenance policy](../rules/log-file-maintenance.md#delegated-record-maintenance).
Prefer a capable worker on the harness's configured lower-cost model when available
and worthwhile. Keep model names, prices and provider commands in the harness's own
configuration. LFG's shared instructions express the policy; they do not configure
or guarantee delegation in every host. Unsupported or unsuitable delegation falls
back to the lead completing the same work directly.

The lead supplies evidence and rationale, the worker stages drafts, and the lead
checks completeness and accuracy before promotion. Preserve substantive detail and
OKF metadata regardless of model cost. Include relevant instructions and source
records in the packet below; STATE plus recent CHANGELOG entries alone do not capture
a session's decisions, full diff or test results. The worker returns missing context
and questions rather than guessing. No recursive delegation or reduced quality bar.

## Selected context packets

```sh
python3 .log-file-genius/product/scripts/lfg.py prime --role reader --objective "Resume auth work" --include logs/adr/003-auth.md --include logs/DEVLOG.md#Daily\ Log --budget 2000
python3 .log-file-genius/product/scripts/lfg.py prime --include logs/adr/003-auth.md
```

The default retains `LFG_SUBAGENT_PRIME`. Subagents stage findings in `.lfg/staged/<id>/`
and return consulted ADR IDs plus unresolved scope; the lead reviews and promotes
canonical log changes. Markdown and JSON packets carry the same role instructions, including staging and
record-quality safeguards. `--role reader` is neutral human/lead context. Repeated selections
are deduplicated. Paths may include an exact heading after `#`. Missing files/sections
are explicit; output covers selected material only. Overflow refuses the packet,
listing unread selections; narrow the task, choose sections, or explicitly raise the
budget. Objective, role, evidence, paths, JSON overhead and excerpts all count.

## Durable lessons and archival

Keep enduring decisions in ADRs and failure analysis in incidents, with links from
their indexes. Record the conditions under which an approach failed and when it
could be reconsidered. Supersede obsolete constraints explicitly. Before archiving,
extract any still-useful lesson through normal human/agent work; the archiver does
not invent summaries. ADRs and incidents remain reachable after dated log entries move.
Archive preview refuses unsupported headings and oversized unparsed content. Back up
before converting legacy sections to canonical date entries. Review links after moving.

<a id="optional-okf-bundle"></a>

## OKF knowledge bundle

New installations initialize OKF metadata and a navigation index automatically. The
installer treats a project as new only when neither `logs/` nor `.logfile-config.yml`
exists. Existing projects retain their records and opt into the conversion below;
`--force` skips prompts, not preservation. See the [existing-project upgrade](MIGRATION_GUIDE.md#upgrade-an-existing-lfg-project-including-okf).

`logs/` is the usual bundle boundary; with custom paths the default is STATE's directory.
Use `metadata --bundle path` when all desired context lives under a different root.
Scattered paths are reported as partial scope; nothing is relocated.

```sh
python3 .log-file-genius/product/scripts/lfg.py metadata --index
python3 .log-file-genius/product/scripts/lfg.py metadata --index --write
python3 .log-file-genius/product/scripts/lfg.py metadata --restore
```

The producer targets the minimal representation requirements of [Google Open Knowledge Format (OKF) v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md):
add a nonempty `type`, preserve `doc`, `related`, custom keys and bodies. Titles are
quoted safely. Migration never adds `verified`, fabricated provenance, or lifecycle
status. ADR Status remains distinct from optional OKF draft/stable/deprecated status.
All nonreserved Markdown counts, including archives, templates and READMEs. Optional
lowercase `index.md` is a directory listing; `log.md` is reserved for date-grouped updates.

The runtime intentionally accepts a small YAML mapping/scalar subset. Unsupported
YAML is left untouched and reported, not declared invalid OKF. Validate advanced
metadata using a full YAML parser outside the runtime. A partial result is not a
conformance certificate. Basic representation conformance does not prove host discovery.

Writes validate before replacement, save exact-byte backups, recheck the target, then
atomically replace each file. Collection writes are not a single transaction. An
interruption leaves `.lfg/metadata-migration.json` plus backups: repeat `--write` to
resume the frozen plan, or `--restore` to restore original bytes. Restore uses the
bundle recorded in the journal; an explicit `--bundle` must match it. Concurrent
changes refuse restoration; inspect them first. Do not remove the journal until recovery is
complete. Root index publication comes last; partial migration is never reported complete.

## Native entry points and limits

Use `--ai-assistant generic` (`-AiAssistant generic` in PowerShell) when switching
between tools. Named options include `claude-code`, `codex`, `pi`, `warp`, `orca`,
and `hermes`; they share one context collection. `grok-build`, `aider`, and legacy
`augment` remain available. These options configure LFG files, not the agent itself.

| Reader | Shared entry point | Verify in the actual host |
|---|---|---|
| Claude Code | Root CLAUDE.md imports AGENTS.md, or an existing .claude/CLAUDE.md imports ../AGENTS.md | `/context` lists the memory files; inspect exclusions and other imports |
| Codex | Root AGENTS.md; pointer in existing root AGENTS.override.md | Effective instruction chain, nested overrides, configured size limit |
| Pi | AGENTS.md; root override points back to it | Startup header lists the file; context discovery is enabled |
| Warp | AGENTS.md; pointer in an existing WARP.md because it takes priority | Project Rules/References show the applicable file |
| Orca | The selected Claude/Codex agent's entry point | Actual worktree has the committed files and initialized source submodule |
| Hermes | AGENTS.md; pointers in existing .hermes.md, HERMES.md, and root override | Effective priority file and working directory; preserve global SOUL.md |
| Grok Build | Trusted repository AGENTS.md | Repository trust and duplicate loading |
| Aider | Explicit `--read AGENTS.md` | Opt-in read/config; LFG does not change Aider settings |
| Augment (legacy) | Root AGENTS.md | Modified old .augment rules can still duplicate guidance |
| Human / custom bot / OKF consumer | README/STATE/index links or explicit file loading | The reader has access to the selected files; no universal bot loader |

### .agents and .claude coexistence

`AGENTS.md` is an instruction file. `.agents/skills/` is an on-demand skill location
used by Codex and Pi. Claude uses its own `.claude/skills/`, settings, hooks, and
agent definitions. LFG preserves those directories and does not install or invoke
skills automatically. Existing skills can read the same STATE/ADR records and use
the repo-local CLI; they do not need a separate memory store.

Claude imports are relative to the containing file. A root `CLAUDE.md` uses
`@AGENTS.md`; `.claude/CLAUDE.md` uses `@../AGENTS.md`. Avoid importing the same
protocol from several always-loaded files. Existing user imports are preserved. Native symlinks directly to the in-repository
AGENTS.md remain intact; external or unrelated symlink destinations require manual
setup.

### Preservation and scope

Install/update retains user instructions. Only exact known shipped legacy rule
bytes move out of autoload; modified copies remain with a diagnostic. Backup files
use non-Markdown extensions. Root priority files are handled; inspect nested
AGENTS.override.md, WARP.md, and Hermes files separately when starting below the
root. A pointer asks the reader to consult AGENTS.md; it is not a universal import
mechanism. Trust settings and model behavior can still prevent that read.

Keep shared entry files and the source submodule reference in Git when using
worktrees. Run `git submodule update --init` in a new worktree before CLI commands.
Do not copy a personal `.agents` or `.claude` directory over another worktree's
configuration to make discovery work.

### What is verified

LFG's automated tests check generated files, preservation, repeated setup,
installer aliases, route selection, and metadata migration. CI exercises Python
3.10/3.14 on Linux, macOS, and Windows. These checks do not execute every host or
prove a model follows the instructions.

Fresh-session retrieval smoke test on 2026-09-16: Claude Code 2.1.273 read the
generic installation's protocol and returned the fixture's baseline, next action,
and routed ADR constraint with source paths. This was one read-only trial, not a
cross-model reliability measurement. Codex's local CLI could not run its configured
model without an upgrade; Pi 0.85.1 lacked provider authentication. Warp, Orca, and
Hermes native sessions were not exercised. Their file conventions and installer
fixtures are covered; native behavior remains unverified.

For each host/version you intend to rely on:

1. Install into a disposable Git project containing a STATE and a known routed ADR.
2. Start a fresh session at the root; inspect the host's loaded context.
3. Ask for the baseline, next action, and relevant ADR with exact file references.
4. Repeat from a nested directory and with your existing priority/override files.
5. Change a decision and start another session; confirm it reads the changed record.
6. Perform a small task and verify the handoff preserves actual evidence.

Record results as host/version/date, working directory, loaded entry file, expected
record, and observed result. Unrun checks remain unverified. “Flawless across tools”
is an acceptance goal, not a result inferred from creating Markdown files.

Startup, STATE, and routing budgets are small reading targets, not claims about
measured host injection. Count actual loaded bytes, tool output, and duplicate
reads separately. STATE is evidence for coordination, not a lock against edits.

### Primary references

Entry conventions checked on 2026-09-16:

- [Codex instructions](https://learn.chatgpt.com/docs/agent-configuration/agents-md) and [skills](https://learn.chatgpt.com/docs/build-skills)
- [Claude project memory/imports](https://code.claude.com/docs/en/memory)
- [Pi context files and skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md)
- [Warp project rules and precedence](https://docs.warp.dev/agents/capabilities/rules/)
- [Orca agent hooks and memory](https://www.onorca.dev/docs/agents/hooks-memory)
- [Hermes context-file priority](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files)
- [Google OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md)
