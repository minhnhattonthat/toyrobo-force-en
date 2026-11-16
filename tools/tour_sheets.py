"""tour_sheets.py: one contact sheet per scene of a warp_all.py tour, for the visual-QA gate (qa_gate.py).

    python -X utf8 tools/tour_sheets.py work/qa/tour_en [--only factory,link_battle]

Per scene dir: $SKILL/scripts/sheet.py DIR --from 1400 --out DIR/sheet.png (the warp lands ~frame 1422, so the
boot logos are left out); the title-menu scenes (scenes.gba.txt rows with record `title`) start at frame 0. Old
sheet*.png in the dir are deleted first so a shorter run leaves no stale page. Then:
    qa_gate.py init work/qa/manifest.tsv work/qa/tour_en --glob "*sheet*.png" --build build/toyrobo_force_en.gba
"""
import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
from skill import SKILL  # noqa: E402


def title_scenes():
    out = set()
    for line in (ROOT / "tools/debug/scenes.gba.txt").read_text(encoding="utf-8").splitlines():
        cols = [c.strip() for c in line.split("|")]
        if len(cols) > 1 and not line.startswith("#") and cols[1] == "title":
            out.add(cols[0])
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("tour")
    ap.add_argument("--only")
    a = ap.parse_args()
    only = set(a.only.split(",")) if a.only else None
    titles = title_scenes()
    n = 0
    for d in sorted(p for p in Path(a.tour).iterdir() if p.is_dir()):
        if (only and d.name not in only) or not any(d.glob("f0*.png")):  # skip non-scene dirs (finals/)
            continue
        for old in d.glob("sheet*.png"):
            old.unlink()
        lo = 0 if d.name in titles else 1400
        r = subprocess.run([sys.executable, "-X", "utf8", str(Path(SKILL) / "scripts" / "sheet.py"), str(d),
                            "--from", str(lo), "--out", str(d / "sheet.png")], capture_output=True, text=True)
        if r.returncode:
            sys.exit(f"{d.name}: sheet.py failed\n{r.stderr}")
        n += 1
    print(f"{n} sheets in {a.tour}")


if __name__ == "__main__":
    main()
