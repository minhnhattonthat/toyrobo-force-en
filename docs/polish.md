# Polish pass

Minor findings deferred from reviews. Tick each `[x]` when fixed or `waived: reason`; the release script refuses to
run while any line is unticked.

## Phase 6 reviewer pass (codex exec, reports in work/qa/review/rep_A-J.md)
- [x] dlg:0105 - "An 'Out of Control' has occurred" reads awkwardly - fixed: "Tell them there's been an 'Out of Control' at Camembert Ranch"
- [x] dlg:0119, dlg:0176 - "Earn all the results you can" unnatural - fixed: "Get the best results you can and secure a budget, or you will have a hard time of it."
- [x] dlg:0219, dlg:0224, dlg:0248 - repeated "Sortieing" is ungainly - fixed: "Heading out without telling the Instructor?" / "Heading out when you don't even know where the bus is?"
- [x] choice:57, choice:60 - "Mass drowning at sea" reads as an incident - fixed: "All leap into the sea." (海に集団身投げ: the escaped Teka throw themselves in, a guess at where they went; matches the sibling choices' form)
- [x] dlg:1258, 1261, 1263, 1266, 1335, 1337, 1339, 1341 - speaker "Chief:" vs "Chief Sumita:" - waived: JP label is 署長 alone, "Chief" is its glossary form; スミタ署長 rows already read "Chief Sumita:"

## Phase 7
- [x] info panel arm row: "Air Gun ( 2)" vs "Tear Gas( 3)" - an odd-length name gets a pad space before "(", an even one none (format strings:2492DC "%s(" is shared; a fix needs the name padded at runtime). Same in the factory descs after a %s: "Equip Fire Shield ?", "The body is Polisteka ." (phase 8, work/qa/cover/play_left 0046) - waived: engine limit (runtime %s/%d insert whole 12-px cells, `docs/re/font.md`); a fix means hooking the game's printf in ARM code for a half-cell gap. Listed under Known issues in the release README.
- [x] review Minor 4: keep_jp list - fixed: `tests/test_build.py` `test_kept_japanese` (KEEP_JP = credits:249170, the lone ♪; any other row without English fails)
- [x] review Minor 5: harden `test_relocated_strings` - fixed: every moved string has a pointer word, its old place is an empty string, its new copy is inside the ROM, no two moved strings overlap
- [x] review Minor 6: "12: 05" / "3x 2" half cells on the load screen and part detail - waived: same engine limit as the info-panel row (runtime %d digits start on a whole cell); readable, listed under Known issues
- [x] review Minor 7: a `--known` file for the `jp_left.py` scan - waived: `jp_left.py --sjis --gba-ptrs` on the build reports 0 runs, so there is nothing to list

## Phase 9 story pass (codex exec, reports in work/qa/story/rep_*.md)
- [x] dlg:0106 - "On to the next training" - fixed: "On to the next exercise."
- [x] dlg:0294 - Emiko "Fine by me" too casual - fixed: "Of course. Humans don't shoot people."
- [x] dlg:0354 - "we old hands" unsupported - fixed: "see just how many Teka we can control."
- [x] dlg:0570 - Gilligan "? You're a kid too." soft - fixed: "Huh? You're a kid yourself!"
- [x] dlg:0740 - Blank "Sir..." hides his bewilderment - fixed: "Huh...?"
- [x] dlg:0745 - Riana "Eek!" reads as alarm - fixed: "Ooh! I knew it, Blank-sama!"
- [x] dlg:0968 - Georg "stop this war" too narrow - fixed: "I mean to put a stop to war."
- [x] dlg:1105 - Georg "gentlemen" excludes Tomomi - fixed: "officers of the Apricot police"
- [x] dlg:1602 - Yuki "What a foolish boy..." too adult - fixed: "What an idiot..."
- [x] dlg:1512 - Tomomi "How tiring." detached - fixed: "Running again? I'm getting tired of this..."
- [x] dlg:1539, dlg:1546 - "show the special police the citizens' anger" stiff - fixed: "how angry the citizens are"
- [x] dlg:1943 - Tomomi "What an inflexible kid." clinical - fixed: "You just won't play along, will you?"
- [x] dlg:2096 - Yuki "Excuse me." reads as leaving - fixed: "--My apologies."
- [x] dlg:2489 - Yuki "We sortie" stiff - fixed: "We launch the moment maintenance is done."
- [x] dlg:2792 - Blank "quie...tly" awkward split - fixed: "Yes, very... carefully."
