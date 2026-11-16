-- Debug: simulate a failed save write or a damaged log, to show "!! Cannot save." (strings:249608) and "Sorry,
-- but Log %d has been erased..." (strings:249694) in their real boxes.
-- Both menus keep their state in struct+0x1F0E = 0x0300275E. Save menu (dispatch 0x0800DB80): 0 menu, 1 prompt,
-- 2 saved 0x0800E110, 3 cannot save 0x0800E218 (set only when the cartridge write fails). Load menu (Continue,
-- dispatch 0x0800EE40): 3 loaded 0x0800F26C, 4 erased 0x0800F330 (a log that fails its check). Each frame a FROM
-- becomes a TO: FROM=2 TO=3 (default) on save_menu, FROM=3 TO=4 on continue.
--   cover.py extra savefail -- --var "SCENE='save_menu'" --var "KEYS='...'" --script tools/debug/savefail.lua
local ST = 0x0300275E
local M = emu.memType.gbaMemory
local from, to = FROM or 2, TO or 3
L.on_frame(function()
  if emu.read(ST, M) == from then
    emu.write(ST, to, M)
    L.log("SAVEFAIL f" .. L.frame)
  end
end)
