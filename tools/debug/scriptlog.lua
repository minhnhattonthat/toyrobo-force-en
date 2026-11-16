-- Probe: log every script record the main interpreter fetches (0x0800A338: about to read the index), with the
-- record bytes and a few state bytes of the game struct at 0x03000850. Use with emu.py --script.
--   IDX   u16 +0x1D08 current record index     SEC  u8 +0x1F0C section id (set by opcode 0x28)
--   MAP   u8  +0x1E24 / +0x1E25 / +0x1E26 (map-script selectors, guesses)
local G = 0x03000850
local M = emu.memType.gbaMemory
local function rd(a) return emu.read(a, M) end
local function rd16(a) return emu.read16(a, M) end
local last = -1
L.on_exec(0x0800A338, 0x0800A338, function()
  local idx = rd16(G + 0x1D08)
  if idx == last then return end
  last = idx
  local rec = 0x083831C8 + idx * 12
  local t = {}
  for i = 0, 5 do t[#t + 1] = string.format("%d", rd16(rec + i * 2)) end
  L.log(string.format("f%d idx %d op %s sec %d m %d/%d/%d", L.frame, idx, table.concat(t, ","),
    rd(G + 0x1F0C), rd(G + 0x1E24), rd(G + 0x1E25), rd(G + 0x1E26)))
end)
