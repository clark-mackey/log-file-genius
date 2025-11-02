#!/usr/bin/env bash
# check-for-updates.sh
# Check for Log File Genius updates from GitHub releases

set -e

# Colors
COLOR_SUCCESS='\033[32m'
COLOR_WARNING='\033[33m'
COLOR_ERROR='\033[31m'
COLOR_INFO='\033[36m'
COLOR_RESET='\033[0m'

# GitHub repository
REPO_OWNER="clark-mackey"
REPO_NAME="log-file-genius"
RELEASES_URL="https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"

VERBOSE=false
if [ "$1" = "-v" ] || [ "$1" = "--verbose" ]; then
    VERBOSE=true
fi

echo ""
echo -e "${COLOR_INFO}🔍 Checking for Log File Genius updates...${COLOR_RESET}"
echo ""

# Read current version from config file
CONFIG_FILE=""
CURRENT_VERSION=""

for path in ".logfile-config.yml" "config/logfile.yml" ".config/logfile.yml"; do
    if [ -f "$path" ]; then
        CONFIG_FILE="$path"
        if grep -q "log_file_genius_version:" "$path"; then
            CURRENT_VERSION=$(grep "log_file_genius_version:" "$path" | sed 's/.*"\([0-9.]*\)".*/\1/')
        fi
        break
    fi
done

if [ -z "$CURRENT_VERSION" ]; then
    echo -e "${COLOR_WARNING}⚠️  No .logfile-config.yml found or version not specified${COLOR_RESET}"
    echo -e "${COLOR_WARNING}   Current version: Unknown${COLOR_RESET}"
    echo ""
else
    echo -e "${COLOR_INFO}📦 Current version: v$CURRENT_VERSION${COLOR_RESET}"
    echo ""
fi

# Fetch latest release from GitHub
if [ "$VERBOSE" = true ]; then
    echo -e "${COLOR_INFO}Fetching latest release from GitHub...${COLOR_RESET}"
fi

# Check if curl is available
if ! command -v curl &> /dev/null; then
    echo -e "${COLOR_ERROR}❌ curl is required but not installed${COLOR_RESET}"
    echo ""
    exit 1
fi

# Fetch release data
RESPONSE=$(curl -s "$RELEASES_URL" 2>&1)
if [ $? -ne 0 ]; then
    echo -e "${COLOR_ERROR}❌ Failed to check for updates${COLOR_RESET}"
    echo -e "${COLOR_ERROR}   Error: Could not connect to GitHub${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_INFO}   You can manually check for updates at:${COLOR_RESET}"
    echo -e "${COLOR_INFO}   https://github.com/$REPO_OWNER/$REPO_NAME/releases${COLOR_RESET}"
    echo ""
    exit 1
fi

# Parse JSON response (using grep and sed for portability)
LATEST_VERSION=$(echo "$RESPONSE" | grep '"tag_name"' | head -1 | sed 's/.*"tag_name": "v\?\([^"]*\)".*/\1/')
RELEASE_NAME=$(echo "$RESPONSE" | grep '"name"' | head -1 | sed 's/.*"name": "\([^"]*\)".*/\1/')
RELEASE_URL=$(echo "$RESPONSE" | grep '"html_url"' | head -1 | sed 's/.*"html_url": "\([^"]*\)".*/\1/')
PUBLISHED_AT=$(echo "$RESPONSE" | grep '"published_at"' | head -1 | sed 's/.*"published_at": "\([^"]*\)".*/\1/' | cut -d'T' -f1)

if [ -z "$LATEST_VERSION" ]; then
    echo -e "${COLOR_ERROR}❌ Failed to parse release information${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_INFO}   You can manually check for updates at:${COLOR_RESET}"
    echo -e "${COLOR_INFO}   https://github.com/$REPO_OWNER/$REPO_NAME/releases${COLOR_RESET}"
    echo ""
    exit 1
fi

echo -e "${COLOR_SUCCESS}🌟 Latest version: v$LATEST_VERSION${COLOR_RESET}"
echo -e "${COLOR_INFO}   Release: $RELEASE_NAME${COLOR_RESET}"
echo -e "${COLOR_INFO}   Published: $PUBLISHED_AT${COLOR_RESET}"
echo ""

# Compare versions
if [ -n "$CURRENT_VERSION" ] && [ "$CURRENT_VERSION" = "$LATEST_VERSION" ]; then
    echo -e "${COLOR_SUCCESS}✅ You're up to date!${COLOR_RESET}"
    echo ""
elif [ -n "$CURRENT_VERSION" ]; then
    echo -e "${COLOR_WARNING}🔔 Update available: v$CURRENT_VERSION → v$LATEST_VERSION${COLOR_RESET}"
    echo ""
    echo -e "${COLOR_INFO}📝 Release notes:${COLOR_RESET}"
    echo -e "${COLOR_INFO}   $RELEASE_URL${COLOR_RESET}"
    echo ""
    
    # Show release body (first 500 chars)
    BODY=$(echo "$RESPONSE" | grep '"body"' | head -1 | sed 's/.*"body": "\(.*\)".*/\1/' | sed 's/\\n/\n/g' | head -c 500)
    if [ -n "$BODY" ]; then
        echo -e "${COLOR_INFO}Summary:${COLOR_RESET}"
        echo "$BODY"
        echo ""
    fi
    
    echo -e "${COLOR_INFO}To update:${COLOR_RESET}"
    echo -e "${COLOR_INFO}1. Review release notes: $RELEASE_URL${COLOR_RESET}"
    echo -e "${COLOR_INFO}2. Check migration guide (if provided)${COLOR_RESET}"
    echo -e "${COLOR_INFO}3. Update your .logfile-config.yml version to: $LATEST_VERSION${COLOR_RESET}"
    echo -e "${COLOR_INFO}4. Pull updated files from the repository${COLOR_RESET}"
    echo ""
else
    echo -e "${COLOR_INFO}📝 Latest release:${COLOR_RESET}"
    echo -e "${COLOR_INFO}   $RELEASE_URL${COLOR_RESET}"
    echo ""
fi

exit 0

