-- objwatch.lua: log battle object OBJ_I (default 114) every OBJ_EVERY frames (default 50): the 0x03003E90 entry
-- (0x18 bytes) and its 0x03005270 entry (x, y in 1/16 px at +0/+2).
local M = emu.memType.gbaMemory
local i, every = OBJ_I or 114, OBJ_EVERY or 50
local function hex(a, n)
  local t = {}
  for k = 0, n - 1, 2 do t[#t + 1] = string.format("%04X", emu.read16(a + k, M)) end
  return table.concat(t, " ")
end
L.on_frame(function(f)
  if f % every ~= 0 then return end
  L.log(string.format("f%d o%d %s | %s", f, i, hex(0x03003E90 + i * 0x18, 0x18), hex(0x03005270 + i * 16, 16)))
end)
