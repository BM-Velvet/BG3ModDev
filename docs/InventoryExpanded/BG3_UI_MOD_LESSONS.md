# BG3 UI Mod Lessons Learned

This document extracts the parts of the project that are worth reusing on future Baldur's Gate 3 UI mods. It focuses on patterns that generalized well, not one-off implementation details.

## 1. Separate Gameplay Data From UI Data

The strongest pattern in this repo is the split between:

- server-side data collection
- client-side data storage and transformation
- XAML-facing view models

Why this worked:

- BG3 gameplay state is easier to read on the server side.
- UI state is easier to manage on the client side.
- XAML becomes much simpler when it binds to a clean VM instead of raw game objects.

Recommended structure:

- server collector module
- server action module
- shared net channel names
- client data store
- client filter/sort layer
- client panel VM per screen

## 2. Treat Noesis Proxies As Temporary

One of the most important findings from this project: do not cache Noesis proxies from SE Lua and expect them to stay valid.

What to assume:

- widgets can expire between calls
- VM proxies can expire between calls
- the actual DataContext object can still stay alive if Noesis owns it

What to do instead:

- re-find widgets from the UI tree every time you need them
- re-acquire `widget.DataContext` every time you need the VM
- cache only plain Lua data or simple flags

This pattern is essential for any BG3 UI mod that interacts with live Noesis objects.

## 3. Copy Native UI Structure When Native Behavior Matters

The project found that "visually similar" XAML is often not enough. For some engine-owned behaviors, the structure has to match the native game pattern closely.

### Native Tooltip Breakthrough

Native item tooltips (description, damage, AC, passives, comparison panel) only work inside a custom panel when the XAML reproduces the exact native `Container.xaml` hierarchy:

```
Border (ls:TooltipExtender.Owner = SelectedCharacter VM)
  └── ListBox (ItemsSource = collection of raw VMInventorySlot objects)
       └── ListBoxItem (ControlTemplate)
            └── ls:LSEntityObject
                  ├── DataContext = "{Binding Object}"       ← VMItem
                  ├── EntityRef   = "{Binding EntityHandle}" ← from VMItem
                  └── ToolTip
                       └── ls:LSTooltip (DIRECT — no wrapper element)
```

**What you must feed it:** raw `VMInventorySlot` objects pulled from the game's own Noesis VM (e.g. `cp.SelectedCharacter.Inventories[1].Slots`), not custom wrapper types.

**What fails and why:**

| Attempt | Result |
|---|---|
| `ItemsControl` + `DataTemplate` | Partial tooltip — name and icon only, no description or stats |
| `<ToolTip><ls:LSTooltip/></ToolTip>` | Same partial result — wrapper breaks engine ownership |
| Bare `LSTooltip` without ListBox context | Empty border |
| `TooltipExtender.Owner` on `LSTooltip` itself | Kills the comparison panel |
| `PlacementTarget` bindings across tooltip boundary | Not supported in Noesis |

**Why it works:** The C++ engine lazily populates tooltip fields (`TechnicalDescription`, `Damages`, `ArmorSection`) only when it detects the exact native structure. "Visually similar" XAML that doesn't match is treated as a foreign element and gets partial data.

**Tooltip pinning (T key):** Add `CanBePinned="True"` to `ls:LSTooltip` and place `<ls:LSInputBinding Style="{DynamicResource PinTooltipBindingStyle}"/>` inside the panel's root Grid. The T key mapping is C++ engine-owned — the `LSInputBinding` just bridges the `UIPinTooltip` event to `PinTooltipCommand`.

General rule: if a native behavior is partial, empty, or inconsistent, compare the full XAML hierarchy against the game's original file before tweaking individual properties.

## 4. Document What Failed, Not Just What Worked

This repo is valuable because it records failed attempts as well as working ones. That should be standard practice for BG3 UI mods.

Examples of failures worth preserving:

- `ItemsControl` plus `DataTemplate` for native tooltip behavior
- wrapping `ls:LSTooltip` in a standard `<ToolTip>`
- assuming `CurrentPlayer` exposes party members directly
- caching Noesis object references across calls

This matters because BG3 UI modding has many engine-specific dead ends that look reasonable from normal WPF expectations.

## 5. Keep XAML Conservative

BG3 Noesis modding is not standard desktop WPF. Several "normal" habits are unsafe or misleading here.

Project rules that should carry forward:

- use `http://` namespace URIs, not `https://`
- prefer explicit, simple bindings over clever binding tricks
- be careful with popup and tooltip boundaries
- assume some WPF features behave differently or only partially
- validate changes against native game XAML when possible

If a feature feels like "this should work in WPF", that is not enough evidence for BG3.

## 6. Build Local Tooling Only When It Earns Its Keep

This repo benefited from repo-local validation for repeated mistakes, but that should be added deliberately, not by default.

For future projects, add local tooling for:

- XAML namespace mistakes
- pack URI mistakes
- suspicious tooltip patterns
- net message mismatches
- Lua patterns known to fail in BG3SE

This kind of tooling is high leverage because BG3 UI debugging inside the game is slow.

## 7. Test Pure Logic Outside The Game

Offline tests exist in this repo for `DataStore` and `FilterEngine`. That is the right boundary.

What to test outside BG3:

- filtering
- sorting
- indexing
- item normalization
- pure formatting helpers

What not to force into offline tests:

- live Noesis widget interaction
- live SE proxy lifetime behavior
- native tooltip integration

The goal is not total coverage. The goal is to move stable logic out of the in-game feedback loop.

## 8. Optimize For Reload Speed

The practical dev loop matters as much as architecture.

Patterns from this repo worth keeping:

- `reset` for fast Lua iteration
- targeted debug commands for VM rebinding
- explicit log prefixes
- clear hotkeys for opening panels and debug actions

Every minute saved from relaunching the game compounds quickly on UI work.

## 9. Prefer Reference-Driven Research

This project benefited from comparing against:

- native BG3 XAML files
- known modding patterns
- the BG3SE API surface in `API.md`

For future mods, research should start from:

1. native game XAML for the closest matching screen
2. BG3SE API docs for what can actually be accessed
3. local experiments with narrow scope

That order is better than inventing a custom structure first and trying to force engine behaviors into it later.

## 10. Reusable Project Rules

These rules are worth adopting across future BG3 UI mods:

- keep feature logic independent from panel-specific XAML
- treat client and server Lua as separate applications
- document engine constraints in-repo as they are discovered
- turn recurring mistakes into lint rules or tests
- keep a workflow document updated during development, not after

## Recommended Files To Carry Into Future Repos

- `Tests/TestRunner.lua`
- the pattern used by `Tests/test_FilterEngine.lua`
- the pattern used by `Tests/test_DataStore.lua`
- a narrow `Tools/` helper only if the project has enough repeated pain to justify it
- the bootstrap layout under `Mod/ScriptExtender/Lua/`
- a workflow/reference document like `WORKFLOW.md`

## Bottom Line

The main transferable result from this project is not "an inventory mod." It is a repeatable way to build BG3 UI mods:

- collect data on the server
- shape it on the client
- bind a clean VM to XAML
- mirror native structures when engine-owned behavior matters
- keep a written record of engine constraints
- support the workflow with local tests and linting
