# Handoff task

This file is the full procedure for producing a handoff document. It is read by
the `handoff` skill's subagent in the subagent's own context, so it never loads
into the main thread. If you are reading this, you are that subagent.

Do all work in your own context. Your final reply must be ONLY the absolute path
to the file you wrote (one line). Do not paste the conversation or the summary
back to the dispatcher.

Your spawn instructions include a **NEXT-SESSION PURPOSE**. If it is a real
purpose (not "none"), treat it as the guide for what to include and emphasize —
tailor every section toward it, and make Next Steps concrete moves toward that
goal. If it is "none", write a general, comprehensive handoff.

## STEP 1 — Extract the current working context

Run:

```
bash "$HOME/.claude/skills/handoff/scripts/handoff_run.sh"
```

It writes the extracted context to a temp file and prints two absolute,
tool-usable paths on stdout:

```
TMP_FILE=<path>       — the extracted context (read this)
HANDOFF_FILE=<path>   — where to write the finished handoff
```

The launcher auto-selects native python3/python or WSL python3, so the same
command works on Linux, macOS, and Windows. Use the exact paths it prints.

## STEP 2 — Read the extracted context

Read `TMP_FILE` with the Read tool. It opens with a `<<<HANDOFF-CONTEXT-META>>>`
block stating whether a compaction was found and how many records were emitted.
If the file is long, read it in chunks with offset.

## STEP 3 — Distill into the handoff document

Be faithful and concrete; a stranger agent must be able to resume cold. Use
exactly this structure:

```
# Handoff — <short title; reflect the purpose if one was given>
_Generated from session <session id>_

## Focus for the next session
Restate the PURPOSE and, in 1–3 bullets, what this handoff therefore emphasizes.
(Omit this section only if PURPOSE is "none".)

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
Concrete, ordered TODOs. If a PURPOSE was given, these are moves toward it.

## Open questions & risks
Unresolved items, ambiguities, things that could bite.

## Verbatim last user request
The most recent thing the user asked, quoted, so intent isn't lost in paraphrase.
```

## STEP 4 — Write the document

Write the document to `HANDOFF_FILE` with the Write tool.

## STEP 5 — Clean up the temp file

```
bash -c 'rm -f "$HOME/.handoff-context.tmp"'
```

## STEP 6 — Reply

Reply with ONLY the value of `HANDOFF_FILE`.
