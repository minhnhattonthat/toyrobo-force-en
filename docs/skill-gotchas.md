# Skill gotchas

One line per gotcha: the reference file it belongs in, then the fact.

- references/setup.md: `fetch_emu.py gba-bios` returned HTTP 404 from retrobios (path `Nintendo/Game%20Boy%20Advance/gba_bios.bin`) on 2026-11-17; copied the same file (SHA-1 300c20df...) from a sibling repo instead.
- SKILL.md Step 0: the plugin guard hook did not load in this session (canary not blocked) until the hooks block was added to .claude/settings.json with the marketplace path.
