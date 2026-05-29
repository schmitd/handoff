---
name: handoff
description: >-
  Capture the current conversation as a standalone handoff document for another
  AI or agent to pick up — like /compact, but the summarization happens entirely
  inside an isolated subagent so the main thread's context is NOT contaminated.
  Use this whenever the user asks to "hand off", "create a handoff", "write a
  handoff doc", "snapshot this conversation", "summarize this for another agent",
  "pass this to another AI", or wants to checkpoint context to a file without
  bloating the current thread. Produces a markdown file in the user's WSL home
  directory; the main agent never reads it.
allowed-tools: Bash
shell: bash
---

# Handoff

Create a handoff document that distills the *current working context* of this
conversation so a different AI/agent (or a fresh session) can continue the work.

## The core idea — protect the main thread

A naive handoff makes the main agent summarize its own conversation inline. That
dumps a large summary back into the main thread, which is exactly the bloat we
want to avoid. Instead, **all summarization happens inside an isolated subagent**.
The subagent reads the conversation transcript *from disk* (an out-of-band
channel the main thread never pays for), distills it, and writes the file. The
main thread only gains: this skill's instructions, one subagent spawn, and a
one-line path back. Nothing about the conversation is re-emitted into it.

"Current working context" is defined precisely: the most recent compaction
summary plus everything after it. Anything before that summary was already
dropped from the live window, so the handoff drops it too. The bundled
`scripts/extract_context.py` implements this slicing.

## Auto-detected paths (resolved at skill load)

These are filled in for the current machine when the skill loads — derived from
`$HOME` and `wslpath`, so nothing is hardcoded to a specific username or WSL
distro:

- **EXTRACTOR** (WSL path to the bundled script): !`echo "${HOME/\/c\//\/mnt\/c\/}/.claude/skills/handoff/scripts/extract_context.py"`
- **OUTPUT_DIR** (Windows UNC of your WSL home): !`wsl.exe -e bash -lc 'wslpath -w "$HOME"'`

When you build the subagent prompt below, substitute the resolved values above
wherever you see `<EXTRACTOR>` and `<OUTPUT_DIR>`.

> Environment assumption: this skill targets a Windows + WSL Claude Code setup
> (transcripts live on the Windows side; `python3` runs under WSL; the Bash tool
> is Git Bash/MINGW, which is what lets the `!` blocks above call `wsl.exe`). On a
> machine without WSL or without Git Bash, the expansions above won't resolve and
> the steps below will fail — see the repo README for porting notes.

## What you (the main agent) must do

Keep your own footprint minimal. **Do NOT** read the transcript, **do NOT** read
the produced handoff file, and **do NOT** summarize the conversation yourself —
doing any of these defeats the entire purpose.

Spawn **exactly one** subagent (general-purpose). Take the prompt below, replace
`<EXTRACTOR>` and `<OUTPUT_DIR>` with the resolved values, and pass it verbatim.
When the subagent returns, tell the user the file path in a single line and stop.
Do not echo the handoff contents.

### Subagent prompt (substitute `<EXTRACTOR>` / `<OUTPUT_DIR>`, then pass verbatim)

```
You are producing a context-handoff document. Do all work in your own context;
your final reply must be ONLY the absolute path to the file you wrote (one line).
Do not paste the conversation or the summary back to me.

STEP 1 — Extract the current working context (runs in WSL):
  wsl.exe -e bash -lc "python3 '<EXTRACTOR>' --session-id $CLAUDE_CODE_SESSION_ID > \$HOME/.handoff-context.tmp"
Then read <OUTPUT_DIR>\.handoff-context.tmp with the Read tool (it begins with a
<<<HANDOFF-CONTEXT-META>>> block telling you whether a compaction was found and how
many records were emitted). If the file is long, read it in chunks with offset.
The script auto-locates the live transcript; if --session-id is empty it falls
back to the most recently modified transcript, which is this session.

STEP 2 — Get a timestamp:
  wsl.exe -e date +%Y%m%d-%H%M%S

STEP 3 — Distill the extracted context into a handoff document. Be faithful and
concrete; a stranger agent must be able to resume cold. Use exactly this structure:

  # Handoff — <short title of the work>
  _Generated <timestamp> from session <session id>_

  ## Objective
  What the user is ultimately trying to achieve (the durable goal, not just the last ask).

  ## Current state
  Where things actually stand right now — what's done, what's in progress.

  ## Key decisions & rationale
  Important choices made and *why* (so the next agent doesn't relitigate them).

  ## Relevant files & artifacts
  Paths created/edited/read, each with a one-line purpose.

  ## Environment & constraints
  Anything the next agent must know to operate (OS/WSL specifics, hosts, tools,
  credentials-by-reference, conventions). Never copy secrets — reference them.

  ## Next steps
  Concrete, ordered TODOs to continue the work.

  ## Open questions & risks
  Unresolved items, ambiguities, things that could bite.

  ## Verbatim last user request
  The most recent thing the user asked, quoted, so intent isn't lost in paraphrase.

STEP 4 — Write that document with the Write tool to:
  <OUTPUT_DIR>\handoff-<timestamp>.md

STEP 5 — Clean up the temp file:
  wsl.exe -e bash -lc "rm -f \$HOME/.handoff-context.tmp"

STEP 6 — Reply with ONLY the path: <OUTPUT_DIR>\handoff-<timestamp>.md
```

## After the subagent returns

Report the path to the user in one line, e.g.:

> Handoff written to `\\wsl.localhost\Ubuntu\home\<you>\handoff-20260529-094210.md`

That's it. Your context is unchanged apart from this exchange.
