# _common.ps1 — dot-sourced by all BG3ModDev tools
# Usage: . "$PSScriptRoot\_common.ps1"

$REPO_ROOT = (Resolve-Path "$PSScriptRoot\..").Path

function Load-Env {
    $envFile = Join-Path $REPO_ROOT ".env.ps1"
    if (-not (Test-Path $envFile)) {
        Write-Error "No .env.ps1 found. Run .\tools\Setup-Env.ps1 first."
        exit 1
    }
    . $envFile
}

function Require-Divine {
    if (-not (Test-Path $DIVINE_PATH)) {
        Write-Error "Divine.exe not found at: $DIVINE_PATH`nRun .\tools\Setup-Env.ps1 to download it."
        exit 1
    }
}

function Write-Step([string]$msg) {
    Write-Host "  >> $msg" -ForegroundColor Cyan
}

function Write-OK([string]$msg) {
    Write-Host "  OK $msg" -ForegroundColor Green
}

function Write-Warn([string]$msg) {
    Write-Host "WARN $msg" -ForegroundColor Yellow
}
