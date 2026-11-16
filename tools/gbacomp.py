"""gbacomp.py: GBA BIOS LZ77 (type 0x10) decompress/compress and a block scanner.

    python -X utf8 tools/gbacomp.py scan ROM [--min 64]         # list plausible LZ77 blocks: offset, packed, unpacked
    python -X utf8 tools/gbacomp.py dump ROM OFF OUT             # decompress one block to a file

decompress(data, off) -> (bytes, end_offset). compress(data) -> bytes (VRAM-safe: no displacement 1).
"""
import sys


def decompress(data, off=0, limit=1 << 24):
    if data[off] != 0x10:
        raise ValueError("not LZ77")
    size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
    if size == 0 or size > limit:
        raise ValueError("bad size")
    out = bytearray()
    p = off + 4
    n = len(data)
    while len(out) < size:
        if p >= n:
            raise ValueError("ran off end")
        flags = data[p]
        p += 1
        for bit in range(8):
            if len(out) >= size:
                break
            if flags & (0x80 >> bit):
                if p + 1 >= n:
                    raise ValueError("ran off end")
                b1, b2 = data[p], data[p + 1]
                p += 2
                length = (b1 >> 4) + 3
                disp = ((b1 & 0xF) << 8 | b2) + 1
                if disp > len(out):
                    raise ValueError("disp before start")
                for _ in range(length):
                    out.append(out[-disp])
            else:
                if p >= n:
                    raise ValueError("ran off end")
                out.append(data[p])
                p += 1
    return bytes(out[:size]), p


def compress(data):
    """Greedy: longest match, nearest on ties, displacement >= 2. Candidates come from a 3-byte-key index."""
    out = bytearray([0x10, len(data) & 0xFF, len(data) >> 8 & 0xFF, len(data) >> 16 & 0xFF])
    data = bytes(data)
    n = len(data)
    index = {}  # 3-byte key -> positions, ascending
    indexed = 0  # positions < indexed are in index

    def find(i):
        nonlocal indexed
        while indexed < i - 1:  # j <= i - 2
            index.setdefault(data[indexed:indexed + 3], []).append(indexed)
            indexed += 1
        maxlen = min(18, n - i)
        best_len, best_disp = 0, 0
        if maxlen < 3:
            return 0, 0
        cands = index.get(data[i:i + 3])
        if not cands:
            return 0, 0
        start = max(0, i - 4096)
        for j in reversed(cands):
            if j < start:
                break
            k = 3
            while k < maxlen and data[j + k] == data[i + k]:
                k += 1
            if k > best_len:
                best_len, best_disp = k, i - j
                if k == maxlen:
                    break
        return best_len, best_disp

    i = 0
    while i < n:
        flag_pos = len(out)
        out.append(0)
        flags = 0
        for bit in range(8):
            if i >= n:
                break
            best_len, best_disp = find(i)
            if best_len >= 3:
                flags |= 0x80 >> bit
                d = best_disp - 1
                out.append((best_len - 3) << 4 | d >> 8)
                out.append(d & 0xFF)
                i += best_len
            else:
                out.append(data[i])
                i += 1
        out[flag_pos] = flags
    while len(out) % 4:
        out.append(0)
    return bytes(out)


def scan(data, min_size=64, align=4):
    for off in range(0, len(data) - 4, align):
        if data[off] != 0x10:
            continue
        size = data[off + 1] | data[off + 2] << 8 | data[off + 3] << 16
        if size < min_size or size > 0x40000:
            continue
        try:
            out, end = decompress(data, off)
        except ValueError:
            continue
        if end - off >= size + size // 8 + 8:  # bigger than raw: noise
            continue
        yield off, end - off, len(out)


if __name__ == "__main__":
    cmd = sys.argv[1]
    rom = open(sys.argv[2], "rb").read()
    if cmd == "scan":
        mn = int(sys.argv[4]) if len(sys.argv) > 4 and sys.argv[3] == "--min" else 64
        for off, packed, size in scan(rom, mn):
            print(f"{off:07X}\t{packed}\t{size}")
    elif cmd == "dump":
        out, _ = decompress(rom, int(sys.argv[3], 16))
        open(sys.argv[4], "wb").write(out)
