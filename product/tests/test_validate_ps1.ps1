$ErrorActionPreference = "Stop"
$tmp = Join-Path ([IO.Path]::GetTempPath()) ([Guid]::NewGuid())
New-Item -ItemType Directory -Path $tmp | Out-Null
New-Item -ItemType Directory -Path (Join-Path $tmp "alt") | Out-Null
Push-Location $tmp
# Quoted path + a trailing comment on the token_targets header exercise
# quote-stripping and the relaxed parent-header match.
@"
paths:
  changelog: "alt/CHANGELOG.md"
  devlog: alt/DEVLOG.md
token_targets:  # budgets
  changelog: 9000
  devlog: 13000
"@ | Set-Content -Path ".logfile-config.yml" -Encoding utf8
"# x" | Set-Content alt/CHANGELOG.md
"# x" | Set-Content alt/DEVLOG.md
$repo = $env:LFG_REPO
$out = & powershell -NoProfile -File (Join-Path $repo "product/scripts/validate-log-files.ps1") -PrintConfig
Pop-Location
Remove-Item -Recurse -Force $tmp
# Join array into a single string so -match/-notmatch work as substring tests
$outStr = $out -join "`n"
if ($outStr -notmatch "CHANGELOG_PATH=alt/CHANGELOG.md") { throw "path not read" }
if ($outStr -notmatch "CHANGELOG_TOKEN_ERROR=9000") { throw "token not read" }
if ($outStr -notmatch "CHANGELOG_TOKEN_WARNING=7200") { throw "warning not 80%" }
Write-Host "PASS"
