#!/usr/bin/env bash
# Check for Unicode characters that may cause encoding issues
# Usage: ./check-unicode.sh [--fix]

set -euo pipefail

FIX=false
if [[ "${1:-}" == "--fix" ]]; then
    FIX=true
fi

# Unicode characters to check for (with ASCII replacements)
declare -A unicode_chars=(
    ["→"]="->"
    ["←"]="<-"
    ["↑"]="^"
    ["↓"]="v"
    ["•"]="-"
    ["✓"]="[OK]"
    ["✗"]="[X]"
    ["⚠"]="[WARNING]"
    ["ℹ"]="[INFO]"
)

# Files to check (relative to repo root)
files_to_check=(
    "logs/CHANGELOG.md"
    "logs/DEVLOG.md"
    "logs/ai-usage-log.md"
    "logs/adr/"*.md
    "logs/archive/"*.md
    "README.md"
    "INSTALL.md"
    "product/docs/"*.md
    "product/templates/"*.md
)

echo "Checking for Unicode characters that may cause encoding issues..."
echo ""

issues_found=0
files_checked=0

for pattern in "${files_to_check[@]}"; do
    # Expand glob pattern
    for file in $pattern; do
        if [[ ! -f "$file" ]]; then
            continue
        fi
        
        ((files_checked++))
        
        file_issues=()
        for char in "${!unicode_chars[@]}"; do
            if grep -q "$char" "$file" 2>/dev/null; then
                count=$(grep -o "$char" "$file" | wc -l)
                file_issues+=("$count x '$char'")
            fi
        done
        
        if [[ ${#file_issues[@]} -gt 0 ]]; then
            echo "  $file: ${file_issues[*]}"
            ((issues_found++))
            
            if [[ "$FIX" == "true" ]]; then
                # Create backup
                cp "$file" "$file.bak"
                
                # Replace Unicode characters
                for char in "${!unicode_chars[@]}"; do
                    replacement="${unicode_chars[$char]}"
                    # Use sed with proper escaping
                    sed -i "s/$char/$replacement/g" "$file"
                done
                
                echo "    [FIXED] Replaced Unicode characters"
                rm "$file.bak"
            fi
        fi
    done
done

echo ""

if [[ $issues_found -eq 0 ]]; then
    echo "[OK] No problematic Unicode characters found in $files_checked files!"
    exit 0
fi

if [[ "$FIX" == "true" ]]; then
    echo "[OK] Fixed Unicode characters in $issues_found file(s)!"
else
    echo "Found Unicode characters in $issues_found file(s)."
    echo ""
    echo "To automatically fix these issues, run:"
    echo "  ./product/scripts/check-unicode.sh --fix"
    echo ""
    echo "Note: Some Unicode characters (like • in navigation) may be intentional."
    echo "Review changes before committing!"
fi

exit 0

