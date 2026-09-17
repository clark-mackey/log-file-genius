# Installer Testing Guide

Test the shared context lifecycle and preservation behavior for Claude Code, Codex,
Pi, Warp, Orca, and Hermes. Augment remains a legacy compatibility case.

## Automated checks

From the source repository with Python 3.10+ and development dependencies installed:

```bash
python -B -m pytest product/tests -q
python -B product/scripts/lfg.py generate --check
python -B product/scripts/update_template_hashes.py --check
bash product/tests/smoke_install.sh
bash product/tests/smoke_update.sh
bash product/tests/test_validate_sh.sh
bash product/tests/test_validators_accept_templates.sh
```

Windows uses `product/tests/smoke_install.ps1` and `smoke_update.ps1`. CI runs Python
3.10/3.14 across Linux, macOS, and Windows. `test_context_workplan.py` exercises
installer choices with a real local Git source remote, repeated installation,
selected packets, archival, and update. A source checkout without development
logs intentionally skips the repository dogfood archive test.

## Manual setup checks

Use a disposable Git repository and a local source checkout. Do not run destructive
fixtures against your own records.

1. **Fresh generic install:** STATE, ADR index, managed AGENTS.md, Claude import,
   README pointer, and config exist. Inspect all reported warnings.
2. **Existing project:** user instructions, logs, incident index, and config survive.
   `--force` skips confirmation; it does not authorize overwriting records.
3. **Repeat setup:** managed content is stable and native pointers are not duplicated.
4. **Claude variants:** generic setup works before Claude is used; an existing
   `.claude/CLAUDE.md` gets the correct relative import when no root file exists.
5. **Priority files:** preserve existing AGENTS.override.md, WARP.md, .hermes.md,
   and HERMES.md while linking back to the shared protocol.
6. **Skills/settings:** existing `.agents/skills`, `.claude/skills`, hooks, agent
   definitions, and settings remain unchanged.
7. **Unsafe destinations:** external/noncanonical symlinked entry files and malformed managed blocks
   refuse unsafe writes; originals remain available for manual reconciliation. Native symlinks to the
   in-repository AGENTS.md stay intact.
8. **Legacy rules:** exact known LFG rules retire with recoverable bytes; modified
   copies remain visible for review.
9. **Worktrees:** committed entry files are present and `git submodule update --init`
   makes the CLI available from the actual agent worktree.
10. **OKF:** new installs create metadata and a navigation index automatically; existing
    logs or configuration remain unconverted, even with force. Preview and migrate
    an existing bundle explicitly. Validate both paths with a full YAML parser in development. Unsupported YAML, partial scope, and interrupted migrations
    must not be reported as complete conformance.

A failed operation may leave earlier per-file changes; setup is not a transaction
across the whole repository. Review diagnostics and backups before retrying.

## Host-level acceptance

File generation tests are necessary but do not show what a host actually loaded.
Use the [host/version checklist](context-guide.md#what-is-verified) in a fresh
session for each claimed integration. Verify root/nested starts, priority files,
actual record retrieval, and a real handoff. Record unrun cases as unverified.

For Orca, test the selected underlying agent in its worktree. For `.agents` and
`.claude` skills, test the host's skill discovery separately from AGENTS.md loading.
Google OKF representation conformance is also separate from agent behavior.

[Contributor setup](../../CONTRIBUTING.md) · [Consumer installation](../../INSTALL.md)
