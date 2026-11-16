-- autofight.lua: battle bot for a top-down battle (G12 arrest proof). Steers the robot (OAM 25, 32x32) at the
-- nearest enemy sprite (OAM 80-95, 16x16), fires A every other 8 frames, and rams it (the arrest: shoot it down,
-- then touch it). Pair with freeze.lua FREEZE='3003C98=00000000' (the battle timer, u32; time-up is the "loss":
-- 0x08012F70 compares it with the per-battle limit table 0x08249750[battle id 0x03004EF8]).
-- Optional: BOT_FIRE=0 never fires (ram only); BOT_LOG=N logs the target every N frames.
local M = emu.memType.gbaSpriteRam
local want = {}
local function spr(i)
  local a0, a1 = emu.read16(i * 8, M), emu.read16(i * 8 + 2, M)
  if (a0 & 0x300) == 0x200 then return nil end
  local x, y = a1 & 0x1FF, a0 & 0xFF
  if x >= 240 then x = x - 512 end
  if y >= 160 then y = y - 256 end
  local half = ({ 4, 8, 16, 32 })[(a1 >> 14) + 1]  -- square sprites only (shape 0)
  return x + half, y + half, emu.read16(i * 8 + 4, M) & 0x3FF
end
L.on_frame(function(f)
  want = {}
  local px, py = spr(25)
  if not px then return end
  py = py + 4
  -- Target groups in priority order (OAM index = object index in 0x03003E90): 112-126 large Teka (the culprit),
  -- 80-95 enemy robots; the nearest visible sprite of the first group that has one.
  local best, bx, by
  for _, g in ipairs({ { 112, 126 }, { BOT_LO or 80, BOT_HI or 95 } }) do
    for i = g[1], g[2] do
      local x, y = spr(i)
      if x and x > 32 and x < 240 and y > 0 and y < 160 then
        local d = (x - px) ^ 2 + (y - py) ^ 2
        if not best or d < best then best, bx, by = d, x, y end
      end
    end
    if best then break end
  end
  if best then
    if bx < px - 3 then want.left = true elseif bx > px + 3 then want.right = true end
    if by < py - 3 then want.up = true elseif by > py + 3 then want.down = true end
  elseif (f // 120) % 2 == 0 then want.up = true else want.right = true end
  if (BOT_FIRE or 1) ~= 0 and (f // 8) % 2 == 0 then want.a = true end
  if BOT_LOG and f % BOT_LOG == 0 then
    L.log(string.format("f%d p %d,%d target %s", f, px, py, best and string.format("%d,%d", bx, by) or "-"))
  end
end)
emu.addEventCallback(L.safe(function() emu.setInput(want, 0) end), emu.eventType.inputPolled)
