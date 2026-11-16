# Polish pass

Minor findings deferred from reviews. Tick each `[x]` when fixed or `waived: reason`; the release script refuses to
run while any line is unticked.

## Phase 6 reviewer pass (codex exec, reports in work/qa/review/rep_A-J.md)
- [ ] dlg:0105 - "An 'Out of Control' has occurred" reads awkwardly; try "there's been an 'Out of Control' incident at Camembert Ranch"
- [ ] dlg:0119, dlg:0176 - "Earn all the results you can" unnatural; "Get the best results you can and secure enough funding"
- [ ] dlg:0219, dlg:0224, dlg:0248 - repeated "Sortieing" is ungainly; "Heading out without telling the Instructor?"
- [ ] choice:57, choice:60 - "Mass drowning at sea" reads as an incident, not a deliberate act (who jumps: check the scene)
- [x] dlg:1258, 1261, 1263, 1266, 1335, 1337, 1339, 1341 - speaker "Chief:" vs "Chief Sumita:" - waived: JP label is 署長 alone, "Chief" is its glossary form; スミタ署長 rows already read "Chief Sumita:"

## Phase 7
- [ ] info panel arm row: "Air Gun ( 2)" vs "Tear Gas( 3)" - an odd-length name gets a pad space before "(", an even one none (format strings:2492DC "%s(" is shared; a fix needs the name padded at runtime). Same in the factory descs after a %s: "Equip Fire Shield ?", "The body is Polisteka ." (phase 8, work/qa/cover/play_left 0046)
