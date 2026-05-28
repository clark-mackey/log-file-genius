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
    }

    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

