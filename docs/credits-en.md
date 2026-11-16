# English ending credits (for phase 7 layout)

Source: `script/strings.tsv` rows `credits:*` (0x248D44-0x249258) and the JP run
`emu.py rom/... --script tools/debug/warp.lua --var "SCENE='ending'" --frames 8400` (sheets in `work/qa/end_jp/big*.png`).
Ruling: credits in English (glossary, D-rulings). Names in Western order, Hepburn without macrons.
Readings of staff kanji names are **unverified** (marked `?`): no English credits exist for this game; check
MobyGames / the manual before release if a source turns up.

The pieces are code-placed (each string has its own literal pool entry, `ref:` column), many only 2-12 bytes, and
some screens draw words vertically one kana per string. The English needs the layout work in phase 7: relocate each
string (or one string per line) into the expanded ROM and rewrite its literal; vertical gags become horizontal
lines unless the code that steps the y position is kept (then one English word per line works).

## Ending report (done in phase 6)

`credits:248D44` is one block, already in English and checked in-game (`docs/re/shots/en_ending_report.png`):

> For all our searching, Dr. Georg, teacher Emiko and one Toyrobo were never found; we have concluded they
> vanished with the Prometheus.
>  I hereby report that the revolt case is now closed in full.
>        Teka Crime Unit
>        Senior Officer Yuki Tachibana

## Cast (one card per character portrait, in order)

| Card | JP pieces (ids) | English |
|---|---|---|
| title | キャスト 248E50 | Cast |
| Yuki | アプリコット警察 248E5C / 巡査長 248E70 / ユウキ・タチバナ 248E78 | Apricot Police / Senior Officer / Yuki Tachibana |
| Tomomi | アプリコット警察 / 巡査 248E98 / トモミ・ 248E8C + アッテンボロー 248EA0 (two lines) | Apricot Police / Officer / Tomomi / Attenborough |
| Gilligan | アプリコット警察 / 巡査 / ギリガン・ブロック 248EB0 | Apricot Police / Officer / Gilligan Brock |
| Blank | アプリコット警察 / 巡査 / ブランク 248EC4 | Apricot Police / Officer / Blank |
| Mayor | アプリコット市長 248ED0 / アドルフ・ 248EE4 + フランシスカ 248EF0 | Mayor of Apricot / Adolf Francisca |
| Chief | アプリコット警察 + 署長 248F00 / コウゾウ・スミタ 248F08 | Apricot Police Chief / Kozo Sumita |
| Riana | 市長の娘 248F1C / リアナ・ 248F28 + フランシスカ | The Mayor's Daughter / Riana Francisca |
| Peta | の、248F58 / ボーイフレンド 248F48 / のつもりの 248F60 / ペータ・カワモト 248F34 | Her Self-Styled / Boyfriend / Peta Kawamoto (JP joke: "her would-be boyfriend"; three short lines under Riana's card) |
| Pauillac | アプリコット警察 + 学校 248F6C / 教官 248F74 / ポイヤック 248F7C | Apricot Police School / Instructor / Pauillac |
| Mordel | カシスの将軍 248F88 / モーデル 248F98 | General of Cassis / Mordel |
| robots | ポリステカ 248FA4 + ”サンナナ” 248FB0 / ポリステカ + ”ジロー” 248FC0 / 冥福を祈る 248FCC | Polisteka "Sannana" / Polisteka "Jiro" / Rest in Peace |
| Workteka | アプリコット 248FD8 + のワークテカ 248FE8 / フランボワーズ 248FF8 + のワークテカ / カシスの 249008 + ワークテカ 249014 / 以下略 249020 | Apricot's Workteka / Framboise's Workteka / Cassis's Workteka / ...and the rest |
| Georg | 天才工学博士 249028 / ゲオルグ・ 249038 + ウエンツ 249044 | Genius Engineer / Dr. Georg Wentz |
| Richter | リヒター 249050 | Richter |
| Emiko | 保母 24905C / エミコ 249064 | Teacher / Emiko |

ウエンツ: Wentz (German Wenz/Wentz; the family name is only in the credits).

## Staff

| Role (JP pieces) | English role | Name (JP pieces) | English name |
|---|---|---|---|
| スタッフ 24906C | Staff | | |
| プロデューサー 249078 | Producer | 大友貴司 249088 | Takashi Otomo ? |
| ディレクター 249094 | Director | 真岡　公 2490A4 + 平 2490B0 | Kohei Maoka ? |
| ゲ｜ム デザ (one kana each: 2490B4 2490B8 2490BC 2490C0 2490C4) + イン 2490C8 (vertical) | Game Design | 雲母星彦 (in 2490C8) | Hoshihiko Kirara ? |
| キャラクター 2490D8 + デザイン 2490E8 | Character Design | 西 川 伸 司 (2490F4-249100, vertical) | Shinji Nishikawa |
| プログラ 249104 + ム 2490BC (vertical tail) | Programming | 中 山 249110 249114 + ひろいち 249118 | Hiroichi Nakayama ? |
| プ ロ 249124 249128 + グラム 24912C (vertical) | Programming | 森俊 (in 24912C) + 樹 249138 | Toshiki Mori ? |
| グ ラ フ ィック (24913C 249140 249144 249148, vertical) | Graphics | 東 田 悟 (249150 249154 249158, vertical) | Satoru Higashida ? |
| 音 楽 (24915C 249160, vertical) + ♪ 249170 | Music | 山本　秀樹 249164 | Hideki Yamamoto ? |
| グラフィック 249180 (with 中田) | Graphics | 中田 + 智 子 (249194 249198) | Tomoko Nakata ? |
| グ ラ フ ィック (vertical, second use) | Graphics | 寺沢　耕一 249174 | Koichi Terasawa ? |
| グラフィック 24919C | Graphics | 兼子　睦郎 2491AC / ひで 2491B8 / 佐賀野　仁志 2491C0 | Mutsuro Kaneko ? / Hide / Hitoshi Sagano ? |
| ＰＤ 2491D0 | PD (production desk; keep "PD") | 札場　哲 (in 2491D0) | Satoshi Fudaba ? |
| 宣 伝 広報 (2491E4 2491E8 2491EC, vertical) | Publicity | ローリー鈴木 2491F4 | Rolly Suzuki ? |
| 脚 本 (249204 249208, vertical) | Scenario | 高岡 24920C + 明 249214 | Akira Takaoka ? |
| Ｔｈｅ　Ｅｎｄ　ｏｆ 249218 / トイロボフォース 249230 | The End of / Toyrobo Force | | |
| 製作著作 249244 (above the GLOBAL A logo, a tile graphic) | Produced by | | |
| Ａｎｄ 249250, Ｉｎ 249258 | And / In (used by the post-game screens at ref 002200 / 002300) | | |

## How it was fitted (phase 7, done)
- Each piece is drawn by `bl 0x080114EC` with `movs r2,#pos` just before it: `pos` = row * 18 + column of an
  18-cell grid (12 px a cell, 2 English letters a cell; text past column 17 wraps to the next row).
  `python -X utf8 tools/credits_pos.py` lists every piece with its row, column, JP and English.
- Pieces longer than their room are moved by the build to `engine.NEW_STRINGS` and their literals rewritten
  (`windows.relocatable`); `{none}` writes an empty piece (the vertical kana gags: the role sits on one row).
- A piece drawn after a longer neighbour on the same row cuts that neighbour off at its own column ("Riana Fr"),
  so split names keep both pieces and the second moves to where the first ends: `engine.CREDIT_POS` (10 moves).
- Checked in-game: `work/qa/end_en` (warp `ending`, 8400 frames), cast and staff all English and on screen.

## Fit notes for phase 7 (as planned)
- Every English line above is at most 22 letters (11 cells), so a card line fits where the JP line sat; the work is
  only giving each line its own relocated string.
- Pieces shared by two screens (`ref:` with two offsets: 248E5C x4, 248E78, 248E8C, 248EA0, 248EB0, 248EC4, 248EF0,
  248FA4, 248FE8, 2490BC, 24913C-249148, 249230) must stay one string or be split by rewriting each literal.
- The vertical kana gags (ゲ/｜/ム...) read one glyph per row; in English write the role on one row.
