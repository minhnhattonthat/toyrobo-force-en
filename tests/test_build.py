"""Phase 7 ROM-level checks on a fresh English build (references/pipeline.md §Checks).

- every changed byte has a logged write whose original bytes match the original ROM, no write overlaps another
  (romdiff.check), and every write lands in an allowed range: a unit's span, the expansion past the original ROM,
  an engine literal or credits position, or a pointer word of a relocated string;
- every relocated string: each of its pointer words now points at the encoded English, NUL-terminated, and no other
  aligned word in the original ROM pointed at the old address (no reader left behind);
- every table the build writes gets all its English: the count inserted equals the rows with an `en`.
"""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import engine  # noqa: E402
import gfx  # noqa: E402
import romdiff  # noqa: E402
import strmap  # noqa: E402
import text  # noqa: E402
import units  # noqa: E402


@unittest.skipUnless(build.ORIG.is_file(), "rom/ missing")
class BuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig = build.ORIG.read_bytes()
        us, datas = build.unpack(cls.orig)
        cls.enc = build.apply_edits(us, datas)
        cls.out = build.pack(cls.orig, us, datas, cls.enc)
        cls.new = bytes(cls.out.data)
        cls.spans = [s for u in us for s in units.spans(u)]

    def writes(self):
        for line in self.out.log:
            off, o, n, who = line.split(None, 3)
            yield int(off, 16), bytes.fromhex(o), bytes.fromhex(n), who

    def test_romdiff_clean(self):
        errs, _ = romdiff.check(self.orig, self.new, set(), list(self.writes()))
        self.assertEqual(errs, [])

    def test_writes_in_allowed_ranges(self):
        allowed = list(self.spans) + [(len(self.orig), engine.ROM_SIZE)]
        lits = [engine.LIT_DIALOGUE_SHIFT, engine.LIT_DIALOGUE_BASE, engine.LIT_FONT_HI, engine.LIT_FONT_BASE,
                *engine.LIT_FONT_GLYPH]
        allowed += [(o, o + 4) for o in lits] + [(o, o + 2) for o, *_ in engine.CREDIT_POS]
        allowed += [(ref, ref + 4) for _, refs, _ in self.enc.moved for ref in refs]
        allowed += gfx.spans()  # graphics-text tile blocks (tools/gfx.py)
        bad =[f"{off:06X} {who}" for off, o, _, who in self.writes()
               if not any(lo <= off and off + len(o) <= hi for lo, hi in allowed)]
        self.assertEqual(bad, [])

    def test_pause_panel(self):
        """Issue #1: the battle pause panel and flee prompt maps point only at redrawn word tiles or the fill tile,
        and the fill tile itself is untouched."""
        drawn = {(c - gfx.PAUSE_CHR) // 32 for row in gfx.GROUPS["pause"]["grid"] for c in row if c is not None}
        fill = gfx._pt(0xDF)
        self.assertEqual(self.new[fill:fill + 32], self.orig[fill:fill + 32])
        for off, _, new in gfx.PAUSE_MAPS:
            self.assertEqual(self.new[off:off + 20], gfx._prow(*new))
            self.assertLessEqual(set(new) - {0xDF}, drawn)
        for t in drawn:  # every word tile was redrawn (no kana left)
            self.assertNotEqual(self.new[gfx._pt(t):gfx._pt(t) + 32], self.orig[gfx._pt(t):gfx._pt(t) + 32],
                                f"tile {t:02X}")

    def test_arrest_burst(self):
        """Issue #1: the in-battle タイホ! burst (LZ 0x1179D4, tiles 0x189-0x18A / 0x1A9-0x1AA) is redrawn."""
        import gbacomp
        old, new = gbacomp.decompress(self.orig, 0x1179D4)[0], gbacomp.decompress(self.new, 0x1179D4)[0]
        for t in (0x189, 0x18A, 0x1A9, 0x1AA):
            self.assertNotEqual(old[t * 32:t * 32 + 32], new[t * 32:t * 32 + 32], f"tile {t:03X}")

    def test_relocated_strings(self):
        self.assertTrue(self.enc.moved, "nothing relocated: the credits and D12 labels need it")
        words = {}
        for a in range(0, len(self.orig) - 3, 4):
            words.setdefault(struct.unpack_from("<I", self.orig, a)[0], []).append(a)
        for old, refs, raw in self.enc.moved:
            stale = sorted(set(words.get(engine.ROM_BASE + old, [])) - set(refs))
            self.assertEqual(stale, [], f"{old:06X}: pointer words the build did not rewrite")
            self.assertTrue(refs, f"{old:06X}: relocated with no pointer word to rewrite")
            self.assertEqual(self.new[old], 0, f"{old:06X}: old place not left as an empty string")
            for ref in refs:
                ptr = struct.unpack_from("<I", self.new, ref)[0] - engine.ROM_BASE
                self.assertGreaterEqual(ptr, engine.NEW_STRINGS)
                self.assertLess(ptr + len(raw), engine.ROM_SIZE)
                self.assertEqual(self.new[ptr:ptr + len(raw) + 1], raw + b"\0", f"{old:06X} via {ref:06X}")
        # no two relocated strings share bytes in the new area
        spans = sorted((struct.unpack_from("<I", self.new, refs[0])[0] - engine.ROM_BASE, len(raw) + 1)
                       for _, refs, raw in self.enc.moved)
        for (a, n), (b, _) in zip(spans, spans[1:]):
            self.assertLessEqual(a + n, b, f"relocated strings overlap at {a:06X}/{b:06X}")

    def test_kept_japanese(self):
        # Rows deliberately left without English (KEEP_JP); any other empty `en` is an untranslated row.
        KEEP_JP = {"credits:249170"}  # a lone ♪, drawn by the original font glyph
        rows = [r for rs in text.load_all().values() for r in rs if r["kind"] == "text"]
        self.assertEqual({r["id"] for r in rows if not r["en"]}, KEEP_JP)

    def test_string_map(self):
        # build/strings.tsv (text coverage): one address per text row, each holding that row's encoded first bytes
        rows = [r for rs in text.load_all().values() for r in rs]
        pairs = strmap.addresses(self.new, rows)
        self.assertEqual(len(pairs), sum(r["kind"] == "text" for r in rows))
        moved = {engine.ROM_BASE + engine.NEW_STRINGS <= a for _, a in pairs}
        self.assertEqual(moved, {False, True})  # relocated strings follow their pointer
        empty = {r["id"] for r in rows if r["en"] == "{none}"}  # deliberately blank (credits:2490B0)
        for rid, a in pairs:
            if rid not in empty:
                self.assertNotIn(self.new[a - engine.ROM_BASE], (0x00, 0xFF), rid)

    def test_every_dialogue_row_inserted(self):
        # (apply_edits itself refuses a run where fewer rows were inserted than have an `en`)
        for r in (r for rs in text.load_all().values() for r in rs if r["en"] and r["id"].startswith("dlg:")):
            slot = engine.NEW_DIALOGUE + int(r["id"][4:]) * engine.DIALOGUE_SLOT
            self.assertNotEqual(self.new[slot:slot + 2], b"\xff\xff", r["id"])


if __name__ == "__main__":
    unittest.main()
