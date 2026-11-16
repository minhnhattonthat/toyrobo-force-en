# Event script, game state RAM, debug warp (phase 2)

Addresses for the dump in `rom.sha1`. Listing: `python -X utf8 tools/script_dump.py > work/re/script.txt`.

## Main event script (verified: disassembly of 0x0800A2E4 + runtime log `tools/debug/scriptlog.lua`)
- One array of **5538 records x 12 bytes** at ROM **0x3831C8-0x393560**: `u16 opcode, u16 a1..a5`. The pointer
  comes from table 0x083F36DC[struct+0x1D07] (entry 0 = 0x083831C8; the other entries are graphics pointers, so
  the selector byte stays 0).
- Interpreter at 0x0800A2E4, called per frame: `r4 = script + idx*12`, `opcode <= 0x2A`, jump table at 0x0800A378.
  **0x0800A338** is the safe point (about to read the index; no opcode running): the warp hooks it.
- **Game struct base 0x03000850** (IWRAM). Fields used:
  | field | addr | meaning | state |
  |---|---|---|---|
  | +0x1D08 u16 | 0x03002558 | current record index | verified (warp) |
  | +0x1D0A u16 | 0x0300255A | resume record (saved by op 40 and op 23) | disasm |
  | +0x1D07 u8 | 0x03002557 | script table selector (always 0) | disasm |
  | +0x1E24 u8 | 0x03002674 | current map id (op 22 a1) | runtime log |
  | +0x1E25 u8 | 0x03002675 | set by op 39 (a1-1); op 22 needs it (map entry point?). Mid-section map warps poke it | verified (wrong value -> map script jumped to record 0) |
  | +0x1E26 u8 | 0x03002676 | music (op 17 a2) | guess |
  | +0x1F0C u8 | 0x0300275C | opcode result: battle won (1) / lost (0); op 40 also stores its section id | verified (disasm 0x0800D7F8, watch) |
  | +0x0800.. | 0x03001050 | 0x280 u16 flag array, cleared to 0xF001 by op 4 | disasm, guess |
- Opcodes (counts over the script; meanings from disasm + runtime, **guess** unless noted):
  | op | n | args | meaning |
  |---|---|---|---|
  | 15 | 2927 | portrait, ?, 10, **slot** | message: slot k at 0x397070 + k*0x80 (verified: slot = record order) |
  | 19 | 575 | rec | goto (verified, runtime) |
  | 21 | 199 | 5, 3, choice id | choice menu (0x3766BC table); branches by following gotos |
  | 22 | 296 | map, mode, map-script entry | enter map; mode 1 = interactive location selector (verified, runtime) |
  | 23 | 95 | battle id (0-35), win rec, lose rec | battle (verified: 0x0800D7F8 picks by +0x1F0C) |
  | 25 / 26 | 87 / 105 | flag, value / flag, rec | set flag / jump if flag set |
  | 31 | 47 | slot, part, rec, ... | give part (messages ボディ/右腕/左腕/パソコプ) |
  | 34 / 35 | 250 / 100 | rec / - | gosub / return (verified, runtime: 80 -> 5303 -> 81) |
  | 38 | 87 | 0-5 | facility menu (0 = factory: A メンテ, B もどる, R じょうほう = robot status panel) (verified) |
  | 39 | 186 | n | struct+0x1E25 = n-1 |
  | 40 | 24 | section 0-23 | section start: card / location banner, saves the resume record (verified) |
  | 41 | 1 | - | ending (record 5412: ending report, cast, staff, then post-game at 5413) (verified) |
  | 42 | 1 | - | new-game start (record 0) |
  | 17 | 200 | 1, n | music |
  | 14 | 206 | 3 / 6 / 7 | screen effect (7 often before messages; 3 once, before the ending) |
  | 30 | 20 | 1-2, price, recs | purchase prompt |
  | 4, 5, 12, 13, 16, 18, 24, 36 | rare | | unknown: each first use is a warp scene (`op04_sewer`...) |
- Story order: sections 0-23 at records 5..4582; the last story battle is battle 19 (record 4719); record 4794
  goes to the ending (5412). Records 4800-5538 are shop/workshop subroutines and the post-game.

## Battle (verified: watch on 0x0300275C, disassembly)
- Battle end handlers: **win 0x080138C8** (draws the sortie report 出撃報告書 with the result balloon, G10; stores
  +0x1F0C = 1), **loss 0x0801394C** (+0x1F0C = 0); jump table 0x0801381C indexed by 0x03005070. Battle 0 (training
  chase) ends on its timer as a loss after ~1150 frames.
- Debug only: `warp.lua` WIN=1 writes `b 0x080138C8` (0xE7BC) over the loss handler's first instruction in the
  emulator's ROM copy, so every loss becomes a win; LOSE=1 the reverse. Never in a release build.
- Not found yet: robot life / enemy life addresses (a GOD mode). Not needed for scene coverage.

## Debug warp (phase 2)
- `tools/debug/warp.lua` + `tools/debug/scenes.gba.txt`; `tools/debug/warp_all.py` runs every scene and builds
  `work/qa/warp_all/finals*.png`; `--states` regenerates `work/states/<scene>.mss`.
- Title scenes boot to the title menu and drive it with keys (Continue = load screen 日誌1-4, two-player menu).
- Field: START on a map = save screen (日誌1-4 きろくなし), A = save prompt (セーブする/しない, SELECT label);
  B = location selector (banner + arrows; 警察学校, 工場, ゲート in section 1).
- A warp into the middle of a section keeps the previous screen's graphics until the script loads a map or scene,
  so text shows over garbage tiles: pick a record at or just before an op 22 / op 14 for clean shots.
- Leftover debug text: 0x2494DC 「これはシナリオテストだから顔窓もサイズが変わります…」 (scenario-test line;
  no menu found that shows it).
