# BG3ModDev Workflow

## Daily Use

This workspace does not enforce a shared automation flow. Day-to-day work happens inside the relevant mod repo under `mods/`.

Typical loop:

1. Open the mod repo you are working on.
2. Edit files there.
3. Use that repo's own testing, logging, packaging, and release process.
4. Commit and push from that mod repo when ready.

## Starting a New Mod

Choose a template from `templates/`, copy it into `mods/<Name>/`, then initialize the new repo however you want.

Example:

```powershell
Copy-Item .\templates\ui-mod .\mods\MyMod -Recurse
cd .\mods\MyMod
git init
```

After that, update placeholder values and add whatever tooling or scripts the new mod actually needs.

## Workspace Boundaries

- `BG3ModDev` is a shared container for multiple mod repos.
- `BG3ModDev` does not manage child repos as submodules.
- `BG3ModDev` does not assume automatic linting, hook installation, or auto-push behavior.

## Key Paths

| Path | Purpose |
|------|---------|
| `mods\<Name>\` | A standalone mod repo |
| `mods\<Name>\Mod\` | Mod content |
| `templates\` | Starter layouts and references |
| `game-files\` | Local extracted/reference assets |
| `releases\` | Local build/export artifacts |
| `tools\` | Reserved for future shared tooling |
