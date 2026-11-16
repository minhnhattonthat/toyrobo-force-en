"""gba_layers.py: what draws a GBA screen region, from a ppudump (L.dump_ppu: .io.bin .oam.bin .vram.bin).

    python -X utf8 tools/gba_layers.py work/qa/x/ppu_001750 [--rect x,y,w,h]

Prints DISPCNT, each enabled BG (char base, map base, size, bpp, priority, scroll) with the tile ids of its map
entries inside the rect, and every OAM sprite overlapping the rect (x, y, size, tile, palette, priority).
"""
import argparse
import struct

SIZES = {0: [(8, 8), (16, 16), (32, 32), (64, 64)], 1: [(16, 8), (32, 8), (32, 16), (64, 32)],
         2: [(8, 16), (8, 32), (16, 32), (32, 64)]}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("prefix")
    ap.add_argument("--rect", default="0,0,240,160")
    a = ap.parse_args()
    rx, ry, rw, rh = map(int, a.rect.split(","))
    io = open(a.prefix + ".io.bin", "rb").read()
    oam = open(a.prefix + ".oam.bin", "rb").read()
    vram = open(a.prefix + ".vram.bin", "rb").read()
    disp = struct.unpack_from("<H", io, 0)[0]
    print(f"DISPCNT {disp:04X} mode {disp & 7} BG on {[i for i in range(4) if disp >> (8 + i) & 1]} "
          f"OBJ {'on' if disp & 0x1000 else 'off'} 1D-obj {bool(disp & 0x40)}")
    for bg in range(4):
        if not disp >> (8 + bg) & 1:
            continue
        cnt = struct.unpack_from("<H", io, 8 + 2 * bg)[0]
        hofs, vofs = struct.unpack_from("<HH", io, 0x10 + 4 * bg)
        char, mapb, size, bpp8 = (cnt >> 2 & 3) * 0x4000, (cnt >> 8 & 31) * 0x800, cnt >> 14, cnt >> 7 & 1
        print(f"BG{bg} cnt {cnt:04X} prio {cnt & 3} char {char:05X} map {mapb:05X} size {size} "
              f"{'8bpp' if bpp8 else '4bpp'} scroll {hofs & 511},{vofs & 511}")
        tiles = set()
        for ty in range(ry // 8, (ry + rh + 7) // 8):
            row = []
            for tx in range(rx // 8, (rx + rw + 7) // 8):
                mx, my = (tx + (hofs & 511) // 8) % 64, (ty + (vofs & 511) // 8) % 64
                blk = (mx // 32) + (my // 32) * (2 if size in (1, 3) else 1) if size else 0
                if size == 2:
                    blk = my // 32
                e = struct.unpack_from("<H", vram, mapb + blk * 0x800 + ((my % 32) * 32 + mx % 32) * 2)[0]
                row.append(f"{e & 0x3FF:03X}{'h' if e & 0x400 else ''}{'v' if e & 0x800 else ''}p{e >> 12:X}")
                tiles.add(e & 0x3FF)
            print("   ", " ".join(row))
        print(f"    {len(tiles)} distinct tiles")
    for i in range(128):
        a0, a1, a2 = struct.unpack_from("<HHH", oam, i * 8)
        if a0 >> 8 & 3 == 2:  # hidden
            continue
        shape, sz = a0 >> 14, a1 >> 14
        if shape == 3:
            continue
        w, h = SIZES[shape][sz]
        x, y = a1 & 511, a0 & 255
        x = x - 512 if x >= 240 else x
        y = y - 256 if y >= 160 else y
        if x < rx + rw and x + w > rx and y < ry + rh and y + h > ry:
            print(f"OBJ{i:3d} x{x:4d} y{y:4d} {w}x{h} tile {a2 & 0x3FF:03X} pal {a2 >> 12} prio {a2 >> 10 & 3} "
                  f"{'8bpp' if a0 & 0x2000 else '4bpp'}{' hflip' if a1 & 0x1000 else ''}")


if __name__ == "__main__":
    main()
