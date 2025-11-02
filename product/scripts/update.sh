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

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Log File Genius Update Script       ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
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
if [[ "$AI_ASSISTANT" != "unknown" ]]; then
    RULES_SRC="$SOURCE_ROOT/product/starter-packs/$AI_ASSISTANT"
    
    if [[ "$AI_ASSISTANT" == "augment" ]]; then
        # Update Augment rules
        for rule_file in "$RULES_SRC/.augment/rules/"*.md; do
            if [[ -f "$rule_file" ]]; then
                rule_name=$(basename "$rule_file")
                dest_file="$PROJECT_ROOT/.augment/rules/$rule_name"
                
                if prompt_update "Augment rule: $rule_name" "$rule_file" "$dest_file"; then
                    mkdir -p "$PROJECT_ROOT/.augment/rules"
                    cp "$rule_file" "$dest_file"
                    print_success "Updated: $rule_name"
                fi
            fi
        done
    elif [[ "$AI_ASSISTANT" == "claude-code" ]]; then
        # Update Claude Code instructions
        if prompt_update "Claude Code instructions" \
            "$RULES_SRC/.claude/project_instructions.md" \
            "$PROJECT_ROOT/.claude/project_instructions.md"; then
            mkdir -p "$PROJECT_ROOT/.claude"
            cp "$RULES_SRC/.claude/project_instructions.md" "$PROJECT_ROOT/.claude/"
            print_success "Updated: project_instructions.md"
        fi
    fi
fi

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

# Update templates (careful - users may have customized these)
print_info "Checking templates..."
print_warning "Note: Templates are often customized. Review changes carefully."
echo ""

for template in "$SOURCE_ROOT/product/templates/"*.md; do
    if [[ -f "$template" ]]; then
        template_name=$(basename "$template")
        dest_template="$PROJECT_ROOT/templates/$template_name"
        
        if prompt_update "Template: $template_name" "$template" "$dest_template"; then
            mkdir -p "$PROJECT_ROOT/templates"
            cp "$template" "$dest_template"
            print_success "Updated: $template_name"
        fi
    fi
done

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Update Complete! ✓                   ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
print_info "Your Log File Genius installation is up to date!"
echo ""
print_info "Documentation: .log-file-genius/product/docs/"
print_info "Run validation: ./scripts/validate-log-files.sh"
echo ""

