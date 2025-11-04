#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validates Log File Genius CHANGELOG and DEVLOG files

.DESCRIPTION
    Runs format and token count validation on CHANGELOG.md and DEVLOG.md files.
    Provides clear error messages and suggestions for fixes.

.PARAMETER Changelog
    Run only CHANGELOG validation

.PARAMETER Devlog
    Run only DEVLOG validation

.PARAMETER Tokens
    Run only token count validation

.PARAMETER Verbose
    Show detailed validation output

.EXAMPLE
    .\validate-log-files.ps1
    Run all validations

.EXAMPLE
    .\validate-log-files.ps1 -Changelog
    Run only CHANGELOG validation

.EXAMPLE
    .\validate-log-files.ps1 -Verbose
    Run all validations with detailed output
#>

param(
    [switch]$Changelog,
    [switch]$Devlog,
    [switch]$Tokens,
    [switch]$Verbose
)

# Configuration - Standard paths (all logs in /logs/ folder)
$CHANGELOG_PATH = "logs/CHANGELOG.md"
$DEVLOG_PATH = "logs/DEVLOG.md"

# Default token targets (can be overridden by profile)
$CHANGELOG_TOKEN_WARNING = 8000
$CHANGELOG_TOKEN_ERROR = 10000
$DEVLOG_TOKEN_WARNING = 12000
$DEVLOG_TOKEN_ERROR = 15000
$COMBINED_TOKEN_WARNING = 20000
$COMBINED_TOKEN_ERROR = 25000
$VALIDATION_STRICTNESS = "errors"  # Options: strict, errors, warnings-only, disabled
$FAIL_ON_WARNINGS = $false

# Note: STATE and ADR validation not yet implemented
# Future: Add STATE_TOKEN_WARNING = 400, STATE_TOKEN_ERROR = 500

# Colors
$COLOR_SUCCESS = "Green"
$COLOR_WARNING = "Yellow"
$COLOR_ERROR = "Red"
$COLOR_INFO = "Cyan"

# Exit codes
$EXIT_SUCCESS = 0
$EXIT_WARNING = 1
$EXIT_ERROR = 2

# Validation results
$validationResults = @{
    Passed = 0
    Warnings = 0
    Errors = 0
}

#region Helper Functions

function Write-ValidationResult {
    param(
        [string]$Name,
        [string]$Status,
        [string]$Message = ""
    )
    
    $icon = switch ($Status) {
        "PASSED" { "[OK]"; $validationResults.Passed++ }
        "WARNING" { "[!]"; $validationResults.Warnings++ }
        "ERROR" { "[X]"; $validationResults.Errors++ }
    }
    
    $color = switch ($Status) {
        "PASSED" { $COLOR_SUCCESS }
        "WARNING" { $COLOR_WARNING }
        "ERROR" { $COLOR_ERROR }
    }
    
    $output = "$icon $Name validation: $Status"
    if ($Message) {
        $output += " - $Message"
    }
    
    Write-Host $output -ForegroundColor $color
}

function Get-TokenCount {
    param([string]$FilePath)
    
    if (-not (Test-Path $FilePath)) {
        return 0
    }
    
    $content = Get-Content $FilePath -Raw
    $wordCount = ($content -split '\s+').Count
    $tokenEstimate = [math]::Ceiling($wordCount * 1.3)
    
    return $tokenEstimate
}

function Get-PercentageOfTarget {
    param(
        [int]$Current,
        [int]$Target
    )

    return [math]::Round(($Current / $Target) * 100)
}

function Load-ProfileConfig {
    # Check for config file in standard locations
    $configPaths = @(
        ".logfile-config.yml",
        "config/logfile.yml",
        ".config/logfile.yml"
    )

    $configFile = $null
    foreach ($path in $configPaths) {
        if (Test-Path $path) {
            $configFile = $path
            break
        }
    }

    if (-not $configFile) {
        if ($Verbose) {
            Write-Host "No config file found. Using default profile (solo-developer)" -ForegroundColor $COLOR_INFO
        }
        return
    }

    if ($Verbose) {
        Write-Host "Loading profile config from: $configFile" -ForegroundColor $COLOR_INFO
    }

    # Simple YAML parsing for our limited use case
    # We only need to read profile name and overrides.token_targets
    $content = Get-Content $configFile -Raw

    # Extract profile name
    if ($content -match 'profile:\s*(\S+)') {
        $profileName = $matches[1]
        if ($Verbose) {
            Write-Host "Profile: $profileName" -ForegroundColor $COLOR_INFO
        }
    }

    # Extract token target overrides if present
    if ($content -match 'changelog_warning:\s*(\d+)') {
        $script:CHANGELOG_TOKEN_WARNING = [int]$matches[1]
    }
    if ($content -match 'changelog_error:\s*(\d+)') {
        $script:CHANGELOG_TOKEN_ERROR = [int]$matches[1]
    }
    if ($content -match 'devlog_warning:\s*(\d+)') {
        $script:DEVLOG_TOKEN_WARNING = [int]$matches[1]
    }
    if ($content -match 'devlog_error:\s*(\d+)') {
        $script:DEVLOG_TOKEN_ERROR = [int]$matches[1]
    }
    if ($content -match 'combined_warning:\s*(\d+)') {
        $script:COMBINED_TOKEN_WARNING = [int]$matches[1]
    }
    if ($content -match 'combined_error:\s*(\d+)') {
        $script:COMBINED_TOKEN_ERROR = [int]$matches[1]
    }

    # Extract validation strictness
    if ($content -match 'strictness:\s*(\S+)') {
        $script:VALIDATION_STRICTNESS = $matches[1]
    }
    if ($content -match 'fail_on_warnings:\s*(true|false)') {
        $script:FAIL_ON_WARNINGS = $matches[1] -eq 'true'
    }

    # Extract version and check for updates
    if ($content -match 'log_file_genius_version:\s*"?([0-9.]+)"?') {
        $configVersion = $matches[1]
        $latestVersion = "0.2.0"  # Current version

        if ($configVersion -ne $latestVersion) {
            Write-Host ""
            Write-Host "⚠️  Log File Genius update available: v$latestVersion (you have v$configVersion)" -ForegroundColor Yellow
            Write-Host "    See: https://github.com/clark-mackey/log-file-genius/releases" -ForegroundColor Yellow
            Write-Host ""
        }
    }
}

#endregion

#region CHANGELOG Validation

function Test-Changelog {
    if ($Verbose) {
        Write-Host "`n=== CHANGELOG Validation ===" -ForegroundColor $COLOR_INFO
    }
    
    # Check file exists
    if (-not (Test-Path $CHANGELOG_PATH)) {
        Write-ValidationResult "CHANGELOG" "ERROR" "File not found: $CHANGELOG_PATH"
        return $EXIT_ERROR
    }
    
    $content = Get-Content $CHANGELOG_PATH -Raw
    $lines = Get-Content $CHANGELOG_PATH
    $errors = @()
    
    # Check for Unreleased section
    if ($content -notmatch '##\s+\[Unreleased\]') {
        $errors += "Missing '## [Unreleased]' section"
    }
    
    # Check for at least one category
    $categories = @('### Added', '### Changed', '### Fixed', '### Deprecated', '### Removed', '### Security')
    $hasCategory = $false
    foreach ($category in $categories) {
        if ($content -match [regex]::Escape($category)) {
            $hasCategory = $true
            break
        }
    }
    
    if (-not $hasCategory) {
        $errors += "Missing at least one category (Added, Changed, Fixed, Deprecated, Removed, Security)"
    }
    
    # Check date formats (YYYY-MM-DD)
    $datePattern = '##\s+\[[\d\.]+\]\s+-\s+(\d{4}-\d{2}-\d{2})'
    $invalidDates = $lines | Where-Object { 
        $_ -match '##\s+\[[\d\.]+\]\s+-\s+' -and $_ -notmatch $datePattern 
    }
    
    if ($invalidDates) {
        $errors += "Invalid date format found. Expected: YYYY-MM-DD"
        if ($Verbose) {
            foreach ($line in $invalidDates) {
                Write-Host "  Invalid: $line" -ForegroundColor $COLOR_ERROR
            }
        }
    }
    
    # Report results
    if ($errors.Count -eq 0) {
        Write-ValidationResult "CHANGELOG" "PASSED"
        return $EXIT_SUCCESS
    } else {
        Write-ValidationResult "CHANGELOG" "ERROR" "$($errors.Count) issue(s) found"
        if ($Verbose) {
            foreach ($error in $errors) {
                Write-Host "  - $error" -ForegroundColor $COLOR_ERROR
            }
        }
        return $EXIT_ERROR
    }
}

#endregion

#region DEVLOG Validation

function Test-Devlog {
    if ($Verbose) {
        Write-Host "`n=== DEVLOG Validation ===" -ForegroundColor $COLOR_INFO
    }
    
    # Check file exists
    if (-not (Test-Path $DEVLOG_PATH)) {
        Write-ValidationResult "DEVLOG" "ERROR" "File not found: $DEVLOG_PATH"
        return $EXIT_ERROR
    }
    
    $content = Get-Content $DEVLOG_PATH -Raw
    $lines = Get-Content $DEVLOG_PATH
    $errors = @()
    
    # Check for Current Context section
    if ($content -notmatch '##\s+Current Context') {
        $errors += "Missing '## Current Context' section"
    }
    
    # Check for Daily Log section
    if ($content -notmatch '##\s+Daily Log') {
        $errors += "Missing '## Daily Log' section"
    }
    
    # Check for required Current Context fields
    $requiredFields = @('Version', 'Active Branch', 'Phase')
    foreach ($field in $requiredFields) {
        if ($content -notmatch "\*\*$field") {
            $errors += "Missing required field in Current Context: $field"
        }
    }
    
    # Check entry date formats (### YYYY-MM-DD: Title)
    $entryPattern = '###\s+\d{4}-\d{2}-\d{2}:'
    $invalidEntries = $lines | Where-Object { 
        $_ -match '###\s+\d' -and $_ -notmatch $entryPattern 
    }
    
    if ($invalidEntries) {
        $errors += "Invalid entry date format found. Expected: ### YYYY-MM-DD: Title"
        if ($Verbose) {
            foreach ($line in $invalidEntries) {
                Write-Host "  Invalid: $line" -ForegroundColor $COLOR_ERROR
            }
        }
    }
    
    # Report results
    if ($errors.Count -eq 0) {
        Write-ValidationResult "DEVLOG" "PASSED"
        return $EXIT_SUCCESS
    } else {
        Write-ValidationResult "DEVLOG" "ERROR" "$($errors.Count) issue(s) found"
        if ($Verbose) {
            foreach ($error in $errors) {
                Write-Host "  - $error" -ForegroundColor $COLOR_ERROR
            }
        }
        return $EXIT_ERROR
    }
}

#endregion

#region Token Count Validation

function Test-TokenCounts {
    if ($Verbose) {
        Write-Host "`n=== Token Count Validation ===" -ForegroundColor $COLOR_INFO
    }
    
    $changelogTokens = Get-TokenCount $CHANGELOG_PATH
    $devlogTokens = Get-TokenCount $DEVLOG_PATH
    $combinedTokens = $changelogTokens + $devlogTokens
    
    $warnings = @()
    $errors = @()
    
    # Check CHANGELOG
    if ($changelogTokens -ge $CHANGELOG_TOKEN_ERROR) {
        $pct = Get-PercentageOfTarget $changelogTokens $CHANGELOG_TOKEN_ERROR
        $errors += "CHANGELOG at $changelogTokens tokens ($pct% of $CHANGELOG_TOKEN_ERROR target)"
    } elseif ($changelogTokens -ge $CHANGELOG_TOKEN_WARNING) {
        $pct = Get-PercentageOfTarget $changelogTokens $CHANGELOG_TOKEN_ERROR
        $warnings += "CHANGELOG at $changelogTokens tokens ($pct% of $CHANGELOG_TOKEN_ERROR target)"
    }
    
    # Check DEVLOG
    if ($devlogTokens -ge $DEVLOG_TOKEN_ERROR) {
        $pct = Get-PercentageOfTarget $devlogTokens $DEVLOG_TOKEN_ERROR
        $errors += "DEVLOG at $devlogTokens tokens ($pct% of $DEVLOG_TOKEN_ERROR target)"
    } elseif ($devlogTokens -ge $DEVLOG_TOKEN_WARNING) {
        $pct = Get-PercentageOfTarget $devlogTokens $DEVLOG_TOKEN_ERROR
        $warnings += "DEVLOG at $devlogTokens tokens ($pct% of $DEVLOG_TOKEN_ERROR target)"
    }
    
    # Check Combined
    if ($combinedTokens -ge $COMBINED_TOKEN_ERROR) {
        $pct = Get-PercentageOfTarget $combinedTokens $COMBINED_TOKEN_ERROR
        $errors += "Combined at $combinedTokens tokens ($pct% of $COMBINED_TOKEN_ERROR target)"
    } elseif ($combinedTokens -ge $COMBINED_TOKEN_WARNING) {
        $pct = Get-PercentageOfTarget $combinedTokens $COMBINED_TOKEN_ERROR
        $warnings += "Combined at $combinedTokens tokens ($pct% of $COMBINED_TOKEN_ERROR target)"
    }
    
    # Report results
    if ($errors.Count -gt 0) {
        Write-ValidationResult "Token count" "ERROR" "$($errors.Count) limit(s) exceeded"
        if ($Verbose) {
            foreach ($error in $errors) {
                Write-Host "  - $error" -ForegroundColor $COLOR_ERROR
            }
            Write-Host "  Recommendation: Archive entries older than 30 days" -ForegroundColor $COLOR_INFO
        }
        return $EXIT_ERROR
    } elseif ($warnings.Count -gt 0) {
        Write-ValidationResult "Token count" "WARNING" "$($warnings.Count) threshold(s) approaching"
        if ($Verbose) {
            foreach ($warning in $warnings) {
                Write-Host "  - $warning" -ForegroundColor $COLOR_WARNING
            }
            Write-Host "  Recommendation: Consider archiving entries older than 30 days" -ForegroundColor $COLOR_INFO
        }
        return $EXIT_WARNING
    } else {
        $pct = Get-PercentageOfTarget $combinedTokens $COMBINED_TOKEN_ERROR
        Write-ValidationResult "Token count" "PASSED" "Combined: $combinedTokens tokens ($pct% of target)"
        return $EXIT_SUCCESS
    }
}

#endregion

#region Main Execution

Write-Host "" -ForegroundColor $COLOR_INFO
Write-Host "Log File Genius Validation" -ForegroundColor $COLOR_INFO
Write-Host "================================" -ForegroundColor $COLOR_INFO
Write-Host "" -ForegroundColor $COLOR_INFO

# Load profile configuration
Load-ProfileConfig

$exitCode = $EXIT_SUCCESS

# Determine which validations to run
$runAll = -not ($Changelog -or $Devlog -or $Tokens)

if ($runAll -or $Changelog) {
    $result = Test-Changelog
    if ($result -gt $exitCode) { $exitCode = $result }
}

if ($runAll -or $Devlog) {
    $result = Test-Devlog
    if ($result -gt $exitCode) { $exitCode = $result }
}

if ($runAll -or $Tokens) {
    $result = Test-TokenCounts
    if ($result -gt $exitCode) { $exitCode = $result }
}

# Summary
Write-Host "`n================================" -ForegroundColor $COLOR_INFO
Write-Host "Summary: $($validationResults.Passed) passed, $($validationResults.Warnings) warning(s), $($validationResults.Errors) error(s)" -ForegroundColor $COLOR_INFO

# Apply strictness settings
if ($VALIDATION_STRICTNESS -eq "disabled") {
    $exitCode = $EXIT_SUCCESS
    Write-Host "" -ForegroundColor $COLOR_INFO
    Write-Host "[INFO] Validation disabled by profile. All checks passed." -ForegroundColor $COLOR_INFO
    Write-Host "" -ForegroundColor $COLOR_INFO
} elseif ($VALIDATION_STRICTNESS -eq "warnings-only") {
    # Never fail, just show warnings
    $exitCode = $EXIT_SUCCESS
    if ($validationResults.Warnings -gt 0 -or $validationResults.Errors -gt 0) {
        Write-Host "" -ForegroundColor $COLOR_WARNING
        Write-Host "[!] Validation issues found (warnings-only mode). Commit allowed." -ForegroundColor $COLOR_WARNING
        Write-Host "" -ForegroundColor $COLOR_WARNING
    } else {
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
        Write-Host "[OK] All validations passed!" -ForegroundColor $COLOR_SUCCESS
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
    }
} elseif ($VALIDATION_STRICTNESS -eq "strict" -or $FAIL_ON_WARNINGS) {
    # Fail on warnings or errors
    if ($exitCode -ge $EXIT_WARNING) {
        Write-Host "" -ForegroundColor $COLOR_ERROR
        Write-Host "[X] Validation failed (strict mode). Please fix all issues before committing." -ForegroundColor $COLOR_ERROR
        Write-Host "    To bypass validation, use: git commit --no-verify" -ForegroundColor $COLOR_INFO
        Write-Host "" -ForegroundColor $COLOR_INFO
        $exitCode = $EXIT_ERROR
    } else {
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
        Write-Host "[OK] All validations passed!" -ForegroundColor $COLOR_SUCCESS
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
    }
} else {
    # Default: errors mode - fail only on errors
    if ($exitCode -eq $EXIT_ERROR) {
        Write-Host "" -ForegroundColor $COLOR_ERROR
        Write-Host "[X] Validation failed. Please fix errors before committing." -ForegroundColor $COLOR_ERROR
        Write-Host "    To bypass validation, use: git commit --no-verify" -ForegroundColor $COLOR_INFO
        Write-Host "" -ForegroundColor $COLOR_INFO
    } elseif ($exitCode -eq $EXIT_WARNING) {
        Write-Host "" -ForegroundColor $COLOR_WARNING
        Write-Host "[!] Validation warnings present. Commit allowed." -ForegroundColor $COLOR_WARNING
        Write-Host "" -ForegroundColor $COLOR_WARNING
    } else {
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
        Write-Host "[OK] All validations passed!" -ForegroundColor $COLOR_SUCCESS
        Write-Host "" -ForegroundColor $COLOR_SUCCESS
    }
}

exit $exitCode

#endregion

