# __MOD_NAME__

A Baldur's Gate 3 UI mod built with Noesis XAML and BG3 Script Extender.

## Development

```powershell
# Watch BG3 log output
python Tools/watch_log.py

# Lint Lua and XAML files
python Tools/lint.py

# Pack for release (run from BG3ModDev root)
..\..\..\tools\Pack-Mod.ps1 -ModName __MOD_NAME__ -Version 1.0.0
```

## Structure

```
Mod/
├── GUI/
│   ├── Pages/
│   │   └── MainPanel.xaml     # Main UI panel (Canvas root, Visibility bound to VM)
│   └── Resources/
│       └── Resources.xaml     # Shared styles and brushes
└── ScriptExtender/
    ├── Config.json            # SE config
    └── Lua/
        ├── BootstrapClient.lua
        ├── BootstrapServer.lua
        ├── Client/
        │   ├── MainPanelVM.lua    # Noesis ViewModel — bind/toggle panel
        │   └── NetHandlers.lua    # Server broadcast listeners
        └── Server/
            └── NetHandlers.lua   # Client request handlers
Tests/
├── TestRunner.lua             # Offline test harness (no BG3 needed)
└── test_example.lua           # Example test file
```

## Key Patterns

- **Never cache Noesis proxies** — re-find UI objects fresh on every call
- **Bind Canvas.Visibility** to a VM string property, not UIWidget.Visibility (BG3 owns that)
- **http:// not https://** in XAML xmlns attributes (https:// crashes the game)
- **Use `Trigger Property="Tag"`** not `DataTrigger` for binding-driven Tag changes in ControlTemplates
- **WrapPanel not horizontal StackPanel** when columns use `Width="*"`

## MCM Keybinding

Default key: F10 (configurable in Mod Configuration Menu → __MOD_NAME__ → Settings).
Change `Default.Keyboard.Key` in `Mod/MCM_blueprint.json`.
