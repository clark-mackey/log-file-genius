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

## Selected context packets

```sh
python3 .log-file-genius/product/scripts/lfg.py prime --role reader --objective "Resume auth work" --include logs/adr/003-auth.md --include logs/DEVLOG.md#Daily\ Log --budget 2000
python3 .log-file-genius/product/scripts/lfg.py prime --include logs/adr/003-auth.md
```

The default retains `LFG_SUBAGENT_PRIME`. Subagents stage findings in `.lfg/staged/<id>/`
and return consulted ADR IDs plus unresolved scope; the lead reviews and promotes
canonical log changes. `--role reader` is neutral human/lead context. Repeated selections
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

## Optional OKF bundle

`logs/` is the usual bundle boundary; with custom paths the default is STATE's directory.
Use `metadata --bundle path` when all desired context lives under a different root.
Scattered paths are reported as partial scope; nothing is relocated.

```sh
python3 .log-file-genius/product/scripts/lfg.py metadata --index
python3 .log-file-genius/product/scripts/lfg.py metadata --index --write
python3 .log-file-genius/product/scripts/lfg.py metadata --restore
```

The producer follows [OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md):
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
resume the frozen plan, or `--restore` to restore original bytes. Concurrent changes
refuse restoration; inspect them first. Do not remove the journal until recovery is
complete. Root index publication comes last; partial migration is never reported complete.

## Native entry points and limits

Install with `--ai-assistant codex`, `hermes`, `grok-build`, `generic` or `aider`
(`-AiAssistant` in PowerShell), as well as the existing `augment`/`claude-code`
choices. These choices install pointers; they are not behavioral certification.
Use `generic` for a human or a custom bot. Aider still requires explicit `--read AGENTS.md`.

| Reader | Entry point | What still needs checking |
|---|---|---|
| Codex | Root AGENTS.md; pointer in existing root AGENTS.override.md | Nested overrides, configured size limits and actual loaded chain |
| Claude Code | Root CLAUDE.md imports AGENTS.md | User imports/rules may duplicate guidance |
| Hermes | AGENTS.md; pointers in existing .hermes AGENTS files | Effective context-file priority and nested scope |
| Grok Build | Trusted repository rules including AGENTS.md | Repository trust; hosts loading CLAUDE as well may duplicate |
| Augment | Root AGENTS.md | Existing modified .augment/rules remain; inspect duplicates |
| Aider | Explicit read/config pointing at AGENTS.md | Opt-in; no automatic configuration changes |
| Custom bot / OKF consumer | Host explicitly loads index/startup | No universal native filename or automatic injection |
| Human | README links to STATE and decisions | No CLI required |

Install/update preserves user instructions. Only exact known shipped rule bytes move
out of autoload; modified copies remain with a diagnostic. Backup files use non-Markdown
extensions. Inspect nested overrides manually. Targets are 150–250 startup, 500 STATE,
300–500 routing tokens; estimates use characters/4. Count actual host injection, tool
output and duplicate reads separately. Cross-host/model and blinded-human outcome
gates must be measured before claiming reliable support.

Native loading references: [Codex](https://learn.chatgpt.com/docs/agent-configuration/agents-md),
[Claude Code](https://code.claude.com/docs/en/memory),
[Hermes](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files),
[Grok Build](https://github.com/xai-org/grok-build/blob/main/crates/codegen/xai-grok-pager/docs/user-guide/12-project-rules.md),
[Augment](https://docs.augmentcode.com/cli/rules), and
[Aider](https://aider.chat/docs/usage/conventions.html). These describe entry conventions;
they do not replace the workplan's native-loading and task-application tests.
