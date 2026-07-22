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
high_risk = r"付款|扣款|payment|charge|retry|重試|刪除|delete|drop|migration|遷移|queue|佇列|consumer|auth|授權|production|正式環境"
mitigation = r"冪等|idempot|重複|duplicate|回滾|rollback|補償|compensat|未見輸入|consequence|風險"
if re.search(high_risk, text, re.I) and not re.search(mitigation, text, re.I):
    raise SystemExit(1)
raise SystemExit(0)' <<<"$payload"; then
  exit 0
fi

printf '%s\n' '{"systemMessage":"v4 advisory: high-risk domain detected without an explicit idempotency, rollback/compensation, duplicate-execution, or unseen-input consequence check; run Blindspot Pass.","hookSpecificOutput":{"hookEventName":"UserPromptSubmit"}}'
exit 1
