"""credits_pos.py: list where each credits piece is drawn (read-only analysis of the original ROM).

The credits code loads a piece with `ldr r0,[pc,#n]` (the `ref:` word in script/strings.tsv), then `movs r2,#pos`
and `bl 0x080114EC`. `pos` is a linear cell position in an 18-cell-wide grid (0x03000850+0x1F08): row = pos // 18,
column = pos % 18, 12 px a cell, 2 letters a cell; text past column 17 wraps to the next row. tools/engine.py
CREDIT_POS moves pieces by rewriting that immediate.

    python -X utf8 tools/credits_pos.py        id  ref  movs-offset  pos (row,col)  en
"""
import struct
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import text  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


def sites(rom, lo=0x400, hi=0x2400):
    """{ref word offset: [(movs r2 offset, pos)]} for every ldr r0 of a literal in [lo, hi)."""
    out = {}
    for a in range(lo, hi, 2):
        h = struct.unpack_from("<H", rom, a)[0]
        if h & 0xFF00 != 0x4800:  # ldr r0, [pc, #imm8*4]
            continue
        ref = ((a + 4) & ~3) + (h & 0xFF) * 4
        for b in range(a + 2, a + 12, 2):
            g = struct.unpack_from("<H", rom, b)[0]
            if g & 0xFF00 == 0x2200:  # movs r2, #imm8
                out.setdefault(ref, []).append((b, g & 0xFF))
                break
    return out


def main():
    rom = (ROOT / "rom" / "Toyrobo Force (Japan).gba").read_bytes()
    s = sites(rom)
    rows = [r for r in text.load_all()["strings.tsv"] if r["id"].startswith("credits:")]
    for r in rows:
        for ref in (int(x, 16) for x in r["where"][4:].split(",")):
            for off, pos in s.get(ref, [(None, None)]):
                where = f"{off:06X} {pos:3d} ({pos // 18},{pos % 18:2d})" if off else "-"
                print(f"{r['id']}  {ref:06X}  {where}  {r['jp']} | {r['en']}")


if __name__ == "__main__":
    main()
