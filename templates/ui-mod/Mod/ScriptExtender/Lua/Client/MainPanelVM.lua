-- __MOD_NAME__ — Main Panel ViewModel
-- Manages binding between the Noesis XAML panel and Lua game state.
--
-- KEY RULES (learned the hard way):
--   1. Never cache Noesis proxy objects — always re-find them fresh each call.
--   2. Bind Canvas.Visibility to a VM string ("Visible"/"Collapsed") — BG3's
--      state machine owns UIWidget.Visibility and will fight you otherwise.
--   3. Call populate OR RequestRefresh, never both in the same frame (freezes/crashes).

Mods.__MOD_NAME__ = Mods.__MOD_NAME__ or {}
local VM = {}
Mods.__MOD_NAME__.MainPanelVM = VM

-- UI widget handle (re-found each call — never cached across turns)
local PANEL_NAME = "__MOD_NAME__MainPanel"

local state = {
    visible    = false,
    statusText = "Ready",
}

-- ── Internal helpers ──────────────────────────────────────────────────────────

local function GetWidget()
    -- Re-query the UI manager every time — Noesis proxies expire between calls.
    return Ext.UI.GetByName(PANEL_NAME)
end

local function GetVM(widget)
    if not widget then return nil end
    local ok, vm = pcall(function() return widget:GetRoot() end)
    return ok and vm or nil
end

local function PushState(vm)
    if not vm then return end
    pcall(function()
        vm.Visibility  = state.visible and "Visible" or "Collapsed"
        vm.StatusText  = state.statusText
    end)
end

-- ── Public API ────────────────────────────────────────────────────────────────

function VM.Init()
    -- Called once after SessionLoaded + 2s delay.
    -- Register any event listeners or initial data fetch here.
    _P("[__MOD_NAME__] MainPanelVM.Init")
end

function VM.TryBind()
    -- Attempts to bind the ViewModel to the Noesis panel.
    -- Safe to call multiple times — idempotent.
    local widget = GetWidget()
    if not widget then
        _P("[__MOD_NAME__] Panel not found: " .. PANEL_NAME)
        return false
    end
    local vm = GetVM(widget)
    if not vm then return false end
    PushState(vm)
    return true
end

function VM.Toggle()
    state.visible = not state.visible
    local widget = GetWidget()
    local vm     = GetVM(widget)
    PushState(vm)
    if widget then
        -- Show/hide the UIWidget so BG3 input routing works correctly.
        widget:SetVisible(state.visible)
    end
end

function VM.Show()
    state.visible = true
    local widget = GetWidget()
    if widget then widget:SetVisible(true) end
    PushState(GetVM(widget))
end

function VM.Hide()
    state.visible = false
    local widget = GetWidget()
    if widget then widget:SetVisible(false) end
    PushState(GetVM(widget))
end
