# Translator brief (phase 6)

Read `glossary.md` first (rulings, style rules, terms, "Decisions from earlier batches"), then for each batch:

1. `python -X utf8 tools/tl_body.py view bNNN` -- one line per row: `id form body`, `{br}` shown as ` / `, the
   leading `{face}`/`{spk}` codes and trailing `{wait}` hidden (they are put back from the JP). An id marked `*`
   keeps codes inside the body: the English must carry those codes too, in the same order.
2. Write `work/tl/bNNN.body.tsv` (file-write tool, never a heredoc): `id<TAB>English body`, every id, same order.
   Dialogue `Name: "line"`; a JP row that opens 「 without closing it continues on the next row: open the quote and
   close it on the row whose JP closes 」. Narration and system lines stay plain.
3. `python -X utf8 tools/tl_body.py wrap bNNN && python -X utf8 tools/batches.py check bNNN` until OK. Fix lines by
   writing a fix file (`id<TAB>body`) and `tools/tl_body.py set bNNN FIX`.
4. `python -X utf8 tools/batches.py merge bNNN` writes the English into `script/` (and into every untranslated row
   of the same box kind with the same JP). `--overwrite` only to change English already merged.

Budgets (the check measures them with the build's own wrap): dialogue 40 letters x 3 lines and 149 bytes incl.
codes (a {face} costs 7 bytes, {spk} 4, {wait} 2); choices 24 letters incl. the quotes; names 10, parts 18,
items 14, descriptions 28 x 3. Plain ASCII only.

Quality bar (mistakes to avoid): no gendered words for characters whose gender is unknown (Pauillac); keep jokes
and running gags (Pauillac's insults, Tomomi's "good kids read the manual!", "You must have some deep plan..."); keep
each voice (glossary "Voices"); honorifics after names (Yuki-kun, Emiko-san); no abbreviations.
