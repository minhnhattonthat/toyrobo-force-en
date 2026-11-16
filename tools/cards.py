"""cards.py: the section cards (docs/re/graphics.md G7/G17): chapter label + section name, drawn as OBJ strips.

    python -X utf8 tools/cards.py list                 # every card record
    python -X utf8 tools/cards.py show OUT.png [--zoom 2] [--en]   # every card's strips (original, or as built)

Card records are 28 bytes at CARD_TABLE (pointed to from the section-start code): bg ptr A, bg ptr B, strip ptr,
layout word (byte 0 = total tiles, byte 1 = 0, byte 2 = label sprites, byte 3 = name sprites), then three
(x, y) halfword pairs: label, name, logo. The strip is raw 4bpp tiles in 1D OBJ order: label sprites then name
sprites, each sprite 32x16 = 8 tiles (row 0 tiles 0-3, row 1 tiles 4-7), copied to OBJ VRAM 0x14000.
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CARD_TABLE = 0x37641C
REC = 28
NEW_STRIPS = 0x580000  # English strips (tools/gfx.py apply_cards); 24 x <= 7 sprites x 256 bytes
NEW_STRIPS_END = 0x590000

# English per record (same order as the table = section order sec00-sec23), docs/re/graphics.md G7/G17.
# 第N章 "Chapter N" (a city), 第N話 "Episode N", 序 "Prologue". Names follow glossary.md.
CARDS_EN = [
    ("Chapter 1", "Apricot City"),
    ("Prologue", "Training"),
    ("Episode 1", "Is This Really a Drill?"),
    ("Episode 2", "Runaway Kindergarten"),
    ("Episode 3", "The Revolt Begins"),
    ("Chapter 2", "Framboise City"),
    ("Episode 4", "The Mayor Kidnapped"),
    ("Episode 5", "Rescue the Mayor"),
    ("Chapter 3", "Cassis City"),
    ("Episode 6", "The Army Runs Amok"),
    ("Episode 7", "I Hate the Army"),
    ("Chapter 4", "Lingonberry Capital"),
    ("Episode 8", "Raid on Lingonberry Police"),
    ("Episode 9", "Special Police"),
    ("Chapter 5", "Marmalade City"),
    ("Episode 10", "Tomomi, Marmalade's Chief"),
    ("Episode 11", "Citizens' Revolution"),
    ("Episode 12", "Don't Let Them Escape"),
    ("Chapter 6", "Blackberry Island"),
    ("Episode 13", "The Search"),
    ("Episode 14", "Deep in the Volcano"),
    ("Episode 15", "The Trap"),
    ("Episode 16", "The Carrier Argo"),
    ("Episode 17", "You Are Not Human"),
]
INK, OUTLINE = 15, 8  # white letters, dark outline, transparent ground (the band behind is other sprites)


def sprites_from_rows(rows):
    """16 rows of n*32 indices -> n sprites of 8 tiles (1D order) as bytes."""
    out = bytearray()
    for s in range(len(rows[0]) // 32):
        for t in range(8):
            tx, ty = s * 32 + t % 4 * 8, t // 4 * 8
            for y in range(8):
                for x in range(0, 8, 2):
                    out.append(rows[ty + y][tx + x] | rows[ty + y][tx + x + 1] << 4)
    return bytes(out)


def records(rom):
    out, off = [], CARD_TABLE
    while True:
        a, b, strip, lay, p1, p2, p3 = struct.unpack_from("<7I", rom, off)
        if not (0x08000000 <= a < 0x08400000 and 0x08000000 <= strip < 0x08800000) or len(out) == 24:
            break
        out.append(dict(off=off, strip=strip - 0x08000000, tiles=lay & 0xFF, label=lay >> 16 & 0xFF,
                        name=lay >> 24, lay=lay, label_xy=(p1 & 0xFFFF, p1 >> 16),
                        name_xy=(p2 & 0xFFFF, p2 >> 16), logo_xy=(p3 & 0xFFFF, p3 >> 16)))
        off += REC
    return out


def sprite_px(rom, at):
    """One 32x16 sprite (8 tiles, 1D) -> 16 rows of 32 palette indices."""
    px = [[0] * 32 for _ in range(16)]
    for t in range(8):
        tx, ty = t % 4 * 8, t // 4 * 8
        for y in range(8):
            for x in range(8):
                b = rom[at + t * 32 + y * 4 + x // 2]
                px[ty + y][tx + x] = b >> 4 if x & 1 else b & 15
    return px


def strip_px(rom, rec):
    """(label rows, name rows): each 16 rows wide label*32 / name*32."""
    sprites = [sprite_px(rom, rec["strip"] + i * 256) for i in range(rec["label"] + rec["name"])]
    join = lambda sps: [sum((s[y] for s in sps), []) for y in range(16)]  # noqa: E731
    return join(sprites[:rec["label"]]), join(sprites[rec["label"]:])


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("list", "show"))
    ap.add_argument("out", nargs="?")
    ap.add_argument("--zoom", type=int, default=2)
    ap.add_argument("--rom", default=str(ROOT / "rom" / "Toyrobo Force (Japan).gba"))
    a = ap.parse_args()
    rom = Path(a.rom).read_bytes()
    recs = records(rom)
    if a.cmd == "list":
        for i, r in enumerate(recs):
            print(f"{i:2d} {r['off']:06X} strip {r['strip']:06X} tiles {r['tiles']:3d} label {r['label']} "
                  f"name {r['name']} lay {r['lay']:08X} label@{r['label_xy']} name@{r['name_xy']} "
                  f"logo@{r['logo_xy']}")
        return
    from PIL import Image
    pal = {0: (40, 40, 60)}
    shade = lambda v: pal.get(v, (v * 16, v * 16, v * 16))  # noqa: E731
    img = Image.new("RGB", (8 + 64 + 8 + 192 + 8, len(recs) * 18 + 2), (90, 0, 90))
    for i, r in enumerate(recs):
        lab, name = strip_px(rom, r)
        for x0, rows in ((8, lab), (80, name)):
            for y, row in enumerate(rows):
                for x, v in enumerate(row):
                    img.putpixel((x0 + x, 2 + i * 18 + y), shade(v))
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
