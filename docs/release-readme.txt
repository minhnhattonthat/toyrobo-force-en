Toyrobo Force - English translation patch v{version}
=====================================================

Unofficial English fan translation of Toyrobo Force (Game Boy Advance, Global A Entertainment, 2001; Japan only).
This zip holds only the patch. No game data is included; you need your own dump of the Japanese cartridge.
Do not ask for or share patched ROMs.

How to apply
------------
1. Get a clean dump of the Japanese game. It must match exactly:
     No-Intro name: Toyrobo Force (Japan)
     Size:   {o_size} bytes
     CRC32:  {o_crc}
     MD5:    {o_md5}
     SHA-1:  {o_sha1}
2. Apply {patch} with any BPS patcher (Floating IPS / flips, beat, or the web patcher at
   https://www.marcrobledo.com/RomPatcher.js/). The patcher checks the base ROM's CRC and refuses a wrong dump.
3. The patched ROM is 8 MiB:
     Size:   {b_size} bytes
     CRC32:  {b_crc}
     SHA-1:  {b_sha1}

Play from a cold boot: emulator savestates made on the Japanese ROM or an older patch carry the old code and font
in memory and will show garbled text. Use in-game saves instead.
Tested in MesenCE 2.2.1 (GBA core) with the official GBA BIOS.

What is translated
------------------
- Dialogue and story: all of it.
- Menus, items, robot parts, facility screens, system messages, two-player menus: all of it.
- Graphics with text (title menu, chapter cards, map banners, battle and sortie report labels, factory signs,
  result balloons): redrawn in English. The title logo was already in English and is unchanged.
- Ending report, cast and staff credits: English. Staff name readings are our best reading of the kanji.

Style: names follow the game's own katakana (Western order); honorifics such as -chan and -sama are kept.

Known issues
------------
- Numbers and names the game fills in at run time can sit after a small gap ("Air Gun ( 2)", "12: 05"): the
  English font packs two letters per 12-pixel cell, and those inserts start on a whole cell. Cosmetic only.
- Report bugs at https://github.com/minhnhattonthat/toyrobo-force-en/issues (a savestate helps most).

Credits
-------
Translation, tools and hacking: minhnhattonthat, with extensive AI assistance (Claude by Anthropic, plus OpenAI Codex
for independent reviews). Corrections are very welcome.
Toyrobo Force is (c) 2001 Global A Entertainment. This project is not affiliated with them.
