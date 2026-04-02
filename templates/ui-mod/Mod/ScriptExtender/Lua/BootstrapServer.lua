-- __MOD_NAME__ — Server Entry Point

Ext.Require("Server/NetHandlers.lua")

Ext.Events.SessionLoaded:Subscribe(function()
    _P("[__MOD_NAME__] Server loaded")
end)
