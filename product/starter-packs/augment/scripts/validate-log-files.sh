#!/bin/bash
#
# Log File Genius - Validation Script (Bash)
#
# Validates CHANGELOG.md and DEVLOG.md files for format and token counts.
# Uses only standard Unix tools (grep, wc, awk, sed) - no dependencies.
#
# Usage:
#   ./scripts/validate-log-files.sh              # Run all validations
#   ./scripts/validate-log-files.sh --changelog  # Run only CHANGELOG validation
#   ./scripts/validate-log-files.sh --devlog     # Run only DEVLOG validation
#   ./scripts/validate-log-files.sh --tokens     # Run only token count validation
#   ./scripts/validate-log-files.sh --verbose    # Show detailed output
#
# Exit codes:
#   0 = Success (all checks passed)
#   1 = Warning (non-blocking, commit allowed)
#   2 = Error (blocking, commit prevented)
#

# Configuration
CHANGELOG_PATH="docs/planning/CHANGELOG.md"
DEVLOG_PATH="docs/planning/DEVLOG.md"
CHANGELOG_TOKEN_WARNING=8000
CHANGELOG_TOKEN_ERROR=10000
DEVLOG_TOKEN_WARNING=12000
DEVLOG_TOKEN_ERROR=15000
COMBINED_TOKEN_WARNING=20000
COMBINED_TOKEN_ERROR=25000

# Exit codes
EXIT_SUCCESS=0
EXIT_WARNING=1
EXIT_ERROR=2

# Validation results
PASSED=0
WARNINGS=0
ERRORS=0

# Parse command-line arguments
RUN_CHANGELOG=false
RUN_DEVLOG=false
RUN_TOKENS=false
VERBOSE=false

for arg in "$@"; do
    case $arg in
        --changelog) RUN_CHANGELOG=true ;;
        --devlog) RUN_DEVLOG=true ;;
        --tokens) RUN_TOKENS=true ;;
        --verbose) VERBOSE=true ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--changelog] [--devlog] [--tokens] [--verbose]"
            exit 1
            ;;
    esac
done

# If no specific validation flags, run all
if [ "$RUN_CHANGELOG" = false ] && [ "$RUN_DEVLOG" = false ] && [ "$RUN_TOKENS" = false ]; then
    RUN_CHANGELOG=true
    RUN_DEVLOG=true
    RUN_TOKENS=true
fi

# Helper functions
write_validation_result() {
    local name=$1
    local status=$2
    local message=$3
    
    case $status in
        PASSED)
            echo -e "\033[32m[OK] $name validation: PASSED${message:+ - $message}\033[0m"
            ((PASSED++))
            ;;
        WARNING)
            echo -e "\033[33m[!] $name validation: WARNING${message:+ - $message}\033[0m"
            ((WARNINGS++))
            ;;
        ERROR)
            echo -e "\033[31m[X] $name validation: ERROR${message:+ - $message}\033[0m"
            ((ERRORS++))
            ;;
    esac
}

get_token_count() {
    local file_path=$1
    
    if [ ! -f "$file_path" ]; then
        echo 0
        return
    fi
    
    # Count words and estimate tokens (word_count * 1.3)
    local word_count=$(wc -w < "$file_path")
    local token_estimate=$(awk "BEGIN {print int($word_count * 1.3 + 0.5)}")
    
    echo "$token_estimate"
}

get_percentage() {
    local current=$1
    local target=$2
    
    awk "BEGIN {print int(($current / $target) * 100 + 0.5)}"
}

# CHANGELOG Validation
validate_changelog() {
    if [ "$VERBOSE" = true ]; then
        echo -e "\n\033[36m=== CHANGELOG Validation ===\033[0m"
    fi
    
    # Check file exists
    if [ ! -f "$CHANGELOG_PATH" ]; then
        write_validation_result "CHANGELOG" "ERROR" "File not found: $CHANGELOG_PATH"
        return
    fi
    
    local errors=()

    # Check for Unreleased section
    if ! grep -q "^## \[Unreleased\]" "$CHANGELOG_PATH"; then
        errors+=("Missing '## [Unreleased]' section")
    fi

    # Check for at least one category
    local categories=("Added" "Changed" "Fixed" "Deprecated" "Removed" "Security")
    local has_category=false
    for category in "${categories[@]}"; do
        if grep -q "^### $category" "$CHANGELOG_PATH"; then
            has_category=true
            break
        fi
    done

    if [ "$has_category" = false ]; then
        errors+=("Missing at least one category (Added, Changed, Fixed, Deprecated, Removed, Security)")
    fi
    
    # Check date format (YYYY-MM-DD)
    local invalid_dates=$(grep -E "^## \[[0-9]" "$CHANGELOG_PATH" | grep -v -E "\[[0-9]{4}-[0-9]{2}-[0-9]{2}\]" || true)
    if [ -n "$invalid_dates" ]; then
        errors+=("Invalid date format (expected YYYY-MM-DD)")
        if [ "$VERBOSE" = true ]; then
            echo -e "\033[31m  Invalid dates found:\033[0m"
            echo "$invalid_dates" | while read -r line; do
                echo -e "\033[31m  $line\033[0m"
            done
        fi
    fi
    
    # Report results
    if [ ${#errors[@]} -eq 0 ]; then
        write_validation_result "CHANGELOG" "PASSED"
    else
        write_validation_result "CHANGELOG" "ERROR" "${#errors[@]} issue(s) found"
        if [ "$VERBOSE" = true ]; then
            for error in "${errors[@]}"; do
                echo -e "\033[31m  - $error\033[0m"
            done
        fi
    fi
}

# DEVLOG Validation
validate_devlog() {
    if [ "$VERBOSE" = true ]; then
        echo -e "\n\033[36m=== DEVLOG Validation ===\033[0m"
    fi
    
    # Check file exists
    if [ ! -f "$DEVLOG_PATH" ]; then
        write_validation_result "DEVLOG" "ERROR" "File not found: $DEVLOG_PATH"
        return
    fi
    
    local errors=()
    
    # Check for Current Context section
    if ! grep -q "^## Current Context" "$DEVLOG_PATH"; then
        errors+=("Missing '## Current Context' section")
    fi
    
    # Check for Daily Log section
    if ! grep -q "^## Daily Log" "$DEVLOG_PATH"; then
        errors+=("Missing '## Daily Log' section")
    fi
    
    # Check for required fields in Current Context
    local required_fields=("Version" "Active Branch" "Phase")
    for field in "${required_fields[@]}"; do
        if ! grep -q "\*\*$field" "$DEVLOG_PATH"; then
            errors+=("Missing required field in Current Context: $field")
        fi
    done
    
    # Check entry date format (### YYYY-MM-DD: Title)
    local invalid_entries=$(grep -E "^### [0-9]" "$DEVLOG_PATH" | grep -v -E "^### [0-9]{4}-[0-9]{2}-[0-9]{2}:" || true)
    if [ -n "$invalid_entries" ]; then
        errors+=("Invalid entry date format (expected ### YYYY-MM-DD: Title)")
        if [ "$VERBOSE" = true ]; then
            echo -e "\033[31m  Invalid entries found:\033[0m"
            echo "$invalid_entries" | while read -r line; do
                echo -e "\033[31m  $line\033[0m"
            done
        fi
    fi
    
    # Report results
    if [ ${#errors[@]} -eq 0 ]; then
        write_validation_result "DEVLOG" "PASSED"
    else
        write_validation_result "DEVLOG" "ERROR" "${#errors[@]} issue(s) found"
        if [ "$VERBOSE" = true ]; then
            for error in "${errors[@]}"; do
                echo -e "\033[31m  - $error\033[0m"
            done
        fi
    fi
}

# Token Count Validation
validate_tokens() {
    if [ "$VERBOSE" = true ]; then
        echo -e "\n\033[36m=== Token Count Validation ===\033[0m"
    fi
    
    local changelog_tokens=$(get_token_count "$CHANGELOG_PATH")
    local devlog_tokens=$(get_token_count "$DEVLOG_PATH")
    local combined_tokens=$((changelog_tokens + devlog_tokens))
    
    local errors=()
    local warnings=()
    
    # Check CHANGELOG tokens
    if [ $changelog_tokens -ge $CHANGELOG_TOKEN_ERROR ]; then
        errors+=("CHANGELOG: $changelog_tokens tokens ($(get_percentage $changelog_tokens $CHANGELOG_TOKEN_ERROR)% of $CHANGELOG_TOKEN_ERROR limit)")
    elif [ $changelog_tokens -ge $CHANGELOG_TOKEN_WARNING ]; then
        warnings+=("CHANGELOG: $changelog_tokens tokens ($(get_percentage $changelog_tokens $CHANGELOG_TOKEN_ERROR)% of $CHANGELOG_TOKEN_ERROR limit)")
    fi
    
    # Check DEVLOG tokens
    if [ $devlog_tokens -ge $DEVLOG_TOKEN_ERROR ]; then
        errors+=("DEVLOG: $devlog_tokens tokens ($(get_percentage $devlog_tokens $DEVLOG_TOKEN_ERROR)% of $DEVLOG_TOKEN_ERROR limit)")
    elif [ $devlog_tokens -ge $DEVLOG_TOKEN_WARNING ]; then
        warnings+=("DEVLOG: $devlog_tokens tokens ($(get_percentage $devlog_tokens $DEVLOG_TOKEN_ERROR)% of $DEVLOG_TOKEN_ERROR limit)")
    fi
    
    # Check combined tokens
    if [ $combined_tokens -ge $COMBINED_TOKEN_ERROR ]; then
        errors+=("Combined: $combined_tokens tokens ($(get_percentage $combined_tokens $COMBINED_TOKEN_ERROR)% of $COMBINED_TOKEN_ERROR limit)")
    elif [ $combined_tokens -ge $COMBINED_TOKEN_WARNING ]; then
        warnings+=("Combined: $combined_tokens tokens ($(get_percentage $combined_tokens $COMBINED_TOKEN_ERROR)% of $COMBINED_TOKEN_ERROR limit)")
    fi
    
    # Report results
    if [ ${#errors[@]} -gt 0 ]; then
        write_validation_result "Token count" "ERROR" "${#errors[@]} limit(s) exceeded"
        if [ "$VERBOSE" = true ]; then
            for error in "${errors[@]}"; do
                echo -e "\033[31m  - $error\033[0m"
            done
            echo -e "\033[36m  Recommendation: Archive entries older than 30 days\033[0m"
        fi
    elif [ ${#warnings[@]} -gt 0 ]; then
        write_validation_result "Token count" "WARNING" "${#warnings[@]} threshold(s) exceeded"
        if [ "$VERBOSE" = true ]; then
            for warning in "${warnings[@]}"; do
                echo -e "\033[33m  - $warning\033[0m"
            done
            echo -e "\033[36m  Recommendation: Consider archiving entries older than 30 days\033[0m"
        fi
    else
        local percentage=$(get_percentage $combined_tokens $COMBINED_TOKEN_ERROR)
        write_validation_result "Token count" "PASSED" "$combined_tokens tokens ($percentage% of $COMBINED_TOKEN_ERROR target)"
    fi
}

# Main execution
echo ""
echo -e "\033[36mLog File Genius Validation\033[0m"
echo -e "\033[36m================================\033[0m"
echo ""

# Run validations
if [ "$RUN_CHANGELOG" = true ]; then
    validate_changelog
fi

if [ "$RUN_DEVLOG" = true ]; then
    validate_devlog
fi

if [ "$RUN_TOKENS" = true ]; then
    validate_tokens
fi

# Determine exit code
EXIT_CODE=$EXIT_SUCCESS
if [ $ERRORS -gt 0 ]; then
    EXIT_CODE=$EXIT_ERROR
elif [ $WARNINGS -gt 0 ]; then
    EXIT_CODE=$EXIT_WARNING
fi

# Summary
echo ""
echo -e "\033[36m================================\033[0m"
echo -e "\033[36mSummary: $PASSED passed, $WARNINGS warning(s), $ERRORS error(s)\033[0m"

if [ $EXIT_CODE -eq $EXIT_ERROR ]; then
    echo ""
    echo -e "\033[31m[X] Validation failed. Please fix errors before committing.\033[0m"
    echo -e "\033[36m    To bypass validation, use: git commit --no-verify\033[0m"
    echo ""
elif [ $EXIT_CODE -eq $EXIT_WARNING ]; then
    echo ""
    echo -e "\033[33m[!] Validation warnings present. Commit allowed.\033[0m"
    echo ""
else
    echo ""
    echo -e "\033[32m[OK] All validations passed!\033[0m"
    echo ""
fi

exit $EXIT_CODE

