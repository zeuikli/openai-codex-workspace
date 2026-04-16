#!/usr/bin/env bash
# Per-turn caveman mode reinforcement hook.
#
# Inspired by JuliusBrussee/caveman caveman-mode-tracker.js:
#   "The SessionStart hook injects the full ruleset once, but models lose it
#    when other plugins inject competing style instructions every turn.
#    This keeps caveman visible in the model's attention on every user message."
#
# Injects ~28 tokens per turn to prevent mid-session drift back to verbose.
# Event: UserPromptSubmit (Claude Code) — may not be supported in Codex CLI.
# If unsupported, this hook is silently ignored.
set -euo pipefail

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"UserPromptSubmit","additionalContext":"CAVEMAN ACTIVE (auto). Drop articles/filler/pleasantries/hedging. Fragments OK. Security/destructive: write normal."}}
JSON
