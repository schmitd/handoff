# handoff

A minimal [Claude Code](https://claude.com/claude-code) skill that snapshots the current conversation into a standalone handoff document for another AI/agent to pick up — like `/compact`, but **without contaminating the main thread**.

## Why

A naive handoff makes the main agent summarize its own conversation inline, dumping a large summary back into the live context window — exactly the bloat you wanted to avoid. This skill does all the summarization inside an **isolated subagent** that reads the session transcript **from disk** (an out-of-band channel the main thread never pays for), distills it, and writes the file. The main thread gains only the skill instructions, one subagent spawn (~470 tokens), and a one-line path back — the ~42k tokens of distillation work stay isolated.

## How it works

1. The main agent spawns exactly one subagent and otherwise does nothing.
2. The subagent runs [`scripts/extract_context.py`](scripts/extract_context.py), which locates the live session transcript (`.jsonl`) and slices it to the **current working context**: the most recent compaction summary plus everything after it (anything before was already dropped from the live window). If the session was never compacted, the whole conversation is used.
3. The subagent distills that into a structured handoff Markdown file and returns only the path.

## Install

Copy this directory into your Claude Code skills folder:

```
~/.claude/skills/handoff/
├── SKILL.md
└── scripts/extract_context.py
```

Then invoke with `/handoff`.

## Notes / portability

This was built on Windows + WSL (the transcript store lives on the Windows side at `~/.claude/projects/<slug>/<session-id>.jsonl`, and `extract_context.py` runs under WSL `python3`). The output path and the WSL invocation in `SKILL.md` are hard-coded to that setup — adjust the paths in `SKILL.md` for your environment.

Inspired by [Matt Pocock's handoff skill](https://www.aihero.dev/skills-handoff), reworked to keep the main thread's context untouched.
