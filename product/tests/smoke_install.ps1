# product/tests/smoke_install.ps1
# Cross-platform installer smoke test (PowerShell).
# Asserts a fresh install produces the expected files, config blocks,
# frontmatter, AGENTS.md (LF + no BOM), and that the installed rule equals
# the canonical fragment (install==update parity).

$ErrorActionPreference = "Stop"

$REPO = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$TMP  = [System.IO.Path]::GetTempPath()
$TMP  = Join-Path $TMP ([System.IO.Path]::GetRandomFileName())
New-Item -ItemType Directory -Path $TMP | Out-Null

try {
    Set-Location $TMP
    New-Item -ItemType Directory -Path ".claude" | Out-Null

    # Run the real installer.  install.ps1 resolves SourceRoot as $ScriptDir/..
    # which equals $REPO/product when invoked via the real repo path, so
    # templates and ai-rules are sourced from the real repo.
    powershell -NoProfile -File "$REPO\product\scripts\install.ps1" `
        -Profile solo-developer `
        -AiAssistant claude-code `
        -Force | Out-Null

    # --- File existence ---
    $expectedFiles = @(
        "logs\CHANGELOG.md",
        "logs\DEVLOG.md",
        "logs\STATE.md",
        ".logfile-config.yml",
        ".claude\rules\log-file-maintenance.md"
    )
    foreach ($f in $expectedFiles) {
        if (-not (Test-Path $f)) {
            throw "FAIL: missing $f"
        }
    }
    if (-not (Test-Path "logs\adr" -PathType Container)) {
        throw "FAIL: missing logs\adr directory"
    }

    # --- Config blocks ---
    $configContent = Get-Content ".logfile-config.yml" -Raw
    if ($configContent -notmatch '(?m)^paths:') {
        throw "FAIL: no paths block in .logfile-config.yml"
    }
    if ($configContent -notmatch '(?m)^token_targets:') {
        throw "FAIL: no token_targets block in .logfile-config.yml"
    }

    # --- Frontmatter ---
    $firstLine = (Get-Content "logs\CHANGELOG.md" -TotalCount 1)
    if ($firstLine -ne "---") {
        throw "FAIL: CHANGELOG.md missing frontmatter (first line is '$firstLine')"
    }

    # Spec 2: AGENTS.md at project root with frontmatter.
    if (-not (Test-Path "AGENTS.md")) { Write-Host "FAIL: AGENTS.md missing at project root"; exit 1 }
    $firstLine = (Get-Content "AGENTS.md" -TotalCount 1)
    if ($firstLine -ne "---") { Write-Host "FAIL: AGENTS.md missing frontmatter"; exit 1 }

    # Spec 2: AGENTS.md must be LF + no BOM.
    $bytes = [System.IO.File]::ReadAllBytes("$pwd\AGENTS.md")
    if ($bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF) {
        Write-Host "FAIL: AGENTS.md has UTF-8 BOM"; exit 1
    }
    $text = [System.IO.File]::ReadAllText("$pwd\AGENTS.md")
    if ($text.Contains("`r`n")) { Write-Host "FAIL: AGENTS.md has CRLF line endings"; exit 1 }

    # Spec 2: installed rule == canonical fragment.
    $installed = (Get-FileHash ".claude\rules\log-file-maintenance.md").Hash
    $canonical = (Get-FileHash "$REPO\product\rules\log-file-maintenance.md").Hash
    if ($installed -ne $canonical) { Write-Host "FAIL: installed rule != canonical fragment"; exit 1 }

    # update.sh must not reference starter-packs
    $updateSh = Get-Content "$REPO\product\scripts\update.sh" -Raw
    if ($updateSh -match 'starter-packs') {
        throw "FAIL: update.sh still references starter-packs"
    }

    Write-Host "PASS (powershell)"
}
finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Recurse -Force $TMP -ErrorAction SilentlyContinue
}
