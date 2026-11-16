"""text.py: the game's text as rows (extract, TSV files in script/, insertion into the unpacked units).

Codec: tbl/jp.tbl through tools/tbl.py, with the digit arguments of `#5` / `#2` folded into the token:
`#510` <-> `{spk:10}`, `#212345` <-> `{face:12345}`, `#0` <-> `{br}`, `#4` <-> `{wait}`. Bytes the table lacks
decode as `[XX]` and encode back, so decode -> encode is byte-exact (tests/test_extract.py).

Rows (one per text field the build owns; tools/extract.py writes them, build.py applies `en`):
    id      stable, address-based: dlg:<slot>, <table>:<record>, choice:<record>, <region>:<rom offset hex>
    kind    text, or data (decodes as text but is not: never translated, lint refuses an `en`)
    where   what reads it: dialogue `rec:<script record>`, strings `ref:<offsets of the pointer words>`
    max     bytes available in place (field width - 1, slot 127, or room up to the next string)
    jp      original text (tokens as above)
    en      translation; empty = keep the original bytes
    notes   free text

Files: script/dialogue/sNN.tsv (one per script section, prelude in s00), script/tables.tsv (names, parts,
items, descriptions), script/choices.tsv, script/strings.tsv (credits, status/save strings, battle prompts).
"""
import re
import struct
from pathlib import Path

import tbl
import units

ROOT = Path(__file__).resolve().parents[1]
SCRIPT_DIR = ROOT / "script"
TABLE = ROOT / "tbl" / "jp.tbl"
COLUMNS = ("id", "kind", "where", "max", "jp", "en", "notes")

_table = None


def table():
    global _table
    if _table is None:
        _table = tbl.Table.load(TABLE)
    return _table


_FOLD = re.compile(r"\{(spk)\}(\d\d)|\{(face)\}(\d{5})")
_UNFOLD = re.compile(r"\{(spk):(\d\d)\}|\{(face):(\d{5})\}")


def decode(raw):
    text, _ = table().decode(raw, 0, len(raw))
    return _FOLD.sub(lambda m: f"{{{m[1] or m[3]}:{m[2] or m[4]}}}", text)


def encode(text):
    return table().encode(_UNFOLD.sub(lambda m: f"{{{m[1] or m[3]}}}{m[2] or m[4]}", text))


# Entries in the string regions that decode as text but are not (found in phase 4, docs/re/text.md).
DATA = {
    "strings:2492E7": "binary data read by code at 0x95C4, not text",
    "strings:2494DC": "debug random-number table (its own text says so) interleaved with test text; read as bytes",
    "strings:24956C": "save signature 'toyroboforce', compared byte for byte by the save code",
}
TABLES = ("names", "parts_a", "parts_b", "items_a", "items_b", "descs")
REGIONS = ("credits", "strings", "swap", "prompts")
# Dialogue limit: the engine (tools/engine.py) moves the slots to 256 bytes, but the msg opcode copies a slot into
# a 150-byte buffer (0x030026C0, strcpy at 0x0800B1A8), so 149 bytes + NUL.
DIALOGUE_MAX = 149
REGION_NOTES = {
    "swap": "fixed width: pad with full-width spaces to the original length",
    "prompts": "fixed width: pad with full-width spaces to the original length",
}


def _ptr_refs(rom, lo, hi):
    """{target file offset: [offsets of u32 words pointing at it]} for every 2-aligned ROM word into [lo, hi)."""
    refs = {}
    for i in range(0, len(rom) - 3, 2):
        v = struct.unpack_from("<I", rom, i)[0] - units.ROM_BASE
        if lo <= v < hi:
            refs.setdefault(v, []).append(i)
    return refs


def _row(id_, where, max_, jp, kind="text", notes=""):
    return {"id": id_, "kind": kind, "where": where, "max": str(max_), "jp": jp, "en": "", "notes": notes}


def extract(rom):
    """All rows from the original ROM, as {file name relative to script/: [row dicts]}."""
    us = units.make_units()
    datas = {u.name: u.unpack(rom) for u in us}
    by = {u.name: u for u in us}
    files = {}

    # dialogue: slot -> the msg record that shows it and its section
    section, rec_of, sec_of = 0, {}, {}
    for n, r in enumerate(datas["script"]):
        if r[0] == 40:
            section = r[1]
        elif r[0] == 15:
            rec_of.setdefault(r[4], n)
            sec_of.setdefault(r[4], section)
    for k, raw in enumerate(datas["dialogue"]):
        where = f"rec:{rec_of[k]}" if k in rec_of else ""
        name = f"dialogue/s{sec_of.get(k, 0):02d}.tsv"
        files.setdefault(name, []).append(_row(f"dlg:{k:04d}", where, DIALOGUE_MAX, decode(raw)))

    rows = []
    for t in TABLES:
        u = by[t]
        for k, r in enumerate(datas[t]):
            if "text" in r:
                rows.append(_row(f"{t}:{k}", f"@{u.base + k * u.size:06X}", u.width - 1, decode(r["text"])))
    files["tables.tsv"] = rows

    u = by["choices"]
    files["choices.tsv"] = [
        _row(f"choice:{k}", f"@{u.base + k * u.size:06X}", u.width - 1, decode(r["text"]))
        for k, r in enumerate(datas["choices"]) if "text" in r]

    rows = []
    for name in REGIONS:
        u = by[name]
        refs = _ptr_refs(rom, u.lo, u.hi)
        strs = datas[name]
        for i, (off, raw) in enumerate(strs):
            nxt = strs[i + 1][0] if i + 1 < len(strs) else u.hi
            id_ = f"{name}:{off:06X}"
            where = "ref:" + ",".join(f"{r:06X}" for r in refs.get(off, []))
            kind = "data" if id_ in DATA else "text"
            rows.append(_row(id_, where, nxt - off - 1, decode(raw), kind, DATA.get(id_, REGION_NOTES.get(name, ""))))
    files["strings.tsv"] = rows
    return files


def dumps(rows):
    out = ["\t".join(COLUMNS)]
    for r in rows:
        for c in COLUMNS:
            if any(ch in r[c] for ch in "\t\r\n"):
                raise ValueError(f"{r['id']}: tab or newline in {c}")
        out.append("\t".join(r[c] for c in COLUMNS))
    return "\n".join(out) + "\n"


def loads(text, name="?"):
    lines = text.split("\n")
    if lines[0].lstrip("﻿").rstrip("\r") != "\t".join(COLUMNS):
        raise ValueError(f"{name}: header must be {COLUMNS}")
    rows = []
    for n, line in enumerate(lines[1:], 2):
        line = line.rstrip("\r")
        if not line:
            continue
        cells = line.split("\t")
        if len(cells) != len(COLUMNS):
            raise ValueError(f"{name}:{n}: {len(cells)} columns, want {len(COLUMNS)}")
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def load_all(root=SCRIPT_DIR):
    """{file name relative to script/: rows} for every TSV under script/."""
    return {p.relative_to(root).as_posix(): loads(p.read_text(encoding="utf-8"), p.name)
            for p in sorted(root.rglob("*.tsv"))}


def apply(us, datas, rows, field="en", encoder=None):
    """Write each row's `field` (when non-empty) into the unpacked unit data in place. Returns the count.
    `encoder(row, text) -> bytes` (default: the Japanese table, `encode`); build.py passes the English engine's."""
    idx = {u.name: i for i, u in enumerate(us)}
    region_pos = {}
    n = 0
    for r in rows:
        text = r[field]
        if not text:
            continue
        if r["kind"] != "text":
            raise ValueError(f"{r['id']}: kind {r['kind']} must not be translated")
        raw = encoder(r, text) if encoder else encode(text)
        if len(raw) > int(r["max"]):
            raise ValueError(f"{r['id']}: {len(raw)} bytes, max {r['max']}")
        unit, _, key = r["id"].partition(":")
        if unit == "dlg":
            datas[idx["dialogue"]][int(key)] = raw
        elif unit == "choice":
            datas[idx["choices"]][int(key)]["text"] = raw
        elif unit in TABLES:
            datas[idx[unit]][int(key)]["text"] = raw
        elif unit in REGIONS:
            strs = datas[idx[unit]]
            pos = region_pos.setdefault(unit, {off: i for i, (off, _) in enumerate(strs)})
            off = int(key, 16)
            strs[pos[off]] = (off, raw)
        else:
            raise ValueError(f"{r['id']}: unknown unit")
        n += 1
    return n
