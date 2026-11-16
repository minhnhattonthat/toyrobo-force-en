"""Phase 4: script/*.tsv is a complete, byte-exact dump of the original ROM's text.

- the table file is what tools/make_jp_tbl.py generates;
- the committed TSVs match a fresh dump (ids, kind, where, max, jp);
- roundtrip: every row's jp encodes to the original bytes, and a build that inserts every jp as if it were the
  translation gives the original ROM byte for byte;
- coverage: every text field of every text unit has exactly one row, and no Japanese-looking run outside the
  owned ranges is left except the waived non-text ranges below.
"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import build  # noqa: E402
import make_jp_tbl  # noqa: E402
import sjis_scan  # noqa: E402
import text  # noqa: E402
import units  # noqa: E402

ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"

# Runs that look like Japanese outside every owned range, checked by hand in phase 4 (hex dumps): all are
# 16-bit tile-map / palette / table words that happen to fall in the Shift-JIS range, none is read as text.
WAIVED = [
    (0x012580, 0x0125A0, "Thumb code"),
    (0x089CD0, 0x08CB80, "graphics data (repeated ヨ / ャ words)"),
    (0x0DF260, 0x0DF270, "tile pixel data"),
    (0x1A5690, 0x1A5EB0, "tile-map words (ビＳ pattern)"),
    (0x1B8840, 0x1BFC60, "tile-map words"),
    (0x1CD980, 0x1F8B90, "tile-map words (ヽヾゝゞ patterns)"),
    (0x2067C0, 0x206810, "tile-map words (チЯ pattern)"),
    (0x23CD30, 0x242000, "tile-map words (0x82xx / 0x52xx map entries)"),
    (0x363980, 0x363C00, "tile-map words"),
]


@unittest.skipUnless(ROM.is_file(), "needs the original ROM in rom/")
class TestExtract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig = ROM.read_bytes()
        cls.files = text.load_all()
        cls.rows = [r for rows in cls.files.values() for r in rows]

    def test_table_current(self):
        self.assertEqual(text.TABLE.read_text(encoding="utf-8"), make_jp_tbl.text())

    def test_tsv_matches_fresh_dump(self):
        fresh = text.extract(self.orig)
        self.assertEqual(sorted(fresh), sorted(self.files))
        keys = ("id", "kind", "where", "max", "jp")
        for name, rows in fresh.items():
            self.assertEqual([[r[k] for k in keys] for r in rows],
                             [[r[k] for k in keys] for r in self.files[name]], name)

    def test_ids_unique(self):
        ids = [r["id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_codec_roundtrip_every_field(self):
        us = units.make_units()
        datas = {u.name: u.unpack(self.orig) for u in us}
        raws = list(datas["dialogue"])
        raws += [r["text"] for t in (*text.TABLES, "choices") for r in datas[t] if "text" in r]
        raws += [s for name in text.REGIONS for _, s in datas[name]]
        for raw in raws:
            self.assertEqual(text.encode(text.decode(raw)), raw, raw)

    def test_insert_jp_is_identity(self):
        us, datas = build.unpack(self.orig)
        n = text.apply(us, datas, [r for r in self.rows if r["kind"] == "text"], field="jp")
        self.assertEqual(n, sum(r["kind"] == "text" for r in self.rows))
        self.assertEqual(bytes(build.pack(self.orig, us, datas).data), self.orig)

    def test_every_field_has_a_row(self):
        us = units.make_units()
        datas = {u.name: u.unpack(self.orig) for u in us}
        want = len(datas["dialogue"])
        want += sum("text" in r for t in (*text.TABLES, "choices") for r in datas[t])
        want += sum(len(datas[name]) for name in text.REGIONS)
        self.assertEqual(len(self.rows), want)

    def test_no_text_outside_owned_ranges(self):
        us = units.make_units()
        for u in us:
            u.unpack(self.orig)
        owned = sorted(s for u in us for s in units.spans(u)) + [(a, b) for a, b, _ in WAIVED]
        chars = set("".join(r["jp"] for r in self.rows))
        left = []
        for a, b, *_ in sjis_scan.runs(self.orig, 2):
            if any(s <= a and b <= e for s, e in owned):
                continue
            t = self.orig[a:b].decode("cp932", "replace")
            kana = sum("ぁ" <= c <= "ヿ" for c in t)
            textlike = kana >= 3 and 2 * kana >= len(t)
            textlike |= all(c in chars for c in t) and len(set(t)) > 1 and 0 in (self.orig[b], self.orig[a - 1])
            if textlike:
                left.append(f"{a:06X} {t[:30]}")
        self.assertEqual(left, [])

    def test_lint(self):
        import lint
        self.assertEqual(lint.errors(self.files), [])
        row = dict(self.files["dialogue/s01.tsv"][1])
        bad = [dict(row, en="{spk:02}Poyack: Line up!{wait}"),       # lost {face}
               dict(row, en="{face:10402}{spk:02}Poyack: Line up!{wait} "),  # trailing blank
               dict(row, en="{face:10402}{spk:02}{bogus}{wait}"),     # unknown control
               dict(self.files["strings.tsv"][0], kind="data", en="x")]
        self.assertEqual(len(lint.errors({"t": bad})), 4)

    def test_apply_en(self):
        us, datas = build.unpack(self.orig)
        rows = [dict(r) for r in self.files["dialogue/s01.tsv"][:1]]
        rows[0]["en"] = "{face:10402}{spk:02}Hello{wait}"
        text.apply(us, datas, rows)
        out = build.pack(self.orig, us, datas)
        slot = int(rows[0]["id"].split(":")[1])
        base = 0x397070 + slot * 0x80
        self.assertEqual(bytes(out.data[base:base + 18]), b"#210402#502Hello#4")
        data = [dict(r, en="x") for r in self.rows if r["kind"] == "data"][:1]
        self.assertTrue(data)
        with self.assertRaises(ValueError):
            text.apply(us, datas, data)


if __name__ == "__main__":
    unittest.main()
