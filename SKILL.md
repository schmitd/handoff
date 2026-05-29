---
name: handoff
description: >-
  Capture the current conversation as a standalone handoff document for another
  AI or agent to pick up — like /compact, but the summarization happens entirely
  inside an isolated subagent so the main thread's context is NOT contaminated.
  Use this whenever the user asks to "hand off", "create a handoff", "write a
  handoff doc", "snapshot this conversation", "summarize this for another agent",
  "pass this to another AI", or wants to checkpoint context to a file without
  bloating the current thread. The user can describe what the next session will
  focus on (passed as arguments) and the document is tailored to that purpose.
  Produces a markdown file in the user's home directory; the main agent never
  reads it.
allowed-tools: Bash
argument-hint: "[what the next session will focus on]"
---

# Handoff

Snapshot this conversation into a standalone handoff document for another AI/agent
(or a fresh session) to pick up — like `/compact`, but **all summarization happens
inside an isolated subagent**, so the main thread's context is never contaminated.

Your job here is only to orchestrate. The actual procedure — extracting the
current working context, distilling it, and the document template — lives in a
bundled task file that the **subagent reads in its own context**. That keeps it
out of this (main) thread entirely; the only reason this skill is cheap is that
you do not load or run that procedure yourself.

## What you (the main agent) must do

1. Note the user's stated focus for the next session (may be empty):

   > **PURPOSE:** $ARGUMENTS

2. Spawn **exactly one** general-purpose subagent. Its prompt must contain only:
   - `NEXT-SESSION PURPOSE: ` followed by the PURPOSE above (or the word `none`
     if it is empty), and
   - this instruction, verbatim:
     `Read the file at <TASK_FILE> and follow it exactly. Your final reply must be ONLY the absolute path to the file you write.`

   where `<TASK_FILE>` is:

   > !`cygpath -w "$HOME/.claude/skills/handoff/references/handoff-task.md" 2>/dev/null || echo "$HOME/.claude/skills/handoff/references/handoff-task.md"`

3. Do **NOT** read `<TASK_FILE>` yourself, do **NOT** read the transcript, and do
   **NOT** summarize the conversation — each of those reloads into this thread the
   very context the skill exists to keep out of it.

4. When the subagent returns, report the path to the user in one line and stop:

   > Handoff written to `<path>`
