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

# Configuration
$CHANGELOG_PATH = "project/planning/CHANGELOG.md"
$DEVLOG_PATH = "project/planning/DEVLOG.md"
$CHANGELOG_TOKEN_WARNING = 8000
$CHANGELOG_TOKEN_ERROR = 10000
$DEVLOG_TOKEN_WARNING = 12000
$DEVLOG_TOKEN_ERROR = 15000
$COMBINED_TOKEN_WARNING = 20000
$COMBINED_TOKEN_ERROR = 25000

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

exit $exitCode

#endregion

