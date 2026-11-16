"""The warp scene list matches the event script: every section and battle id has a scene at its record."""
import struct
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "tools" / "debug"))

import script_dump  # noqa: E402
from warp_all import load_scenes  # noqa: E402


class SceneListTest(unittest.TestCase):
    def test_parses(self):
        scenes = load_scenes()
        names = [s[0] for s in scenes]
        self.assertEqual(len(names), len(set(names)), "duplicate scene names")
        for name, rec, hold in scenes:
            self.assertTrue(rec == "title" or 0 <= int(rec) < script_dump.NREC, name)
            self.assertGreater(hold, 0, name)


@unittest.skipUnless(ROM.is_file(), "rom/ missing")
class SceneRomTest(unittest.TestCase):
    def setUp(self):
        rom = ROM.read_bytes()
        self.recs = dict(script_dump.records(rom))
        self.scenes = {s[0]: s[1] for s in load_scenes()}

    def test_every_section(self):
        secs = {r[1]: n for n, r in self.recs.items() if r[0] == 40}
        self.assertEqual(sorted(secs), list(range(24)))
        for sec, n in secs.items():
            self.assertEqual(self.scenes.get(f"sec{sec:02d}"), str(n), f"sec{sec:02d}")

    def test_every_battle(self):
        ids = {r[1] for r in self.recs.values() if r[0] == 23}
        for b in ids:
            rec = self.scenes.get(f"battle{b:02d}")
            self.assertIsNotNone(rec, f"battle{b:02d} missing")
            r = self.recs[int(rec)]
            self.assertEqual((r[0], r[1]), (23, b), f"battle{b:02d} record")

    def test_script_end(self):
        self.assertEqual(self.recs[0][0], 42)
        self.assertEqual(self.recs[5412][0], 41)
        past = struct.unpack_from("<H", ROM.read_bytes(), script_dump.SCRIPT + 12 * script_dump.NREC)[0]
        self.assertGreater(past, 0x2A, "the script runs past NREC records")


if __name__ == "__main__":
    unittest.main()
