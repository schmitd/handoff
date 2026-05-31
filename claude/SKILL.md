---
name: handoff
description: >-
  Snapshot the conversation into a handoff document for another agent or fresh
  session — built in an isolated subagent so the main thread stays clean. For
  "hand off", "handoff doc", "snapshot this conversation". Optional arg: the
  next session's focus.
allowed-tools: Bash
argument-hint: "[next session's focus]"
---

Don't summarize or read the transcript yourself — spawn exactly one general-purpose subagent whose whole prompt is:

`NEXT-SESSION PURPOSE: $ARGUMENTS` (use `none` if empty)
`Read <TASK_FILE> and follow it exactly; reply with ONLY the absolute path you write.`

where `<TASK_FILE>` = !`cygpath -w "$HOME/.claude/skills/handoff/references/handoff-task.md" 2>/dev/null || echo "$HOME/.claude/skills/handoff/references/handoff-task.md"`

Then output the path alone, without preamble.
