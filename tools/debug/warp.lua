-- Debug warp for Toyrobo Force (GBA). Use with emu.py --script tools/debug/warp.lua --var "SCENE='<name>'".
-- Cold boot -> title -> New game (presses queued here; give no --route) -> on the main script interpreter's first
-- record fetch (exec 0x0800A338, the safe point: no opcode is running) the record index (u16 at 0x03002558 =
-- game struct 0x03000850 + 0x1D08) is overwritten with the scene's record, then the game runs from there.
-- Scene list: tools/debug/scenes.gba.txt (name, record index, optional pokes, optional presses after the warp).
-- Opt-in globals: REC=<n> warps to any record without a scene entry; KEYS='300 -;6 start' replaces the scene's
-- after-warp presses; POKES='3002675=01' replaces its pokes (hex addr=value, value width = byte/half/word by
-- digit count); SCENES=[[path]] overrides the list path; WIN=1 / LOSE=1 turn every battle's end into a win / a
-- loss (below). Addresses and opcodes: docs/re/script.md.
local G = 0x03000850
local IDX = G + 0x1D08
local M = emu.memType.gbaMemory

local function load_scenes(path)
  local t = {}
  for line in io.lines(path) do
    local l = line:gsub("#.*", "")
    local f = {}
    for col in (l .. "|"):gmatch("([^|]*)|") do f[#f + 1] = col:match("^%s*(.-)%s*$") end
    -- columns: name, record (or "title"), hold frames (read by warp_all.py), pokes, keys, flags
    if f[1] and f[1] ~= "" then
      t[f[1]] = { rec = tonumber(f[2]), title = f[2] == "title", pokes = f[4] or "", keys = f[5] or "",
                  flags = f[6] or "" }
    end
  end
  return t
end

local scene
if REC then
  scene = { rec = REC, pokes = "", keys = "", flags = "" }
else
  -- The default path is relative to Mesen's working folder (once tools/mesen, now emu.py's per-run folder, so it
  -- no longer resolves): warp_all.py and cover.py pass SCENES=[[absolute path]]; hand runs should too.
  local scenes = load_scenes(SCENES or "../debug/scenes.gba.txt")
  scene = scenes[SCENE or ""]
  if not scene then error("unknown SCENE " .. tostring(SCENE) .. " (see tools/debug/scenes.gba.txt)") end
end

local function queue_keys(s)  -- "FRAMES BUTTONS;FRAMES BUTTONS", same syntax as a route line
  for step in s:gmatch("[^;]+") do
    local n, spec = step:match("^%s*(%d+)%s+(%S+)%s*$")
    if n then L.press(spec, tonumber(n)) end
  end
end

-- Boot presses: logos (~1000 frames), START at "PRESS START" (-> title menu, cursor on New game).
L.press("-", 1000); L.press("start", 6); L.press("-", 300)
if scene.title then
  -- Title-menu scene (Continue, link battle): no warp, the scene's keys drive the title menu.
  queue_keys(KEYS or scene.keys)
  L.log("TITLE scene " .. tostring(SCENE))
  return
end
L.press("start", 6); L.press("-", 300); L.press("a", 6); L.press("-", 30)

local function apply_pokes(s)
  for addr, val in s:gmatch("(%x+)=(%x+)") do
    local a, v = tonumber(addr, 16), tonumber(val, 16)
    if #val <= 2 then emu.write(a, v, M) elseif #val <= 4 then emu.write16(a, v, M) else emu.write32(a, v, M) end
  end
end

local warped = false
L.on_exec(0x0800A338, 0x0800A338, function()
  if warped then return end
  warped = true
  apply_pokes(POKES or scene.pokes)
  emu.write16(IDX, scene.rec, M)
  L.log(string.format("WARP f%d scene %s rec %d", L.frame, tostring(SCENE or REC), scene.rec))
  queue_keys(KEYS or scene.keys)  -- after-warp presses
end)

-- WIN=1: every battle that ends in a loss (timer out or robot down; just wait) ends in a win instead. Patches the
-- emulator's ROM copy only: the loss handler 0x0801394C (stores struct+0x1F0C = 0) starts with a Thumb branch to
-- the win handler 0x080138C8 (result balloon, struct+0x1F0C = 1). LOSE=1 does the reverse.
local function patch16(cpu_addr, half)
  emu.write(cpu_addr - 0x08000000, half & 0xFF, emu.memType.gbaPrgRom)
  emu.write(cpu_addr - 0x08000000 + 1, half >> 8, emu.memType.gbaPrgRom)
end
if scene.flags:find("win") then WIN = 1 end
if scene.flags:find("lose") then LOSE = 1 end
if WIN then patch16(0x0801394C, 0xE7BC) end  -- b 0x080138C8
if LOSE then patch16(0x080138C8, 0xE040) end -- b 0x0801394C
