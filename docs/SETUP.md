# BG3ModDev — First-Time Setup

## Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| Git | Yes | With submodule support |
| Python 3.x | Yes | For lint.py and watch_log.py |
| PowerShell 5+ | Yes | For all tools\*.ps1 scripts |
| BG3 Script Extender | Yes | Install before launching BG3 with mods |
| Mod Configuration Menu (MCM) | For ui-mod template | Dependency of ui-mod keybindings |

## Step 1: Clone the repo

```powershell
git clone <your-remote-url> BG3ModDev
cd BG3ModDev
```

## Step 2: Run Setup-Env.ps1

```powershell
.\tools\Setup-Env.ps1
```

This will:
1. Ask for your BG3 game path, AppData path, and Multitool path
2. Write `.env.ps1` (machine-specific, gitignored)
3. Download Divine.exe (LSLib CLI) into `divine\`
4. Verify Python is available
5. Initialize git submodules

**If the script is blocked by Windows execution policy:**
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

## Step 3: Link your mod to AppData

```powershell
.\tools\Link-Mod.ps1 -ModName BaldursGateInventory
```

This creates a directory junction:
```
AppData\Local\Larian Studios\Baldur's Gate 3\Mods\BaldursGateInventory
    → BG3ModDev\mods\BaldursGateInventory\Mod\
```

This means edits in the repo are instantly visible in BG3 — no file copying needed.

**Note:** Junction creation requires admin rights on Windows. Run PowerShell as Administrator if this fails.

## Step 4: Enable in Mod Manager

Launch BG3, open Mod Manager, and enable your mod. Script Extender mods don't always show up here — check the AppData path directly if missing.

## Unpacking Game Files (Optional)

To browse game assets for reference:

```powershell
# Unpack the most useful paks (~5 GB)
.\tools\Unpack-Game.ps1                    # Shared + Game + Gustav

# Unpack a specific pak
.\tools\Unpack-Game.ps1 -PakName Shared

# Unpack everything (~20 GB)
.\tools\Unpack-Game.ps1 -All
```

Output goes to `game-files\<PakName>\` (gitignored).

## Troubleshooting

**Junction creation fails:**
Run PowerShell as Administrator, or use `mklink /J` in an elevated Command Prompt:
```
mklink /J "C:\Users\<you>\AppData\Local\Larian Studios\Baldur's Gate 3\Mods\ModName" "C:\path\to\BG3ModDev\mods\ModName\Mod"
```

**Divine.exe download fails:**
Download manually from https://github.com/Norbyte/lslib/releases
Extract `divine.exe` and place it in `BG3ModDev\divine\`.

**Python not found:**
Install Python 3.x from https://python.org and ensure it's on your PATH.
