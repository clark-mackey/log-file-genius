#!/usr/bin/env bash
# Log File Genius Update Script
# Updates Log File Genius files while preserving user customizations

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Script directory detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(pwd)"

echo -e "${BLUE}===========================================${NC}"
echo -e "${BLUE}|   Log File Genius Update Script       |${NC}"
echo -e "${BLUE}===========================================${NC}"
echo ""

# Helper functions
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

migrate_devlog_to_state() {
    local config=".logfile-config.yml"
    local devlog="logs/DEVLOG.md"
    local state="logs/STATE.md"

    # Resolve paths from config (block-aware: devlog/state appear under paths:),
    # matching how the validators read them. Fall back to logs/.
    if [ -f "$config" ]; then
        local d s
        d=$(awk '/^[A-Za-z_]+:/{inblk=($0 ~ /^paths:/)} inblk && $1=="devlog:"{print $2; exit}' "$config")
        s=$(awk '/^[A-Za-z_]+:/{inblk=($0 ~ /^paths:/)} inblk && $1=="state:"{print $2; exit}' "$config")
        d="${d%\"}"; d="${d#\"}"; d="${d%\'}"; d="${d#\'}"
        s="${s%\"}"; s="${s#\"}"; s="${s%\'}"; s="${s#\'}"
        [ -n "$d" ] && devlog="$d"
        [ -n "$s" ] && state="$s"
    fi

    [ -f "$devlog" ] || return 0
    if ! grep -q "## Current Context" "$devlog"; then return 0; fi
    if [ -f "$state" ]; then
        print_warning "DEVLOG has a legacy Current Context, but STATE.md already exists."
        print_info "Review and move it manually if needed; leaving files unchanged."
        return 0
    fi
    print_info "Migrating DEVLOG Current Context / Last Session into new STATE.md"
    # Capture ONLY the Current Context and Last Session sections (by their own
    # headings), stopping at any other top-level heading — avoids sweeping in
    # intervening sections (e.g. an ADR index) or, when no Daily Log exists,
    # the entire rest of the file.
    {
        echo "# Current State"
        echo ""
        awk '
          /^## (Current Context|Last Session)/ { f=1; print; next }
          /^## / { f=0 }
          f { print }
        ' "$devlog"
    } > "$state"
    print_success "Created STATE from legacy DEVLOG sections at $state (review it)."
}

if [ "${LFG_MIGRATE_ONLY:-0}" = "1" ]; then
    migrate_devlog_to_state
    exit 0
fi

# Check if .log-file-genius exists
if [[ ! -d "$PROJECT_ROOT/.log-file-genius" ]]; then
    print_error "Log File Genius not found!"
    echo ""
    echo "Expected to find .log-file-genius/ in project root."
    echo "Current directory: $PROJECT_ROOT"
    echo ""
    echo "Please run this script from your project root, or install Log File Genius first:"
    echo "  ./.log-file-genius/product/scripts/install.sh"
    exit 1
fi

# Update source repository
print_info "Updating Log File Genius source..."
cd "$PROJECT_ROOT/.log-file-genius"
git fetch origin
CURRENT_COMMIT=$(git rev-parse HEAD)
LATEST_COMMIT=$(git rev-parse origin/main)

if [[ "$CURRENT_COMMIT" == "$LATEST_COMMIT" ]]; then
    print_success "Already up to date ($(git rev-parse --short HEAD))"
    cd "$PROJECT_ROOT"
else
    print_info "Updating from $(git rev-parse --short HEAD) to $(git rev-parse --short origin/main)"
    git pull origin main
    print_success "Source updated"
    cd "$PROJECT_ROOT"
fi

echo ""
print_info "Checking for file updates..."
echo ""

# Detect AI assistant
detect_ai_assistant() {
    if [[ -d "$PROJECT_ROOT/.augment" ]]; then
        echo "augment"
    elif [[ -d "$PROJECT_ROOT/.claude" ]]; then
        echo "claude-code"
    elif [[ -d "$PROJECT_ROOT/.cursor" ]]; then
        echo "cursor"
    else
        echo "unknown"
    fi
}

AI_ASSISTANT=$(detect_ai_assistant)
if [[ "$AI_ASSISTANT" == "unknown" ]]; then
    print_warning "Could not detect AI assistant"
    echo "Skipping AI assistant rules update"
    echo ""
else
    print_info "Detected AI assistant: $AI_ASSISTANT"
fi

# Function to prompt for file update
prompt_update() {
    local file_type="$1"
    local src="$2"
    local dest="$3"
    
    if [[ ! -f "$src" ]]; then
        return 1
    fi
    
    if [[ ! -f "$dest" ]]; then
        # File doesn't exist, just copy it
        print_info "New file available: $file_type"
        return 0
    fi
    
    # Check if files are different
    if diff -q "$src" "$dest" > /dev/null 2>&1; then
        # Files are identical, skip
        return 1
    fi
    
    # Files are different, prompt user
    print_warning "Update available: $file_type"
    echo "  Source: $src"
    echo "  Destination: $dest"
    read -p "  Update this file? (y/N/d=diff): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Dd]$ ]]; then
        # Show diff
        echo ""
        diff -u "$dest" "$src" || true
        echo ""
        read -p "  Apply this update? (y/N): " -n 1 -r
        echo
    fi
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        return 0
    else
        print_info "Skipped: $file_type"
        return 1
    fi
}

# Update AI assistant rules
# Map AI_ASSISTANT to target name in fragment frontmatter.
case "$AI_ASSISTANT" in
    augment)     RULES_TARGET="augment_rules"; RULES_DEST="$PROJECT_ROOT/.augment/rules" ;;
    claude-code) RULES_TARGET="claude_rules";  RULES_DEST="$PROJECT_ROOT/.claude/rules"  ;;
    *)           print_warning "Unknown assistant: $AI_ASSISTANT"; AI_ASSISTANT="unknown" ;;
esac

if [ "$AI_ASSISTANT" != "unknown" ]; then
    mkdir -p "$RULES_DEST"

    # Walk fragments; route by frontmatter `targets`.
    for frag in "$SOURCE_ROOT/product/rules/"*.md; do
        [ -f "$frag" ] || continue
        targets=$(awk '
            /^---$/{count++; if(count==2)exit; next}
            count==1 && /^targets:/{ sub(/^targets:[[:space:]]*/,""); print; exit }
        ' "$frag")
        case ",$(echo "$targets" | tr -d '[] ')," in
            *",$RULES_TARGET,"*)
                fname=$(basename "$frag")
                dest="$RULES_DEST/$fname"
                if prompt_update "Rule: $fname" "$frag" "$dest"; then
                    cp "$frag" "$dest"
                    print_success "Updated: $fname"
                fi
                ;;
        esac
    done

    # Render Claude project_instructions template (claude-code only).
    if [ "$AI_ASSISTANT" = "claude-code" ]; then
        TMPL="$SOURCE_ROOT/product/install-templates/claude/project_instructions.md.tmpl"
        DEST="$PROJECT_ROOT/.claude/project_instructions.md"
        if [ -f "$TMPL" ]; then
            # Render to a temp file so prompt_update can diff against existing.
            RENDERED=$(mktemp)
            sed \
                -e 's|{{paths.changelog}}|logs/CHANGELOG.md|g' \
                -e 's|{{paths.devlog}}|logs/DEVLOG.md|g' \
                -e 's|{{paths.state}}|logs/STATE.md|g' \
                -e 's|{{paths.adr_dir}}|logs/adr/|g' \
                "$TMPL" > "$RENDERED"
            if prompt_update "Claude project_instructions.md" "$RENDERED" "$DEST"; then
                cp "$RENDERED" "$DEST"
                print_success "Updated: project_instructions.md"
            fi
            rm -f "$RENDERED"
        fi
    fi
fi

# Update AGENTS.md at project root via the managed-block merge (Spec 4 §1).
# This REPLACES the old prompt-then-overwrite: a "y" there fully overwrote the
# file (data loss). The merge is strictly safer — it preserves user content,
# only rewrites the LFG block, and is idempotent (no-op on a re-run). The
# merge entrypoint owns read, merge, and atomic write.
LFG_PY="$SOURCE_ROOT/product/scripts/lfg.py"
PYTHON_BIN=""
if command -v python3 > /dev/null 2>&1; then
    PYTHON_BIN="python3"
elif command -v python > /dev/null 2>&1; then
    PYTHON_BIN="python"
fi

if [ -z "$PYTHON_BIN" ]; then
    # No merge possible without Python. NEVER fall back to overwriting.
    print_warning "Python not found; skipping AGENTS.md update (merge requires Python)."
elif [ ! -f "$LFG_PY" ]; then
    print_warning "lfg.py not found at $LFG_PY; skipping AGENTS.md update."
else
    print_info "Merging AGENTS.md (preserves your content, refreshes the LFG block)"
    # Surface the CLI's own output; on non-zero exit warn but keep going.
    if "$PYTHON_BIN" "$LFG_PY" merge-agents-md --to "$PROJECT_ROOT/AGENTS.md"; then
        print_success "AGENTS.md merge complete"
    else
        print_warning "AGENTS.md merge reported a problem (see above); continuing update."
    fi
fi

# Migrate legacy DEVLOG context into STATE.md for existing installs
migrate_devlog_to_state

# Update validation scripts
print_info "Checking validation scripts..."
if prompt_update "validate-log-files.sh" \
    "$SOURCE_ROOT/product/scripts/validate-log-files.sh" \
    "$PROJECT_ROOT/scripts/validate-log-files.sh"; then
    cp "$SOURCE_ROOT/product/scripts/validate-log-files.sh" "$PROJECT_ROOT/scripts/"
    chmod +x "$PROJECT_ROOT/scripts/validate-log-files.sh"
    print_success "Updated: validate-log-files.sh"
fi

if prompt_update "validate-log-files.ps1" \
    "$SOURCE_ROOT/product/scripts/validate-log-files.ps1" \
    "$PROJECT_ROOT/scripts/validate-log-files.ps1"; then
    cp "$SOURCE_ROOT/product/scripts/validate-log-files.ps1" "$PROJECT_ROOT/scripts/"
    print_success "Updated: validate-log-files.ps1"
fi

# Templates are NOT copied to a project-root templates/ dir (Spec 4 §3).
# They live only in .log-file-genius/product/templates/ (the submodule).
# A root templates/ left over from older versions (LFG-installed) is moved
# to backups; a user-authored templates/ is left untouched. We ONLY ever
# inspect "$PROJECT_ROOT/templates" here — never the user's root
# .logfile-config.yml or anything outside that subdir.
ROOT_TEMPLATES="$PROJECT_ROOT/templates"
if [ -d "$ROOT_TEMPLATES" ]; then
    MATCH_HELPER="$SOURCE_ROOT/product/scripts/update_template_hashes.py"
    if [ -z "$PYTHON_BIN" ]; then
        print_warning "Python not found; leaving root templates/ untouched (cannot verify hashes)."
    elif [ ! -f "$MATCH_HELPER" ]; then
        print_warning "Template hash helper not found; leaving root templates/ untouched."
    else
        # --match-dir exit 0 => >=1 file matches an LFG-shipped hash (any version).
        if "$PYTHON_BIN" "$MATCH_HELPER" --match-dir "$ROOT_TEMPLATES" > /dev/null 2>&1; then
            BACKUP_DIR="$PROJECT_ROOT/.log-file-genius/.backups/templates-$(date +%s)"
            mkdir -p "$(dirname "$BACKUP_DIR")"
            # Count files before the move for the message.
            N_FILES=$(find "$ROOT_TEMPLATES" -type f | wc -l | tr -d ' ')
            mv "$ROOT_TEMPLATES" "$BACKUP_DIR"
            print_success "Moved $N_FILES LFG-installed templates to $BACKUP_DIR (they now live in .log-file-genius/product/templates/)."
        else
            print_info "Kept your templates/ (not LFG-installed)."
        fi
    fi
fi

echo ""
echo -e "${GREEN}===========================================${NC}"
echo -e "${GREEN}|   Update Complete! ✓                   |${NC}"
echo -e "${GREEN}===========================================${NC}"
echo ""
print_info "Your Log File Genius installation is up to date!"
echo ""
print_info "Documentation: .log-file-genius/product/docs/"
print_info "Run validation: ./scripts/validate-log-files.sh"
echo ""
