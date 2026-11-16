"""Translation batches (docs/translator-brief.md): split untranslated text, check translator output, merge it back.

    python -X utf8 tools/batches.py split [--size 3500]   work/tl/bNNN.tsv and build/terms_bNNN.txt for untranslated JP
    python -X utf8 tools/batches.py check [bNNN ...]      a batch's .out.tsv; with no batch, all shipped English (for check.py)
    python -X utf8 tools/batches.py merge bNNN ... [--overwrite]   check, then write the English into script/

Copied from the skill's assets/batches.py; the ADAPTER reads and writes this repo's script/ TSVs (tools/text.py) and
measures width with the build's own wrap and lint (tools/windows.py, tools/lint.py).
Batch TSV: id, speaker, form, limit, JP. Output: work/tl/bNNN.out.tsv, id<TAB>English, every id once, same order.
Rows whose JP repeats an earlier row's JP exactly are batched once; merge copies the English to every copy.
"""
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import lint  # noqa: E402
import text  # noqa: E402
import windows  # noqa: E402

TL = ROOT / "work/tl"
SCRIPT = ROOT / "script"
GLOSSARY = ROOT / "glossary.md"
MAX_ENTRIES = 150

# ---- ADAPTER: this game's text format ----
TOKEN = re.compile(r"\{[^}\n]*\}|%0?\d*[ds]")  # control codes and printf fields; must survive translation
FREE = {"{br}", "{none}"}  # layout codes the English may place freely (the build word-wraps; {none} = empty piece)
VARIABLE = r"%0?\d*d"  # a number the game draws: "1st" comes out as "1th"
HONORIFICS = {"さん": "-san", "くん": "-kun", "ちゃん": "-chan", "君": "-kun", "様": "-sama"}  # checked only right after a katakana name (行くんだ, 保母さん are not)
SPEAKER =re.compile(r"^(?:\{[^}]*\})*([^「{]{1,12})「")


def docs():
    """(path, rows, entries) per script file; entries are the rows themselves (id, kind, where, max, jp, en, notes)."""
    for path in sorted(SCRIPT.rglob("*.tsv")):
        rows = text.loads(path.read_text(encoding="utf-8"), path.name)
        yield path, rows, rows


def needs_english(entry):
    """Empty JP isn't "untranslated": it would be re-queued forever. data rows are never translated."""
    return entry["kind"] == "text" and bool(entry["jp"].strip()) and not entry["en"]


def group_of(entry):
    return entry["id"]


def speaker(entry):
    m = SPEAKER.match(entry["jp"])
    return m[1].strip("　 ") if m else ""


def form(entry):
    return windows.variant(entry["id"])


def limit_label(entry):
    v = windows.VARIANTS[form(entry)]
    shape = f"{v['wrap']}x{v['lines']} " if v["wrap"] else ""
    cap = f" show {v['cap']}" if v["cap"] else ""
    return f"{shape}{entry['max']}B{cap}"


def width_problems(entry, en):
    """The build's own wrap and lint, on this one row."""
    name = "batch"
    return [e.split(": ", 1)[1] for e in lint.errors({name: [dict(entry, en=en)]})]


def encodable(char):
    return " " <= char <= "~"
# ---- end of ADAPTER ----


def kind(char):
    if "぀" <= char <= "ゟ":
        return "hiragana"
    if "゠" <= char <= "ヿ":
        return "katakana"
    if "一" <= char <= "鿿" or char == "々":
        return "kanji"
    return "other"


def has_term(jp, term):
    """term occurs as a whole kana or kanji run: ミン isn't in タイミング, くも isn't in ぼくも."""
    for m in re.finditer(re.escape(term), jp):
        a, b = m.start(), m.end()
        if (a == 0 or kind(jp[a - 1]) != kind(term[0])) and (b == len(jp) or kind(jp[b]) != kind(term[-1])):
            return True
    return False


def glossary():
    """[(JP forms, EN forms, avoid forms)] from glossary.md's | JP | EN | max | notes | Avoid | tables."""
    rows = []
    if not GLOSSARY.exists():
        return rows
    for line in GLOSSARY.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) >= 2 and cells[0] not in ("JP", "") and not set(cells[0]) <= set("-: "):
            avoid = [x.strip() for x in cells[4].split("/") if x.strip()] if len(cells) > 4 else []
            rows.append(([x.strip() for x in cells[0].split("/")], [x.strip() for x in cells[1].split("/")], avoid))
    return rows


def problems(entry, en, terms):
    """Every rule, on one line of English."""
    jp = entry["jp"]
    if not en.strip():
        return ["empty English"]
    if entry.get("id") in windows.SJIS:  # written with the Japanese table; lint checks it
        return width_problems(entry, en)
    out = []
    plain = TOKEN.sub("", en)
    if bad := sorted({c for c in plain if not encodable(c) and c != "\n"}):
        out.append(f"unencodable characters {bad}")
    if re.search(r"\\u[0-9a-fA-F]{4}", en) or "\t" in en or "\n" in en:
        out.append("escape sequence, newline or tab in the English")
    want = Counter(t for t in TOKEN.findall(jp) if t not in FREE)
    have = Counter(t for t in TOKEN.findall(en) if t not in FREE)
    if want != have:
        out.append(f"control codes differ: JP {dict(want)} EN {dict(have)}")
    if re.search(VARIABLE + r"(st|nd|rd|th)\b", en):
        out.append('ordinal suffix after a variable (write "No. %d")')
    jp_plain = TOKEN.sub("", jp)
    for jps, ens, avoid in terms:
        if any(has_term(jp_plain, j) for j in jps) and not any(e.lower() in en.lower() for e in ens):
            out.append(f"glossary: {jps[0]} -> {ens[0]}")
        out += [f"glossary Avoid: {a}" for a in avoid if re.search(rf"\b{re.escape(a)}\b", en)]
    for jp_form, en_form in HONORIFICS.items():
        waived = "no honorific" in (entry.get("notes") or "")  # a row's notes say why it is dropped on purpose
        if re.search(f"[ァ-ヺー]{jp_form}", jp_plain) and en_form.lower() not in en.lower() and not waived:
            out.append(f"honorific {jp_form} needs {en_form} (or note why not in the batch report)")
    return out + width_problems(entry, en)


def index():
    return {e["id"]: e for _, _, entries in docs() for e in entries}


def read_tsv(path):
    return [line.split("\t") for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def existing():
    return sorted(TL.glob("b[0-9][0-9][0-9].tsv"))


def split(size):
    """Numbers on from the last batch and leaves out ids already batched, so a repeat run can't duplicate work."""
    TL.mkdir(parents=True, exist_ok=True)
    (ROOT / "build").mkdir(exist_ok=True)
    taken = {r[0] for p in existing() for r in read_tsv(p)}
    n = max((int(p.stem[1:]) for p in existing()), default=0)
    groups, seen = {}, set()
    for _, _, entries in docs():
        for e in entries:
            if e["kind"] == "text" and e["id"] in taken:
                seen.add((form(e), e["jp"]))
    for _, _, entries in docs():
        for e in entries:
            if needs_english(e) and e["id"] not in taken and (form(e), e["jp"]) not in seen:
                seen.add((form(e), e["jp"]))
                groups.setdefault(group_of(e), []).append(e)
    batches, cur, chars = [], [], 0
    for group in groups.values():
        c = sum(len(TOKEN.sub("", e["jp"])) for e in group)
        if cur and (chars + c > size or len(cur) + len(group) > MAX_ENTRIES
                    or cur[-1]["id"].partition(":")[0] != group[0]["id"].partition(":")[0]):
            batches.append(cur)
            cur, chars = [], 0
        cur += group
        chars += c
    if cur:
        batches.append(cur)
    terms = glossary()
    for batch in batches:
        n += 1
        name = f"b{n:03d}"
        path = TL / f"{name}.tsv"
        if path.exists():
            sys.exit(f"{path} already exists")
        rows = [f"{e['id']}\t{speaker(e)}\t{form(e)}\t{limit_label(e)}\t{e['jp']}" for e in batch]
        path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="\n")
        jps = " ".join(TOKEN.sub("", e["jp"]) for e in batch)
        used = [(j, ens[0]) for jpl, ens, _ in terms for j in jpl if has_term(jps, j)]
        (ROOT / f"build/terms_{name}.txt").write_text("".join(f"{j}\t{e}\n" for j, e in used)
                                                      or "(no glossary terms in this batch)\n", encoding="utf-8", newline="\n")
    print(f"{len(batches)} new batches in {TL}, {len(taken)} ids already batched")


def check_batch(batch, entries, terms):
    want = [r[0] for r in read_tsv(TL / f"{batch}.tsv")]
    rows = [(r[0], "\t".join(r[1:])) for r in read_tsv(TL / f"{batch}.out.tsv")]
    bad = []
    if [r[0] for r in rows] != want:
        got = [r[0] for r in rows]
        dup = sorted(i for i, c in Counter(got).items() if c > 1)
        bad.append(f"ids differ: missing {sorted(set(want) - set(got))[:8]} extra {sorted(set(got) - set(want))[:8]} "
                   f"duplicate {dup[:8]} (order must match too)")
    for eid, en in rows:
        if eid in entries:
            bad += [f"{eid}: {p}: {en!r}" for p in problems(entries[eid], en, terms)]
    return bad, dict(rows)


def merge(new, overwrite):
    """Refuses to replace different English unless told to, before anything is written. English for a row also goes
    to every untranslated row with the same JP (they were batched once)."""
    entries = index()
    by_jp = {(form(entries[i]), entries[i]["jp"]): en for i, en in new.items() if i in entries}
    if not overwrite:
        for _, _, rows in docs():
            for e in rows:
                if e["id"] in new and e["en"] and e["en"] != new[e["id"]]:
                    sys.exit(f"{e['id']} would lose {e['en']!r}: pass --overwrite if that is meant")
    changed = 0
    for path, rows, _ in docs():
        touched = False
        for e in rows:
            en = new.get(e["id"]) or (not e["en"] and e["kind"] == "text" and by_jp.get((form(e), e["jp"])))
            if en and e["en"] != en:
                e["en"] = en
                touched = True
                changed += 1
        if touched:
            path.write_text(text.dumps(rows), encoding="utf-8", newline="\n")
    print(f"merged: {changed} entries changed")


def main(argv):
    if not argv:
        sys.exit(__doc__)
    cmd, args = argv[0], argv[1:]
    if cmd == "split":
        return split(int(args[args.index("--size") + 1]) if "--size" in args else 3500)
    overwrite = "--overwrite" in args
    names = [a for a in args if a != "--overwrite"]
    entries, terms = index(), glossary()
    if cmd == "check" and not names:
        bad = [f"{i}: {p}: {e['en']!r}" for i, e in entries.items() if e["en"] for p in problems(e, e["en"], terms)]
        print(f"{len(entries)} entries, {len(bad)} problems")
        print("\n".join(bad[:200]))
        return 1 if bad else 0
    if cmd not in ("check", "merge") or not names:
        sys.exit(__doc__)
    new, failed = {}, 0
    for batch in names:
        bad, rows = check_batch(batch, entries, terms)
        new.update(rows)
        failed += bool(bad)
        print(f"{batch}: " + ("OK" if not bad else f"{len(bad)} problems"))
        for line in bad:
            print("  " + line)
    if failed:
        return 1
    if cmd == "merge":
        merge(new, overwrite)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
