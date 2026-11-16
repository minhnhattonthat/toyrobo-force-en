"""lint.py: text lint over script/*.tsv (tools/check.py runs it). Exit 1 on any error.

Checks every row with an `en`:
- kind must be text (data rows are never translated);
- `en` encodes with the table (no unencodable character, no unknown {control});
- the control codes {spk:NN}, {face:NNNNN} and {wait} match the jp's, in order;
- leading and trailing blanks (half- or full-width spaces) match the jp's.
Byte limits are checked by the pack itself (overlong text is refused); width/overflow lint comes with phase 5.
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import text  # noqa: E402

CODES = re.compile(r"\{(?:spk:\d\d|face:\d{5}|wait)\}")
BLANKS = " 　"


def _edge(s):
    return len(s) - len(s.lstrip(BLANKS)), len(s) - len(s.rstrip(BLANKS))


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
            try:
                text.encode(en)
            except ValueError as e:
                out.append(f"{where}: {e}")
            if CODES.findall(en) != CODES.findall(jp):
                out.append(f"{where}: control codes {CODES.findall(en)} != jp {CODES.findall(jp)}")
            if _edge(en) != _edge(jp):
                out.append(f"{where}: leading/trailing blanks {_edge(en)} != jp {_edge(jp)}")
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
