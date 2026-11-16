-- Probe: log each change of the battle state byte 0x03005070 (0 init, 1 running?, 2 win, 3 lose, 4+ ending;
-- handler table at 0x0801381C). Use with emu.py --script.
local last = -1
L.on_frame(function(f)
  local v = emu.read(0x03005070, emu.memType.gbaMemory)
  if v ~= last then L.log(string.format("f%d bstate %d", f, v)); last = v end
end)
-- Log the first frame and every 300th call of the dispatcher (0x080137FC) and the state-0 handler.
local n1, n2 = 0, 0
L.on_exec(0x080137FC, 0x080137FC, function()
  n1 = n1 + 1
  if n1 == 1 or n1 % 300 == 0 then L.log(string.format("f%d dispatch #%d", L.frame, n1)) end
end)
L.on_exec(0x0801383C, 0x0801383C, function()
  n2 = n2 + 1
  if n2 == 1 or n2 % 300 == 0 then L.log(string.format("f%d state0 #%d", L.frame, n2)) end
end)
