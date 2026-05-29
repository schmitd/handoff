# handoff

A minimal [Claude Code](https://claude.com/claude-code) skill that snapshots the current conversation into a standalone handoff document for another AI/agent to pick up — like `/compact`, but **without contaminating the main thread**.

## Why

I was inspired by Matt Pocock.

A naive handoff makes the main agent summarize its own conversation inline, dumping a large summary back into the live context window — exactly the bloat you wanted to avoid. This skill does all the summarization inside an **isolated subagent** that reads the session transcript **from disk** (an out-of-band channel the main thread never pays for), distills/compacts it, and writes the file. The main thread gains only the skill instructions, one subagent spawn (~470 tokens), and a one-line path back — the ~42k tokens of distillation work stay isolated.

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

This was built on **Windows + WSL** (the transcript store lives on the Windows side at `~/.claude/projects/<slug>/<session-id>.jsonl`, and `extract_context.py` runs under WSL `python3`).

Paths are **resolved dynamically at skill-load time** via the `` !`<command>` `` substitution feature — `SKILL.md` derives the script path from `$HOME` and the output directory from `wslpath -w "$HOME"`, so nothing is hardcoded to a specific username or WSL distro. You should be able to drop this into any Windows + WSL Claude Code setup unchanged.

Two environment assumptions remain, and they are **not** universal:

- **Git Bash / MINGW must be the Bash tool's shell.** Claude Code only uses Git Bash if Git for Windows is installed; otherwise it falls back to PowerShell, and the bash-syntax `!` blocks here won't resolve.
- **WSL with `python3` must be present.** The extractor is invoked through `wsl.exe`.

For a non-WSL machine (native Windows-only, macOS, or Linux) you'd want to invoke `python3` natively instead of through `wsl.exe` and write the output to `$HOME` directly. The core `extract_context.py` is plain stdlib Python and already globs `~/.claude/projects` as well as `/mnt/c/...`, so it runs anywhere Python does — only the `SKILL.md` wrapper is environment-specific.

Inspired by [Matt Pocock's handoff skill](https://www.aihero.dev/skills-handoff), reworked to keep the main thread's context untouched.
