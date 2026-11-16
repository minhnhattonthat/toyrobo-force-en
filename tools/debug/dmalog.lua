-- GBA DMA3 log: every write to DMA3SAD/DAD/CNT (0x040000D4-0x040000DF) between FROM and TO, one line per DMA start
-- (src, dst, count/flags), so a VRAM tile can be traced to its ROM or RAM source.
--   emu.py ROM --script tools/debug/dmalog.lua --var FROM=1030 --var TO=1036 [--var DST_LO=0x06008000 --var DST_HI=0x0600FFFF]
local from, to = FROM or 0, TO or math.huge
local lo, hi = DST_LO or 0, DST_HI or 0xFFFFFFFF
local src, dst = 0, 0
L.on_write(0x040000D4, 0x040000DF, function(addr, value)
  if L.frame < from or L.frame > to then return end
  if addr == 0x040000D4 then src = value
  elseif addr == 0x040000D8 then dst = value
  elseif addr == 0x040000DC and dst >= lo and dst <= hi then
    L.log(string.format("f%d DMA3 src=%08X dst=%08X cnt=%08X", L.frame, src, dst, value))
  end
end)
