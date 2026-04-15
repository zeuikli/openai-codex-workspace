#!/usr/bin/env bash
set -euo pipefail

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"This repository is Codex-native. Use .codex/agents for subagents and .agents/skills for reusable workflows. Prefer safe Bash commands and avoid destructive operations without approval. Treat the nine Karpathy principles (AGENTS.md → Karpathy 實作原則) as hard rules: surface assumptions, push back on conflicts, naive-first before optimize, declare Done when criteria before acting, keep blast radius minimal."}}
JSON
