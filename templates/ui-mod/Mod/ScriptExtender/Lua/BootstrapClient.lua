-- __MOD_NAME__ — Client Entry Point

Ext.Require("Client/NetHandlers.lua")
Ext.Require("Client/MainPanelVM.lua")

Ext.Events.SessionLoaded:Subscribe(function()
    _P("[__MOD_NAME__] Client loaded")

    Ext.Timer.WaitFor(2000, function()
        local ok, err = pcall(Mods.__MOD_NAME__.MainPanelVM.Init)
        if ok then
            pcall(Mods.__MOD_NAME__.MainPanelVM.TryBind)
        else
            _P("[__MOD_NAME__] MainPanelVM.Init failed: " .. tostring(err))
        end
    end)

    pcall(function()
        MCM.Keybinding.SetCallback("main_panel_key", function()
            pcall(Mods.__MOD_NAME__.MainPanelVM.TryBind)
            Mods.__MOD_NAME__.MainPanelVM.Toggle()
        end)
        _P("[__MOD_NAME__] MCM keybindings registered")
    end)
end)
