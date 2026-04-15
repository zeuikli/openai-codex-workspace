#!/usr/bin/env bash
set -euo pipefail

payload="$(cat)"
command="$(printf '%s' "$payload" | python3 -c 'import sys,json
try:
    data=json.load(sys.stdin)
    print(((data.get("tool_input") or {}).get("command")) or "")
except Exception:
    print("")')"

if [[ -z "$command" ]]; then
  exit 0
fi

reason=""

if [[ "$command" =~ (^|[[:space:]])git[[:space:]]+push([[:space:]]|$) ]]; then
  # Push policy:
  # - allow: git push [remote] <feature-branch>, where branch matches codex/* or feature/*
  # - deny:  push to main/master (or unknown branch)
  # This keeps "agent can push feature branches" while protecting default branches.
  remote="origin"
  branch=""
  # shellcheck disable=SC2206
  parts=($command)
  for ((i=0; i<${#parts[@]}; i++)); do
    token="${parts[$i]}"
    if [[ "$token" == "push" ]]; then
      # parse non-flag args after "push"
      non_flags=()
      for ((j=i+1; j<${#parts[@]}; j++)); do
        t="${parts[$j]}"
        if [[ "$t" == -* ]]; then
          continue
        fi
        non_flags+=("$t")
      done
      if (( ${#non_flags[@]} >= 1 )); then
        remote="${non_flags[0]}"
      fi
      if (( ${#non_flags[@]} >= 2 )); then
        branch="${non_flags[1]}"
      fi
      break
    fi
  done

  # branch omitted -> deny (avoid pushing current branch without explicit target)
  if [[ -z "$branch" ]]; then
    reason="Blocked git push without explicit branch. Allowed: git push <remote> codex/* or feature/*"
  elif [[ "$branch" =~ ^(main|master)$ ]]; then
    reason="Blocked git push to protected branch: $branch"
  elif [[ "$branch" =~ ^(codex|feature)/.+$ ]]; then
    # optional remote guard
    if [[ ! "$remote" =~ ^(origin|upstream)$ ]]; then
      reason="Blocked git push to untrusted remote: $remote"
    fi
  else
    reason="Blocked git push to non-feature branch: $branch (allowed: codex/* or feature/*)"
  fi
elif [[ "$command" =~ (^|[[:space:]])git[[:space:]]+reset[[:space:]]+--hard([[:space:]]|$) ]]; then
  reason="Blocked destructive git reset --hard command."
elif [[ "$command" =~ rm[[:space:]]+-rf[[:space:]]+/([[:space:]]|$) ]]; then
  reason="Blocked destructive rm -rf / pattern."
elif [[ "$command" =~ curl[^\|]*\|[[:space:]]*(sh|bash) ]]; then
  reason="Blocked curl pipe to shell pattern."
elif [[ "$command" =~ wget[^\|]*\|[[:space:]]*(sh|bash) ]]; then
  reason="Blocked wget pipe to shell pattern."
fi

if [[ -n "$reason" ]]; then
  cat <<JSON
{"systemMessage":"Repository hook blocked an unsafe Bash command.","hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"deny","permissionDecisionReason":"$reason"}}
JSON
fi
