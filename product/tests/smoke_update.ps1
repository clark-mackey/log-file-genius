# product/tests/smoke_update.ps1
# Cross-platform UPDATE smoke test (PowerShell) — Spec 4 brownfield-safe update.
#
# The full update.ps1 needs a real .log-file-genius/ git submodule + `git fetch`,
# which is too heavy for a smoke test. We exercise the SPECIFIC new behaviors
# update.ps1 performs, via the same entrypoints:
#   - AGENTS.md merge:      lfg.py merge-agents-md --to <path>            (Spec 4 §1)
#   - root templates/ move: update_template_hashes.py --match-dir + the
#                           backup-move logic from update.ps1            (Spec 4 §3)
#
# Scenarios mirror smoke_update.sh:
#   1. v0.3.0 AGENTS.md (doc: AGENTS, no markers) -> wrapped.
#   2. LFG-installed root templates/ -> moved to .log-file-genius/.backups/.
#   3. user-authored AGENTS.md -> block prepended, content preserved.
#   4. user-authored root templates/ -> left in place.
#   5. Notepad CRLF+BOM v0.3.0 AGENTS.md -> wrapped + normalized (no BOM, LF).
#   6. repeated merge is a byte-identical no-op.

$ErrorActionPreference = "Stop"

$REPO        = Resolve-Path (Join-Path $PSScriptRoot "..\..")
$LFG_PY      = Join-Path $REPO "product\scripts\lfg.py"
$MATCH       = Join-Path $REPO "product\scripts\update_template_hashes.py"

$py = $null
if (Get-Command python -ErrorAction SilentlyContinue) { $py = "python" }
elseif (Get-Command python3 -ErrorAction SilentlyContinue) { $py = "python3" }
if (-not $py) { Write-Host "FAIL: python not found (required for merge)"; exit 1 }

function Fail($msg) { Write-Host "FAIL: $msg"; exit 1 }

function New-Tmp {
    $p = Join-Path ([System.IO.Path]::GetTempPath()) ([System.IO.Path]::GetRandomFileName())
    New-Item -ItemType Directory -Path $p | Out-Null
    return $p
}

function Get-V030Agents($dest) {
    # `git show` writes to stdout; capture as bytes-safe text and write LF.
    $content = & git -C $REPO show "v0.3.0:product/AGENTS.md"
    # $content is an array of lines (CRLF stripped by PowerShell); rejoin with LF.
    $text = ($content -join "`n") + "`n"
    [System.IO.File]::WriteAllText($dest, $text, (New-Object System.Text.UTF8Encoding($false)))
}

# Mirror update.ps1's backup-move logic. Returns the backup dir path if it moved,
# or $null if root templates/ was left in place / absent.
function Move-LfgTemplates($projectRoot) {
    $rootTemplates = Join-Path $projectRoot "templates"
    if (-not (Test-Path $rootTemplates -PathType Container)) { return $null }
    & $py $MATCH --match-dir $rootTemplates *> $null
    if ($LASTEXITCODE -eq 0) {
        $stamp = [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
        $rand  = Get-Random
        $backup = Join-Path $projectRoot ".log-file-genius\.backups\templates-$stamp-$rand"
        New-Item -ItemType Directory -Path (Split-Path $backup -Parent) -Force | Out-Null
        Move-Item -Path $rootTemplates -Destination $backup
        return $backup
    }
    return $null
}

$tmps = @()
try {
    # --- Scenario 1: v0.3.0 AGENTS.md (no markers) -> wrapped --------------
    $t1 = New-Tmp; $tmps += $t1
    $a1 = Join-Path $t1 "AGENTS.md"
    Get-V030Agents $a1
    $txt = [System.IO.File]::ReadAllText($a1)
    if ($txt -match 'LFG:BEGIN') { Fail "scenario 1: v0.3.0 fixture already has markers" }
    & $py $LFG_PY merge-agents-md --to $a1 *> $null
    $txt = [System.IO.File]::ReadAllText($a1)
    if ($txt -notmatch '<!-- LFG:BEGIN v') { Fail "scenario 1: BEGIN marker not added" }
    if ($txt -notmatch '<!-- LFG:END -->') { Fail "scenario 1: END marker not added" }
    if ($txt -notmatch '(?m)^doc: AGENTS$') { Fail "scenario 1: canonical body missing" }
    if (([regex]::Matches($txt, 'LFG:BEGIN')).Count -ne 1) { Fail "scenario 1: more than one BEGIN marker" }
    Write-Host "  ok scenario 1: v0.3.0 AGENTS.md wrapped"

    # --- Scenario 2: LFG-installed root templates/ -> moved ----------------
    $t2 = New-Tmp; $tmps += $t2
    New-Item -ItemType Directory -Path (Join-Path $t2 ".log-file-genius") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $t2 "templates") | Out-Null
    Copy-Item (Join-Path $REPO "product\templates\CHANGELOG_template.md") (Join-Path $t2 "templates\CHANGELOG_template.md")
    $backup = Move-LfgTemplates $t2
    if (Test-Path (Join-Path $t2 "templates") -PathType Container) { Fail "scenario 2: root templates/ still present" }
    if (-not $backup) { Fail "scenario 2: no backup dir reported" }
    if (-not (Test-Path $backup -PathType Container)) { Fail "scenario 2: backup dir does not exist" }
    if (-not (Test-Path (Join-Path $backup "CHANGELOG_template.md"))) { Fail "scenario 2: backed-up template missing" }
    if ($backup -notlike "*\.log-file-genius\.backups\templates-*") { Fail "scenario 2: backup not under .log-file-genius/.backups/" }
    Write-Host "  ok scenario 2: LFG-installed root templates/ moved to backups"

    # --- Scenario 3: user-authored AGENTS.md -> block prepended ------------
    $t3 = New-Tmp; $tmps += $t3
    $a3 = Join-Path $t3 "AGENTS.md"
    $sentinel = "USER_SENTINEL_4f3a9b_KEEP_ME"
    [System.IO.File]::WriteAllText($a3, "# My Project Agent Notes`n`n$sentinel - custom team instructions.`n", (New-Object System.Text.UTF8Encoding($false)))
    & $py $LFG_PY merge-agents-md --to $a3 *> $null
    $txt = [System.IO.File]::ReadAllText($a3)
    if ($txt -notmatch [regex]::Escape($sentinel)) { Fail "scenario 3: user sentinel lost (data loss!)" }
    if ($txt -notmatch '<!-- LFG:BEGIN v') { Fail "scenario 3: BEGIN marker not prepended" }
    if ($txt -notmatch '<!-- LFG:END -->') { Fail "scenario 3: END marker missing" }
    $beginIdx = $txt.IndexOf("LFG:BEGIN")
    $sentIdx  = $txt.IndexOf($sentinel)
    if ($beginIdx -ge $sentIdx) { Fail "scenario 3: block not prepended above user content" }
    Write-Host "  ok scenario 3: user-authored AGENTS.md preserved, block prepended above"

    # --- Scenario 4: user-authored root templates/ -> left in place --------
    $t4 = New-Tmp; $tmps += $t4
    New-Item -ItemType Directory -Path (Join-Path $t4 ".log-file-genius") | Out-Null
    New-Item -ItemType Directory -Path (Join-Path $t4 "templates") | Out-Null
    [System.IO.File]::WriteAllText((Join-Path $t4 "templates\my_template.md"), "my own template content - not shipped by LFG $(Get-Random)`n", (New-Object System.Text.UTF8Encoding($false)))
    $backup4 = Move-LfgTemplates $t4
    if (-not (Test-Path (Join-Path $t4 "templates") -PathType Container)) { Fail "scenario 4: user templates/ was moved" }
    if (-not (Test-Path (Join-Path $t4 "templates\my_template.md"))) { Fail "scenario 4: user template file disappeared" }
    if ($backup4) { Fail "scenario 4: a backup was created for user-authored templates" }
    if (Test-Path (Join-Path $t4 ".log-file-genius\.backups") -PathType Container) { Fail "scenario 4: backups dir created for user templates" }
    Write-Host "  ok scenario 4: user-authored root templates/ left in place"

    # --- Scenario 5: Notepad CRLF+BOM v0.3.0 AGENTS.md -> wrapped+normalized -
    $t5 = New-Tmp; $tmps += $t5
    $lf5 = Join-Path $t5 "lf.md"
    $a5  = Join-Path $t5 "AGENTS.md"
    Get-V030Agents $lf5
    # Re-encode as UTF-8 BOM + CRLF (simulating a Notepad save on Windows).
    $body = [System.IO.File]::ReadAllText($lf5)
    $crlf = $body -replace "`n", "`r`n"
    $bom  = [byte[]](0xEF,0xBB,0xBF)
    $bytes = $bom + [System.Text.Encoding]::UTF8.GetBytes($crlf)
    [System.IO.File]::WriteAllBytes($a5, $bytes)
    # Sanity: fixture has a BOM and CR bytes.
    $raw = [System.IO.File]::ReadAllBytes($a5)
    if (-not ($raw[0] -eq 0xEF -and $raw[1] -eq 0xBB -and $raw[2] -eq 0xBF)) { Fail "scenario 5: fixture missing BOM" }
    if (-not ($raw -contains 0x0D)) { Fail "scenario 5: fixture missing CRLF" }
    & $py $LFG_PY merge-agents-md --to $a5 *> $null
    $raw = [System.IO.File]::ReadAllBytes($a5)
    $txt = [System.Text.Encoding]::UTF8.GetString($raw)
    if ($txt -notmatch '<!-- LFG:BEGIN v') { Fail "scenario 5: markers not detected/added" }
    if ($raw.Length -ge 3 -and $raw[0] -eq 0xEF -and $raw[1] -eq 0xBB -and $raw[2] -eq 0xBF) { Fail "scenario 5: BOM not stripped on write" }
    if ($raw -contains 0x0D) { Fail "scenario 5: CRLF not normalized to LF" }
    Write-Host "  ok scenario 5: Notepad CRLF+BOM v0.3.0 file wrapped and normalized"

    # --- Scenario 6: repeated merge is a byte-identical no-op --------------
    $before = [System.IO.File]::ReadAllBytes($a1)
    $out6 = & $py $LFG_PY merge-agents-md --to $a1 2>&1 | Out-String
    if ($out6 -notmatch 'up to date') { Fail "scenario 6: re-merge did not report up-to-date: $out6" }
    $after = [System.IO.File]::ReadAllBytes($a1)
    if (-not ([System.Linq.Enumerable]::SequenceEqual($before, $after))) { Fail "scenario 6: re-merge changed the file (not idempotent)" }
    Write-Host "  ok scenario 6: repeated merge is a byte-identical no-op"

    Write-Host "PASS (powershell)"
}
finally {
    foreach ($t in $tmps) {
        if ($t -and (Test-Path $t)) { Remove-Item -Recurse -Force $t -ErrorAction SilentlyContinue }
    }
}
