You review part of a JP->English fan translation of the Japan-only GBA game Toyrobo Force (police cadets and their
robots, "Teka"; a comic, light-hearted tone with a darker late plot). Read-only: no edits, no git, no subagents.
Mechanical validity (ids, control codes, width) is already enforced by a check tool - judge translation quality.
Return the report as your final message (Markdown), nothing else.

Repo root is the current directory. Inputs:
- Pairs files for this part: FILES . Each entry is `>> id | JP` then the English on the next line; `/` marks a line
  break; neighbouring entries are the context. Read ALL of each file, in parts if large.
- `glossary.md`: binding names, terms and rulings (honorifics kept, Western name order, "Confirm!" for コンファー,
  Pauillac/Mayor Framboise/Father Tuck have no he/she, speaker labels like `Chief Sumita:`). Read it first.
- `docs/style-reference.md`: the binding voice rules (each speaker's JP markers and the English devices for them;
  e.g. Blank courteous and hesitant with small stutters, Dr. Georg elderly but restrained, no regional accent).
  Judge every voice against it; a flattened voice is Important.
- `docs/synopsis.md`: plot, reveals and who knows what when (e.g. Richter's robot identity is not foreshadowed).
- `docs/credits-en.md` for the cast.
- Display limits you must NOT flag: names 10 letters, items 14, parts 18; ♪ ； ▼ have no glyph and are dropped on
  purpose; the glossary lists allowed short forms ("Right: %s", "%d-Hit", "Air Bullets").

Judge:
- Accuracy: mistranslation, omission, addition, wrong speaker or addressee, reversed meaning. Quote the JP and say
  what it means.
- Consistency: glossary names/terms exactly (one-letter slips), honorifics stable within a scene, ranks right
  (cadets become Officers in s02; Yuki "Senior Officer").
- Things players caught that reviewers missed: jokes/wordplay losing their punch; "1th" ordinals; abbreviated names
  or terms; stock phrases that read awkwardly ("... GET!").
- Voice: Yuki upbeat and quick; Tomomi sensible, sharp-tongued (feminine わよ/のね/かしら should keep some colour);
  Gilligan brash, food-minded, casual ("ya", "gonna"); Blank cool and terse; Pauillac fussy, polite, insulting the
  cadets with nicknames; Chief Sumita gruff; Polisteka/Teka stiff and literal; Dr. Georg the scientist. Speech
  quirks, register (old-man じゃ/のう/わし, rough ぜ/ねぇ/っス, feminine かしら/わよ) and emotional intensity must
  come through, not be normalised into neutral prose. A flattened voice is Important, not Minor.
- Naturalness: would an English reader stumble?

Report format:
### Issues
#### Critical (meaning reversed, broken placeholder grammar, wrong speaker)
#### Important (clear mistranslation, glossary inconsistency, abbreviation, voice flattened, joke dead)
#### Minor (style; deferred to a polish pass)
One line each: `id - JP gist - problem - suggested EN`. Only real problems; no praise; skip a section if empty.
### Assessment
Approved | Needs fixes - one sentence why.
