-- objlog.lua: dump the battle object table (0x03003E90, 0x18 bytes each, OBJ_N entries, default 40) and the
-- parallel table 0x03005270 (16 bytes each) at frame OBJ_AT (default 1). +0x12 = score on a kill, +0x14 != 0 =
-- arrestable (the arrest path 0x0801BA0C marks struct+0x1F61 records and sets 0x03005270[i]+0xB = 4).
local M = emu.memType.gbaMemory
local function hex(a, n)
  local t = {}
  for k = 0, n - 1, 2 do t[#t + 1] = string.format("%04X", emu.read16(a + k, M)) end
  return table.concat(t, " ")
end
L.on_frame(function(f)
  if f ~= (OBJ_AT or 1) then return end
  for i = 0, (OBJ_N or 40) - 1 do
    L.log(string.format("%2d %s | %s", i, hex(0x03003E90 + i * 0x18, 0x18), hex(0x03005270 + i * 16, 16)))
  end
end)
