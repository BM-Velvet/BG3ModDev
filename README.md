# BG3ModDev

Workspace for Baldur's Gate 3 mod development. It keeps templates, reference material, unpacked game files, release artifacts, and one or more mod repos under `mods/`.

The repo no longer ships an active toolchain. The `tools/` folder is intentionally kept as a placeholder for future utilities once a better workflow is settled.

## Structure

```text
BG3ModDev/
|-- mods/           # Individual mod repos live here
|-- game-files/     # Local extracted/reference assets
|-- tools/          # Reserved for future tooling
|-- templates/      # Starter layouts and reference scaffolds
|-- divine/         # Optional third-party packaging binaries
|-- releases/       # Local build/export artifacts
`-- docs/           # Notes on setup and workflow
```

## Working Model

- Each mod keeps its own repository inside `mods/`.
- This repo is a shared workspace, not a parent repo that tracks child repos as submodules.
- Git workflows such as commits, hooks, pushes, and releases are handled inside each mod repo however that repo chooses.

## Adding a Mod

Create or clone a repo into `mods/`:

```powershell
git clone <remote-url> mods\MyMod
```

You can also copy one of the templates into a new folder under `mods/` and initialize git there manually.

## Templates

- `templates/ui-mod` - UI-oriented layout with XAML, Lua, tests, and placeholder `Tools/`
- `templates/basic-lua-mod` - Minimal Lua-only layout

See [docs/SETUP.md](/C:/Users/BogdanMichon/Documents/BG3ModDev/docs/SETUP.md) and [docs/WORKFLOW.md](/C:/Users/BogdanMichon/Documents/BG3ModDev/docs/WORKFLOW.md) for the simplified workspace notes.
