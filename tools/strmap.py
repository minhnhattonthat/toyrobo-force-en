"""strmap.py: the address the game reads each text row's first byte from, in a built ROM (text coverage).

    python -X utf8 tools/strmap.py [ROM] [--out build/strings.tsv]

build.py writes build/strings.tsv (id<TAB>hex CPU address) next to the ROM; `$SKILL/scripts/textcover.py` checks
it against the TEXT lines `tools/debug/cover.py` logs. Addresses follow the build's layout:
- dlg:k     slot k of the relocated dialogue (engine.NEW_DIALOGUE + k * engine.DIALOGUE_SLOT);
- @addr     table and choice records, packed in place (`where` column);
- ref:w,..  credits/strings/prompts: the pointer word at w in the built ROM (relocated strings follow it).
"""
import argparse
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

import engine  # noqa: E402
import text  # noqa: E402

GBA = 0x08000000


def addresses(rom, rows):
    """[(id, CPU address)] for every text row, in row order."""
    out = []
    for r in rows:
        if r["kind"] != "text":
            continue
        rid, where = r["id"], r["where"]
        if rid.startswith("dlg:"):
            off = engine.NEW_DIALOGUE + int(rid[4:]) * engine.DIALOGUE_SLOT
            out.append((rid, GBA | off))
        elif where.startswith("@"):
            out.append((rid, GBA | int(where[1:], 16)))
        elif where.startswith("ref:"):
            w = int(where[4:].split(",")[0], 16)
            (ptr,) = struct.unpack_from("<I", rom, w)
            if ptr & 0xFE000000 != GBA:
                raise ValueError(f"{rid}: pointer word {w:06X} holds {ptr:08X}, not a ROM address")
            out.append((rid, ptr))
        else:
            raise ValueError(f"{rid}: no address rule for where={where!r}")
    return out


def ranges(path, gap=0x2000):
    """The textcover.lua RANGES string covering every address in a strings.tsv (clusters closer than `gap` merge;
    each range runs 0x100 past its last string)."""
    addrs = sorted(int(line.split("\t")[1], 16) for line in open(path, encoding="utf-8") if "\t" in line)
    spans = []
    for a in addrs:
        if spans and a - spans[-1][1] < gap:
            spans[-1][1] = a
        else:
            spans.append([a, a])
    return ",".join(f"{lo:X}-{hi + 0xFF:X}" for lo, hi in spans)


def write_tsv(rom, path):
    rows = [r for rs in text.load_all().values() for r in rs]
    pairs = addresses(rom, rows)
    Path(path).write_text("".join(f"{i}\t{a:08X}\n" for i, a in pairs), encoding="utf-8")
    return len(pairs)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=str(ROOT / "build" / "toyrobo_force_en.gba"))
    ap.add_argument("--out", default=str(ROOT / "build" / "strings.tsv"))
    a = ap.parse_args()
    n = write_tsv(Path(a.rom).read_bytes(), a.out)
    print(f"{a.out}: {n} strings")


if __name__ == "__main__":
    main()
