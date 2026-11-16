"""gfx_grid.py: turn a screen region of a BG layer (from a ppudump) into a gfx.py grid of ROM tile offsets.

    python -X utf8 tools/gfx_grid.py work/qa/x/ppu_002100 --bg 1 --rect x,y,w,h [--png out.png]

The rect is in screen pixels; it is widened to whole map cells (fine scroll included). For every cell the tool
finds the VRAM tile's 32 bytes raw in the ROM (unflipped, as stored) and prints a `grid=` literal for
tools/gfx.py: each cell is the ROM offset (| gfx.HFLIP / gfx.VFLIP as the map entry flips it), or None for a
tile found nowhere or tile 0. Then per cell: how many ROM copies the tile has (`dup`) and how often the same tile
id is used by the enabled BG maps outside the rect (`shared`): a redraw must not touch a shared tile, or another
part of the screen changes with it. --png renders the grid as the screen shows it (zoom 4) with the BG palette.
"""
import argparse
import struct
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"
HFLIP, VFLIP = 1 << 28, 1 << 29


def bg_info(io, bg):
    cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
    hofs, vofs = struct.unpack_from("<HH", io, 0x10 + 4 * bg)
    return dict(char=(cnt >> 2 & 3) * 0x4000, map=(cnt >> 8 & 31) * 0x800, size=cnt >> 14,
                hofs=hofs & 511, vofs=vofs & 511)


def entry(vram, b, mx, my):
    mx, my = mx % (64 if b["size"] in (1, 3) else 32), my % (64 if b["size"] >= 2 else 32)
    blk = (mx // 32) + (my // 32) * (2 if b["size"] == 3 else 1)
    return struct.unpack_from("<H", vram, b["map"] + blk * 0x800 + ((my % 32) * 32 + mx % 32) * 2)[0]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prefix")
    ap.add_argument("--bg", type=int, required=True)
    ap.add_argument("--rect", required=True)
    ap.add_argument("--png")
    a = ap.parse_args()
    io = Path(a.prefix + ".io.bin").read_bytes()
    vram = Path(a.prefix + ".vram.bin").read_bytes()
    pal = Path(a.prefix + ".pal.bin").read_bytes()
    rom = ROM.read_bytes()
    disp = struct.unpack_from("<H", io, 0)[0]
    b = bg_info(io, a.bg)
    rx, ry, rw, rh = map(int, a.rect.split(","))
    x0, y0 = (rx + b["hofs"]) // 8, (ry + b["vofs"]) // 8
    x1, y1 = (rx + rw - 1 + b["hofs"]) // 8, (ry + rh - 1 + b["vofs"]) // 8
    cells = {(mx, my) for my in range(y0, y1 + 1) for mx in range(x0, x1 + 1)}
    uses = {}
    for bg in range(4):
        if not disp >> (8 + bg) & 1:
            continue
        o = bg_info(io, bg)
        if o["char"] != b["char"]:
            continue
        for my in range(o["vofs"] // 8, o["vofs"] // 8 + 21):
            for mx in range(o["hofs"] // 8, o["hofs"] // 8 + 31):
                if bg == a.bg and (mx, my) in cells:
                    continue
                t = entry(vram, o, mx, my) & 0x3FF
                uses[t] = uses.get(t, 0) + 1
    grid, notes, pals = [], [], set()
    for my in range(y0, y1 + 1):
        row = []
        for mx in range(x0, x1 + 1):
            e = entry(vram, b, mx, my)
            t = e & 0x3FF
            pals.add(e >> 12)
            data = vram[b["char"] + t * 32:b["char"] + t * 32 + 32]
            hits, i = [], rom.find(data)
            while i >= 0 and len(hits) < 9:
                hits.append(i)
                i = rom.find(data, i + 1)
            if t == 0 or not hits or not any(data):
                row.append(None)
                continue
            row.append(hits[0] | (HFLIP if e & 0x400 else 0) | (VFLIP if e & 0x800 else 0))
            if len(hits) > 1 or uses.get(t):
                notes.append(f"cell ({mx - x0},{my - y0}) tile {t:03X} @{hits[0]:06X} dup {len(hits) - 1} "
                             f"shared {uses.get(t, 0)}")
        grid.append(row)
    print(f"# BG{a.bg} map cells x {x0}-{x1} y {y0}-{y1}, screen origin ({x0 * 8 - b['hofs']},"
          f"{y0 * 8 - b['vofs']}), palettes {sorted(pals)}")
    print("grid=[")
    for row in grid:
        print("    [" + ", ".join("None" if c is None else
                                  f"0x{c & 0xFFFFFF:06X}" + ("|H" if c & HFLIP else "") + ("|V" if c & VFLIP else "")
                                  for c in row) + "],")
    print("]")
    for n in notes:
        print("#", n)
    if a.png:
        from PIL import Image
        p = sorted(pals)[0]
        cols = [struct.unpack_from("<H", pal, (p * 16 + i) * 2)[0] for i in range(16)]
        rgb = [((c & 31) * 8, (c >> 5 & 31) * 8, (c >> 10 & 31) * 8) for c in cols]
        img = Image.new("RGB", (len(grid[0]) * 8, len(grid) * 8))
        for gy in range(y0, y1 + 1):
            for gx in range(x0, x1 + 1):
                e = entry(vram, b, gx, gy)
                d = vram[b["char"] + (e & 0x3FF) * 32:][:32]
                for y in range(8):
                    for x in range(8):
                        v = d[y * 4 + x // 2] >> (4 * (x & 1)) & 15
                        X = 7 - x if e & 0x400 else x
                        Y = 7 - y if e & 0x800 else y
                        img.putpixel(((gx - x0) * 8 + X, (gy - y0) * 8 + Y), rgb[v])
        img.resize((img.width * 4, img.height * 4), Image.NEAREST).save(a.png)
        print("#", a.png)


if __name__ == "__main__":
    main()
