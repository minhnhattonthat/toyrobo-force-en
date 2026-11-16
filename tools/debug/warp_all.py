"""Run every scene in tools/debug/scenes.gba.txt from a cold boot and prove it with a shot.

    python -X utf8 tools/debug/warp_all.py [ROM] [--only sec03,battle_win] [--jobs 3] [--states] [--out DIR]

Per scene: emu.py ROM --script tools/debug/warp.lua --var SCENE='<name>' --frames <boot + hold> --smoke, into
DIR/<name>/ (shots every 100 frames, final.png). --states also saves work/states/<name>.mss at the end (regenerate
the library after any code, font or graphics change). A scene fails if emu.py exits non-zero (Lua error, smoke:
flat final frame) or its log lacks the WARP/TITLE line. Writes DIR/results.tsv and DIR/finals*.png (one tile per
scene, in list order). Exit 1 if any scene failed.
"""
import argparse
import os
import shutil
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
from skill import SKILL  # noqa: E402

SCENES = os.path.join(REPO, "tools", "debug", "scenes.gba.txt")
WARP = os.path.join(REPO, "tools", "debug", "warp.lua")
BOOT = 1430  # the warp lands at about frame 1422 (logos, title, New game)


def load_scenes(path=SCENES):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0]
        cols = [c.strip() for c in line.split("|")]
        if cols[0]:
            out.append((cols[0], cols[1], int(cols[2])))
    return out


def run(rom, out, name, hold, states):
    d = os.path.join(out, name)
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), rom, "--out", d,
           "--frames", str(BOOT + hold), "--shot-every", "100", "--smoke", "--timeout", "900",
           "--script", WARP, "--var", f"SCENE='{name}'"]
    if states:
        cmd += ["--state-out", os.path.join(REPO, "work", "states", name + ".mss")]
    with open(d + ".out", "w", encoding="utf-8") as log:
        code = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)
    try:
        text = open(os.path.join(d, "log.txt"), encoding="utf-8").read()
    except OSError:
        text = ""
    warped = "WARP " in text or "TITLE " in text
    ok = code == 0 and warped and os.path.exists(os.path.join(d, "final.png"))
    return name, ok, code, warped


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("rom", nargs="?", default=os.path.join(REPO, "rom", "Toyrobo Force (Japan).gba"))
    ap.add_argument("--only", help="comma-separated scene names")
    ap.add_argument("--jobs", type=int, default=3)
    ap.add_argument("--states", action="store_true")
    ap.add_argument("--out", default=os.path.join(REPO, "work", "qa", "warp_all"))
    a = ap.parse_args()
    scenes = load_scenes()
    if a.only:
        want = set(a.only.split(","))
        unknown = want - {s[0] for s in scenes}
        if unknown:
            sys.exit(f"unknown scenes: {', '.join(sorted(unknown))}")
        scenes = [s for s in scenes if s[0] in want]
    os.makedirs(a.out, exist_ok=True)
    rom = os.path.abspath(a.rom)
    with ThreadPoolExecutor(a.jobs) as ex:
        results = list(ex.map(lambda s: run(rom, a.out, s[0], s[2], a.states), scenes))
    with open(os.path.join(a.out, "results.tsv"), "w", encoding="utf-8") as f:
        for name, ok, code, warped in results:
            f.write(f"{name}\t{'ok' if ok else 'FAIL'}\texit={code}\twarped={warped}\n")
    fdir = os.path.join(a.out, "finals")
    os.makedirs(fdir, exist_ok=True)
    finals = []
    for n, *_ in results:  # copies named after the scene, so the sheet's tile labels say which scene it is
        src = os.path.join(a.out, n, "final.png")
        if os.path.exists(src):
            finals.append(os.path.join(fdir, n + ".png"))
            shutil.copyfile(src, finals[-1])
    if finals:
        subprocess.call([sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "sheet.py"), *finals,
                         "--div", "2", "--cols", "6", "--max", "24", "--out", os.path.join(a.out, "finals.png")])
    bad = [n for n, ok, *_ in results if not ok]
    print(f"{len(results) - len(bad)}/{len(results)} scenes ok" + (f"; FAILED: {', '.join(bad)}" if bad else ""))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
