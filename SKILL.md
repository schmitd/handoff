---
name: handoff
description: >-
  Capture the current conversation as a standalone handoff document for another
  AI or agent to pick up — like /compact, but the summarization happens entirely
  inside an isolated subagent so the main thread's context is NOT contaminated.
  Use this whenever the user asks to "hand off", "create a handoff", "write a
  handoff doc", "snapshot this conversation", "summarize this for another agent",
  "pass this to another AI", or wants to checkpoint context to a file without
  bloating the current thread. Produces a markdown file in the user's home
  directory; the main agent never reads it.
allowed-tools: Bash
---

# Handoff

Create a handoff document that distills the *current working context* of this
conversation so a different AI/agent (or a fresh session) can continue the work.

## The core idea — protect the main thread

A naive handoff makes the main agent summarize its own conversation inline, which
dumps a large summary back into the live window — the exact bloat we want to
avoid. Instead, **all summarization happens inside an isolated subagent**. It
reads the transcript *from disk* (an out-of-band channel the main thread never
pays for), distills it, and writes the file. The main thread only gains: this
skill's instructions, one subagent spawn, and a one-line path back.

"Current working context" is defined precisely: the most recent compaction
summary plus everything after it (anything before was already dropped from the
live window). The bundled scripts implement this — `handoff_run.sh` selects an
interpreter and resolves paths for the current OS, and `extract_context.py` does
the slicing. That keeps these instructions identical on Linux, macOS, and
Windows (with or without WSL).

## What you (the main agent) must do

Keep your footprint minimal. **Do NOT** read the transcript, **do NOT** read the
produced handoff file, and **do NOT** summarize the conversation yourself — any
of those defeats the purpose. Spawn **exactly one** subagent (general-purpose)
with the prompt below, passed verbatim. When it returns, report the path in a
single line and stop.

### Subagent prompt (pass verbatim)

```
You are producing a context-handoff document. Do all work in your own context;
your final reply must be ONLY the absolute path to the file you wrote (one line).
Do not paste the conversation or the summary back to me.

STEP 1 — Extract the current working context. Run:
  bash "$HOME/.claude/skills/handoff/scripts/handoff_run.sh"
It writes the extracted context to a temp file and prints two absolute,
tool-usable paths on stdout:
  TMP_FILE=<path>       — the extracted context (read this)
  HANDOFF_FILE=<path>   — where to write the finished handoff
The launcher auto-selects native python3/python or WSL python3, so this same
command works on Linux, macOS, and Windows. Use the exact paths it prints.

STEP 2 — Read TMP_FILE with the Read tool. It opens with a <<<HANDOFF-CONTEXT-META>>>
block stating whether a compaction was found and how many records were emitted.
If the file is long, read it in chunks with offset.

STEP 3 — Distill the context into a handoff document. Be faithful and concrete;
a stranger agent must be able to resume cold. Use exactly this structure:

  # Handoff — <short title of the work>
  _Generated from session <session id>_

  ## Objective
  What the user is ultimately trying to achieve (the durable goal, not just the last ask).

  ## Current state
  Where things actually stand right now — what's done, what's in progress.

  ## Key decisions & rationale
  Important choices made and *why* (so the next agent doesn't relitigate them).

  ## Relevant files & artifacts
  Paths created/edited/read, each with a one-line purpose.

  ## Environment & constraints
  Anything the next agent must know to operate (OS/shell specifics, hosts, tools,
  credentials-by-reference, conventions). Never copy secrets — reference them.

  ## Next steps
  Concrete, ordered TODOs to continue the work.

  ## Open questions & risks
  Unresolved items, ambiguities, things that could bite.

  ## Verbatim last user request
  The most recent thing the user asked, quoted, so intent isn't lost in paraphrase.

STEP 4 — Write that document to HANDOFF_FILE with the Write tool.

STEP 5 — Clean up the temp file:
  bash -c 'rm -f "$HOME/.handoff-context.tmp"'

STEP 6 — Reply with ONLY the value of HANDOFF_FILE.
```

## After the subagent returns

Report the path to the user in one line, e.g.:

> Handoff written to `<HANDOFF_FILE>`

That's it. Your context is unchanged apart from this exchange.
