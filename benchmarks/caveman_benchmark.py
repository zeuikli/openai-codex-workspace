#!/usr/bin/env python3
"""
Caveman compression benchmark for OpenAI Codex Workspace.
Tests models × compression levels and records real API metrics.

Models:
  gpt-5.4, gpt-5.4-mini, gpt-5.4-nano  → Chat Completions API
  gpt-5.3-codex                         → Responses API (completion model)

Levels: none (baseline) · lite · full · ultra

Usage:
    # Load key from .env.local (never committed to git)
    python3 benchmarks/caveman_benchmark.py

    # Or pass key directly via env
    OPENAI_API_KEY=<key> python3 benchmarks/caveman_benchmark.py

Results:
    benchmarks/results/caveman_benchmark_results.json
    benchmarks/results/caveman_benchmark_report.md
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── Load .env.local (never overwrites existing env vars) ──────────────────────
_env_local = ROOT / ".env.local"
if _env_local.exists():
    for _line in _env_local.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

# ── Model config ──────────────────────────────────────────────────────────────
# Chat models → completions API
CHAT_MODELS = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano"]
# Completion model → Responses API
RESPONSES_MODELS = ["gpt-5.3-codex"]

ALL_MODELS = CHAT_MODELS + RESPONSES_MODELS

MODEL_DISPLAY = {
    "gpt-5.4":        "gpt-5.4",
    "gpt-5.4-mini":   "gpt-5.4-mini",
    "gpt-5.4-nano":   "gpt-5.4-nano",
    "gpt-5.3-codex":  "gpt-5.3-codex (Responses API)",
}

# ── Caveman system prompts ────────────────────────────────────────────────────
CAVEMAN_SYSTEM = {
    "none": (
        "You are a helpful technical assistant. Respond clearly and completely."
    ),
    "lite": (
        "CAVEMAN MODE: lite. Drop filler words and hedging. Keep articles and full sentences. "
        "Professional but tight. No pleasantries."
    ),
    "full": (
        "CAVEMAN MODE: full. Drop articles (a/an/the), filler (just/really/basically/actually/simply), "
        "pleasantries, hedging. Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged."
    ),
    "ultra": (
        "CAVEMAN MODE: ultra. Maximum compression. Abbreviate (DB/auth/config/req/res/fn/impl). "
        "Strip conjunctions. Arrows for causality (X→Y). One word when one word enough. Telegraphic."
    ),
}

LEVELS = ["none", "lite", "full", "ultra"]

# ── Test prompts ──────────────────────────────────────────────────────────────
TEST_PROMPTS = [
    "Why does my React component re-render every time the parent updates?",
    "Explain database connection pooling.",
    "What's the difference between TCP and UDP?",
    "How do I fix a memory leak in a long-running Node.js process?",
    "What does the SQL EXPLAIN command tell me?",
]

RESULTS_DIR  = Path(__file__).parent / "results"
RESULTS_JSON = RESULTS_DIR / "caveman_benchmark_results.json"
RESULTS_MD   = RESULTS_DIR / "caveman_benchmark_report.md"


# ── Helpers ───────────────────────────────────────────────────────────────────
def count_words(text: str) -> int:
    return len(text.split())


def count_chars(text: str) -> int:
    return len(text)


def compute_reduction(baseline: float, compressed: float) -> float:
    if baseline <= 0:
        return 0.0
    return round((baseline - compressed) / baseline * 100, 1)


# ── API calls ─────────────────────────────────────────────────────────────────
def run_chat(client: OpenAI, model: str, level: str, prompt: str) -> dict:
    system = CAVEMAN_SYSTEM[level]
    t0 = time.monotonic()
    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_completion_tokens=512,
            temperature=0,
        )
        latency_ms = round((time.monotonic() - t0) * 1000)
        content = resp.choices[0].message.content or ""
        usage = resp.usage
        return {
            "ok": True,
            "latency_ms":    latency_ms,
            "input_tokens":  usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens":  usage.total_tokens,
            "output_words":  count_words(content),
            "output_chars":  count_chars(content),
            "content":       content,
            "error":         None,
        }
    except Exception as e:
        return _error_result(time.monotonic() - t0, str(e))


def run_responses(client: OpenAI, model: str, level: str, prompt: str) -> dict:
    """Responses API for completion models like gpt-5.3-codex."""
    system = CAVEMAN_SYSTEM[level]
    full_input = f"{system}\n\n{prompt}"
    t0 = time.monotonic()
    try:
        resp = client.responses.create(
            model=model,
            input=full_input,
            max_output_tokens=512,
        )
        latency_ms = round((time.monotonic() - t0) * 1000)
        content = resp.output_text or ""
        usage = resp.usage
        return {
            "ok": True,
            "latency_ms":    latency_ms,
            "input_tokens":  getattr(usage, "input_tokens", 0),
            "output_tokens": getattr(usage, "output_tokens", 0),
            "total_tokens":  getattr(usage, "total_tokens", 0),
            "output_words":  count_words(content),
            "output_chars":  count_chars(content),
            "content":       content,
            "error":         None,
        }
    except Exception as e:
        return _error_result(time.monotonic() - t0, str(e))


def _error_result(elapsed_s: float, error: str) -> dict:
    return {
        "ok": False,
        "latency_ms":    round(elapsed_s * 1000),
        "input_tokens":  0,
        "output_tokens": 0,
        "total_tokens":  0,
        "output_words":  0,
        "output_chars":  0,
        "content":       "",
        "error":         error,
    }


def run_single(client: OpenAI, model: str, level: str, prompt: str) -> dict:
    if model in RESPONSES_MODELS:
        return run_responses(client, model, level, prompt)
    return run_chat(client, model, level, prompt)


# ── Benchmark runner ──────────────────────────────────────────────────────────
def run_benchmark(api_key: str) -> dict:
    client = OpenAI(api_key=api_key)
    results: dict = {}
    total_runs = len(ALL_MODELS) * len(LEVELS) * len(TEST_PROMPTS)
    run_n = 0

    print(f"\nRunning {total_runs} API calls "
          f"({len(ALL_MODELS)} models × {len(LEVELS)} levels × {len(TEST_PROMPTS)} prompts)")
    print("=" * 70)

    for model in ALL_MODELS:
        results[model] = {}
        for level in LEVELS:
            results[model][level] = []
            for prompt in TEST_PROMPTS:
                run_n += 1
                api_type = "responses" if model in RESPONSES_MODELS else "chat"
                print(f"[{run_n:3d}/{total_runs}] {model} ({api_type}) / {level:5s} / {prompt[:40]}…")
                r = run_single(client, model, level, prompt)
                r["prompt"] = prompt
                results[model][level].append(r)
                if r["ok"]:
                    print(f"         → {r['output_tokens']:4d} out-tok  "
                          f"{r['output_words']:4d} words  {r['latency_ms']}ms")
                else:
                    print(f"         → ERROR: {r['error'][:80]}")
                time.sleep(0.4)  # rate-limit headroom

    return results


# ── Aggregation ───────────────────────────────────────────────────────────────
def aggregate(runs: list[dict]) -> dict:
    ok_runs = [r for r in runs if r["ok"]]
    if not ok_runs:
        return {"ok": False, "n": 0, "errors": len(runs)}
    n = len(ok_runs)
    return {
        "ok":               True,
        "n":                n,
        "avg_output_tokens": round(sum(r["output_tokens"] for r in ok_runs) / n, 1),
        "avg_output_words":  round(sum(r["output_words"]  for r in ok_runs) / n, 1),
        "avg_latency_ms":    round(sum(r["latency_ms"]    for r in ok_runs) / n, 1),
        "avg_input_tokens":  round(sum(r["input_tokens"]  for r in ok_runs) / n, 1),
        "errors":            len(runs) - n,
    }


# ── Report builder ────────────────────────────────────────────────────────────
def build_report(results: dict, run_at: str) -> str:
    lines: list[str] = []
    lines += [
        "# Caveman Compression Benchmark Report",
        f"\n**Run at:** {run_at}",
        f"**Prompts:** {len(TEST_PROMPTS)} standard technical questions",
        f"**Models:** {' · '.join(ALL_MODELS)}",
        f"**Compression levels:** none (baseline) · lite · full · ultra",
        "",
    ]

    lines += [
        "## Architecture Decision: AGENTS vs SKILL vs Hooks",
        "",
        "| Primitive | Best for | Caveman fit |",
        "|-----------|----------|-------------|",
        "| **SKILL** | On-demand, user-invocable via `/caveman` | ✅ **Best** — loaded only when needed, multi-level, progressive disclosure |",
        "| **Hooks** | SessionStart flag + statusline | ⚠️ Partial — good for activation, hooks still experimental |",
        "| **AGENTS.md** | Persistent standing rules | ⚠️ Too broad — bakes compression into every agent |",
        "",
        "> **Recommended pattern:** SKILL as primary interface + Hook for SessionStart flag + AGENTS.md one-liner reference.",
        "",
    ]

    lines.append("## Results by Model\n")

    for model in ALL_MODELS:
        display = MODEL_DISPLAY.get(model, model)
        lines.append(f"### {display}\n")
        lines += [
            "| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |",
            "|-------|----------------|-----------|------------------|-------------------------|--------|",
        ]
        aggs = {lvl: aggregate(results.get(model, {}).get(lvl, [])) for lvl in LEVELS}
        baseline_tokens = aggs["none"]["avg_output_tokens"] if aggs["none"]["ok"] else 0

        for level in LEVELS:
            a = aggs[level]
            if not a["ok"]:
                lines.append(f"| {level} | — | — | — | — | {a.get('errors', 'all')} |")
                continue
            if level == "none":
                reduction_str = "— (baseline)"
            else:
                r = compute_reduction(baseline_tokens, a["avg_output_tokens"])
                reduction_str = f"**{r:+.1f}%**" if r < 0 else f"{r:.1f}%"
            lines.append(
                f"| {level} | {a['avg_output_tokens']} | {a['avg_output_words']} | "
                f"{a['avg_latency_ms']} | {reduction_str} | {a['errors']} |"
            )
        lines.append("")

    # Cross-model summary
    lines += [
        "## Cross-Model Summary\n",
        "### Token Reduction at Each Compression Level vs None (baseline)\n",
        "| Model | None (baseline) | lite | full | ultra | Best reduction |",
        "|-------|----------------|------|------|-------|----------------|",
    ]
    for model in ALL_MODELS:
        display = MODEL_DISPLAY.get(model, model)
        none_a = aggregate(results.get(model, {}).get("none", []))
        base = none_a["avg_output_tokens"] if none_a["ok"] else 0
        cells = [f"{base:.0f}"]
        best = 0.0
        for lvl in ["lite", "full", "ultra"]:
            a = aggregate(results.get(model, {}).get(lvl, []))
            if a["ok"] and base > 0:
                r = compute_reduction(base, a["avg_output_tokens"])
                cells.append(f"{r:.1f}%")
                if r > best:
                    best = r
            else:
                cells.append("—")
        cells.append(f"**{best:.1f}%**")
        lines.append(f"| {display} | " + " | ".join(cells) + " |")

    lines.append("")

    # Latency summary
    lines += [
        "### Average Latency at `full` Level (ms)\n",
        "| Model | Avg Latency (ms) |",
        "|-------|-----------------|",
    ]
    for model in ALL_MODELS:
        display = MODEL_DISPLAY.get(model, model)
        a = aggregate(results.get(model, {}).get("full", []))
        lat = f"{a['avg_latency_ms']}" if a["ok"] else "—"
        lines.append(f"| {display} | {lat} |")
    lines.append("")

    # Sample outputs
    lines += [
        "## Sample Outputs (first prompt)\n",
        f"**Prompt:** `{TEST_PROMPTS[0]}`\n",
    ]
    for model in ALL_MODELS[:2]:
        display = MODEL_DISPLAY.get(model, model)
        lines.append(f"### {display}\n")
        for level in ["none", "full", "ultra"]:
            runs = results.get(model, {}).get(level, [])
            if runs and runs[0]["ok"]:
                content = runs[0]["content"].strip()
                if len(content) > 500:
                    content = content[:500] + "…"
                lines.append(f"**{level}:** {content}\n")

    lines += [
        "---",
        f"*Generated by `benchmarks/caveman_benchmark.py` · {run_at}*",
        "*gpt-5.3-codex benchmarked via OpenAI Responses API*",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Add to .env.local or export before running.")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    print(f"\nCaveman Benchmark — {run_at}")
    print(f"Chat models : {', '.join(CHAT_MODELS)}")
    print(f"Codex model : {', '.join(RESPONSES_MODELS)} (Responses API)")
    print(f"Levels      : {', '.join(LEVELS)}")

    results = run_benchmark(api_key)

    with open(RESULTS_JSON, "w") as f:
        json.dump(
            {"run_at": run_at, "models": ALL_MODELS, "levels": LEVELS, "results": results},
            f,
            indent=2,
        )
    print(f"\nRaw results → {RESULTS_JSON}")

    report = build_report(results, run_at)
    with open(RESULTS_MD, "w") as f:
        f.write(report)
    print(f"Report      → {RESULTS_MD}")

    # Print quick summary
    print("\n── Quick Summary (avg output tokens at `full` level) ──")
    for model in ALL_MODELS:
        none_a = aggregate(results.get(model, {}).get("none", []))
        full_a = aggregate(results.get(model, {}).get("full", []))
        if full_a["ok"] and none_a["ok"]:
            r = compute_reduction(none_a["avg_output_tokens"], full_a["avg_output_tokens"])
            print(f"  {model:<20} none={none_a['avg_output_tokens']:6.1f}  full={full_a['avg_output_tokens']:6.1f}  reduction={r:.1f}%")
        else:
            err = full_a if not full_a["ok"] else none_a
            print(f"  {model:<20} ERROR — {err}")


if __name__ == "__main__":
    main()
