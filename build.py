"""build.py: build the English ROM.

    python -X utf8 build.py              # -> build/toyrobo_force_en.gba + build/writes.tsv (romdiff.py --writes)
    python -X utf8 build.py --identity   # pack every unit with no edits; exit 1 unless the result == original ROM

Steps: check the dump against rom.sha1, unpack every unit in tools/units.py, insert the `en` column of
script/*.tsv (tools/text.py), pack every unit back, write the ROM and its write log.
"""
import argparse
import hashlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))

import check_rom  # noqa: E402
import engine  # noqa: E402
import gfx  # noqa: E402
import marker  # noqa: E402
import text  # noqa: E402
import units  # noqa: E402
import windows  # noqa: E402

ORIG = ROOT / "rom" / "Toyrobo Force (Japan).gba"
OUT = ROOT / "build" / "toyrobo_force_en.gba"
MARK = ROOT / "build" / "toyrobo_force_marker.gba"
FIXED = ("swap:", "prompts:")  # strings.tsv rows padded to their jp length (docs/re/text.md)


def unpack(rom):
    us = units.make_units()
    return us, [u.unpack(rom) for u in us]


def pack(orig, us, datas, enc=None):
    """Blank every byte the units own, then pack them all: a byte a unit forgets to write stays 0xFF.
    With an engine encoder, expand the ROM first and apply the engine patches (tools/engine.py) last."""
    out = units.Rom(orig)
    if enc:
        engine.expand(out)
    out.blank([s for u in us for s in units.spans(u)])
    for u, d in zip(us, datas):
        u.pack(d, out)
    if enc:
        engine.patch(out, enc)
        engine.relocate_strings(out, enc.moved)
        engine.move_credits(out)
        gfx.apply(out)
    return out


def apply_edits(us, datas, mark=False, qa=()):
    """Insert every non-empty `en` from script/*.tsv (tools/text.py) into the unpacked units, encoded by the
    English engine (dialogue word-wrapped to 40 letters). mark: replace every text row by its marker
    (tools/marker.py) instead. Returns the engine encoder (its pair codes make the font)."""
    rows = [r for rows in text.load_all().values() for r in rows]
    if mark:
        tags = marker.short_ids(rows)
        for r in rows:
            if r["kind"] == "text":
                r["en"] = marker.marker(r, tags[r["id"]], text.encode, wide=mark == "wide")
    over = dict(q.split("=", 1) for q in qa)
    over_ids = set(over)
    for r in rows:
        if r["id"] in over:
            r["en"] = over.pop(r["id"])
    if over:
        raise SystemExit(f"--qa: unknown ids {sorted(over)}")
    enc = engine.Encoder()
    items = {}
    for r in rows:
        if r["en"] and r["id"] in windows.SJIS and not (mark and r["id"] not in over_ids):
            items[r["id"]] = [text.encode(r["en"])]  # raw bytes pass through Encoder.encode
        elif r["en"]:
            try:
                # marker rows are already sized for their box; only the dialogue marker relies on the wrap
                plain = mark and r["id"] not in over_ids and not r["id"].startswith("dlg:")
                items[r["id"]] = enc.cells(r["en"], **({} if plain else windows.wrap_args(r["id"])))
            except ValueError as e:
                raise SystemExit(f"{r['id']}: {e}")
    enc.assign()

    moved = []  # (old offset, pointer words, bytes): strings longer than their room, written to engine.NEW_STRINGS

    def encode(r, _):
        raw = enc.encode(items[r["id"]])
        if r["id"].startswith(FIXED):  # fixed-width prompts: pad with full-width spaces to the jp's length
            raw += b"\x81\x40" * ((len(text.encode(r["jp"])) - len(raw)) // 2)
        if len(raw) > int(r["max"]) and windows.relocatable(r):
            moved.append((int(r["id"].partition(":")[2], 16), windows.refs(r), raw))
            return b""  # the old place keeps an empty string; no pointer reaches it any more
        return raw

    n = text.apply(us, datas, rows, encoder=encode)
    if n != sum(1 for r in rows if r["en"]):  # every table gets all its English (pipeline.md §Checks)
        raise SystemExit(f"inserted {n} rows, {sum(1 for r in rows if r['en'])} have an en")
    enc.moved = moved
    print(f"text: {n} of {sum(r['kind'] == 'text' for r in rows)} rows {'marked' if mark else 'translated'}, "
          f"{len(enc.code)} letter pairs")
    dlg = next(u for u in us if u.name == "dialogue")
    dlg.relocate(engine.NEW_DIALOGUE, engine.DIALOGUE_SLOT, text.DIALOGUE_MAX)
    return enc


def build(identity=False, mark=False, qa=()):
    orig = ORIG.read_bytes()
    us, datas = unpack(orig)
    enc = None if identity else apply_edits(us, datas, mark, qa)
    return orig, pack(orig, us, datas, enc)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--identity", action="store_true", help="repack with no edits and compare to the original")
    ap.add_argument("--marker", nargs="?", const="jp", choices=("jp", "wide"),
                    help="every text row as [id] marker text -> " + MARK.name + "; jp: each run as long as the "
                    "jp's (dialogue: 3 full lines), wide: every field filled to its byte limit (-> _wide.gba)")
    ap.add_argument("--qa", action="append", default=[], metavar="ID=TEXT",
                    help="override one row's en (stress lines for the width gate; repeatable)")
    ap.add_argument("--out", type=Path, help="output ROM (default build/toyrobo_force_en.gba or _marker.gba)")
    args = ap.parse_args()
    check_rom.check()
    orig, out = build(identity=args.identity, mark=args.marker, qa=args.qa)
    dest = (args.out.resolve() if args.out else MARK.with_name(MARK.stem + "_wide.gba") if args.marker == "wide"
            else MARK if args.marker else OUT)
    if args.identity:
        if bytes(out.data) != orig:
            diff = next(i for i in range(min(len(orig), len(out.data))) if orig[i] != out.data[i])
            print(f"identity FAILED: first difference at {diff:06X}; {len(out.log)} writes changed bytes")
            return 1
        print(f"identity ok: {len(orig)} bytes, byte-identical, sha1 {hashlib.sha1(orig).hexdigest()}")
        return 0
    dest.parent.mkdir(exist_ok=True)
    dest.write_bytes(out.data)
    (dest.parent / (dest.stem + ".writes.tsv" if args.marker else "writes.tsv")).write_text(
        out.writes_text(), encoding="utf-8")
    print(f"{dest.relative_to(ROOT)}: {len(out.data)} bytes, {len(out.log)} writes, "
          f"sha1 {hashlib.sha1(out.data).hexdigest()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
