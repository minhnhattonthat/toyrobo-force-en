-- Debug: show every factory description (descs:0-143, 0x393EF0 + n*0x58) in its real window, for text coverage.
-- The factory formats each desc with sprintf 0x08025F90(buf, fmt, ...) (directly or through 0x0800A098(fmt));
-- fmt = 0x08393EF0 + (3*msg + keeper)*0x58, keeper = struct+0x1F0C (see 0x08003940). On each sprintf whose fmt
-- points into the table this swaps in the next desc with the same printf signature (none, %s, %d, ...: the
-- caller's arguments still fit; a plain call may also take a %d one), so ordinary factory use (icon cursor moves
-- for the plain and %d ones, assemblies for the %s ones) draws them all:
--   cover.py extra descs -- --var "SCENE='factory'" --script tools/debug/descs.lua --var "KEYS='300 -;6 right;60 -;...'"
-- ONLY='119' serves just those ids. Logs "DESC n f<frame>" per swap and "DESC LEFT <sig>: n" for signatures not yet used up, every 600 frames.
-- Never in a release build (Lua only).
local BASE, N, STRIDE = 0x08393EF0, 144, 0x58
local M = emu.memType.gbaMemory
local only = nil  -- ONLY='119,120': serve just these ids
if ONLY then
  only = {}
  for id in tostring(ONLY):gmatch("%d+") do only[tonumber(id)] = true end
end
local queues = {}  -- signature -> list of desc ids still to show
for n = 0, N - 1 do
  if only and not only[n] then goto continue end
  local sig, a = "", BASE + n * STRIDE
  for i = 0, STRIDE - 2 do
    local b = emu.read(a + i, M)
    if b == 0 then break end
    if b == 0x25 then sig = sig .. string.char(emu.read(a + i + 1, M)) end
  end
  queues[sig] = queues[sig] or {}
  table.insert(queues[sig], n)
  ::continue::
end
local key
L.on_exec(0x08025F90, 0x08025F90, function()
  local s = emu.getState()
  if not key then key = s["cpu.r1"] and "cpu.r1" or "cpu.r[1]" end
  local fmt = s[key] or -1
  if fmt < BASE or fmt >= BASE + N * STRIDE then return end
  local n = (fmt - BASE) // STRIDE
  local sig = ""  -- the printf signature of the desc the game asked for
  for i = 0, STRIDE - 2 do
    local b = emu.read(BASE + n * STRIDE + i, M)
    if b == 0 then break end
    if b == 0x25 then sig = sig .. string.char(emu.read(BASE + n * STRIDE + i + 1, M)) end
  end
  local q = queues[sig]
  if (not q or #q == 0) and sig == "" then
    -- a plain desc asked with no arguments may become a %d one: sprintf prints whatever number is in r2 (the
    -- value is junk, the text is the string under test); %s never (a junk pointer can hang the drawer)
    for sg, q2 in pairs(queues) do
      if #q2 > 0 and sg:match("^d+$") then q = q2 end
    end
  end
  if q and #q > 0 then
    local m = table.remove(q, 1)
    emu.setState({ [key] = BASE + m * STRIDE })
    L.log(string.format("DESC %d f%d (asked %d)", m, L.frame, n))
  end
end)
L.on_frame(function()
  if L.frame % 600 ~= 0 then return end
  for sg, q in pairs(queues) do
    if #q > 0 then L.log(string.format("DESC LEFT '%s': %d", sg, #q)) end
  end
end)
