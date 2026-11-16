"""List rows of one speaker: id | jp body | en body. usage: voice.py SPEAKER_RE [OUT]"""
import re, sys, csv
from pathlib import Path
sys.path.insert(0, "tools")
from tl_body import parts

pat = re.compile(sys.argv[1])
out = []
for f in sorted(Path("script/dialogue").glob("*.tsv")):
    lines = f.read_text(encoding="utf-8").splitlines()
    hdr = lines[0].split("\t")
    cont = False
    for line in lines[1:]:
        r = dict(zip(hdr, line.split("\t")))
        lead, body, tail = parts(r["jp"])
        hit = pat.match(body) or (cont and "「" not in body)
        if pat.match(body):
            cont = "」" not in body
        elif cont:
            cont = "」" not in body and "「" not in body
        if hit:
            e = parts(r["en"])[1] if r.get("en") else ""
            out.append(f"{r['id']}\t{body}\t{e}")
text = "\n".join(out) + "\n"
if len(sys.argv) > 2:
    Path(sys.argv[2]).write_text(text, encoding="utf-8")
print(len(out))
