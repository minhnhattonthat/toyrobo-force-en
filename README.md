# Toyrobo Force English translation

Unofficial English fan translation of **Toyrobo Force** (Game Boy Advance, Global A Entertainment, 2001; Japan only):
the source text and tools that build the patch.

**Just want to play?** Download the patch from [Releases](../../releases) and follow its README. This repository holds
no game data you can play; you need your own dump of the Japanese game.

**Found a bug?** [Report it](../../issues/new/choose): untranslated text, typos, overflow, crashes. Attaching a savestate
helps most.

## Translation status

| Part | Status |
|---|---|
| Dialogue / story | Translated |
| Menus, items, robot parts, facility screens, system messages | Translated |
| Title menu, chapter cards, map banners, battle and report labels, factory signs (graphics) | Translated (title logo was already English) |
| Name entry | None in this game |
| Ending report, cast and staff credits | Translated |

Known issues: numbers and names filled in at run time can sit after a small gap ("Air Gun ( 2)", "12: 05"), since the
English font packs two letters per 12-pixel cell; cosmetic only. See also [Issues](../../issues).

Base ROM (No-Intro): `Toyrobo Force (Japan)`, 4194304 bytes, CRC32 `227FC16B`, MD5
`8e5b4bb736b5030cf13052634d01ef69`, SHA-1 `6ef30145099d09cf1a1f2b3bc6618a985dabdaae`. The patch is BPS; the patched
ROM is 8 MiB. Tested in MesenCE 2.2.1; play from a cold boot.

## What's here

| Path | What it is |
|---|---|
| `script/` | Every text block: original Japanese and English. Translation fixes go here. |
| `glossary.md` | Binding names, terms and style rules. |
| `tools/` | Python build chain: extract, insert, lint, release. |
| `tests/` | unittest suite (ROM-dependent tests skip when the ROM is absent). |
| `docs/re/` | Reverse-engineering notes. |
| `docs/decisions.md`, `docs/status.md` | Rulings with their reasons; current progress and open bugs. |
| `docs/fonts.md` | Fonts used and their licences. |
| `AGENTS.md` | Instructions for coding agents (`CLAUDE.md` points to it). |
| `.codex/agents/`, `.opencode/agents/` | Subagent types (translator, reviewer, visual QA, playtester, graphics) for Codex and opencode; Claude Code gets them from the plugin. |

## Build your own patched ROM

Needs Python 3.12+ and your own dump of the Japanese game.

```sh
git clone https://github.com/minhnhattonthat/toyrobo-force-en
cd toyrobo-force-en
# copy your dump to: rom/Toyrobo Force (Japan).gba
#   (4194304 bytes, SHA-1 6ef30145099d09cf1a1f2b3bc6618a985dabdaae; the build refuses any other dump, see rom.sha1)
python -X utf8 build.py                                # -> build/toyrobo_force_en.gba
python -X utf8 tools/check.py                          # tests + text lint
```

## Support

If you enjoy this translation, you can support my work on Ko-fi:

[![Support me on Ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/minhnhattonthat)

## Licence

Tools and English translation: MIT. The original Japanese text in `script/` is Global A Entertainment's and is included
only so the translation can be checked against it. Toyrobo Force is (c) 2001 Global A Entertainment; this project is
not affiliated with them. Do not share patched ROMs.

The translation was made with extensive AI assistance (Claude by Anthropic, reviews by OpenAI Codex). Corrections are
very welcome.
