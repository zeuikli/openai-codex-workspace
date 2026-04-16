#!/usr/bin/env python3
"""
Caveman compression benchmark for OpenAI Codex Workspace.
Tests models × compression levels and records real API metrics.

Usage:
    OPENAI_API_KEY=<key> python3 benchmarks/caveman_benchmark.py

Results are written to benchmarks/results/caveman_benchmark_results.json
and benchmarks/results/caveman_benchmark_report.md
"""
import os
import sys
import json
import time
import datetime
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai package not installed. Run: pip install openai")
    sys.exit(1)

# ──────────────────────────────────────────
# Config
# ──────────────────────────────────────────
MODELS = [
    "gpt-5.4",
    "gpt-5.4-mini",
    "gpt-5.4-nano",
    "gpt-5.2",       # gpt-5.3-codex is a completion model (not chat); gpt-5.2 is nearest chat substitute
]

# Display names — note the substitution for gpt-5.3-codex
MODEL_DISPLAY = {
    "gpt-5.4":      "gpt-5.4",
    "gpt-5.4-mini": "gpt-5.4-mini",
    "gpt-5.4-nano": "gpt-5.4-nano",
    "gpt-5.2":      "gpt-5.3-codex → gpt-5.2 (codex variants are completion-only models)",
}

# Caveman system prompts per compression level
CAVEMAN_PROMPTS = {
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

# Test prompts (subset from benchmarks/prompts/en.txt)
TEST_PROMPTS = [
    "Why does my React component re-render every time the parent updates?",
    "Explain database connection pooling.",
    "What's the difference between TCP and UDP?",
    "How do I fix a memory leak in a long-running Node.js process?",
    "What does the SQL EXPLAIN command tell me?",
]

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_JSON = RESULTS_DIR / "caveman_benchmark_results.json"
RESULTS_MD   = RESULTS_DIR / "caveman_benchmark_report.md"


def count_words(text: str) -> int:
    return len(text.split())


def count_chars(text: str) -> int:
    return len(text)


def run_single(client: OpenAI, model: str, level: str, prompt: str) -> dict:
    system = CAVEMAN_PROMPTS[level]
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
            "latency_ms": latency_ms,
            "input_tokens":  usage.prompt_tokens,
            "output_tokens": usage.completion_tokens,
            "total_tokens":  usage.total_tokens,
            "output_words":  count_words(content),
            "output_chars":  count_chars(content),
            "content":       content,
            "error":         None,
        }
    except Exception as e:
        latency_ms = round((time.monotonic() - t0) * 1000)
        return {
            "ok": False,
            "latency_ms": latency_ms,
            "input_tokens":  0,
            "output_tokens": 0,
            "total_tokens":  0,
            "output_words":  0,
            "output_chars":  0,
            "content":       "",
            "error":         str(e),
        }


def compute_reduction(baseline: float, compressed: float) -> float:
    if baseline <= 0:
        return 0.0
    return round((baseline - compressed) / baseline * 100, 1)


def run_benchmark(api_key: str) -> dict:
    client = OpenAI(api_key=api_key)
    results = {}
    levels = ["none", "lite", "full", "ultra"]

    total_runs = len(MODELS) * len(levels) * len(TEST_PROMPTS)
    run_n = 0

    print(f"\nRunning {total_runs} API calls ({len(MODELS)} models × {len(levels)} levels × {len(TEST_PROMPTS)} prompts)")
    print("=" * 60)

    for model in MODELS:
        results[model] = {}
        for level in levels:
            results[model][level] = []
            for prompt in TEST_PROMPTS:
                run_n += 1
                print(f"[{run_n:3d}/{total_runs}] {model} / {level:5s} / {prompt[:45]}...")
                r = run_single(client, model, level, prompt)
                r["prompt"] = prompt
                results[model][level].append(r)
                if r["ok"]:
                    print(f"         → {r['output_tokens']} out-tokens, {r['output_words']} words, {r['latency_ms']}ms")
                else:
                    print(f"         → ERROR: {r['error'][:80]}")
                # Avoid rate limits
                time.sleep(0.5)

    return results


def aggregate(runs: list[dict]) -> dict:
    ok_runs = [r for r in runs if r["ok"]]
    if not ok_runs:
        return {"ok": False, "n": 0}
    n = len(ok_runs)
    return {
        "ok": True,
        "n": n,
        "avg_output_tokens": round(sum(r["output_tokens"] for r in ok_runs) / n, 1),
        "avg_output_words":  round(sum(r["output_words"]  for r in ok_runs) / n, 1),
        "avg_latency_ms":    round(sum(r["latency_ms"]    for r in ok_runs) / n, 1),
        "avg_input_tokens":  round(sum(r["input_tokens"]  for r in ok_runs) / n, 1),
        "errors":            len(runs) - n,
    }


def build_report(results: dict, run_at: str) -> str:
    lines = []
    lines.append("# Caveman Compression Benchmark Report")
    lines.append(f"\n**Run at:** {run_at}")
    lines.append(f"**Prompts:** {len(TEST_PROMPTS)} standard technical questions")
    lines.append(f"**Compression levels:** none (baseline) · lite · full · ultra\n")

    lines.append("## Architecture Decision: AGENTS vs SKILL vs Hooks\n")
    lines.append(
        "For this OpenAI Codex Workspace, **SKILL** is the right primitive for caveman:\n\n"
        "| Primitive | Best for | Caveman fit |\n"
        "|-----------|----------|-------------|\n"
        "| **SKILL** | On-demand behaviour loaded per-task; user-invocable via `/caveman` | ✅ **Best** — loaded only when needed, supports multiple intensity variants, progressive disclosure |\n"
        "| **Hooks** | Always-on session-start or per-turn side-effects | ⚠️ Partial — good for SessionStart flag + statusline, but Codex hooks still experimental |\n"
        "| **AGENTS.md** | Persistent standing rules for every task | ⚠️ Too broad — bakes compression into every agent, wastes tokens when not wanted |\n\n"
        "**Recommended pattern for Codex:** SKILL as primary interface + Hook for SessionStart flag write + AGENTS.md one-liner reference.\n"
    )

    lines.append("## Results by Model\n")

    for model in MODELS:
        display = MODEL_DISPLAY.get(model, model)
        lines.append(f"### {display}\n")

        # Table header
        lines.append("| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |")
        lines.append("|-------|-------------------|-----------|------------------|-------------------------|--------|")

        aggs = {}
        for level in ["none", "lite", "full", "ultra"]:
            aggs[level] = aggregate(results.get(model, {}).get(level, []))

        baseline_tokens = aggs["none"]["avg_output_tokens"] if aggs["none"]["ok"] else 0
        baseline_words  = aggs["none"]["avg_output_words"]  if aggs["none"]["ok"] else 0

        for level in ["none", "lite", "full", "ultra"]:
            a = aggs[level]
            if not a["ok"]:
                lines.append(f"| {level} | — | — | — | — | {a.get('errors', 'all')} |")
                continue
            tok_reduction = compute_reduction(baseline_tokens, a["avg_output_tokens"]) if level != "none" else "—"
            reduction_str = f"{tok_reduction}%" if isinstance(tok_reduction, float) else tok_reduction
            lines.append(
                f"| {level} | {a['avg_output_tokens']} | {a['avg_output_words']} | "
                f"{a['avg_latency_ms']} | {reduction_str} | {a['errors']} |"
            )
        lines.append("")

    lines.append("## Cross-Model Summary (full compression level)\n")
    lines.append("| Model | Avg Output Tokens (full) | Token Reduction vs None | Avg Latency (ms) |")
    lines.append("|-------|--------------------------|-------------------------|------------------|")

    for model in MODELS:
        display = MODEL_DISPLAY.get(model, model)
        none_agg = aggregate(results.get(model, {}).get("none", []))
        full_agg = aggregate(results.get(model, {}).get("full", []))
        if not full_agg["ok"] or not none_agg["ok"]:
            lines.append(f"| {display} | — | — | — |")
            continue
        reduction = compute_reduction(none_agg["avg_output_tokens"], full_agg["avg_output_tokens"])
        lines.append(
            f"| {display} | {full_agg['avg_output_tokens']} | {reduction}% | {full_agg['avg_latency_ms']} |"
        )

    lines.append("")
    lines.append("## Sample Outputs (first prompt)\n")
    first_prompt = TEST_PROMPTS[0]
    lines.append(f"**Prompt:** `{first_prompt}`\n")

    for model in MODELS[:2]:  # Show first 2 models to keep report readable
        display = MODEL_DISPLAY.get(model, model)
        lines.append(f"### {display}\n")
        for level in ["none", "full", "ultra"]:
            runs = results.get(model, {}).get(level, [])
            if runs and runs[0]["ok"]:
                content = runs[0]["content"].strip()
                # Truncate very long outputs
                if len(content) > 400:
                    content = content[:400] + "…"
                lines.append(f"**{level}:** {content}\n")

    lines.append("---")
    lines.append(f"*Generated by `benchmarks/caveman_benchmark.py` · {run_at}*")

    return "\n".join(lines)


def main():
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set.")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    run_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    print(f"\nCaveman Benchmark — {run_at}")
    print(f"Models: {', '.join(MODELS)}")
    print(f"Levels: none, lite, full, ultra")

    results = run_benchmark(api_key)

    # Save raw JSON (no API key inside)
    with open(RESULTS_JSON, "w") as f:
        json.dump({"run_at": run_at, "models": MODELS, "results": results}, f, indent=2)
    print(f"\nRaw results → {RESULTS_JSON}")

    # Build and save Markdown report
    report = build_report(results, run_at)
    with open(RESULTS_MD, "w") as f:
        f.write(report)
    print(f"Report      → {RESULTS_MD}")

    return results


if __name__ == "__main__":
    main()
