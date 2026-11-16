# Decisions

The user's rulings on scope, style and trade-offs, newest last. Read before asking the user anything; if a later
decision replaces one, mark the old one "replaced by D<n>" instead of deleting it. Binding term spellings live in
`glossary.md`; this file holds the why.

| # | Date | Question | Options offered | Decision and reason |
|---|---|---|---|---|
| D1 | 2026-11-17 | Honorifics and name order | keep (-san), drop; JP or Western order | Keep honorifics; Western order (given name first). Owner's standing answer for one-shot runs. |
| D2 | 2026-11-17 | Romanization source for names | official art, earlier patch, Hepburn | Official English names where they exist, else an earlier fan patch, else Hepburn without macrons. Owner's standing answer. |
| D3 | 2026-11-17 | Credits | stay Japanese, translate | English. Owner's standing answer. |
| D4 | 2026-11-17 | Abbreviations | engine work first (default), abbreviate | Engine work first (skill default; not overridden by the owner). |
| D5 | 2026-11-17 | Graphics text left in Japanese | none (default), list | Translate all of it (titles, menus, banners, cards); leave the original Japanese logo only if it has no official English version. The title logo here is already Latin ("ToyroboForce"). |
| D6 | 2026-11-17 | Specs and plans | need approval, pre-approved | Pre-approved: keep going through every checkpoint, report at the end. |
| D7 | 2026-11-17 | Existing saves / savestates | user's saves, none | None provided; build the debug tool as usual. |
| D8 | 2026-11-17 | Git identity | set, ask | Already set by new-game.ps1 (minhnhattonthat); do not change it. |
| D9 | 2026-11-17 | English font (agent ruling under D6, no owner input needed) | half-width, digraph (2 letters per 12-px cell), VWF | Digraph: 6-px monospace letters, 40 per dialogue line, no renderer or caller changes (every text routine draws the same 12-px cells); VWF would need the renderer and 14 callers rewritten. Revisit only if a box proves too tight. |
