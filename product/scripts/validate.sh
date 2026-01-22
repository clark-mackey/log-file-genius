#!/bin/bash
#
# Log File Genius - Validation Script (thin wrapper)
#
# Calls the unified Python CLI for validation.
# This is a thin wrapper to maintain Bash compatibility.
#
# Usage:
#   ./validate.sh              # Run all validations
#   ./validate.sh --changelog  # Run only CHANGELOG validation
#   ./validate.sh --devlog     # Run only DEVLOG validation
#   ./validate.sh --tokens     # Run only token count validation
#   ./validate.sh --verbose    # Show detailed output
#   ./validate.sh --json       # JSON output
#

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LFG_PATH="$SCRIPT_DIR/lfg.py"

python3 "$LFG_PATH" validate "$@"
exit $?

