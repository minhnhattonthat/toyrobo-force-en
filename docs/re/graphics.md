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

## Not yet toured (add rows when the debug tool reaches them; the static sweep above covers their tiles)
Robot status / parts screens (labels are SJIS text at 0x249298+), shop, save/load, link battle (ふたりでたいせん)
screens, every chapter card after 序, game over, ending report and staff roll (staff text is SJIS at 0x248D44+, so
probably font-drawn; confirm).
