"""The supported dump is present and matches rom.sha1 (skips on a clone without rom/)."""
import hashlib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"


@unittest.skipUnless(ROM.is_file(), "rom/ missing")
class RomTest(unittest.TestCase):
    def test_sha1(self):
        want = [l.split()[0] for l in (ROOT / "rom.sha1").read_text().splitlines() if l and not l.startswith("#")][0]
        self.assertEqual(hashlib.sha1(ROM.read_bytes()).hexdigest(), want)

    def test_header(self):
        data = ROM.read_bytes()
        self.assertEqual(data[0xB2], 0x96)  # fixed GBA header byte


if __name__ == "__main__":
    unittest.main()
