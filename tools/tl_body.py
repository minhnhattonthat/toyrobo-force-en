"""tl_body.py: translate a batch by its text body only; the leading {face}/{spk} run and trailing {wait} run are
put back from the JP.

    python -X utf8 tools/tl_body.py view bNNN        id | body, {br} shown as " / ", ids marked * when the body keeps
                                                     codes the English must carry too
    python -X utf8 tools/tl_body.py wrap bNNN        work/tl/bNNN.body.tsv (id<TAB>English body) -> bNNN.out.tsv
    python -X utf8 tools/tl_body.py set bNNN FIX     replace body rows by id from FIX (id<TAB>English body)

A body line that starts with "{" is taken as the full row (codes and all) and copied unchanged.
"""
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TL = ROOT / "work/tl"
LEAD = re.compile(r"^(?:\{(?:spk:\d\d|face:\d{5})\})*")
TAIL = re.compile(r"(?:\{wait\})*$")


def parts(jp):
    lead = LEAD.match(jp).group(0)
    rest = jp[len(lead):]
    tail = TAIL.search(rest).group(0)
    return lead, rest[:len(rest) - len(tail)], tail


def rows(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def view(batch):
    for r in rows(TL / f"{batch}.tsv"):
        _, body, _ = parts(r[4])
        mark = "*" if re.search(r"\{(?!br\})", body) else ""
        shown = re.sub(r"\{br\}[　 ]*", " / ", body)
        print(f"{r[0]}{mark} {r[2][0]} {shown}")


def wrap(batch):
    jp = {r[0]: r[4] for r in rows(TL / f"{batch}.tsv")}
    out = []
    for r in rows(TL / f"{batch}.body.tsv"):
        eid, en = r[0], "\t".join(r[1:]).strip()
        if en.startswith("{"):
            out.append(f"{eid}\t{en}")
            continue
        lead, _, tail = parts(jp[eid])
        out.append(f"{eid}\t{lead}{en}{tail}")
    (TL / f"{batch}.out.tsv").write_text("\n".join(out) + "\n", encoding="utf-8", newline="\n")
    print(f"{batch}: {len(out)} rows -> {batch}.out.tsv")


def setrows(batch, fixfile):
    """Replace body rows by id from a fix file (id<TAB>English body lines)."""
    fix = {r[0]: "\t".join(r[1:]) for r in rows(Path(fixfile))}
    path = TL / f"{batch}.body.tsv"
    old = rows(path)
    if missing := set(fix) - {r[0] for r in old}:
        sys.exit(f"not in {path.name}: {sorted(missing)}")
    path.write_text("".join(f"{r[0]}\t{fix.get(r[0], chr(9).join(r[1:]))}\n" for r in old), encoding="utf-8",
                    newline="\n")
    print(f"{batch}: {len(fix)} rows replaced")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    cmd, batch = sys.argv[1], sys.argv[2]
    if cmd == "set":
        setrows(batch, sys.argv[3])
    else:
        {"view": view, "wrap": wrap}[cmd](batch)
