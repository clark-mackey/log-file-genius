#!/usr/bin/env python3
"""
Log File Genius - Unified CLI

Single entry point for all LFG operations, reducing PowerShell/Bash duplication.
Shell scripts become thin wrappers that call this Python script.

Usage:
    python lfg.py validate [--changelog] [--devlog] [--tokens] [--verbose] [--json]
    python lfg.py lint [files...] [--json]
    python lfg.py secrets [paths...] [--strict] [--json]
    python lfg.py check-version [--update]
    python lfg.py check-rules [--rules-dir DIR] [--json]
    python lfg.py status

Exit codes:
    0 - Success
    1 - Warnings
    2 - Errors
    3 - Self-test failed
"""

import argparse
import importlib.util
import sys
from pathlib import Path

# Add scripts directory to path for imports
SCRIPT_DIR = Path(__file__).parent
sys.path.insert(0, str(SCRIPT_DIR))


def import_module(name: str):
    """Import a module by file path (handles hyphenated names)"""
    file_path = SCRIPT_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace('-', '_'), file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cmd_validate(args):
    """Run validation on log files"""
    lint_logs = import_module('lint-logs')

    # Build arguments for lint-logs
    sys.argv = ['lint-logs']
    if args.changelog:
        sys.argv.append('--changelog-only')
    if args.devlog:
        sys.argv.append('--devlog-only')
    if getattr(args, 'state_only', False):
        # STATE-only mode: validate STATE.md alone so callers (e.g.
        # update.{sh,ps1}) can detect a STATE-specific failure without
        # false-positiving on CHANGELOG/DEVLOG issues. Exits 2 iff STATE.md
        # has errors (e.g. missing '## Current Context'); budget warnings
        # stay exit 0 unless --strict is also passed through lint-logs.
        sys.argv.append('--state')
    if args.verbose:
        sys.argv.append('--verbose')
    if args.json:
        sys.argv.append('--json')

    return lint_logs.main()


def cmd_lint(args):
    """Run the linter on specific files"""
    lint_logs = import_module('lint-logs')

    sys.argv = ['lint-logs'] + args.files
    if args.json:
        sys.argv.append('--json')

    return lint_logs.main()


def cmd_secrets(args):
    """Run secret detection"""
    detect_secrets = import_module('detect-secrets')

    sys.argv = ['detect-secrets'] + (args.paths or ['logs/'])
    if args.strict:
        sys.argv.append('--strict')
    if args.json:
        sys.argv.append('--json')
    if args.allowlist:
        sys.argv.extend(['--allowlist', args.allowlist])

    return detect_secrets.main()


def cmd_check_version(args):
    """Check version synchronization"""
    check_version = import_module('check-version')

    sys.argv = ['check-version']
    if args.update:
        sys.argv.append('--update')

    return check_version.main()


def cmd_check_rules(args):
    """Check AI rules for conflicts"""
    check_ai_rules = import_module('check-ai-rules')

    sys.argv = ['check-ai-rules']
    if args.rules_dir:
        sys.argv.extend(['--rules-dir', args.rules_dir])
    if args.json:
        sys.argv.append('--json')

    return check_ai_rules.main()


def cmd_status(args):
    """Show project status"""
    print("\n" + "="*60)
    print("Log File Genius - Status")
    print("="*60)

    # Check for log files
    logs_dir = Path('logs')
    changelog = logs_dir / 'CHANGELOG.md'
    devlog = logs_dir / 'DEVLOG.md'

    print(f"\nLog files:")
    print(f"  CHANGELOG: {'✓' if changelog.exists() else '✗'} {changelog}")
    print(f"  DEVLOG:    {'✓' if devlog.exists() else '✗'} {devlog}")

    # Check for config
    config_paths = ['.logfile-config.yml', 'config/logfile.yml']
    config_found = None
    for p in config_paths:
        if Path(p).exists():
            config_found = p
            break
    print(f"\nConfig: {config_found or 'Using defaults'}")

    # Check for pre-commit hook
    hook_path = Path('.git/hooks/pre-commit')
    print(f"Pre-commit hook: {'✓ installed' if hook_path.exists() else '✗ not installed'}")

    # Check for VERSION.json
    version_file = SCRIPT_DIR.parent / 'VERSION.json'
    if version_file.exists():
        import json
        with open(version_file) as f:
            version_data = json.load(f)
        print(f"Version: {version_data.get('version', 'unknown')}")

    print("\n" + "="*60)
    return 0


def cmd_generate(args):
    """Regenerate product/AGENTS.md from rules fragments"""
    from generator import parse_fragment, render_agents_md, GeneratorError
    rules_dir = Path(__file__).resolve().parent.parent / "rules"
    if not rules_dir.is_dir():
        print(f"ERROR: rules dir not found at {rules_dir}", file=sys.stderr)
        return 2

    fragments = []
    for p in sorted(rules_dir.glob("*.md")):
        try:
            fragments.append(parse_fragment(p))
        except GeneratorError as e:
            print(f"ERROR: {p.name}: {e}", file=sys.stderr)
            return 2

    try:
        rendered = render_agents_md(fragments)
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    # Default output: product/AGENTS.md, unless --out specified.
    default_out = Path(__file__).resolve().parent.parent / "AGENTS.md"
    out_path = Path(args.out) if getattr(args, "out", None) else default_out

    if getattr(args, "check", False):
        existing = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        if existing == rendered:
            return 0
        print(f"DRIFT: {out_path} would change after `lfg generate`.", file=sys.stderr)
        print("Run `python product/scripts/lfg.py generate` and commit the result.",
              file=sys.stderr)
        return 1

    # Write with explicit LF + UTF-8, no BOM.
    out_path.write_bytes(rendered.encode("utf-8"))
    tokens = len(rendered) // 4
    from generator import AGENTS_TOKEN_BUDGET
    print(f"Wrote {out_path} ({tokens} tokens, budget {AGENTS_TOKEN_BUDGET})")
    return 0


def cmd_merge_agents_md(args):
    """Merge the canonical managed block into a target AGENTS.md (brownfield-safe).

    Builds the marker-wrapped block from the rules fragments (same loading path
    as cmd_generate), then merges it into the target via agents_merge, preserving
    any surrounding user content. Idempotent: re-running on an up-to-date file
    writes nothing.
    """
    import agents_merge
    import generator
    from generator import parse_fragment, GeneratorError

    rules_dir = Path(__file__).resolve().parent.parent / "rules"
    if not rules_dir.is_dir():
        print(f"ERROR: rules dir not found at {rules_dir}", file=sys.stderr)
        return 2

    fragments = []
    for p in sorted(rules_dir.glob("*.md")):
        try:
            fragments.append(parse_fragment(p))
        except GeneratorError as e:
            print(f"ERROR: {p.name}: {e}", file=sys.stderr)
            return 2

    try:
        running_version = generator.read_repo_version()
        block = generator.render_block(fragments, version=running_version)
    except GeneratorError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 2

    existing = agents_merge.read_text_normalized(args.to)

    # Pre-merge visibility (SHOULD-FIX 4): inspect `existing` read-only to tell
    # the user WHICH merge case will apply before we write. Especially the wrap
    # case (old LFG body replaced) and the prepend case (user content kept).
    # This does not change merge_into_existing's behavior or return type.
    begin_match = agents_merge.LFG_BEGIN_RE.search(existing)
    has_begin = begin_match is not None
    end_idx = existing.find(agents_merge.LFG_END_LIT)
    has_valid_block = has_begin and end_idx != -1 and end_idx > begin_match.end()
    if not existing.strip():
        print(f"No existing AGENTS.md; creating managed block at {args.to}.")
    elif has_begin and not has_valid_block:
        # Corrupt half-marker — say nothing positive; the error path handles it.
        pass
    elif has_begin:
        print(f"Existing AGENTS.md has an LFG managed block; refreshing it in place: {args.to}")
    elif not args.no_wrap and agents_merge.looks_like_lfg(existing):
        print("Existing AGENTS.md matched LFG content; regenerated managed block "
              "(previous body replaced).")
    else:
        print("Existing AGENTS.md preserved; LFG block prepended above your content.")

    try:
        merged = agents_merge.merge_into_existing(
            existing or None,
            block,
            running_version,
            allow_wrap=not args.no_wrap,
            force_downgrade=args.force_downgrade,
        )
    except agents_merge.ForwardVersionError:
        # Re-extract the captured version for a precise message.
        match = agents_merge.LFG_BEGIN_RE.search(existing)
        captured = match.group("ver") if match else "?"
        print(
            f"ERROR: AGENTS.md at {args.to} was managed by a newer LFG "
            f"(v{captured}). Re-run with --force-downgrade to overwrite.",
            file=sys.stderr,
        )
        return 2
    except agents_merge.CorruptMarkerError:
        # Half-broken managed block (BEGIN with no valid END). We refuse rather
        # than risk emitting a second BEGIN marker that a later merge would
        # mis-slice. This errors regardless of --no-wrap — the user must repair
        # the file by hand (ASCII-only message for cross-platform consoles).
        print(
            f"ERROR: AGENTS.md at {args.to} has an LFG:BEGIN marker but no "
            f"valid END marker (corrupt). Fix it manually, then re-run.",
            file=sys.stderr,
        )
        return 2

    # Idempotency short-circuit: compare against the normalized on-disk content.
    if merged == existing:
        print(f"AGENTS.md already up to date (no change): {args.to}")
        return 0

    agents_merge.atomic_write(args.to, merged)
    print(f"Updated {args.to}")
    return 0


def cmd_prime(args):
    """Emit a subagent context digest (STATE + last N CHANGELOG entries)."""
    from primer import build_prime
    if args.n < 1:
        print(f"ERROR: --n must be >= 1 (got {args.n})", file=sys.stderr)
        return 2
    out = build_prime(project_root=Path.cwd(), n=args.n, as_json=args.json)
    # STATE/CHANGELOG content can include non-ASCII (emoji in templates,
    # Unicode in entries). On Windows, the console default is cp1252, so
    # `print()` raises UnicodeEncodeError. Write UTF-8 bytes directly to
    # bypass the encoding layer.
    sys.stdout.buffer.write(out.encode("utf-8"))
    sys.stdout.buffer.write(b"\n")
    return 0


def cmd_promote(args):
    """Promote a subagent's staged entries into canonical CHANGELOG/DEVLOG."""
    from promoter import promote
    return promote(Path.cwd(), args.subagent_id)


def cmd_archive(args):
    """Build an ArchivePlan and (if not --dry-run) apply it after confirmation."""
    if args.state or args.adr:
        if args.state:
            sys.stderr.buffer.write(
                "STATE files don't archive -- STATE is a snapshot, not a ledger. "
                "Trim or overwrite it directly. See product/docs/log_file_how_to.md.\n"
                .encode("utf-8")
            )
        if args.adr:
            sys.stderr.buffer.write(
                "ADRs don't archive -- they remain referenceable forever. "
                "See product/docs/log_file_how_to.md.\n"
                .encode("utf-8")
            )
        return 2

    from archive import build_plan, apply, ArchiveError
    include_changelog = True
    include_devlog = True
    if args.changelog and not args.devlog:
        include_devlog = False
    elif args.devlog and not args.changelog:
        include_changelog = False

    plan = build_plan(
        project_root=Path.cwd(),
        include_changelog=include_changelog,
        include_devlog=include_devlog,
    )

    # Stream the human-readable plan to stdout (UTF-8 bytes — matches cmd_prime).
    sys.stdout.buffer.write(plan.to_human().encode("utf-8"))
    sys.stdout.buffer.write(b"\n")

    if plan.refusal_reasons and not plan.actions:
        return 2

    if args.dry_run or plan.is_empty():
        return 0

    if not args.force:
        try:
            reply = input("Apply this archive plan? [y/N] ").strip().lower()
        except EOFError:
            reply = ""
        if reply not in ("y", "yes"):
            print("Aborted.", file=sys.stderr)
            return 1

    try:
        apply(plan)
    except ArchiveError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 3
    print(f"Applied {len(plan.actions)} archive action(s).")
    return 0


def cmd_migrate_state(args):
    """Build a STATE migration plan and (if not --dry-run) apply it.

    Mirrors cmd_archive: resolve config + STATE/DEVLOG paths, build the plan,
    stream it to stdout, then either dry-run (write nothing), prompt+apply, or
    --force-apply. The two MigrateError guards (already-compliant/empty plan, or
    already-migrated snapshot in DEVLOG) are NOT failures — they're no-ops, so
    they print a clear ASCII message and return 0.

    today's date is sourced here at the CLI layer (the pure planner/apply never
    calls datetime.now() — same convention archive.py uses for timestamps).
    """
    import migrate_state
    from config_parser import parse_config

    project_root = Path.cwd()
    config_path = project_root / ".logfile-config.yml"
    cfg = parse_config(str(config_path))
    paths = cfg.get("paths", {})

    state_path = project_root / paths.get("state", "logs/STATE.md")
    devlog_path = project_root / paths.get("devlog", "logs/DEVLOG.md")

    if not state_path.exists():
        print(f"ERROR: STATE.md not found at {state_path}", file=sys.stderr)
        return 2

    state_content = migrate_state.read_text_normalized(state_path)
    plan = migrate_state.build_plan(state_content, cfg)

    # Stream the human-readable plan to stdout (UTF-8 bytes — matches cmd_archive).
    sys.stdout.buffer.write(plan.to_human().encode("utf-8"))
    sys.stdout.buffer.write(b"\n")

    if args.dry_run:
        return 0

    if not args.force:
        try:
            reply = input("Apply this migration plan? [y/N] ").strip().lower()
        except EOFError:
            reply = ""
        if reply not in ("y", "yes"):
            print("Aborted.", file=sys.stderr)
            return 1

    from datetime import datetime
    today = datetime.now().strftime("%Y-%m-%d")

    try:
        migrate_state.apply(
            plan,
            state_path=state_path,
            devlog_path=devlog_path,
            today=today,
            config_path=config_path,
        )
    except migrate_state.MigrateError as e:
        # Guard trips (already-compliant/empty plan, or already-migrated) are
        # no-ops, not failures: print a clear ASCII message and exit 0.
        print(str(e).replace("—", "--"))
        return 0

    print(f"Applied STATE migration ({state_path.name} rewritten).")
    return 0


def cmd_install_hooks(args):
    """Install git pre-commit hooks"""
    import shutil

    hook_source = SCRIPT_DIR / 'pre-commit'
    hook_dest = Path('.git/hooks/pre-commit')

    if not Path('.git').exists():
        print("[X] Error: Not a git repository")
        return 2

    if not hook_source.exists():
        print(f"[X] Error: Hook source not found: {hook_source}")
        return 2

    # Check for existing hook
    if hook_dest.exists() and not args.force:
        print(f"[!] Pre-commit hook already exists: {hook_dest}")
        print("    Use --force to overwrite")
        return 1

    # Create hooks directory if needed
    hook_dest.parent.mkdir(parents=True, exist_ok=True)

    # Copy hook
    shutil.copy2(hook_source, hook_dest)

    # Make executable (Unix only)
    try:
        import os
        os.chmod(hook_dest, 0o755)
    except:
        pass  # Windows doesn't need this

    print(f"[OK] Pre-commit hook installed: {hook_dest}")
    print("     Runs: secret detection + log validation")
    print("     Mode: warn-only (set LFG_STRICT=1 to block)")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description='Log File Genius - Unified CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # validate command
    p_validate = subparsers.add_parser('validate', help='Validate log files')
    p_validate.add_argument('--changelog', action='store_true', help='Only validate CHANGELOG')
    p_validate.add_argument('--devlog', action='store_true', help='Only validate DEVLOG')
    p_validate.add_argument('--state-only', dest='state_only', action='store_true',
                            help='Only validate STATE (non-zero exit iff STATE has errors)')
    p_validate.add_argument('--tokens', action='store_true', help='Only check token counts')
    p_validate.add_argument('--verbose', action='store_true', help='Verbose output')
    p_validate.add_argument('--json', action='store_true', help='JSON output')
    
    # lint command
    p_lint = subparsers.add_parser('lint', help='Lint specific files')
    p_lint.add_argument('files', nargs='*', default=[], help='Files to lint')
    p_lint.add_argument('--json', action='store_true', help='JSON output')
    
    # secrets command
    p_secrets = subparsers.add_parser('secrets', help='Detect secrets')
    p_secrets.add_argument('paths', nargs='*', help='Paths to scan')
    p_secrets.add_argument('--strict', action='store_true', help='Treat warnings as errors')
    p_secrets.add_argument('--json', action='store_true', help='JSON output')
    p_secrets.add_argument('--allowlist', help='Path to allowlist file')
    
    # check-version command
    p_version = subparsers.add_parser('check-version', help='Check version sync')
    p_version.add_argument('--update', action='store_true', help='Update checksums')
    
    # check-rules command  
    p_rules = subparsers.add_parser('check-rules', help='Check AI rules for conflicts')
    p_rules.add_argument('--rules-dir', help='Directory containing rules')
    p_rules.add_argument('--json', action='store_true', help='JSON output')
    
    # status command
    subparsers.add_parser('status', help='Show project status')

    # install-hooks command
    p_hooks = subparsers.add_parser('install-hooks', help='Install git pre-commit hooks')
    p_hooks.add_argument('--force', action='store_true', help='Overwrite existing hook')

    # generate command
    p_gen = subparsers.add_parser('generate', help='Regenerate AGENTS.md from fragments')
    p_gen.add_argument('--check', action='store_true',
                       help='Exit non-zero if AGENTS.md would change (CI mode)')
    p_gen.add_argument('--out', help='Write to a non-default path (testing)')

    # prime command
    p_prime = subparsers.add_parser('prime', help='Emit a subagent context digest')
    p_prime.add_argument('--n', type=int, default=5,
                         help='Number of CHANGELOG Unreleased entries to include (default 5)')
    p_prime.add_argument('--json', action='store_true', help='JSON output')

    # promote command
    p_prom = subparsers.add_parser(
        'promote', help="Promote a subagent's staged entries into canonical CHANGELOG/DEVLOG")
    p_prom.add_argument('subagent_id',
                        help='Subagent id matching the .lfg/staged/<id>/ directory')

    # archive command
    p_arch = subparsers.add_parser(
        'archive',
        help="Archive old CHANGELOG version blocks and DEVLOG entries (deterministic, work-aware)")
    p_arch.add_argument('--dry-run', action='store_true',
                        help='Show the plan but write nothing (default if no flag)')
    p_arch.add_argument('--force', action='store_true',
                        help='Skip the confirmation prompt')
    p_arch.add_argument('--changelog', action='store_true',
                        help='Scope to CHANGELOG only')
    p_arch.add_argument('--devlog', action='store_true',
                        help='Scope to DEVLOG only')
    p_arch.add_argument('--state', action='store_true',
                        help='(rejected) STATE does not archive')
    p_arch.add_argument('--adr', action='store_true',
                        help='(rejected) ADRs do not archive')

    # migrate-state command
    p_migrate = subparsers.add_parser(
        'migrate-state',
        help="Bring a brownfield STATE.md into the current spec (deterministic, previewable)")
    p_migrate.add_argument('--dry-run', action='store_true',
                           help='Show the plan but write nothing')
    p_migrate.add_argument('--force', action='store_true',
                           help='Skip the confirmation prompt')

    # merge-agents-md command
    p_merge = subparsers.add_parser(
        'merge-agents-md',
        help="Merge the canonical managed block into a target AGENTS.md (brownfield-safe)")
    p_merge.add_argument('--to', required=True,
                         help='Path to the target AGENTS.md (created if absent)')
    p_merge.add_argument('--no-wrap', action='store_true',
                         help='Prepend the block instead of wrapping pre-marker LFG content')
    p_merge.add_argument('--force-downgrade', action='store_true',
                         help='Overwrite a block managed by a newer LFG version')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    # Dispatch to command handler
    handlers = {
        'validate': cmd_validate,
        'lint': cmd_lint,
        'secrets': cmd_secrets,
        'check-version': cmd_check_version,
        'check-rules': cmd_check_rules,
        'status': cmd_status,
        'install-hooks': cmd_install_hooks,
        'generate': cmd_generate,
        'prime': cmd_prime,
        'promote': cmd_promote,
        'archive': cmd_archive,
        'migrate-state': cmd_migrate_state,
        'merge-agents-md': cmd_merge_agents_md,
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

