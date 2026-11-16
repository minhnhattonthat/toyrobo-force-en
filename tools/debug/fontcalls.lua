-- Who draws text through the font lookup? Logs each distinct (caller, code) at 0x0800FC30 (docs/re/font.md):
--   emu.py ROM --script tools/debug/warp.lua --var "SCENE='sec05'" --script tools/debug/fontcalls.lua [--var FROM=1400]
-- Lines: "FONT f<frame> lr=<return address> code=<SJIS code> <char>". Text drawn without this lookup (graphics) logs
-- nothing, so a screen whose words never show up here is tiles, not text.
local from = FROM or 0
local seen, keys = {}, nil
local function reg(s, n)
  return s["cpu.r" .. n] or (s["cpu.r"] and s["cpu.r"][n]) or -1
end
L.on_exec(0x0800FC30, 0x0800FC30, function()
  if L.frame < from then return end
  local s = emu.getState()
  if not keys then
    keys = {}
    for k, _ in pairs(s) do if k:find("^cpu%.") then keys[#keys + 1] = k end end
    table.sort(keys)
    L.log("FONT state keys: " .. table.concat(keys, " ", 1, math.min(#keys, 40)))
  end
  local code, lr = reg(s, 0) & 0xFFFF, reg(s, 14)
  local k = lr .. ":" .. code
  if seen[k] then return end
  seen[k] = true
  L.log(string.format("FONT f%d lr=%08X code=%04X", L.frame, lr, code))
end)
