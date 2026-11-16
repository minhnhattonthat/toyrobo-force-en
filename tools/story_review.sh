#!/bin/sh
# Story-pass reviewer through `codex exec` (read-only sandbox; D11), one chapter per call.
# usage: tools/story_review.sh CHAPTER...   (from the repo root; chapters are work/qa/story/chapters/<CHAPTER>.txt
# made by tools/story.py) -> work/qa/story/rep_<CHAPTER>.md, log_<CHAPTER>.txt. Prompt: docs/story-review-prompt.md.
# A re-review after fixes: move the earlier reports to work/qa/story/<round>/ first; with PREV=<round> the prompt
# points the reviewer at work/qa/story/<round>/rep_<CHAPTER>.md so it can confirm the fixes.
mkdir -p work/qa/story
for ch in "$@"; do
  sed "s|FILE|work/qa/story/chapters/$ch.txt|" docs/story-review-prompt.md > "work/qa/story/prompt_$ch.md"
  if [ -n "$PREV" ] && [ -f "work/qa/story/$PREV/rep_$ch.md" ]; then
    printf '\n## Re-review\nThis chapter was reviewed before and its findings were fixed. The earlier report is `%s`:\n%s\n' \
      "work/qa/story/$PREV/rep_$ch.md" "check each earlier finding is resolved, then judge the whole chapter as above." \
      >> "work/qa/story/prompt_$ch.md"
  fi
  codex exec -s read-only --skip-git-repo-check --ephemeral -o "work/qa/story/rep_$ch.md" - \
    < "work/qa/story/prompt_$ch.md" > "work/qa/story/log_$ch.txt" 2>&1
  echo "$ch exit $?"
done
