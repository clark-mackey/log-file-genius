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
    
    # Check for VERSION.json
    version_file = SCRIPT_DIR.parent / 'VERSION.json'
    if version_file.exists():
        import json
        with open(version_file) as f:
            version_data = json.load(f)
        print(f"Version: {version_data.get('version', 'unknown')}")
    
    print("\n" + "="*60)
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
    }
    
    return handlers[args.command](args)


if __name__ == '__main__':
    sys.exit(main())

