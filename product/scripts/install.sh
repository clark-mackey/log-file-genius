#!/usr/bin/env bash
# Log File Genius Installer
# Installs Log File Genius from .log-file-genius/ source to your project

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory detection
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
PROJECT_ROOT="$(pwd)"

# Check if running from .log-file-genius/
if [[ ! "$SCRIPT_DIR" =~ \.log-file-genius ]]; then
    echo -e "${YELLOW}⚠️  Warning: This script should be run from .log-file-genius/product/scripts/${NC}"
    echo -e "${YELLOW}   Current location: $SCRIPT_DIR${NC}"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Log File Genius Installer v1.0      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Function to print success
print_success() {
    echo -e "${GREEN}✓${NC} $1"
}

# Function to print error
print_error() {
    echo -e "${RED}✗${NC} $1"
}

# Function to print warning
print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Function to print info
print_info() {
    echo -e "${BLUE}ℹ${NC} $1"
}

# Check for incorrect installation
check_incorrect_installation() {
    if [[ -d "$PROJECT_ROOT/product" ]] || [[ -d "$PROJECT_ROOT/project" ]]; then
        print_error "Detected incorrect installation!"
        echo ""
        echo "Found /product or /project folders in your project root."
        echo "These are meta-directories for building Log File Genius itself."
        echo "They should NOT be in your project."
        echo ""
        echo "Would you like to run the cleanup script to fix this?"
        read -p "Run cleanup? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            bash "$SCRIPT_DIR/cleanup.sh"
            echo ""
            echo "Cleanup complete. Re-run this installer."
            exit 0
        else
            echo "Please manually remove /product and /project folders before continuing."
            exit 1
        fi
    fi
}

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

# Prompt for AI assistant
prompt_ai_assistant() {
    echo -e "${BLUE}Which AI assistant are you using?${NC}"
    echo "1) Augment"
    echo "2) Claude Code"
    echo "3) Cursor (coming soon)"
    echo "4) GitHub Copilot (coming soon)"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1) echo "augment" ;;
        2) echo "claude-code" ;;
        3) echo "cursor" ;;
        4) echo "github-copilot" ;;
        *) echo "augment" ;;  # Default
    esac
}

# Prompt for profile
prompt_profile() {
    echo ""
    echo -e "${BLUE}Which profile fits your project best?${NC}"
    echo "1) solo-developer (default) - Individual developers, flexible"
    echo "2) team - Teams of 2+, consistent documentation"
    echo "3) open-source - Public projects, strict formatting"
    echo "4) startup - MVPs/prototypes, minimal overhead"
    echo ""
    read -p "Enter choice (1-4): " choice
    
    case $choice in
        1) echo "solo-developer" ;;
        2) echo "team" ;;
        3) echo "open-source" ;;
        4) echo "startup" ;;
        *) echo "solo-developer" ;;  # Default
    esac
}

# Copy directory contents
copy_directory_contents() {
    local src="$1"
    local dest="$2"
    
    if [[ ! -d "$src" ]]; then
        print_error "Source directory not found: $src"
        return 1
    fi
    
    mkdir -p "$dest"
    cp -r "$src"/* "$dest/" 2>/dev/null || true
    return 0
}

# Copy file
copy_file() {
    local src="$1"
    local dest="$2"
    
    if [[ ! -f "$src" ]]; then
        print_error "Source file not found: $src"
        return 1
    fi
    
    mkdir -p "$(dirname "$dest")"
    cp "$src" "$dest"
    return 0
}

# Main installation
main() {
    print_info "Starting installation..."
    echo ""
    
    # Check for incorrect installation
    check_incorrect_installation
    
    # Detect or prompt for AI assistant
    AI_ASSISTANT=$(detect_ai_assistant)
    if [[ "$AI_ASSISTANT" == "unknown" ]]; then
        AI_ASSISTANT=$(prompt_ai_assistant)
    else
        print_info "Detected AI assistant: $AI_ASSISTANT"
    fi
    
    # Prompt for profile
    PROFILE=$(prompt_profile)
    print_info "Selected profile: $PROFILE"
    echo ""

    # Prompt for log file locations (brownfield support)
    echo -e "${CYAN}Where should your log files be located?${NC}"
    echo -e "${CYAN}Press Enter to use defaults, or specify custom paths:${NC}"
    echo ""

    read -p "CHANGELOG location [docs/planning/CHANGELOG.md]: " CHANGELOG_PATH
    CHANGELOG_PATH=${CHANGELOG_PATH:-docs/planning/CHANGELOG.md}

    read -p "DEVLOG location [docs/planning/DEVLOG.md]: " DEVLOG_PATH
    DEVLOG_PATH=${DEVLOG_PATH:-docs/planning/DEVLOG.md}

    read -p "ADR directory [docs/adr]: " ADR_PATH
    ADR_PATH=${ADR_PATH:-docs/adr}

    read -p "STATE location [docs/STATE.md]: " STATE_PATH
    STATE_PATH=${STATE_PATH:-docs/STATE.md}

    echo ""
    print_info "Log file paths configured"
    echo ""

    # Determine source paths
    STARTER_PACK_DIR="$SOURCE_ROOT/product/starter-packs/$AI_ASSISTANT"
    TEMPLATES_DIR="$SOURCE_ROOT/product/templates"
    SCRIPTS_DIR="$SOURCE_ROOT/product/scripts"
    
    # Check if starter pack exists
    if [[ ! -d "$STARTER_PACK_DIR" ]]; then
        print_error "Starter pack not found for $AI_ASSISTANT"
        print_info "Available starter packs:"
        ls -1 "$SOURCE_ROOT/product/starter-packs/"
        exit 1
    fi
    
    print_info "Installing from: $STARTER_PACK_DIR"
    echo ""

    # Create log-file-genius folder for all installed files
    INSTALL_FOLDER="$PROJECT_ROOT/log-file-genius"
    mkdir -p "$INSTALL_FOLDER"

    # Install AI assistant configuration (must be at root)
    if [[ "$AI_ASSISTANT" == "augment" ]]; then
        if copy_directory_contents "$STARTER_PACK_DIR/.augment" "$PROJECT_ROOT/.augment"; then
            print_success "Installed Augment rules"
        fi
    elif [[ "$AI_ASSISTANT" == "claude-code" ]]; then
        if copy_directory_contents "$STARTER_PACK_DIR/.claude" "$PROJECT_ROOT/.claude"; then
            print_success "Installed Claude Code configuration"
        fi
    fi

    # Install templates to log-file-genius/templates/
    if copy_directory_contents "$TEMPLATES_DIR" "$INSTALL_FOLDER/templates"; then
        print_success "Installed templates"
    fi

    # Install validation scripts to log-file-genius/scripts/
    mkdir -p "$INSTALL_FOLDER/scripts"
    if copy_file "$SCRIPTS_DIR/validate-log-files.sh" "$INSTALL_FOLDER/scripts/validate-log-files.sh"; then
        chmod +x "$INSTALL_FOLDER/scripts/validate-log-files.sh"
        print_success "Installed validation script (Bash)"
    fi
    if copy_file "$SCRIPTS_DIR/validate-log-files.ps1" "$INSTALL_FOLDER/scripts/validate-log-files.ps1"; then
        print_success "Installed validation script (PowerShell)"
    fi

    # Install profile configuration (at root)
    if copy_file "$STARTER_PACK_DIR/.logfile-config.yml" "$PROJECT_ROOT/.logfile-config.yml"; then
        # Update profile and add paths in config file
        if command -v sed &> /dev/null; then
            sed -i.bak "s/profile: .*/profile: $PROFILE/" "$PROJECT_ROOT/.logfile-config.yml"
            rm -f "$PROJECT_ROOT/.logfile-config.yml.bak"
        fi

        # Add paths section
        cat >> "$PROJECT_ROOT/.logfile-config.yml" << EOF

installation:
  folder: log-file-genius

paths:
  changelog: $CHANGELOG_PATH
  devlog: $DEVLOG_PATH
  adr: $ADR_PATH
  state: $STATE_PATH
EOF
        print_success "Installed profile configuration ($PROFILE)"
    fi

    # Install git hooks to log-file-genius/git-hooks/
    if [[ -d "$STARTER_PACK_DIR/.git-hooks" ]]; then
        copy_directory_contents "$STARTER_PACK_DIR/.git-hooks" "$INSTALL_FOLDER/git-hooks"
        print_success "Installed git hook templates"
        echo ""
        print_info "To enable git hooks, run:"
        echo "  cp log-file-genius/git-hooks/pre-commit .git/hooks/pre-commit"
        echo "  chmod +x .git/hooks/pre-commit"
    fi
    
    echo ""
    echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║   Installation Complete!               ║${NC}"
    echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
    echo ""
    print_info "Next steps:"
    echo "  1. Initialize your log files from templates:"
    echo "     cp log-file-genius/templates/CHANGELOG_template.md docs/planning/CHANGELOG.md"
    echo "     cp log-file-genius/templates/DEVLOG_template.md docs/planning/DEVLOG.md"
    echo "     cp log-file-genius/templates/ADR_template.md docs/adr/ADR-template.md"
    echo ""
    echo "  2. Customize templates in log-file-genius/templates/ if needed"
    echo ""
    echo "  3. Start using your AI assistant - it will automatically maintain logs!"
    echo ""
    print_info "Documentation: .log-file-genius/product/docs/"
    print_info "Run validation: ./log-file-genius/scripts/validate-log-files.sh"
    echo ""
}

# Run main
main "$@"

