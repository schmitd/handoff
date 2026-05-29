# Handoff task (you are the handoff subagent)

Work entirely in your own context. Final reply = ONLY the absolute path you write — nothing else.

Only run the steps below. Summarize from `TMP_FILE` alone — never search, grep, fetch, or open any other file.

Your spawn prompt gives a **NEXT-SESSION PURPOSE**. If it's a real purpose (not "none"), make it the guide: tailor every section toward it and write Next steps as concrete moves toward it. If "none", write a general, comprehensive handoff.

**STEP 1 — extract.** Run: `bash "$HOME/.claude/skills/handoff/scripts/handoff_run.sh"`
It prints two absolute, tool-usable paths and writes the context to the first:
`TMP_FILE=<read this>` and `HANDOFF_FILE=<write the handoff here>`. (Works on Linux/macOS/Windows±WSL.)

**STEP 2 — read** `TMP_FILE` (opens with a `<<<HANDOFF-CONTEXT-META>>>` block; read in chunks if long).

**STEP 3 — write** the handoff to `HANDOFF_FILE` (Write tool). Be faithful and concrete — a stranger agent must resume cold. Use exactly these sections:

```
# Handoff — <short title; reflect the purpose if given>
_session <id>_

## Focus for the next session   (omit only if PURPOSE is "none")
Restate PURPOSE + 1–3 bullets on what this handoff therefore emphasizes.

## Objective            — the durable goal, not just the last ask
## Current state        — what's done / in progress
## Key decisions & rationale  — choices + *why* (so it isn't relitigated)
## Relevant files & artifacts — each path + one-line purpose
## Environment & constraints  — OS/shell, hosts, tools, conventions; reference secrets, never copy them
## Next steps           — ordered TODOs (moves toward PURPOSE if one was given)
## Open questions & risks
## Verbatim last user request — quote it
```

**STEP 4 — clean up:** `bash -c 'rm -f "$HOME/.handoff-context.tmp"'`

**STEP 5 — reply** with ONLY the value of `HANDOFF_FILE`.
