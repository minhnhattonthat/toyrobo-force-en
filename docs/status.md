# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (phase 7 review fixed; G4 title menu redrawn as the graphics pilot).
- **Phase 8 so far:** phase 7 review (`.harness/reviews/toyrobo-force-en-phase7.md`) Important 1-2 + Minor 3 fixed
  (8a46e91): alignment spaces in the Log/Power/Charge Cost/%d-Way rows + `lint.align_errors`; `engine._wrap` is
  balanced (greedy line count, narrowest width) + stub-line lint (0 stubs left, was 102); `check.py` runs the
  batch term check. Minors 4-7 still open (keep_jp list, harden `test_relocated_strings`, look at "12: 05" /
  "3x 2" half cells on the load screen and part detail, `--known` file for the phase 9 scan).
  Tour on the review-fix build (e8f9e47): `work/qa/tour_en`, 99/99 ok, not yet sheeted or reviewed.
  Graphics pipeline: `tools/gfx.py` (groups of raw 4bpp tiles, labels redrawn with the `font_en` letters, applied
  by build.py, logged, in the allowed ranges), `tools/gba_layers.py` (which BG/OBJ draws a rect from a ppudump),
  `tools/debug/dmalog.lua` (DMA3 sources: how G4 was traced; the game queues DMAs in RAM at 0x03000850+0x235C),
  `tools/lz_dump.py` (all LZ blocks for vramfind). Palettes for previews in `gfx/pal/`.
- **Phase 8 to-do** (`references/emulator-qa.md`, done-when in the skill's phase table):
  0. Graphics first (every redraw changes the build, and the gate needs a tour of the final build): G3, G5-G8,
     G10, G12, G14, G15, G17 in `docs/re/graphics.md`. Method that worked for G4: warp, ppudump, `gba_layers.py
     --rect` for the layer and tile ids, `dmalog.lua --var FROM/TO` around the screen's load for the ROM source,
     `gfx.py show` for fill/ink indices, add a group + labels, `gfx.py preview`, build `--out work/x.gba`, warp,
     zoom. Compressed sources (LZ blocks, e.g. G10 at 0x2BC310) need gfx.py to recompress through the LZ unit.
  1. Then re-run `tools/debug/warp_all.py build/... --out work/qa/tour_en`, per-scene sheets, `qa_gate.py init /
     todo`, visual-QA verdicts: no nested workers in Orca, so a fresh read-only pass yourself or `codex exec`
     (D11), and write the verdicts.
  2. Part-detail strings relocated in phase 7 ("Right Arm: %s", "Left Arm: %s", "%d-Shot Burst", "{br}Right/Left
     arm power +5", refs 0x97xx-0x9Axx): find the screen that shows them (a part's detail view in the factory or
     a shop; `factory_maint` only shows "It doesn't seem to need maintenance...") and confirm they fit.
  3. Graphics text (G1-G17 in `docs/re/graphics.md`, incl. the title menu, section cards, game over): redraw in
     English (`references/graphics.md`), zoomed cold-boot shot of each.
  4. `inkbox.py` on choice/centred boxes, `textcover.py` exit 0.
  No subagents in Orca runs: work in the main thread and hand back at ~150k context.
- **Done:**
  - Step 0: repo set up (rom.sha1 pinned, `tools/check.py` + pre-commit gate proven to reject a failing test, guard
    hook proven on the canary, own MesenCE 2.2.1 + GBA BIOS, boot route, AGENTS.md, decisions D1-D8).
  - Phase 1: `docs/re/text.md` (SJIS full-width text; 2927 dialogue slots of 128 bytes at 0x397070, read by the
    opcode at 0x0800A424 via the single literal 0x08397070 -> relocatable to wider slots in expanded ROM; control codes
    `#0 #4 #5nn #2nnnnn`; other tables: names/items 0x393560, choices 0x3766BC, credits/status 0x248D44, link
    prompts 0x3F7592). `docs/re/graphics.md` (G1-G17 from tour + full static sweep + debug-tool tour).
  - Phase 2: `docs/re/script.md` (event script = 5538 x 12-byte records at 0x3831C8; record index u16 at
    0x03002558; opcodes: msg 15, goto 19, choice 21, map 22, battle 23, gosub/return 34/35, facility 38, section 40,
    ending 41; battle win/loss handlers 0x080138C8 / 0x0801394C). `tools/debug/warp.lua` + `scenes.gba.txt` (98
    scenes: title menus, 24 section cards, map/save/location, factory + 5 facilities with info panels, choices, all 36
    battle ids, win/loss sortie reports via WIN=1/LOSE=1, ending report/cast/staff, post-game, rare opcodes).
    `tools/debug/warp_all.py` ran all 98 from a cold boot: 98/98 ok, proof sheets `work/qa/warp_all/finals*.png`
    read and checked. `tests/test_scenes.py` keeps every section and battle id in the scene list.
    `tools/script_dump.py` lists the script (with text) for phase 4.
  - Phase 3: `build.py` (`--identity`) + `tools/units.py` unpack/pack the script records, the 6 record tables at
    0x393560-0x397070, 2927 dialogue slots, 696 choice records, the 0x248D44 strings, the 0x3F788C pointer table +
    prompts and the 36 LZ77 blocks; pack blanks every owned byte first and the result is byte-identical
    (`tests/test_identity.py`, also: every unit's bytes needed, edits logged for `romdiff.py --writes`, overlong text
    refused, changed LZ block recompressed in place). `tests/test_gbacomp.py` roundtrips all 36 blocks; compress()
    now indexes 3-byte keys (check 28 s -> 3 s) with identical output.
  - Phase 4: `script/` TSVs (columns id kind where max jp en notes; `tools/text.py` documents them):
    `dialogue/s00-s23.tsv` (2927 slots, by script section, `where` = msg record), `tables.tsv` (225 names/parts/
    items/descs), `choices.tsv` (397 text records; 299 non-text ones stay raw in the unit), `strings.tsv` (credits,
    status/save strings, swap + link prompts, with the pointer-word offsets; 3 rows `kind` data). `tbl/jp.tbl`
    generated by `tools/make_jp_tbl.py` (cp932 + `{br} {wait} {spk:NN} {face:NNNNN}`). `tools/extract.py` (never
    clobbers `en`; `--check`), `build.py` inserts `en`, `tools/lint.py` (codes, blanks, data rows) runs in check.
    Units re-split: credits/strings around a 14-pointer function table, swap prompts + their 12-pointer table at
    0x3F76A4, link prompts. `tests/test_extract.py`: TSV == fresh dump, codec roundtrip of every field, inserting
    every jp rebuilds the original ROM, row count == fields, coverage scan clean (tile-map false hits waived).
  - Phase 5 (`docs/re/font.md`): text drawing traced (0x080109CC per char, 0x0800FC30 font search, 0x08011DD8
    render; 12x12 1bpp font of 847 glyphs at 0x3F9594, no ASCII). English **digraph** engine (D9): two 5-px letters
    per 12-px cell, pair glyphs generated at build time into a relocated font at 0x4B7000 (`tools/engine.py`,
    `tools/font_en.py`); ROM expanded to 8 MiB; dialogue moved to 256-byte slots at 0x400000 (149-byte limit from
    the 0x030026C0 message buffer). `build.py --marker [wide]`, `--qa ID=TEXT --out F`. Marker tour of all 98
    scenes ok (`work/qa/marker/finals*.png`): every font-drawn box shows its id; what stays Japanese is tiles
    (G4 G6 G7 G10 G14 G15 G17, proved with `tools/debug/fontcalls.lua`). Width gate in `tools/windows.py` (build
    wrap + lint caps/lines): dialogue 40x3, choices 24, names 10, parts 18, items 14, descs 28x3 padded, help 40x3;
    torture line ok (`docs/re/shots/`). `tests/test_engine.py`.
  - Phase 6 so far: `tools/batches.py` (skill asset adapted to the TSVs: check uses the build's wrap + lint, merge
    copies English to same-JP rows of the same box kind), `tools/tl_body.py`, glossary seeded (names Hepburn, cities
    and people after fruit/wine/cheese), `engine._width` (wrap no longer counts mid-line codes as letters).
  - Phase 6 end: ending report in English (`report` window in `tools/windows.py`: 36 letters x 8 lines; engine
    passes the raw `@` byte through and keeps a paragraph's leading spaces; shots `docs/re/shots/*_ending_report.png`).
    `docs/credits-en.md`, `docs/synopsis.md`, `docs/style-reference.md` (both drafted by `codex exec` from the
    whole script, spot-checked). Reviewer pass: `tools/pairs.py` -> `work/qa/review/sNN.txt`; 10 `codex exec`
    reviews (rep_A-J.md: 3 Critical, 59 Important, ~50 Minor) -> 142 rows fixed (batches b900-b902, merged
    --overwrite incl. same-JP copies); re-review of every changed row (rep_R2) -> 6 more fixes -> rep_R3 Approved.
    Remaining Minors in `docs/polish.md`. Glossary voices updated (Blank hesitant, Georg old-man register).
  - Phase 6 review fixes (`.harness/reviews/toyrobo-force-en-phase6.md`): Georg voice ruled restrained (D10), all
    135 of his rows re-read, 71 revised; 8 Blank rows; codex voice review with the style reference + synopsis
    (`docs/reviews/voice-blank-georg.md`: Approved, 3 Minors applied). Kanji honorifics 君/様 in the batch check
    (waiver: a row's notes "no honorific ..."). Translator brief + `docs/review-prompt.md` read lists and report
    format; `tools/review.sh` (codex reviews, D11); D12 short labels.
  - Phase 7: credits in English (`docs/credits-en.md` §How it was fitted): strings longer than their room are
    moved to `engine.NEW_STRINGS` (0x4E0000) with every pointer word rewritten (`windows.relocatable`, lint caps
    credits 22 / panel 29 letters); `{none}` = empty piece; `engine.CREDIT_POS` moves 10 pieces on the 18-cell
    grid (`tools/credits_pos.py`). Date template `００／００　` (SJIS row, `windows.SJIS`). D12 labels grown.
    Old dialogue slots cleared after the move. `tests/test_build.py`: romdiff clean, every write in an allowed
    range, relocated strings reached by every pointer word and by no stale one; build refuses a run that inserts
    fewer rows than have English. `jp_left.py --sjis --gba-ptrs` on the build: 0 Japanese runs. Only JP left on purpose: the ♪
    credits piece (a symbol) and graphics text (phase 8).
    Cast and staff checked in-game (`work/qa/end_en`, warp `ending`). Robot info panel fixed in-game
    (`work/qa/info_en`): labels had run into values ("RighAir Gun", "Opti:"); arm names moved to col 4, "Opt:",
    parts cap 14 (3 parts renamed, D12). Last build sha1 8d061f90, smoke ok.
- **Next:** phase 8 (above). Any `ref:` string can now grow: give it the English, the build relocates it (lint
  caps it by screen width in `windows.RELOC_CAP`). Link/swap prompts are fixed width (build pads with spaces).
  Text inside LZ blocks and all G-rows are graphics (phase 8). Emulator runs: never build while one is open; one
  `ending` run stopped at f4620 (exit 1, cause unknown) and the rerun was clean, so rerun once before debugging.
- **Debug tool limits:** mid-section warps keep the previous screen's tiles until the script loads a map (choice
  boxes show over black); facility1-5 all show the same workshop menu; no GOD mode (robot life address not found;
  WIN=1 covers battle end screens); the two-player battle itself needs a link partner (only its menu is reached).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
