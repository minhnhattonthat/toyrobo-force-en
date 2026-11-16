"""units.py: every ROM region the build rewrites, as unpack/pack pairs.

Each unit has `unpack(rom) -> data` (plain Python values: bytes, ints, lists) and `pack(data, out)`, which writes
through `out.write(off, bytes, who)` (a `Rom`, which logs every write for `romdiff.py --writes`). The identity build
(`build.py --identity`, `tests/test_identity.py`) packs every unit with what it unpacked and must give the original
ROM byte for byte. Layouts and how they were found: `docs/re/text.md`, `docs/re/script.md`, `docs/re/graphics.md`.
"""
import struct

import gbacomp

ROM_BASE = 0x08000000


class Rom:
    """A ROM image being built. `write` logs `OFFSET ORIG_HEX NEW_HEX who` for every byte range it changes."""

    def __init__(self, orig):
        self.orig = bytes(orig)
        self.data = bytearray(orig)
        self.log = []

    def write(self, off, data, who):
        end = off + len(data)
        if end > len(self.data):
            self.data.extend(b"\xff" * (end - len(self.data)))
        self.data[off:end] = data
        orig = self.orig[off:end].ljust(len(data), b"\xff")
        if orig != data:
            self.log.append(f"{off:06X} {orig.hex()} {bytes(data).hex()} {who}")

    def blank(self, ranges):
        """Fill ranges with 0xFF (not logged), so packing must regenerate every byte a unit owns."""
        for s, e in ranges:
            self.data[s:e] = b"\xff" * (e - s)

    def writes_text(self):
        return "".join(line + "\n" for line in self.log)


def _cstr(field):
    """Text up to the first NUL, and whether everything after it is NUL (a clean padded field)."""
    i = field.find(b"\0")
    if i < 0:
        return bytes(field), True
    return bytes(field[:i]), not any(field[i:])


class Slots:
    """Fixed-size NUL-padded text slots: the dialogue array read by the opcode at 0x0800A424."""

    def __init__(self, name, base, count, size):
        self.name, self.base, self.count, self.size = name, base, count, size
        self.span = (base, base + count * size)

    def unpack(self, rom):
        out = []
        for k in range(self.count):
            text, clean = _cstr(rom[self.base + k * self.size:self.base + (k + 1) * self.size])
            if not clean or len(text) >= self.size:
                raise ValueError(f"{self.name} slot {k}: not a NUL-padded string")
            out.append(text)
        return out

    def pack(self, texts, out):
        if len(texts) != self.count:
            raise ValueError(f"{self.name}: {len(texts)} slots, want {self.count}")
        for k, t in enumerate(texts):
            if len(t) >= self.size:
                raise ValueError(f"{self.name} slot {k}: {len(t)} bytes, max {self.size - 1}")
            out.write(self.base + k * self.size, t.ljust(self.size, b"\0"), f"{self.name}[{k}]")


class Records:
    """An array of fixed-size records of little-endian u16 fields (the event script: u16 opcode, u16 a1..a5)."""

    def __init__(self, name, base, count, fields):
        self.name, self.base, self.count = name, base, count
        self.fmt = "<%dH" % fields
        self.size = struct.calcsize(self.fmt)
        self.span = (base, base + count * self.size)

    def unpack(self, rom):
        return [struct.unpack_from(self.fmt, rom, self.base + k * self.size) for k in range(self.count)]

    def pack(self, recs, out):
        if len(recs) != self.count:
            raise ValueError(f"{self.name}: {len(recs)} records, want {self.count}")
        blob = b"".join(struct.pack(self.fmt, *r) for r in recs)
        out.write(self.base, blob, self.name)


class RecTable:
    """Fixed-size records whose first `width` bytes are a NUL-padded text field; the rest is kept as raw bytes.

    A record whose field is not a clean padded string (no text, or data after the NUL) is kept whole: its entry
    has `raw` instead of `text`. Name/item/part tables at 0x393560, choice menus at 0x3766BC."""

    def __init__(self, name, base, count, size, width):
        self.name, self.base, self.count, self.size, self.width = name, base, count, size, width
        self.span = (base, base + count * size)

    def unpack(self, rom):
        out = []
        for k in range(self.count):
            rec = bytes(rom[self.base + k * self.size:self.base + (k + 1) * self.size])
            text, clean = _cstr(rec[:self.width])
            if text and clean and len(text) < self.width:
                out.append({"text": text, "rest": rec[self.width:]})
            else:
                out.append({"raw": rec})
        return out

    def pack(self, recs, out):
        if len(recs) != self.count:
            raise ValueError(f"{self.name}: {len(recs)} records, want {self.count}")
        for k, r in enumerate(recs):
            if "raw" in r:
                rec = r["raw"]
            else:
                if len(r["text"]) >= self.width:
                    raise ValueError(f"{self.name}[{k}]: {len(r['text'])} bytes, max {self.width - 1}")
                rec = r["text"].ljust(self.width, b"\0") + r["rest"]
            if len(rec) != self.size:
                raise ValueError(f"{self.name}[{k}]: record is {len(rec)} bytes, want {self.size}")
            out.write(self.base + k * self.size, rec, f"{self.name}[{k}]")


class StrRegion:
    """NUL-terminated strings packed in a region, each at its original offset, NUL fill between them.

    Unpacks to a list of (offset, text). Pack keeps every offset (pointer owners are not traced yet: phase 4) and
    refuses a string that would run into the next one."""

    def __init__(self, name, lo, hi):
        self.name, self.lo, self.hi = name, lo, hi
        self.span = (lo, hi)

    def unpack(self, rom):
        out = []
        o = self.lo
        while o < self.hi:
            e = rom.index(b"\0", o)
            if e >= self.hi:
                raise ValueError(f"{self.name}: string at {o:06X} runs past {self.hi:06X}")
            out.append((o, bytes(rom[o:e])))
            o = e + 1
            while o < self.hi and rom[o] == 0:
                o += 1
        return out

    def pack(self, strs, out):
        blob = bytearray(self.hi - self.lo)
        last = self.lo
        for off, text in strs:
            if off < last:
                raise ValueError(f"{self.name}: string at {off:06X} overlaps the one before")
            end = off + len(text) + 1
            if end > self.hi:
                raise ValueError(f"{self.name}: string at {off:06X} runs past {self.hi:06X}")
            blob[off - self.lo:end - 1 - self.lo] = text
            last = end
        out.write(self.lo, bytes(blob), self.name)


class PtrTable:
    """`count` GBA pointers (u32, 0x08000000 | file offset) at `base`. Unpacks to file offsets."""

    def __init__(self, name, base, count):
        self.name, self.base, self.count = name, base, count
        self.span = (base, base + 4 * count)

    def unpack(self, rom):
        vals = struct.unpack_from("<%dI" % self.count, rom, self.base)
        if any(not ROM_BASE <= v < ROM_BASE + len(rom) for v in vals):
            raise ValueError(f"{self.name}: not a ROM pointer table")
        return [v - ROM_BASE for v in vals]

    def pack(self, offs, out):
        if len(offs) != self.count:
            raise ValueError(f"{self.name}: {len(offs)} pointers, want {self.count}")
        out.write(self.base, struct.pack("<%dI" % self.count, *(ROM_BASE + o for o in offs)), self.name)


class LZBlocks:
    """The BIOS-LZ77 (type 0x10) blocks `gbacomp.scan` finds. Unpacks to {offset: decompressed bytes}.

    Pack keeps the original packed bytes of an unchanged block (8 of the 36 don't recompress to the same bytes:
    the game's compressor differs from ours) and recompresses a changed one in place; a block that no longer fits
    its original space is an error until relocation exists (phase 7)."""

    def __init__(self, name, offsets):
        self.name, self.offsets = name, list(offsets)
        self._orig = {}
        self.spans = []  # (start, end) per block, filled by unpack

    def unpack(self, rom):
        out = {}
        self.spans = []
        for off in self.offsets:
            data, end = gbacomp.decompress(rom, off)
            self._orig[off] = (data, bytes(rom[off:end]))
            self.spans.append((off, end))
            out[off] = data
        return out

    def pack(self, blocks, out):
        for off, data in blocks.items():
            orig_data, orig_packed = self._orig[off]
            if data == orig_data:
                packed = orig_packed
            else:
                packed = gbacomp.compress(data)
                _, core = gbacomp.decompress(packed, 0)  # drop compress()'s 4-byte padding
                if core > len(orig_packed):
                    raise ValueError(f"{self.name} {off:06X}: {core} bytes packed, room {len(orig_packed)}")
                packed = packed[:core].ljust(len(orig_packed), b"\0")
            out.write(off, packed, f"{self.name} {off:06X}")


# Offsets from `gbacomp.py scan` on the original ROM (pinned so a text edit can't add or drop a "block").
LZ_OFFSETS = (
    0x0343CC, 0x0C3FC4, 0x0C9C0C, 0x0CFB38, 0x0D4A28, 0x1179D4, 0x121374, 0x12562C, 0x12B66C, 0x1316B0,
    0x24E19C, 0x24EFF4, 0x250024, 0x251130, 0x252154, 0x253134, 0x253FD8, 0x255080, 0x2561B4, 0x2572C0,
    0x258430, 0x259274, 0x25A1EC, 0x25B0D8, 0x25C0B4, 0x25D054, 0x25DEE8, 0x25ED5C, 0x25FC80, 0x260C58,
    0x27DB5C, 0x2905E0, 0x2925E0, 0x2B6460, 0x2BB0A8, 0x2BC310,
)


def spans(unit):
    """The byte ranges a unit owns (LZBlocks: one per block, known after unpack)."""
    return unit.spans if hasattr(unit, "spans") else [unit.span]


def make_units():
    """Every unit the build packs, in write order. Spans must not overlap (tests/test_identity.py checks)."""
    return [
        Records("script", 0x3831C8, 5538, 6),
        RecTable("names", 0x393560, 8, 0x14, 14),
        RecTable("parts_a", 0x393600, 39, 0x20, 22),
        RecTable("parts_b", 0x393AE0, 19, 0x20, 22),
        RecTable("items_a", 0x393D40, 8, 0x18, 18),
        RecTable("items_b", 0x393E00, 10, 0x18, 20),
        RecTable("descs", 0x393EF0, 144, 0x58, 88),
        Slots("dialogue", 0x397070, 2927, 0x80),
        RecTable("choices", 0x3766BC, 696, 0x24, 30),
        StrRegion("strings", 0x248D44, 0x2496C8),
        PtrTable("prompt_ptrs", 0x3F788C, 10),
        StrRegion("prompts", 0x3F7592, 0x3F788C),
        LZBlocks("lz", LZ_OFFSETS),
    ]
