<#
.SYNOPSIS
    Creates an AppData directory junction for a mod so BG3 picks it up live.

.DESCRIPTION
    Links:
        $BG3_APPDATA_PATH\Mods\<ModName>  →  mods\<ModName>\Mod

    Requires admin rights (directory junctions need elevation on Windows).
    Idempotent — safe to re-run if the junction already exists.

.PARAMETER ModName
    Name of the mod subfolder inside mods\.

.EXAMPLE
    .\tools\Link-Mod.ps1 -ModName BaldursGateInventory
#>

param(
    [Parameter(Mandatory)][string]$ModName
)

. "$PSScriptRoot\_common.ps1"
Load-Env

$modSource = Join-Path $REPO_ROOT "mods\$ModName\Mod"
$modTarget = Join-Path $BG3_APPDATA_PATH "Mods\$ModName"

if (-not (Test-Path $modSource)) {
    Write-Error "Mod source not found: $modSource"
    exit 1
}

if (Test-Path $modTarget) {
    $item = Get-Item $modTarget -Force
    if ($item.LinkType -eq "Junction") {
        Write-OK "Junction already exists: $modTarget -> $($item.Target)"
        exit 0
    } else {
        Write-Error "Path exists but is not a junction: $modTarget`nRemove it manually before linking."
        exit 1
    }
}

# Create the junction (requires admin on Windows)
try {
    New-Item -ItemType Junction -Path $modTarget -Target $modSource | Out-Null
    Write-OK "Linked: $modTarget`n     -> $modSource"
    Write-Host ""
    Write-Warn "Reminder: enable '$ModName' in BG3 Mod Manager if not already active."
} catch {
    Write-Error "Failed to create junction: $_`nTry running PowerShell as Administrator."
    exit 1
}
