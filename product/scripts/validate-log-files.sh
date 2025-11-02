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

# Configuration - Default values (can be overridden by profile)
CHANGELOG_PATH="project/planning/CHANGELOG.md"
DEVLOG_PATH="project/planning/DEVLOG.md"
CHANGELOG_TOKEN_WARNING=8000
CHANGELOG_TOKEN_ERROR=10000
DEVLOG_TOKEN_WARNING=12000
DEVLOG_TOKEN_ERROR=15000
COMBINED_TOKEN_WARNING=20000
COMBINED_TOKEN_ERROR=25000
VALIDATION_STRICTNESS="errors"  # Options: strict, errors, warnings-only, disabled
FAIL_ON_WARNINGS=false

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

load_profile_config() {
    # Check for config file in standard locations
    local config_file=""

    for path in ".logfile-config.yml" "config/logfile.yml" ".config/logfile.yml"; do
        if [ -f "$path" ]; then
            config_file="$path"
            break
        fi
    done

    if [ -z "$config_file" ]; then
        if [ "$VERBOSE" = true ]; then
            echo -e "\033[36mNo config file found. Using default profile (solo-developer)\033[0m"
        fi
        return
    fi

    if [ "$VERBOSE" = true ]; then
        echo -e "\033[36mLoading profile config from: $config_file\033[0m"
    fi

    # Simple YAML parsing for our limited use case
    # Extract profile name
    if grep -q "^profile:" "$config_file"; then
        local profile_name=$(grep "^profile:" "$config_file" | awk '{print $2}')
        if [ "$VERBOSE" = true ]; then
            echo -e "\033[36mProfile: $profile_name\033[0m"
        fi
    fi

    # Extract token target overrides if present
    if grep -q "changelog_warning:" "$config_file"; then
        CHANGELOG_TOKEN_WARNING=$(grep "changelog_warning:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "changelog_error:" "$config_file"; then
        CHANGELOG_TOKEN_ERROR=$(grep "changelog_error:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "devlog_warning:" "$config_file"; then
        DEVLOG_TOKEN_WARNING=$(grep "devlog_warning:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "devlog_error:" "$config_file"; then
        DEVLOG_TOKEN_ERROR=$(grep "devlog_error:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "combined_warning:" "$config_file"; then
        COMBINED_TOKEN_WARNING=$(grep "combined_warning:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "combined_error:" "$config_file"; then
        COMBINED_TOKEN_ERROR=$(grep "combined_error:" "$config_file" | awk '{print $2}')
    fi

    # Extract validation strictness
    if grep -q "strictness:" "$config_file"; then
        VALIDATION_STRICTNESS=$(grep "strictness:" "$config_file" | awk '{print $2}')
    fi
    if grep -q "fail_on_warnings:" "$config_file"; then
        local fail_value=$(grep "fail_on_warnings:" "$config_file" | awk '{print $2}')
        if [ "$fail_value" = "true" ]; then
            FAIL_ON_WARNINGS=true
        fi
    fi
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

# Load profile configuration
load_profile_config

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

# Apply strictness settings
if [ "$VALIDATION_STRICTNESS" = "disabled" ]; then
    EXIT_CODE=$EXIT_SUCCESS
    echo ""
    echo -e "\033[36m[INFO] Validation disabled by profile. All checks passed.\033[0m"
    echo ""
elif [ "$VALIDATION_STRICTNESS" = "warnings-only" ]; then
    # Never fail, just show warnings
    EXIT_CODE=$EXIT_SUCCESS
    if [ $WARNINGS -gt 0 ] || [ $ERRORS -gt 0 ]; then
        echo ""
        echo -e "\033[33m[!] Validation issues found (warnings-only mode). Commit allowed.\033[0m"
        echo ""
    else
        echo ""
        echo -e "\033[32m[OK] All validations passed!\033[0m"
        echo ""
    fi
elif [ "$VALIDATION_STRICTNESS" = "strict" ] || [ "$FAIL_ON_WARNINGS" = true ]; then
    # Fail on warnings or errors
    if [ $EXIT_CODE -ge $EXIT_WARNING ]; then
        echo ""
        echo -e "\033[31m[X] Validation failed (strict mode). Please fix all issues before committing.\033[0m"
        echo -e "\033[36m    To bypass validation, use: git commit --no-verify\033[0m"
        echo ""
        EXIT_CODE=$EXIT_ERROR
    else
        echo ""
        echo -e "\033[32m[OK] All validations passed!\033[0m"
        echo ""
    fi
else
    # Default: errors mode - fail only on errors
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
fi

exit $EXIT_CODE

