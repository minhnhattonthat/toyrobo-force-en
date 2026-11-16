"""lz_dump.py: decompress every BIOS-LZ77 block gbacomp.scan finds into a directory, for vramfind.py.

    python -X utf8 tools/lz_dump.py ROM OUTDIR [--min 256]

Writes OUTDIR/lz_<offset hex>.bin per block. vramfind then names the block by its file.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gbacomp  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom")
    ap.add_argument("out")
    ap.add_argument("--min", type=int, default=256)
    a = ap.parse_args()
    data = open(a.rom, "rb").read()
    os.makedirs(a.out, exist_ok=True)
    n = 0
    for blk in gbacomp.scan(data, a.min):
        off = blk[0]
        raw, _ = gbacomp.decompress(data, off)
        with open(os.path.join(a.out, f"lz_{off:06X}.bin"), "wb") as f:
            f.write(raw)
        n += 1
    print(f"{n} blocks -> {a.out}")


if __name__ == "__main__":
    main()
