# BG3ModDev Setup

## Purpose

This workspace stays light, but it has one shared terminal app for the core development loop.

## Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| Git | Yes | For cloning this repo and each mod repo |
| Python 3.11+ | Yes | Required for the `bg3dev` terminal app |
| BG3 Script Extender | Usually | Needed by most Lua-based mods |
| Mod Configuration Menu (MCM) | Sometimes | Needed by some UI mods |
| PowerShell / Divine | Optional | Used by some app actions depending on your workflow |

## Basic Setup

1. Clone this workspace.
2. Run `python -m bg3dev setup` and save your local BG3 paths.
3. Add one or more mod repos under `mods/`.
4. Install whatever local dependencies each mod repo documents.

Example:

```powershell
git clone <your-remote-url> BG3ModDev
cd BG3ModDev
python -m bg3dev setup
git clone <mod-remote-url> mods\MyMod
```

## Local Conventions

- `mods/` is for real mod repos.
- `bg3dev/` contains the terminal app.
- `templates/` is for starter structures and reference layouts.
- `game-files/` and `releases/` are local workspace folders and are ignored by git.
- `tools/` is still available for future helpers if the app should not own them.

## Notes

- The app writes its machine-local config to `.bg3dev.local.toml` and does not commit it.
- If `.env.ps1` already exists, the app can use it as a legacy fallback until you save the new config.
- Loose-folder deployment targets `BG3\Data\Mods`.
- Packaged `.pak` copy actions target AppData `Mods`.
