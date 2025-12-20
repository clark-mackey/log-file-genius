# Claude Code Installation Module for Log File Genius
# Add this to product/scripts/install.ps1

function Install-ClaudeCode {
    Write-Host "🤖 Installing Claude Code support..." -ForegroundColor Cyan
    
    $TemplateDir = Join-Path $PSScriptRoot "..\templates\.claude"
    $TargetDir = ".claude"
    
    # Create .claude directory structure
    New-Item -ItemType Directory -Path "$TargetDir\commands" -Force | Out-Null
    New-Item -ItemType Directory -Path "$TargetDir\rules" -Force | Out-Null
    
    # Copy CLAUDE.md to project root
    if (-not (Test-Path "CLAUDE.md")) {
        Copy-Item (Join-Path $PSScriptRoot "..\templates\CLAUDE.md") "CLAUDE.md"
        Write-Host "  ✅ Created CLAUDE.md" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  CLAUDE.md already exists, skipping" -ForegroundColor Yellow
    }
    
    # Copy slash commands
    $commands = @("devlog-entry", "changelog-entry", "adr-create", "state-update")
    foreach ($cmd in $commands) {
        $targetPath = "$TargetDir\commands\$cmd.md"
        if (-not (Test-Path $targetPath)) {
            Copy-Item "$TemplateDir\commands\$cmd.md" $targetPath
            Write-Host "  ✅ Installed /project:$cmd command" -ForegroundColor Green
        }
    }
    
    # Copy rules
    $rules = @("logging", "handoff-protocol")
    foreach ($rule in $rules) {
        $targetPath = "$TargetDir\rules\$rule.md"
        if (-not (Test-Path $targetPath)) {
            Copy-Item "$TemplateDir\rules\$rule.md" $targetPath
            Write-Host "  ✅ Installed $rule rules" -ForegroundColor Green
        }
    }
    
    # Copy hooks (with backup if exists)
    $hooksPath = "$TargetDir\hooks.json"
    if (Test-Path $hooksPath) {
        Copy-Item $hooksPath "$hooksPath.backup"
        Write-Host "  ⚠️  Backed up existing hooks.json" -ForegroundColor Yellow
    }
    Copy-Item "$TemplateDir\hooks.json" $hooksPath
    Write-Host "  ✅ Installed hooks.json" -ForegroundColor Green
    
    Write-Host "`n✅ Claude Code support installed!" -ForegroundColor Green
    Write-Host "`nAvailable slash commands:"
    Write-Host "  /project:devlog-entry    - Add narrative entry"
    Write-Host "  /project:changelog-entry - Add factual entry"
    Write-Host "  /project:adr-create      - Create decision record"
    Write-Host "  /project:state-update    - Update project state"
}

function Test-ClaudeCode {
    # Check for Claude Code CLI
    if (Get-Command "claude" -ErrorAction SilentlyContinue) {
        return $true
    }
    
    # Check for existing .claude directory
    if (Test-Path ".claude") {
        return $true
    }
    
    # Check for Claude Code config in home
    if (Test-Path "$env:USERPROFILE\.claude") {
        return $true
    }
    
    return $false
}

# Add to main installer detection logic:
# if (Test-ClaudeCode) {
#     Install-ClaudeCode
# }
