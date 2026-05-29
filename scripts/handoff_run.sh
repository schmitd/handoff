#!/usr/bin/env bash
# handoff_run.sh — portable extractor launcher for the `handoff` skill.
#
# Encapsulates every platform difference so the skill's subagent instructions can
# be identical on Linux, macOS, and Windows (Git Bash, with or without WSL):
#
#   1. Runs the bundled extract_context.py with whatever Python is usable —
#      native python3/python if present, else WSL python3 as a fallback (the
#      common Windows + WSL case, where the Git Bash shell has no real python).
#   2. Prints two ABSOLUTE, HOST-FORM paths the Read/Write tools can use directly:
#        TMP_FILE=<path>      the extracted current-context file (read this)
#        HANDOFF_FILE=<path>  where to write the finished handoff document
#
# The only assumption is that the Bash tool's shell is bash — i.e. native
# bash/zsh on Unix, or Git Bash/MINGW on Windows. (PowerShell-only Windows
# installs are not supported; install Git for Windows.)
set -euo pipefail

here="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
script="$here/extract_context.py"
sid="${CLAUDE_CODE_SESSION_ID:-}"          # empty is fine: extractor falls back
tmp_sh="$HOME/.handoff-context.tmp"        # path as the current shell sees it

# --- extract, choosing an interpreter ---------------------------------------
if python3 -c 'pass' >/dev/null 2>&1; then
  python3 "$script" --session-id "$sid" > "$tmp_sh"
elif command -v python >/dev/null 2>&1 \
     && python -c 'import sys; sys.exit(0 if sys.version_info[0] >= 3 else 1)' >/dev/null 2>&1; then
  python "$script" --session-id "$sid" > "$tmp_sh"
elif command -v wsl.exe >/dev/null 2>&1; then
  # No usable native Python; run inside WSL. Translate /c/... -> /mnt/c/... so
  # WSL can see the Windows-side script and temp file (same bytes either way).
  to_wsl() { printf '%s' "$1" | sed 's|^/\([a-zA-Z]\)/|/mnt/\1/|'; }
  wsl.exe -e bash -lc "python3 '$(to_wsl "$script")' --session-id '$sid' > '$(to_wsl "$tmp_sh")'"
else
  echo "handoff_run.sh: no usable Python found (native python3/python, or WSL)." >&2
  exit 1
fi

# --- emit host-form paths for the Read/Write tools --------------------------
# On Windows the shell path (/c/Users/..) is not what the tools want (C:\Users\..);
# cygpath bridges that. On Unix the shell path is already the host path.
if command -v cygpath >/dev/null 2>&1; then
  tmp_host="$(cygpath -w "$tmp_sh")"
  dir_host="$(cygpath -w "$HOME")"
  sep='\'
else
  tmp_host="$tmp_sh"
  dir_host="$HOME"
  sep='/'
fi

ts="$(date +%Y%m%d-%H%M%S)"
echo "TMP_FILE=${tmp_host}"
echo "HANDOFF_FILE=${dir_host}${sep}handoff-${ts}.md"
