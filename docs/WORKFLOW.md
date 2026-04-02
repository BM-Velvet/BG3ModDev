# BG3ModDev — Day-to-Day Workflow

## Daily Dev Loop

```powershell
# 1. Watch log output in a separate terminal
python .\tools\shared\watch_log.py --mod MyMod

# 2. Edit files in mods\MyMod\ — BG3 picks them up via the AppData junction

# 3. Reload the mod in-game (if your mod supports it)
#    In BG3 console: !mymod_reload

# 4. Before committing, lint
python .\tools\shared\lint.py --mod-root .\mods\MyMod

# 5. Commit in the mod's own repo
cd mods\MyMod
git add .
git commit -m "..."
cd ..\..

# 6. Update the submodule pointer in BG3ModDev
git add mods\MyMod
git commit -m "Update submodule: MyMod"
```

## Starting a New Mod

```powershell
.\tools\New-Mod.ps1 -ModName "MyMod" -Template ui-mod -Author "YourName"
```

This:
1. Copies the `ui-mod` template to `mods\MyMod\`
2. Replaces all `__MOD_NAME__`, `__MOD_UUID__`, `__AUTHOR__` placeholders
3. `git init` + initial commit inside the new folder
4. Registers it as a git submodule
5. Creates the AppData junction automatically

## Packing for Release

```powershell
.\tools\Pack-Mod.ps1 -ModName MyMod -Version 1.2.0
# Output: releases\MyMod_1.2.0.pak
```

Upload `releases\MyMod_1.2.0.pak` to Nexus Mods or wherever you distribute.

## Updating All Mods (after cloning on a new machine)

```powershell
.\tools\Sync-Env.ps1
```

This runs `git submodule update --init --recursive` and re-creates any missing AppData junctions.

## Log Watcher Tips

```powershell
# Default — shows everything from your mod
python .\tools\shared\watch_log.py --mod BaldursGateInventory

# Filter to a specific subsystem tag
python .\tools\shared\watch_log.py --filter "[Armory]"

# Show all SE output (no filter)
python .\tools\shared\watch_log.py --filter ""

# Custom output path
python .\tools\shared\watch_log.py --mod MyMod --output logs\session.log
```

The output file (`last_session.log` by default) is written from each mod's `Tools\` stub — Claude Code can read it at any time for debugging.

## Linting

The pre-commit hook in each mod (`.git/hooks/pre-commit`) automatically runs `lint.py` on staged Lua/XAML files.

Manual lint:
```powershell
# Lint an entire mod
python .\tools\shared\lint.py --mod-root .\mods\MyMod

# Lint specific files
python .\tools\shared\lint.py --mod-root .\mods\MyMod .\mods\MyMod\Mod\GUI\Pages\MainPanel.xaml
```

Errors (exit code 1) block commits. Warnings (exit code 0) are advisory.

## Key Paths Reference

| Path | Purpose |
|------|---------|
| `mods\<Name>\` | Mod git repo (submodule) |
| `mods\<Name>\Mod\` | Actual mod content (linked to AppData) |
| `game-files\<PakName>\` | Unpacked game assets (gitignored) |
| `releases\` | Packed .pak outputs (gitignored) |
| `divine\divine.exe` | LSLib CLI for pack/unpack |
| `.env.ps1` | Machine-specific paths (gitignored) |
| `AppData\...\Mods\<Name>` | Junction → `mods\<Name>\Mod\` |
