#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Validates Log File Genius CHANGELOG and DEVLOG files (thin wrapper)

.DESCRIPTION
    Calls the unified Python CLI for validation.
    This is a thin wrapper to maintain PowerShell compatibility.

.EXAMPLE
    .\validate.ps1
    .\validate.ps1 -Verbose
    .\validate.ps1 -Changelog
#>

param(
    [switch]$Changelog,
    [switch]$Devlog,
    [switch]$Tokens,
    [switch]$Verbose,
    [switch]$Json
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$LfgPath = Join-Path $ScriptDir "lfg.py"

$args = @("validate")
if ($Changelog) { $args += "--changelog" }
if ($Devlog) { $args += "--devlog" }
if ($Tokens) { $args += "--tokens" }
if ($Verbose) { $args += "--verbose" }
if ($Json) { $args += "--json" }

python $LfgPath @args
exit $LASTEXITCODE

