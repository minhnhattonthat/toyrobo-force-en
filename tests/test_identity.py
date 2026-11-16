"""Identity build: unpack every unit and pack it back with no edits -> the original ROM, byte for byte.

pack() blanks every byte the units own first, so this proves each packer regenerates its whole region."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import build  # noqa: E402
import romdiff  # noqa: E402
import units  # noqa: E402


@unittest.skipUnless(build.ORIG.is_file(), "rom/ missing")
class IdentityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.orig = build.ORIG.read_bytes()

    def fresh(self):
        return build.unpack(self.orig)

    def test_identity(self):
        orig, out = build.build(identity=True)
        self.assertEqual(out.log, [])
        self.assertTrue(bytes(out.data) == orig, "identity build differs from the original ROM")

    def test_spans_disjoint(self):
        us, _ = self.fresh()
        spans = sorted((s, e, u.name) for u in us for s, e in units.spans(u))
        for (s1, e1, n1), (s2, e2, n2) in zip(spans, spans[1:]):
            self.assertLessEqual(e1, s2, f"{n1} {s1:06X}-{e1:06X} overlaps {n2} {s2:06X}")
        self.assertEqual(len([1 for _, _, n in spans if n == "lz"]), 36)

    def test_every_unit_writes_its_bytes(self):
        us, datas = self.fresh()
        for skip in range(len(us)):
            out = units.Rom(self.orig)
            out.blank([s for u in us for s in units.spans(u)])
            for i, (u, d) in enumerate(zip(us, datas)):
                if i != skip:
                    u.pack(d, out)
            self.assertNotEqual(bytes(out.data), self.orig, f"{us[skip].name}: blanking it went unnoticed")

    def test_edit_is_logged_and_contained(self):
        us, datas = self.fresh()
        names = [u.name for u in us]
        dlg = datas[names.index("dialogue")]
        dlg[5] = "テスト#4".encode("cp932")
        out = build.pack(self.orig, us, datas)
        self.assertEqual(len(out.log), 1)
        self.assertTrue(out.log[0].startswith("%06X " % (0x397070 + 5 * 0x80)))
        writes = []
        for line in out.log:
            off, o, n, who = line.split(None, 3)
            writes.append((int(off, 16), bytes.fromhex(o), bytes.fromhex(n), who))
        errs, _ = romdiff.check(self.orig, bytes(out.data), set(), writes)
        self.assertEqual(errs, [])

    def test_overlong_text_refused(self):
        us, datas = self.fresh()
        names = [u.name for u in us]
        datas[names.index("dialogue")][0] = b"\x82\xa0" * 64
        with self.assertRaises(ValueError):
            build.pack(self.orig, us, datas)
        us, datas = self.fresh()
        recs = datas[names.index("names")]
        recs[0] = dict(recs[0], text=b"A" * 14)
        with self.assertRaises(ValueError):
            build.pack(self.orig, us, datas)

    def test_pointer_table(self):
        us, datas = self.fresh()
        names = [u.name for u in us]
        ptrs = datas[names.index("prompt_ptrs")]
        strs = dict(datas[names.index("prompts")])
        self.assertEqual(ptrs[0], 0x3F7704)
        self.assertTrue(all(p in strs for p in ptrs))
        swap = dict(datas[names.index("swap")])
        self.assertTrue(all(p in swap for p in datas[names.index("swap_ptrs")]))
        ptrs[0] += 2
        out = build.pack(self.orig, us, datas)
        self.assertEqual(out.data[0x3F788C:0x3F7890], (0x08000000 + 0x3F7706).to_bytes(4, "little"))
        self.assertTrue(strs)

    def test_lz_changed_block_recompressed(self):
        import gbacomp
        us, datas = self.fresh()
        names = [u.name for u in us]
        blocks = datas[names.index("lz")]
        off = 0x2BC310  # battle-result speech balloons (G10)
        data = bytearray(blocks[off])
        data[0] ^= 0xFF
        blocks[off] = bytes(data)
        out = build.pack(self.orig, us, datas)
        got, _ = gbacomp.decompress(out.data, off)
        self.assertEqual(got, bytes(data))
        self.assertEqual(len(out.log), 1)


if __name__ == "__main__":
    unittest.main()
