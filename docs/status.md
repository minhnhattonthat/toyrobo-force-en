# Status

Updated at the end of every session. Keep it to what the next session needs; history is in git.

- **Phase:** 2. Debug tool next (phase 1 recon done 2026-11-17). Last build: none yet.
- **Done:**
  - Step 0: repo set up (rom.sha1 pinned, `tools/check.py` + pre-commit gate proven to reject a failing test, guard
    hook proven on the canary, own MesenCE 2.2.1 + GBA BIOS, boot route, AGENTS.md, decisions D1-D8).
  - Phase 1: `docs/re/text.md` (SJIS full-width text; 2927 dialogue slots of 128 bytes at 0x397070, read by the
    opcode at 0x0800A424 via the single literal 0x08397070 -> relocatable to wider slots in expanded ROM; control codes
    `#0 #4 #5nn #2nnnnn`; other tables: names/items 0x393560, choices 0x3766BC, credits/status 0x248D44, link
    prompts 0x3F7592). `docs/re/graphics.md` (G1-G13 from tour + full static sweep). No prior fan patch exists.
- **Next:** phase 2 debug tool (`references/emulator-qa.md` §Debug tool): find the script/scene variables in RAM
  (the opcode interpreter around 0x0800A3D0-0x0800A660 reads records through r4: find its script pointer in IWRAM/EWRAM)
  so `tools/debug/warp.lua` can jump to any chapter, map, battle, shop/status screen, ending and credits from a cold
  boot. Then extend graphics.md's "Not yet toured" list with shots from those warps.
- **Open bugs:** none.
- **Waiting on the user:** nothing.
