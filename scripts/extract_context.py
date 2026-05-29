#!/usr/bin/env python3
"""Extract the *current working context* from a Claude Code session transcript.

The current working context is, by construction, everything the main agent can
still see: the most recent compaction summary plus every record that follows it.
Anything before that summary was already discarded from the live window during
compaction, so we drop it too. If the session has never been compacted, the
whole conversation is the current context.

This emits clean, readable text to stdout for a handoff subagent to distill into
a final document. It is intentionally lossy on noise (raw tool plumbing, base64,
huge outputs) but faithful on substance (user asks, assistant reasoning and
replies, decisions, tool intentions and salient results).

Designed to run under WSL python3. Accepts Windows-style or WSL-style paths.

Usage:
    extract_context.py [--session-id ID] [--transcript PATH] [--max-block CHARS]

Resolution order for the transcript:
    1. --transcript if given
    2. the .jsonl matching --session-id under any .claude/projects dir
    3. the most recently modified .jsonl under .claude/projects (the live session)
"""
import argparse
import glob
import json
import os
import sys

# Substrings that mark a compaction-summary record. Claude Code has marked these
# differently across versions, so we check several signals rather than one field.
_COMPACT_PREAMBLES = (
    "This session is being continued from a previous conversation",
    "The conversation is summarized below",
)


def find_transcript(session_id, explicit):
    if explicit:
        return explicit
    roots = []
    # WSL view of Windows homes, plus a native ~/.claude.
    roots += glob.glob("/mnt/c/Users/*/.claude/projects")
    roots += glob.glob("/mnt/*/Users/*/.claude/projects")
    home_proj = os.path.expanduser("~/.claude/projects")
    if os.path.isdir(home_proj):
        roots.append(home_proj)
    candidates = []
    for r in roots:
        if session_id:
            candidates += glob.glob(os.path.join(r, "*", f"{session_id}.jsonl"))
        else:
            candidates += glob.glob(os.path.join(r, "*", "*.jsonl"))
    if not candidates:
        return None
    # Most recently modified == the live session when no id is pinned.
    return max(candidates, key=os.path.getmtime)


def load_records(path):
    recs = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    return recs


def message_text(rec):
    """Concatenate the plain-text blocks of a user/assistant message record."""
    msg = rec.get("message") or {}
    content = msg.get("content")
    if isinstance(content, str):
        return content
    out = []
    if isinstance(content, list):
        for b in content:
            if isinstance(b, dict) and b.get("type") == "text":
                out.append(b.get("text", ""))
    return "\n".join(out)


def is_compaction(rec):
    t = str(rec.get("type", ""))
    sub = str(rec.get("subtype", ""))
    if rec.get("isCompactSummary") is True:
        return True
    if t in ("summary", "compact", "compaction"):
        return True
    if sub in ("compact_boundary", "compact"):
        return True
    # A continuation turn injected after compaction reads as a user message that
    # opens with the standard preamble.
    txt = message_text(rec)
    if txt:
        head = txt[:600]
        if any(p in head for p in _COMPACT_PREAMBLES):
            return True
    return False


def last_compaction_index(recs):
    idx = -1
    for i, r in enumerate(recs):
        if is_compaction(r):
            idx = i
    return idx


def clip(text, limit):
    text = text.rstrip()
    if limit and len(text) > limit:
        return text[:limit] + f"\n…[clipped {len(text) - limit} chars]"
    return text


def render(rec, max_block):
    """Render one record as readable markdown, or return None to skip it."""
    t = rec.get("type")
    msg = rec.get("message") or {}
    role = msg.get("role")
    content = msg.get("content")

    # The compaction summary itself: emit in full-ish, it's the spine of context.
    if is_compaction(rec):
        body = message_text(rec) or json.dumps(rec.get("summary", ""))
        return "## [COMPACTION SUMMARY — start of current context]\n\n" + clip(body, max_block * 4)

    if t == "user":
        parts = []
        if isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                if b.get("type") == "text":
                    parts.append(clip(b.get("text", ""), max_block))
                elif b.get("type") == "tool_result":
                    res = b.get("content", "")
                    if isinstance(res, list):
                        res = "\n".join(
                            x.get("text", "") for x in res if isinstance(x, dict)
                        )
                    parts.append("← tool result: " + clip(str(res), max_block // 2))
        elif isinstance(content, str):
            parts.append(clip(content, max_block))
        body = "\n".join(p for p in parts if p.strip())
        return ("## User\n" + body) if body.strip() else None

    if t == "assistant":
        parts = []
        if isinstance(content, list):
            for b in content:
                if not isinstance(b, dict):
                    continue
                bt = b.get("type")
                if bt == "text":
                    parts.append(clip(b.get("text", ""), max_block))
                elif bt == "thinking":
                    # Thinking is the bulkiest, least necessary part for a summary —
                    # keep just enough to convey intent.
                    parts.append("(thinking) " + clip(b.get("thinking", ""), 500))
                elif bt == "tool_use":
                    name = b.get("name", "?")
                    inp = json.dumps(b.get("input", {}), ensure_ascii=False)
                    parts.append(f"→ tool: {name}({clip(inp, 400)})")
        elif isinstance(content, str):
            parts.append(clip(content, max_block))
        body = "\n".join(p for p in parts if p.strip())
        return ("## Assistant\n" + body) if body.strip() else None

    # Drop bookkeeping records (ai-title, queue-operation, attachment, etc.).
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--session-id", default=os.environ.get("CLAUDE_CODE_SESSION_ID", ""))
    ap.add_argument("--transcript", default="")
    ap.add_argument("--max-block", type=int, default=2500,
                    help="char cap per rendered block before clipping")
    args = ap.parse_args()

    path = find_transcript(args.session_id.strip(), args.transcript.strip())
    if not path or not os.path.isfile(path):
        sys.stderr.write("ERROR: could not locate transcript "
                         f"(session-id={args.session_id!r})\n")
        return 2

    recs = load_records(path)
    start = last_compaction_index(recs)
    sliced = recs[start:] if start >= 0 else recs

    print("<<<HANDOFF-CONTEXT-META>>>")
    print(f"transcript: {path}")
    print(f"total_records: {len(recs)}")
    if start >= 0:
        print(f"compaction_found: yes (record #{start}) — emitting from there to end")
    else:
        print("compaction_found: no — session never compacted, emitting full conversation")
    print(f"records_emitted: {len(sliced)}")
    print("<<<END-META>>>\n")

    rendered = []
    for r in sliced:
        out = render(r, args.max_block)
        if out:
            rendered.append(out)
    print("\n\n".join(rendered))
    return 0


if __name__ == "__main__":
    sys.exit(main())
