---
name: handoff
description: >-
  Snapshot the current conversation into a handoff document for another agent/AI
  or a fresh session — like /compact, but produced inside an isolated subagent so
  the main thread isn't contaminated. Trigger on "hand off", "handoff doc",
  "snapshot this conversation", "pass this to another agent", or checkpointing
  context to a file. Optional argument: what the next session will focus on.
allowed-tools: Bash
argument-hint: "[what the next session will focus on]"
---

# Handoff

All the real work happens in a subagent so this thread stays clean — you only dispatch.

1. The next session's focus (may be empty): **$ARGUMENTS**

2. Spawn **exactly one** general-purpose subagent whose prompt is only these two lines:
   - `NEXT-SESSION PURPOSE: <the focus above, or "none" if empty>`
   - `Read <TASK_FILE> and follow it exactly. Reply with ONLY the absolute path you write.`

   where `<TASK_FILE>` is:
   > !`cygpath -w "$HOME/.claude/skills/handoff/references/handoff-task.md" 2>/dev/null || echo "$HOME/.claude/skills/handoff/references/handoff-task.md"`

3. Do **NOT** read the task file, read the transcript, or summarize anything yourself — that reloads into this thread the very context the skill exists to keep out.

4. Report the path the subagent returns, in one line.
