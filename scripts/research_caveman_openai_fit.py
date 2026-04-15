#!/usr/bin/env python3
"""Research harness: caveman verbosity x OpenAI model fit.

Notes:
- Uses public examples from caveman README/SKILL and OpenAI pricing/benchmark blog snippets.
- Designed to run offline once constants are embedded.
"""
from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from pathlib import Path
import re
import time

ROOT = Path(__file__).resolve().parents[1]
OUT_JSON = ROOT / "docs" / "reports" / "caveman_openai_fit_20260415.json"
OUT_MD = ROOT / "docs" / "reports" / "caveman_openai_fit_20260415.md"

BASELINE_TEXT = (
    "The reason your React component is re-rendering is likely because you're "
    "creating a new object reference on each render cycle. When you pass an inline "
    "object as a prop, React's shallow comparison sees it as a different object every "
    "time, which triggers a re-render. I'd recommend using useMemo to memoize the object."
)

CAVEMAN_LEVELS = {
    "lite": "Your component re-renders because you create a new object reference each render. Inline object props fail shallow comparison every time. Wrap it in `useMemo`.",
    "full": "New object ref each render. Inline object prop = new ref = re-render. Wrap in `useMemo`.",
    "ultra": "Inline obj prop → new ref → re-render. `useMemo`.",
}

# OpenAI public prices (USD per 1M output tokens)
MODELS = {
    "gpt-5.4": {"output_per_1m": 15.0, "terminal_bench": 75.1, "swe_bench": 57.7},
    "gpt-5.4-mini": {"output_per_1m": 4.5, "terminal_bench": 60.0, "swe_bench": 54.4},
    "gpt-5.4-nano": {"output_per_1m": 1.25, "terminal_bench": 46.3, "swe_bench": 52.4},
    "gpt-5-mini": {"output_per_1m": 2.0, "terminal_bench": 38.2, "swe_bench": 45.7},
}

# Qualitative clarity/stability penalties by compression level (0..1 higher better).
LEVEL_QUALITY = {
    "lite": 0.98,
    "full": 0.92,
    "ultra": 0.85,
}

LOAD_PATHS = {
    "hooks": {
        "manual_steps": 0,
        "autoload": 1,
        "payload_chars": 405,  # .codex/hooks.json command literal length (approx)
    },
    "agents": {
        "manual_steps": 0,
        "autoload": 1,
        "payload_chars": 120,  # AGENTS.md reference list only
    },
    "skills": {
        "manual_steps": 1,  # user needs /caveman or $caveman activation
        "autoload": 0,
        "payload_chars": 2800,  # SKILL body (approx, single skill)
    },
    "rules": {
        "manual_steps": 1,
        "autoload": 0,
        "payload_chars": 380,  # always-on snippet length
    },
}


def approx_tokens(text: str) -> int:
    # conservative approximation for mixed en/code content.
    words = re.findall(r"\w+|[`=<>→\-]+", text)
    return max(1, round(len(words) * 1.3))


@dataclass
class LevelResult:
    level: str
    tokens: int
    save_vs_baseline: float


def evaluate_level(item: tuple[str, str], baseline_tokens: int) -> LevelResult:
    level, text = item
    tokens = approx_tokens(text)
    save = (baseline_tokens - tokens) / baseline_tokens
    return LevelResult(level=level, tokens=tokens, save_vs_baseline=save)


def main() -> None:
    baseline_tokens = approx_tokens(BASELINE_TEXT)

    # sub-agent style parallel workers
    started = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as ex:
        results = list(ex.map(lambda kv: evaluate_level(kv, baseline_tokens), CAVEMAN_LEVELS.items()))
    elapsed_ms = (time.perf_counter() - started) * 1000

    levels = {r.level: {"tokens": r.tokens, "save_vs_baseline": round(r.save_vs_baseline, 4)} for r in results}

    # model x level grid
    grid = []
    for model, meta in MODELS.items():
        for level, r in levels.items():
            expected_output_tokens = r["tokens"]
            output_cost = expected_output_tokens * meta["output_per_1m"] / 1_000_000
            perf = (meta["terminal_bench"] * 0.6 + meta["swe_bench"] * 0.4) / 100
            fitness = perf * LEVEL_QUALITY[level] / max(output_cost, 1e-9)
            grid.append(
                {
                    "model": model,
                    "level": level,
                    "expected_tokens": expected_output_tokens,
                    "estimated_output_cost_usd": round(output_cost, 8),
                    "quality_perf_score": round(perf * LEVEL_QUALITY[level], 4),
                    "fitness_score": round(fitness, 2),
                }
            )

    grid.sort(key=lambda x: x["fitness_score"], reverse=True)

    load_test = {}
    for name, data in LOAD_PATHS.items():
        # lower score = faster/easier to reach active state
        activation_latency_score = data["manual_steps"] * 100 + data["payload_chars"] * 0.05 - data["autoload"] * 30
        load_test[name] = {
            **data,
            "activation_latency_score": round(activation_latency_score, 2),
        }

    ranking = sorted(load_test.items(), key=lambda kv: kv[1]["activation_latency_score"])

    payload = {
        "generated_at": "2026-04-15",
        "baseline_tokens": baseline_tokens,
        "parallel_worker_elapsed_ms": round(elapsed_ms, 2),
        "levels": levels,
        "model_level_grid_top5": grid[:5],
        "load_test": load_test,
        "load_ranking_fastest_first": [name for name, _ in ranking],
        "assumptions": [
            "Token count uses offline approximation; not API usage meter.",
            "Cost uses OpenAI public output-token prices only.",
            "Load test compares activation friction (steps + payload), not network latency.",
        ],
    }

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md = [
        "# Caveman × OpenAI Model Fit (2026-04-15)",
        "",
        f"- Baseline token estimate: **{baseline_tokens}**",
        f"- Sub-agent style parallel run time: **{payload['parallel_worker_elapsed_ms']} ms**",
        "",
        "## Level compression (vs baseline)",
        "",
        "| Level | Tokens | Save vs baseline |",
        "|---|---:|---:|",
    ]
    for level in ("lite", "full", "ultra"):
        md.append(f"| {level} | {levels[level]['tokens']} | {levels[level]['save_vs_baseline']:.2%} |")

    md += [
        "",
        "## Top model+level combinations (fitness)",
        "",
        "| Rank | Model | Level | Est. output cost (USD/msg) | Quality×Perf | Fitness |",
        "|---:|---|---|---:|---:|---:|",
    ]
    for i, row in enumerate(grid[:5], start=1):
        md.append(
            f"| {i} | {row['model']} | {row['level']} | {row['estimated_output_cost_usd']:.8f} | {row['quality_perf_score']:.4f} | {row['fitness_score']:.2f} |"
        )

    md += [
        "",
        "## Activation efficiency: Skills vs AGENTS vs Hooks vs Rules",
        "",
        "| Mechanism | Autoload | Manual steps | Payload chars | Activation latency score (↓ better) |",
        "|---|---:|---:|---:|---:|",
    ]
    for name in [n for n, _ in ranking]:
        d = load_test[name]
        md.append(
            f"| {name} | {d['autoload']} | {d['manual_steps']} | {d['payload_chars']} | {d['activation_latency_score']:.2f} |"
        )

    md += [
        "",
        "Fastest-to-activate ranking: " + " > ".join(payload["load_ranking_fastest_first"]),
        "",
        "## Assumptions",
        "",
    ]
    md.extend([f"- {a}" for a in payload["assumptions"]])

    OUT_MD.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Wrote: {OUT_JSON}")
    print(f"Wrote: {OUT_MD}")


if __name__ == "__main__":
    main()
