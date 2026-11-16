"""Make work/tl/BNNN.tsv from the ids in BNNN.body.tsv, copying rows from the original batch files."""
import sys
from pathlib import Path
tl = Path("work/tl")
b = sys.argv[1]
want = [l.split("\t")[0] for l in (tl / f"{b}.body.tsv").read_text(encoding="utf-8").splitlines() if l.strip()]
rows = {}
for f in sorted(tl.glob("b0*.tsv")):
    if f.name.count(".") > 1:
        continue
    for l in f.read_text(encoding="utf-8").splitlines():
        p = l.split("\t")
        if p and p[0] in want and p[0] not in rows:
            rows[p[0]] = l
print("missing", [w for w in want if w not in rows])
(tl / f"{b}.tsv").write_text("".join(rows[w] + "\n" for w in want if w in rows), encoding="utf-8")
