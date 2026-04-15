#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
command="$(printf '%s' "$payload" | python3 -c 'import sys,json
try:
    data=json.load(sys.stdin)
    print(((data.get("tool_input") or {}).get("command")) or "")
except Exception:
    print("")')"

if [[ "$command" =~ (^|[[:space:]])git[[:space:]]+commit([[:space:]]|$) ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PostToolUse","additionalContext":"A commit was created. Before any manual push, run a deep review and confirm tests for affected files."}}
JSON
fi
