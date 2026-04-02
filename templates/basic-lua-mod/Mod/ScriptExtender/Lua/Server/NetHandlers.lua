-- __MOD_NAME__ — Server Net Handlers
-- Receives requests from the client and broadcasts results.

Mods.__MOD_NAME__ = Mods.__MOD_NAME__ or {}

-- Example: respond to a client request
-- Ext.RegisterNetListener("__MOD_NAME___ExampleRequest", function(channel, payload, userId)
--     local result = { message = "hello from server" }
--     Ext.Net.BroadcastMessage("__MOD_NAME___ExampleBroadcast", Ext.Json.Stringify(result))
-- end)
