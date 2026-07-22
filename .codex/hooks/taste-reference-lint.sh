#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
if python3 -c 'import json, re, sys
try:
    data = json.load(sys.stdin)
except Exception:
    raise SystemExit(0)
tool = data.get("tool_input") or {}
text = "\n".join(str(data.get(key) or "") for key in ("prompt", "user_prompt", "content"))
text += "\n" + "\n".join(str(tool.get(key) or "") for key in ("command", "content", "new_string", "description"))
taste = r"專業一點|高級感|更好看|現代一點|professional|premium|polished|make it nicer|better style"
reference = r"參考|範例|樣本|reference|sample|example|方向|選項|草案"
raise SystemExit(1 if re.search(taste, text, re.I) and not re.search(reference, text, re.I) else 0)' <<<"$payload"; then
  exit 0
fi

printf '%s\n' '{"systemMessage":"v4 advisory: taste/visual request lacks a reference or multiple directions; do not silently choose one style and claim completion.","hookSpecificOutput":{"hookEventName":"PreToolUse"}}'
exit 1
