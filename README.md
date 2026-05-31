# handoff

Minimal handoff skills for Claude Code and Codex.

The intent is the same in both variants: keep the main thread clean by spawning
one isolated subagent, reading the live transcript/rollout from disk, writing a
standalone Markdown handoff, and returning only the file path.

## Variants

- `claude/` - Claude Code version. Reads `~/.claude/projects/**/*.jsonl` and uses Claude Code transcript fields.
- `codex/` - Codex version. Reads `~/.codex/sessions/**/*.jsonl` and uses Codex rollout fields.

They are intentionally separate. The Claude version is better for Claude Code;
the Codex version is better for Codex.

## Install

Claude Code:

```bash
cp -R claude ~/.claude/skills/handoff
```

Codex:

```bash
cp -R codex ~/.codex/skills/handoff
```

Then ask for a handoff, optionally with the next session's focus:

```text
handoff finish the OAuth refresh-token bug
```

## Layout

```text
claude/
  SKILL.md
  references/handoff-task.md
  scripts/handoff_run.sh
  scripts/extract_context.py
codex/
  SKILL.md
  references/handoff-task.md
  scripts/handoff_run.sh
  scripts/extract_context.py
```

Inspired by Matt Pocock's handoff skill and adapted to keep summarization out of
the active agent context.
