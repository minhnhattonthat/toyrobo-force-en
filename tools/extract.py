"""extract.py: dump the original ROM's text to script/*.tsv (format: tools/text.py).

    python -X utf8 tools/extract.py            # writes only files that don't exist yet
    python -X utf8 tools/extract.py --check    # exit 1 if any file's ids/kind/where/max/jp differ from a fresh dump
    python -X utf8 tools/extract.py --force    # rewrite files, keeping every row's en and notes (refuses a lost id)

The dump never clobbers English: without --force an existing file is left alone, and --force carries `en`/`notes`
over by id and refuses to drop an id that has an `en`.
"""
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402
import text  # noqa: E402

ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"
KEYS = ("id", "kind", "where", "max", "jp")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group()
    g.add_argument("--check", action="store_true")
    g.add_argument("--force", action="store_true")
    args = ap.parse_args()
    check_rom.check()
    fresh = text.extract(ROM.read_bytes())
    have = text.load_all() if text.SCRIPT_DIR.is_dir() else {}
    bad = 0
    for name, rows in fresh.items():
        path = text.SCRIPT_DIR / name
        old = have.get(name)
        if args.check:
            if old is None or [[r[k] for k in KEYS] for r in old] != [[r[k] for k in KEYS] for r in rows]:
                print(f"{name}: differs from a fresh dump")
                bad += 1
            continue
        if old is not None:
            if not args.force:
                continue
            keep = {r["id"]: r for r in old}
            ids = {r["id"] for r in rows}
            lost = [i for i, r in keep.items() if i not in ids and r["en"]]
            if lost:
                print(f"{name}: refusing, these translated ids are gone from the dump: {lost[:10]}")
                return 1
            for r in rows:
                if r["id"] in keep:
                    r["en"], r["notes"] = keep[r["id"]]["en"], keep[r["id"]]["notes"] or r["notes"]
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text.dumps(rows), encoding="utf-8", newline="\n")
        print(f"script/{name}: {len(rows)} rows")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
