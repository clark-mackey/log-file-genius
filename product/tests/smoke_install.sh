#!/usr/bin/env bash
# product/tests/smoke_install.sh
# Cross-platform installer smoke test (bash).
# Asserts a fresh install produces the expected files, config blocks,
# frontmatter, AGENTS.md (LF + no BOM), and that the installed rule equals
# the canonical fragment (install==update parity).
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

# Spec 2: AGENTS.md must land at project root.
test -f AGENTS.md || { echo "FAIL: AGENTS.md missing at project root"; exit 1; }
head -1 AGENTS.md | grep -q '^---$' || { echo "FAIL: AGENTS.md missing frontmatter"; exit 1; }

# Spec 2: AGENTS.md must be LF + no BOM (generator's documented contract).
if grep -q $'\r' AGENTS.md; then echo "FAIL: AGENTS.md has CRLF line endings"; exit 1; fi
head -c 3 AGENTS.md | grep -q $'\xEF\xBB\xBF' && { echo "FAIL: AGENTS.md has UTF-8 BOM"; exit 1; } || true

# Spec 2: installed rule must equal the canonical fragment.
diff -q .claude/rules/log-file-maintenance.md \
    "$REPO/product/rules/log-file-maintenance.md" \
    || { echo "FAIL: installed rule != canonical fragment"; exit 1; }

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
