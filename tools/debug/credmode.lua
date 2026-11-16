-- Probe: which credits handler runs, and in which state. The main loop (0x0800065E) calls one of two credits
-- sequences while bit 5 of struct+0x284C is set: mode struct+0x1F0D == 1 -> 0x08000764 (story ending), == 0 ->
-- 0x08001FB4 (states 0-6, state = struct+0x1F0E; states 3 and 5 draw "And" / "In"). Logs each change of
-- (handler, state). Use with emu.py --script tools/debug/warp.lua --script tools/debug/credmode.lua.
local G = 0x03000850
local M = emu.memType.gbaMemory
local last = ""
local function hit(name)
  return function()
    local s = string.format("%s mode %d state %d", name, emu.read(G + 0x1F0D, M), emu.read(G + 0x1F0E, M))
    if s ~= last then
      last = s
      L.log(string.format("f%d CRED %s", L.frame, s))
    end
  end
end
-- MODE0=1: clear the mode byte each time the main loop reads it (0x08000640), so the ending (REC=4794) plays the
-- mode-0 roll the script never selects (record 4794 op 14 3 is followed by op 41, mode 1). For a fit check only.
if MODE0 then
  L.on_exec(0x08000640, 0x08000640, function() emu.write(G + 0x1F0D, 0, M) end)
end
L.on_exec(0x08001FB4, 0x08001FB4, hit("mode0"))
L.on_exec(0x08000764, 0x08000764, hit("mode1"))
