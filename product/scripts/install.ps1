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
    # -Profile remains the public CLI flag for backward compatibility; the
    # internal variable is renamed to $ProjectProfile so it doesn't shadow
    # PowerShell's $Profile automatic variable (path to the user profile script).
    [Alias('Profile')]
    [string]$ProjectProfile = "",
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
Write-Host "+========================================+" -ForegroundColor Blue
Write-Host "|   Log File Genius Installer v$VERSION      |" -ForegroundColor Blue
Write-Host "+========================================+" -ForegroundColor Blue
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

if (-not $ProjectProfile) {
    Write-Host ""
    Write-Host "Select your project profile:"
    Write-Host "  1) solo-developer  - Individual developers (flexible, minimal overhead)"
    Write-Host "  2) team            - Teams of 2+ developers (consistent docs)"
    Write-Host "  3) open-source     - Public projects (strict formatting)"
    Write-Host "  4) startup         - Fast-moving startups (minimal overhead)"
    Write-Host ""
    $choice = Read-Host "Enter choice (1-4)"
    
    switch ($choice) {
        "1" { $ProjectProfile = "solo-developer" }
        "2" { $ProjectProfile = "team" }
        "3" { $ProjectProfile = "open-source" }
        "4" { $ProjectProfile = "startup" }
        default {
            Print-Error "Invalid choice. Exiting."
            exit 1
        }
    }
}

Print-Success "Profile: $ProjectProfile"
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
    "logs/incidents"  # standalone incident reports (Spec 5)
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
    "templates/INCIDENT_template.md" = "logs/incidents/TEMPLATE.md"
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

# Seed a STATIC empty-state incidents index README. We deliberately do NOT run
# `lfg incidents-index` here: seeding via the CLI would add a python dependency
# to a path that does not otherwise require one. This placeholder carries the
# LFG:INCIDENTS-INDEX generated-marker, so the first real `lfg incidents-index`
# run overwrites it in place (no .bak). The content mirrors
# incidents.build_index's empty-dir output byte-for-byte. Written no-BOM, LF.
$incidentsReadme = @"
---
doc: INCIDENTS-INDEX
related:
  changelog: ../CHANGELOG.md
  devlog: ../DEVLOG.md
  state: ../STATE.md
---


<!-- LFG:INCIDENTS-INDEX generated by lfg incidents-index -->

# Incident Reports

Standalone incident reports for this project, newest first. Generated by ``lfg incidents-index``.

_No incidents recorded yet._
"@
# Normalize to LF and guarantee a single trailing newline so the file matches
# incidents.build_index's output byte-for-byte (the closing "@ drops the final
# newline, so append one explicitly).
$incidentsReadme = ($incidentsReadme -replace "`r`n", "`n") + "`n"
[System.IO.File]::WriteAllText((Join-Path $ProjectRoot "logs/incidents/README.md"), $incidentsReadme, (New-Object System.Text.UTF8Encoding $false))
$CreatedItems += "logs/incidents/README.md"
Print-Success "Seeded logs/incidents/README.md (empty-state index)"

# ============================================================================
# INSTALL AI RULES
# ============================================================================

Print-Info "Installing AI assistant rules..."

switch ($AiAssistant) {
    "augment"     { $rulesTarget = "augment_rules"; $rulesDest = Join-Path $ProjectRoot ".augment\rules" }
    "claude-code" { $rulesTarget = "claude_rules";  $rulesDest = Join-Path $ProjectRoot ".claude\rules"  }
    default       { Rollback-Installation "Unknown assistant: $AiAssistant" }
}

if (-not (Test-Path $rulesDest)) {
    New-Item -ItemType Directory -Path $rulesDest -Force | Out-Null
}
$CreatedItems += $rulesDest

Get-ChildItem -Path (Join-Path $SourceRoot "rules") -Filter "*.md" | ForEach-Object {
    $text = Get-Content $_.FullName -Raw
    # Extract frontmatter block (between the first two '---' lines).
    if ($text -match "(?ms)^---\s*\r?\n(.*?)\r?\n---") {
        $fm = $Matches[1]
        if ($fm -match "(?m)^targets:\s*(.+)$") {
            $targets = ($Matches[1] -replace '\[|\]','' -split ',' | ForEach-Object { $_.Trim() })
            if ($targets -contains $rulesTarget) {
                $dest = Join-Path $rulesDest $_.Name
                Copy-Item -Path $_.FullName -Destination $dest -Force
                $CreatedItems += $dest
                Print-Success "Installed $($_.Name)"
            }
        }
    }
}

if ($AiAssistant -eq "claude-code") {
    $tmpl = Join-Path $SourceRoot "install-templates\claude\project_instructions.md.tmpl"
    $dest = Join-Path $ProjectRoot ".claude\project_instructions.md"
    $rendered = (Get-Content $tmpl -Raw) `
        -replace '\{\{paths\.changelog\}\}','logs/CHANGELOG.md' `
        -replace '\{\{paths\.devlog\}\}','logs/DEVLOG.md' `
        -replace '\{\{paths\.state\}\}','logs/STATE.md' `
        -replace '\{\{paths\.adr_dir\}\}','logs/adr/'
    # Spec requires no BOM. Windows PowerShell 5.1's `Set-Content -Encoding utf8`
    # writes UTF-8 *with* BOM, so use .NET directly with a no-BOM encoding.
    [System.IO.File]::WriteAllText($dest, $rendered, (New-Object System.Text.UTF8Encoding $false))
    $CreatedItems += $dest
    Print-Success "Rendered .claude/project_instructions.md"
}

# Merge the canonical managed block into the project-root AGENTS.md.
# Brownfield-safe: the merge CLI (lfg.py merge-agents-md) builds the
# marker-wrapped block from product/rules/ and either creates the file,
# refreshes the managed block in place, wraps a pre-marker LFG body, or
# prepends above user content (printing which case applied). It writes
# UTF-8 LF no-BOM and is idempotent. Never clobbers user-owned content.
$lfgPy = Join-Path $ScriptDir "lfg.py"
$agentsDest = Join-Path $ProjectRoot "AGENTS.md"
$agentsPreexisting = Test-Path $agentsDest

# Resolve a python interpreter the same way validate-log-files.ps1 does.
$python = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $python = "python" }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $python = "python3" }

if ($python -and (Test-Path $lfgPy)) {
    & $python $lfgPy merge-agents-md --to $agentsDest
    if ($LASTEXITCODE -eq 0) {
        # Only track for rollback if WE created it — merging into a pre-existing
        # user file must never be rolled back (that would lose their content).
        if (-not $agentsPreexisting) { $CreatedItems += $agentsDest }
        Print-Success "Merged AGENTS.md managed block at project root"
    }
    else {
        # Non-zero = corrupt marker or forward-version block; the merge left the
        # file untouched. Don't abort the install — everything else succeeded.
        Print-Warning "AGENTS.md was left as-is (merge could not complete safely)."
        Print-Warning "Resolve it manually, then re-run: $python `"$lfgPy`" merge-agents-md --to `"$agentsDest`""
    }
}
else {
    # No python available: degrade gracefully. Only fall back to the old copy
    # behavior when the target does NOT already exist — never overwrite an
    # existing AGENTS.md without the merge (preserves the no-data-loss guarantee).
    $agentsSrc = Join-Path $SourceRoot "AGENTS.md"
    if ($agentsPreexisting) {
        Print-Warning "python not found and AGENTS.md already exists; skipped (will not overwrite)."
        Print-Warning "Install python and re-run: <python> `"$lfgPy`" merge-agents-md --to `"$agentsDest`""
    }
    elseif (Test-Path $agentsSrc) {
        # Re-emit with LF + no BOM in case the source was checked out CRLF.
        $agentsText = (Get-Content $agentsSrc -Raw) -replace "`r`n", "`n"
        [System.IO.File]::WriteAllText($agentsDest, $agentsText, (New-Object System.Text.UTF8Encoding $false))
        $CreatedItems += $agentsDest
        Print-Warning "python not found; copied AGENTS.md verbatim (no managed-block merge)."
        Print-Success "Installed AGENTS.md at project root"
    }
}

# ============================================================================
# CREATE CONFIG FILE
# ============================================================================

Print-Info "Creating .logfile-config.yml..."

$configContent = @"
# Log File Genius Configuration
# All log files are in /logs/ folder (standard structure)

log_file_genius_version: "$VERSION"
profile: $ProjectProfile
ai_assistant: $AiAssistant

paths:
  changelog: logs/CHANGELOG.md
  devlog: logs/DEVLOG.md
  state: logs/STATE.md
  adr_dir: logs/adr/
  incidents_dir: logs/incidents/

token_targets:
  changelog: 10000
  devlog: 15000
  combined: 25000
  state: 500

# Presets and customization: .log-file-genius/product/profiles/*.yml
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
Print-Info "Documentation: .log-file-genius/product/docs/log_file_how_to.md"
Write-Host ""
