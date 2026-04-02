-- __MOD_NAME__ — Client Net Handlers
-- Receives broadcasts from the server.

Mods.__MOD_NAME__ = Mods.__MOD_NAME__ or {}

-- Example: uncomment and rename to handle a server broadcast
-- Ext.RegisterNetListener("__MOD_NAME___ExampleBroadcast", function(channel, payload)
--     local ok, data = pcall(Ext.Json.Parse, payload)
--     if not ok then return end
--     _P("[__MOD_NAME__] Received broadcast: " .. tostring(data))
-- end)
