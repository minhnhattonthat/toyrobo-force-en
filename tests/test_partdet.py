"""Part-detail window (factory assemble/swap lists, builder 0x080096E8): every line the game composes from the
strings at 0x2492EC..0x2494B4 must fit the window's 14 cells. "%d-Shot Burst" made line 2 sixteen cells: the
text wrapped to a 4th line, which overwrote the window's shared blank tile and drew garbage over the whole box
(phase 8, work/qa/inv6 after the fix). Digit counts follow the jp's own alignment variants (each extra full-width
space stands for one digit fewer); %s is a name at its window cap."""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))

import engine  # noqa: E402
import text  # noqa: E402
import windows  # noqa: E402

CELLS = 14
NAME = {"names": windows.VARIANTS["names"]["cap"], "parts": windows.VARIANTS["parts"]["cap"],
        "items": windows.VARIANTS["items"]["cap"]}
# window lines: (string ids in draw order, digits per %d in order, letters of a %s)
LINES = [
    (["2492EC"], [], NAME["names"]),                      # Body: %s
    (["2492FC"], [2], 0),                                 # Life: %d
    (["24930C"], [4], 0),                                 # Maintenance per Life: %d
    (["249328"], [], NAME["parts"]),                      # Right Arm: %s
    (["2493CC"], [], NAME["parts"]),                      # Left Arm: %s
    (["249334", "249360", "249378"], [3, 2, 1], 0),       # Power%d + %d-Way + %d-Shot
    (["249340", "24936C", "249378"], [2, 1, 1], 0),
    (["249350", "24936C", "249378"], [1, 1, 1], 0),
    (["249380"], [1, 3], 0),                              # Charge Cost: %dx%d
    (["249398"], [1, 2], 0),
    (["2493B0"], [1, 1], 0),
    (["2493D8"], [], NAME["items"]),                      # Pasocop: %s
    (["2493E8"], [2], 0),                                 # Speed: %d
    (["2493F8"], [], NAME["items"]),                      # Option: %s
] + [([a], [], 0) for a in ("249404", "249418", "24942C", "249444", "24945C", "249470", "249488", "24949C",
                            "2494B4")]


class PartDetail(unittest.TestCase):
    def test_lines_fit(self):
        rows = {r["id"]: r for rows in text.load_all().values() for r in rows}
        for ids, digits, name in LINES:
            cells, d = 0, list(digits)
            for i in ids:
                en = rows["strings:" + i]["en"].replace("{br}", "")
                e = engine.Encoder()
                for it in e.cells(en):
                    if isinstance(it, str):
                        cells += 1
                    elif it == b"%d":
                        cells += d.pop(0)
                    elif it == b"%s":
                        cells += -(-name // 2)
            with self.subTest(ids=ids):
                self.assertLessEqual(cells, CELLS, f"{ids}: {cells} cells")


if __name__ == "__main__":
    unittest.main()
