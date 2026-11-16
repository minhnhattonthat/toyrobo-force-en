-- freeze.lua: hold RAM values every frame (cheat-style), e.g. god mode in battle.
-- emu.py ... --script tools/debug/freeze.lua --var "FREEZE='3005B0E=00C8'"  (hex addr=value; byte/half/word by
-- digit count, as warp.lua POKES). 0x03005B0E u16 = the battle HUD's bottom number (200 at the start of battle01,
-- 189 400 frames later; found by RAM diff with tools/debug/ramsnap.lua). Holding it does NOT stop the robot going
-- down: it is not the life. Battle god mode (docs/re/script.md §Battle): FREEZE='3003C98=00000000 3003DF8=3C'
-- (timer u32 held at 0 = no time-up; hit-invulnerability timer held = no damage).
local M = emu.memType.gbaMemory
local list = {}
for a, val in (FREEZE or ""):gmatch("(%x+)=(%x+)") do
  list[#list + 1] = { tonumber(a, 16), tonumber(val, 16), #val }
end
L.on_frame(function(n)
  for _, p in ipairs(list) do
    local a, v, w = p[1], p[2], p[3]
    if w <= 2 then emu.write(a, v, M) elseif w <= 4 then emu.write16(a, v, M) else emu.write32(a, v, M) end
  end
end)
