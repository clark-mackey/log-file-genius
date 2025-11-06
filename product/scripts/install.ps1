#!/usr/bin/env pwsh
# Log File Genius Installer (PowerShell)
# Installs Log File Genius to your project with standard /logs/ structure
#
# Usage:
#   install.ps1 [-Profile <profile>] [-AiAssistant <augment|claude-code>] [-Force]
#
# Options:
#   -Profile        Profile to use (solo-developer, team, open-source, startup)
#   -AiAssistant    AI assistant to install rules for (augment, claude-code)
#   -Force          Skip confirmation prompts (validation still runs)

param(
    [string]$Profile = "",
    [string]$AiAssistant = "",
    [switch]$Force = $false,
    [switch]$Help = $false
)

# Show help if requested
if ($Help) {
    Write-Host "Log File Genius Installer v0.2.0"
    Write-Host ""
    Write-Host "Usage: install.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "Options:"
    Write-Host "  -Profile <name>       Profile to use (solo-developer, team, open-source, startup)"
    Write-Host "  -AiAssistant <name>   AI assistant (augment, claude-code)"
    Write-Host "  -Force                Skip confirmation prompts"
    Write-Host "  -Help                 Show this help message"
    Write-Host ""
    Write-Host "Examples:"
    Write-Host "  install.ps1 -Profile solo-developer -Force"
    Write-Host "  install.ps1 -AiAssistant augment"
    exit 0
}

$ErrorActionPreference = "Stop"

# ============================================================================
# CONFIGURATION
# ============================================================================

$VERSION = "0.2.0"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceRoot = Resolve-Path (Join-Path $ScriptDir "..")
$ProjectRoot = Get-Location

# Track created items for rollback
$CreatedItems = @()

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

function Print-Success {
    param([string]$Message)
    Write-Host "[OK] $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Print-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Cyan
}

function Rollback-Installation {
    param([string]$Reason)

    Print-Error "Installation failed: $Reason"

    if ($CreatedItems.Count -gt 0) {
        Print-Warning "Rolling back changes..."

        foreach ($item in $CreatedItems) {
            if (Test-Path $item) {
                Remove-Item -Path $item -Recurse -Force -ErrorAction SilentlyContinue
                Print-Info "Removed $item"
            }
        }

        Print-Success "Rollback complete"
    }

    exit 1
}

# ============================================================================
# BANNER
# ============================================================================

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   Log File Genius Installer v$VERSION      ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# ============================================================================
# DETECT AI ASSISTANT
# ============================================================================

if (-not $AiAssistant) {
    Print-Info "Detecting AI assistant..."
    
    if (Test-Path ".augment") {
        $AiAssistant = "augment"
        Print-Success "Detected Augment"
    }
    elseif (Test-Path ".claude") {
        $AiAssistant = "claude-code"
        Print-Success "Detected Claude Code"
    }
    else {
        Write-Host ""
        Write-Host "Which AI assistant are you using?"
        Write-Host "  1) Augment"
        Write-Host "  2) Claude Code"
        Write-Host ""
        $choice = Read-Host "Enter choice (1-2)"
        
        switch ($choice) {
            "1" { $AiAssistant = "augment" }
            "2" { $AiAssistant = "claude-code" }
            default {
                Print-Error "Invalid choice. Exiting."
                exit 1
            }
        }
    }
}

# ============================================================================
# SELECT PROFILE
# ============================================================================

if (-not $Profile) {
    Write-Host ""
    Write-Host "Select your project profile:"
    Write-Host "  1) solo-developer  - Individual developers (flexible, minimal overhead)"
    Write-Host "  2) team            - Teams of 2+ developers (consistent docs)"
    Write-Host "  3) open-source     - Public projects (strict formatting)"
    Write-Host "  4) startup         - Fast-moving startups (minimal overhead)"
    Write-Host ""
    $choice = Read-Host "Enter choice (1-4)"
    
    switch ($choice) {
        "1" { $Profile = "solo-developer" }
        "2" { $Profile = "team" }
        "3" { $Profile = "open-source" }
        "4" { $Profile = "startup" }
        default {
            Print-Error "Invalid choice. Exiting."
            exit 1
        }
    }
}

Print-Success "Profile: $Profile"
Print-Success "AI Assistant: $AiAssistant"

# ============================================================================
# CHECK FOR EXISTING INSTALLATION
# ============================================================================

$logsExists = Test-Path "logs"
$configExists = Test-Path ".logfile-config.yml"

if ($logsExists -or $configExists) {
    Write-Host ""
    Print-Warning "Existing installation detected!"
    if ($logsExists) { Print-Warning "  - logs/ folder exists" }
    if ($configExists) { Print-Warning "  - .logfile-config.yml exists" }
    Write-Host ""
    
    if (-not $Force) {
        $continue = Read-Host "Continue and overwrite? (y/N)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            Print-Info "Installation cancelled."
            exit 0
        }
    }
}

# ============================================================================
# CREATE LOGS FOLDER STRUCTURE
# ============================================================================

Write-Host ""
Print-Info "Creating /logs/ folder structure..."

$foldersToCreate = @(
    "logs",
    "logs/adr",
    "logs/incidents"
)

foreach ($folder in $foldersToCreate) {
    if (-not (Test-Path $folder)) {
        New-Item -ItemType Directory -Path $folder -Force | Out-Null
        $CreatedItems += $folder
        Print-Success "Created $folder/"
    }
    else {
        Print-Info "$folder/ already exists"
    }
}

# ============================================================================
# COPY TEMPLATES TO /logs/
# ============================================================================

Print-Info "Copying log file templates..."

$templateMappings = @{
    "templates/CHANGELOG_template.md" = "logs/CHANGELOG.md"
    "templates/DEVLOG_template.md" = "logs/DEVLOG.md"
    "templates/STATE_template.md" = "logs/STATE.md"
    "templates/ADR_template.md" = "logs/adr/TEMPLATE.md"
}

$templateErrors = @()

foreach ($mapping in $templateMappings.GetEnumerator()) {
    $source = Join-Path $SourceRoot $mapping.Key
    $dest = $mapping.Value

    if (Test-Path $source) {
        Copy-Item -Path $source -Destination $dest -Force
        $CreatedItems += $dest
        Print-Success "Copied $dest"
    }
    else {
        Print-Error "Template not found: $source"
        $templateErrors += $source
    }
}

if ($templateErrors.Count -gt 0) {
    Rollback-Installation "Missing template files"
}

# ============================================================================
# INSTALL AI RULES
# ============================================================================

Print-Info "Installing AI assistant rules..."

if ($AiAssistant -eq "augment") {
    $rulesSource = Join-Path $SourceRoot "ai-rules/augment"
    $rulesDest = ".augment/rules"

    # Track if .augment existed before we started
    $augmentExisted = Test-Path ".augment"

    if (-not (Test-Path ".augment")) {
        New-Item -ItemType Directory -Path ".augment" -Force | Out-Null
    }
    if (-not (Test-Path $rulesDest)) {
        New-Item -ItemType Directory -Path $rulesDest -Force | Out-Null
    }

    # Track directory creation for rollback
    if (-not $augmentExisted) {
        $CreatedItems += ".augment"
    } else {
        $CreatedItems += ".augment/rules"
    }

    try {
        Get-ChildItem -Path $rulesSource -Filter "*.md" -Recurse -ErrorAction Stop | ForEach-Object {
            $relativePath = $_.FullName.Substring($rulesSource.Length + 1)
            $destPath = Join-Path $rulesDest $relativePath
            $destDir = Split-Path -Parent $destPath

            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }

            Copy-Item -Path $_.FullName -Destination $destPath -Force -ErrorAction Stop
            $CreatedItems += $destPath
            Print-Success "Installed .augment/rules/$relativePath"
        }
    }
    catch {
        Rollback-Installation "Failed to copy AI rules: $($_.Exception.Message)"
    }
}
elseif ($AiAssistant -eq "claude-code") {
    $rulesSource = Join-Path $SourceRoot "ai-rules/claude-code"
    $rulesDest = ".claude/rules"

    # Track if .claude existed before we started
    $claudeExisted = Test-Path ".claude"

    if (-not (Test-Path ".claude")) {
        New-Item -ItemType Directory -Path ".claude" -Force | Out-Null
    }
    if (-not (Test-Path $rulesDest)) {
        New-Item -ItemType Directory -Path $rulesDest -Force | Out-Null
    }

    # Track directory creation for rollback
    if (-not $claudeExisted) {
        $CreatedItems += ".claude"
    } else {
        $CreatedItems += ".claude/rules"
    }

    try {
        Get-ChildItem -Path $rulesSource -Filter "*.md" -Recurse -ErrorAction Stop | ForEach-Object {
            $relativePath = $_.FullName.Substring($rulesSource.Length + 1)
            $destPath = Join-Path $rulesDest $relativePath
            $destDir = Split-Path -Parent $destPath

            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }

            Copy-Item -Path $_.FullName -Destination $destPath -Force -ErrorAction Stop
            $CreatedItems += $destPath
            Print-Success "Installed .claude/rules/$relativePath"
        }

        # Copy project_instructions.md if it exists
        $projectInstructions = Join-Path $rulesSource "project_instructions.md"
        if (Test-Path $projectInstructions) {
            Copy-Item -Path $projectInstructions -Destination ".claude/" -Force -ErrorAction Stop
            $CreatedItems += ".claude/project_instructions.md"
            Print-Success "Installed .claude/project_instructions.md"
        }
    }
    catch {
        Rollback-Installation "Failed to copy AI rules: $($_.Exception.Message)"
    }
}

# ============================================================================
# CREATE CONFIG FILE
# ============================================================================

Print-Info "Creating .logfile-config.yml..."

$configContent = @"
# Log File Genius Configuration
# All log files are in /logs/ folder (standard structure)

# Version tracking
log_file_genius_version: "$VERSION"

# Profile selection
profile: $Profile

# AI assistant
ai_assistant: $AiAssistant

# For customization options, see:
# - .log-file-genius/docs/profile-selection-guide.md
# - .log-file-genius/profiles/*.yml
"@

Set-Content -Path ".logfile-config.yml" -Value $configContent -Force
$CreatedItems += ".logfile-config.yml"
Print-Success "Created .logfile-config.yml"

# ============================================================================
# VALIDATION
# ============================================================================

Write-Host ""
Print-Info "Validating installation..."

$errors = @()

if (-not (Test-Path "logs/CHANGELOG.md")) { $errors += "logs/CHANGELOG.md missing" }
if (-not (Test-Path "logs/DEVLOG.md")) { $errors += "logs/DEVLOG.md missing" }
if (-not (Test-Path "logs/STATE.md")) { $errors += "logs/STATE.md missing" }
if (-not (Test-Path ".logfile-config.yml")) { $errors += ".logfile-config.yml missing" }

if ($AiAssistant -eq "augment" -and -not (Test-Path ".augment/rules/log-file-maintenance.md")) {
    $errors += ".augment/rules/log-file-maintenance.md missing"
}
if ($AiAssistant -eq "claude-code" -and -not (Test-Path ".claude/rules/log-file-maintenance.md")) {
    $errors += ".claude/rules/log-file-maintenance.md missing"
}

if ($errors.Count -gt 0) {
    Print-Error "Installation validation failed:"
    foreach ($err in $errors) {
        Print-Error "  - $err"
    }
    Rollback-Installation "Validation failed"
}

Print-Success "Installation validated successfully!"

# ============================================================================
# SUCCESS MESSAGE
# ============================================================================

Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "   Installation Complete!" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""
Print-Success "Log files installed to: logs/"
Print-Success "AI rules installed to: .$AiAssistant/rules/"
Print-Success "Config file: .logfile-config.yml"
Write-Host ""
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host "NEXT STEP: Document this installation" -ForegroundColor Cyan
Write-Host "-----------------------------------" -ForegroundColor Cyan
Write-Host ""
Write-Host "Copy and paste this prompt to your AI assistant:" -ForegroundColor Yellow
Write-Host ""
Write-Host '"I just installed Log File Genius. Please:' -ForegroundColor White
Write-Host ' 1. Update CHANGELOG.md with what was installed' -ForegroundColor White
Write-Host ' 2. Update DEVLOG.md with why we installed it' -ForegroundColor White
Write-Host ' 3. Create an ADR documenting the architectural decision' -ForegroundColor White
Write-Host '    to adopt Log File Genius for project documentation"' -ForegroundColor White
Write-Host ""
Write-Host "This will:" -ForegroundColor Gray
Write-Host "  - Show you how the system works" -ForegroundColor Gray
Write-Host "  - Create your first log entries" -ForegroundColor Gray
Write-Host "  - Document the architectural decision" -ForegroundColor Gray
Write-Host "  - Validate that AI rules are working" -ForegroundColor Gray
Write-Host ""
Print-Info "Documentation: .log-file-genius/docs/log_file_how_to.md"
Write-Host ""

