"""windows.py: per-box text budgets from the width gate (docs/re/font.md §Width gate), used by build.py and lint.

Each variant: letters per line (`wrap`; None = one line, no wrap), `pad` (end short lines with spaces instead of
{br}), `lines` visible, `cap` (letters the screen shows, when code clips below the field's byte max), `measured`
(the shot that proves it) or None for a guess. A row's byte limit is still its TSV `max`.
"""

SHOTS = "docs/re/shots/"
VARIANTS = {
    "dialogue": dict(wrap=40, pad=False, lines=3, cap=None,
                     measured=SHOTS + "p5_dialogue_3x40.png: 3 full lines of 40 letters, no blank line after a full one"),
    "descs": dict(wrap=28, pad=True, lines=3, cap=84,
                  measured=SHOTS + "p5_wide_choice_descs.png (factory_maint): 14 cells = 28 letters a line, 3 lines"),
    "choice": dict(wrap=None, pad=False, lines=1, cap=24,
                   measured=SHOTS + "p5_wide_choice_descs.png (choice, shop_buy): 24 of 28 letters shown"),
    "names": dict(wrap=None, pad=False, lines=1, cap=10,
                  measured=SHOTS + "p5_wide_save_info_title.png (factory_info): robot name shows 10 of 12 letters"),
    # the parts list shows 18 letters, but the robot info panel draws an arm part as "Right: <name>( n)" from
    # col 4 of a 14-cell row (engine.CREDIT_POS), so a name may be 14 letters (work/qa/info_en, phase 7)
    "parts": dict(wrap=None, pad=False, lines=1, cap=14,
                  measured=SHOTS + "p5_wide_save_info_title.png (factory_info): part name shows 18 of 20 letters"),
    "items": dict(wrap=None, pad=False, lines=1, cap=14,
                  measured=SHOTS + "p5_wide_save_info_title.png (factory_info): item name shows 14 of 16 letters"),
    "strings": dict(wrap=None, pad=False, lines=1, cap=None, measured=None),  # budget = room (`max`); see font.md
    "help": dict(wrap=40, pad=False, lines=3, cap=None,
                 measured=SHOTS + "p5_wide_save_info_title.png (title): shown in the dialogue box, 40 letters a line"),
    # ending report: full screen, the game wraps at 19 cells; wrap 36 keeps clear of a full line before {br}
    "report": dict(wrap=36, pad=False, lines=8, cap=None,
                   measured=SHOTS + "jp_ending_report.png (ending, JP): 19 cells a line, 8 lines"),
}

# strings shown in the dialogue box (title-menu help, save/load messages), word-wrapped like dialogue
HELP = {"strings:2495F0", "strings:249608", "strings:249620", "strings:24965C", "strings:249678", "strings:249694"}


# Strings reached only through code pointer words (`where` = ref:...) may outgrow their room: the build moves
# them to engine.NEW_STRINGS and rewrites the words. Their budget is then the screen, letters per line:
# credits pieces are centred lines right of the cast portrait (22 letters = 132 px, docs/credits-en.md); info and
# status panel rows are px 64-238 = 29 letters including the value a %s/%d draws (docs/re/font.md).
RELOC_CAP = {"credits": 22, "strings": 29}

# rows whose `en` is written with the Japanese table, not the English engine: the save-date template, which code
# at 0x0800B580 copies and fills by adding to bytes 1/3/7/9 (the low bytes of full-width digits), 6 cells
SJIS = {"strings:2494CC"}


def relocatable(row):
    return row["id"].partition(":")[0] in RELOC_CAP and row["where"].startswith("ref:") and row["id"] not in HELP \
        and row["id"] != "credits:248D44"


def refs(row):
    return [int(x, 16) for x in row["where"][4:].split(",")]


def lines_used(items, wrap):
    """Lines an encoded row fills in a window `wrap` letters wide: cells advance the counter, {br} rounds it up to
    the next line (the game's rule, docs/re/font.md); other tokens take no cell."""
    per, n = wrap // 2, 0
    for it in items:
        if isinstance(it, str):
            n += 1
        elif it == b"#0":
            n = (n // per + 1) * per
    return max(1, -(-n // per))


def variant(row_id):
    unit = row_id.partition(":")[0]
    if unit == "dlg":
        return "dialogue"
    if row_id in HELP:
        return "help"
    if row_id == "credits:248D44":
        return "report"
    if unit == "choice":
        return "choice"
    if unit in ("names",):
        return "names"
    if unit in ("parts_a", "parts_b"):
        return "parts"
    if unit in ("items_a", "items_b"):
        return "items"
    if unit == "descs":
        return "descs"
    return "strings"


def wrap_args(row_id):
    v = VARIANTS[variant(row_id)]
    return {"wrap": v["wrap"], "pad": v["pad"]}
