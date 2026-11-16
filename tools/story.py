"""story.py: story-pass chapter files from script/dialogue (read-only on the TSVs).

    python -X utf8 tools/story.py [--out work/qa/story/chapters]

One file per chapter (groups of dialogue sections, from docs/synopsis.md's section list), rows in script-record
order: `>> id | speaker | JP` then `   EN`. The speaker is the English label before `: "` (or `-`). Face/speaker/wait
tokens are dropped and {br} becomes " / ", as in tools/pairs.py. Then:
    python -X utf8 $SKILL/scripts/qa_gate.py init work/qa/story/manifest.tsv work/qa/story/chapters --glob "*.txt"
"""
import argparse
import re
from pathlib import Path

from pairs import ROOT, clean, rec, rows

# chapter -> dialogue sections (s23 is split: finale dlg:2397-2558, then supplementary/optional records)
CHAPTERS = {
    "c01_academy": ["s00", "s01"],
    "c02_ranch": ["s02"],
    "c03_bus": ["s03"],
    "c04_revolt": ["s04", "s05"],
    "c05_framboise": ["s06"],
    "c06_oilrig": ["s07", "s08"],
    "c07_cassis": ["s09"],
    "c08_coup": ["s10"],
    "c09_lingonberry": ["s11", "s12"],
    "c10_fugitives": ["s13", "s14"],
    "c11_marmalade": ["s15"],
    "c12_goldfish": ["s16", "s17", "s18"],
    "c13_emiko": ["s19"],
    "c14_island": ["s20", "s21", "s22"],
    "c15_finale": ["s23a"],
    "c16_extras": ["s23b"],
}
FINALE_END = 2558
SPK = re.compile(r'^([^"「:]{1,40}): "')


def section(name):
    base = name[:3]
    rs = sorted(rows(ROOT / "script" / "dialogue" / f"{base}.tsv"), key=rec)
    if name == "s23a":
        rs = [r for r in rs if int(r["id"].split(":")[1]) <= FINALE_END]
    elif name == "s23b":
        rs = [r for r in rs if int(r["id"].split(":")[1]) > FINALE_END]
    return rs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "work" / "qa" / "story" / "chapters"))
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    for ch, secs in CHAPTERS.items():
        lines = []
        n = 0
        for s in secs:
            for r in section(s):
                en = clean(r["en"]) if r["en"] else "(untranslated)"
                m = SPK.match(en)
                lines.append(f">> {r['id']} | {m.group(1) if m else '-'} | {clean(r['jp'])}")
                lines.append(f"   {en}")
                n += 1
        (out / f"{ch}.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"{ch}: {n}")


if __name__ == "__main__":
    main()
