# __MOD_NAME__

A Baldur's Gate 3 mod.

## Development

This template does not include shared scripts for watching logs, linting, or packaging. Add only the tooling this mod actually needs.

## Structure

```text
Mod/
`-- ScriptExtender/
    |-- Config.json
    `-- Lua/
        |-- BootstrapClient.lua
        |-- BootstrapServer.lua
        |-- Client/
        |   `-- NetHandlers.lua
        `-- Server/
            `-- NetHandlers.lua
```

## Net Channel Convention

Prefix net channel names with `__MOD_NAME___` to avoid collisions.
