---
name: handoff
description: >-
  Snapshot the current Codex conversation into a handoff document for another
  agent or a fresh session. Use for "hand off", "handoff doc", "snapshot this
  conversation", or "continue this in a new session". Optional arg: the next
  session's focus.
---

Spawn exactly one subagent. Do not summarize the transcript yourself.

Prompt:

`NEXT-SESSION PURPOSE: <user's focus, or none>`
`Read $HOME/.codex/skills/handoff/references/handoff-task.md and follow it exactly. Reply with ONLY the absolute path you write.`

Return the subagent's path alone.
