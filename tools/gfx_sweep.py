"""gfx_sweep.py: static graphics sweep sheets (Phase 1 survey).

    python -X utf8 tools/gfx_sweep.py raw ROM OUT --start 0x9C800 --end 0x710000 [--page 0x20000] [--fmt gba4] [--zoom 2]
    python -X utf8 tools/gfx_sweep.py lz  ROM OUT [--fmt gba4] [--zoom 2] [--page-h 1400]

raw: renders [start,end) as linear GBA tiles, `page` bytes per sheet, 64 tiles per row, with the ROM offset of
every 8th row on the left. Pages that are all 0xFF/0x00 are skipped and listed as skipped (never silently).
lz: decompresses every block gbacomp.scan finds and stacks them, labelled with offset and size, into sheets.
Both write OUT/index.tsv (sheet -> offsets covered, or skip reason). Greyscale, colour 0 black.
"""
import argparse
import os
import sys

from PIL import Image, ImageDraw

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gbacomp  # noqa: E402

COLS = 64
LABEL_W = 64


def tiles_img(data, fmt, cols=COLS):
    tb = 32 if fmt == "gba4" else 64
    n = len(data) // tb
    rows = (n + cols - 1) // cols
    img = Image.new("L", (cols * 8, max(rows, 1) * 8), 0)
    px = img.load()
    for t in range(n):
        b = data[t * tb:(t + 1) * tb]
        tx, ty = (t % cols) * 8, (t // cols) * 8
        for y in range(8):
            for x in range(8):
                if fmt == "gba4":
                    v = b[y * 4 + x // 2]
                    v = (v >> 4) if x & 1 else (v & 15)
                    v *= 17
                else:
                    v = b[y * 8 + x]
                px[tx + x, ty + y] = v
    return img


def raw(a, rom):
    os.makedirs(a.out, exist_ok=True)
    idx = []
    tb = 32 if a.fmt == "gba4" else 64
    row_bytes = a.cols * tb
    for p, off in enumerate(range(a.start, a.end, a.page)):
        chunk = rom[off:min(off + a.page, a.end)]
        if chunk.count(0xFF) > len(chunk) * 0.98 or chunk.count(0) > len(chunk) * 0.98:
            idx.append(f"-\t{off:07X}\t{off + len(chunk):07X}\tskipped: fill")
            print(f"skip {off:07X} fill")
            continue
        t = tiles_img(chunk, a.fmt, a.cols)
        t = t.resize((t.width * a.zoom, t.height * a.zoom), Image.NEAREST)
        img = Image.new("L", (t.width + LABEL_W, t.height), 40)
        img.paste(t, (LABEL_W, 0))
        d = ImageDraw.Draw(img)
        for r in range(0, (len(chunk) + row_bytes - 1) // row_bytes, 8):
            d.text((2, r * 8 * a.zoom), f"{off + r * row_bytes:06X}", fill=255)
        name = f"raw_{a.fmt}_{off:07X}.png"
        img.save(os.path.join(a.out, name))
        idx.append(f"{name}\t{off:07X}\t{off + len(chunk):07X}\trow={row_bytes:#x} bytes")
        print(name)
    open(os.path.join(a.out, "index.tsv"), "w").write("\n".join(idx) + "\n")


def lz(a, rom):
    os.makedirs(a.out, exist_ok=True)
    idx = []
    parts = []
    only = {int(x, 16) for x in a.only.split(",")} if a.only else None
    for off, packed, size in gbacomp.scan(rom):
        if only is not None and off not in only:
            continue
        out, _ = gbacomp.decompress(rom, off)
        if size < 512:
            idx.append(f"-\t{off:07X}\t{size}\tskipped: under 512 bytes (palette/map)")
            continue
        t = tiles_img(out, a.fmt, 32)
        t = t.resize((t.width * a.zoom, t.height * a.zoom), Image.NEAREST)
        parts.append((off, size, t))
    sheet, y, items, n = [], 0, [], 0

    def flush():
        nonlocal sheet, y, items, n
        if not sheet:
            return
        w = 32 * 8 * a.zoom + 2 * 8 + 8
        img = Image.new("L", (w * a.ncol, max(y, 1)), 40)
        # ncol columns of blocks side by side to keep sheets square-ish
        d = ImageDraw.Draw(img)
        for x0, y0, off, size, t in sheet:
            img.paste(t, (x0, y0 + 12))
            d.text((x0, y0), f"{off:07X} ({size}B)", fill=255)
        name = f"lz_{a.fmt}_{n:02d}.png"
        img = img.crop((0, 0, img.width, max(yy + 12 + tt.height for _, yy, _, _, tt in sheet)))
        img.save(os.path.join(a.out, name))
        idx.append(f"{name}\t" + ",".join(f"{o:07X}" for o in items))
        print(name, len(items))
        sheet, y, items, n = [], 0, [], n + 1

    col_y = [0] * a.ncol
    w = 32 * 8 * a.zoom + 24
    for off, size, t in parts:
        c = col_y.index(min(col_y))
        if col_y[c] + t.height + 12 > a.page_h and sheet:
            y = max(col_y)
            flush()
            col_y = [0] * a.ncol
            c = 0
        sheet.append((c * w, col_y[c], off, size, t))
        items.append(off)
        col_y[c] += t.height + 16
        y = max(col_y)
    y = max(col_y)
    flush()
    open(os.path.join(a.out, "index.tsv"), "w").write("\n".join(idx) + "\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mode", choices=["raw", "lz"])
    ap.add_argument("rom")
    ap.add_argument("out")
    num = lambda s: int(s, 0)  # noqa: E731
    ap.add_argument("--start", type=num, default=0)
    ap.add_argument("--end", type=num, default=None)
    ap.add_argument("--page", type=num, default=0x20000)
    ap.add_argument("--page-h", type=int, default=1400)
    ap.add_argument("--ncol", type=int, default=2, help="lz: block columns per sheet")
    ap.add_argument("--only", help="lz: comma-separated hex block offsets to render")
    ap.add_argument("--cols", type=int, default=COLS, help="raw: tiles per row")
    ap.add_argument("--fmt", default="gba4", choices=["gba4", "gba8"])
    ap.add_argument("--zoom", type=int, default=2)
    a = ap.parse_args()
    rom = open(a.rom, "rb").read()
    if a.end is None:
        a.end = len(rom)
    (raw if a.mode == "raw" else lz)(a, rom)


if __name__ == "__main__":
    main()
