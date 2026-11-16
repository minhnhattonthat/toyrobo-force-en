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
| compression | BIOS LZ77 only, 36 blocks (`tools/gbacomp.py scan`; codec copied from a sibling GBA repo, roundtrip test still to add in phase 3) | verified decompression of all 36 |

Prior work: no earlier fan translation or community tools found (web search 2026-11-17).
Tools: `tools/sjis_scan.py` (SJIS run/cluster map), `tools/gfx_sweep.py` + `tools/gbacomp.py` (static sweep, LZ77).
