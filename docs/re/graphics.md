# Graphics text survey (phase 1)

Sources: a cold-boot tour (`tools/routes/boot.txt` + A-mash to frame 9000: logos, title, title menu, intro, prologue
card, police HQ, map, first choice menu; `work/qa/tour1/`) and a static sweep of the whole ROM
(`tools/gfx_sweep.py raw 0x10000-0x393560` as linear gba4, 64 tiles/row, 15 sheets of 0x20000; `gfx_sweep.py lz` over
the 36 BIOS-LZ77 blocks `gbacomp.scan` finds; sheets read by a read-only codex reviewer, verdicts in
`work/sweep/review_*.md`). No region was skipped (index: `work/sweep/*/index.tsv`).

Status column: **todo** = Japanese, must be redrawn or re-sourced; **ok** = already English; **text** = drawn at run
time from the font by the text engine (handled by script work, not graphics).

| # | screen / element | Japanese | where (guess unless marked) | status |
|---|---|---|---|---|
| G1 | title logo | ToyroboForce (Latin) | LZ block 0x2BB0A8 (sweep) | ok (no change; D5) |
| G2 | title "PRESS START BUTTON!" | Latin | LZ block 0x2BB0A8 | ok |
| G3 | title copyright lines | ©2001 Global A Entertainment; © 西川伸司 キャラクターデザイン | OBJ sprites from LZ block 0x2BB0A8 (decompressed to OBJ VRAM 0x14000, 2D mapping, sheet 32 tiles wide); sprite records (attr0, attr1, attr2, 0) at 0x24A6E0+ relative to (128,128), line 2 = 5 records at 0x24A73C | **done**: `gfx.py` group `title_obj` draws "Character Design: Shinji Nishikawa" (proportional font_en, ink 14, outline 11) as three 64x32 sprites on blank sheet tiles 0x318/0x358/0x398 (`OAM_PATCHES`); block recompressed is 270 bytes larger, so it moves to 0x500000 (`LZ_MOVES`, literal at 0x1F874). Shot `work/qa/g3_en/zoom.png`. Line 1 is Latin already |
| G4 | title-menu buttons | さいしょから / つづき / ふたりでたいせん | the whole title screen (art, logo, buttons) is 352 raw 4bpp tiles at 0x2B6B8-0x2E2B8 in VRAM order, DMA'd to VRAM 0x8000 at f1033-1035 through the RAM DMA queue at 0x03000850+0x235C (`tools/debug/dmalog.lua`); BG1, 32 tiles wide, palettes 2 (normal) / 3 (selected) | **done** (phase 8 pilot): `tools/gfx.py` group `title`: "New Game" / "Continue" / "Two-Player Battle" in the font_en letters, fill 2 ink 3; cold-boot shot `work/qa/g4_en/zoom.png` |
| G5 | intro katakana logo トイロボフォース | トイロボフォース | title screen (before the menu) is BG2 mode 4: a 240x160 8bpp bitmap, LZ block 0x2B6460 (vramfind, work/qa/g3); the katakana sits at about x 54-176, y 46-57 over the pink pill and navy stripes. Plan: paste the official Latin logo (G1, title tile block 0x2B6B8) or redraw "TOYROBO FORCE" bold with a white outline; the background under the letters must be repainted (stripes) | todo (no official English logo; D5 says translate since only the Latin title logo is official) |
| G6 | map location banner | 警察学校 (and every other map location) | framed banner on the town map. **Tiles, not text** (verified phase 5: stays Japanese in the marker build and `tools/debug/fontcalls.lua` logs no font lookup while it draws, warp `map_location`); source tiles not traced | todo (redraw, phase 8) |
| G7 | chapter card | 序　訓練 (one per chapter) | over the robot intro screen. **Tiles, not text** (verified phase 5: Japanese on all 24 section cards in the marker build, no font lookup while sec05's card draws; "第二章" exists nowhere as SJIS) | todo (redraw, phase 8) |
| G8 | battle start/countdown | かまえ, GO, countdown digits | raw ~0x13C000 (かまえ), ~0x139800 (GO) | todo (かまえ) |
| G9 | battle HUD labels | LIFE, LV(?), Latin fragments | raw ~0x062800, ~0x0B9000, ~0x13E000 | ok (Latin) |
| G10 | battle-result speech balloons | どんなもんです♪ / むりはできませんし / すみません… / よーし。やったね♪ / しょうがないわね / ま、こんなもんだな / しょうがねえな | LZ block 0x2BC310 | todo |
| G11 | "PRESS SELECT" / interface fragments | Latin | raw ~0x0A5000 | ok |
| G12 | small Japanese labels near character / interface art | unreadable fragments | raw ~0x065000, ~0x0FC000, ~0x101800-0x103000, LZ 0x25C0B4 | todo: identify in the tour once the debug tool reaches the screens (status, shop, battle) |
| G13 | dialogue / choice / menu font | full font | raw ~0x0A7000-0x0B8800 and ~0x0D9000-0x0E1000 (two font sizes) | text (engine work in phase 5) |

| G14 | sortie report (battle end) | 出撃報告書, 任務, 完了 / 失敗(?), 成果, 以上, 評価 (+ rank letter) | warp `battle_win` / `battle_lose`; source not traced | todo |
| G15 | facility menu buttons | Ⓐメンテ Ⓑもどる Ⓡじょうほう, PRESS, zit (money unit) | warp `factory`, `facility1-5` (all show the same workshop menu) | todo (PRESS/zit Latin: ok) |
| G16 | save prompt label | SELECT tag over セーブする/セーブしない | warp `save_confirm` | ok (Latin); the menu text is font |
| G17 | chapter card subtitle | 第二話　ぼうそう幼稚園 (one per section, 24) + katakana logo G5 | warp `sec00`-`sec23`; **tiles, not text** (same evidence as G7) | todo (redraw, phase 8) |

## Toured with the debug tool (phase 2; proof sheets `work/qa/warp_all/finals*.png`)
Every section card (sec00-sec23), title menu / Continue (load: 日誌1-4 きろくなし) / two-player menu, save screen and
prompt, location selector banner (工場, ゲート...), factory menu and robot info panel (ライフ：右：左：コプ：OP：,
font text from 0x249298+), choice boxes, all 36 battle ids, win and loss sortie reports, the ending report, cast and
staff roll (font text over black, from 0x248D44+), post-game map. No separate game-over screen seen: a lost
battle shows the loss report, then branches to its lose record (retry script; every op 23 has one). Not yet looked at closely: two-player battle itself (needs a link partner).
