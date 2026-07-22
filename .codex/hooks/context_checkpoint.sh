#!/usr/bin/env bash
set -euo pipefail

phase="${1:-post}"
cat >/dev/null

if [[ "$phase" == "pre" ]]; then
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PreCompact","additionalContext":"v4 checkpoint：保留 Goal、Done-when、已驗證 receipt、未完成風險、Deviations、G-LoopA 狀態與工作樹狀態；Memory consolidation 不得覆寫原始 evidence。"}}
JSON
else
  cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"PostCompact","additionalContext":"v4 resume：先重讀 AGENTS.md、Memory.md、HARNESS-THE-LOOP.md，核對最新需求、Done-when、驗證 receipt、git status 與最新 diff；以外部 state anchor 為準，不從壓縮摘要猜測目標。"}}
JSON
fi
