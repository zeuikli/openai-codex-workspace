#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
if python3 -c 'import json, pathlib, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
tool = data.get("tool_input") or {}
path = str(tool.get("file_path") or tool.get("path") or "")
parts = [str(tool.get(key) or "") for key in ("content", "new_string", "command", "description")]
if path and pathlib.Path(path).is_file():
    try:
        parts.append(pathlib.Path(path).read_text(encoding="utf-8"))
    except OSError:
        pass
text = "\n".join(parts)
patterns = (
    r"\bif\s+\w+\s*==\s*\[[^\n]+\]",
    r"\bcase\s+\S+\s*:",
    r"(?:hardcode|hard-coded|special[-_ ]case|字面特判|寫死|特判)",
)
raise SystemExit(1 if any(re.search(pattern, text, re.I) for pattern in patterns) else 0)' <<<"$payload"; then
  exit 0
fi

printf '%s\n' '{"systemMessage":"v4 advisory: possible literal special-case or hard-coded fixture path detected; inspect unseen-input generalization before claiming verified.","hookSpecificOutput":{"hookEventName":"PostToolUse"}}'
exit 1
