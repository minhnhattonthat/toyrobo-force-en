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
import cards  # noqa: E402
import font_en  # noqa: E402

HFLIP, VFLIP = 1 << 28, 1 << 29  # grid cell flags (tools/gfx_grid.py writes grids)

# label: (x, y, w, h) clear rect in block pixels, text, clear index, ink index, shadow index or None, scale
# [, dict(prop=, outline=, left=)]. A group is a raw run (at, tiles, cols), an LZ block (lz, ...) or a grid.
GROUPS = {
    # G4 title menu: the whole title screen is 352 raw tiles at 0x2B6B8, DMA'd to VRAM 0x8000 (BG1, 32 tiles
    # wide; work/qa/g4_title, tools/debug/dmalog.lua). Button fill index and ink measured with `show`.
    # Buttons: fill 2, ink 3, text rows 37-47 / 53-63 / 69-79 (the third button's bottom frame is elsewhere).
    "title": dict(at=0x2B6B8, tiles=352, cols=32, pal=("gfx/pal/title.pal.bin", 2), labels=[
        ((108, 36, 104, 12), "New Game", 2, 3, None, 1),
        ((108, 52, 104, 12), "Continue", 2, 3, None, 1),
        ((107, 68, 106, 12), "Two-Player Battle", 2, 3, None, 1),
    ]),
    # G3 title-screen credit line (OBJ, 2D mapping): the title sprites are LZ block 0x2BB0A8, decompressed to OBJ
    # VRAM 0x14000 (tile 0x200), a sheet 32 tiles wide. "キャラクターデザイン 西川伸司" was 5 sprites 128 px wide
    # (tiles 0x3C0.., 0x384..; work/qa/g3). The English needs 181 px, so the line's 5 sprite records in the title
    # OAM table (OAM_PATCHES) become three 64x32 sprites over blank, unused sheet tiles (rows below 160 are off
    # screen); the strip is drawn once and cut into 64-px pieces.
    "title_obj": dict(lz=0x2BB0A8, at=0, tiles=512, cols=32, pal=("gfx/pal/title_obj.pal.bin", 17), labels=[],
                      strips=[dict(w=192, h=16, text="Character Design: Shinji Nishikawa", ink=14, shadow=None,
                                   outline=11, prop=True, dest=[(192, 64), (192, 80), (192, 96)])]),
    # G14/G12 battle UI sheet: raw 4bpp, 32 tiles wide (0x400 bytes a tile row), aligned at 0x0FB16C; the sortie
    # report's labels are BG1 cells pointing into it (work/qa/p8g/r_rep.png). Rects are sheet pixels.
    # Cell budgets are the BG1 map's (3 tiles for 任務/成果/以上, 4 for 評価 and the stamps): hence Task / Haul /
    # Rank / Clear / Fail (Mission, Results, Rating, Failed don't fit in the font_en letters).
    "report": dict(at=0x0FB16C, tiles=32 * 36, cols=32, pal=("gfx/pal/report.pal.bin", 7), labels=[
        ((0, 128, 80, 16), "Sortie Report", 0, 6, None, 1, dict(prop=True)),
        ((136, 32, 24, 16), "Task", 0, 1, None, 1, dict(prop=True)),
        ((80, 144, 24, 16), "Haul", 0, 1, None, 1, dict(prop=True)),
        ((0, 144, 32, 24), "Rank", 0, 6, None, 1, dict(prop=True)),
        ((176, 240, 24, 16), "End", 0, 1, None, 1, dict(prop=True)),
        ((128, 120, 32, 24), "Clear", 0, 14, None, 1, dict(prop=True, outline=12)),
        ((128, 144, 32, 24), "Fail", 0, 13, None, 1, dict(prop=True, outline=11)),
        # Loss report's key panel (BG3, map cells 0x0FD36C..): Ⓐ/Ⓑ 終了, ▲上, ▼下. 下 has 2 tiles on its top row
        # but only 1 below (the next cell is the shared blank 0x02B278): "Dn" sits in the top row (flagged
        # abbreviation; "Down" is 23 px).
        ((128, 64, 24, 16), "Exit", 15, 11, None, 1, dict(prop=True)),
        ((128, 80, 16, 16), "Up", 15, 11, None, 1, dict(prop=True)),
        ((144, 80, 16, 16), "", 15, 11, None, 1),
        ((144, 80, 16, 9), "Dn", 15, 11, None, 1, dict(prop=True)),
    ]),
    # G15 workshop menu buttons (factory and facility1-5): BG1 palette 0, raw tiles; grid from
    # `gfx_grid.py <factory dump> --bg 1 --rect 4,84,72,62`: map cells 3-8 of rows 2-7 (cell 3 is the button's
    # right half for A/B; for R it holds the start of じ). Fill F, ink B, text rows 4-12 / 20-28 / 36-44.
    "factory": dict(pal=("gfx/pal/factory.pal.bin", 0), grid=[
        [0x064D14 | HFLIP, 0x0654F4, 0x065514, 0x065534, 0x065554, 0x065574],
        [0x064DD4 | HFLIP, 0x065594, 0x0655B4, 0x0655D4, 0x0655F4, 0x065614],
        [0x064EB4, 0x064ED4, 0x064EF4, 0x064F14, 0x064F34, 0x064F54],
        [0x064F94, 0x064FB4, 0x064FD4, 0x064FF4, 0x065014, 0x065034],
        [0x065654, 0x065674, 0x065694, 0x0656B4, 0x0656D4, 0x0656F4],
        [0x065734, 0x065754, 0x065774, 0x065794, 0x0657B4, 0x0657D4],
    ], labels=[
        ((8, 2, 40, 13), "Repair", 15, 11, None, 1, dict(prop=True, left=True)),
        ((8, 18, 40, 13), "Back", 15, 11, None, 1, dict(prop=True, left=True)),
        ((8, 34, 40, 13), "Info", 15, 11, None, 1, dict(prop=True, left=True)),
    ]),
}


def sprite_grid(base, sprites, w=8, h=4):
    """Grid of a row of OBJ sprites stored back to back in 1D order (each w x h tiles)."""
    return [[base + (c // w) * w * h * 32 + (r * w + c % w) * 32 for c in range(sprites * w)] for r in range(h)]


# G6 map location banners: 35 images of 128x32 (two 64x32 sprites, 1D) + their 32-byte palette, stride 0x820 from
# 0x0A6D84, in the order of the game's location ids (work/qa/p8g/banners*.png). Frame interior: fill 7 (navy) at
# x 8-119, y 8-23 (rows 7 and 24 are fill too, kept as a margin); the kanji are white, index 1.
LOC_BANNERS = 0x0A6D84
LOC_RECT, LOC_FILL, LOC_INK, LOC_SHADOW = (8, 8, 112, 16), 7, 1, None
LOCATIONS_EN = [
    "Gate", "Police Academy", "Factory", "Police Station", "City Hall", "Kindergarten", "Downtown", "Hospital",
    "Soldier Base", "Laboratory", "Hotel", "Army Headquarters", "Restaurant", "Metropolitan Police",
    "Fishing Village", "West Slope", "Cave Entrance", "East Slope", "Apricot", "Camembert Ranch", "Plum Mountain",
    "Apricot Port", "Framboise", "Winery", "Offshore Oil Rig", "Cassis", "Arsenal", "Battlefield Hill",
    "Lingonberry", "Special Police", "Kanpachi Dam", "Marmalade", "Sherwood Forest", "Marmalade Sea", "Blackberry",
]
for _i, _name in enumerate(LOCATIONS_EN):
    GROUPS[f"loc{_i:02d}"] = dict(pal=("gfx/pal/map.pal.bin", 25), grid=sprite_grid(LOC_BANNERS + _i * 0x820, 2),
                                  labels=[(LOC_RECT, _name, LOC_FILL, LOC_INK, LOC_SHADOW, 1, dict(prop=True))])

# (ROM offset, original bytes, new bytes, why): sprite records next to a redrawn group. Title OAM table records are
# (attr0, attr1, attr2, 0) relative to (128, 128); 0x24A73C holds the credit line's 5 (docs/re/graphics.md G3).
_C = (0x4010, 0xC018, 0x1398, 0)  # x -104/-40/+24: the same span as line 1 (x 24-216)
OAM_PATCHES = [
    (0x24A73C, bytes.fromhex("1040b881c0130000" "1040d881c4130000" "1000f841c8130000" "1040088084130000"
                             "1000284088130000"),
     struct.pack("<20H", 0x4010, 0xC198, 0x1318, 0, 0x4010, 0xC1D8, 0x1358, 0, *_C, *_C, *_C),
     "title credit line: 3 sprites 64x32 (the last one repeated in the spare records)"),
]


def _grid(g):
    """A grid group's shape: cols and tiles filled in from the grid (rows of ROM offsets | flips, or None)."""
    if "grid" in g and "cols" not in g:
        g["cols"], g["tiles"] = len(g["grid"][0]), len(g["grid"]) * len(g["grid"][0])
    return g


def _cell(g, t):
    """(ROM offset, hflip, vflip) of tile t, or None for a grid cell with no tile of its own."""
    if "grid" not in g:
        return g["at"] + t * 32, False, False
    c = g["grid"][t // g["cols"]][t % g["cols"]]
    return None if c is None else (c & 0xFFFFFF, bool(c & HFLIP), bool(c & VFLIP))


def decode(rom, g):
    """Block (or grid of tiles as the screen shows them) -> list of rows of palette indices (cols*8 wide)."""
    _grid(g)
    w, rows = g["cols"] * 8, (g["tiles"] + g["cols"] - 1) // g["cols"] * 8
    px = [[0] * w for _ in range(rows)]
    for t in range(g["tiles"]):
        cell = _cell(g, t)
        if cell is None:
            continue
        base, hf, vf = cell
        tx, ty = t % g["cols"] * 8, t // g["cols"] * 8
        for y in range(8):
            for x in range(8):
                b = rom[base + y * 4 + x // 2]
                px[ty + (7 - y if vf else y)][tx + (7 - x if hf else x)] = b >> 4 if x & 1 else b & 15
    return px


def encode_tile(px, g, t):
    """Tile t's 32 bytes as stored (a grid cell's flips undone)."""
    _, hf, vf = _cell(g, t)
    tx, ty = t % g["cols"] * 8, t // g["cols"] * 8
    out = bytearray(32)
    for y in range(8):
        for x in range(0, 8, 2):
            r = px[ty + (7 - y if vf else y)]
            a, b = (tx + 7 - x, tx + 6 - x) if hf else (tx + x, tx + x + 1)
            out[y * 4 + x // 2] = r[a] | r[b] << 4
    return bytes(out)


def tile_writes(px, g, touched):
    """[(ROM offset, bytes)] for the touched tiles; a grid tile shown twice must come out the same both times, and
    a touched cell with no tile of its own must stay blank."""
    out = {}
    for t in sorted(touched):
        cell = _cell(g, t)
        tx, ty = t % g["cols"] * 8, t // g["cols"] * 8
        if cell is None:
            if any(px[ty + y][tx + x] for y in range(8) for x in range(8)):
                raise ValueError(f"grid cell {t} has no ROM tile but the redraw inks it")
            continue
        data = encode_tile(px, g, t)
        if out.setdefault(cell[0], data) != data:
            raise ValueError(f"tile {cell[0]:06X} is shown twice in the grid and would need two contents")
    return sorted(out.items())


def _glyph_cols(ch, prop):
    """(first column, width) of a glyph: the full cell, or its inked columns (space = 3 px) when proportional."""
    if not prop:
        return 0, font_en.WIDTH
    m = 0
    for bits in font_en.GLYPHS[ch]:
        m |= bits
    cols = [x for x in range(font_en.WIDTH) if m >> (font_en.WIDTH - 1 - x) & 1]
    return (cols[0], cols[-1] - cols[0] + 1) if cols else (0, 3)


def text_width(s, scale=1, prop=False):
    return (sum(_glyph_cols(ch, prop)[1] + 1 for ch in s) - 1) * scale


def draw(px, lab, prop=False, outline=None, left=False):
    """Draw a label; outline: an index drawn on the 8 neighbours of every ink pixel (the title sprites' style);
    left: start at the rect's left edge instead of centring. A label tuple may carry these as a 7th item (dict)."""
    (x, y, w, h), s, clear, ink, shadow, scale = lab[:6]
    if len(lab) > 6:
        prop, outline, left = lab[6].get("prop", prop), lab[6].get("outline", outline), lab[6].get("left", left)
    for yy in range(y, y + h):
        for xx in range(x, x + w):
            px[yy][xx] = clear
    m = 1 if outline is not None else 0
    tw, th = text_width(s, scale, prop) + 2 * m, font_en.HEIGHT * scale + 2 * m
    if tw > w or th > h:
        raise ValueError(f"{s!r}: {tw}x{th} px, rect {w}x{h}")
    ox, oy = x + (0 if left else (w - tw) // 2) + m, y + (h - th) // 2 + m
    passes = [(dx, dy, outline) for dx in (-1, 0, 1) for dy in (-1, 0, 1) if (dx or dy)] if m else []
    for dx, dy, idx in passes + [(1, 1, shadow), (0, 0, ink)]:
        if idx is None:
            continue
        pen = ox
        for ch in s:
            c0, cw = _glyph_cols(ch, prop)
            for gy, bits in enumerate(font_en.GLYPHS[ch]):
                for gx in range(c0, c0 + cw):
                    if bits >> (font_en.WIDTH - 1 - gx) & 1:
                        for sy in range(scale):
                            for sx in range(scale):
                                X = pen + (gx - c0) * scale + sx + dx
                                Y = oy + gy * scale + sy + dy
                                if x <= X < x + w and y <= Y < y + h:
                                    px[Y][X] = idx
            pen += (cw + 1) * scale


def _touch(touched, g, x, y, w, h):
    for ty in range(y // 8, (y + h + 7) // 8):
        for tx in range(x // 8, (x + w + 7) // 8):
            touched.add(ty * g["cols"] + tx)


def redraw(buf, name):
    """(block pixels after the English labels and strips, set of tile numbers touched). buf: the ROM for a raw
    group, the decompressed block for an LZ group."""
    g = GROUPS[name]
    px = decode(buf, g)
    touched = set()
    for lab in g["labels"]:
        draw(px, lab)
        _touch(touched, g, *lab[0])
    for st in g.get("strips", ()):
        piece = st.get("piece", 64)
        canvas = [[st.get("clear", 0)] * st["w"] for _ in range(st["h"])]
        draw(canvas, ((0, 0, st["w"], st["h"]), st["text"], st.get("clear", 0), st["ink"], st["shadow"], 1),
             st.get("prop", False), st.get("outline"))
        for i, (dx, dy) in enumerate(st["dest"]):
            for yy in range(st["h"]):
                px[dy + yy][dx:dx + piece] = canvas[yy][i * piece:(i + 1) * piece]
            _touch(touched, g, dx, dy, piece, st["h"])
    return px, touched


# Redrawn LZ blocks that outgrow their packed size go to the expanded ROM (units.LZBlocks.moves): block offset ->
# (new offset, pointer words). 0x500000-0x580000 is free (tools/engine.py layout ends at NEW_STRINGS_END 0x4F0000).
LZ_MOVES = {
    0x2BB0A8: (0x500000, [0x1F874]),  # title sprites (G3), loaded via the literal at 0x1F874
}


def apply_lz(blocks):
    """Redraw the LZ groups inside the unpacked LZ unit ({block offset: bytes}) before it is packed."""
    for name, g in GROUPS.items():
        if "lz" in g:
            buf = bytearray(blocks[g["lz"]])
            px, touched = redraw(buf, name)
            for t in sorted(touched):
                buf[g["at"] + t * 32:g["at"] + t * 32 + 32] = encode_tile(px, g, t)
            blocks[g["lz"]] = bytes(buf)


def card_strip(label, name):
    """(strip bytes, label sprites, name sprites) for one section card (tools/cards.py), text left-aligned."""
    parts = []
    for s, cap in ((label, 2), (name, 5)):
        w = text_width(s) + 2
        n = (w + 31) // 32
        if n > cap:
            raise ValueError(f"card text {s!r}: {w} px, room {cap * 32}")
        rows = [[0] * (n * 32) for _ in range(16)]
        draw(rows, ((0, 0, w, 16), s, 0, cards.INK, None, 1), outline=cards.OUTLINE)
        parts.append((cards.sprites_from_rows(rows), n))
    return parts[0][0] + parts[1][0], parts[0][1], parts[1][1]


def apply_cards(out):
    """Section cards (G7/G17): each English strip goes to cards.NEW_STRIPS; its record's strip pointer and layout
    word (total tiles, label sprites, name sprites) are rewritten. Positions stay (label x 12 / name x 80 or
    4 / 56: the name has 160 px either way)."""
    pos = cards.NEW_STRIPS
    for rec, (label, name) in zip(cards.records(out.data), cards.CARDS_EN, strict=True):
        strip, nl, nn = card_strip(label, name)
        if pos + len(strip) > cards.NEW_STRIPS_END:
            raise ValueError("card strips run past NEW_STRIPS_END")
        out.write(pos, strip, f"gfx:card {label}")
        lay = 8 * (nl + nn) | nl << 16 | nn << 24
        (lx, ly), (nx, ny) = rec["label_xy"], rec["name_xy"]
        nx = max(nx, lx + text_width(label) + 12)  # "Episode 8" is wider than 第八話: keep a 2-letter gap
        if nx + text_width(name) + 2 > 240:
            raise ValueError(f"card {name!r} runs off screen at x {nx}")
        out.write(rec["off"] + 8, struct.pack("<IIHHHH", 0x08000000 + pos, lay, lx, ly, nx, ny),
                  f"gfx:card record {label}")
        pos += len(strip)


def apply(out):
    """Write every raw group's redrawn tiles and the sprite-record patches into the Rom being built (units.Rom)."""
    apply_cards(out)
    for name, g in GROUPS.items():
        if "lz" in g:
            continue
        px, touched = redraw(out.data, name)
        for off, data in tile_writes(px, g, touched):
            if bytes(out.data[off:off + 32]) != data:
                out.write(off, data, f"gfx:{name}")
    for off, old, new, why in OAM_PATCHES:
        if bytes(out.data[off:off + len(old)]) != old or len(new) != len(old):
            raise ValueError(f"gfx patch {off:06X} ({why}): original bytes differ")
        out.write(off, new, f"gfx:{why}")


def spans():
    """Byte ranges apply() may write (tests/test_build.py allowed ranges; LZ blocks are the LZ unit's own)."""
    return ([(g["at"], g["at"] + g["tiles"] * 32) for g in GROUPS.values() if "lz" not in g and "grid" not in g]
            + [(c & 0xFFFFFF, (c & 0xFFFFFF) + 32) for g in GROUPS.values() for row in g.get("grid", ())
               for c in row if c is not None]
            + [(off, off + len(old)) for off, old, _, _ in OAM_PATCHES]
            + [(ref, ref + 4) for _, refs in LZ_MOVES.values() for ref in refs]
            + [(cards.CARD_TABLE + i * cards.REC + 8, cards.CARD_TABLE + i * cards.REC + 24) for i in range(24)])


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
    if "lz" in g:
        import gbacomp
        rom = gbacomp.decompress(rom, g["lz"])[0]
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
