# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.
- references/pipeline.md §Repo layout: editing a TSV row with Claude Code's Edit tool drops trailing tabs when the
  edit reaches the line end (empty `notes` column) and the loader then fails on 6 columns; give the row a note or
  keep the edit away from the line end.
- references/pipeline.md §Checks (GBA): code-placed credits pieces on this engine are positioned by a `movs r2,#pos`
  before each draw call (cell index in a fixed-width grid), and a piece drawn later on the same row cuts off a
  longer earlier one: list positions with a small scanner (`tools/credits_pos.py`) before writing the English.

- references/setup.md: `fetch_emu.py gba-bios` returned HTTP 404 from retrobios (path `Nintendo/Game%20Boy%20Advance/gba_bios.bin`) on 2026-11-17; copied the same file (SHA-1 300c20df...) from a sibling repo instead.
- SKILL.md Step 0: the plugin guard hook did not load in this session (canary not blocked) until the hooks block was added to .claude/settings.json with the marketplace path.
- references/emulator-qa.md §Debug tool: on Mesen GBA, a debug-only "always win" can patch the emulator's ROM copy from Lua (`emu.write(file_off, byte, emu.memType.gbaPrgRom)`, e.g. a Thumb `b` over the loss handler's first instruction); no CPU-register writes needed.
- references/pipeline.md §Marker: to tell font-drawn text from tiles, hook the font lookup with `L.on_exec` and log r0/lr (`emu.getState()["cpu.r0"]`/`["cpu.r14"]` on Mesen GBA); a screen whose words never hit the lookup is graphics. Faster and surer than reading tile dumps (tools/debug/fontcalls.lua).
- references/pipeline.md §Marker: a game whose renderer draws fixed 12-px cells takes a digraph font with zero ASM: relocate and extend the binary-searched font table, give each used letter pair a valid-SJIS code (lead 0xE0-0xFC) at build time.
- SKILL/agent environment: the context-mode hook truncates Bash/Read output over a few KB to a search stub; read files in ranges (Read offset/limit) and send disassembly to a file first.
- references/emulator-qa.md §emu.py: `--script` files are embedded into `_run.lua` as separate chunks, so a top-level `return` in one script ends only that script; but `dofile`/`io.open` inside them resolve against tools/mesen.
- docs/translator-brief.md / tools/batches.py: the skill's batches.py adapter assumes JSON script files; TSV repos need docs()/merge rewritten (done here). Also its wrap assumption: engine wrap must not count mid-line control codes as letters (engine._width here).
- SKILL.md ground rules (file-edit tool): the Edit tool drops a trailing TAB at the end of an edited line, so a TSV row with an empty last column loses that column (text.py then refuses the file); re-add it with a scratch script, or end old/new strings before the last tab.
- references/graphics.md §Find the source (GBA): vramfind found title tiles only as short dup runs; logging DMA3 SAD/DAD/CNT writes (tools/debug/dmalog.lua here) around the screen load gave the exact ROM source in one run. Worth a probes/ script for GBA.
tour_en sheet.py per scene: frames after the warp only (--from 1400; title menus --from 0), else the cold-boot frames fill each sheet (emulator-qa.md §Visual QA)
codex exec -s read-only can't write the verdict file: make its final message the TSV and grep it out (tools/vqa.sh) (emulator-qa.md §Visual QA)
- references/translation.md §Review (story pass): a full re-review after fixes keeps finding new nits; giving the reviewer its earlier report (tools/story_review.sh PREV=r1) lets it confirm the fixes first. Codex exec as the story reviewer: ~5-10 min per chapter of 100-370 rows, 4 in parallel fine.
- references/emulator-qa.md §Debug tool: tools/debug/warp.lua's default scene path ('../debug/scenes.gba.txt', relative to Mesen's working folder) failed with emu.py in a git worktree; pass --var "SCENES=[[<abs path>]]".
- references/platform-gba.md: GBA BGxHOFS/VOFS are write-only, so a ppudump io.bin holds garbage scroll values and tools/gfx_grid.py's screen rect lands on the wrong map cells (pause panel, issue #1); render the whole 32x32 map from the dump instead.
- references/graphics.md §Survey: the phase 1 sweep + tour missed screens behind in-battle input (START pause panel) and transient sprites (the arrest burst in an LZ OBJ sheet); a player found both (issue #1). Tour every in-battle menu and check the battle OBJ VRAM sheets for kana.
