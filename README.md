# Log File Genius

**Project memory you can carry between coding agents.**

Keep current work, decisions, changes, and lessons in Markdown and Git. Give Claude Code, Codex, Pi, Warp, Orca, and Hermes a small entry point to the same project knowledge, with optional **Google Open Knowledge Format (OKF) v0.2** metadata.

[Install](INSTALL.md) · [Context guide](product/docs/context-guide.md) · [Agent compatibility](product/docs/context-guide.md#native-entry-points-and-limits) · [Contribute](CONTRIBUTING.md)

## What it does

- **Resume work:** `STATE.md` records the baseline branch/commit, next action, tests, and blockers. Check it against the current checkout before relying on it.
- **Find decisions:** ADR routing connects a task or file path to the decisions that govern it.
- **Keep useful history:** CHANGELOG records what changed, DEVLOG explains why, and incident reports preserve lessons from failures.
- **Share selected context:** Send a colleague or subagent the records they need with explicit file/section selection.
- **Change agents without moving your knowledge:** `AGENTS.md` carries the shared reading protocol; Claude imports it through `CLAUDE.md`. Existing skills and tool settings stay yours.
- **Use open formats:** The optional OKF producer adds metadata and an index to a selected knowledge bundle, with preview, backups, and recovery.

No hosted memory service, model API, vector database, or mandatory plugin. Markdown works on its own; the automation uses Python's standard library.

## Quick start

Run from an existing Git repository. Use Python **3.10+** for the CLI and automated setup; Bash 4+ or PowerShell 5.1+ for the installer.

**macOS / Linux**

```bash
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
bash .log-file-genius/product/scripts/install.sh --ai-assistant generic --profile solo-developer
```

**Windows PowerShell**

```powershell
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
.\.log-file-genius\product\scripts\install.ps1 -AiAssistant generic -Profile solo-developer
```

Use `generic` when you switch between agents. Named choices include `claude-code`, `codex`, `pi`, `warp`, `orca`, and `hermes`. They share the same records and setup; see the [installation guide](INSTALL.md) for existing projects and custom paths.

## One knowledge collection, multiple entry points

| Path | Purpose |
|---|---|
| `logs/STATE.md` | Current work and handoff evidence |
| `logs/CHANGELOG.md`, `logs/DEVLOG.md` | Change history and reasoning |
| `logs/adr/`, `logs/incidents/` | Decisions, routes, and lessons |
| `AGENTS.md` | Compact shared instructions, merged into your existing file |
| `CLAUDE.md` or existing `.claude/CLAUDE.md` | Imports the shared instructions for Claude |
| `.agents/skills/`, `.claude/skills/` | Your on-demand skills; preserved, not replaced by LFG |
| `.log-file-genius/` | Hidden source checkout, procedures, templates, and CLI |

`AGENTS.md` and `.agents/` have different jobs: the file supplies project instructions; the directory can hold reusable skills. LFG installs the context protocol, not a new skills framework. Your skills can read the same logs and call the same CLI.

## Agent compatibility

Claude Code uses a small import of `AGENTS.md`. Codex and Pi use `AGENTS.md`; Warp uses it unless an existing `WARP.md` takes priority. Orca uses the conventions of its selected agent. Hermes can prefer its own context file, so LFG adds a pointer to existing priority files.

Install/update tests verify the files LFG produces. Actual discovery also depends on the host version, working directory, trust settings, and overrides. The [compatibility table and verification steps](product/docs/context-guide.md#native-entry-points-and-limits) describe those boundaries. Augment remains a legacy installation option.

## Daily use

Start with STATE and the ADR index. Follow matching decisions, verify recorded evidence, then do the work. Update records for meaningful changes and handoffs; a read-only question does not need a documentation commit.

From your project root (use `python` on Windows):

```bash
python3 .log-file-genius/product/scripts/lfg.py freshness
python3 .log-file-genius/product/scripts/lfg.py routes --check
python3 .log-file-genius/product/scripts/lfg.py prime --role reader --include logs/STATE.md
python3 .log-file-genius/product/scripts/lfg.py validate
```

Other tools include `archive --dry-run`, `incidents-index`, `secrets`, and opt-in `install-hooks`. Run `lfg.py --help` for the full list. Secret detection is a check, not a guarantee that a file contains no secrets.

## Google Open Knowledge Format

LFG targets the minimal representation requirements of [Google's OKF v0.2](https://github.com/GoogleCloudPlatform/open-knowledge-format/blob/main/SPEC.md) for a selected bundle, normally `logs/`. It preserves document bodies and custom metadata and can add a navigation index.

```bash
# Preview before applying
python3 .log-file-genius/product/scripts/lfg.py metadata --index
python3 .log-file-genius/product/scripts/lfg.py metadata --index --write
```

The producer handles a bounded YAML subset. Unsupported existing YAML is preserved and reported; a partial conversion is not a conformance claim. Metadata does not prove that an agent loaded or followed a document. See [OKF migration and recovery](product/docs/context-guide.md#optional-okf-bundle).

## Updating

```bash
bash .log-file-genius/product/scripts/update.sh
```

On Windows, run `.\.log-file-genius\product\scripts\update.ps1`. The updater preserves user content outside LFG's managed blocks and retains existing logs/config. Review its messages about overrides, modified legacy rules, and optional migrations.

## Learn more

- [Installation and troubleshooting](INSTALL.md)
- [Finding context, routing decisions, and handing off work](product/docs/context-guide.md)
- [Documentation methodology](product/docs/log_file_how_to.md)
- [Migrating existing records](product/docs/MIGRATION_GUIDE.md)
- [Examples](product/examples/README.md)
- [Contributing and test commands](CONTRIBUTING.md)

[MIT license](LICENSE) · [Issues](https://github.com/clark-mackey/log-file-genius/issues)

<!-- LFG:POINTER:BEGIN -->
Project context: [STATE](logs/STATE.md), [decisions](logs/adr/README.md).
<!-- LFG:POINTER:END -->
