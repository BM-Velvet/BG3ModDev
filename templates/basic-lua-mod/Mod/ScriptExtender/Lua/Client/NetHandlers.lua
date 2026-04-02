-- __MOD_NAME__ — Client Net Handlers
-- Receives broadcasts from the server.

Mods.__MOD_NAME__ = Mods.__MOD_NAME__ or {}

-- Example: listen for a broadcast from the server
-- Ext.RegisterNetListener("__MOD_NAME___ExampleBroadcast", function(channel, payload)
--     local data = Ext.Json.Parse(payload)
--     _P("[__MOD_NAME__] Received: " .. tostring(data))
-- end)
