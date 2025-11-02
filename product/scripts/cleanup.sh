#!/usr/bin/env bash
# Log File Genius Cleanup Script
# Removes incorrectly installed /product and /project folders

set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_ROOT="$(pwd)"

echo -e "${BLUE}╔════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║   Log File Genius Cleanup Script      ║${NC}"
echo -e "${BLUE}╚════════════════════════════════════════╝${NC}"
echo ""

# Check if product or project folders exist
if [[ ! -d "$PROJECT_ROOT/product" ]] && [[ ! -d "$PROJECT_ROOT/project" ]]; then
    echo -e "${GREEN}✓${NC} No incorrect installation detected."
    echo "Your project looks clean!"
    exit 0
fi

echo -e "${YELLOW}⚠${NC} Detected incorrect installation:"
[[ -d "$PROJECT_ROOT/product" ]] && echo "  - /product folder found"
[[ -d "$PROJECT_ROOT/project" ]] && echo "  - /project folder found"
echo ""
echo "These folders are meta-directories for building Log File Genius itself."
echo "They should NOT be in your project root."
echo ""

# Show what will be removed
echo -e "${BLUE}The following will be removed:${NC}"
[[ -d "$PROJECT_ROOT/product" ]] && echo "  - $PROJECT_ROOT/product/"
[[ -d "$PROJECT_ROOT/project" ]] && echo "  - $PROJECT_ROOT/project/"
echo ""

# Confirm
read -p "Proceed with cleanup? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Remove folders
if [[ -d "$PROJECT_ROOT/product" ]]; then
    rm -rf "$PROJECT_ROOT/product"
    echo -e "${GREEN}✓${NC} Removed /product folder"
fi

if [[ -d "$PROJECT_ROOT/project" ]]; then
    rm -rf "$PROJECT_ROOT/project"
    echo -e "${GREEN}✓${NC} Removed /project folder"
fi

echo ""
echo -e "${GREEN}╔════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║   Cleanup Complete! ✓                  ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}ℹ${NC} Next steps:"
echo "  1. Ensure .log-file-genius/ submodule is properly installed"
echo "  2. Run the installer: ./.log-file-genius/product/scripts/install.sh"
echo ""

