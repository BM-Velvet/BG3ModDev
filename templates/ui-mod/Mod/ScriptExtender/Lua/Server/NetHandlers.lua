-- __MOD_NAME__ — Server Net Handlers
-- Receives requests from the client and broadcasts results.

Mods.__MOD_NAME__ = Mods.__MOD_NAME__ or {}

-- Example: uncomment and rename to handle a client request
-- Ext.RegisterNetListener("__MOD_NAME___ExampleRequest", function(channel, payload, userId)
--     local ok, args = pcall(Ext.Json.Parse, payload)
--     if not ok then return end
--
--     -- ... do server-side work ...
--     local result = { status = "ok" }
--     Ext.Net.BroadcastMessage("__MOD_NAME___ExampleBroadcast", Ext.Json.Stringify(result))
-- end)
