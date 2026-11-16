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
| G6 | map location banner | 警察学校 (and every other map location) | framed banner on the town map. **Tiles, not text** (verified phase 5, warp `map_location`). Source: 35 pre-drawn 128x32 OBJ images (two 64x32 sprites, 1D) + a 32-byte palette each, stride 0x820 from 0x0A6D84, in location-id order (`work/qa/p8g/banners*.png`) | **done**: `gfx.LOCATIONS_EN` (groups `loc00`-`loc34`, `gfx.sprite_grid`), white font_en on the navy fill; shot `work/qa/p8g2/zoom.png` |
| G7 | chapter card | 序　訓練 (one per chapter) | over the robot intro screen. **Tiles, not text** (verified phase 5: Japanese on all 24 section cards in the marker build, no font lookup while sec05's card draws; "第二章" exists nowhere as SJIS) | **done** with G17: OBJ strips, `tools/cards.py` (records, `show`), `gfx.apply_cards` |
| G8 | battle start/countdown | かまえ, GO, countdown digits | raw ~0x13C000 (かまえ), ~0x139800 (GO) | todo: the sheet at 0x139000+ (32 tiles wide, column start not found) holds 3/2/1/GO boxes (Latin) and two big banners かち (ink E, x 23-145) / まけ (ink B, x 152-255+), y 80-141, over a 9-index band y 112-135; no かまえ found. None of them shows in story battles (battle00 start, battle_win/lose shot every 25-30 frames): two-player link battle only, which the emulator can't reach |
| G9 | battle HUD labels | LIFE, LV(?), Latin fragments | raw ~0x062800, ~0x0B9000, ~0x13E000 | ok (Latin) |
| G10 | battle-result speech balloons | どんなもんです♪ / むりはできませんし / すみません… / よーし。やったね♪ / しょうがないわね / ま、こんなもんだな / しょうがねえな | LZ block 0x2BC310 (sheet 32 tiles wide of 80x64 balloons; rows Blank / Tomomi / Gilligan) | done: `gfx.BALLOONS_EN`, LZ group `balloon` (fits in place); shot `work/qa/g10_win/zoom.png` (warp `battle_win`, f3000) |
| G11 | "PRESS SELECT" / interface fragments | Latin | raw ~0x0A5000 | ok |
| G12 | small Japanese labels near character / interface art | unreadable fragments | raw ~0x065000 (= G15, done), ~0x0FC000-0x103000 (= the battle-UI sheet at 0x0FB16C: still Japanese there: タイホ!, 終了 (battle end?), robot type names マーケテカ ドメステカ ワークテカ ポリステカ ポリジエンヌ ソルジャー パンクテカ, テカに関する報告, パーツ, テカ名, 右腕 左腕 ボディ, コプ), LZ 0x25C0B4 | redrawn offline in group `report` (Bust!, Marketeka..Bankteka, Teka Report, End, R.Arm/L.Arm/Body/Pasocop, Parts/Names tabs; preview `work/qa/g12_prev_c.png`); **not yet seen in game**: the Teka report page and the stamp need arrests in a played battle (WIN=1 ends it with none) |
| G13 | dialogue / choice / menu font | full font | raw ~0x0A7000-0x0B8800 and ~0x0D9000-0x0E1000 (two font sizes) | text (engine work in phase 5) |

| G14 | sortie report (battle end) | 出撃報告書, 任務, 完了 / 失敗, 成果, 以上, 評価 (+ rank letter); loss report key panel 終了 / 上 / 下 | warp `battle_win` / `battle_lose`. Raw battle-UI sheet, 32 tiles wide aligned at 0x0FB16C (`work/qa/p8g/r_rep.png`; also holds G12's labels), shown through BG1/BG3 map cells | **done** (group `report`): Sortie Report / Task / Clear / Fail / Haul / Rank / End; Exit / Up / Dn (map cell budgets: see gfx.py comments). Shots `work/qa/p8g2/zoom.png`, `work/qa/p8g/lose_en_crop.png` |
| G15 | facility menu buttons | Ⓐメンテ Ⓑもどる Ⓡじょうほう, PRESS, zit (money unit) | warp `factory`, `facility1-5`. Raw tiles 0x064D14+ on BG1 (`tools/gfx_grid.py` maps the screen cells to ROM tiles) | **done** (grid group `factory`): Repair / Back / Info ("Maintenance" is 43 px for 40); shot `work/qa/p8g2/zoom.png` (factory + facility1) |
| G16 | save prompt label | SELECT tag over セーブする/セーブしない | warp `save_confirm` | ok (Latin); the menu text is font |
| G17 | chapter card subtitle | 第二話　ぼうそう幼稚園 (one per section, 24) + katakana logo G5 | warp `sec00`-`sec23`; **tiles, not text** (same evidence as G7). Card table: 24 records of 28 bytes at 0x37641C (bg ptrs, strip ptr, layout word = total tiles / label sprites / name sprites, label/name/logo x,y); each strip is raw 4bpp 32x16 OBJ sprites (1D) DMA'd to OBJ VRAM 0x14000, ink 15 outline 8 | **done**: `cards.CARDS_EN` ("Chapter N" / "Episode N" / "Prologue" + names), strips drawn in font_en at 0x580000, records repointed, name x pushed right of the wider label; strips `work/qa/g7/cards_en.png`, in game `work/qa/g7/en_cards_game*.png`. The katakana logo sprite (G5) on the card stays todo |

## Toured with the debug tool (phase 2; proof sheets `work/qa/warp_all/finals*.png`)
Every section card (sec00-sec23), title menu / Continue (load: 日誌1-4 きろくなし) / two-player menu, save screen and
prompt, location selector banner (工場, ゲート...), factory menu and robot info panel (ライフ：右：左：コプ：OP：,
font text from 0x249298+), choice boxes, all 36 battle ids, win and loss sortie reports, the ending report, cast and
staff roll (font text over black, from 0x248D44+), post-game map. No separate game-over screen seen: a lost
battle shows the loss report, then branches to its lose record (retry script; every op 23 has one). Not yet looked at closely: two-player battle itself (needs a link partner).
