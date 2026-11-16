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

## Credits rolls (verified: disassembly + `tools/debug/credmode.lua`)
- The main loop (0x0800065E) runs a credits roll while bit 5 of struct+0x284C is set; struct+0x1F0D picks it:
  **1 -> 0x08000764** (the staff roll; states 0-27+ in struct+0x1F0E), **0 -> 0x08001FB4** (a 7-state cast card:
  Yuki Tachibana / Tomomi Attenborough / Gilligan Brock / "And" Blank / "In" Toyrobo Force; jump table 0x08001FDC).
  Op 41 sets the mode to 1, op 42 to 0 (handlers 0x0800A628 / 0x0800A634). Op 14 3 (record 4794, the only op 14
  3) starts the roll and is followed by goto 5412 = op 41, so the mode-0 card never runs in game; op 42 is only
  record 0. `credmode.lua --var MODE0=1` forces it at REC=4794 (shot `work/qa/credits_andin.png`: both fit).
- Op 14 args: 3 = credits (0x0800D068(2,1)), 6 (87 records) and 7 (118) are other screen effects; 2, 4, 5 unused.

## Factory, parts and save RAM (verified in game: pokes + `tools/debug/descs.lua`, `savefail.lua`)
- Parts owned (u8 counts, cap 99, op 31 = 0x0800D21C): struct+0x1D47 (8 bodies), +0x1D4F (39 right arms), +0x1D76
  (19 left arms), +0x1D89 (8 Pasocops), +0x1D91 (options). Money u32 +0x1D0C (0x0300255C).
- Save/load menu state +0x1F0E; factory keeper (desc variant) +0x1F0C; factory desc n = 0x393EF0 +
  (3*msg+keeper)*0x58. sprintf 0x08025F90. Arm data: right 0x393600, left 0x393AE0 (0x20 each: power +0x16, ways
  +0x17, shots +0x18).
- SRAM log n at 0x0E000000 + n*0x640 (4 copies at +k*0x190; hours u16 +0x10, minutes +0x12).

## Battle (verified: watch on 0x0300275C, disassembly)
- Battle end handlers: **win 0x080138C8** (draws the sortie report 出撃報告書 with the result balloon, G10; stores
  +0x1F0C = 1), **loss 0x0801394C** (+0x1F0C = 0); jump table 0x0801381C indexed by 0x03005070. Battle 0 (training
  chase) ends on its timer as a loss after ~1150 frames.
- Debug only: `warp.lua` WIN=1 writes `b 0x080138C8` (0xE7BC) over the loss handler's first instruction in the
  emulator's ROM copy, so every loss becomes a win; LOSE=1 the reverse. Never in a release build.
- Loss causes (verified by write watch + disassembly, phase 8 G12):
  - **Time-up**: 0x08012F70 compares the battle timer u32 0x03003C98 with the limit table 0x08249750 (u16 per
    battle id; battle id u8 0x03004EF8) and sets 0x03005070 = 1. Battle01 times out at ~f2150 of a warp.
  - **Robot down**: player hit handler ~0x08017F40: if the invulnerability timer u8 0x03003DF8 (0x03003DF0+8) is 0,
    HP u8 at 0x03005A80 + 16*[0x03005C78] + 2 drops by 1 and the timer is set to 60; HP 0 -> 0x080180C8 (lives
    0x03003E16 -1 -> mode 0x0300502C = 5 -> loss). Mode byte 0x0300502C: 4 battle running, 5 robot down, 9 loss
    report, 10 win report.
  - God mode: `freeze.lua` FREEZE='3003C98=00000000 3003DF8=3C'.
- Objects: table 0x03003E90 (0x18 bytes, index = OAM index; +0x12 score on a kill (0x8000 flag on bosses), +0x14
  HP, the bullet-hit code 0x0801B8E6 subtracts damage), positions in 0x03005270 (16 bytes, x/y in 1/16 px). OAM 25
  = the player robot (32x32), 80-95 enemy robots, 96-111 their shadows. Score u16 0x03004EFC (5 per drone),
  added to money at the sortie report.
- **Teka report** (G12 labels: テカに関する報告 / タイホ! stamp / names / parts): drawn by the report state 4
  (0x080139C8 -> 0x08013A16) only when the arrest count u16 0x03003DFA (0x03003DF0+0xA) is non-zero: row i =
  Teka type u8 0x03003DFC+i (1-7; cell 9+type, type 0 would show cell 9 = "Fail") and part u8 0x03003E04+i
  (0 Body, 1 R.Arm, 2 L.Arm, 3 Pasocop; cell 0x11+part); more than 5 rows add the Up/Dn arrows (cells 0x15/0x16).
  Reach it without an arrest: warp battle01 with WIN=1 and freeze.lua FREEZE='3003DFA=0007 3003DFC=04030201
  3003E00=00070605 3003E04=03020100 3003E08=00020100', then A on the sortie report (~f3500).
- Probes: `watchw.lua` (writes + PC), `oamlog.lua`, `objlog.lua`, `objwatch.lua`, `autofight.lua` (OAM-steered
  bot; kills drones but never reached an arrest in battle01).

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
