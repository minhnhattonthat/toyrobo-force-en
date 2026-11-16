"""marker.py: `[id] marker text` for every text row, for the marker build (`build.py --marker`).

Ids are short so they fit small fields: d<slot> dialogue, n/pa/pb/ia/ib/ds<record> tables, c<record> choices,
cr/st/sw/pr<n> the n-th string of the credits/strings/swap/prompts region (row order in script/strings.tsv).
- dialogue: the jp's leading {face}/{spk} codes and trailing {wait}, then the id and filler for LINES full lines
  of 40 letters (the box width the engine gives), cut to the byte limit;
- tables and choices without codes: id + filler up to the field's byte limit (`max`);
- anything with codes or printf formats (descs, strings, prompts): every jp text run between them becomes the
  same number of bytes of filler (first run starts with the id), so code-placed layouts keep their sizes.
"""
import re

import engine

FILLER = "The quick brown fox jumps over the lazy dog. "
SHORT = {"names": "n", "parts_a": "pa", "parts_b": "pb", "items_a": "ia", "items_b": "ib", "descs": "ds",
         "choice": "c", "credits": "cr", "strings": "st", "swap": "sw", "prompts": "pr"}
LINES = 3
LEAD = re.compile(r"(?:\{(?:spk:\d\d|face:\d{5})\})*")


def short_ids(rows):
    out, count = {}, {}
    for r in rows:
        unit, _, key = r["id"].partition(":")
        if unit == "dlg":
            out[r["id"]] = f"d{int(key)}"
        elif unit in ("credits", "strings", "swap", "prompts"):
            n = count[unit] = count.get(unit, -1) + 1
            out[r["id"]] = f"{SHORT[unit]}{n}"
        else:
            out[r["id"]] = f"{SHORT[unit]}{key}"
    return out


def _fill(tag, n):
    s = f"[{tag}]" + "".join(FILLER for _ in range(n // len(FILLER) + 2))
    return s[:n].rstrip(" ") if n > 0 else ""


def marker(row, tag, jp_bytes, wide=False):
    """wide: fill every non-dialogue row to its byte limit (codes and formats kept, at the end), to find where each
    box clips (the width gate); the field's room is `max`, which for strings runs up to the next string."""
    jp = row["jp"]
    unit = row["id"].partition(":")[0]
    limit = int(row["max"]) // 2 * 2  # letters come in 2-byte cells
    if wide and unit != "dlg":
        toks = "".join(t for t in engine.TOKEN.findall(jp) if t != "{br}")
        room = limit - len(jp_bytes(toks)) - 1  # a %d prints at least one digit cell (2 bytes) for its 2
        return _fill(tag, room - room % 2).ljust(room - room % 2) + toks
    if unit == "dlg":
        lead = LEAD.match(jp).group(0)
        tail = "{wait}" if jp.endswith("{wait}") else ""
        room = limit - len(jp_bytes(lead)) - len(jp_bytes(tail))
        # exactly 40 letters per line (dot-padded, no inner spaces, so the balanced wrap can't narrow them), joined
        # by single spaces: the wrap drops those spaces and emits no {br}, so the body costs one byte per letter
        lines = [line.ljust(40, ".").replace(" ", "_")
                 for line in engine._greedy(_fill(tag, 40 * LINES + 40), 40)[:LINES]]
        room -= room % 2
        body, used = "", 0
        for line in lines:
            piece = line[:room - used]
            if not piece:
                break
            body += (" " if body else "") + piece
            used += len(piece)
        return lead + body.rstrip(" ") + tail
    parts = engine.TOKEN.split(jp)
    toks = engine.TOKEN.findall(jp)
    if len(parts) == 1 and unit not in ("credits", "strings", "swap", "prompts"):
        return _fill(tag, limit)
    out, first = "", True
    for i, seg in enumerate(parts):
        n = len(jp_bytes(seg)) if seg else 0
        n -= n % 2
        if n:
            out += (_fill(tag, n) if first else _fill("", n + 2)[2:]).ljust(n)  # same bytes as the jp run
            first = False
        if i < len(toks):
            out += toks[i]
    return out
