# BG3ModDev Setup

## Purpose

This workspace is intentionally light. It does not assume a shared automation stack, submodules, or repo-managed git hooks.

## Prerequisites

| Tool | Required | Notes |
|------|----------|-------|
| Git | Yes | For cloning this repo and each mod repo |
| BG3 Script Extender | Usually | Needed by most Lua-based mods |
| Mod Configuration Menu (MCM) | Sometimes | Needed by some UI mods |
| Python / PowerShell / Divine | Optional | Only if a specific mod repo chooses to use them |

## Basic Setup

1. Clone this workspace.
2. Add one or more mod repos under `mods/`.
3. Install whatever local dependencies each mod repo documents.
4. Set up your own local BG3 testing workflow for live files, packaged files, logging, and asset extraction.

Example:

```powershell
git clone <your-remote-url> BG3ModDev
cd BG3ModDev
git clone <mod-remote-url> mods\MyMod
```

## Local Conventions

- `mods/` is for real mod repos.
- `templates/` is for starter structures and reference layouts.
- `game-files/` and `releases/` are local workspace folders and are ignored by git.
- `tools/` is currently a placeholder only.

## Notes

- If you want junctions into BG3 `AppData`, packaging scripts, or log watchers, define them in the specific mod repo or add a new shared approach later.
- If you use Divine or other third-party binaries, keep them local and document their usage where it matters.
