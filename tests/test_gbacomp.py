"""gbacomp roundtrip: decompress(compress(x)) == x on all 36 real LZ77 blocks, and compress is VRAM-safe."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import gbacomp  # noqa: E402
import units  # noqa: E402

ROM = ROOT / "rom" / "Toyrobo Force (Japan).gba"


def displacements(packed):
    """Every back-reference displacement in a packed block."""
    _, end = gbacomp.decompress(packed, 0)
    size = packed[1] | packed[2] << 8 | packed[3] << 16
    p, n, out = 4, 0, []
    while n < size:
        flags = packed[p]
        p += 1
        for bit in range(8):
            if n >= size:
                break
            if flags & (0x80 >> bit):
                out.append(((packed[p] & 0xF) << 8 | packed[p + 1]) + 1)
                n += (packed[p] >> 4) + 3
                p += 2
            else:
                n += 1
                p += 1
    return out


class SyntheticTest(unittest.TestCase):
    def test_small_inputs(self):
        for data in (b"\0", b"abc", b"\0" * 5000, bytes(range(256)) * 20, b"ab" * 3000):
            packed = gbacomp.compress(data)
            self.assertEqual(gbacomp.decompress(packed, 0)[0], data)
            self.assertEqual(len(packed) % 4, 0)
            self.assertNotIn(1, displacements(packed))


@unittest.skipUnless(ROM.is_file(), "rom/ missing")
class RomBlocksTest(unittest.TestCase):
    def test_scan_matches_pinned_offsets(self):
        rom = ROM.read_bytes()
        self.assertEqual([o for o, _, _ in gbacomp.scan(rom)], list(units.LZ_OFFSETS))

    def test_roundtrip_every_block(self):
        rom = ROM.read_bytes()
        same = 0
        for off in units.LZ_OFFSETS:
            data, end = gbacomp.decompress(rom, off)
            packed = gbacomp.compress(data)
            self.assertEqual(gbacomp.decompress(packed, 0)[0], data, f"block {off:06X}")
            self.assertNotIn(1, displacements(packed), f"block {off:06X}: displacement 1 (not VRAM-safe)")
            same += gbacomp.decompress(packed, 0)[1] == end - off and packed.startswith(rom[off:end])
        # The game's own compressor matches ours on 28 blocks; a change here means compress() changed behaviour.
        self.assertEqual(same, 28)


if __name__ == "__main__":
    unittest.main()
