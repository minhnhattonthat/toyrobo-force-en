# Text: encoding, layout, pointers

ROM: 4 MiB (0x400000), game code ATRJ, save type SRAM (`SRAM_V112` at 0x3674E8). Data ends at 0x3FF2AB; 0x3FF2AC-0x3FFFFF
is 0xFF/0x00 fill (candidate only, untested). Expanding past 4 MiB (to 8/16 MiB) is the clean free-space option: SRAM
saves are unaffected by ROM size and the patch stays BPS (<=16 MiB).

## Encoding (verified: decoded known on-screen strings, e.g. the title-menu help line 「さいしょから遊ぶか…」 at 0x249620)
- Plain **Shift-JIS (cp932)**, full-width only. No half-width katakana or ASCII letters in dialogue; ASCII is used only
  for control codes. `tools/sjis_scan.py` maps every run (11374 runs >= 3 chars incl. false hits in graphics/code;
  `work/re/runs.tsv`).
- Whether the draw routine accepts single-byte ASCII glyphs is **unknown** (phase 5 engine spike: hook the draw call).

## Dialogue: fixed 128-byte slots (verified by layout; reader verified by disassembly)
- Array base `0x08397070`, slot k at `0x397070 + k*0x80`, 2927 slots up to 0x3F27F0 (slot 0 at 0x397070 is used;
  first slot with a leading zero byte boundary is 0x3970F0). Every slot is NUL-padded; longest text is 126 bytes.
- Reader (verified, disasm): script opcode handler at `0x0800A424`: `ldrh r3,[r4,#8]; lsls r3,#7; ldr r4,=0x08397070;
  adds r3,r4; bl 0x0800ADD4`. The literal `0x08397070` is the only reference in the ROM (file 0xA438), so the slot size
  (the `lsls #7` at 0xA42C) and the base can be changed in one place to relocate the whole script to wider slots in
  expanded ROM (e.g. 256-byte slots: `lsls #8`). Script opcodes are records read through r4 (u16 fields).
- Control codes (counts over all slots; ASCII inside SJIS text):
  | code | count | meaning (guess, to verify in phase 5) |
  |---|---|---|
  | `#0` | 1806 | line break |
  | `#4` | 2831 | end of message / wait for key (96 slots end without it: likely continued or choice prompts) |
  | `#5nn` (3 digits) | 2606 | speaker / name tag id, before the speaker name, e.g. `#510スミタ警…` |
  | `#2nnnnn` (6 digits) | 2959 | portrait / face / position params, often two in a row at message start |
  Speaker names are written inline in the text (`ユウキ「…」`), not looked up.
- Text uses full-width spaces (　) for indentation of continuation lines.

## Other text tables (layout read from hex; pointer owners not yet traced except where noted)
| range | content | layout |
|---|---|---|
| 0x393560-0x3970F0 | robot names (ブランク, ポリステカ…), items (虫よけピストル…), parts | fixed-width records, NUL-padded names + u16 stats; referenced from code via literals 0x08393560, 0x08393600, 0x08393AE0, 0x08393D40… (316 literals into 0x0839xxxx-0x083Fxxxx, `disasm.py xref`) |
| 0x3766BC-0x37C888 | choice menus (「おーけー。行こう」「ちょっと待って」…) | 0x24-byte entries: 26-byte NUL-padded text, u16 target, u16 3, ... ; groups headed by script records (`04 00 6a 00 …`) |
| 0x248D44-0x2496C4 | ending report, staff credits, cast, robot status screen labels (ライフ：, 右腕名：…), part effects, save/load prompts | NUL-terminated strings, 4-byte aligned; pointer tables to find (phase 4) |
| 0x3F7592-0x3F7889 | robot swap prompts (だれを使う？…), link-cable battle messages | fixed-width full-width-space-padded strings with a pointer table right after (`0x083F75xx` words) |
| 0x3F27F0 / 0x3F2980 | 20-byte records read by opcodes at 0xA4E4 / 0xA4A0 | not text (layout data) |

## Choice / opcode table
Opcode jump table at ~0x0800A3D0 (Thumb `adr` words decode as data). Other text-bearing opcodes to identify in phase 4
by xref of the literals above.

## Extract (phase 4, verified by `tests/test_extract.py`)
- Tokens: `#0` {br}, `#4` {wait}, `#5NN` {spk:NN} (always 2 digits: 00 01 02 03 04 09 10 14 15 16), `#2NNNNN`
  {face:NNNNN} (always 5 digits). Only these four `#` codes occur. `%d`/`%s`/`%02d` printf formats in descs and the
  status/save strings stay literal. No `[ ] { }` in the ROM's text; every text row decodes with no `[XX]` escape.
- Dialogue: every one of the 2927 slots is shown by exactly one msg record (`where` = `rec:N`); files split by the
  section (opcode 40) the record sits in.
- String regions: every string start is reached by a pointer word (`where` = `ref:` offsets; most are Thumb literal
  pools, so moving a string means rewriting those words). Found while tracing: 0x249260-0x249298 is a table of 14
  Thumb function pointers (`0x08002785`, `0x080126D1` x13), and the status label `ライフ：` starts at 0x249298 (pointer
  at 0x8DE4); 0x2494C8 is pointed at too (by 0xB3C8), i.e. the NUL ending `#0スピードがあがる` doubles as an empty
  string: keep a NUL there or repoint 0xB3C8 when that string moves. Credits are drawn piece by piece (single
  kana/kanji strings such as `ゲ` `｜` `ム`, each with its own literal), so the credits redo is code + layout work.
- Prompt area 0x3F7592-0x3F788C: 12 swap prompts (pointer table 0x3F76A4, read by 0x1EA18/0x1F214), byte tables at
  0x3F768E-0x3F76A4 and 0x3F76D4-0x3F7704 (not text), 10 link prompts (pointer table 0x3F788C). Prompts are padded
  to fixed width with full-width spaces.
- Data rows (`kind` data, never translated): 0x2492E7 (bytes read at 0x95C4), 0x2494DC (a debug "乱数テーブル" random
  table interleaved with test text), 0x24956C `toyroboforce` (save signature).
- Coverage: outside the owned ranges, the only Japanese-looking runs are tile-map / palette words (waived ranges in
  `tests/test_extract.py`).
