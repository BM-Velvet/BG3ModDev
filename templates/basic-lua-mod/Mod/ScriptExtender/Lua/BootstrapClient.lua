-- __MOD_NAME__ — Client Entry Point

Ext.Require("Client/NetHandlers.lua")

Ext.Events.SessionLoaded:Subscribe(function()
    _P("[__MOD_NAME__] Client loaded")
end)
