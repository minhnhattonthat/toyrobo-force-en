"""build.py: build the English ROM.

    python -X utf8 build.py              # -> build/toyrobo_force_en.gba + build/writes.tsv (romdiff.py --writes)
    python -X utf8 build.py --identity   # pack every unit with no edits; exit 1 unless the result == original ROM

Steps: check the dump against rom.sha1, unpack every unit in tools/units.py, apply the text edits (none yet:
phase 4 adds the script/ TSVs), pack every unit back, write the ROM and its write log.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402
import units  # noqa: E402

ORIG = ROOT / "rom" / "Toyrobo Force (Japan).gba"
OUT = ROOT / "build" / "toyrobo_force_en.gba"


def unpack(rom):
    us = units.make_units()
    return us, [u.unpack(rom) for u in us]


def pack(orig, us, datas):
    """Blank every byte the units own, then pack them all: a byte a unit forgets to write stays 0xFF."""
    out = units.Rom(orig)
    out.blank([s for u in us for s in units.spans(u)])
    for u, d in zip(us, datas):
        u.pack(d, out)
    return out


def apply_edits(us, datas):
    """Text edits go here (phase 4 onward). Identity build: none."""
    return datas


def build(identity=False):
    orig = ORIG.read_bytes()
    us, datas = unpack(orig)
    if not identity:
        datas = apply_edits(us, datas)
    return orig, pack(orig, us, datas)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="repack with no edits and compare to the original")
    args = ap.parse_args()
    check_rom.check()
    orig, out = build(identity=args.identity)
    if args.identity:
        if bytes(out.data) != orig:
            diff = next(i for i in range(min(len(orig), len(out.data))) if orig[i] != out.data[i])
            print(f"identity FAILED: first difference at {diff:06X}; {len(out.log)} writes changed bytes")
            return 1
        print(f"identity ok: {len(orig)} bytes, byte-identical, sha1 {hashlib.sha1(orig).hexdigest()}")
        return 0
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_bytes(out.data)
    (OUT.parent / "writes.tsv").write_text(out.writes_text(), encoding="utf-8")
    print(f"{OUT.relative_to(ROOT)}: {len(out.data)} bytes, {len(out.log)} writes, "
          f"sha1 {hashlib.sha1(out.data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
