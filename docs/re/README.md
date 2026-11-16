# Reverse-engineering notes

One file per subsystem (text engine, pointers, compression, font, graphics). Mark every finding with how far it is
proven, so a later session doesn't build on a guess:

- **verified** - and how: a decoded known string, a corrupt-and-boot test, a breakpoint hit on the drawing path, a
  passing roundtrip test. Name the test or savestate.
- **guess** - and why it seems likely (byte pattern, another game, an earlier patch's notes). Promote it to verified
  before code depends on it.

Addresses are for the dump in `rom.sha1` unless a note says otherwise.

| File | Covers | State |
|---|---|---|
| text.md | ROM header/size/save, Shift-JIS encoding, 128-byte dialogue slots and their reader, control codes, other text tables, free space | encoding + slot reader verified; control-code meanings and table owners guessed |
| graphics.md | graphics-text survey (tour + static sweep), G1-G13 | sources partly verified (vramfind), rest guessed |
| script.md | event script (5538 x 12-byte records at 0x3831C8), opcodes, game struct 0x03000850, battle win/loss handlers, debug warp | interpreter, index, sections, battles, gosub/goto verified; most opcode meanings guessed |
| compression | BIOS LZ77 only, 36 blocks (`tools/gbacomp.py scan`, offsets pinned in `tools/units.py`). Our greedy compressor reproduces the game's bytes on 28 of 36; the build keeps original bytes for unchanged blocks | verified: `tests/test_gbacomp.py` roundtrips all 36, no displacement 1 |
| identity build | `tools/units.py`: script records, name/part/item/desc record tables (0x393560-0x397070: 20/32/32/24/24/88-byte records, text fields 14/22/22/18/20/88), dialogue slots, choices (696 x 0x24 records 0x3766BC-0x37C89C, text field 30; 299 non-text records kept raw), credits 0x248D44-0x249260 + strings 0x249298-0x2496C8 (0x249260-0x249298 = 14 Thumb function pointers, not owned), swap prompts 0x3F7592-0x3F768E + their 12-pointer table at 0x3F76A4, link prompts 0x3F7704-0x3F788C + their 10-pointer table at 0x3F788C (byte tables between them not owned), 36 LZ blocks | verified: `build.py --identity` and `tests/test_identity.py` (every unit's bytes blanked, repacked, byte-identical) |
| font.md | text drawing (0x080109CC per char, 0x0800FC30 font search, 0x08011DD8 render), font table 0x3F9594, English digraph engine (`tools/engine.py`, `tools/font_en.py`), relocations, marker build results, width gate (`tools/windows.py`) | verified: disasm + marker tour (98 scenes) + `tests/test_engine.py` |
| extract | `tools/text.py` (codec, rows, insertion), `tools/extract.py` (dump; never clobbers `en`), `tbl/jp.tbl` (`tools/make_jp_tbl.py`), `script/*.tsv` (3722 text rows + 3 data rows), `tools/lint.py`. Details in text.md §Extract | verified: `tests/test_extract.py` (TSV == fresh dump, every jp encodes to its bytes, inserting every jp rebuilds the original ROM, every field has a row, no Japanese-looking run outside owned/waived ranges) |

Prior work: no earlier fan translation or community tools found (web search 2026-11-17).
Tools: `tools/sjis_scan.py` (SJIS run/cluster map), `tools/gfx_sweep.py` + `tools/gbacomp.py` (static sweep, LZ77).
