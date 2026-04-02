# BG3ModDev

Modding dev environment for Baldur's Gate 3. Hosts multiple mods as git submodules and provides tooling for the full mod development lifecycle.

## Quick Start

```powershell
# First-time setup (run once per machine)
.\tools\Setup-Env.ps1

# Scaffold a new mod
.\tools\New-Mod.ps1 -ModName "MyMod" -Template ui-mod -Author "YourName"

# Link an existing mod to AppData for live testing
.\tools\Link-Mod.ps1 -ModName "BaldursGateInventory"

# Watch the BG3 log for your mod's output
python .\tools\shared\watch_log.py

# Pack a mod into a .pak for release
.\tools\Pack-Mod.ps1 -ModName "BaldursGateInventory" -Version "1.0.0"
```

## Structure

```
BG3ModDev/
├── mods/           # Git submodules — one per mod
├── game-files/     # Unpacked game assets (gitignored, populate with Unpack-Game.ps1)
├── tools/          # PowerShell tooling + shared Python utilities
├── templates/      # Mod scaffolds (ui-mod, basic-lua-mod)
├── divine/         # LSLib CLI binary (downloaded by Setup-Env.ps1)
├── releases/       # Packed .pak outputs (gitignored)
└── docs/           # Setup and workflow reference
```

## Tools Reference

| Script | Purpose |
|--------|---------|
| `tools\Setup-Env.ps1` | First-time setup: paths, Divine download, submodule init |
| `tools\New-Mod.ps1` | Scaffold a new mod from a template |
| `tools\Link-Mod.ps1` | Symlink mod → AppData for live BG3 testing |
| `tools\Unlink-Mod.ps1` | Remove AppData symlink |
| `tools\Pack-Mod.ps1` | Pack mod folder into .pak for release |
| `tools\Unpack-Game.ps1` | Extract game .pak files to game-files/ |
| `tools\Sync-Env.ps1` | Update all submodules + re-link AppData junctions |
| `tools\shared\lint.py` | XAML + Lua linter |
| `tools\shared\watch_log.py` | Tail BG3 script extender log |

## Adding an Existing Mod

```powershell
# If the mod has a remote repo:
git submodule add <remote-url> mods/ModName

# If the mod is local only:
git submodule add ./mods/ModName

.\tools\Link-Mod.ps1 -ModName "ModName"
```

## Templates

- **`ui-mod`** — Full XAML + Lua mod with one panel, MCM keybinding, client/server net channel, offline tests
- **`basic-lua-mod`** — Minimal Lua-only mod (no UI)

See `docs/SETUP.md` for a full walkthrough.
