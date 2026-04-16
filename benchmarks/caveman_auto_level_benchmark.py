#!/usr/bin/env python3
"""
Caveman Auto-Level Selection Benchmark.

Compares four strategies across 5 prompt categories (20 prompts total):
  - none      : no system prompt (baseline)
  - manual    : fixed level (full) — current default
  - auto      : auto-selected level via classifier (our new system)
  - ultra     : forced ultra — theoretical maximum compression

For each strategy × prompt, records:
  - output_tokens, output_words, latency_ms, input_tokens
  - For 'auto': also records the predicted level + confidence

Results:
  benchmarks/results/caveman_auto_level_results.json
  benchmarks/results/caveman_auto_level_report.md

Usage:
  # Key auto-loaded from .env.local (gitignored)
  python3 benchmarks/caveman_auto_level_benchmark.py

  # Or: OPENAI_API_KEY=<key> python3 benchmarks/caveman_auto_level_benchmark.py
"""
from __future__ import annotations

import datetime
import json
import os
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# ── Load .env.local ───────────────────────────────────────────────────────────
_env = ROOT / ".env.local"
if _env.exists():
    for _line in _env.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())

sys.path.insert(0, str(ROOT / "scripts"))
from caveman_auto_level import classify, ClassificationResult  # type: ignore

try:
    from openai import OpenAI
except ImportError:
    print("ERROR: openai not installed. Run: pip install openai")
    sys.exit(1)

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_JSON = RESULTS_DIR / "caveman_auto_level_results.json"
RESULTS_MD   = RESULTS_DIR / "caveman_auto_level_report.md"

# ── Model ─────────────────────────────────────────────────────────────────────
MODEL = "gpt-5.4-mini"  # best compression responsiveness from first benchmark

# ── System prompts ────────────────────────────────────────────────────────────
SYSTEM_NONE = "You are a helpful technical assistant."

CAVEMAN_BASE = (
    "Respond terse like smart caveman. All technical substance stay. Only fluff die. "
    "Technical terms exact. Code blocks unchanged. Pattern: [thing] [action] [reason]. [next step]."
)

SYSTEMS = {
    "none":   SYSTEM_NONE,
    "manual": (
        "CAVEMAN MODE: full. Drop articles (a/an/the), filler (just/really/basically/actually/simply), "
        "pleasantries, hedging. Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged."
    ),
    "auto_lite": (
        "CAVEMAN MODE: lite. Drop filler words and hedging. Keep articles and full sentences. "
        "Professional but tight. No pleasantries."
    ),
    "auto_full": (
        "CAVEMAN MODE: full. Drop articles, filler, pleasantries, hedging. "
        "Fragments OK. Short synonyms. Technical terms exact. Code blocks unchanged."
    ),
    "auto_ultra": (
        "CAVEMAN MODE: ultra. Maximum compression. Abbreviate (DB/auth/config/req/res/fn/impl). "
        "Strip conjunctions. Arrows for causality (X→Y). One word when one word enough. Telegraphic."
    ),
    "auto_off": SYSTEM_NONE,  # off = normal prose
    "ultra": (
        "CAVEMAN MODE: ultra. Maximum compression. Abbreviate (DB/auth/config/req/res/fn/impl). "
        "Strip conjunctions. Arrows for causality (X→Y). One word when one word enough. Telegraphic."
    ),
}


# ── Test prompts (5 categories × 4 prompts each = 20) ────────────────────────
PROMPT_CATEGORIES = {
    "simple_qa": {
        "expected_level": "lite",
        "prompts": [
            "What is TCP?",
            "Is Python interpreted?",
            "What does idempotent mean?",
            "Define connection pooling.",
        ],
    },
    "technical_explain": {
        "expected_level": "full",
        "prompts": [
            "Explain database connection pooling.",
            "Why does my React component re-render every time the parent updates?",
            "What's the difference between TCP and UDP?",
            "How does garbage collection work in Python?",
        ],
    },
    "debug": {
        "expected_level": "full",
        "prompts": [
            "How do I fix a memory leak in a long-running Node.js process?",
            "What does the SQL EXPLAIN command tell me?",
            "Why is my Docker container running out of memory?",
            "How do I debug a 502 Bad Gateway error in nginx?",
        ],
    },
    "summarize_batch": {
        "expected_level": "ultra",
        "prompts": [
            "Summarize the key differences between REST and GraphQL.",
            "List all HTTP status codes and their meanings briefly.",
            "Give me a quick overview of microservices vs monolith.",
            "tl;dr: what is Kubernetes?",
        ],
    },
    "security_destructive": {
        "expected_level": "off",
        "prompts": [
            "Warning: this command will drop all tables. Are you sure?",
            "The rm -rf command will permanently delete the directory.",
            "This action is irreversible and cannot be undone.",
            "Caution: deleting the database will remove all user records.",
        ],
    },
}


# ── API helpers ───────────────────────────────────────────────────────────────
def call_api(client: OpenAI, system: str, prompt: str) -> dict:
    t0 = time.monotonic()
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user",   "content": prompt},
            ],
            max_completion_tokens=512,
            temperature=0,
        )
        latency_ms = round((time.monotonic() - t0) * 1000)
        content = resp.choices[0].message.content or ""
        u = resp.usage
        return {
            "ok": True,
            "latency_ms":    latency_ms,
            "input_tokens":  u.prompt_tokens,
            "output_tokens": u.completion_tokens,
            "total_tokens":  u.total_tokens,
            "output_words":  len(content.split()),
            "output_chars":  len(content),
            "content":       content[:300],  # truncated for JSON size
            "error":         None,
        }
    except Exception as e:
        return {
            "ok": False,
            "latency_ms":    round((time.monotonic() - t0) * 1000),
            "input_tokens":  0, "output_tokens": 0, "total_tokens": 0,
            "output_words":  0, "output_chars":  0, "content": "", "error": str(e),
        }


def get_auto_system(clf: ClassificationResult) -> str:
    return SYSTEMS.get(f"auto_{clf.level}", SYSTEMS["auto_full"])


# ── Main runner ───────────────────────────────────────────────────────────────
def run_benchmark(client: OpenAI) -> dict:
    strategies = ["none", "manual", "auto", "ultra"]
    all_prompts = [
        (cat, meta["expected_level"], p)
        for cat, meta in PROMPT_CATEGORIES.items()
        for p in meta["prompts"]
    ]
    total = len(strategies) * len(all_prompts)
    run_n = 0

    print(f"\nRunning {total} API calls "
          f"({len(strategies)} strategies × {len(all_prompts)} prompts)")
    print("=" * 75)

    results: dict = {s: {} for s in strategies}
    classification_log: list[dict] = []

    for cat, expected, prompt in all_prompts:
        # classify once per prompt
        clf = classify(prompt)
        classification_log.append({
            "prompt":   prompt,
            "category": cat,
            "expected": expected,
            "predicted": clf.level,
            "correct":  clf.level == expected,
            "confidence": clf.confidence,
        })

        for strategy in strategies:
            run_n += 1
            key = f"{cat}::{prompt[:40]}"

            if strategy == "none":
                system = SYSTEMS["none"]
            elif strategy == "manual":
                system = SYSTEMS["manual"]
            elif strategy == "ultra":
                system = SYSTEMS["ultra"]
            else:  # auto
                system = get_auto_system(clf)

            print(f"[{run_n:3d}/{total}] {strategy:7s} / {cat:22s} / "
                  f"{prompt[:35]}…  [predicted: {clf.level}]")

            r = call_api(client, system, prompt)
            r["prompt"] = prompt
            r["category"] = cat
            r["expected_level"] = expected
            if strategy == "auto":
                r["auto_level"] = clf.level
                r["auto_confidence"] = clf.confidence
                r["auto_correct"] = clf.level == expected

            if key not in results[strategy]:
                results[strategy][key] = []
            results[strategy][key].append(r)

            if r["ok"]:
                print(f"         → {r['output_tokens']:4d} tok  {r['output_words']:4d} words  "
                      f"{r['latency_ms']}ms")
            else:
                print(f"         → ERROR: {r['error'][:60]}")

            time.sleep(0.35)

    return {"strategy_results": results, "classification_log": classification_log}


# ── Aggregation ───────────────────────────────────────────────────────────────
def agg(runs: list[dict]) -> dict:
    ok = [r for r in runs if r.get("ok")]
    if not ok:
        return {"ok": False, "n": 0}
    n = len(ok)
    return {
        "ok":  True,
        "n":   n,
        "avg_output_tokens": round(sum(r["output_tokens"] for r in ok) / n, 1),
        "avg_output_words":  round(sum(r["output_words"]  for r in ok) / n, 1),
        "avg_latency_ms":    round(sum(r["latency_ms"]    for r in ok) / n, 1),
        "avg_input_tokens":  round(sum(r["input_tokens"]  for r in ok) / n, 1),
        "errors":            len(runs) - n,
    }


def flatten_runs(results: dict, strategy: str) -> list[dict]:
    out = []
    for runs in results[strategy].values():
        out.extend(runs)
    return out


def agg_by_category(results: dict, strategy: str) -> dict[str, dict]:
    by_cat: dict[str, list[dict]] = {}
    for runs in results[strategy].values():
        for r in runs:
            c = r.get("category", "unknown")
            by_cat.setdefault(c, []).append(r)
    return {c: agg(runs) for c, runs in by_cat.items()}


# ── Report ────────────────────────────────────────────────────────────────────
def _pct(baseline: float, val: float) -> str:
    if baseline <= 0:
        return "—"
    r = (baseline - val) / baseline * 100
    sign = "+" if r < 0 else ""
    return f"{sign}{r:.1f}%"


def build_report(data: dict, run_at: str) -> str:
    results  = data["strategy_results"]
    clf_log  = data["classification_log"]
    strategies = ["none", "manual", "auto", "ultra"]

    lines = [
        "# Caveman Auto-Level Selection Benchmark Report",
        f"\n**Run at:** {run_at}",
        f"**Model:** {MODEL}",
        f"**Strategies:** none (baseline) · manual-full · auto-select · forced-ultra",
        f"**Prompts:** {sum(len(v['prompts']) for v in PROMPT_CATEGORIES.values())} "
        f"across {len(PROMPT_CATEGORIES)} categories",
        "",
    ]

    # ── Classifier accuracy ───────────────────────────────────────────────────
    correct = sum(1 for c in clf_log if c["correct"])
    total   = len(clf_log)
    lines += [
        "## Classifier Accuracy",
        "",
        f"**{correct}/{total} prompts correctly classified ({correct/total*100:.1f}%)**",
        "",
        "| Category | Expected | Predicted | Correct | Confidence |",
        "|----------|----------|-----------|---------|------------|",
    ]
    for c in clf_log:
        check = "✅" if c["correct"] else "❌"
        lines.append(
            f"| {c['prompt'][:45]!r} | {c['expected']} | {c['predicted']} | "
            f"{check} | {c['confidence']:.2f} |"
        )
    lines.append("")

    # ── Overall summary ───────────────────────────────────────────────────────
    lines += [
        "## Overall Summary (all prompts aggregated)",
        "",
        "| Strategy | Avg Out-Tokens | Avg Words | Avg Latency (ms) | "
        "Token Reduction vs None | Errors |",
        "|----------|----------------|-----------|------------------|"
        "-------------------------|--------|",
    ]
    none_agg = agg(flatten_runs(results, "none"))
    none_tok = none_agg["avg_output_tokens"] if none_agg["ok"] else 0

    for strategy in strategies:
        all_runs = flatten_runs(results, strategy)
        a = agg(all_runs)
        if not a["ok"]:
            lines.append(f"| {strategy} | — | — | — | — | {a.get('errors','all')} |")
            continue
        reduction = _pct(none_tok, a["avg_output_tokens"])
        lines.append(
            f"| {strategy} | {a['avg_output_tokens']} | {a['avg_output_words']} | "
            f"{a['avg_latency_ms']} | {reduction} | {a['errors']} |"
        )
    lines.append("")

    # ── Per-category breakdown ────────────────────────────────────────────────
    lines += [
        "## Per-Category Breakdown",
        "",
        "| Category | Expected | none | manual | auto | ultra | "
        "Auto Reduction vs None |",
        "|----------|----------|------|--------|------|-------|"
        "------------------------|",
    ]
    for cat, meta in PROMPT_CATEGORIES.items():
        exp = meta["expected_level"]
        row_aggs = {}
        for strategy in strategies:
            by_cat = agg_by_category(results, strategy)
            row_aggs[strategy] = by_cat.get(cat, {"ok": False})

        none_t = row_aggs["none"]["avg_output_tokens"] if row_aggs["none"]["ok"] else 0
        auto_t = row_aggs["auto"]["avg_output_tokens"] if row_aggs["auto"]["ok"] else 0
        reduction = _pct(none_t, auto_t)

        cells = [
            f"{row_aggs[s]['avg_output_tokens']:.0f}" if row_aggs[s]["ok"] else "—"
            for s in ["none", "manual", "auto", "ultra"]
        ]
        lines.append(
            f"| {cat} | `{exp}` | {cells[0]} | {cells[1]} | {cells[2]} | "
            f"{cells[3]} | **{reduction}** |"
        )
    lines.append("")

    # ── Auto vs manual comparison ─────────────────────────────────────────────
    auto_all   = agg(flatten_runs(results, "auto"))
    manual_all = agg(flatten_runs(results, "manual"))
    none_all   = none_agg

    if auto_all["ok"] and manual_all["ok"] and none_all["ok"]:
        auto_vs_none   = _pct(none_all["avg_output_tokens"],   auto_all["avg_output_tokens"])
        auto_vs_manual = _pct(manual_all["avg_output_tokens"], auto_all["avg_output_tokens"])
        lines += [
            "## Key Findings",
            "",
            f"- **Auto vs None baseline**: {auto_vs_none} token reduction",
            f"- **Auto vs Manual-full**: {auto_vs_manual} additional reduction",
            f"- **Classifier accuracy**: {correct}/{total} = {correct/total*100:.1f}%",
            f"- **Auto avg latency**: {auto_all['avg_latency_ms']}ms "
            f"(manual: {manual_all['avg_latency_ms']}ms)",
            "",
        ]

    # Recommendation
    lines += [
        "## Recommendation",
        "",
        "| Scenario | Recommended Strategy |",
        "|----------|---------------------|",
        "| Codex workspace default | **auto** (via AGENTS.md + SessionStart injection) |",
        "| Max compression, homogeneous tasks | manual ultra |",
        "| Mixed conversation with Q&A | auto (adapts per prompt) |",
        "| Security/destructive operations | auto (level=off auto-detected) |",
        "",
        "---",
        f"*Generated by `benchmarks/caveman_auto_level_benchmark.py` · {run_at}*",
    ]
    return "\n".join(lines)


# ── Main ──────────────────────────────────────────────────────────────────────
def main() -> None:
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("ERROR: OPENAI_API_KEY not set. Add to .env.local or export.")
        sys.exit(1)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    run_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")

    print(f"\nCaveman Auto-Level Benchmark — {run_at}")
    print(f"Model  : {MODEL}")
    print(f"Strategy: none · manual(full) · auto(classifier) · ultra")

    client = OpenAI(api_key=api_key)
    data = run_benchmark(client)

    # Save JSON
    with open(RESULTS_JSON, "w") as f:
        json.dump({"run_at": run_at, "model": MODEL, **data}, f, indent=2)
    print(f"\nRaw results → {RESULTS_JSON}")

    # Save Markdown
    report = build_report(data, run_at)
    with open(RESULTS_MD, "w") as f:
        f.write(report)
    print(f"Report      → {RESULTS_MD}")

    # Quick summary
    data_results = data["strategy_results"]
    clf_log = data["classification_log"]
    none_tok = agg(flatten_runs(data_results, "none"))["avg_output_tokens"]
    correct  = sum(1 for c in clf_log if c["correct"])

    print("\n── Quick Summary ──")
    for s in ["none", "manual", "auto", "ultra"]:
        a = agg(flatten_runs(data_results, s))
        if a["ok"]:
            r = (none_tok - a["avg_output_tokens"]) / none_tok * 100 if none_tok else 0
            print(f"  {s:<8} avg_out_tok={a['avg_output_tokens']:5.1f}  "
                  f"reduction={r:+.1f}%  latency={a['avg_latency_ms']}ms")
    print(f"  Classifier accuracy: {correct}/{len(clf_log)} = "
          f"{correct/len(clf_log)*100:.1f}%")


if __name__ == "__main__":
    main()
