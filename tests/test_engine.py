"""The English engine (tools/engine.py, docs/re/font.md): glyphs, encoder, font table, ROM patches."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import engine  # noqa: E402
import font_en  # noqa: E402
import marker  # noqa: E402
import text  # noqa: E402

ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"


class Glyphs(unittest.TestCase):
    def test_widths(self):
        for ch, rows in font_en.GLYPHS.items():
            self.assertEqual(len(rows), font_en.HEIGHT, ch)
            self.assertTrue(all(0 <= r < 1 << font_en.WIDTH for r in rows), ch)

    def test_torture_set(self):
        for ch in "".join(chr(c) for c in range(0x20, 0x7F)):
            if ch not in "{}\\|^`":  # { } are token syntax; the rest never occur in the script
                self.assertIn(ch, font_en.GLYPHS)


class Encoder(unittest.TestCase):
    def enc(self, s, wrap=None):
        e = engine.Encoder()
        items = e.cells(s, wrap)
        e.assign()
        return e, items, e.encode(items)

    def test_one_byte_per_letter_and_padding(self):
        _, items, raw = self.enc("Hello")
        self.assertEqual(items, ["He", "ll", "o "])
        self.assertEqual(len(raw), 6)

    def test_codes_are_safe(self):
        for c in engine._codes():
            hi, lo = c >> 8, c & 0xFF
            self.assertTrue(0xE0 <= hi <= 0xFC and 0x40 <= lo <= 0xFC and lo != 0x7F)

    def test_tokens_pass_through(self):
        _, items, raw = self.enc("{face:10402}{spk:02}Hi!{wait}")
        self.assertEqual(raw[:11], b"#210402#502")
        self.assertTrue(raw.endswith(b"#4"))
        _, _, raw = self.enc("Life: %d")
        self.assertTrue(raw.endswith(b"%d"))

    def test_space_pair_is_fullwidth_space(self):
        _, _, raw = self.enc("A   B")
        self.assertIn(b"\x81\x40", raw)

    def test_wrap_full_line_has_no_br(self):
        line = "x" * 40
        _, items, raw = self.enc(line + " " + "y" * 10, wrap=40)
        self.assertNotIn(b"#0", raw)
        _, items, raw = self.enc("short words here and a few more words, then wrapping", wrap=40)
        self.assertEqual(raw.count(b"#0"), 1)

    def test_unknown_glyph(self):
        with self.assertRaises(ValueError):
            engine.Encoder().cells("日本")


class Rom(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig, cls.out = build.build(mark=True)
        cls.data = bytes(cls.out.data)

    def test_size_and_literals(self):
        d = self.data
        self.assertEqual(len(d), engine.ROM_SIZE)
        self.assertEqual(d[engine.LIT_DIALOGUE_SHIFT:engine.LIT_DIALOGUE_SHIFT + 2], b"\x1b\x02")
        word = lambda o: struct.unpack_from("<I", d, o)[0]  # noqa: E731
        self.assertEqual(word(engine.LIT_DIALOGUE_BASE), 0x08000000 + engine.NEW_DIALOGUE)
        self.assertEqual(word(engine.LIT_FONT_BASE), 0x08000000 + engine.NEW_FONT)
        for o in engine.LIT_FONT_GLYPH:
            self.assertEqual(word(o), 0x08000000 + engine.NEW_FONT + 2)

    def test_font_sorted_and_keeps_japanese(self):
        d = self.data
        n = struct.unpack_from("<I", d, engine.LIT_FONT_HI)[0] + 1
        codes = [d[engine.NEW_FONT + i * 26] << 8 | d[engine.NEW_FONT + i * 26 + 1] for i in range(n)]
        self.assertEqual(codes, sorted(set(codes)))
        self.assertEqual(d[engine.NEW_FONT:engine.NEW_FONT + 847 * 26],
                         self.orig[engine.FONT:engine.FONT + 847 * 26])

    def test_every_dialogue_slot_relocated(self):
        d = self.data
        for k in range(2927):
            slot = d[engine.NEW_DIALOGUE + k * 256:engine.NEW_DIALOGUE + (k + 1) * 256]
            self.assertLess(slot.index(0), engine.DIALOGUE_BUFFER, k)
            self.assertFalse(any(slot[slot.index(0):]), k)

    def test_marker_ids_unique(self):
        rows = [r for rs in text.load_all().values() for r in rs]
        tags = marker.short_ids(rows)
        self.assertEqual(len(set(tags.values())), len(tags))


if __name__ == "__main__":
    unittest.main()
