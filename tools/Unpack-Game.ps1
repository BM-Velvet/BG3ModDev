<#
.SYNOPSIS
    Unpacks BG3 game .pak files into game-files\ for asset reference.

.DESCRIPTION
    Calls:
        divine.exe --action=extract-package --source=<game.pak> --destination=game-files\<PakName> --game=bg3

    CAUTION: All paks combined are ~20 GB. Use -PakName to unpack selectively.

.PARAMETER PakName
    Name of the .pak to unpack (without extension), e.g. "Shared", "Gustav", "Game".
    Omit to unpack the default set: Shared, Game, Gustav.

.PARAMETER All
    Unpack ALL .pak files in the game Data\ directory (very large — ~20 GB+).

.EXAMPLE
    .\tools\Unpack-Game.ps1 -PakName Shared
    .\tools\Unpack-Game.ps1                    # unpacks Shared, Game, Gustav
    .\tools\Unpack-Game.ps1 -All               # unpacks everything (~20 GB)
#>

param(
    [string]$PakName = "",
    [switch]$All
)

. "$PSScriptRoot\_common.ps1"
Load-Env
Require-Divine

$gameDataDir  = Join-Path $BG3_GAME_PATH "Data"
$outputBase   = Join-Path $REPO_ROOT "game-files"

if (-not (Test-Path $gameDataDir)) {
    Write-Error "BG3 Data directory not found: $gameDataDir"
    exit 1
}

# Determine which paks to unpack
if ($All) {
    Write-Warn "Unpacking ALL paks — this may use 20+ GB of disk space."
    $confirm = Read-Host "Continue? [y/N]"
    if ($confirm -notmatch '^[yY]') { exit 0 }
    $paks = Get-ChildItem -Path $gameDataDir -Filter "*.pak" | Select-Object -ExpandProperty Name | ForEach-Object { [System.IO.Path]::GetFileNameWithoutExtension($_) }
} elseif ($PakName -ne "") {
    $paks = @($PakName)
} else {
    $paks = @("Shared", "Game", "Gustav")
    Write-Host "No -PakName specified — unpacking default set: $($paks -join ', ')"
}

foreach ($pak in $paks) {
    $srcPak  = Join-Path $gameDataDir "$pak.pak"
    $destDir = Join-Path $outputBase $pak

    if (-not (Test-Path $srcPak)) {
        Write-Warn "Not found: $srcPak — skipping"
        continue
    }

    Write-Step "Unpacking $pak.pak -> game-files\$pak\"
    New-Item -ItemType Directory -Path $destDir -Force | Out-Null

    & $DIVINE_PATH `
        --action=extract-package `
        --source="$srcPak" `
        --destination="$destDir" `
        --game=bg3

    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Divine returned exit code $LASTEXITCODE for $pak"
    } else {
        Write-OK "Unpacked: game-files\$pak\"
    }
}
