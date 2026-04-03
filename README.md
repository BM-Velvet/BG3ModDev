# BG3ModDev

Workspace for Baldur's Gate 3 mod development. It keeps templates, reference material, unpacked game files, release artifacts, and one or more mod repos under `mods/`.

The shared workflow lives in a small Python terminal app instead of a pile of scripts.

## Quick Start

```powershell
# Save local machine paths
python -m bg3dev setup

# See workspace and mod status
python -m bg3dev status

# Launch the interactive app
python -m bg3dev

# Rename a mod repo and its in-mod identifiers
python -m bg3dev rename-mod --mod InventoryExpanded --name InventoryExpanded --display-name "Inventory Expanded"

# Build a beta package for testing
python -m bg3dev package --mod InventoryExpanded --version 1.0.0 --beta
```

## Structure

```text
BG3ModDev/
|-- mods/           # Individual mod repos live here
|-- bg3dev/         # Workspace terminal app
|-- game-files/     # Local extracted/reference assets
|-- tools/          # Reserved for future helpers outside the app
|-- templates/      # Starter layouts and reference scaffolds
|-- lslib/          # Optional LSlib bundle; Divine is auto-detected here
|-- releases/       # Local build/export artifacts
`-- docs/           # Notes on setup and workflow
```

## Working Model

- Each mod keeps its own repository inside `mods/`.
- This repo is a shared workspace, not a parent repo that tracks child repos as submodules.
- Git workflows such as commits and pushes still happen inside each mod repo.
- Shared operational tasks like status, mod creation, deploy, packaging, and log watching run through `bg3dev`.
- Packaging auto-detects `Divine.exe` from `lslib/Packed/Tools/Divine.exe` by default.

## App Capabilities

- discover mods under `mods/`
- show git, deploy, and readiness status
- create a new mod from a template with placeholder replacement
- rename a mod repo plus its metadata and Script Extender mod table together
- deploy or undeploy a loose mod folder to `BG3\Data\Mods`
- package a mod with Divine
- package a beta `.pak` by appending `-beta` to the filename
- optionally copy packaged `.pak` output to AppData `Mods`
- run offline Lua tests when present
- tail BG3 logs for a selected mod

## Adding a Mod

Create a new mod:

```powershell
python -m bg3dev new-mod --name MyMod --template ui-mod --author YourName
```

Or clone an existing repo into `mods/`:

```powershell
git clone <remote-url> mods\MyMod
```

## Templates

- `templates/ui-mod` - UI-oriented layout with XAML, Lua, tests, and placeholder `Tools/`
- `templates/basic-lua-mod` - Minimal Lua-only layout

See [docs/SETUP.md](/C:/Users/BogdanMichon/Documents/BG3ModDev/docs/SETUP.md) and [docs/WORKFLOW.md](/C:/Users/BogdanMichon/Documents/BG3ModDev/docs/WORKFLOW.md) for the workspace workflow.
