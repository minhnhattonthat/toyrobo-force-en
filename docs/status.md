# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 8. QA in the emulator: in progress (build e3c66762; text coverage 3715/3722 + 5 waived, 2 left;
  visual-QA gate must be re-run (build changed since e43b2203); G12 in game still open).
- **Latest session (build sha1 e3c66762):** factory/save coverage + fixes.
  Fixed: part-detail window overflow ("%d-Shot Burst" made line 2 sixteen cells -> 4th line overwrote the window's
  blank tile, garbage over the whole box): "%d-Shot", "Maint. per Life: %d" (D13, `tests/test_partdet.py`,
  glossary メンテ also "maint."). Graphics leftovers found in game and redrawn (gfx.py): G15c `factory_sell`
  Ⓐはいきゃく -> "Sell" (4th workshop icon), G15d `sortie_remove`/`sortie_add`/`sortie_done` Ⓐはずす/くわえる/Ⓑおわる
  -> "Remove"/"Add"/"Done" (5th icon). Shots `work/qa/sell_en/zoom.png`, `work/qa/sortie_en`, `work/qa/sortie_add3`.
  RAM (docs/re/script.md should get these): parts counts struct+0x1D47 (8 bodies), +0x1D4F (39 right arms), +0x1D76
  (19 left), +0x1D89 (8 Pasocops), +0x1D91 (options), cap 99 (op 31 = 0x0800D21C); money u32 +0x1D0C (0x0300255C);
  save/load menu state +0x1F0E; factory keeper (desc variant) +0x1F0C; desc n = 0x393EF0 + (3*msg+keeper)*0x58;
  sprintf 0x08025F90; arm data right 0x393600 / left 0x393AE0 (0x20 each: power +0x16, ways +0x17, shots +0x18);
  SRAM log n at 0x0E000000 + n*0x640 (4 copies at +k*0x190, hours u16 +0x10, minutes +0x12).
  Coverage tools: `cover.py extra NAME -- <emu args>` (one warp run + probe -> `work/qa/cover/extra_NAME`);
  `tools/debug/descs.lua` (swaps every factory desc into sprintf by printf signature; `ONLY=`), 
  `tools/debug/savefail.lua` (state 2->3 "Cannot save", FROM=3 TO=4 "erased"). Runs done (all count in the report):
  extra_descs (factory, POKES counts=05 at 0x03002597-0x030025EA + money, icon moves), extra_descs_s (assemblies,
  scratch keys), extra_desc119, extra_parts, extra_save (save on field), extra_load (+ --sav work/states/saved_log1.sav),
  extra_load_qa (`work/states/saves_qa.sav`: logs at 0/5/12/123 h), extra_savefail, extra_erased, extra_ending_long
  (REC 4794, 32000 f), extra_attract (idle boot); play sessions `play_fac1`, `play_left` (`acc/log.txt`). Waivers
  `docs/text_unshown.tsv` (249334/249360 data-proven, 2494CC no #3 code, choice 176/177 = unused group 44).
  **Left:** credits:249250 "And" / 249258 "In": drawn by the mode-0 handler 0x08001FB4 (states 3 and 5 of jump table
  0x08001FDC, state = struct+0x1F0E; called from the main loop 0x0800065E while struct+0x1F0D == 0); not seen in the
  ending to f32000 nor in a 9000-frame idle boot. Next: watch writes to 0x0300275D/0x0300275E to find what enters
  mode 0 state 3 (maybe the post-credits "The End" sequence or the link-battle end), run it, or waive with proof.
  Then: rebuild is final for text -> re-run `cover.py sweep` + `tour` + the extras above on the final build (strings
  addresses come from it) -> `cover.py report` exit 0; full visual re-tour (`warp_all.py`, `tour_sheets.py`,
  `qa_gate.py init --build`, `tools/vqa.sh`), add the new screens (factory sell/sortie, part-detail windows, save
  rows) to the tour/sheets; G12 in game (arrest).
- **Session before (build unchanged, sha1 e43b2203):** text-coverage tooling, committed (28e148f).
  `build.py` now writes `build/strings.tsv` (`tools/strmap.py`: dlg slots, `@` table/choice records, `ref:`
  pointer words read from the built ROM so relocated strings follow; test `test_build.test_string_map`).
  `tools/debug/sweep.lua` (after warp.lua, REC=first target): runs every op 15 / op 21 record of a range in turn
  with A mashed (`OPS_LIST`, `THEN`/`THEN_POKES`/`AFTER` to chain into another scene). `tools/debug/cover.py
  sweep|tour|report` (14 chunks of 400 records, ~6 min at 4 jobs; tour = `warp_all.py --cover RANGES`; report =
  textcover.py with mask 0x1FFFFFF and `docs/text_unshown.tsv` once it exists). Results in `work/qa/cover/`
  (+ `extra_ending`: REC=4794 for 13000 frames): **all 2927 dialogue slots and 395/397 choices shown**, 0 STUCK.
  inkbox: title menu and link menu Start/Quit centred (exit 0; the JP link menu is itself 3 px off).
  **Never shown (260)**, by group, with what to do:
  1. descs 142, parts_a 37, parts_b 17, items_a 7, items_b 9 and the part-detail strings 0x2492CC-0x2494B4
     ("Body: %s" ... "Speed goes up", "+Fire/+Laser"): need a screen listing owned parts / a shop. New game owns
     no spares: the factory icons (assemble = 2nd icon, swap = 3rd) show empty slots (`work/qa/partdet*`).
     Op 31 (47 records, "give part") swept with `OPS_LIST='31'` ran in 47 frames: it likely only tests
     ownership and branches, not a give (unverified). Next: find the parts-inventory RAM (op 31 handler or the
     swap screen's reader; `disasm.py` on the part-detail builder 0x080096E8(type, id), called from
     0x0800483C..0x08004EEE) and poke it, or sweep op 30 (purchase prompt, 20 records) for the shop screens.
  2. names:1-7 (the teka types): the Teka report page = G12; same arrest blocker.
  3. Save/load: "Log %d  %d:%02d" x3, "Saved to the log.", "!! Cannot save.", "Your data's all loaded!", "Sorry,
     but Log %d has been erased...", 0x2494CC "００／００": one run that saves on the field (START, A), soft-resets
     and loads through Continue.
  4. choice:176/177 「おーけー。行こう」/「ちょっと待って」: no op 21 among all 199 that the sweep ran reads them:
     probably an orphan group; prove it (map choice ids to table records) and waive.
  5. credits:249250 "And", 249258 "In" (refs 0x002200 / 0x002300, a credits function the normal ending does not
     run; "The End of / Toyrobo Force / Produced by" are shown only after f8000, past `ending_last`'s hold:
     consider raising it). Find what calls those refs, or waive with the reason.
  Then: `docs/text_unshown.tsv` for proven-unreachable ids, `cover.py report` exit 0, G12 in game.
- **Session before (build sha1 e43b2203):** visual-QA issues 2 and 3 fixed. New `retile` group kind in `gfx.py`
  (a block of N raw tiles + its own BG map: the canvas is drawn from the map, re-tiled into unique tiles with flips
  folded and written in place with a new map; refuses > N tiles): G18 the six workshop signs `sign0-5`
  ("<Town>" / "Factory", `gfx.SIGNS_EN`; tiles + 13x4 map per town at 0x066DF4..), G18 Ⓐけってい -> "Confirm"
  (grid group `factory_ok`, missed by the first verdicts), G19 two-player menu はじめる/おわる -> "Start"/"Quit"
  (`link_menu`, 0x24A208 + map 0x24A608). Shots `work/qa/p8x/signs_en.png`, `work/qa/p8x/link_battle/final.png`.
  Full re-tour `work/qa/tour_en` 99/99, sheets by new `tools/tour_sheets.py`, `qa_gate.py init --build`, 4 codex
  chunks (`work/qa/verdicts/p8b_*.tsv`): 104/104 ok, check exit 0. Any rebuild needs the tour + sheets + init +
  todo + `tools/vqa.sh` on the changed chunks again.
  **Next:** text coverage (build writes `build/strings.tsv` id<TAB>address; tour with `textcover.lua` RANGES over
  the dialogue slots 0x400000+ / tables; plan scenes that run each section with A held, or waive with reasons),
  then part-detail strings (step 2), `inkbox.py` on any centred box (link menu Start/Quit and the title menu are
  centred), G12 in game.
- **Session before (build sha1 da023e2d):** G5 done: the katakana logo is on the title *sprites* (not the bitmap):
  `gfx.py` `logos` (erase + per-column band refill + bold slanted `LOGO_GLYPHS`) in `title_obj`, and new sprite
  groups (`sprites=[(ROM, w tiles, h tiles, x, y)]`, canvas `size`) for the section-card logo `card_logo` (raw 1D
  sprites at 0x0A58A4/0x0A60A4/0x0A64A4, flat band refill). Shots `work/qa/g5_title/zoom.png`, `work/qa/g5_card/z.png`.
  G8 done offline: sheet aligned at 0x139040 (32 tiles wide), group `g8` + `G8_EN` "WIN!"/"LOSE" (labels can take
  `keep=True` = draw without clearing); link battle only, preview `work/qa/g8_en_z.png`. G12: tried a scripted
  fight (KEYS mash in battle01): the robot goes down, no arrest; `tools/debug/ramsnap.lua` + `freeze.lua` added;
  0x03005B0E u16 is the HUD bottom number but holding it is not god mode (life still unknown).
  Tour `work/qa/tour_en` (99/99) and `work/qa/tour_jp` (original), per-scene `sheet.png` (frames from 1400; title
  menus from 0), `work/qa/manifest.tsv` (110 sheets, build a8c..9b9f2455), chunks `work/qa/chunks/`, verdicts by
  `tools/vqa.sh` (codex exec read-only; brief `docs/visual-qa-brief.md`) in `work/qa/verdicts/`. Issues:
  1. **fixed** (recheck_1.tsv): Continue help line "Which log shall we resume?" drew its 13th cell stale
     ("resumdd") -> "Resume from which log?"; the help lines seem to hold 12 cells (24 letters) per line: check the
     other HELP rows if one ever grows.
  2. **fixed** (G18): workshop name sign (upper right, "アプリコットの工場" etc., 6 towns) still Japanese on factory,
     factory_info, factory_maint, facility1-5 and their _info scenes (12 sheets). Find whether font text (marker
     build would show an id) or tiles (gba_layers/vramfind), then translate/redraw ("Apricot Factory" ...; town
     names in glossary / `LOCATIONS_EN`).
  3. **fixed** (G19): link_battle menu はじめる / おわる still Japanese (link_battle/sheet_2): same check (font or tiles).
  Choice boxes are left-aligned in the original too (`work/qa/inkbox_jp.png` vs `inkbox_a.png`): inkbox's centring
  test does not apply to them; still run inkbox on any centred box found.
  Then: rebuild -> re-run the whole tour (build changed since the manifest) -> sheets -> `qa_gate.py init ... --build`
  -> `todo` -> `tools/vqa.sh` on the changed chunks -> `qa_gate.py check` exit 0. Still open after that: text
  coverage (no `build/strings.tsv` yet: build must write id<TAB>address of every string, tour runs need
  `$SKILL/scripts/lua/probes/textcover.lua` with RANGES; most dialogue is unreachable by the 99-scene tour, so plan
  scenes that run each section with A held, or waive with reasons), part-detail strings (step 2 below), G12 in game.
- **Session before (build sha1 1bb4c0b1):** G10 balloons: LZ group `balloon` + `gfx.BALLOONS_EN` (7 lines, rows
  Blank / Tomomi / Gilligan, block fits in place), seen in game for Tomomi win and loss (`work/qa/g10_win/zoom.png`,
  `work/qa/g12l`). G12 labels added to group `report` (Bust! stamp, the 7 robot types, Teka Report, End,
  R.Arm/L.Arm/Body/Pasocop, Parts/Names tabs; offline preview `work/qa/g12_prev_c.png`); the sortie report still
  looks right in game (`work/qa/g12w/z.png`). Their screen (a Teka report page after arrests, and the stamp in
  battle) needs a played battle with an arrest: try a savestate after an arrest, or find the arrest count in RAM
  and poke it before WIN=1. G8: see `docs/re/graphics.md` (かち/まけ + 3/2/1/GO are link-battle only, not in story
  battles; sheet layout not decoded). Next: G5 logo, then G8 (decide: redraw offline WIN/LOSE or note it as
  unreachable), then the tour + verdicts (step 1 below).
- **Earlier session (graphics, build sha1 98ae6379):** `gfx.py` grid groups (rows of ROM tile offsets | HFLIP/VFLIP,
  `tile_writes` refuses a tile shown twice with two contents); `tools/gfx_grid.py DUMP --bg N --rect` prints the grid
  of a screen region from a ppudump (ROM offset per map cell, dup/shared notes, `--png`). Label tuples take a 7th
  dict (prop/outline/left). G15 factory buttons (Repair/Back/Info), G6 all 35 map banners (`LOCATIONS_EN`, 0x0A6D84
  stride 0x820), G14 sortie report + loss key panel (group `report` = battle-UI sheet at 0x0FB16C, 32 tiles wide).
  Proof shots `work/qa/p8g2/zoom.png`, `work/qa/p8g/lose_en_crop.png`. Flagged: loss panel 下 = "Dn" (only 1 tile
  under it); report labels Task/Haul/Rank (3-4 tile cells).
  Next: G10 balloons (LZ 0x2BC310: decompress, find each phrase's tiles, LZ group like `title_obj`, `LZ_MOVES` if it
  grows); G8 かまえ (battle start, raw ~0x13C000: warp battle00 early frames + dump); G12 = the rest of the
  battle-UI sheet (タイホ!, robot type names, テカに関する報告, パーツ, テカ名, 右腕/左腕/ボディ: find each screen);
  G5 katakana logo (title bitmap LZ 0x2B6460 + the card logo sprite).
- **Graphics done this session** (`docs/re/graphics.md` rows): G3 title credit line ("Character Design: Shinji
  Nishikawa", OBJ from LZ 0x2BB0A8: `gfx.py` LZ groups + `strips` + `OAM_PATCHES`, block moved to 0x500000 via
  `LZ_MOVES` / `units.LZBlocks.moves`); G7+G17 all 24 section cards (`tools/cards.py` list/show, `cards.CARDS_EN`,
  `gfx.apply_cards`: strips at 0x580000, records at 0x37641C repointed). `gfx.draw` has `prop` (proportional) and
  `outline`. Free space now used: 0x500000+ moved LZ blocks, 0x580000-0x590000 card strips.
  Leads for the rest: G5 katakana logo = title bitmap LZ 0x2B6460 (240x160 8bpp, letters ~x54-176 y46-57) + a logo
  sprite on every card; G10 balloons = LZ 0x2BC310 (literal at 0x15A9C, so `LZ_MOVES` works if it grows).
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
  0. Graphics first (every redraw changes the build, and the gate needs a tour of the final build): G5, G6, G8,
     G10, G12, G14, G15 in `docs/re/graphics.md`. Method that worked for G4: warp, ppudump, `gba_layers.py
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
