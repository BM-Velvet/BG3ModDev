<#
.SYNOPSIS
    Removes the AppData junction for a mod.

.DESCRIPTION
    Removes the directory junction at $BG3_APPDATA_PATH\Mods\<ModName>.
    Does NOT delete any mod files in the repo.

.PARAMETER ModName
    Name of the mod.

.EXAMPLE
    .\tools\Unlink-Mod.ps1 -ModName BaldursGateInventory
#>

param(
    [Parameter(Mandatory)][string]$ModName
)

. "$PSScriptRoot\_common.ps1"
Load-Env

$modTarget = Join-Path $BG3_APPDATA_PATH "Mods\$ModName"

if (-not (Test-Path $modTarget)) {
    Write-Warn "Junction not found: $modTarget (nothing to remove)"
    exit 0
}

$item = Get-Item $modTarget -Force
if ($item.LinkType -ne "Junction") {
    Write-Error "Path exists but is not a junction: $modTarget`nNot removing — remove manually."
    exit 1
}

Remove-Item $modTarget -Force
Write-OK "Removed junction: $modTarget"
