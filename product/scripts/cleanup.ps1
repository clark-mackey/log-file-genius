#!/usr/bin/env pwsh
# Log File Genius Cleanup Script (PowerShell)
# Removes incorrectly installed /product and /project folders

$ErrorActionPreference = "Stop"
$ProjectRoot = Get-Location

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Blue
Write-Host "║   Log File Genius Cleanup Script      ║" -ForegroundColor Blue
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Blue
Write-Host ""

# Check if product or project folders exist
$productDir = Join-Path $ProjectRoot "product"
$projectDir = Join-Path $ProjectRoot "project"

if (-not (Test-Path $productDir) -and -not (Test-Path $projectDir)) {
    Write-Host "[OK] No incorrect installation detected." -ForegroundColor Green
    Write-Host "Your project looks clean!"
    exit 0
}

Write-Host "[WARNING] Detected incorrect installation:" -ForegroundColor Yellow
if (Test-Path $productDir) { Write-Host "  - /product folder found" }
if (Test-Path $projectDir) { Write-Host "  - /project folder found" }
Write-Host ""
Write-Host "These folders are meta-directories for building Log File Genius itself."
Write-Host "They should NOT be in your project root."
Write-Host ""

# Show what will be removed
Write-Host "The following will be removed:" -ForegroundColor Blue
if (Test-Path $productDir) { Write-Host "  - $productDir" }
if (Test-Path $projectDir) { Write-Host "  - $projectDir" }
Write-Host ""

# Confirm
$confirm = Read-Host "Proceed with cleanup? (y/N)"
if ($confirm -ne 'y' -and $confirm -ne 'Y') {
    Write-Host "Cleanup cancelled."
    exit 0
}

# Remove folders
if (Test-Path $productDir) {
    Remove-Item -Path $productDir -Recurse -Force
    Write-Host "[OK] Removed /product folder" -ForegroundColor Green
}

if (Test-Path $projectDir) {
    Remove-Item -Path $projectDir -Recurse -Force
    Write-Host "[OK] Removed /project folder" -ForegroundColor Green
}

Write-Host ""
Write-Host "╔════════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║   Cleanup Complete!                    ║" -ForegroundColor Green
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor Green
Write-Host ""
Write-Host "[INFO] Next steps:" -ForegroundColor Blue
Write-Host "  1. Ensure .log-file-genius\ submodule is properly installed"
Write-Host "  2. Run the installer: .\.log-file-genius\product\scripts\install.ps1"
Write-Host ""

