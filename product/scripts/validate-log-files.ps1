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

.PARAMETER State
    Run only STATE validation

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
    [switch]$State,
    [switch]$Tokens,
    [switch]$Verbose,
    [switch]$PrintConfig
)

# Configuration - Standard paths (all logs in /logs/ folder)
$CHANGELOG_PATH = "logs/CHANGELOG.md"
$DEVLOG_PATH = "logs/DEVLOG.md"
$STATE_PATH = "logs/STATE.md"

# Default token targets (can be overridden by profile)
$CHANGELOG_TOKEN_WARNING = 8000
$CHANGELOG_TOKEN_ERROR = 10000
$DEVLOG_TOKEN_WARNING = 12000
$DEVLOG_TOKEN_ERROR = 15000
$COMBINED_TOKEN_WARNING = 20000
$COMBINED_TOKEN_ERROR = 25000
$VALIDATION_STRICTNESS = "errors"  # Options: strict, errors, warnings-only, disabled
$FAIL_ON_WARNINGS = $false

# STATE token targets
$STATE_TOKEN_WARNING = 400
$STATE_TOKEN_ERROR = 500

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
    
    # Estimate tokens at ~4 characters per token — the documented canonical
    # heuristic, matching lint-logs.py (len//4) and the rule files.
    $content = Get-Content $FilePath -Raw
    if (-not $content) { return 0 }
    return [math]::Floor($content.Length / 4)
}

function Get-PercentageOfTarget {
    param(
        [int]$Current,
        [int]$Target
    )

    return [math]::Round(($Current / $Target) * 100)
}

function Read-NestedConfig {
    param([string]$Content, [string]$Parent, [string]$Key)
    $lines = $Content -split "`r?`n"
    $inBlock = $false
    foreach ($line in $lines) {
        if ($line -match '^[A-Za-z_]+:') {
            # Match the parent header without a strict end-anchor so a trailing
            # comment (token_targets:  # budgets) still opens the block, matching
            # the bash validator's behavior.
            $inBlock = ($line -match ('^' + [regex]::Escape($Parent) + ':'))
            continue
        }
        if ($inBlock -and $line -match ('^\s+' + [regex]::Escape($Key) + ':\s*(\S+)')) {
            # Strip one layer of surrounding quotes so quoted scalars match the
            # canonical config_parser.py.
            return $Matches[1].Trim('"').Trim("'")
        }
    }
    return $null
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

    $cfg = Get-Content $configFile -Raw

    # Read nested paths block
    $v = Read-NestedConfig $cfg "paths" "changelog"
    if ($v) { $script:CHANGELOG_PATH = $v }
    $v = Read-NestedConfig $cfg "paths" "devlog"
    if ($v) { $script:DEVLOG_PATH = $v }
    $v = Read-NestedConfig $cfg "paths" "state"
    if ($v) { $script:STATE_PATH = $v }

    # Read nested token_targets block; derive warnings at 80%
    $v = Read-NestedConfig $cfg "token_targets" "changelog"
    if ($v) {
        $script:CHANGELOG_TOKEN_ERROR = [int]$v
        $script:CHANGELOG_TOKEN_WARNING = [int]([int]$v * 0.8)
    }
    $v = Read-NestedConfig $cfg "token_targets" "devlog"
    if ($v) {
        $script:DEVLOG_TOKEN_ERROR = [int]$v
        $script:DEVLOG_TOKEN_WARNING = [int]([int]$v * 0.8)
    }

    # Extract validation strictness
    if ($cfg -match 'strictness:\s*(\S+)') {
        $script:VALIDATION_STRICTNESS = $matches[1]
    }
    if ($cfg -match 'fail_on_warnings:\s*(true|false)') {
        $script:FAIL_ON_WARNINGS = $matches[1] -eq 'true'
    }

    # Extract version and check for updates
    if ($cfg -match 'log_file_genius_version:\s*"?([0-9.]+)"?') {
        $configVersion = $matches[1]

        # Resolve the latest-known version from VERSION.json (this script lives
        # in product/scripts/, the manifest in product/). Fall back to a
        # hardcoded current version if the manifest can't be read.
        $scriptDir = Split-Path -Parent $PSCommandPath
        $versionFile = Join-Path $scriptDir "..\VERSION.json"
        $latestVersion = "0.3.0"  # Fallback if VERSION.json is unreadable
        if (Test-Path $versionFile) {
            try {
                $manifest = Get-Content $versionFile -Raw | ConvertFrom-Json
                if ($manifest.version) { $latestVersion = $manifest.version }
            } catch { }
        }

        # Three-way comparison (ahead / behind / current). Delegate to the
        # Python comparator (single source of truth, handles pre-release +
        # build metadata); fall back to a plain string compare if python is
        # unavailable.
        $relation = ""
        $checkScript = Join-Path $scriptDir "check-version.py"
        $python = $null
        if (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }
        elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $python = "python3" }
        if ($python -and (Test-Path $checkScript)) {
            try {
                $relation = (& $python $checkScript --compare $configVersion $latestVersion 2>$null).Trim()
            } catch { $relation = "" }
        }
        if (-not $relation) {
            if ($configVersion -eq $latestVersion) { $relation = "current" } else { $relation = "behind" }
        }

        if ($relation -eq "behind") {
            Write-Host ""
            Write-Host "[!] Log File Genius update available: v$latestVersion (you have v$configVersion)" -ForegroundColor Yellow
            Write-Host "    See: https://github.com/clark-mackey/log-file-genius/releases" -ForegroundColor Yellow
            Write-Host ""
        } elseif ($relation -eq "ahead") {
            Write-Host ""
            Write-Host "[i] Log File Genius: you are on v$configVersion, newer than the latest-known v$latestVersion." -ForegroundColor Cyan
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
        Write-Host "  Hint: Run installer first: .log-file-genius/product/scripts/install.ps1" -ForegroundColor $COLOR_INFO
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
        Write-Host "  Hint: Run installer first: .log-file-genius/product/scripts/install.ps1" -ForegroundColor $COLOR_INFO
        return $EXIT_ERROR
    }
    
    $content = Get-Content $DEVLOG_PATH -Raw
    $lines = Get-Content $DEVLOG_PATH
    $errors = @()

    # Check for Daily Log section (DEVLOG is narrative only; Current Context lives in STATE.md)
    if ($content -notmatch '##\s+Daily Log') {
        $errors += "Missing '## Daily Log' section"
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

#region STATE Validation

function Test-State {
    if ($Verbose) {
        Write-Host "`n=== STATE Validation ===" -ForegroundColor $COLOR_INFO
    }

    # STATE is first-class but optional in existing flows; warn if missing, don't hard-error
    if (-not (Test-Path $STATE_PATH)) {
        Write-ValidationResult "STATE" "WARNING" "File not found: $STATE_PATH (create STATE.md for current context + session handoff)"
        return $EXIT_WARNING
    }

    $content = Get-Content $STATE_PATH -Raw
    $errors = @()

    # Check for Current Context section (STATE owns Version/Branch/Phase)
    if ($content -notmatch '##\s+Current Context') {
        $errors += "Missing '## Current Context' section"
    }

    # Check for required fields in Current Context
    $requiredFields = @('Version', 'Active Branch', 'Phase')
    foreach ($field in $requiredFields) {
        if ($content -notmatch "\*\*$field") {
            $errors += "Missing required field in Current Context: $field"
        }
    }

    # Token budget: STATE should stay lean (the now), default <500. WARNING not
    # error — STATE has no archival, and a fresh template carries removable guidance.
    $stateTokens = Get-TokenCount $STATE_PATH
    if ($stateTokens -gt $STATE_TOKEN_ERROR) {
        Write-ValidationResult "STATE" "WARNING" "Over token target ($stateTokens > $STATE_TOKEN_ERROR) - trim to the now (remove template guidance)"
    } elseif ($stateTokens -gt $STATE_TOKEN_WARNING) {
        Write-ValidationResult "STATE" "WARNING" "Approaching token target ($stateTokens/$STATE_TOKEN_ERROR)"
    }

    # Report results
    if ($errors.Count -eq 0) {
        Write-ValidationResult "STATE" "PASSED"
        return $EXIT_SUCCESS
    } else {
        Write-ValidationResult "STATE" "ERROR" "$($errors.Count) issue(s) found"
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
    
    # Calculate tokens to reclaim
    $tokensOverBudget = $combinedTokens - $COMBINED_TOKEN_ERROR

    # Report results
    if ($errors.Count -gt 0) {
        Write-ValidationResult "Token count" "ERROR" "$($errors.Count) limit(s) exceeded"
        if ($Verbose) {
            foreach ($error in $errors) {
                Write-Host "  - $error" -ForegroundColor $COLOR_ERROR
            }
            Write-Host "" -ForegroundColor $COLOR_INFO
            Write-Host "  [!] ARCHIVAL REQUIRED" -ForegroundColor $COLOR_ERROR
            Write-Host "  Run ``lfg archive --dry-run`` to see a work-aware archival plan." -ForegroundColor $COLOR_INFO
            Write-Host "  Target: Remove ~$tokensOverBudget tokens to get under budget." -ForegroundColor $COLOR_INFO
        }
        return $EXIT_ERROR
    } elseif ($warnings.Count -gt 0) {
        Write-ValidationResult "Token count" "WARNING" "$($warnings.Count) threshold(s) approaching"
        if ($Verbose) {
            foreach ($warning in $warnings) {
                Write-Host "  - $warning" -ForegroundColor $COLOR_WARNING
            }
            Write-Host "" -ForegroundColor $COLOR_INFO
            Write-Host "  [!] Consider archiving OLDEST entries to stay under budget" -ForegroundColor $COLOR_WARNING
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

if ($PrintConfig) {
    Write-Output "CHANGELOG_PATH=$CHANGELOG_PATH"
    Write-Output "DEVLOG_PATH=$DEVLOG_PATH"
    Write-Output "STATE_PATH=$STATE_PATH"
    Write-Output "CHANGELOG_TOKEN_ERROR=$CHANGELOG_TOKEN_ERROR"
    Write-Output "CHANGELOG_TOKEN_WARNING=$CHANGELOG_TOKEN_WARNING"
    Write-Output "DEVLOG_TOKEN_ERROR=$DEVLOG_TOKEN_ERROR"
    Write-Output "DEVLOG_TOKEN_WARNING=$DEVLOG_TOKEN_WARNING"
    Write-Output "STATE_TOKEN_ERROR=$STATE_TOKEN_ERROR"
    Write-Output "STATE_TOKEN_WARNING=$STATE_TOKEN_WARNING"
    exit 0
}

$exitCode = $EXIT_SUCCESS

# Determine which validations to run
$runAll = -not ($Changelog -or $Devlog -or $State -or $Tokens)

if ($runAll -or $Changelog) {
    $result = Test-Changelog
    if ($result -gt $exitCode) { $exitCode = $result }
}

if ($runAll -or $Devlog) {
    $result = Test-Devlog
    if ($result -gt $exitCode) { $exitCode = $result }
}

if ($runAll -or $State) {
    $result = Test-State
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

