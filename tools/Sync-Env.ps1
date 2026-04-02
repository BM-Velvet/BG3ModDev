<#
.SYNOPSIS
    Syncs all mod submodules and re-links AppData junctions.

.DESCRIPTION
    1. Runs `git submodule update --init --recursive`
    2. For each submodule under mods/, runs Link-Mod.ps1 if the junction doesn't exist

.EXAMPLE
    .\tools\Sync-Env.ps1
#>

. "$PSScriptRoot\_common.ps1"
Load-Env

Write-Step "Updating git submodules..."
Push-Location $REPO_ROOT
git submodule update --init --recursive
Pop-Location
Write-OK "Submodules up to date"

Write-Step "Syncing AppData junctions..."
$modsDir = Join-Path $REPO_ROOT "mods"
if (Test-Path $modsDir) {
    foreach ($modFolder in Get-ChildItem -Path $modsDir -Directory) {
        $modName   = $modFolder.Name
        $modSource = Join-Path $modFolder.FullName "Mod"
        $modTarget = Join-Path $BG3_APPDATA_PATH "Mods\$modName"

        if (-not (Test-Path $modSource)) { continue }

        if (Test-Path $modTarget) {
            Write-OK "Already linked: $modName"
        } else {
            Write-Step "Linking $modName..."
            & "$PSScriptRoot\Link-Mod.ps1" -ModName $modName
        }
    }
}

Write-Host "`nSync complete." -ForegroundColor Green
