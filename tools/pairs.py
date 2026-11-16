"""pairs.py: reviewer input files from script/ (`>> id | JP` / `EN` lines, read-only on the TSVs).

    python -X utf8 tools/pairs.py [--out work/qa/review]

One file per dialogue section (sNN.txt, rows in script-record order = story order), plus tables.txt, choices.txt
and strings.txt. Face/speaker/wait tokens are dropped for reading; {br} becomes " / ". Rows without `en` are
listed with EN `(untranslated)`. Neighbouring rows are the context, so no separate +-2 lines are written.
"""
import argparse
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NOISE = re.compile(r"\{(?:face:\d{5}|spk:\d\d|wait)\}")


def clean(s):
    return NOISE.sub("", s).replace("{br}", " / ").strip()


def rows(path):
    with open(path, encoding="utf-8", newline="") as f:
        return [r for r in csv.DictReader(f, delimiter="\t", quoting=csv.QUOTE_NONE) if r["kind"] == "text"]


def rec(r):
    m = re.match(r"rec:(\d+)", r["where"])
    return int(m.group(1)) if m else 0


def write(out, name, rs):
    lines = []
    for r in rs:
        lines.append(f">> {r['id']} | {clean(r['jp'])}")
        lines.append(f"   {clean(r['en']) if r['en'] else '(untranslated)'}")
    (out / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(rs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "review"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for p in sorted((ROOT / "script" / "dialogue").glob("s*.tsv")):
        n = write(out, p.stem + ".txt", sorted(rows(p), key=rec))
        print(f"{p.stem}: {n}")
    for name in ("tables", "choices", "strings"):
        print(f"{name}: {write(out, name + '.txt', rows(ROOT / 'script' / (name + '.tsv')))}")


if __name__ == "__main__":
    main()
