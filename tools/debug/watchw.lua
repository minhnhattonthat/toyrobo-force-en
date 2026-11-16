-- watchw.lua: log writes to a RAM range with the writing PC (find what changes a value).
-- emu.py ... --script tools/debug/watchw.lua --var "W_LO=0x03004EF8" --var "W_HI=0x03004EF8" [--var "W_VAL=0x13"]
-- W_VAL: log only writes of that value; W_MAX: stop logging after that many lines (default 200).
local n, max = 0, W_MAX or 200
L.on_write(W_LO, W_HI or W_LO, function(addr, value)
  if n >= max or (W_VAL and value ~= W_VAL) then return end
  n = n + 1
  L.log(string.format("f%d w %08X = %X pc %08X", L.frame, addr, value, L.pc()))
end)
