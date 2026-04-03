# __MOD_NAME__

A Baldur's Gate 3 UI mod built with Noesis XAML and BG3 Script Extender.

## Development

This template does not include an opinionated toolchain. Add the scripts, logging workflow, packaging steps, and validation you want for this mod.

## Structure

```text
Mod/
|-- GUI/
|   |-- Pages/
|   |   `-- MainPanel.xaml     # Main UI panel
|   `-- Resources/
|       `-- Resources.xaml     # Shared styles and brushes
`-- ScriptExtender/
    |-- Config.json
    `-- Lua/
        |-- BootstrapClient.lua
        |-- BootstrapServer.lua
        |-- Client/
        |   |-- MainPanelVM.lua
        |   `-- NetHandlers.lua
        `-- Server/
            `-- NetHandlers.lua
Tests/
|-- TestRunner.lua
|-- test_example.lua
Tools/
`-- .gitkeep
```

## Key Patterns

- Never cache Noesis proxies
- Bind `Canvas.Visibility` to a VM string property
- Use `http://` in XAML namespace attributes, not `https://`
- Prefer `Trigger Property="Tag"` over `DataTrigger` for binding-driven tag changes
- Prefer `WrapPanel` over a horizontal `StackPanel` when grid columns use `Width="*"`

## MCM Keybinding

Default key: F10. Change `Default.Keyboard.Key` in `Mod/MCM_blueprint.json`.
