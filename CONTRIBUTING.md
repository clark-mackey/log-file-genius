# Contributing to Log File Genius

LFG keeps project context in Markdown and Git, shared across humans and coding agents. Contributions should preserve existing records, stay small, and keep the Python runtime standard-library-only.

## Branches and scope

`development` holds product code and internal project records. `main` is the distributable: promote product changes and necessary public documentation/CI selectively through a PR. Do not merge the whole development branch or copy internal logs, plans, or research into main.

## Development setup

Use Python **3.10+**, Git, and Bash or PowerShell. Development tests use pytest and PyYAML; consumer runtime code must not require them.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install pytest pyyaml
python -B -m pytest product/tests -q
```

On Windows, activate `.venv\Scripts\Activate.ps1`. Run shell checks on macOS/Linux and PowerShell checks on Windows.

## Where to make changes

| Behavior | Source |
|---|---|
| Compact shared reading protocol and native pointers | `product/scripts/startup.py` |
| Generated output and managed-block rendering | `product/scripts/generator.py` |
| Detailed maintenance guidance | `product/rules/log-file-maintenance.md`, `product/docs/context-guide.md` |
| Bash/PowerShell setup | `product/scripts/install.*`, `product/scripts/update.*` |
| ADR discovery and routing | `product/scripts/routing.py` |
| Optional OKF migration | `product/scripts/metadata.py` |
| Templates and ownership hashes | `product/templates/`, `product/scripts/known_template_hashes.json` |

`product/AGENTS.md` is generated from the compact protocol in `startup.py`. The generator retains legacy fragment parsing helpers; changing a rule fragment does not change the startup body or automatically install per-tool rule copies.

After changing startup text:

```bash
python product/scripts/lfg.py generate
python product/scripts/lfg.py generate --check
```

`render_full()` emits the distributable body; `render_block()` wraps it in `<!-- LFG:BEGIN v… -->` / `<!-- LFG:END -->` markers for merging into consumer files. Preserve the marker contract and user-owned surrounding content.

After changing templates:

```bash
python product/scripts/update_template_hashes.py
python product/scripts/update_template_hashes.py --check
```

Retain historical ownership hashes. Do not guess that a user-edited file belongs to LFG. Updates must preserve custom records/settings and provide exact-byte recovery where promised.

## Agent compatibility

Prioritize shared `AGENTS.md`, Claude's import, coexistence with `.agents/skills/` and `.claude/`, and selected-bundle OKF representation. Keep knowledge in one collection. A host adapter should point to that collection rather than duplicate records or replace host settings.

For Claude Code, Codex, Pi, Warp, Orca, and Hermes changes:

1. Check current primary documentation for actual entry filenames, precedence, and trust behavior.
2. Add a focused regression test for the changed setup or preservation behavior.
3. Exercise clean install, repeat install, update, user-owned instructions, and priority overrides.
4. Record which host/version/session was actually tested. Generated files and unit tests alone do not prove the host loaded or followed the protocol.

See [entry points and verification](product/docs/context-guide.md#native-entry-points-and-limits). Keep legacy Augment support functional without making it the primary installation story.

## Checks before a PR

```bash
python -B -m pytest product/tests -q
python -B product/scripts/lfg.py generate --check
python -B product/scripts/update_template_hashes.py --check
bash product/tests/smoke_install.sh
bash product/tests/smoke_update.sh
bash product/tests/test_validate_sh.sh
bash product/tests/test_validators_accept_templates.sh
```

Windows equivalents include `product/tests/smoke_install.ps1` and `smoke_update.ps1`. GitHub Actions runs the installer checks and the Python 3.10/3.14 matrix across Linux, macOS, and Windows.

For docs-only changes, check relative links and examples. For OKF changes, distinguish minimal bundle conformance from a full YAML consumer, optional verification metadata, and host behavior. Never fabricate provenance or verification fields.

## Pull requests

Describe the concrete problem, resulting behavior, validation, and remaining limits. Keep unrelated changes separate. Link issues where useful. Use a clear commit subject, such as `Fix: preserve Claude instructions during context setup`.

Report bugs through [GitHub Issues](https://github.com/clark-mackey/log-file-genius/issues), including the LFG commit/version, host/version, OS, reproduction steps, and expected/actual behavior. Redact secrets and private project records.

Contributions are licensed under the project's [MIT license](LICENSE).
