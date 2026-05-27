#!/usr/bin/env bash
set -euo pipefail
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT
cd "$TMP"
mkdir -p logs alt
# Quoted path + trailing comment exercise quote-stripping and comment tolerance.
cat > .logfile-config.yml <<'EOF'
paths:
  changelog: "alt/CHANGELOG.md"
  devlog: alt/DEVLOG.md
token_targets:
  changelog: 9000  # tight
  devlog: 13000
EOF
printf '# x\n' > alt/CHANGELOG.md
printf '# x\n' > alt/DEVLOG.md

cp "$OLDPWD/product/scripts/validate-log-files.sh" ./vlf.sh
OUT="$(bash ./vlf.sh --print-config)"
echo "$OUT" | grep -q "CHANGELOG_PATH=alt/CHANGELOG.md" || { echo "path not read"; exit 1; }
echo "$OUT" | grep -q "CHANGELOG_TOKEN_ERROR=9000" || { echo "token not read"; exit 1; }
echo "$OUT" | grep -q "CHANGELOG_TOKEN_WARNING=7200" || { echo "warning not 80%"; exit 1; }
echo "PASS"
