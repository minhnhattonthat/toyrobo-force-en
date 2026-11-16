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
| G3 | title copyright lines | ©2001 Global A Entertainment; © 西川伸司 キャラクターデザイン | LZ block 0x2BB0A8 | todo (credit line: "Character Design © Shinji Nishikawa") |
| G4 | title-menu buttons | さいしょから / つづき / ふたりでたいせん | title-menu frame tiles raw at 0x2C7D6-0x2DFD7 (vramfind, verified raw match); the button lettering is among 97 tiles found nowhere raw -> compressed or composed at run time from the font (no SJIS copy of ふたりでたいせん exists) | todo |
| G5 | intro katakana logo トイロボフォース | トイロボフォース | raw ~0x0FE800-0x100800 (sweep, guess); also LZ 0x2BB0A8 | todo (no official English logo; D5 says translate since only the Latin title logo is official) |
| G6 | map location banner | 警察学校 (and every other map location) | framed banner on the town map, glyphs look like the 12px font: likely font-drawn; no spaced SJIS copy found | todo (confirm source in phase 5) |
| G7 | chapter card | 序　訓練 (one per chapter) | over the robot intro screen; likely font-drawn (訓練 exists in SJIS in slot text) | todo (confirm per chapter with the debug tool) |
| G8 | battle start/countdown | かまえ, GO, countdown digits | raw ~0x13C000 (かまえ), ~0x139800 (GO) | todo (かまえ) |
| G9 | battle HUD labels | LIFE, LV(?), Latin fragments | raw ~0x062800, ~0x0B9000, ~0x13E000 | ok (Latin) |
| G10 | battle-result speech balloons | どんなもんです♪ / むりはできませんし / すみません… / よーし。やったね♪ / しょうがないわね / ま、こんなもんだな / しょうがねえな | LZ block 0x2BC310 | todo |
| G11 | "PRESS SELECT" / interface fragments | Latin | raw ~0x0A5000 | ok |
| G12 | small Japanese labels near character / interface art | unreadable fragments | raw ~0x065000, ~0x0FC000, ~0x101800-0x103000, LZ 0x25C0B4 | todo: identify in the tour once the debug tool reaches the screens (status, shop, battle) |
| G13 | dialogue / choice / menu font | full font | raw ~0x0A7000-0x0B8800 and ~0x0D9000-0x0E1000 (two font sizes) | text (engine work in phase 5) |

| G14 | sortie report (battle end) | 出撃報告書, 任務, 完了 / 失敗(?), 成果, 以上, 評価 (+ rank letter) | warp `battle_win` / `battle_lose`; source not traced | todo |
| G15 | facility menu buttons | Ⓐメンテ Ⓑもどる Ⓡじょうほう, PRESS, zit (money unit) | warp `factory`, `facility1-5` (all show the same workshop menu) | todo (PRESS/zit Latin: ok) |
| G16 | save prompt label | SELECT tag over セーブする/セーブしない | warp `save_confirm` | ok (Latin); the menu text is font |
| G17 | chapter card subtitle | 第二話　ぼうそう幼稚園 (one per section, 24) + katakana logo G5 | warp `sec00`-`sec23`; card text looks font-drawn | todo (confirm source in phase 5) |

## Toured with the debug tool (phase 2; proof sheets `work/qa/warp_all/finals*.png`)
Every section card (sec00-sec23), title menu / Continue (load: 日誌1-4 きろくなし) / two-player menu, save screen and
prompt, location selector banner (工場, ゲート...), factory menu and robot info panel (ライフ：右：左：コプ：OP：,
font text from 0x249298+), choice boxes, all 36 battle ids, win and loss sortie reports, the ending report, cast and
staff roll (font text over black, from 0x248D44+), post-game map. No separate game-over screen seen: a lost
battle shows the loss report, then branches to its lose record (retry script; every op 23 has one). Not yet looked at closely: two-player battle itself (needs a link partner).
