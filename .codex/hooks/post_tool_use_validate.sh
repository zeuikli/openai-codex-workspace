#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
file="$(printf '%s' "$payload" | python3 -c 'import json, sys
try:
    data = json.load(sys.stdin)
    print(((data.get("tool_input") or {}).get("file_path")) or "")
except Exception:
    print("")')"

[[ -z "$file" || ! -f "$file" ]] && exit 0

case "$file" in
  *.sh) bash -n "$file" ;;
  *.json) python3 -c 'import json, sys; json.load(open(sys.argv[1], encoding="utf-8"))' "$file" ;;
  *.py) python3 -c 'import pathlib, sys; compile(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), sys.argv[1], "exec")' "$file" ;;
  *.toml) python3 -c 'import sys
try:
    import tomllib
except ImportError:
    import tomli as tomllib
tomllib.load(open(sys.argv[1], "rb"))' "$file" ;;
esac
