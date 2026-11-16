# Font, text drawing and the English engine (phase 5)

## How the game draws text (verified by disassembly and the marker build)
- **Per character:** `0x080109CC(ptr, x0, ...)`, 14 callers (dialogue `0x0800B26A`, menus, choices...). A byte
  0x30-0x39 is an ASCII digit: drawn as full-width ０-９ (0x824F+), 1 byte consumed. Anything else is a 2-byte SJIS
  code. 0x8140 (full-width space) is skipped (advance only). It returns the bytes consumed; the cell counter
  (struct 0x03000850 + 0x1F08) advances by one per character.
- **Position:** cell n is 12 px (1.5 tiles) wide; even cells start on a tile, odd cells half-way into one. Dialogue
  lines are 20 cells; `#0` {br} rounds the counter up to the next multiple of 20, so a {br} after a full line
  makes a blank line (the engine encoder never emits one there).
- **Lookup:** `0x0800FC30(code)` binary-searches the font table at **0x3F9594**: 848 entries of 26 bytes (u16 BE
  code, then 12 rows of u16 BE bits, bit 15 = leftmost px, 12 px used), sorted; the last entry is a 0000 stub. The
  search bound is the literal 0x34F at 0xFC3C, the base the literal at 0xFC78; glyph data = 0x083F9596 + index*26
  (literals at 0x10948, 0x1EA1C, 0x1F218, 0x21DC8). The table holds 847 glyphs: kana, kanji, full-width digits and
  a few full-width capitals; no ASCII.
- **Render:** `0x08010890` queues (glyph ptr, VRAM tile 0x06004000 + n*32, parity, stride, colour) at struct
  +0x2794 (12-byte entries, count at +0x2848); `0x08011DD8` expands the 1bpp rows to 4bpp, writing 8 px with `str`
  and the 4-px half with `strh`, so neighbouring cells never clobber each other. Rows start at pixel row 2 of a
  tile row and run on into the next one (12 rows). No shadow: ink colour or paper colour per pixel.
- **Message buffer:** the msg opcode copies the slot into 0x030026C0 (strcpy at 0x0800B1A8); the next field is at
  +0x96, so a message is at most **149 bytes** + NUL, whatever the slot size.

## The English engine (tools/engine.py, tools/font_en.py)
- **Digraph font** (decided 2026-11-17): two 5-px letters per 12-px cell (left letter px 1-5, right px 7-11, rows
  1-9), 6 px per letter, 40 letters per dialogue line. Chosen over a VWF because it needs no change to the
  renderer, the position maths or any of the 14 callers: every text routine already draws 12-px cells from the same
  table. Letter glyphs are our own 5x9 design (`tools/font_en.py`; caps 7 rows, descenders 2).
- **Codes:** the build collects every letter pair the English uses and numbers them from 0xE040 (lead 0xE0-0xFC,
  trail 0x40-0xFC minus 0x7F: valid SJIS lead bytes, never a digit, '#' or NUL); room for 5452 pairs. A pair of
  spaces is 0x8140. One byte per letter: a field of N bytes holds N letters (the jp held N/2 characters).
- **ROM:** expanded to 8 MiB. New font table (847 original glyphs + pair glyphs, sorted) at 0x4B7000; the five
  literals above and the search bound point at it. Dialogue moved to 2927 x 256-byte slots at 0x400000 (`lsls
  r3,r3,#7` -> `#8` at 0xA42C, literal 0x08397070 at 0xA438 -> 0x08400000); the old slots stay untouched.
- Tokens and printf formats (%d %s %02d) pass through as the game's bytes; an odd letter run gets a trailing space
  so every token starts on a cell. Runtime digits (%d) are full-width (12 px each).
- `build.py --marker` -> `build/toyrobo_force_marker.gba` (every text row as `[id]` + filler, tools/marker.py);
  `build.py --marker wide` fills every field to its byte limit (`_wide.gba`); `build.py --qa ID=TEXT --out F`
  overrides single rows for stress tests.

## Marker build results (2026-11-17, all 98 warp scenes, `work/qa/marker/finals*.png`)
- Every font-drawn box shows its `[id]`: dialogue, choices, save/load menu and prompts, factory info panel, part
  descriptions, title help, link prompts, credits/cast/staff. 98/98 scenes boot and warp.
- Still Japanese, and all **tiles** (no font lookup while they draw, `tools/debug/fontcalls.lua`): chapter cards
  G7/G17, map banners G6, title buttons G4, facility buttons G15, sortie report G14, battle balloons G10. Phase 8.
- Non-text rows stay out (`kind` data: 0x2492E7, 0x2494DC, 0x24956C save signature); saves still work.

## Width gate (tools/windows.py holds these for build.py and lint.py; proofs in docs/re/shots/)
| variant | rows | budget | how measured |
|---|---|---|---|
| dialogue | dlg:* | 40 letters x 3 lines, 149 bytes | marker: 3 full lines, last letter at px 238; no blank line after a full line |
| dialogue-box strings | strings:2495F0..249694 (help, save/load) | 40 x 3, room (`max`) | wide marker on the title: wraps at 40 |
| link/swap prompts | prompts:*, swap:* | the jp's byte length (fixed width, build pads) | marker: shown in the dialogue box |
| choices | choice:* | 24 letters | wide: 24 of 28 shown (choice, shop_buy) |
| robot names | names:* | 10 letters | wide: 10 of 12 shown in the info panel |
| part names | parts_a/b:* | 18 letters | wide: 18 of 20 shown |
| item names | items_a/b:* | 14 letters | wide: 14 of 16 shown |
| part descriptions | descs:* | 28 letters x 3 lines (84), lines padded with spaces | wide: window wraps every 14 cells |
| info-panel labels | strings:249298.. (`ライフ：%d`, part labels) | room (`max`, 2-8 bytes) | panel row is px 64-238 = 29 letters incl. values; growing a label needs string relocation + literal rewrite (phase 7) |
| save-menu rows | strings (`日誌%d`) | room (16) + slot digit | wide: box holds ~19 letters + digit, room binds first |
| credits / cast / staff | credits:* | room (`max`) per piece | pieces are code-placed, many 2-12 bytes; English credits need layout work (relocate + literal rewrite) |
- **Torture line** (all printable ASCII, double spaces, … ♪): `docs/re/shots/p5_torture.png`, every glyph right.
- Runtime numbers (%d) print full-width digits, 12 px each.
