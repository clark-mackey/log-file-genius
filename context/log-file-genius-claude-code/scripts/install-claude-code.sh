#!/bin/bash
# Claude Code Installation Module for Log File Genius
# Add this to product/scripts/install.sh

install_claude_code() {
    echo "🤖 Installing Claude Code support..."
    
    local TEMPLATE_DIR="${SCRIPT_DIR}/../templates/.claude"
    local TARGET_DIR=".claude"
    
    # Create .claude directory structure
    mkdir -p "${TARGET_DIR}/commands"
    mkdir -p "${TARGET_DIR}/rules"
    
    # Copy CLAUDE.md to project root
    if [ ! -f "CLAUDE.md" ]; then
        cp "${SCRIPT_DIR}/../templates/CLAUDE.md" "CLAUDE.md"
        echo "  ✅ Created CLAUDE.md"
    else
        echo "  ⚠️  CLAUDE.md already exists, skipping"
    fi
    
    # Copy slash commands
    for cmd in devlog-entry changelog-entry adr-create state-update; do
        if [ ! -f "${TARGET_DIR}/commands/${cmd}.md" ]; then
            cp "${TEMPLATE_DIR}/commands/${cmd}.md" "${TARGET_DIR}/commands/"
            echo "  ✅ Installed /project:${cmd} command"
        fi
    done
    
    # Copy rules
    for rule in logging handoff-protocol; do
        if [ ! -f "${TARGET_DIR}/rules/${rule}.md" ]; then
            cp "${TEMPLATE_DIR}/rules/${rule}.md" "${TARGET_DIR}/rules/"
            echo "  ✅ Installed ${rule} rules"
        fi
    done
    
    # Copy hooks (with backup if exists)
    if [ -f "${TARGET_DIR}/hooks.json" ]; then
        cp "${TARGET_DIR}/hooks.json" "${TARGET_DIR}/hooks.json.backup"
        echo "  ⚠️  Backed up existing hooks.json"
    fi
    cp "${TEMPLATE_DIR}/hooks.json" "${TARGET_DIR}/"
    echo "  ✅ Installed hooks.json"
    
    echo "✅ Claude Code support installed!"
    echo ""
    echo "Available slash commands:"
    echo "  /project:devlog-entry    - Add narrative entry"
    echo "  /project:changelog-entry - Add factual entry"
    echo "  /project:adr-create      - Create decision record"
    echo "  /project:state-update    - Update project state"
}

detect_claude_code() {
    # Check for Claude Code CLI
    if command -v claude &> /dev/null; then
        return 0
    fi
    
    # Check for existing .claude directory
    if [ -d ".claude" ]; then
        return 0
    fi
    
    # Check for Claude Code config in home
    if [ -d "${HOME}/.claude" ]; then
        return 0
    fi
    
    return 1
}

# Add to main installer detection logic:
# if detect_claude_code; then
#     install_claude_code
# fi
