#!/usr/bin/env pwsh
# Log File Genius Installer (PowerShell)
# Installs Log File Genius from .log-file-genius/ source to your project

param(
    [string]$Profile = "",
    [string]$AiAssistant = "",
    [switch]$Force = $false
)

$ErrorActionPreference = "Stop"

# Script directory detection
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceRoot = Resolve-Path (Join-Path $ScriptDir "../..")
$ProjectRoot = Get-Location

# Check if running from .log-file-genius/
if ($ScriptDir -notmatch '\.log-file-genius') {
    Write-Host "⚠️  Warning: This script should be run from .log-file-genius/product/scripts/" -ForegroundColor Yellow
    Write-Host "   Current location: $ScriptDir" -ForegroundColor Yellow
    Write-Host ""
    if (-not $Force) {
        $continue = Read-Host "Continue anyway? (y/N)"
        if ($continue -ne 'y' -and $continue -ne 'Y') {
            exit 1
        }
    }
}

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   Log File Genius Installer v1.0      ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Helper functions
function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Error {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

function Print-Info {
    param([string]$Message)
    Write-Host "ℹ $Message" -ForegroundColor Blue
}

# Check for incorrect installation
function Check-IncorrectInstallation {
    $productDir = Join-Path $ProjectRoot "product"
    $projectDir = Join-Path $ProjectRoot "project"
    
    if ((Test-Path $productDir) -or (Test-Path $projectDir)) {
        Print-Error "Detected incorrect installation!"
        Write-Host ""
        Write-Host "Found /product or /project folders in your project root."
        Write-Host "These are meta-directories for building Log File Genius itself."
        Write-Host "They should NOT be in your project."
        Write-Host ""
        $cleanup = Read-Host "Run cleanup script to fix this? (y/N)"
        if ($cleanup -eq 'y' -or $cleanup -eq 'Y') {
            & "$ScriptDir/cleanup.ps1"
            Write-Host ""
            Write-Host "Cleanup complete. Re-run this installer."
            exit 0
        } else {
            Write-Host "Please manually remove /product and /project folders before continuing."
            exit 1
        }
    }
}

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

# Prompt for AI assistant
function Prompt-AiAssistant {
    Write-Host "Which AI assistant are you using?" -ForegroundColor Blue
    Write-Host "1) Augment"
    Write-Host "2) Claude Code"
    Write-Host "3) Cursor (coming soon)"
    Write-Host "4) GitHub Copilot (coming soon)"
    Write-Host ""
    $choice = Read-Host "Enter choice (1-4)"
    
    switch ($choice) {
        "1" { return "augment" }
        "2" { return "claude-code" }
        "3" { return "cursor" }
        "4" { return "github-copilot" }
        default { return "augment" }
    }
}

# Prompt for profile
function Prompt-Profile {
    Write-Host ""
    Write-Host "Which profile fits your project best?" -ForegroundColor Blue
    Write-Host "1) solo-developer (default) - Individual developers, flexible"
    Write-Host "2) team - Teams of 2+, consistent documentation"
    Write-Host "3) open-source - Public projects, strict formatting"
    Write-Host "4) startup - MVPs/prototypes, minimal overhead"
    Write-Host ""
    $choice = Read-Host "Enter choice (1-4)"
    
    switch ($choice) {
        "1" { return "solo-developer" }
        "2" { return "team" }
        "3" { return "open-source" }
        "4" { return "startup" }
        default { return "solo-developer" }
    }
}

# Copy directory contents
function Copy-DirectoryContents {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (-not (Test-Path $Source)) {
        Print-Error "Source directory not found: $Source"
        return $false
    }
    
    if (-not (Test-Path $Destination)) {
        New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    }
    
    Copy-Item -Path "$Source\*" -Destination $Destination -Recurse -Force
    return $true
}

# Copy file
function Copy-FileItem {
    param(
        [string]$Source,
        [string]$Destination
    )
    
    if (-not (Test-Path $Source)) {
        Print-Error "Source file not found: $Source"
        return $false
    }
    
    $destDir = Split-Path -Parent $Destination
    if (-not (Test-Path $destDir)) {
        New-Item -ItemType Directory -Path $destDir -Force | Out-Null
    }
    
    Copy-Item -Path $Source -Destination $Destination -Force
    return $true
}

# Main installation
function Main {
    Print-Info "Starting installation..."
    Write-Host ""
    
    # Check for incorrect installation
    Check-IncorrectInstallation
    
    # Detect or prompt for AI assistant
    if ($AiAssistant -eq "") {
        $detectedAssistant = Detect-AiAssistant
        if ($detectedAssistant -eq "unknown") {
            $AiAssistant = Prompt-AiAssistant
        } else {
            $AiAssistant = $detectedAssistant
            Print-Info "Detected AI assistant: $AiAssistant"
        }
    }
    
    # Prompt for profile
    if ($Profile -eq "") {
        $Profile = Prompt-Profile
    }
    Print-Info "Selected profile: $Profile"
    Write-Host ""
    
    # Determine source paths
    $StarterPackDir = Join-Path $SourceRoot "product\starter-packs\$AiAssistant"
    $TemplatesDir = Join-Path $SourceRoot "product\templates"
    $ScriptsDir = Join-Path $SourceRoot "product\scripts"
    
    # Check if starter pack exists
    if (-not (Test-Path $StarterPackDir)) {
        Print-Error "Starter pack not found for $AiAssistant"
        Print-Info "Available starter packs:"
        Get-ChildItem (Join-Path $SourceRoot "product\starter-packs") -Directory | ForEach-Object { Write-Host "  - $($_.Name)" }
        exit 1
    }
    
    Print-Info "Installing from: $StarterPackDir"
    Write-Host ""
    
    # Install AI assistant configuration
    if ($AiAssistant -eq "augment") {
        $augmentSrc = Join-Path $StarterPackDir ".augment"
        $augmentDest = Join-Path $ProjectRoot ".augment"
        if (Copy-DirectoryContents $augmentSrc $augmentDest) {
            Print-Success "Installed Augment rules"
        }
    } elseif ($AiAssistant -eq "claude-code") {
        $claudeSrc = Join-Path $StarterPackDir ".claude"
        $claudeDest = Join-Path $ProjectRoot ".claude"
        if (Copy-DirectoryContents $claudeSrc $claudeDest) {
            Print-Success "Installed Claude Code configuration"
        }
    }
    
    # Install templates
    $templatesDest = Join-Path $ProjectRoot "templates"
    if (Copy-DirectoryContents $TemplatesDir $templatesDest) {
        Print-Success "Installed templates"
    }
    
    # Install validation scripts
    $scriptsDest = Join-Path $ProjectRoot "scripts"
    if (-not (Test-Path $scriptsDest)) {
        New-Item -ItemType Directory -Path $scriptsDest -Force | Out-Null
    }
    
    $bashScript = Join-Path $ScriptsDir "validate-log-files.sh"
    $bashDest = Join-Path $scriptsDest "validate-log-files.sh"
    if (Copy-FileItem $bashScript $bashDest) {
        Print-Success "Installed validation script (Bash)"
    }
    
    $ps1Script = Join-Path $ScriptsDir "validate-log-files.ps1"
    $ps1Dest = Join-Path $scriptsDest "validate-log-files.ps1"
    if (Copy-FileItem $ps1Script $ps1Dest) {
        Print-Success "Installed validation script (PowerShell)"
    }
    
    # Install profile configuration
    $configSrc = Join-Path $StarterPackDir ".logfile-config.yml"
    $configDest = Join-Path $ProjectRoot ".logfile-config.yml"
    if (Copy-FileItem $configSrc $configDest) {
        # Update profile in config file
        $content = Get-Content $configDest -Raw
        $content = $content -replace 'profile: .*', "profile: $Profile"
        Set-Content -Path $configDest -Value $content
        Print-Success "Installed profile configuration ($Profile)"
    }
    
    # Install git hooks (optional)
    $gitHooksSrc = Join-Path $StarterPackDir ".git-hooks"
    if (Test-Path $gitHooksSrc) {
        $gitHooksDest = Join-Path $ProjectRoot ".git-hooks"
        Copy-DirectoryContents $gitHooksSrc $gitHooksDest | Out-Null
        Print-Success "Installed git hook templates"
        Write-Host ""
        Print-Info "To enable git hooks, run:"
        Write-Host "  Copy-Item .git-hooks\pre-commit .git\hooks\pre-commit"
    }
    
    Write-Host ""
    Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║   Installation Complete! 🎉            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Print-Info "Next steps:"
    Write-Host "  1. Initialize your log files from templates:"
    Write-Host "     Copy-Item templates\CHANGELOG_template.md docs\planning\CHANGELOG.md"
    Write-Host "     Copy-Item templates\DEVLOG_template.md docs\planning\DEVLOG.md"
    Write-Host "     Copy-Item templates\ADR_template.md docs\adr\ADR-template.md"
    Write-Host ""
    Write-Host "  2. Customize the templates for your project"
    Write-Host ""
    Write-Host "  3. Start using your AI assistant - it will automatically maintain logs!"
    Write-Host ""
    Print-Info "Documentation: .log-file-genius\product\docs\"
    Print-Info "Run validation: .\scripts\validate-log-files.ps1"
    Write-Host ""
}

# Run main
Main

