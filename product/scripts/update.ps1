#!/usr/bin/env pwsh
# Log File Genius Update Script (PowerShell)
# Updates Log File Genius files while preserving user customizations

param(
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"
$ProjectRoot = Get-Location

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   Log File Genius Update Script       ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Helper functions
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
    Write-Host "[INFO] $Message" -ForegroundColor Blue
}

# Check if .log-file-genius exists
$SourceRoot = Join-Path $ProjectRoot ".log-file-genius"
if (-not (Test-Path $SourceRoot)) {
    Print-Error "Log File Genius not found!"
    Write-Host ""
    Write-Host "Expected to find .log-file-genius\ in project root."
    Write-Host "Current directory: $ProjectRoot"
    Write-Host ""
    Write-Host "Please run this script from your project root, or install Log File Genius first:"
    Write-Host "  .\.log-file-genius\product\scripts\install.ps1"
    exit 1
}

# Update source repository
Print-Info "Updating Log File Genius source..."
Push-Location $SourceRoot
git fetch origin | Out-Null
$currentCommit = git rev-parse HEAD
$latestCommit = git rev-parse origin/main

if ($currentCommit -eq $latestCommit) {
    $shortCommit = git rev-parse --short HEAD
    Print-Success "Already up to date ($shortCommit)"
    Pop-Location
} else {
    $shortCurrent = git rev-parse --short HEAD
    $shortLatest = git rev-parse --short origin/main
    Print-Info "Updating from $shortCurrent to $shortLatest"
    git pull origin main | Out-Null
    Print-Success "Source updated"
    Pop-Location
}

Write-Host ""
Print-Info "Checking for file updates..."
Write-Host ""

# Detect AI assistant
function Detect-AiAssistant {
    if (Test-Path (Join-Path $ProjectRoot ".augment")) {
        return "augment"
    } elseif (Test-Path (Join-Path $ProjectRoot ".claude")) {
        return "claude-code"
    } elseif (Test-Path (Join-Path $ProjectRoot ".cursor")) {
        return "cursor"
    } else {
        return "unknown"
    }
}

$AiAssistant = Detect-AiAssistant
if ($AiAssistant -eq "unknown") {
    Print-Warning "Could not detect AI assistant"
    Write-Host "Skipping AI assistant rules update"
    Write-Host ""
} else {
    Print-Info "Detected AI assistant: $AiAssistant"
}

# Function to prompt for file update
function Prompt-Update {
    param(
        [string]$FileType,
        [string]$Source,
        [string]$Destination
    )
    
    if (-not (Test-Path $Source)) {
        return $false
    }
    
    if (-not (Test-Path $Destination)) {
        # File doesn't exist, just copy it
        Print-Info "New file available: $FileType"
        return $true
    }
    
    # Check if files are different
    $srcHash = Get-FileHash $Source -Algorithm MD5
    $destHash = Get-FileHash $Destination -Algorithm MD5
    
    if ($srcHash.Hash -eq $destHash.Hash) {
        # Files are identical, skip
        return $false
    }
    
    # Files are different, prompt user
    if ($Force) {
        return $true
    }
    
    Print-Warning "Update available: $FileType"
    Write-Host "  Source: $Source"
    Write-Host "  Destination: $Destination"
    $response = Read-Host "  Update this file? (y/N/d=diff)"
    
    if ($response -eq 'd' -or $response -eq 'D') {
        # Show diff (basic comparison)
        Write-Host ""
        Write-Host "=== Current File ===" -ForegroundColor Yellow
        Get-Content $Destination | Select-Object -First 20
        Write-Host ""
        Write-Host "=== New File ===" -ForegroundColor Green
        Get-Content $Source | Select-Object -First 20
        Write-Host ""
        $response = Read-Host "  Apply this update? (y/N)"
    }
    
    if ($response -eq 'y' -or $response -eq 'Y') {
        return $true
    } else {
        Print-Info "Skipped: $FileType"
        return $false
    }
}

# Update AI assistant rules
if ($AiAssistant -ne "unknown") {
    $RulesSrc = Join-Path $SourceRoot "product\starter-packs\$AiAssistant"
    
    if ($AiAssistant -eq "augment") {
        # Update Augment rules
        $rulesPath = Join-Path $RulesSrc ".augment\rules"
        if (Test-Path $rulesPath) {
            Get-ChildItem -Path $rulesPath -Filter "*.md" | ForEach-Object {
                $ruleName = $_.Name
                $srcFile = $_.FullName
                $destFile = Join-Path $ProjectRoot ".augment\rules\$ruleName"
                
                if (Prompt-Update "Augment rule: $ruleName" $srcFile $destFile) {
                    $destDir = Split-Path -Parent $destFile
                    if (-not (Test-Path $destDir)) {
                        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
                    }
                    Copy-Item -Path $srcFile -Destination $destFile -Force
                    Print-Success "Updated: $ruleName"
                }
            }
        }
    } elseif ($AiAssistant -eq "claude-code") {
        # Update Claude Code instructions
        $srcFile = Join-Path $RulesSrc ".claude\project_instructions.md"
        $destFile = Join-Path $ProjectRoot ".claude\project_instructions.md"
        
        if (Prompt-Update "Claude Code instructions" $srcFile $destFile) {
            $destDir = Split-Path -Parent $destFile
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path $srcFile -Destination $destFile -Force
            Print-Success "Updated: project_instructions.md"
        }
    }
}

# Update validation scripts
Print-Info "Checking validation scripts..."
$bashScript = Join-Path $SourceRoot "product\scripts\validate-log-files.sh"
$bashDest = Join-Path $ProjectRoot "scripts\validate-log-files.sh"
if (Prompt-Update "validate-log-files.sh" $bashScript $bashDest) {
    $destDir = Split-Path -Parent $bashDest
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item -Path $bashScript -Destination $bashDest -Force
    Print-Success "Updated: validate-log-files.sh"
}

$ps1Script = Join-Path $SourceRoot "product\scripts\validate-log-files.ps1"
$ps1Dest = Join-Path $ProjectRoot "scripts\validate-log-files.ps1"
if (Prompt-Update "validate-log-files.ps1" $ps1Script $ps1Dest) {
    $destDir = Split-Path -Parent $ps1Dest
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    Copy-Item -Path $ps1Script -Destination $ps1Dest -Force
    Print-Success "Updated: validate-log-files.ps1"
}

# Update templates (careful - users may have customized these)
Print-Info "Checking templates..."
Print-Warning "Note: Templates are often customized. Review changes carefully."
Write-Host ""

$templatesPath = Join-Path $SourceRoot "product\templates"
if (Test-Path $templatesPath) {
    Get-ChildItem -Path $templatesPath -Filter "*.md" | ForEach-Object {
        $templateName = $_.Name
        $srcTemplate = $_.FullName
        $destTemplate = Join-Path $ProjectRoot "templates\$templateName"
        
        if (Prompt-Update "Template: $templateName" $srcTemplate $destTemplate) {
            $destDir = Split-Path -Parent $destTemplate
            if (-not (Test-Path $destDir)) {
                New-Item -ItemType Directory -Path $destDir -Force | Out-Null
            }
            Copy-Item -Path $srcTemplate -Destination $destTemplate -Force
            Print-Success "Updated: $templateName"
        }
    }
}

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Update Complete!                     ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Print-Info "Your Log File Genius installation is up to date!"
Write-Host ""
Print-Info "Documentation: .log-file-genius\product\docs\"
Print-Info "Run validation: .\scripts\validate-log-files.ps1"
Write-Host ""

