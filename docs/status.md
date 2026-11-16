# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 9. Release: next (phase 8 done-when met on build e3c66762, reproducible: smoke ok, visual-QA gate
  `qa_gate.py check work/qa/manifest.tsv work/qa/verdicts` 114/114 exit 0, `cover.py report` 3717/3722 + 5 waived
  exit 0, inkbox ok, every graphics row G1-G17 English in game, `tools/check.py` 0 problems).
- **Latest session (build sha1 e3c66762, unchanged):** G12 seen in game, phase 8 closed.
  Battle RE (`docs/re/script.md` §Battle): the battle01 "loss at ~f2150" was the **time limit** (timer u32
  0x03003C98 vs table 0x08249750), not life; robot HP u8 0x03005A80+16*[0x03005C78]+2 with the hit-invulnerability
  timer 0x03003DF8. God mode: `freeze.lua` FREEZE='3003C98=00000000 3003DF8=3C'. The **Teka report** page is drawn
  after the sortie report when the arrest count u16 0x03003DFA > 0 (types 0x03003DFC+i, parts 0x03003E04+i), so it
  was forced with freeze pokes on a WIN=1 battle01 warp (recipe in script.md). Shots `work/qa/g12_teka_report_a.png`
  / `_b.png` (zooms `work/qa/g12rep4/zoom.png`, `work/qa/g12rep5/zoom.png`): Bust! stamp, Teka Report, Names/Parts,
  all 7 Teka names, Body/R.Arm/L.Arm/Pasocop, Up/Dn arrows, all English, inside their cells; read-only visual pass
  by me: ok. A real arrest was not achieved: `tools/debug/autofight.lua` (OAM-steered bot, god mode) clears drones
  but did not reach the culprit in battle01. New probes: `watchw.lua` (writes + PC), `oamlog.lua`, `objlog.lua`,
  `objwatch.lua`.
- **Phase 9 to-do** (skill phase table; `references/pipeline.md` §Release):
  1. Story-pass verdict per chapter (`qa_gate.py check work/qa/story/manifest.tsv ...`, `references/translation.md`
     §Review); no nested workers in Orca: a fresh read-only pass yourself or `codex exec` (D11, `tools/review.sh`).
  2. `docs/polish.md`: tick or fix every line (review Minors). Phase 7 review Minors 4-7 still open: keep_jp list,
     harden `test_relocated_strings`, the "12: 05" / "3x 2" half cells on the load screen and part detail, a
     `--known` file for the `jp_left.py` scan.
  3. `tools/release.py`: runs `qa_gate.py check` on every manifest + `textcover.py`; `jp_left.py` on the release
     build (no unintended Japanese); debug tool off in the release build; patch built, re-applied, verified;
     README (repo + zip) without placeholders and with the base ROM hashes; zip = patch + README. Never
     `gh release create`.
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
  - Phase 8: all graphics rows G1-G17 redrawn and seen in game (`docs/re/graphics.md`), part-detail/factory/save
    fixes, text coverage (`tools/debug/cover.py`, waivers `docs/text_unshown.tsv`), full tour `work/qa/tour_en`
    103 scenes + sheets, visual-QA verdicts `work/qa/verdicts/`, G12 Teka report forced and shot.
- **Next:** phase 9 (above). Any `ref:` string can now grow: give it the English, the build relocates it (lint
  caps it by screen width in `windows.RELOC_CAP`). Link/swap prompts are fixed width (build pads with spaces).
  Text inside LZ blocks and all G-rows are graphics (phase 8). Emulator runs: never build while one is open; one
  `ending` run stopped at f4620 (exit 1, cause unknown) and the rerun was clean, so rerun once before debugging.
- **Debug tool limits:** mid-section warps keep the previous screen's tiles until the script loads a map (choice
  boxes show over black); facility1-5 all show the same workshop menu; battle god mode via `freeze.lua` (above;
  WIN=1 covers battle end screens); the two-player battle itself needs a link partner (only its menu is reached).
- **Open bugs:** none.
- **Waiting on the user:** nothing.
