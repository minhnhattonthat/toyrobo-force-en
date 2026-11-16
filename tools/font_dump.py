"""font_dump.py: list or render the game's 12x12 dialogue font (docs/re/font.md).

    python -X utf8 tools/font_dump.py list            # index, SJIS code, character
    python -X utf8 tools/font_dump.py png OUT.png     # all glyphs on a sheet (32 per row, 2x zoom)

The font is 848 entries of 26 bytes at 0x3F9594: u16 big-endian SJIS code, then 12 rows of u16 big-endian bits
(bit 15 = leftmost pixel), sorted by code; 0x0800FC30 binary-searches it.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"
FONT = 0x3F9594
COUNT = 0x350
SIZE = 26


def glyphs(rom):
    for i in range(COUNT):
        e = rom[FONT + i * SIZE: FONT + (i + 1) * SIZE]
        code = e[0] << 8 | e[1]
        rows = [e[2 + r * 2] << 8 | e[3 + r * 2] for r in range(12)]
        yield i, code, rows


def char(code):
    try:
        return bytes([code >> 8, code & 0xFF]).decode("cp932")
    except UnicodeDecodeError:
        return "?"


def main():
    rom = ROM.read_bytes()
    if sys.argv[1] == "list":
        for i, code, rows in glyphs(rom):
            print(f"{i:4d} {code:04X} {char(code)}")
    else:
        from PIL import Image
        img = Image.new("L", (32 * 14 * 2, (COUNT // 32 + 1) * 14 * 2), 255)
        for i, code, rows in glyphs(rom):
            ox, oy = (i % 32) * 14, (i // 32) * 14
            for y, bits in enumerate(rows):
                for x in range(16):
                    if bits >> (15 - x) & 1:
                        for dx in range(2):
                            for dy in range(2):
                                img.putpixel(((ox + x) * 2 + dx, (oy + y) * 2 + dy), 0)
        img.save(sys.argv[2])


if __name__ == "__main__":
    main()
