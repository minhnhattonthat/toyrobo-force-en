"""Dump the main event script (5538 records of 12 bytes at ROM 0x3831C8) as text, one record per line.

    python -X utf8 tools/script_dump.py [ROM] > work/re/script.txt

Each line: record index, opcode, the five u16 args, and for opcode 15 (message) the decoded text of its slot
(slot = arg 4, at 0x397070 + slot*0x80). Layout notes: docs/re/script.md.
"""
import struct
import sys

ROM = "rom/Toyrobo Force (Japan).gba"
SCRIPT, NREC = 0x3831C8, 5538
SLOTS, SLOT = 0x397070, 0x80
NAMES = {15: "msg", 19: "goto", 21: "choice", 40: "section", 41: "end41", 42: "start"}


def records(rom):
    for n in range(NREC):
        yield n, struct.unpack_from("<6H", rom, SCRIPT + 12 * n)


def slot_text(rom, k):
    raw = rom[SLOTS + k * SLOT:SLOTS + (k + 1) * SLOT].split(b"\0", 1)[0]
    return raw.decode("cp932", "replace")


def main():
    rom = open(sys.argv[1] if len(sys.argv) > 1 else ROM, "rb").read()
    for n, r in records(rom):
        op = r[0]
        extra = "  " + slot_text(rom, r[4]) if op == 15 else ""
        print(f"{n:4d} {op:2d} {NAMES.get(op, ''):7s} {' '.join(f'{a:5d}' for a in r[1:])}{extra}")


if __name__ == "__main__":
    main()
