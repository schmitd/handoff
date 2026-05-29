# handoff

A minimal [Claude Code](https://claude.com/claude-code) skill that snapshots the current conversation into a standalone handoff document for another AI/agent to pick up — like `/compact`, but **without contaminating the main thread**.

## Why

I was inspired by Matt Pocock.

A naive handoff makes the main agent summarize its own conversation inline, dumping a large summary back into the live context window — exactly the bloat you wanted to avoid. This skill does all the summarization inside an **isolated subagent** that reads the session transcript **from disk** (an out-of-band channel the main thread never pays for), distills/compacts it, and writes the file. The main thread gains only the skill instructions, one subagent spawn (~470 tokens), and a one-line path back — the ~42k tokens of distillation work stay isolated.

## How it works

1. The main agent spawns exactly one subagent and otherwise does nothing.
2. The subagent runs [`scripts/handoff_run.sh`](scripts/handoff_run.sh), a launcher that picks a working interpreter (native `python3`/`python`, or WSL `python3` as a fallback), runs [`scripts/extract_context.py`](scripts/extract_context.py), and prints two host-form paths (`TMP_FILE`, `HANDOFF_FILE`).
3. `extract_context.py` locates the live session transcript (`.jsonl`) and slices it to the **current working context**: the most recent compaction summary plus everything after it (anything before was already dropped from the live window). If the session was never compacted, the whole conversation is used.
4. The subagent distills that into a structured handoff Markdown file (written to your home directory) and returns only the path.

## Install

Copy this directory into your Claude Code skills folder:

```
~/.claude/skills/handoff/
├── SKILL.md
└── scripts/
    ├── handoff_run.sh        # portable launcher (interpreter + path resolution)
    └── extract_context.py    # transcript slicer (stdlib only)
```

Then invoke with `/handoff`. The handoff document is written to your home directory as `handoff-<timestamp>.md`.

## Cross-platform

The skill instructions are **identical on every platform** — all OS-specific logic lives in `handoff_run.sh`, so there are no per-OS branches in `SKILL.md` (which keeps the main-thread context minimal and the prompt cache-stable). The launcher handles:

| Environment | Interpreter | Notes |
|---|---|---|
| Linux | native `python3` | transcripts at `~/.claude/projects/`, output to `$HOME` |
| macOS (zsh/bash) | native `python3` | same as Linux |
| Windows + Git Bash, native Python | native `python3`/`python` | output to the Windows `%USERPROFILE%` |
| Windows + Git Bash, **no** native Python | **WSL** `python3` | transcripts/script reached via `/mnt/c/...`; `cygpath` converts paths to `C:\...` host form |

**The one hard requirement:** the Claude Code Bash tool must be a real bash — native `bash`/`zsh` on Unix, or **Git Bash / MINGW on Windows**. Claude Code only uses Git Bash if Git for Windows is installed; without it the Bash tool falls back to PowerShell, where these bash-based scripts won't run. (Install Git for Windows on a Windows host.)

The core `extract_context.py` is plain stdlib Python and globs both `~/.claude/projects` and `/mnt/c/.../.claude/projects`, so it runs anywhere Python does.

Inspired by [Matt Pocock's handoff skill](https://www.aihero.dev/skills-handoff), reworked to keep the main thread's context untouched.
