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
  food-minded cadet, casual "ya", "gonna"); Blank (courteous, hesitant, literal Toyrobo; stutters "Y-yes!");
  Pauillac (fussy polite instructor); Chief Sumita (gruff boss); Polisteka / Teka robots (stiff, literal, formal);
  Dr. Georg (elderly わし/じゃ/のう register in restrained old-fashioned English: "You'd best...", "eh?",
  "my boy" now and then, chuckles "Heh heh heh"; no regional accent, no "ya"; D10).
  Full voice table and examples: `docs/style-reference.md`; plot and reveals: `docs/synopsis.md`.

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
| (map banners) | Gate, Police Academy, Factory, Police Station, City Hall, Kindergarten, Downtown (市内), Hospital, Soldier Base, Laboratory (研究所), Hotel, Army Headquarters, Restaurant, Metropolitan Police (警視庁), Fishing Village, West/East Slope, Cave Entrance, Apricot Port, Winery, Offshore Oil Rig, Arsenal (兵器庫), Battlefield Hill, Special Police, Marmalade Sea, Camembert Ranch, Plum Mountain, Sherwood Forest | | the 35 location banners (`tools/gfx.py` LOCATIONS_EN) | |

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
| メンテ | maintenance / maint. | | "Maint." only where a window is too narrow (part-detail line, 14 cells) | |
| パーツ | part / parts | | | |
| オプション | option | | equipment option | |
| バレットパック | Bullet Pack / Air Bullets / Land Bullets | | 対空/対地 = Anti-Air / Anti-Ground; items window (14 letters): Air Bullets / Land Bullets | |
| パワーアップ | Power Up | | | |
| パワーシールド | Power Shield | | | |
| ステルスシールド | Stealth Shield | | | |
| ミラーシールド | Mirror Shield | | | |
| ファイアーシールド | Fire Shield | | | |
| マーマーライト | Murmurlight | | a weapon part | |
| ベローニング | Belloning | | anti-ground rifle | |
| 対空 | anti-air / Air Power Up / Air Bullets | | item 対空パワーアップ: the items window shows 14 letters | |
| 対地 | anti-ground / Ground Shotgun / Land Power Up / Land Bullets | | parts 18 / items 14 letters: 対地ショットガン, 対地パワーアップ | |
| タイホ | arrest | | | |

## Decisions from earlier batches
- b003-b008: surnames ユウキ・タチバナ Yuki Tachibana, トモミ・アッテンボロー Tomomi Attenborough, ギリガン・ブロック
  Gilligan Brock. Ranks after promotion (s02): Tomomi and Gilligan "Officer", Yuki "Senior Officer".
- Pauillac is a Teka; its gender is never stated so far: no he/she, no "sir/ma'am" (use "the Instructor", "it").
- Pauillac's insults used as speaker labels: 豆つぶ Peanut, 米つぶ Rice Grain, ずんどう Barrel, カマキリ頭
  Mantis-Head, 身長×× Height XX, ウエスト×× Waist XX, せいしんねんれい×才 Mental Age X.
- Street/place names so far: コットン通り Cotton Street, レンガ通り Brick Street, とけい坂 Clock Hill, カシューそうげん
  Cashew Plains, ピメント池 Pimento Pond, ハクサイとうげ Cabbage Pass, こけもも Lingonberry, サザンカ幼稚園 Sazanka
  Kindergarten, カマンベール牧場 Camembert Ranch, プラム山 Plum Mountain, かくし山荘 the Hidden Lodge.
- The "Doctor" (博士) is Dr. Georg (revealed dlg:1100); speaker label stays "Doctor" for 博士, "Dr. Georg" for
  ゲオルグ博士. Richter is his grandson (孫). Emiko is a Teka ('97 Elise type teacher), she.
- b009-b023: 通信 = "Radio:", 通信・X = "X (radio):"; 反対派 = "Opposition:"; 様 kept as -sama (Blank-sama);
  Mayor Framboise and Father Tuck are instructor Teka of unknown gender: no he/she for them (Mayor Hanna and the
  "Mayor" Riana's father are human, she/he fine). Blank is a Polisteka/Toyrobo, "he". ワイン工場 the winery;
  こけももの都 Lingonberry Capital; こけももけいしちょう Lingonberry Metropolitan Police; とくべつ警察 special
  police; こけももちょうほうぶ Lingonberry Intelligence; 戦場が丘 Battlefield Hill; ブリオッシュ山 Mount Brioche;
  シャーウッドの森 Sherwood Forest; エルヴィン大佐 Colonel Erwin; 獅子身中の虫 "viper in my bosom";
  プロメテウス Prometheus (bomber). Gilligan calls Polijenne "Marian" after the Robin Hood code (dlg:1703).
- b024-b044: 声 = "Voice:", Xの声 = "X's voice:"; スピーカー "Speaker:"; thoughts （...） stay in parentheses inside
  the quotes (Richter: "(Emiko-san...)"); 空母『アルゴー』 the carrier 'Argo'; お料理上手Ｍｋ．Ⅲ 'Master Chef Mk. III';
  お掃除上手 'Master Cleaner'; くろまく 'mastermind'; ふくろのネズミ "rat in a trap"; Richter is a Toyrobo (he).
  The factory/facility descs have three voices: polite (calls him "Blank-san"), Tomomi, Gilligan ("ya").
  Weapons: ニンジンミッソー Carrot Missile, スワローレーザー Swallow Laser, トライマクナム Tri-Magnum, ダイモン Daimon,
  虫よけピストル Bug Pistol, パンプキンボム Pumpkin Bomb, オサルトライフル Apesault Rifle (pun kept), カネホーク Moneyhawk,
  小銭バルカン Coin Vulcan (like キッチンバルカン Kitchen Vulcan; must fit the info panel); Pasocops are tank names
  (Elephant, Type 90, Comet, Matilda, Valentine, Christie, Tiger, Firefly). 日誌 (save slot) = "Log".
  連射 = "%d-Shot Burst" (part info; relocated, D12). Info panel: "Right:"/"Left:", "Cop:", "Opt:" (JP labels are
  2-3 cells; an arm part name of up to 16 letters fits after them, `engine.CREDIT_POS`).
- ▼ has no English glyph: dropped from descs 15-38, 63-74, 102-110 (no code compares 0x81A5; restore if phase 7
  adds the glyph).
- ♪ and ； (sweat mark) have no English glyph: drop them or end on "!" / "...".
- 『』 terms in quotes: 'Teka Revolt', 'Out of Control' (アウト・オブ・コントロール), 'field training' (実習).
