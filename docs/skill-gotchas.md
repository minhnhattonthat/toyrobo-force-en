# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md: `fetch_emu.py gba-bios` returned HTTP 404 from retrobios (path `Nintendo/Game%20Boy%20Advance/gba_bios.bin`) on 2026-11-17; copied the same file (SHA-1 300c20df...) from a sibling repo instead.
- SKILL.md Step 0: the plugin guard hook did not load in this session (canary not blocked) until the hooks block was added to .claude/settings.json with the marketplace path.
- references/emulator-qa.md §Debug tool: on Mesen GBA, a debug-only "always win" can patch the emulator's ROM copy from Lua (`emu.write(file_off, byte, emu.memType.gbaPrgRom)`, e.g. a Thumb `b` over the loss handler's first instruction); no CPU-register writes needed.
- references/emulator-qa.md §emu.py: `--script` files are embedded into `_run.lua` as separate chunks, so a top-level `return` in one script ends only that script; but `dofile`/`io.open` inside them resolve against tools/mesen.
