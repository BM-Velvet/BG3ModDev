# BG3ModDev

Modding dev environment for Baldur's Gate 3. Provides tooling for the full mod development lifecycle — scaffolding, live testing, packing for release, and unpacking game assets.

## Quick Start

```powershell
# First-time setup (run once per machine)
.\tools\Setup-Env.ps1

# Scaffold a new mod
.\tools\New-Mod.ps1 -ModName "MyMod" -Template ui-mod -Author "YourName"

# Link a mod to AppData for live testing in BG3
.\tools\Link-Mod.ps1 -ModName "MyMod"

# Watch the BG3 log for your mod's output
python .\tools\shared\watch_log.py --mod "MyMod"

# Pack a mod into a .pak for release
.\tools\Pack-Mod.ps1 -ModName "MyMod" -Version "1.0.0"
```

## Structure

```
BG3ModDev/
├── mods/           # Your mods go here (one folder per mod)
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
| `tools\Setup-Env.ps1` | First-time setup: paths, Divine download |
| `tools\New-Mod.ps1` | Scaffold a new mod from a template |
| `tools\Link-Mod.ps1` | Link mod → AppData for live BG3 testing |
| `tools\Unlink-Mod.ps1` | Remove AppData link |
| `tools\Pack-Mod.ps1` | Pack mod folder into .pak for release |
| `tools\Unpack-Game.ps1` | Extract game .pak files to game-files/ |
| `tools\Sync-Env.ps1` | Re-link AppData junctions for all mods in mods/ |
| `tools\shared\lint.py` | XAML + Lua linter |
| `tools\shared\watch_log.py` | Tail BG3 script extender log |

## Adding a Mod

Clone or create your mod inside `mods\`:

```powershell
# Scaffold a new mod from a template
.\tools\New-Mod.ps1 -ModName "MyMod" -Template ui-mod

# Or clone an existing mod repo
git clone <remote-url> mods\MyMod
.\tools\Link-Mod.ps1 -ModName "MyMod"
```

## Templates

- **`ui-mod`** — Full XAML + Lua mod with one panel, MCM keybinding, client/server net channel, offline tests
- **`basic-lua-mod`** — Minimal Lua-only mod (no UI)

See `docs/SETUP.md` for a full walkthrough.
