#!/usr/bin/env bash
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
tmp="$HOME/.codex-handoff-context.tmp"

if command -v python3 >/dev/null 2>&1; then
  py=python3
elif command -v python >/dev/null 2>&1; then
  py=python
else
  echo "handoff_run.sh: python3 or python is required" >&2
  exit 1
fi

"$py" "$here/extract_context.py" > "$tmp"

ts="$(date +%Y%m%d-%H%M%S)"
echo "TMP_FILE=$tmp"
echo "HANDOFF_FILE=$HOME/handoff-$ts.md"
