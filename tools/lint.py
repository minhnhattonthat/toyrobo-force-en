"""lint.py: text lint over script/*.tsv (tools/check.py runs it). Exit 1 on any error.

Checks every row with an `en`:
- kind must be text (data rows are never translated);
- `en` encodes with the English engine (tools/engine.py: every letter has a glyph, no unknown {control}) and the
  encoded bytes fit `max` (dialogue after its word wrap to 40 letters per line);
- the control codes {spk:NN}, {face:NNNNN} and {wait} and printf formats match the jp's, in order;
- no leading or trailing space (layout is the wrap's job; fixed-width prompts are padded by the build), except a
  leading alignment cell where the jp starts with a full-width space;
- full-width spaces next to a %d/%s (number columns) take as many cells in the English (align_errors);
- no wrapped paragraph ends on a stub line shorter than STUB letters (the build's balanced wrap avoids them).
Box line counts and per-variant widths: docs/re/font.md (width gate).
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import engine  # noqa: E402
import text  # noqa: E402
import windows  # noqa: E402

CODES = re.compile(r"\{(?:spk:\d\d|face:\d{5}|wait)\}|%0?\d*[ds]")


def errors(files):
    out = []
    for name, rows in files.items():
        for r in rows:
            en, jp = r["en"], r["jp"]
            if not en:
                continue
            where = f"script/{name} {r['id']}"
            if r["kind"] != "text":
                out.append(f"{where}: kind {r['kind']} must not have an en")
                continue
            if r["id"] in windows.SJIS:  # Japanese-table row: same byte length as the jp, digits where the jp's are
                raw, orig = text.encode(en), text.encode(jp)
                if len(raw) != len(orig) or any(raw[i:i + 2] != orig[i:i + 2]
                                                for i in range(0, len(orig), 2) if orig[i:i + 2] == b"\x82\x4f"):
                    out.append(f"{where}: must keep the jp's length and its full-width 0 digits in place")
                continue
            enc = engine.Encoder()
            v = windows.VARIANTS[windows.variant(r["id"])]
            try:
                items = enc.cells(en, **windows.wrap_args(r["id"]))
                enc.assign()
                n = len(enc.encode(items))
                if n > int(r["max"]) and windows.relocatable(r):  # the build moves it; the screen is the limit
                    cap = windows.RELOC_CAP[r["id"].partition(":")[0]]
                    wide = max(engine._width(re.sub(r"%s", "s" * 18, re.sub(r"%0?\d*d", "d" * 5, line)))
                               for line in en.split("{br}"))
                    if wide > cap:
                        out.append(f"{where}: a line of {wide} letters (a %s counts 18, a %d 5), screen {cap}")
                elif n > int(r["max"]):
                    out.append(f"{where}: {n} bytes, max {r['max']}")
                if v["cap"] and n > v["cap"]:
                    out.append(f"{where}: {n} letters, the {windows.variant(r['id'])} window shows {v['cap']}")
                if v["wrap"] and windows.lines_used(items, v["wrap"]) > v["lines"]:
                    out.append(f"{where}: {windows.lines_used(items, v['wrap'])} lines, window has {v['lines']}")
            except (ValueError, KeyError) as e:
                out.append(f"{where}: {e}")
            if CODES.findall(en) != CODES.findall(jp):
                out.append(f"{where}: control codes {CODES.findall(en)} != jp {CODES.findall(jp)}")
            # a credits piece drawn right after another on the same line starts with the space between them;
            # a row whose jp starts with a full-width space keeps it as an alignment cell (checked below)
            if en != en.strip(" ") and not (r["id"].startswith("credits:") and en == " " + en.strip(" ")) \
                    and not (jp.startswith("　") and en == en.rstrip(" ")):
                out.append(f"{where}: leading or trailing space")
            out += [f"{where}: {e}" for e in align_errors(en, jp)]
            wrap = windows.wrap_args(r["id"]).get("wrap")
            if wrap and en != engine.NONE:
                for p in en.split("{br}"):
                    lines = engine.para_lines(p, wrap)[1]
                    if len(lines) > 1 and len(lines[-1].strip()) < STUB:
                        out.append(f"{where}: stub last line {lines[-1]!r} (balance the paragraph)")
    return out


STUB = 6  # a wrapped paragraph's last line shorter than this reads as a widow


def _cells(s):
    return (len(s) + 1) // 2


def align_errors(en, jp):
    """Full-width spaces next to a token in the jp line numbers up in a column (the save list's "Log %d　　%d:..",
    "Power　%d"): each such run of k spaces must add exactly k cells to the English too. An English run is padded
    to a whole cell (Encoder._run), so one space is not one cell: k cells are 2k spaces at the start of a run, or
    the end of a run that takes k cells more than the run with one separating space ("Power " 3 cells,
    "Power   " 4)."""
    js, es = engine.TOKEN.split(jp), engine.TOKEN.split(en)
    toks = [""] + engine.TOKEN.findall(jp) + [""]
    if len(js) != len(es) or toks[1:-1] != engine.TOKEN.findall(en):
        return []
    out = []
    for i, (j, e) in enumerate(zip(js, es)):
        before, after = toks[i].startswith("%"), toks[i + 1].startswith("%")  # a printf number or name
        if "　" not in j or e == engine.NONE or not (before or after):
            continue
        if j.strip("　") == "":  # a whole run of spaces: a column gap only between two values
            if before and after and e !=" " * (2 * len(j)):
                out.append(f"{len(j)} full-width spaces between tokens need {2 * len(j)} spaces, not {e!r}")
            continue
        k = (len(j) - len(j.lstrip("　"))) * before
        if k and e[:2 * k + 1] != " " * (2 * k) + e[2 * k:2 * k + 1].strip():
            out.append(f"jp starts a run with {k} full-width space(s): en {e!r} must start with {2 * k} spaces")
        k = (len(j) - len(j.rstrip("　"))) * after
        if k and not (e.endswith(" " * (2 * k)) and _cells(e) - _cells(e.rstrip(" ") + " ") == k):
            out.append(f"jp ends a run with {k} full-width space(s): en {e!r} must end with {k} more cell(s)")
    return out


def main():
    if not text.SCRIPT_DIR.is_dir():
        return 0
    errs = errors(text.load_all())
    for e in errs:
        print(e)
    print(f"lint: {len(errs)} errors")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
