# Glossary - Toyrobo Force

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` fails a line whose JP has a term below and whose English lacks every EN form (EN forms are
`/`-separated alternatives; the first is the preferred one).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Name-san). Name order: Western (given name first).
- Romanisation source: no official English release exists (Japan only), so names are Hepburn without macrons
  (ユウキ Yuki), and katakana loanwords take the English or source-language word they come from (フランボワーズ
  Framboise, ポイヤック Pauillac: the cities and many people are named after fruit, jam, wine and cheese).
- Credits: English.
- Register / flavour: light JP flavour (honorifics). Sound effects: English onomatopoeia ("Bang!", "Whoosh").
- Abbreviations: full names and terms everywhere; prefer engine changes over shortening.

## Style rules
- Dialogue rows: `Speaker: "line"` -- the JP `名前「...」` becomes `Name: "..."`. Keep every `{face:NNNNN}`,
  `{spk:NN}` and `{wait}` in its JP order; `{br}` is optional (the build word-wraps to 40 letters x 3 lines;
  use `{br}` only where a break must fall). Narration rows (no 「」) stay plain sentences.
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> !?, ―― -> --.
- Numbers: ３０，０００ -> 30,000. Currency is the yen sign in JP; write "30,000 yen".
- Ranks and titles stay English ("Chief Sumita", "Mayor Adolf", "General Mordel", "Instructor Pauillac").
- Voices: Yuki (lead cadet, upbeat, quick); Tomomi (sensible, sharp-tongued cadet); Gilligan (big, brash,
  food-minded cadet, casual "ya", "gonna"); Blank (cool, terse cadet); Pauillac (fussy polite instructor);
  Chief Sumita (gruff boss); Polisteka / Teka robots (stiff, literal, formal); Dr. Georg (scientist).
  Refine this list as scenes are translated.

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ユウキ | Yuki | | player cadet, later officer | Yuuki |
| トモミ | Tomomi | | cadet | |
| ギリガン | Gilligan | | cadet | Giligan |
| ブランク | Blank | | cadet | |
| ポイヤック | Pauillac | | instructor (教官) | Poyack |
| スミタ | Sumita | | police chief (署長 Chief) | |
| アドルフ | Adolf | | mayor | |
| フランボワーズ | Framboise | | mayor (フランボワーズ市長 Mayor Framboise) | |
| リアナ | Riana | | girl | Liana |
| リヒター | Richter | | boy with the machine face | |
| ペータ | Peta | | Riana's boyfriend | |
| エミコ | Emiko | | daycare teacher (保母) | |
| マイコ | Maiko | | daycare teacher (保母) | |
| ゲオルグ | Georg | | doctor (博士 Dr.) | George |
| モーデル | Mordel | | general (将軍) | |
| ジェーン | Jane | | secretary (秘書) | |
| ジロー | Jiro | | | |
| ハンナ | Hanna | | | |
| サンナナ | Sannana | | Polisteka No. 37 (３７号) | |
| タック | Tuck | | priest (タック神父 Father Tuck) | |
| ロビン | Robin | | | |
| マリアン | Marian | | | |
| フッド | Hood | | | |
| みーちゃん | Mii-chan | | a Domesteka | |
| グンちゃん | Gun-chan | | a Workteka | |
| アッテンボロー | Attenborough | | | |
| タチバナ | Tachibana | | | |

## Robots (Teka) and robot types
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| テカ | Teka | | the robots of the setting; plural Teka | Teca |
| ポリステカ | Polisteka | 10 | police Teka | |
| ワークテカ | Workteka | 10 | worker Teka | |
| バンクテカ | Bankteka | 10 | bank Teka | |
| ドメステカ | Domesteka | 10 | household Teka | |
| マーケテカ | Marketeka | 10 | shop Teka | |
| メディテカ | Mediteka | 10 | medical Teka | |
| ポリジェンヌ | Polijenne | 10 | | |
| ソルジャー | Soldier | 10 | military robots | |
| トイロボ | Toyrobo | | | |
| トイロボフォース | Toyrobo Force | | | |
| パソコプ | Pasocop | | | |
| テカ反乱 | Teka Revolt | | | Teka Rebellion |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| シティ | City | | "the City" | |
| アプリコット | Apricot | | | |
| カシス | Cassis | | | |
| マーマレード | Marmalade | | | |
| ブラックベリィ | Blackberry | | ブラックベリィアイランド Blackberry Island | |
| カマンベール | Camembert | | | |
| プラム | Plum | | | |
| シャーウッド | Sherwood | | | |
| ハンブルグ | Hamburg | | | |
| カンパチダム | Kanpachi Dam | | | |
| サザンカ | Sazanka | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| コンファー | Confirm | | the cadets' radio acknowledgement ("Confirm!") | Roger |
| 訓練生 | cadet | | | trainee |
| 巡査長 | Senior Officer | | | |
| 巡査 | Officer | | | |
| 署長 | Chief | | | |
| 市長 | Mayor | | | |
| 将軍 | General | | | |
| 教官 | Instructor | | | |
| 神父 | Father | | | |
| 保母 | teacher | | daycare teacher | |
| メンテ | maintenance | | | |
| パーツ | part / parts | | | |
| オプション | option | | equipment option | |
| バレットパック | Bullet Pack | | 対空/対地 = Anti-Air / Anti-Ground | |
| パワーアップ | Power Up | | | |
| パワーシールド | Power Shield | | | |
| ステルスシールド | Stealth Shield | | | |
| ミラーシールド | Mirror Shield | | | |
| ファイアーシールド | Fire Shield | | | |
| マーマーライト | Murmurlight | | a weapon part | |
| ベローニング | Belloning | | anti-ground rifle | |
| 対空 | anti-air | | | |
| 対地 | anti-ground | | | |
| タイホ | arrest | | | |

## Decisions from earlier batches
