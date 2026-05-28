#!/usr/bin/env bash
# Log File Genius Installer (Bash)
# Installs Log File Genius to your project with standard /logs/ structure
#
# Usage:
#   install.sh [--profile <profile>] [--ai-assistant <augment|claude-code>] [--force]
#
# Options:
#   --profile        Profile to use (solo-developer, team, open-source, startup)
#   --ai-assistant   AI assistant to install rules for (augment, claude-code)
#   --force          Skip confirmation prompts (validation still runs)

set -e

# ============================================================================
# CONFIGURATION
# ============================================================================

VERSION="0.2.0"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PROJECT_ROOT="$(pwd)"

# Track created items for rollback
CREATED_ITEMS=()

PROFILE=""
AI_ASSISTANT=""
FORCE=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --help|-h)
            echo "Log File Genius Installer v$VERSION"
            echo ""
            echo "Usage: install.sh [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --profile <name>       Profile to use (solo-developer, team, open-source, startup)"
            echo "  --ai-assistant <name>  AI assistant (augment, claude-code)"
            echo "  --force                Skip confirmation prompts"
            echo "  --help, -h             Show this help message"
            echo ""
            echo "Examples:"
            echo "  install.sh --profile solo-developer --force"
            echo "  install.sh --ai-assistant augment"
            exit 0
            ;;
        --profile)
            PROFILE="$2"
            shift 2
            ;;
        --ai-assistant)
            AI_ASSISTANT="$2"
            shift 2
            ;;
        --force)
            FORCE=true
            shift
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

print_success() {
    echo -e "\033[0;32m[OK]\033[0m $1"
}

print_error() {
    echo -e "\033[0;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[0;33m[WARNING]\033[0m $1"
}

print_info() {
    echo -e "\033[0;36m[INFO]\033[0m $1"
}

rollback_installation() {
    local reason="$1"

    print_error "Installation failed: $reason"

    if [ ${#CREATED_ITEMS[@]} -gt 0 ]; then
        print_warning "Rolling back changes..."

        for item in "${CREATED_ITEMS[@]}"; do
            if [ -e "$item" ]; then
                rm -rf "$item" 2>/dev/null || true
                print_info "Removed $item"
            fi
        done

        print_success "Rollback complete"
    fi

    exit 1
}

# ============================================================================
# BANNER
# ============================================================================

echo ""
echo "â•”â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•—"
echo "â•‘   Log File Genius Installer v$VERSION      â•‘"
echo "â•šâ•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•â•"
echo ""

# ============================================================================
# DETECT AI ASSISTANT
# ============================================================================

if [ -z "$AI_ASSISTANT" ]; then
    print_info "Detecting AI assistant..."
    
    if [ -d ".augment" ]; then
        AI_ASSISTANT="augment"
        print_success "Detected Augment"
    elif [ -d ".claude" ]; then
        AI_ASSISTANT="claude-code"
        print_success "Detected Claude Code"
    else
        echo ""
        echo "Which AI assistant are you using?"
        echo "  1) Augment"
        echo "  2) Claude Code"
        echo ""
        read -p "Enter choice (1-2): " choice
        
        case $choice in
            1) AI_ASSISTANT="augment" ;;
            2) AI_ASSISTANT="claude-code" ;;
            *)
                print_error "Invalid choice. Exiting."
                exit 1
                ;;
        esac
    fi
fi

# ============================================================================
# SELECT PROFILE
# ============================================================================

if [ -z "$PROFILE" ]; then
    echo ""
    echo "Select your project profile:"
    echo "  1) solo-developer  - Individual developers (flexible, minimal overhead)"
    echo "  2) team            - Teams of 2+ developers (consistent docs)"
    echo "  3) open-source     - Public projects (strict formatting)"
    echo "  4) startup         - Fast-moving startups (minimal overhead)"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1) PROFILE="solo-developer" ;;
        2) PROFILE="team" ;;
        3) PROFILE="open-source" ;;
        4) PROFILE="startup" ;;
        *)
            print_error "Invalid choice. Exiting."
            exit 1
            ;;
    esac
fi

print_success "Profile: $PROFILE"
print_success "AI Assistant: $AI_ASSISTANT"

# ============================================================================
# CHECK FOR EXISTING INSTALLATION
# ============================================================================

if [ -d "logs" ] || [ -f ".logfile-config.yml" ]; then
    echo ""
    print_warning "Existing installation detected!"
    [ -d "logs" ] && print_warning "  - logs/ folder exists"
    [ -f ".logfile-config.yml" ] && print_warning "  - .logfile-config.yml exists"
    echo ""
    
    if [ "$FORCE" != "true" ]; then
        read -p "Continue and overwrite? (y/N): " continue
        if [ "$continue" != "y" ] && [ "$continue" != "Y" ]; then
            print_info "Installation cancelled."
            exit 0
        fi
    fi
fi

# ============================================================================
# CREATE LOGS FOLDER STRUCTURE
# ============================================================================

echo ""
print_info "Creating /logs/ folder structure..."

mkdir -p logs/adr
mkdir -p logs/incidents
CREATED_ITEMS+=("logs")

print_success "Created logs/"
print_success "Created logs/adr/"
print_success "Created logs/incidents/"

# ============================================================================
# COPY TEMPLATES TO /logs/
# ============================================================================

print_info "Copying log file templates..."

# Template mappings (Bash 3.2 compatible - no associative arrays)
# Format: "source_path:destination_path"
TEMPLATE_MAPPINGS=(
    "templates/CHANGELOG_template.md:logs/CHANGELOG.md"
    "templates/DEVLOG_template.md:logs/DEVLOG.md"
    "templates/STATE_template.md:logs/STATE.md"
    "templates/ADR_template.md:logs/adr/TEMPLATE.md"
)

TEMPLATE_ERRORS=()

for mapping in "${TEMPLATE_MAPPINGS[@]}"; do
    # Split "source:dest" using parameter expansion (Bash 3.2+ compatible)
    # ${var%%:*} = everything before first ':'
    # ${var##*:} = everything after last ':'
    source_rel="${mapping%%:*}"
    dest="${mapping##*:}"
    source="$SOURCE_ROOT/$source_rel"

    if [ -f "$source" ]; then
        if cp "$source" "$dest" 2>/dev/null; then
            CREATED_ITEMS+=("$dest")
            print_success "Copied $dest"
        else
            print_error "Failed to copy: $source"
            TEMPLATE_ERRORS+=("$source")
        fi
    else
        print_error "Template not found: $source"
        TEMPLATE_ERRORS+=("$source")
    fi
done

if [ ${#TEMPLATE_ERRORS[@]} -gt 0 ]; then
    rollback_installation "Missing template files"
fi

# ============================================================================
# INSTALL AI RULES
# ============================================================================

print_info "Installing AI assistant rules..."

# Map AI_ASSISTANT to its rules-dir target name in fragment frontmatter.
case "$AI_ASSISTANT" in
    augment)     RULES_TARGET="augment_rules"; RULES_DEST="$PROJECT_ROOT/.augment/rules" ;;
    claude-code) RULES_TARGET="claude_rules";  RULES_DEST="$PROJECT_ROOT/.claude/rules"  ;;
    *)           rollback_installation "Unknown assistant: $AI_ASSISTANT" ;;
esac

mkdir -p "$RULES_DEST"
CREATED_ITEMS+=("$RULES_DEST")

# Walk fragments; copy each whose `targets` includes our RULES_TARGET.
for frag in "$SOURCE_ROOT/rules/"*.md; do
    [ -f "$frag" ] || continue
    # Pull the `targets:` line from the YAML frontmatter (between the first two '---' lines).
    targets=$(awk '
        /^---$/{count++; if(count==2)exit; next}
        count==1 && /^targets:/{ sub(/^targets:[[:space:]]*/,""); print; exit }
    ' "$frag")
    case ",$(echo "$targets" | tr -d '[] ')," in
        *",$RULES_TARGET,"*)
            cp "$frag" "$RULES_DEST/$(basename "$frag")"
            CREATED_ITEMS+=("$RULES_DEST/$(basename "$frag")")
            print_success "Installed $(basename "$frag")"
            ;;
    esac
done

# Render Claude project_instructions template (if installing for claude-code).
if [ "$AI_ASSISTANT" = "claude-code" ]; then
    TMPL="$SOURCE_ROOT/install-templates/claude/project_instructions.md.tmpl"
    DEST="$PROJECT_ROOT/.claude/project_instructions.md"
    # Substitute {{paths.X}} tokens. Defaults match Spec 1's canonical.
    sed \
        -e 's|{{paths.changelog}}|logs/CHANGELOG.md|g' \
        -e 's|{{paths.devlog}}|logs/DEVLOG.md|g' \
        -e 's|{{paths.state}}|logs/STATE.md|g' \
        -e 's|{{paths.adr_dir}}|logs/adr/|g' \
        "$TMPL" > "$DEST"
    CREATED_ITEMS+=("$DEST")
    print_success "Rendered .claude/project_instructions.md"
fi

# Drop AGENTS.md at the project root for tools that read it natively.
# Strip CRLF in case the source was checked out on Windows with autocrlf — the
# generator's contract is LF-only, and tools shouldn't see a mixed-line-ending
# file just because of where the user cloned the repo.
if [ -f "$SOURCE_ROOT/AGENTS.md" ]; then
    tr -d '\r' < "$SOURCE_ROOT/AGENTS.md" > "$PROJECT_ROOT/AGENTS.md"
    CREATED_ITEMS+=("$PROJECT_ROOT/AGENTS.md")
    print_success "Installed AGENTS.md at project root"
fi

# ============================================================================
# CREATE CONFIG FILE
# ============================================================================

print_info "Creating .logfile-config.yml..."

cat > .logfile-config.yml << EOF
# Log File Genius Configuration
# All log files are in /logs/ folder (standard structure)

log_file_genius_version: "$VERSION"
profile: $PROFILE
ai_assistant: $AI_ASSISTANT

paths:
  changelog: logs/CHANGELOG.md
  devlog: logs/DEVLOG.md
  state: logs/STATE.md
  adr_dir: logs/adr/

token_targets:
  changelog: 10000
  devlog: 15000
  combined: 25000
  state: 500

# Presets and customization: .log-file-genius/product/profiles/*.yml
EOF

CREATED_ITEMS+=(".logfile-config.yml")
print_success "Created .logfile-config.yml"

# ============================================================================
# VALIDATION
# ============================================================================

echo ""
print_info "Validating installation..."

ERRORS=()

[ ! -f "logs/CHANGELOG.md" ] && ERRORS+=("logs/CHANGELOG.md missing")
[ ! -f "logs/DEVLOG.md" ] && ERRORS+=("logs/DEVLOG.md missing")
[ ! -f "logs/STATE.md" ] && ERRORS+=("logs/STATE.md missing")
[ ! -f ".logfile-config.yml" ] && ERRORS+=(".logfile-config.yml missing")

if [ "$AI_ASSISTANT" = "augment" ] && [ ! -f ".augment/rules/log-file-maintenance.md" ]; then
    ERRORS+=(".augment/rules/log-file-maintenance.md missing")
fi

if [ "$AI_ASSISTANT" = "claude-code" ] && [ ! -f ".claude/rules/log-file-maintenance.md" ]; then
    ERRORS+=(".claude/rules/log-file-maintenance.md missing")
fi

if [ ${#ERRORS[@]} -gt 0 ]; then
    print_error "Installation validation failed:"
    for error in "${ERRORS[@]}"; do
        print_error "  - $error"
    done
    rollback_installation "Validation failed"
fi

print_success "Installation validated successfully!"

# ============================================================================
# SUCCESS MESSAGE
# ============================================================================

echo ""
echo "==================================="
echo "   Installation Complete!"
echo "==================================="
echo ""
print_success "Log files installed to: logs/"

# Display correct AI rules path based on assistant
if [ "$AI_ASSISTANT" = "augment" ]; then
    print_success "AI rules installed to: .augment/rules/"
elif [ "$AI_ASSISTANT" = "claude-code" ]; then
    print_success "AI rules installed to: .claude/rules/"
fi

print_success "Config file: .logfile-config.yml"
echo ""
echo "-----------------------------------"
echo "NEXT STEP: Document this installation"
echo "-----------------------------------"
echo ""
echo "Copy and paste this prompt to your AI assistant:"
echo ""
echo "\"I just installed Log File Genius. Please:"
echo " 1. Update CHANGELOG.md with what was installed"
echo " 2. Update DEVLOG.md with why we installed it"
echo " 3. Create an ADR documenting the architectural decision"
echo "    to adopt Log File Genius for project documentation\""
echo ""
echo "This will:"
echo "  - Show you how the system works"
echo "  - Create your first log entries"
echo "  - Document the architectural decision"
echo "  - Validate that AI rules are working"
echo ""
print_info "Documentation: .log-file-genius/product/docs/log_file_how_to.md"
echo ""

