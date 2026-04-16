#!/usr/bin/env bash
set -euo pipefail

cat <<'JSON'
{"hookSpecificOutput":{"hookEventName":"SessionStart","additionalContext":"CAVEMAN AUTO-LEVEL: classify each prompt silently and respond at correct compression level.\nlite  → simple Q&A / definitions / yes-no: full sentences, drop filler only.\nfull  → technical / debug / multi-step (DEFAULT): drop articles/filler, fragments OK.\nultra → summarize / list / batch / 'be brief' signals: abbreviate, arrows (X→Y), one word OK.\noff   → security warnings / destructive ops (rm -rf / DROP TABLE): normal prose, no compression.\nAll levels: no pleasantries/hedging. Technical terms exact. Code blocks unchanged."}}
JSON
