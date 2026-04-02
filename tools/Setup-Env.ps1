<#
.SYNOPSIS
    First-time setup for BG3ModDev.

.DESCRIPTION
    - Writes .env.ps1 with machine-specific paths
    - Downloads Divine.exe (LSLib CLI) into divine/
    - Verifies Python is available
    - Initializes git submodules

.EXAMPLE
    .\tools\Setup-Env.ps1
#>

. "$PSScriptRoot\_common.ps1"

Write-Host "`nBG3ModDev Setup`n" -ForegroundColor Magenta

# ── 1. Gather paths ─────────────────────────────────────────────────────────

$defaultGame      = "C:\Program Files (x86)\Steam\steamapps\common\Baldurs Gate 3"
$defaultAppData   = "$env:LOCALAPPDATA\Larian Studios\Baldur's Gate 3"
$defaultMultitool = "$env:USERPROFILE\Documents\BG3ModdersMultitool"

function Prompt-Path([string]$label, [string]$default) {
    $input = Read-Host "$label`n  [default: $default]"
    if ([string]::IsNullOrWhiteSpace($input)) { return $default }
    return $input.Trim()
}

$gamePath      = Prompt-Path "BG3 game install path" $defaultGame
$appDataPath   = Prompt-Path "BG3 AppData path" $defaultAppData
$multitoolPath = Prompt-Path "BG3 Modders Multitool path" $defaultMultitool

# ── 2. Validate paths ────────────────────────────────────────────────────────

$ok = $true
foreach ($p in @($gamePath, $appDataPath)) {
    if (-not (Test-Path $p)) {
        Write-Warn "Path not found: $p (continuing anyway)"
    }
}

# ── 3. Write .env.ps1 ────────────────────────────────────────────────────────

$envFile = Join-Path $REPO_ROOT ".env.ps1"
$divinePath = Join-Path $REPO_ROOT "divine\divine.exe"

@"
# BG3ModDev machine configuration — DO NOT COMMIT (gitignored)
`$BG3_GAME_PATH    = "$gamePath"
`$BG3_APPDATA_PATH = "$appDataPath"
`$MULTITOOL_PATH   = "$multitoolPath"
`$DIVINE_PATH      = "$divinePath"
"@ | Set-Content -Path $envFile -Encoding UTF8

Write-OK ".env.ps1 written"

# ── 4. Download Divine.exe ───────────────────────────────────────────────────

Write-Step "Downloading Divine.exe (LSLib)..."

$divineDir = Join-Path $REPO_ROOT "divine"
$divineExe = Join-Path $divineDir "divine.exe"

if (Test-Path $divineExe) {
    Write-OK "Divine.exe already present — skipping download"
} else {
    # Fetch latest LSLib release from GitHub
    try {
        $release = Invoke-RestMethod "https://api.github.com/repos/Norbyte/lslib/releases/latest"
        $asset   = $release.assets | Where-Object { $_.name -like "*.zip" } | Select-Object -First 1
        if (-not $asset) {
            Write-Warn "Could not find LSLib release zip. Download manually from https://github.com/Norbyte/lslib/releases and place divine.exe in divine/"
        } else {
            $zipPath = Join-Path $divineDir "lslib.zip"
            Write-Step "Downloading $($asset.browser_download_url)..."
            Invoke-WebRequest -Uri $asset.browser_download_url -OutFile $zipPath -UseBasicParsing
            Expand-Archive -Path $zipPath -DestinationPath $divineDir -Force
            Remove-Item $zipPath

            # Find divine.exe anywhere in the extracted tree
            $found = Get-ChildItem -Recurse -Path $divineDir -Filter "divine.exe" | Select-Object -First 1
            if ($found -and $found.FullName -ne $divineExe) {
                Move-Item $found.FullName $divineExe -Force
            }

            if (Test-Path $divineExe) {
                Write-OK "divine.exe downloaded to divine\"
            } else {
                Write-Warn "divine.exe not found after extraction. Place it manually in divine\"
            }
        }
    } catch {
        Write-Warn "Failed to download Divine: $_"
        Write-Warn "Download manually from https://github.com/Norbyte/lslib/releases and place divine.exe in divine\"
    }
}

# ── 5. Check Python ──────────────────────────────────────────────────────────

Write-Step "Checking Python..."
try {
    $pyver = & python --version 2>&1
    Write-OK "Python: $pyver"
} catch {
    Write-Warn "Python not found — install Python 3.x to use lint.py and watch_log.py"
}

# ── 6. Init submodules ───────────────────────────────────────────────────────

Write-Step "Initializing git submodules..."
Push-Location $REPO_ROOT
git submodule update --init --recursive
Pop-Location
Write-OK "Submodules initialized"

# ── 7. Summary ───────────────────────────────────────────────────────────────

Write-Host "`n--- Setup complete ---" -ForegroundColor Magenta
Write-Host "  BG3 game   : $gamePath"
Write-Host "  AppData    : $appDataPath"
Write-Host "  Multitool  : $multitoolPath"
Write-Host "  Divine     : $divineExe"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  .\tools\New-Mod.ps1 -ModName MyMod -Template ui-mod"
Write-Host "  .\tools\Link-Mod.ps1 -ModName BaldursGateInventory"
