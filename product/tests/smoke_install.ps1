# product/tests/smoke_install.ps1
# Cross-platform installer smoke test (PowerShell).
# Asserts a fresh install produces the expected files, config blocks, and
# frontmatter, and that the installed rule equals the canonical ai-rules source
# (install==update parity).

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

    # --- install==canonical parity ---
    # update.ps1 requires a git remote, so we verify the property directly:
    # installed rule must be byte-for-byte identical to the canonical source.
    $installedHash = (Get-FileHash ".claude\rules\log-file-maintenance.md" -Algorithm SHA256).Hash
    $canonicalHash = (Get-FileHash "$REPO\product\ai-rules\claude-code\log-file-maintenance.md" -Algorithm SHA256).Hash
    if ($installedHash -ne $canonicalHash) {
        throw "FAIL: installed rule != canonical ai-rules source (hash mismatch)"
    }

    # update.sh must source from ai-rules, not starter-packs
    $updateSh = Get-Content "$REPO\product\scripts\update.sh" -Raw
    if ($updateSh -notmatch 'product/ai-rules/\$AI_ASSISTANT') {
        throw "FAIL: update.sh does not source from ai-rules"
    }
    if ($updateSh -match 'starter-packs') {
        throw "FAIL: update.sh still references starter-packs"
    }

    Write-Host "PASS (powershell)"
}
finally {
    Set-Location $env:USERPROFILE
    Remove-Item -Recurse -Force $TMP -ErrorAction SilentlyContinue
}
