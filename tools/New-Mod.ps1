<#
.SYNOPSIS
    Scaffolds a new BG3 mod from a template.

.DESCRIPTION
    1. Copies templates\<Template>\ to mods\<ModName>\
    2. Replaces __MOD_NAME__, __MOD_UUID__, __AUTHOR__ placeholders
    3. Runs `git init` inside the new mod folder and creates an initial commit
    4. Registers the new folder as a git submodule in BG3ModDev
    5. Runs Link-Mod.ps1 to create the AppData junction

.PARAMETER ModName
    Name for the new mod (used as folder name and in placeholder replacements).
    Must be a valid folder name — no spaces or special characters.

.PARAMETER Template
    Template to use: 'ui-mod' (full XAML+Lua) or 'basic-lua-mod' (Lua only).
    Default: ui-mod

.PARAMETER Author
    Author name substituted into meta.lsx and README. Default: "Unknown"

.PARAMETER SkipLink
    If set, skip creating the AppData junction after scaffolding.

.EXAMPLE
    .\tools\New-Mod.ps1 -ModName "CoolMod" -Template ui-mod -Author "BlueVelvet"
    .\tools\New-Mod.ps1 -ModName "SimpleScript" -Template basic-lua-mod
#>

param(
    [Parameter(Mandatory)][string]$ModName,
    [ValidateSet('ui-mod', 'basic-lua-mod')][string]$Template = 'ui-mod',
    [string]$Author = "Unknown",
    [switch]$SkipLink
)

. "$PSScriptRoot\_common.ps1"
Load-Env

# ── Validate name ────────────────────────────────────────────────────────────

if ($ModName -match '[\\/:*?"<>|]') {
    Write-Error "ModName contains invalid characters: $ModName"
    exit 1
}

$destDir = Join-Path $REPO_ROOT "mods\$ModName"
if (Test-Path $destDir) {
    Write-Error "Mod already exists: $destDir"
    exit 1
}

$templateDir = Join-Path $REPO_ROOT "templates\$Template"
if (-not (Test-Path $templateDir)) {
    Write-Error "Template not found: $templateDir"
    exit 1
}

# ── Generate UUID ────────────────────────────────────────────────────────────

$uuid = [System.Guid]::NewGuid().ToString().ToLower()
Write-Host "`nNew mod: $ModName"
Write-Host "  Template : $Template"
Write-Host "  Author   : $Author"
Write-Host "  UUID     : $uuid`n"

# ── Copy template ────────────────────────────────────────────────────────────

Write-Step "Copying template..."
Copy-Item -Path $templateDir -Destination $destDir -Recurse -Force
Write-OK "Copied to mods\$ModName\"

# ── Replace placeholders ─────────────────────────────────────────────────────

Write-Step "Substituting placeholders..."

$textExtensions = @(".lua", ".xaml", ".xml", ".lsx", ".json", ".md", ".py", ".ps1", ".txt")

Get-ChildItem -Path $destDir -Recurse -File | Where-Object {
    $textExtensions -contains $_.Extension.ToLower()
} | ForEach-Object {
    $content = Get-Content $_.FullName -Raw -Encoding UTF8
    if ($content -match '__MOD_NAME__|__MOD_UUID__|__AUTHOR__') {
        $content = $content `
            -replace '__MOD_NAME__', $ModName `
            -replace '__MOD_UUID__', $uuid `
            -replace '__AUTHOR__',   $Author
        Set-Content -Path $_.FullName -Value $content -Encoding UTF8 -NoNewline
    }
}

Write-OK "Placeholders replaced"

# ── Git init ─────────────────────────────────────────────────────────────────

Write-Step "Initializing git repo in mods\$ModName\..."
Push-Location $destDir
git init -b main
git add .
git commit -m "Init: $ModName scaffold from $Template template"
Pop-Location
Write-OK "Git repo initialized"

# ── Register as submodule ────────────────────────────────────────────────────

Write-Step "Registering as git submodule..."
Push-Location $REPO_ROOT
# Use a relative path so the submodule works without a remote
git submodule add --force "./mods/$ModName" "mods/$ModName"
git commit -m "Add submodule: mods/$ModName"
Pop-Location
Write-OK "Submodule registered"

# ── Link to AppData ──────────────────────────────────────────────────────────

if (-not $SkipLink) {
    $modFolder = Join-Path $destDir "Mod"
    if (Test-Path $modFolder) {
        Write-Step "Creating AppData junction..."
        & "$PSScriptRoot\Link-Mod.ps1" -ModName $ModName
    } else {
        Write-Warn "No Mod\ subfolder found — skipping AppData link (template may not include it)"
    }
}

# ── Done ─────────────────────────────────────────────────────────────────────

Write-Host "`n--- $ModName created ---" -ForegroundColor Green
Write-Host "  Mod folder : mods\$ModName\"
Write-Host "  UUID       : $uuid"
Write-Host ""
Write-Host "Next steps:"
Write-Host "  1. Edit mods\$ModName\Mod\ScriptExtender\Config.json (set ModTable)"
Write-Host "  2. Launch BG3 and enable $ModName in Mod Manager"
Write-Host "  3. python .\tools\shared\watch_log.py --filter `"[$ModName]`""
