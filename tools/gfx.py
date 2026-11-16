"""gfx.py: graphics text (docs/re/graphics.md G-rows) redrawn in English with the project's pixel font.

    python -X utf8 tools/gfx.py show GROUP [--rect x,y,w,h]     # palette indices of a block region, as hex digits
    python -X utf8 tools/gfx.py preview GROUP OUT.png [--zoom 3] [--orig]   # the block as the build writes it

A group is a run of raw 4bpp tiles in the ROM laid out `cols` tiles wide (the order the game copies them to VRAM).
Each label clears a rect to one palette index and draws its English with tools/font_en.py glyphs (5x9, drawn for
this project: the same letters as the dialogue), centred, in an ink index (+ an optional shadow index one pixel
right/down). Glyphs are drawn at `scale` (1 or 2). build.py calls apply(rom) after the text units: every tile a
label touches is re-encoded and written through the logged Rom.write ("gfx:<group>").

Palettes for previews are VRAM palette dumps (L.dump_ppu) copied to gfx/pal/ (gitignored: game data; regenerate
with a warp + `--script $SKILL/scripts/lua/probes/ppudump.lua`, e.g. title: SCENE='title', DUMP_AT=1750).
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import font_en  # noqa: E402

# label: (x, y, w, h) clear rect in block pixels, text, clear index, ink index, shadow index or None, scale
GROUPS = {
    # G4 title menu: the whole title screen is 352 raw tiles at 0x2B6B8, DMA'd to VRAM 0x8000 (BG1, 32 tiles
    # wide; work/qa/g4_title, tools/debug/dmalog.lua). Button fill index and ink measured with `show`.
    # Buttons: fill 2, ink 3, text rows 37-47 / 53-63 / 69-79 (the third button's bottom frame is elsewhere).
    "title": dict(at=0x2B6B8, tiles=352, cols=32, pal=("gfx/pal/title.pal.bin", 2), labels=[
        ((108, 36, 104, 12), "New Game", 2, 3, None, 1),
        ((108, 52, 104, 12), "Continue", 2, 3, None, 1),
        ((107, 68, 106, 12), "Two-Player Battle", 2, 3, None, 1),
    ]),
}


def decode(rom, g):
    """Block -> list of rows of palette indices (cols*8 wide)."""
    w, rows = g["cols"] * 8, (g["tiles"] + g["cols"] - 1) // g["cols"] * 8
    px = [[0] * w for _ in range(rows)]
    for t in range(g["tiles"]):
        base = g["at"] + t * 32
        tx, ty = t % g["cols"] * 8, t // g["cols"] * 8
        for y in range(8):
            for x in range(8):
                b = rom[base + y * 4 + x // 2]
                px[ty + y][tx + x] = b >> 4 if x & 1 else b & 15
    return px


def encode_tile(px, g, t):
    tx, ty = t % g["cols"] * 8, t // g["cols"] * 8
    out = bytearray(32)
    for y in range(8):
        for x in range(0, 8, 2):
            out[y * 4 + x // 2] = px[ty + y][tx + x] | px[ty + y][tx + x + 1] << 4
    return bytes(out)


def text_width(s, scale=1):
    return (len(s) * (font_en.WIDTH + 1) - 1) * scale


def draw(px, lab):
    (x, y, w, h), s, clear, ink, shadow, scale = lab
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[yy][xx] = clear
    tw, th = text_width(s, scale), font_en.HEIGHT * scale
    if tw > w or th > h:
        raise ValueError(f"{s!r}: {tw}x{th} px, rect {w}x{h}")
    ox, oy = x + (w - tw) // 2, y + (h - th) // 2
    for layer, (dx, dy, idx) in enumerate(((1, 1, shadow), (0, 0, ink))):
        if idx is None:
            continue
        for i, ch in enumerate(s):
            rows = font_en.GLYPHS[ch]
            for gy, bits in enumerate(rows):
                for gx in range(font_en.WIDTH):
                    if bits >> (font_en.WIDTH - 1 - gx) & 1:
                        for sy in range(scale):
                            for sx in range(scale):
                                X = ox + (i * (font_en.WIDTH + 1) + gx) * scale + sx + dx
                                Y = oy + gy * scale + sy + dy
                                if x <= X < x + w and y <= Y < y + h:
                                    px[Y][X] = idx


def redraw(rom, name):
    """(block pixels after the English labels, set of tile numbers touched)."""
    g = GROUPS[name]
    px = decode(rom, g)
    touched = set()
    for lab in g["labels"]:
        draw(px, lab)
        x, y, w, h = lab[0]
        for ty in range(y // 8, (y + h + 7) // 8):
            for tx in range(x // 8, (x + w + 7) // 8):
                touched.add(ty * g["cols"] + tx)
    return px, touched


def apply(out):
    """Write every group's redrawn tiles into the Rom being built (units.Rom)."""
    for name, g in GROUPS.items():
        px, touched = redraw(out.data, name)
        for t in sorted(touched):
            out.write(g["at"] + t * 32, encode_tile(px, g, t), f"gfx:{name}")


def spans():
    """Byte ranges apply() may write (tests/test_build.py allowed ranges)."""
    return [(g["at"], g["at"] + g["tiles"] * 32) for g in GROUPS.values()]


def _palette(g):
    path, idx = g["pal"]
    raw = (ROOT / path).read_bytes()[idx * 32:idx * 32 + 32]
    out = []
    for i in range(16):
        c = struct.unpack_from("<H", raw, i * 2)[0]
        out.append(((c & 31) * 255 // 31, (c >> 5 & 31) * 255 // 31, (c >> 10 & 31) * 255 // 31))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmd", choices=("show", "preview"))
    ap.add_argument("group")
    ap.add_argument("out", nargs="?")
    ap.add_argument("--rect")
    ap.add_argument("--zoom", type=int, default=3)
    ap.add_argument("--orig", action="store_true", help="preview the original block (no labels)")
    a = ap.parse_args()
    rom = (ROOT / "rom" / "Toyrobo Force (Japan).gba").read_bytes()
    g = GROUPS[a.group]
    if a.cmd == "show":
        px = decode(rom, g)
        x, y, w, h = map(int, a.rect.split(",")) if a.rect else (0, 0, len(px[0]), len(px))
        for yy in range(y, y + h):
            print(f"{yy:3d} " + "".join(f"{px[yy][xx]:X}" for xx in range(x, x + w)))
        return
    from PIL import Image
    px = decode(rom, g) if a.orig else redraw(rom, a.group)[0]
    pal = _palette(g)
    img = Image.new("RGB", (len(px[0]), len(px)))
    img.putdata([pal[v] for row in px for v in row])
    img = img.resize((img.width * a.zoom, img.height * a.zoom), Image.NEAREST)
    img.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()
