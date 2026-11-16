-- ramsnap.lua: RAM dumps at chosen frames, for diffing (e.g. finding a HUD value's address).
-- emu.py ... --script tools/debug/ramsnap.lua --var "SNAP_AT={1760,2160}" --var "SNAP_DIR=[[C:/abs/dir]]"
-- Writes SNAP_DIR/ram_<frame>.bin via L.dump_ram (absolute dir: Mesen runs in tools/mesen).
local at = {}
for _, f in ipairs(SNAP_AT or {}) do at[f] = true end
L.on_frame(function(n)
  if at[n] then L.dump_ram(string.format("%s/ram_%06d.bin", SNAP_DIR or ".", n)) end
end)
