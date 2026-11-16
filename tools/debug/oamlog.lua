-- oamlog.lua: log the visible OAM sprites (index, x, y, tile, palette, shape/size) at frame OAM_AT (default 1).
local M = emu.memType.gbaSpriteRam
L.on_frame(function(f)
  if f ~= (OAM_AT or 1) then return end
  for i = 0, 127 do
    local a0 = emu.read16(i * 8, M)
    local a1 = emu.read16(i * 8 + 2, M)
    local a2 = emu.read16(i * 8 + 4, M)
    local hidden = (a0 & 0x300) == 0x200
    if not hidden then
      local y, x = a0 & 0xFF, a1 & 0x1FF
      L.log(string.format("%3d x%3d y%3d tile %4d pal %2d shape %d size %d", i, x, y, a2 & 0x3FF, a2 >> 12,
        a0 >> 14, a1 >> 14))
    end
  end
end)
