#!/bin/sh
# Independent reviewer pass through `codex exec` (read-only sandbox; D11).
# usage: tools/review.sh NAME FILE...   (from the repo root; FILEs are pairs files in work/qa/review/ made by
# tools/pairs.py) -> work/qa/review/rep_NAME.md, log_NAME.txt. Prompt: docs/review-prompt.md.
name=$1; shift
files=""
for f in "$@"; do files="$files \`work/qa/review/$f\`"; done
mkdir -p work/qa/review
sed "s|FILES|$files|" docs/review-prompt.md > "work/qa/review/prompt_$name.md"
codex exec -s read-only --skip-git-repo-check --ephemeral -o "work/qa/review/rep_$name.md" - \
  < "work/qa/review/prompt_$name.md" > "work/qa/review/log_$name.txt" 2>&1
echo "$name exit $?"
