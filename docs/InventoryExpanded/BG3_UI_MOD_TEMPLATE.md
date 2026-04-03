# BG3 UI Mod Project Template

Use this as a starting checklist for future BG3 UI mod repositories.

## Recommended Repo Layout

```text
<RepoRoot>/
|-- Mod/
|   |-- GUI/
|   |   |-- Library/
|   |   |-- Pages/
|   |   |-- Resources/
|   |   `-- StateMachines/
|   |-- ScriptExtender/
|   |   |-- Config.json
|   |   `-- Lua/
|   |       |-- BootstrapClient.lua
|   |       |-- BootstrapServer.lua
|   |       |-- Client/
|   |       `-- Server/
|   |-- MCM_blueprint.json
|   `-- meta.lsx
|-- Tests/
|   |-- TestRunner.lua
|   |-- MockData.lua
|   `-- test_<Module>.lua
|-- Tools/
|   `-- .gitkeep
|-- API.md
|-- WORKFLOW.md
`-- README.md
```

## Module Split

Use these responsibilities consistently:

- `Server/Collector.lua` - reads gameplay state and builds normalized data
- `Server/Actions.lua` - performs item actions or gameplay mutations
- `Server/NetHandlers.lua` - server listeners and broadcasts
- `Client/DataStore.lua` - local cache and indexes
- `Client/FilterEngine.lua` - pure filtering and sorting
- `Client/<PanelName>VM.lua` - Noesis-facing VM for one panel
- `Client/NetHandlers.lua` - receives server data and updates local state

Do not combine all of this into one file. BG3 UI iteration gets much harder when collection, state, and rendering are mixed together.

## First Files To Create

When starting a new repo, create these first:

1. `README.md`
2. `WORKFLOW.md`
3. `Mod/ScriptExtender/Config.json`
4. `Mod/ScriptExtender/Lua/BootstrapClient.lua`
5. `Mod/ScriptExtender/Lua/BootstrapServer.lua`
6. `Client/DataStore.lua`
7. `Client/FilterEngine.lua`
8. `Tools/`
9. `Tests/TestRunner.lua`

That sequence forces the project to start with structure instead of ad hoc experiments.

## Development Rules

- Edit only in the repo copy of `Mod/`
- keep the Steam mod install path as a deployment target or junction, not the source of truth
- use one panel VM per screen
- wrap risky Noesis access in `pcall`
- assume Noesis proxies are temporary
- log with a consistent mod prefix
- put hot reload and debug commands in dedicated dev modules

## Workflow Checklist

For each feature:

1. Identify the native BG3 screen or XAML file that is closest to the target behavior.
2. Decide what gameplay data must come from the server.
3. Normalize that data into a client store.
4. Add pure logic tests for filtering, sorting, or shaping.
5. Add or update XAML only after the data contract is stable.
6. Test in game.
7. Record working patterns and failed experiments in `WORKFLOW.md`.

## XAML Rules To Adopt By Default

- use `http://` XML namespaces
- prefer native BG3 layout patterns over custom WPF assumptions
- use explicit resource names and bindings
- avoid clever popup or tooltip binding tricks until proven in game
- compare your tree to native XAML when behavior is incomplete

## Testing Strategy

Use two loops:

- fast offline loop for pure Lua modules under `Tests/`
- slower in-game loop for UI binding, Noesis behavior, and gameplay integration

Suggested commands depend on the repo. If a local Lua interpreter is installed, run the offline tests from `Tests/` as part of normal iteration.

## Documentation Strategy

Keep these documents current while developing:

- `README.md` - what the project is and where to look
- `WORKFLOW.md` - architecture, discoveries, constraints, commands
- `PROGRESS.md` - milestone history if useful

Do not wait until the end to write this down. BG3 UI modding has too many engine-specific details to rely on memory later.

## What To Reuse From This Repo

Strong candidates to copy into new projects:

- the `Tests/` harness pattern
- a small repo-local validation or helper layer under `Tools/` if the project benefits from it
- the bootstrap entry-point layout
- the client store plus panel VM split
- the habit of documenting native XAML references and dead ends

## What Not To Reuse Blindly

Do not copy these without re-validating:

- exact widget lookup indices
- assumptions about specific native DataContext paths
- tooltip structures unless the target behavior matches
- inventory-specific slot mappings

Those are feature- and game-state-dependent.
