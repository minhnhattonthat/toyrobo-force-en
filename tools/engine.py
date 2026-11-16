"""engine.py: the English text engine (docs/re/font.md): digraph font, English encoder, ROM patches.

The game draws every character into a 12x12 cell (12 px advance, 20 cells per dialogue line) from a sorted font
table that 0x0800FC30 binary-searches by SJIS code. English uses **digraphs**: each cell holds two 5-px letters
(6 px advance, 40 letters per line). The build collects every letter pair the English text uses, gives each a
2-byte code (lead 0xE0-0xFC, trail 0x40-0xFC minus 0x7F: valid SJIS, never an ASCII digit or '#'), and writes a
new font table (the original 847 glyphs + the pair glyphs) in expanded ROM. A pair of spaces is 0x8140, the
full-width space the game already skips. Bytes and letters are one to one: a field of N bytes holds N letters.

    enc = Encoder()
    items = enc.cells("Hello there!", wrap=40)   # pass 1, for every English row
    enc.assign()                                 # give codes to every pair seen
    raw = enc.encode(items)                      # pass 2
    patch(out, enc)                              # expanded ROM: relocated dialogue + font, literal rewrites

Control tokens ({br} {wait} {spk:NN} {face:NNNNN}) and printf formats (%d %s %02d) pass through as the game's
own bytes. Text between them is paired; an odd run gets a trailing space, so every token starts on a cell.
"""
import re
import struct

import font_en
import text as textmod

ROM_BASE = 0x08000000
ROM_SIZE = 0x800000          # 8 MiB: SRAM saves don't care, patch stays BPS (<= 16 MiB)

FONT = 0x3F9594              # original table: 848 x 26 bytes (u16 BE code, 12 x u16 BE rows); last is a 0000 stub
FONT_COUNT = 847
GLYPH = 26
NEW_DIALOGUE = 0x400000      # 2927 slots x 256 bytes
DIALOGUE_SLOT = 0x100
NEW_FONT = 0x4B7000
DIALOGUE_BUFFER = 150        # 0x030026C0..0x03002756: the opcode copies the slot here (strcpy at 0x0800B1A8)
LINE_CELLS = 20              # dialogue: {br} rounds the cell counter up to the next multiple of 20

# (file offset, original bytes, what) for every code word the patch rewrites
LIT_DIALOGUE_SHIFT = 0xA42C  # lsls r3,r3,#7 (slot * 128) in the msg opcode at 0x0800A424
LIT_DIALOGUE_BASE = 0xA438   # =0x08397070
LIT_FONT_HI = 0xFC3C         # =0x34F, last index of the binary search
LIT_FONT_BASE = 0xFC78       # =0x083F9594, entry base for the search
LIT_FONT_GLYPH = (0x10948, 0x1EA1C, 0x1F218, 0x21DC8)  # =0x083F9596, glyph data = base + 2 + index * 26

TOKEN = re.compile(r"\{(?:br|wait|spk:\d\d|face:\d{5})\}|%0?\d*[ds]")
SPACE_PAIR = 0x8140


def _codes():
    for lead in range(0xE0, 0xFD):
        for trail in range(0x40, 0xFD):
            if trail != 0x7F:
                yield lead << 8 | trail


MAX_PAIRS = sum(1 for _ in _codes())


def _wrap(words_text, width):
    """Greedy word wrap of one paragraph into lines of at most `width` letters."""
    lines, cur = [], ""
    for word in words_text.split(" "):
        cand = word if not cur else cur + " " + word
        if len(cand) <= width:
            cur = cand
        else:
            if cur:
                lines.append(cur)
            while len(word) > width:
                lines.append(word[:width])
                word = word[width:]
            cur = word
    lines.append(cur)
    return lines


class Encoder:
    def __init__(self):
        self.pairs = set()
        self.code = None

    def _run(self, s, items):
        if len(s) % 2:
            s += " "
        for i in range(0, len(s), 2):
            pair = s[i:i + 2]
            bad = [c for c in pair if c not in font_en.GLYPHS]
            if bad:
                raise ValueError(f"no glyph for {bad[0]!r}")
            items.append(pair)
            if pair != "  ":
                self.pairs.add(pair)

    def cells(self, text, wrap=None, pad=False):
        """Split English text into items: 2-letter str cells and raw bytes (tokens). `wrap` = letters per line:
        word-wrap every paragraph and emit {br} between lines, except after a full line (the game's own wrap
        takes it there; a {br} would add a blank line). pad: end short lines with spaces up to `wrap` instead of
        {br} (windows that wrap by cell count only, like the part descriptions)."""
        if wrap:
            paras = text.split("{br}")
            text = ""
            for i, p in enumerate(paras):
                lead = re.match(r"(?:\{(?:spk:\d\d|face:\d{5})\})*", p).group(0)
                tail = re.search(r"(?:\{wait\})*$", p[len(lead):]).group(0)
                lines = _wrap(p[len(lead):len(p) - len(tail)], wrap)
                text += lead
                for j, line in enumerate(lines):
                    line += " " * (len(line) % 2)  # whole cells, so the next line starts on a cell
                    text += line
                    last = i + 1 == len(paras) and j + 1 == len(lines)
                    if not last and len(line) < wrap:
                        text += " " * (wrap - len(line)) if pad else "{br}"
                text += tail
        items, pos = [], 0
        for m in TOKEN.finditer(text):
            if m.start() > pos:
                self._run(text[pos:m.start()], items)
            items.append(textmod.encode(m.group(0)) if m.group(0).startswith("{") else m.group(0).encode("ascii"))
            pos = m.end()
        if pos < len(text):
            self._run(text[pos:], items)
        return items

    def assign(self):
        if len(self.pairs) > MAX_PAIRS:
            raise ValueError(f"{len(self.pairs)} letter pairs, code space holds {MAX_PAIRS}")
        self.code = dict(zip(sorted(self.pairs), _codes()))

    def encode(self, items):
        out = bytearray()
        for it in items:
            if isinstance(it, bytes):
                out += it
            else:
                c = SPACE_PAIR if it == "  " else self.code[it]
                out += bytes([c >> 8, c & 0xFF])
        return bytes(out)

    def font_table(self, rom):
        """The new font: the original 847 entries (codes <= 0x9872) + one entry per pair, sorted by code."""
        orig = bytes(rom[FONT:FONT + FONT_COUNT * GLYPH])
        extra = bytearray()
        for pair, code in sorted(self.code.items(), key=lambda kv: kv[1]):
            left, right = (font_en.GLYPHS[c] for c in pair)
            rows = [0] * 12
            for r in range(font_en.HEIGHT):
                rows[1 + r] = left[r] << 11 | right[r] << 5
            extra += struct.pack(">H12H", code, *rows)
        return orig + bytes(extra), FONT_COUNT + len(self.code)


def _lit(out, off, old, new, who):
    cur = struct.unpack_from("<I", out.orig, off)[0]
    if cur != old:
        raise ValueError(f"{who}: word at {off:06X} is {cur:08X}, expected {old:08X} (wrong ROM?)")
    out.write(off, struct.pack("<I", new), who)


def expand(out):
    """Grow a units.Rom to 8 MiB of 0xFF (before the units pack: the dialogue goes to NEW_DIALOGUE)."""
    if len(out.data) < ROM_SIZE:
        out.write(len(out.data), b"\xff" * (ROM_SIZE - len(out.data)), "engine: expand to 8 MiB")


def patch(out, enc):
    """Engine patches on an expanded units.Rom: the new font table and its literals, the dialogue base and slot
    size (the dialogue unit itself is packed to NEW_DIALOGUE by build.py)."""
    table, count = enc.font_table(out.orig)
    if NEW_FONT + len(table) > ROM_SIZE:
        raise ValueError("font table runs past the ROM end")
    out.write(NEW_FONT, table, f"engine: font table ({count} glyphs)")
    _lit(out, LIT_FONT_HI, 0x34F, count - 1, "engine: font search hi")
    _lit(out, LIT_FONT_BASE, ROM_BASE + FONT, ROM_BASE + NEW_FONT, "engine: font base")
    for off in LIT_FONT_GLYPH:
        _lit(out, off, ROM_BASE + FONT + 2, ROM_BASE + NEW_FONT + 2, "engine: font glyph base")
    if out.orig[LIT_DIALOGUE_SHIFT:LIT_DIALOGUE_SHIFT + 2] != b"\xdb\x01":
        raise ValueError("engine: msg opcode is not lsls r3,r3,#7 at 0xA42C")
    out.write(LIT_DIALOGUE_SHIFT, b"\x1b\x02", "engine: dialogue slot 256 (lsls r3,r3,#8)")
    _lit(out, LIT_DIALOGUE_BASE, 0x08397070, ROM_BASE + NEW_DIALOGUE, "engine: dialogue base")
