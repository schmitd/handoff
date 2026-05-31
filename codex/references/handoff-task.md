# Handoff Task

Work in your own context. Final reply: ONLY the absolute path written.

1. Run `bash "$HOME/.codex/skills/handoff/scripts/handoff_run.sh"`.
2. Read the printed `TMP_FILE`.
3. Write `HANDOFF_FILE` as a concise, faithful Markdown handoff. If `NEXT-SESSION PURPOSE` is not `none`, bias every section toward that purpose.
4. Run `rm -f "$HOME/.codex-handoff-context.tmp"`.

Use exactly this shape:

```markdown
# Handoff - <short title>
_session <id>_

## Focus for the next session
Omit if purpose is `none`.

## Objective
## Current state
## Key decisions and rationale
## Relevant files and artifacts
## Environment and constraints
## Next steps
## Open questions and risks
## Verbatim last user request
```

Keep it dense. Preserve commands, paths, branch names, verification results, blockers, and user constraints. Mention secrets by role only; never copy secret values.
