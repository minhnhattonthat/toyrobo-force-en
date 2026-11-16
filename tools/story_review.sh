#!/bin/sh
# Story-pass reviewer through `codex exec` (read-only sandbox; D11), one chapter per call.
# usage: tools/story_review.sh CHAPTER...   (from the repo root; chapters are work/qa/story/chapters/<CHAPTER>.txt
# made by tools/story.py) -> work/qa/story/rep_<CHAPTER>.md, log_<CHAPTER>.txt. Prompt: docs/story-review-prompt.md.
mkdir -p work/qa/story
for ch in "$@"; do
  sed "s|FILE|work/qa/story/chapters/$ch.txt|" docs/story-review-prompt.md > "work/qa/story/prompt_$ch.md"
  codex exec -s read-only --skip-git-repo-check --ephemeral -o "work/qa/story/rep_$ch.md" - \
    < "work/qa/story/prompt_$ch.md" > "work/qa/story/log_$ch.txt" 2>&1
  echo "$ch exit $?"
done
