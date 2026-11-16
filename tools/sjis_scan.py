"""sjis_scan.py: map Shift-JIS text runs in the ROM and group them into clusters (recon).

    python -X utf8 tools/sjis_scan.py [--min 4] [--gap 0x200] [--runs OUT.tsv]

A run = consecutive valid 2-byte SJIS chars (plus ASCII digits/punct inside), at least --min chars.
Prints one line per cluster (runs closer than --gap): start, end, runs, bytes, first text.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"


def is_lead(b):
    return 0x81 <= b <= 0x9F or 0xE0 <= b <= 0xEA


def runs(data, min_chars=4):
    i, n = 0, len(data)
    out = []
    while i < n - 1:
        j, chars = i, 0
        while j < n - 1 and is_lead(data[j]) and 0x40 <= data[j + 1] <= 0xFC and data[j + 1] != 0x7F:
            try:
                data[j:j + 2].decode("cp932")
            except UnicodeDecodeError:
                break
            j += 2
            chars += 1
        if chars >= min_chars:
            out.append((i, j, data[i:j].decode("cp932")))
            i = j
        else:
            i += 1
    return out


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--min", type=int, default=4)
    ap.add_argument("--gap", type=lambda s: int(s, 0), default=0x200)
    ap.add_argument("--runs")
    a = ap.parse_args(argv)
    data = ROM.read_bytes()
    rs = runs(data, a.min)
    if a.runs:
        with open(a.runs, "w", encoding="utf-8") as f:
            for s, e, t in rs:
                f.write(f"{s:06X}\t{e - s}\t{t}\n")
    cl = []
    for s, e, t in rs:
        if cl and s - cl[-1][1] < a.gap:
            cl[-1][1] = e
            cl[-1][2] += 1
            cl[-1][3] += e - s
        else:
            cl.append([s, e, 1, e - s, t])
    for s, e, k, b, t in cl:
        print(f"{s:06X}-{e:06X}\t{k}\t{b}\t{t[:24]}")
    print(f"{len(rs)} runs, {sum(e - s for s, e, _ in rs)} bytes, {len(cl)} clusters", file=sys.stderr)


if __name__ == "__main__":
    main()
