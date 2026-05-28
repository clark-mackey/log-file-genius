#!/usr/bin/env bash
# product/tests/smoke_install.sh
# Cross-platform installer smoke test (bash).
# Asserts a fresh install produces the expected files, config blocks, and
# frontmatter, and that the installed rule equals the canonical ai-rules source
# (install==update parity).
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
cd "$TMP"; mkdir .claude

# Simulate the submodule layout the scripts expect.
# install.sh resolves SOURCE_ROOT as "$SCRIPT_DIR/.." — so when we invoke the
# real repo script directly, SOURCE_ROOT becomes $REPO/product and templates +
# ai-rules are sourced from the real repo.  No copy needed; just run it.
bash "$REPO/product/scripts/install.sh" \
    --profile solo-developer \
    --ai-assistant claude-code \
    --force >/dev/null

# --- File existence ---
for f in logs/CHANGELOG.md logs/DEVLOG.md logs/STATE.md .logfile-config.yml \
         .claude/rules/log-file-maintenance.md; do
    test -f "$f" || { echo "FAIL: missing $f"; exit 1; }
done
test -d logs/adr || { echo "FAIL: missing logs/adr"; exit 1; }

# --- Config blocks ---
grep -q "^paths:" .logfile-config.yml      || { echo "FAIL: no paths block"; exit 1; }
grep -q "^token_targets:" .logfile-config.yml || { echo "FAIL: no token_targets block"; exit 1; }

# --- Frontmatter ---
head -1 logs/CHANGELOG.md | grep -q '^---$' || { echo "FAIL: CHANGELOG.md missing frontmatter"; exit 1; }

# --- install==canonical parity ---
# update.sh does a git fetch/pull so we can't run it end-to-end in a temp dir.
# Instead: verify the installed rule is byte-for-byte identical to the
# canonical ai-rules source, and that update.sh sources from ai-rules (not
# starter-packs).
diff -q .claude/rules/log-file-maintenance.md \
    "$REPO/product/ai-rules/claude-code/log-file-maintenance.md" \
    || { echo "FAIL: installed rule != canonical ai-rules source"; exit 1; }

grep -q 'product/ai-rules/\$AI_ASSISTANT' "$REPO/product/scripts/update.sh" \
    || { echo "FAIL: update.sh does not source from ai-rules"; exit 1; }

if grep -q 'starter-packs' "$REPO/product/scripts/update.sh"; then
    echo "FAIL: update.sh still references starter-packs"; exit 1
fi

# --- Validator exits 0 on a fresh install ---
# Mirrors what CI runs (`validate-log-files.sh --verbose` after install). The
# STATE template legitimately warns (over budget until guidance is trimmed);
# in default mode warnings must be non-blocking — anything else breaks CI.
bash "$REPO/product/scripts/validate-log-files.sh" --verbose >/dev/null 2>&1 \
    || { echo "FAIL: validator exits non-zero on a clean install (CI regression)"; exit 1; }

echo "PASS (bash)"
