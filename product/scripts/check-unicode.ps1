# Check for Unicode characters that may cause encoding issues
# Usage: .\check-unicode.ps1 [-Fix]

param(
    [switch]$Fix = $false
)

$ErrorActionPreference = "Stop"

# Unicode characters to check for (using Unicode escape sequences to avoid encoding issues)
$unicodeChars = @{
    "$([char]0x2192)" = '->'  # RIGHTWARDS ARROW
    "$([char]0x2190)" = '<-'  # LEFTWARDS ARROW
    "$([char]0x2191)" = '^'   # UPWARDS ARROW
    "$([char]0x2193)" = 'v'   # DOWNWARDS ARROW
    "$([char]0x2022)" = '-'   # BULLET
    "$([char]0x2713)" = '[OK]'      # CHECK MARK
    "$([char]0x2717)" = '[X]'       # BALLOT X
    "$([char]0x26A0)" = '[WARNING]' # WARNING SIGN
    "$([char]0x2139)" = '[INFO]'    # INFORMATION SOURCE
}

# Files to check (relative to repo root)
$filesToCheck = @(
    'logs\CHANGELOG.md',
    'logs\DEVLOG.md',
    'logs\ai-usage-log.md',
    'logs\adr\*.md',
    'logs\archive\*.md',
    'README.md',
    'INSTALL.md',
    'product\docs\*.md',
    'product\templates\*.md'
)

Write-Host "Checking for Unicode characters that may cause encoding issues..." -ForegroundColor Cyan
Write-Host ""

$issuesFound = @()
$filesChecked = 0

foreach ($pattern in $filesToCheck) {
    $files = Get-ChildItem -Path $pattern -ErrorAction SilentlyContinue
    
    foreach ($file in $files) {
        $filesChecked++
        $content = Get-Content $file.FullName -Raw -Encoding UTF8
        
        $fileIssues = @()
        foreach ($char in $unicodeChars.Keys) {
            if ($content -match [regex]::Escape($char)) {
                $count = ([regex]::Matches($content, [regex]::Escape($char))).Count
                $fileIssues += "$count x '$char'"
            }
        }
        
        if ($fileIssues.Count -gt 0) {
            $relativePath = $file.FullName.Replace((Get-Location).Path + '\', '')
            $issuesFound += [PSCustomObject]@{
                File = $relativePath
                Issues = $fileIssues -join ', '
                FullPath = $file.FullName
            }
        }
    }
}

if ($issuesFound.Count -eq 0) {
    Write-Host "[OK] No problematic Unicode characters found in $filesChecked files!" -ForegroundColor Green
    exit 0
}

Write-Host "Found Unicode characters in $($issuesFound.Count) file(s):" -ForegroundColor Yellow
Write-Host ""

$issuesFound | Format-Table -AutoSize

if ($Fix) {
    Write-Host ""
    Write-Host "Fixing Unicode characters..." -ForegroundColor Cyan
    
    foreach ($issue in $issuesFound) {
        $content = Get-Content $issue.FullPath -Raw -Encoding UTF8
        $modified = $false
        
        foreach ($char in $unicodeChars.Keys) {
            if ($content -match [regex]::Escape($char)) {
                $content = $content.Replace($char, $unicodeChars[$char])
                $modified = $true
            }
        }
        
        if ($modified) {
            # Write with UTF-8 encoding, Unix line endings
            $content | Set-Content $issue.FullPath -Encoding UTF8 -NoNewline
            Write-Host "  Fixed: $($issue.File)" -ForegroundColor Green
        }
    }
    
    Write-Host ""
    Write-Host "[OK] All Unicode characters replaced with ASCII equivalents!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "To automatically fix these issues, run:" -ForegroundColor Yellow
    Write-Host "  .\product\scripts\check-unicode.ps1 -Fix" -ForegroundColor White
    Write-Host ""
    Write-Host "Note: Some Unicode characters (like • in navigation) may be intentional." -ForegroundColor Gray
    Write-Host "Review changes before committing!" -ForegroundColor Gray
}

exit 0

