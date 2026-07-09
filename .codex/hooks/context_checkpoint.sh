#!/usr/bin/env bash
set -euo pipefail

phase="${1:-post}"
cat >/dev/null

if [[ "$phase" == "pre" ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreCompact","additionalContext":"壓縮前 checkpoint：保留目前 Goal、已驗證結果、未完成步驟與工作樹狀態。"}}
JSON
else
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PostCompact","additionalContext":"壓縮後先核對最新使用者需求、執行計畫與 git status，再延續未完成工作；不要從頭重做。"}}
JSON
fi
