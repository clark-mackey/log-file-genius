#!/usr/bin/env pwsh
# check-for-updates.ps1
# Check for Log File Genius updates from GitHub releases

param(
    [switch]$Verbose
)

# Colors
$COLOR_SUCCESS = "Green"
$COLOR_WARNING = "Yellow"
$COLOR_ERROR = "Red"
$COLOR_INFO = "Cyan"

# GitHub repository
$REPO_OWNER = "clark-mackey"
$REPO_NAME = "log-file-genius"
$RELEASES_URL = "https://api.github.com/repos/$REPO_OWNER/$REPO_NAME/releases/latest"

Write-Host ""
Write-Host "🔍 Checking for Log File Genius updates..." -ForegroundColor $COLOR_INFO
Write-Host ""

# Read current version from config file
$configPaths = @(
    ".logfile-config.yml",
    "config/logfile.yml",
    ".config/logfile.yml"
)

$configFile = $null
$currentVersion = $null

foreach ($path in $configPaths) {
    if (Test-Path $path) {
        $configFile = $path
        $content = Get-Content $path -Raw
        if ($content -match 'log_file_genius_version:\s*"?([0-9.]+)"?') {
            $currentVersion = $matches[1]
        }
        break
    }
}

if (-not $currentVersion) {
    Write-Host "⚠️  No .logfile-config.yml found or version not specified" -ForegroundColor $COLOR_WARNING
    Write-Host "   Current version: Unknown" -ForegroundColor $COLOR_WARNING
    Write-Host ""
} else {
    Write-Host "📦 Current version: v$currentVersion" -ForegroundColor $COLOR_INFO
    Write-Host ""
}

# Fetch latest release from GitHub
try {
    if ($Verbose) {
        Write-Host "Fetching latest release from GitHub..." -ForegroundColor $COLOR_INFO
    }
    
    $response = Invoke-RestMethod -Uri $RELEASES_URL -ErrorAction Stop
    $latestVersion = $response.tag_name -replace '^v', ''
    $releaseName = $response.name
    $releaseUrl = $response.html_url
    $publishedAt = [DateTime]::Parse($response.published_at).ToString("yyyy-MM-dd")
    
    Write-Host "🌟 Latest version: v$latestVersion" -ForegroundColor $COLOR_SUCCESS
    Write-Host "   Release: $releaseName" -ForegroundColor $COLOR_INFO
    Write-Host "   Published: $publishedAt" -ForegroundColor $COLOR_INFO
    Write-Host ""
    
    # Compare versions
    if ($currentVersion -and $currentVersion -eq $latestVersion) {
        Write-Host "✅ You're up to date!" -ForegroundColor $COLOR_SUCCESS
        Write-Host ""
    } elseif ($currentVersion) {
        Write-Host "🔔 Update available: v$currentVersion → v$latestVersion" -ForegroundColor $COLOR_WARNING
        Write-Host ""
        Write-Host "📝 Release notes:" -ForegroundColor $COLOR_INFO
        Write-Host "   $releaseUrl" -ForegroundColor $COLOR_INFO
        Write-Host ""
        
        # Show release body (first 500 chars)
        if ($response.body) {
            $body = $response.body
            if ($body.Length -gt 500) {
                $body = $body.Substring(0, 500) + "..."
            }
            Write-Host "Summary:" -ForegroundColor $COLOR_INFO
            Write-Host $body
            Write-Host ""
        }
        
        Write-Host "To update:" -ForegroundColor $COLOR_INFO
        Write-Host "1. Review release notes: $releaseUrl" -ForegroundColor $COLOR_INFO
        Write-Host "2. Check migration guide (if provided)" -ForegroundColor $COLOR_INFO
        Write-Host "3. Update your .logfile-config.yml version to: $latestVersion" -ForegroundColor $COLOR_INFO
        Write-Host "4. Pull updated files from the repository" -ForegroundColor $COLOR_INFO
        Write-Host ""
    } else {
        Write-Host "📝 Latest release:" -ForegroundColor $COLOR_INFO
        Write-Host "   $releaseUrl" -ForegroundColor $COLOR_INFO
        Write-Host ""
    }
    
} catch {
    Write-Host "❌ Failed to check for updates" -ForegroundColor $COLOR_ERROR
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor $COLOR_ERROR
    Write-Host ""
    Write-Host "   You can manually check for updates at:" -ForegroundColor $COLOR_INFO
    Write-Host "   https://github.com/$REPO_OWNER/$REPO_NAME/releases" -ForegroundColor $COLOR_INFO
    Write-Host ""
    exit 1
}

exit 0

