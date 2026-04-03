# BG3ModDev Workflow

## Daily Use

This workspace uses `bg3dev` as the shared operational layer. Day-to-day code changes still happen inside the relevant mod repo under `mods/`.

Typical loop:

1. Run `python -m bg3dev status` or `python -m bg3dev` to inspect workspace state.
2. Open the mod repo you are working on.
3. Edit files there.
4. Use `bg3dev` for shared actions like deploy, package, tests, validation, and log access.
5. Commit and push from that mod repo when ready.

## Starting a New Mod

Use the app to create a mod from a template:

```powershell
python -m bg3dev new-mod --name MyMod --template ui-mod --author YourName
```

The app copies the template, replaces placeholders, generates a UUID, and initializes a git repo in the new mod folder.

## Workspace Boundaries

- `BG3ModDev` is a shared container for multiple mod repos.
- `BG3ModDev` does not manage child repos as submodules.
- `BG3ModDev` does not assume automatic hook installation or auto-push behavior.
- `BG3ModDev` does centralize workspace commands through `bg3dev`.

## Key Paths

| Path | Purpose |
|------|---------|
| `mods\<Name>\` | A standalone mod repo |
| `mods\<Name>\Mod\` | Mod content |
| `bg3dev\` | Shared terminal app |
| `templates\` | Starter layouts and references |
| `game-files\` | Local extracted/reference assets |
| `releases\` | Local build/export artifacts |
| `.bg3dev.local.toml` | Machine-local app config |
| `.bg3dev-actions.toml` | Workspace-owned action registry |
| `tools\` | Reserved for future shared helpers |

`deploy` creates a loose-folder junction under `BG3\Data\Mods`.

`package --copy-to-appdata` copies a built `.pak` into AppData `Mods`.
