"""Text coverage (phase 8 gate): log every string the game reads, then report what was never shown.

    python -X utf8 tools/debug/cover.py sweep  [ROM] [--chunk 400] [--jobs 4]   # -> work/qa/cover/sweep_NNNN/
    python -X utf8 tools/debug/cover.py tour   [ROM] [--jobs 3]                 # warp_all.py --cover -> cover/tour/
    python -X utf8 tools/debug/cover.py report                                  # textcover.py, exit 1 on gaps
    python -X utf8 tools/debug/cover.py extra NAME [ROM] -- EMU_ARGS..          # one scene run -> cover/extra_NAME/

extra: one warp run (warp.lua + EMU_ARGS such as --var "SCENE='factory'" --var "POKES=..." --var "KEYS=..."
--frames N) with the probe, for screens no scene or sweep reaches (parts lists, save/load); see docs/re/script.md.

sweep: the script's records in chunks; each chunk is one cold boot (tools/debug/warp.lua REC=<first target>) plus
tools/debug/sweep.lua, which runs every message (op 15) and choice (op 21) record of the chunk in turn with A
mashed. tour: every debug-tool scene (menus, factory, tables, credits, reports). Both append
$SKILL/scripts/lua/probes/textcover.lua with RANGES built from build/strings.tsv (tools/strmap.py; build.py
writes it). report: `textcover.py work/qa/cover build/strings.tsv --waive docs/text_unshown.tsv`.
"""
import argparse
import os
import shutil
import struct
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

REPO = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(REPO, "tools"))
from skill import SKILL  # noqa: E402
import strmap  # noqa: E402

ROM = os.path.join(REPO, "build", "toyrobo_force_en.gba")
STRINGS = os.path.join(REPO, "build", "strings.tsv")
OUT = os.path.join(REPO, "work", "qa", "cover")
WAIVE = os.path.join(REPO, "docs", "text_unshown.tsv")
DEBUG = os.path.join(REPO, "tools", "debug")
PROBE = os.path.join(SKILL, "scripts", "lua", "probes", "textcover.lua")
SCRIPT, RECORDS = 0x3831C8, 5538
BOOT = 1430
PER_TARGET = 260  # frame budget per message/choice (most take ~100; sweep.lua skips one stuck past 900)


def targets(rom, lo, hi):
    return [r for r in range(lo, hi) if struct.unpack_from("<H", rom, SCRIPT + r * 12)[0] in (15, 21)]


def run_chunk(rom_path, lo, hi, first, n, rng):
    d = os.path.join(OUT, f"sweep_{lo:04d}")
    shutil.rmtree(d, ignore_errors=True)
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), rom_path, "--out", d,
           "--frames", str(BOOT + n * PER_TARGET + 2000), "--mash", "8", "--shot-every", "5000", "--timeout", "3000",
           "--script", os.path.join(DEBUG, "warp.lua"), "--script", os.path.join(DEBUG, "sweep.lua"),
           "--script", PROBE, "--var", f"REC={first}", "--var", f"LO={lo}", "--var", f"HI={hi}",
           "--var", f"RANGES='{rng}'"]
    os.makedirs(OUT, exist_ok=True)
    with open(d + ".out", "w", encoding="utf-8") as log:
        code = subprocess.call(cmd, stdout=log, stderr=subprocess.STDOUT)
    try:
        text = open(os.path.join(d, "log.txt"), encoding="utf-8").read()
    except OSError:
        text = ""
    return lo, code, "SWEEP DONE" in text, text.count("STUCK rec")


def sweep(a):
    rom = open(a.rom, "rb").read()
    rng = strmap.ranges(STRINGS)
    jobs = []
    for lo in range(0, RECORDS, a.chunk):
        hi = min(lo + a.chunk, RECORDS)
        t = targets(rom, lo, hi)
        if t:
            jobs.append((lo, hi, t[0], len(t)))
    with ThreadPoolExecutor(a.jobs) as ex:
        res = list(ex.map(lambda j: run_chunk(a.rom, j[0], j[1], j[2], j[3], rng), jobs))
    bad = 0
    for lo, code, done, stuck in res:
        print(f"sweep_{lo:04d}: exit {code} {'done' if done else 'NOT DONE'} stuck {stuck}")
        bad += code != 0 or not done
    return 1 if bad else 0


def tour(a):
    cmd = [sys.executable, "-X", "utf8", os.path.join(DEBUG, "warp_all.py"), a.rom, "--out",
           os.path.join(OUT, "tour"), "--jobs", str(a.jobs), "--cover", strmap.ranges(STRINGS)]
    return subprocess.call(cmd)


def extra(a):
    d = os.path.join(OUT, f"extra_{a.name}")
    shutil.rmtree(d, ignore_errors=True)
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "emu.py"), a.rom, "--out", d,
           "--shot-every", "100", "--timeout", "3000", "--script", os.path.join(DEBUG, "warp.lua"), *a.emu,
           "--script", PROBE, "--var", f"RANGES='{strmap.ranges(STRINGS)}'"]
    return subprocess.call(cmd)


def report(a):
    cmd = [sys.executable, "-X", "utf8", os.path.join(SKILL, "scripts", "textcover.py"), OUT, STRINGS,
           "--mask", "0x1FFFFFF"]
    if os.path.exists(WAIVE):
        cmd += ["--waive", WAIVE]
    return subprocess.call(cmd)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    argv = sys.argv[1:]
    emu = []
    if "--" in argv:
        i = argv.index("--")
        argv, emu = argv[:i], argv[i + 1:]
    ap.add_argument("cmd", choices=("sweep", "tour", "report", "extra"))
    ap.add_argument("args", nargs="*", help="extra: NAME [ROM]; others: [ROM]")
    ap.add_argument("--chunk", type=int, default=400)
    ap.add_argument("--jobs", type=int, default=4)
    a = ap.parse_args(argv)
    a.emu = emu
    if a.cmd == "extra":
        if not a.args:
            ap.error("extra needs NAME")
        a.name, rest = a.args[0], a.args[1:]
    else:
        rest = a.args
    a.rom = os.path.abspath(rest[0] if rest else ROM)
    return {"sweep": sweep, "tour": tour, "report": report, "extra": extra}[a.cmd](a)


if __name__ == "__main__":
    sys.exit(main())
