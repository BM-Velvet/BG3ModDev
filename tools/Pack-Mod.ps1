<#
.SYNOPSIS
    Packs a mod folder into a .pak file using Divine (LSLib).

.DESCRIPTION
    Calls:
        divine.exe --action=create-package --source=mods\<ModName>\Mod --destination=releases\<ModName>_<Version>.pak --game=bg3

    Output is written to releases\.

.PARAMETER ModName
    Name of the mod subfolder inside mods\.

.PARAMETER Version
    Version string for the output filename (default: "1.0.0").

.PARAMETER CopyToMods
    If set, also copies the .pak to $BG3_APPDATA_PATH\Mods\ for local testing.

.EXAMPLE
    .\tools\Pack-Mod.ps1 -ModName BaldursGateInventory -Version 1.2.0
    .\tools\Pack-Mod.ps1 -ModName BaldursGateInventory -Version 1.2.0 -CopyToMods
#>

param(
    [Parameter(Mandatory)][string]$ModName,
    [string]$Version = "1.0.0",
    [switch]$CopyToMods
)

. "$PSScriptRoot\_common.ps1"
Load-Env
Require-Divine

$modSource  = Join-Path $REPO_ROOT "mods\$ModName\Mod"
$outputPak  = Join-Path $REPO_ROOT "releases\${ModName}_${Version}.pak"
$releasesDir = Join-Path $REPO_ROOT "releases"

if (-not (Test-Path $modSource)) {
    Write-Error "Mod source not found: $modSource"
    exit 1
}

New-Item -ItemType Directory -Path $releasesDir -Force | Out-Null

Write-Step "Packing $ModName v$Version..."
Write-Host "  Source : $modSource"
Write-Host "  Output : $outputPak"

& $DIVINE_PATH `
    --action=create-package `
    --source="$modSource" `
    --destination="$outputPak" `
    --game=bg3

if ($LASTEXITCODE -ne 0) {
    Write-Error "Divine failed with exit code $LASTEXITCODE"
    exit 1
}

Write-OK "Packed: $outputPak"

if ($CopyToMods) {
    $modsDir = Join-Path $BG3_APPDATA_PATH "Mods"
    $dest    = Join-Path $modsDir "${ModName}_${Version}.pak"
    Copy-Item $outputPak $dest -Force
    Write-OK "Copied to: $dest"
}
