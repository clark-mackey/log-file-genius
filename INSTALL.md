# Installation Guide

Install once in a Git repository and use the same project context from Claude Code, Codex, Pi, Warp, Orca, or Hermes. See [agent entry points](product/docs/context-guide.md#native-entry-points-and-limits) for host-specific discovery and verification.

## Prerequisites

- Git and an existing project repository.
- Python **3.10+** for managed setup and the CLI; no third-party runtime packages.
- Bash 4+ on macOS/Linux, or PowerShell 5.1+ on Windows.

You can read and maintain the Markdown without Python. The no-Python installer fallback is limited: it cannot safely merge existing instructions, generate routes, or configure all native entry points. Install Python for the automated path.

## Install

From the project root:

```bash
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
bash .log-file-genius/product/scripts/install.sh --ai-assistant generic --profile solo-developer
```

Windows PowerShell:

```powershell
git submodule add -b main https://github.com/clark-mackey/log-file-genius.git .log-file-genius
.\.log-file-genius\product\scripts\install.ps1 -AiAssistant generic -Profile solo-developer
```

Use `generic` for mixed-agent work. Named choices are `claude-code`, `codex`, `pi`, `warp`, `orca`, `hermes`, `grok-build`, and `aider`; `augment` remains available for existing users. Aider requires an explicit read of `AGENTS.md`. These choices do not install the agent applications.

Profiles: `solo-developer`, `team`, `open-source`, and `startup`. See [profile selection](product/docs/profile-selection-guide.md).

Commit the submodule reference, `.gitmodules`, shared entry files, and project records according to your repository's policy. Never include private credentials in logs.

## What gets installed

| Location | Contents |
|---|---|
| `logs/` | Missing STATE, CHANGELOG, DEVLOG, ADR, and incident records/indexes |
| `AGENTS.md` | A managed LFG block; existing instructions outside it are preserved |
| `CLAUDE.md` | An import of AGENTS.md; an existing `.claude/CLAUDE.md` can be used instead |
| `README.md` | A managed pointer to STATE and the ADR index |
| `.logfile-config.yml` | Configuration when none exists |
| `.log-file-genius/product/` | Source, CLI, documentation, and reference templates |

Existing root overrides and Hermes/Warp priority files receive a short pointer to the shared protocol. Inspect nested overrides separately. LFG does not create a second copy of your knowledge in `.agents/` or `.claude/`, install skills automatically, or replace those directories' settings, skills, hooks, or agents.

Known, unmodified legacy LFG rules are moved to `.lfg/retired-rules/` with their bytes preserved. Modified rule files remain in place and produce a diagnostic so you can resolve duplicate guidance.

Templates stay inside the source checkout; installation does not create a root `templates/` directory.

## Existing projects and force reinstall

Back up or commit current work before adopting a new documentation layout. Existing logs and configuration are retained. An existing `AGENTS.md` is merged using LFG markers, not replaced. Corrupt markers or a newer managed version are reported for manual resolution.

```bash
bash .log-file-genius/product/scripts/install.sh --ai-assistant generic --profile solo-developer --force
```

PowerShell uses `-Force`. This skips the confirmation prompt; it **does not overwrite existing logs or regenerate existing config**. Explicit assistant/profile choices also avoid selection prompts. Review all installer warnings before calling setup complete.

Custom paths in an existing `.logfile-config.yml` are honored by context commands; the shell installers still seed the standard `logs/` layout. Keep your existing path configuration and verify that STATE, ADR routing, and native pointers lead to the intended records. Do not assume installation relocates a custom knowledge collection.

## Verify the installation

From the consumer project root (use `python` on Windows):

```bash
python3 .log-file-genius/product/scripts/lfg.py validate
python3 .log-file-genius/product/scripts/lfg.py routes --check
python3 .log-file-genius/product/scripts/lfg.py freshness
```

An unknown STATE baseline is expected on a fresh install. Record the actual branch, code commit, next action, tests, and blockers after inspecting the project; do not replace unknown evidence with invented results.

Start a fresh session in your chosen agent. Verify its loaded instructions include LFG's AGENTS.md protocol (through Claude's import where appropriate). Ask it to identify the baseline and a governing ADR with source paths. Repeat from a nested project directory if that is how you work. See the [host checklist](product/docs/context-guide.md#native-entry-points-and-limits).

## Updating

```bash
bash .log-file-genius/product/scripts/update.sh
```

```powershell
.\.log-file-genius\product\scripts\update.ps1
```

The updater refreshes the source and managed context. Existing logs/config remain yours. It backs up known older generated instructions before conversion and keeps user-authored content outside managed blocks.

If the source checkout is missing from a worktree, run `git submodule update --init` there. This matters when launching agents in Orca or another worktree-based tool.

For a pre-v0.4.0 STATE layout, `lfg.py migrate-state --dry-run` previews the older structural migration. Review the [current STATE template](product/templates/STATE_template.md) afterward: establishing branch/commit and test evidence is a separate task.

## Optional Google OKF metadata

```bash
python3 .log-file-genius/product/scripts/lfg.py metadata --index
python3 .log-file-genius/product/scripts/lfg.py metadata --index --write
```

Review the preview before applying. The selected bundle is normally `logs/`; custom roots use `--bundle`. Unsupported YAML is preserved and reported. See [scope, conformance, and recovery](product/docs/context-guide.md#optional-okf-bundle) before migrating important records.

## Troubleshooting

- **Agent misses LFG:** inspect its actual loaded context, working directory, trust settings, and higher-priority overrides. The presence of a folder is not proof of loading.
- **Claude misses AGENTS.md:** verify `CLAUDE.md` imports it, or `.claude/CLAUDE.md` imports `../AGENTS.md`. Restart the session and inspect `/context`.
- **Conflicting instructions:** reconcile preserved modified legacy rules with the compact protocol. Keep project-specific requirements.
- **CLI cannot run:** check Python 3.10+, the repository root, and `git submodule update --init`.
- **Validation fails:** read the reported file/error and fix that record. Reinstalling with `--force` will not overwrite it.
- **Version banner disagrees:** the legacy installer config stamp/version parser can produce misleading status; inspect `.log-file-genius/product/VERSION.json` and the checkout. See [update notifications](product/docs/update-notifications.md).

## Uninstalling

Your logs and instructions may contain valuable project-owned content. Do not delete `logs/`, `.agents/`, or `.claude/` wholesale.

1. Keep or archive your knowledge records.
2. Remove only the LFG managed block from AGENTS.md and LFG pointer blocks from README/host files. Preserve other instructions and imports.
3. Review `.lfg/` backups and retired rules before removing LFG recovery data.
4. Remove the source submodule using your repository's normal Git procedure after checking it has no local changes.
5. Remove `.logfile-config.yml` only if you no longer use LFG tooling.

[Context guide](product/docs/context-guide.md) · [Migration guide](product/docs/MIGRATION_GUIDE.md) · [Report an issue](https://github.com/clark-mackey/log-file-genius/issues)
