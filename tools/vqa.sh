#!/bin/sh
# Visual-QA reviewer pass through `codex exec` (read-only sandbox; D11: no nested workers in Orca runs).
# usage: tools/vqa.sh CHUNK   (from the repo root; CHUNK = work/qa/chunks/chunk_NNN.txt from qa_gate.py todo)
# -> work/qa/verdicts/chunk_NNN.tsv (the reviewer's final message, TSV lines only), log in work/qa/vqa/.
# Brief: docs/visual-qa-brief.md. Original-ROM sheets: work/qa/tour_jp/<scene>/sheet.png.
chunk=$1
name=$(basename "$chunk" .txt)
skill=$(python tools/skill.py)
mkdir -p work/qa/vqa work/qa/verdicts
{
  cat docs/visual-qa-brief.md
  echo
  echo "## Your dispatch"
  echo "- \$SKILL is $skill (sheet.py, inkbox.py live in \$SKILL/scripts/)."
  echo "- Chunk file: $chunk. View every image in it with your image-viewing tool; zoom with sheet.py into a"
  echo "  scratch dir under work/qa/vqa/zoom_$name/ only if your sandbox lets you write there; otherwise judge"
  echo "  from the sheet and the single frames beside it (same folder, f00NNNN.png, which you can view directly)."
  echo "- The original ROM's sheets: same scene folder under work/qa/tour_jp/ (sheet.png, f00NNNN.png)."
  echo "- You are read-only: do not write the verdict file. Instead make your FINAL message exactly the verdict"
  echo "  lines, one per id in the chunk, \`id<TAB>ok|issue<TAB>note\`, nothing else (no prose, no code fences)."
} > "work/qa/vqa/prompt_$name.md"
codex exec -s read-only --skip-git-repo-check --ephemeral -o "work/qa/vqa/out_$name.txt" - \
  < "work/qa/vqa/prompt_$name.md" > "work/qa/vqa/log_$name.txt" 2>&1
rc=$?
grep -P '^[^\t]+\t(ok|issue)\t' "work/qa/vqa/out_$name.txt" > "work/qa/verdicts/$name.tsv"
echo "$name exit $rc, $(wc -l < "work/qa/verdicts/$name.tsv") verdicts of $(wc -l < "$chunk")"
