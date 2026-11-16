-- Text-coverage sweep: run every message (op 15) and choice (op 21) record in [LO, HI) one after another, so each
-- dialogue slot and choice menu is read once. Append after tools/debug/warp.lua with REC=<first target> and
-- emu.py --mash (A advances messages and picks a choice's first option); tools/debug/cover.py drives it.
-- At the interpreter's safe point (0x0800A338, as warp.lua): once the warp has landed on the first target, any
-- index other than the current target means that record finished (or branched away): jump to the next target.
-- A target still running after STUCK frames (default 900) is logged and skipped. Logs SWEEP DONE and stops.
-- OPS_LIST='31' sweeps other opcodes (31 = give part: fills the parts inventory); THEN=<record> jumps there after
-- the last target instead of stopping (THEN_POKES byte pokes first; THEN=80 THEN_POKES='3002675=01' = factory),
-- then presses AFTER ('300 -;6 a', route syntax; while they run --mash pauses).
local G = 0x03000850
local IDX = G + 0x1D08
local M = emu.memType.gbaMemory
local SCRIPT = 0x3831C8 -- ROM offset of the 12-byte records (docs/re/script.md)
local OPS = {}
for n in (OPS_LIST or "15,21"):gmatch("%d+") do OPS[tonumber(n)] = true end
local limit = STUCK or 900

local targets = {}
for r = LO, HI - 1 do
  local op = emu.read16(SCRIPT + r * 12, emu.memType.gbaPrgRom)
  if OPS[op] then targets[#targets + 1] = r end
end
L.log(string.format("SWEEP %d targets in records %d-%d", #targets, LO, HI - 1))
if #targets == 0 then L.finish(0) return end

local cur, since = nil, 0
L.on_exec(0x0800A338, 0x0800A338, function()
  if cur and cur > #targets then return end
  local idx = emu.read16(IDX, M)
  if cur == nil then
    if idx == targets[1] then cur, since = 1, L.frame end
    return
  end
  local stuck = L.frame - since > limit
  if idx == targets[cur] and not stuck then return end
  if stuck then L.log(string.format("STUCK rec %d f%d", targets[cur], L.frame)) end
  cur = cur + 1
  if cur > #targets then
    L.log(string.format("SWEEP DONE f%d", L.frame))
    if THEN then
      for addr, val in (THEN_POKES or ""):gmatch("(%x+)=(%x+)") do emu.write(tonumber(addr, 16), tonumber(val, 16), M) end
      emu.write16(IDX, THEN, M)
      L.log(string.format("THEN rec %d f%d", THEN, L.frame))
      for n, spec in (AFTER or ""):gmatch("(%d+)%s+([^;%s]+)") do L.press(spec, tonumber(n)) end -- stops --mash
    else
      L.finish(0)
    end
    return
  end
  since = L.frame
  emu.write16(IDX, targets[cur], M)
end)
