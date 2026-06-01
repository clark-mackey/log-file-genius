#!/usr/bin/env bash
# product/tests/smoke_update.sh
# Cross-platform UPDATE smoke test (bash) — Spec 4 brownfield-safe update.
#
# The full update.sh requires a real .log-file-genius/ git submodule and does a
# `git fetch` against origin — too heavy and network-dependent for a smoke test.
# So we exercise the SPECIFIC new behaviors update.sh performs, using the exact
# same entrypoints update.sh calls:
#   - AGENTS.md merge:      lfg.py merge-agents-md --to <path>   (Spec 4 §1)
#   - root templates/ move: update_template_hashes.py --match-dir + the
#                           backup-move shell logic from update.sh             (Spec 4 §3)
#
# Scenarios (mirror the "test_update_smoke" Test-plan row in SPEC-04):
#   1. v0.3.0 AGENTS.md (doc: AGENTS frontmatter, NO markers) -> update WRAPS it
#      (markers added, canonical body regenerated).
#   2. LFG-installed root templates/ (real product template, hash in manifest)
#      -> moved to .log-file-genius/.backups/templates-*/ (root gone, backup exists).
#   3. USER-authored AGENTS.md (no doc: AGENTS, custom sentinel) -> block PREPENDED
#      above; user content + sentinel preserved.
#   4. USER-authored root templates/ (file whose hash is NOT in the manifest)
#      -> LEFT in place (not moved).
#   5. Notepad-style v0.3.0 AGENTS.md (CRLF + UTF-8 BOM, no markers) -> update
#      wraps it; output normalized to LF + no-BOM, markers detected.
#   6. Repeated merge on an up-to-date managed file is a byte-identical no-op.
set -euo pipefail

REPO="$(cd "$(dirname "$0")/../.." && pwd)"
LFG_PY="$REPO/product/scripts/lfg.py"
MATCH_HELPER="$REPO/product/scripts/update_template_hashes.py"

PYTHON_BIN=""
if command -v python3 >/dev/null 2>&1; then PYTHON_BIN="python3";
elif command -v python >/dev/null 2>&1; then PYTHON_BIN="python"; fi
if [ -z "$PYTHON_BIN" ]; then echo "FAIL: python not found (required for merge)"; exit 1; fi

fail() { echo "FAIL: $1"; exit 1; }

# Mirror update.sh's backup-move block (Spec 4 §3). Given a project root, decide
# whether root templates/ is LFG-installed (>=1 hash matches the manifest) and
# move it to .log-file-genius/.backups/templates-<unixtime>/ if so.
move_lfg_templates() {
    local project_root="$1"
    local root_templates="$project_root/templates"
    [ -d "$root_templates" ] || return 0
    if "$PYTHON_BIN" "$MATCH_HELPER" --match-dir "$root_templates" >/dev/null 2>&1; then
        local backup_dir="$project_root/.log-file-genius/.backups/templates-$(date +%s)-$RANDOM"
        mkdir -p "$(dirname "$backup_dir")"
        mv "$root_templates" "$backup_dir"
        echo "$backup_dir"
    fi
    return 0
}

# ---------------------------------------------------------------------------
# Scenario 1: v0.3.0 AGENTS.md (no markers, doc: AGENTS) -> wrapped on update.
# ---------------------------------------------------------------------------
TMP1="$(mktemp -d)"; trap 'rm -rf "$TMP1"' EXIT
git -C "$REPO" show v0.3.0:product/AGENTS.md > "$TMP1/AGENTS.md"
grep -q 'LFG:BEGIN' "$TMP1/AGENTS.md" && fail "v0.3.0 fixture unexpectedly already has markers"
"$PYTHON_BIN" "$LFG_PY" merge-agents-md --to "$TMP1/AGENTS.md" >/dev/null
grep -q '<!-- LFG:BEGIN v' "$TMP1/AGENTS.md" || fail "scenario 1: BEGIN marker not added after wrap"
grep -q '<!-- LFG:END -->' "$TMP1/AGENTS.md" || fail "scenario 1: END marker not added after wrap"
grep -q '^doc: AGENTS$' "$TMP1/AGENTS.md" || fail "scenario 1: canonical body (doc: AGENTS) not present after wrap"
[ "$(grep -c 'LFG:BEGIN' "$TMP1/AGENTS.md")" = "1" ] || fail "scenario 1: more than one BEGIN marker"
echo "  ok scenario 1: v0.3.0 AGENTS.md wrapped"

# ---------------------------------------------------------------------------
# Scenario 2: LFG-installed root templates/ -> moved to backups.
# ---------------------------------------------------------------------------
TMP2="$(mktemp -d)"; trap 'rm -rf "$TMP1" "$TMP2"' EXIT
mkdir -p "$TMP2/.log-file-genius" "$TMP2/templates"
# Copy a real shipped template so its SHA-256 is in the manifest.
cp "$REPO/product/templates/CHANGELOG_template.md" "$TMP2/templates/CHANGELOG_template.md"
BACKUP="$(move_lfg_templates "$TMP2")"
[ -d "$TMP2/templates" ] && fail "scenario 2: root templates/ still present (should have been moved)"
[ -n "$BACKUP" ] || fail "scenario 2: no backup dir reported"
[ -d "$BACKUP" ] || fail "scenario 2: backup dir does not exist: $BACKUP"
[ -f "$BACKUP/CHANGELOG_template.md" ] || fail "scenario 2: backed-up template missing"
case "$BACKUP" in
    "$TMP2/.log-file-genius/.backups/templates-"*) : ;;
    *) fail "scenario 2: backup not under .log-file-genius/.backups/: $BACKUP" ;;
esac
echo "  ok scenario 2: LFG-installed root templates/ moved to backups"

# ---------------------------------------------------------------------------
# Scenario 3: USER-authored AGENTS.md (no doc: AGENTS) -> block PREPENDED above.
# ---------------------------------------------------------------------------
TMP3="$(mktemp -d)"; trap 'rm -rf "$TMP1" "$TMP2" "$TMP3"' EXIT
SENTINEL="USER_SENTINEL_4f3a9b_KEEP_ME"
printf '# My Project Agent Notes\n\n%s — custom team instructions.\n' "$SENTINEL" > "$TMP3/AGENTS.md"
"$PYTHON_BIN" "$LFG_PY" merge-agents-md --to "$TMP3/AGENTS.md" >/dev/null
grep -q "$SENTINEL" "$TMP3/AGENTS.md" || fail "scenario 3: user sentinel lost (data loss!)"
grep -q '<!-- LFG:BEGIN v' "$TMP3/AGENTS.md" || fail "scenario 3: BEGIN marker not prepended"
grep -q '<!-- LFG:END -->' "$TMP3/AGENTS.md" || fail "scenario 3: END marker missing"
# Block must come ABOVE the user content.
BEGIN_LINE="$(grep -n 'LFG:BEGIN' "$TMP3/AGENTS.md" | head -1 | cut -d: -f1)"
SENT_LINE="$(grep -n "$SENTINEL" "$TMP3/AGENTS.md" | head -1 | cut -d: -f1)"
[ "$BEGIN_LINE" -lt "$SENT_LINE" ] || fail "scenario 3: block not prepended above user content"
echo "  ok scenario 3: user-authored AGENTS.md preserved, block prepended above"

# ---------------------------------------------------------------------------
# Scenario 4: USER-authored root templates/ (hash NOT in manifest) -> LEFT alone.
# ---------------------------------------------------------------------------
TMP4="$(mktemp -d)"; trap 'rm -rf "$TMP1" "$TMP2" "$TMP3" "$TMP4"' EXIT
mkdir -p "$TMP4/.log-file-genius" "$TMP4/templates"
printf 'my own template content — not shipped by LFG %s\n' "$RANDOM" > "$TMP4/templates/my_template.md"
BACKUP4="$(move_lfg_templates "$TMP4")"
[ -d "$TMP4/templates" ] || fail "scenario 4: user templates/ was moved (should be left in place!)"
[ -f "$TMP4/templates/my_template.md" ] || fail "scenario 4: user template file disappeared"
[ -z "$BACKUP4" ] || fail "scenario 4: a backup was created for user-authored templates"
[ -d "$TMP4/.log-file-genius/.backups" ] && fail "scenario 4: a backups dir was created for user templates"
echo "  ok scenario 4: user-authored root templates/ left in place"

# ---------------------------------------------------------------------------
# Scenario 5: Notepad-style v0.3.0 AGENTS.md (CRLF + UTF-8 BOM, no markers).
# Update must wrap it AND normalize output to LF + no-BOM, markers detected.
# (This is the realistic brownfield path: v0.3.0 had no markers.)
# ---------------------------------------------------------------------------
TMP5="$(mktemp -d)"; trap 'rm -rf "$TMP1" "$TMP2" "$TMP3" "$TMP4" "$TMP5"' EXIT
git -C "$REPO" show v0.3.0:product/AGENTS.md > "$TMP5/lf.md"
# Re-encode as UTF-8 BOM + CRLF (simulating a Notepad save on Windows).
"$PYTHON_BIN" - "$TMP5/lf.md" "$TMP5/AGENTS.md" <<'PY'
import sys
src, dst = sys.argv[1], sys.argv[2]
text = open(src, "rb").read().decode("utf-8")
crlf = text.replace("\n", "\r\n")
open(dst, "wb").write(b"\xef\xbb\xbf" + crlf.encode("utf-8"))
PY
# Count CR (0x0D) bytes reliably via python — git-bash grep treats CR as a line
# terminator and won't match it on a CRLF file, so byte-counting is the only
# trustworthy check here.
cr_count() { "$PYTHON_BIN" -c "import sys; sys.stdout.write(str(open(sys.argv[1],'rb').read().count(b'\r')))" "$1"; }
has_bom()  { head -c 3 "$1" | grep -q $'\xEF\xBB\xBF'; }
# Sanity: the fixture really has a BOM and CR bytes before the merge.
has_bom "$TMP5/AGENTS.md" || fail "scenario 5: fixture missing BOM"
[ "$(cr_count "$TMP5/AGENTS.md")" -gt 0 ] || fail "scenario 5: fixture missing CRLF"
"$PYTHON_BIN" "$LFG_PY" merge-agents-md --to "$TMP5/AGENTS.md" >/dev/null
grep -q '<!-- LFG:BEGIN v' "$TMP5/AGENTS.md" || fail "scenario 5: markers not detected/added"
# Output normalized: no BOM, no CR.
has_bom "$TMP5/AGENTS.md" && fail "scenario 5: BOM not stripped on write" || true
[ "$(cr_count "$TMP5/AGENTS.md")" = "0" ] || fail "scenario 5: CRLF not normalized to LF"
echo "  ok scenario 5: Notepad CRLF+BOM v0.3.0 file wrapped and normalized"

# ---------------------------------------------------------------------------
# Scenario 6: repeated merge on an up-to-date managed file is a no-op.
# ---------------------------------------------------------------------------
BEFORE6="$(cksum < "$TMP1/AGENTS.md")"
OUT6="$("$PYTHON_BIN" "$LFG_PY" merge-agents-md --to "$TMP1/AGENTS.md" 2>&1)"
echo "$OUT6" | grep -qi 'up to date' || fail "scenario 6: re-merge did not report up-to-date: $OUT6"
AFTER6="$(cksum < "$TMP1/AGENTS.md")"
[ "$BEFORE6" = "$AFTER6" ] || fail "scenario 6: re-merge changed the file (not idempotent)"
echo "  ok scenario 6: repeated merge is a byte-identical no-op"

echo "PASS (bash)"
