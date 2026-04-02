# __MOD_NAME__

A Baldur's Gate 3 mod.

## Development

```powershell
# Watch BG3 log output
python ../../tools/shared/watch_log.py --mod __MOD_NAME__

# Lint Lua files
python ../../tools/shared/lint.py --mod-root .
```

## Structure

```
Mod/
└── ScriptExtender/
    ├── Config.json          # SE config: ModTable, RequiredVersion
    └── Lua/
        ├── BootstrapClient.lua
        ├── BootstrapServer.lua
        ├── Client/
        │   └── NetHandlers.lua
        └── Server/
            └── NetHandlers.lua
```

## Net Channel Convention

All net channel names should be prefixed with `__MOD_NAME___` to avoid collisions.
