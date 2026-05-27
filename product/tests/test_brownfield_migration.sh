#!/usr/bin/env bash
set -euo pipefail
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$TMP"; mkdir -p logs
# Includes an intervening "## Decisions" section between the now-sections and
# Daily Log — the migration must NOT sweep it into STATE (over-capture regression).
cat > logs/DEVLOG.md <<'EOF'
# Development Log
## Current Context
- Version: v1.2.3
## Last Session
- Done: stuff
## Decisions (ADR Index)
- ADR-001: SHOULD_NOT_APPEAR_IN_STATE
## Daily Log
### 2026-01-01: x
EOF
# Run only the migration function (isolated) to keep the test hermetic.
LFG_MIGRATE_ONLY=1 bash "$OLDPWD/product/scripts/update.sh" || true
test -f logs/STATE.md || { echo "STATE.md not created"; exit 1; }
grep -q "v1.2.3" logs/STATE.md || { echo "Current Context not migrated"; exit 1; }
grep -q "Done: stuff" logs/STATE.md || { echo "Last Session not migrated"; exit 1; }
grep -q "SHOULD_NOT_APPEAR_IN_STATE" logs/STATE.md && { echo "FAIL: over-captured intervening section"; exit 1; }
grep -q "2026-01-01" logs/STATE.md && { echo "FAIL: captured Daily Log"; exit 1; }
echo "PASS"
