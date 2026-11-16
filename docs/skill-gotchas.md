# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md: `fetch_emu.py gba-bios` returned HTTP 404 from retrobios (path `Nintendo/Game%20Boy%20Advance/gba_bios.bin`) on 2026-11-17; copied the same file (SHA-1 300c20df...) from a sibling repo instead.
- SKILL.md Step 0: the plugin guard hook did not load in this session (canary not blocked) until the hooks block was added to .claude/settings.json with the marketplace path.
- references/emulator-qa.md §Debug tool: on Mesen GBA, a debug-only "always win" can patch the emulator's ROM copy from Lua (`emu.write(file_off, byte, emu.memType.gbaPrgRom)`, e.g. a Thumb `b` over the loss handler's first instruction); no CPU-register writes needed.
- references/pipeline.md §Marker: to tell font-drawn text from tiles, hook the font lookup with `L.on_exec` and log r0/lr (`emu.getState()["cpu.r0"]`/`["cpu.r14"]` on Mesen GBA); a screen whose words never hit the lookup is graphics. Faster and surer than reading tile dumps (tools/debug/fontcalls.lua).
- references/pipeline.md §Marker: a game whose renderer draws fixed 12-px cells takes a digraph font with zero ASM: relocate and extend the binary-searched font table, give each used letter pair a valid-SJIS code (lead 0xE0-0xFC) at build time.
- SKILL/agent environment: the context-mode hook truncates Bash/Read output over a few KB to a search stub; read files in ranges (Read offset/limit) and send disassembly to a file first.
- references/emulator-qa.md §emu.py: `--script` files are embedded into `_run.lua` as separate chunks, so a top-level `return` in one script ends only that script; but `dofile`/`io.open` inside them resolve against tools/mesen.
