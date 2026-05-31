#!/usr/bin/env python3
"""Extract the current Codex rollout into compact text for a handoff subagent."""

import argparse
import glob
import json
import os
import sys


def clip(text, limit):
    text = str(text or "").rstrip()
    if limit and len(text) > limit:
        return text[:limit] + f"\n...[clipped {len(text) - limit} chars]"
    return text


def find_rollout(explicit, session_id):
    if explicit:
        return explicit
    roots = [
        os.path.expanduser("~/.codex/sessions/**/*.jsonl"),
        "/mnt/*/Users/*/.codex/sessions/**/*.jsonl",
    ]
    files = []
    for pattern in roots:
        files.extend(glob.glob(pattern, recursive=True))
    if session_id:
        files = [p for p in files if session_id in os.path.basename(p)]
    return max(files, key=os.path.getmtime) if files else None


def load(path):
    records = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            try:
                records.append(json.loads(line))
            except json.JSONDecodeError:
                pass
    return records


def text_from_parts(parts):
    if isinstance(parts, str):
        return parts
    out = []
    if isinstance(parts, list):
        for part in parts:
            if not isinstance(part, dict):
                continue
            if part.get("type") in {"input_text", "output_text", "text"}:
                out.append(part.get("text", ""))
    return "\n".join(x for x in out if x)


def is_compaction(record):
    if record.get("type") in {"summary", "compact", "compaction"}:
        return True
    payload = record.get("payload") or {}
    return bool(payload.get("isCompactSummary"))


def last_compaction(records):
    idx = -1
    for i, record in enumerate(records):
        if is_compaction(record):
            idx = i
    return idx


def render_response_item(payload, max_block):
    kind = payload.get("type")
    if kind == "message":
        role = payload.get("role", "assistant")
        if role not in {"user", "assistant"}:
            return None
        phase = payload.get("phase")
        body = text_from_parts(payload.get("content"))
        if not body:
            return None
        if role == "user" and body.lstrip().startswith("<environment_context>"):
            return None
        label = "User" if role == "user" else "Assistant"
        suffix = f" ({phase})" if phase else ""
        return f"## {label}{suffix}\n{clip(body, max_block)}"
    if kind == "function_call":
        args = clip(payload.get("arguments", ""), 900)
        return f"## Tool call\n{payload.get('name', '?')}({args})"
    if kind == "function_call_output":
        return f"## Tool output\n{clip(payload.get('output', ''), max_block)}"
    if kind in {"web_search_call", "image_generation_call"}:
        return f"## Tool event\n{clip(json.dumps(payload, ensure_ascii=False), 1000)}"
    return None


def render(record, max_block):
    rtype = record.get("type")
    payload = record.get("payload") or {}

    if rtype == "session_meta":
        meta = payload.copy()
        meta.pop("base_instructions", None)
        meta.pop("tools", None)
        return "## Session meta\n" + clip(json.dumps(meta, ensure_ascii=False), 2000)
    if rtype == "turn_context":
        compact = {
            "turn_id": payload.get("turn_id"),
            "cwd": payload.get("cwd"),
            "current_date": payload.get("current_date"),
            "timezone": payload.get("timezone"),
            "approval_policy": payload.get("approval_policy"),
            "sandbox_policy": payload.get("sandbox_policy"),
            "model": payload.get("model"),
            "summary": payload.get("summary"),
        }
        return "## Codex turn context\n" + clip(json.dumps(compact, ensure_ascii=False), 2000)
    if rtype == "response_item":
        return render_response_item(payload, max_block)
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--rollout", default="")
    parser.add_argument("--session-id", default=os.environ.get("CODEX_SESSION_ID", ""))
    parser.add_argument("--max-block", type=int, default=1000)
    args = parser.parse_args()

    path = find_rollout(args.rollout, args.session_id.strip())
    if not path or not os.path.isfile(path):
        sys.stderr.write("ERROR: could not locate Codex rollout jsonl\n")
        return 2

    records = load(path)
    session_id = ""
    for record in records:
        if record.get("type") == "session_meta":
            session_id = ((record.get("payload") or {}).get("id") or "").strip()
            break
    start = last_compaction(records)
    current = records[start:] if start >= 0 else records

    print("<<<HANDOFF-CONTEXT-META>>>")
    print(f"rollout: {path}")
    print(f"session_id: {session_id or 'unknown'}")
    print(f"total_records: {len(records)}")
    print(f"records_emitted: {len(current)}")
    print(f"compaction_found: {'yes' if start >= 0 else 'no'}")
    print("<<<END-META>>>\n")

    blocks = [render(r, args.max_block) for r in current]
    print("\n\n".join(b for b in blocks if b))
    return 0


if __name__ == "__main__":
    sys.exit(main())
