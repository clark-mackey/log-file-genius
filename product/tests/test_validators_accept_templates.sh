#!/usr/bin/env bash
set -euo pipefail
REPO="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$TMP"; mkdir -p logs logs/adr
# Lay down the canonical templates as a real install would.
cp "$REPO/product/templates/CHANGELOG_template.md" logs/CHANGELOG.md
cp "$REPO/product/templates/DEVLOG_template.md" logs/DEVLOG.md
cp "$REPO/product/templates/STATE_template.md" logs/STATE.md
cat > .logfile-config.yml <<'EOF'
paths:
  changelog: logs/CHANGELOG.md
  devlog: logs/DEVLOG.md
  state: logs/STATE.md
token_targets:
  changelog: 10000
  devlog: 15000
  state: 500
EOF

FAIL=0

# The shell validator must NOT error on the canonical DEVLOG (no Current Context there).
# Check exit code (2 = error) rather than grepping output to avoid ANSI/word false-positives.
if bash "$REPO/product/scripts/validate-log-files.sh" --devlog 2>&1; then
    echo "PASS: shell validator accepts canonical DEVLOG template"
else
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" -ge 2 ]; then
        echo "FAIL: shell validator rejects canonical DEVLOG template (exit $EXIT_STATUS)"
        bash "$REPO/product/scripts/validate-log-files.sh" --devlog 2>&1 || true
        FAIL=1
    else
        echo "PASS: shell validator accepts canonical DEVLOG template (warnings only, exit $EXIT_STATUS)"
    fi
fi

# The shell validator must recognize the canonical STATE (has Current Context + required fields).
if bash "$REPO/product/scripts/validate-log-files.sh" --state 2>&1; then
    echo "PASS: shell validator accepts canonical STATE template"
else
    EXIT_STATUS=$?
    if [ "$EXIT_STATUS" -ge 2 ]; then
        echo "FAIL: shell validator rejects canonical STATE template (exit $EXIT_STATUS)"
        bash "$REPO/product/scripts/validate-log-files.sh" --state 2>&1 || true
        FAIL=1
    else
        echo "PASS: shell validator accepts canonical STATE template (warnings only, exit $EXIT_STATUS)"
    fi
fi

if [ "$FAIL" -eq 1 ]; then
    exit 1
fi
echo "PASS"
