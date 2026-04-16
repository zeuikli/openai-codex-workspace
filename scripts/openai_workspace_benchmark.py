#!/usr/bin/env python3
"""OpenAI workspace benchmark for caveman levels.

Runs real API calls when OPENAI_API_KEY exists, otherwise performs a Python dry run
with deterministic token estimates so the benchmark pipeline remains executable.
"""

from __future__ import annotations

import argparse
import json
import os
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
PROMPTS_FILE = REPO_ROOT / "benchmarks" / "prompts" / "en.txt"
SKILL_FILE = REPO_ROOT / ".agents" / "skills" / "caveman" / "SKILL.md"
RESULTS_DIR = REPO_ROOT / "benchmarks" / "results"
ENV_FILE = REPO_ROOT / ".env.local"

MODELS = ["gpt-5.4", "gpt-5.4-mini", "gpt-5.4-nano", "gpt-5.3-codex"]
LEVELS = ["lite", "full", "ultra"]

# Dry-run multipliers are deterministic heuristics for output compression.
# Lower = fewer output tokens.
MODEL_FACTORS = {
    "gpt-5.4": 1.00,
    "gpt-5.4-mini": 0.93,
    "gpt-5.4-nano": 0.82,
    "gpt-5.3-codex": 0.90,
}
LEVEL_FACTORS = {
    "lite": 0.62,
    "full": 0.41,
    "ultra": 0.31,
}

SURFACE_SCORES = {
    "AGENTS": {
        "autoload": 3,
        "scope_control": 5,
        "runtime_switch": 1,
        "operational_risk": 3,
        "workspace_fit": 4,
    },
    "SKILL": {
        "autoload": 4,
        "scope_control": 5,
        "runtime_switch": 5,
        "operational_risk": 4,
        "workspace_fit": 5,
    },
    "HOOKS": {
        "autoload": 5,
        "scope_control": 2,
        "runtime_switch": 3,
        "operational_risk": 2,
        "workspace_fit": 3,
    },
}


@dataclass
class RunResult:
    model: str
    level: str
    median_tokens: int
    mean_tokens: float
    min_tokens: int
    max_tokens: int
    stdev_tokens: float


def load_prompts() -> list[str]:
    return [line.strip() for line in PROMPTS_FILE.read_text().splitlines() if line.strip()]


def load_skill() -> str:
    return SKILL_FILE.read_text()


def load_env_local_if_present() -> None:
    """Best-effort .env.local loader for local runs.

    Keeps secrets out of git and supports users who prefer file-based local config.
    Existing environment variables are not overridden.
    """
    if not ENV_FILE.exists():
        return
    for raw_line in ENV_FILE.read_text().splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip('"').strip("'")
        if key and key not in os.environ:
            os.environ[key] = value


def level_system_prompt(skill_text: str, level: str) -> str:
    return (
        "Answer concisely. "
        f"Force caveman intensity level={level}. "
        "Keep all technical correctness, remove fluff.\n\n"
        f"{skill_text}"
    )


def token_count(text: str) -> int:
    try:
        import tiktoken  # type: ignore

        enc = tiktoken.get_encoding("o200k_base")
        return len(enc.encode(text))
    except Exception:
        # Safe fallback if tokenizer unavailable.
        return max(1, len(text) // 4)


def dry_run_responses(prompts: list[str], model: str, level: str) -> list[int]:
    model_factor = MODEL_FACTORS[model]
    level_factor = LEVEL_FACTORS[level]
    scores: list[int] = []
    for p in prompts:
        base = max(18, int(token_count(p) * 4.1))
        estimate = int(base * model_factor * level_factor)
        scores.append(max(12, estimate))
    return scores


def real_run_responses(client: Any, prompts: list[str], model: str, level: str, skill_text: str) -> list[int]:
    output_tokens: list[int] = []
    system_prompt = level_system_prompt(skill_text, level)
    for prompt in prompts:
        response = client.responses.create(
            model=model,
            input=prompt,
            instructions=system_prompt,
            max_output_tokens=600,
            temperature=0,
        )
        usage = getattr(response, "usage", None)
        if usage is None:
            output_tokens.append(token_count(getattr(response, "output_text", "")))
            continue

        # SDK compatibility: usage may expose either dict-like or attributes.
        ot = None
        if isinstance(usage, dict):
            ot = usage.get("output_tokens")
        else:
            ot = getattr(usage, "output_tokens", None)
        if ot is None:
            ot = token_count(getattr(response, "output_text", ""))
        output_tokens.append(int(ot))
        time.sleep(0.1)
    return output_tokens


def summarize(model: str, level: str, values: list[int]) -> RunResult:
    return RunResult(
        model=model,
        level=level,
        median_tokens=int(statistics.median(values)),
        mean_tokens=round(statistics.mean(values), 2),
        min_tokens=min(values),
        max_tokens=max(values),
        stdev_tokens=round(statistics.pstdev(values), 2),
    )


def rank_surfaces() -> list[dict[str, Any]]:
    weighted: list[dict[str, Any]] = []
    for name, dims in SURFACE_SCORES.items():
        # Weights tuned for this workspace: scope+fit are key.
        score = (
            dims["autoload"] * 0.20
            + dims["scope_control"] * 0.25
            + dims["runtime_switch"] * 0.20
            + dims["operational_risk"] * 0.15
            + dims["workspace_fit"] * 0.20
        )
        weighted.append({"surface": name, "score": round(score, 2), "dimensions": dims})
    return sorted(weighted, key=lambda x: x["score"], reverse=True)


def markdown_table(rows: list[RunResult]) -> str:
    lines = [
        "| Model | Level | Median output tokens | Mean | Min | Max | StdDev |",
        "|---|---|---:|---:|---:|---:|---:|",
    ]
    for r in sorted(rows, key=lambda x: (x.model, LEVELS.index(x.level))):
        lines.append(
            f"| {r.model} | {r.level} | {r.median_tokens} | {r.mean_tokens} | {r.min_tokens} | {r.max_tokens} | {r.stdev_tokens} |"
        )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark OpenAI models against caveman levels")
    parser.add_argument("--models", nargs="*", default=MODELS)
    parser.add_argument("--levels", nargs="*", default=LEVELS)
    parser.add_argument("--output-prefix", default="openai_workspace_benchmark")
    args = parser.parse_args()

    invalid_models = sorted(set(args.models) - set(MODELS))
    invalid_levels = sorted(set(args.levels) - set(LEVELS))
    if invalid_models:
        raise SystemExit(f"Unsupported models: {invalid_models}. Allowed: {MODELS}")
    if invalid_levels:
        raise SystemExit(f"Unsupported levels: {invalid_levels}. Allowed: {LEVELS}")

    load_env_local_if_present()
    prompts = load_prompts()
    skill_text = load_skill()
    has_key = bool(os.environ.get("OPENAI_API_KEY"))

    rows: list[RunResult] = []

    if has_key:
        from openai import OpenAI  # type: ignore

        client = OpenAI()
        mode = "live"
        for model in args.models:
            for level in args.levels:
                vals = real_run_responses(client, prompts, model, level, skill_text)
                rows.append(summarize(model, level, vals))
    else:
        mode = "dry_run"
        for model in args.models:
            for level in args.levels:
                vals = dry_run_responses(prompts, model, level)
                rows.append(summarize(model, level, vals))

    best = min(rows, key=lambda r: r.median_tokens)
    surfaces = rank_surfaces()
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")

    payload = {
        "metadata": {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "mode": mode,
            "prompt_file": str(PROMPTS_FILE.relative_to(REPO_ROOT)),
            "skill_file": str(SKILL_FILE.relative_to(REPO_ROOT)),
            "models": args.models,
            "levels": args.levels,
            "openai_api_key_present": has_key,
        },
        "results": [r.__dict__ for r in rows],
        "best": best.__dict__,
        "surface_ranking": surfaces,
        "recommendation": {
            "primary": "SKILL",
            "secondary": "AGENTS",
            "optional": "HOOKS",
            "reason": "SKILL gives strongest runtime control + low risk; AGENTS locks governance; HOOKS only for auto-start convenience.",
        },
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    json_path = RESULTS_DIR / f"{args.output_prefix}_{ts}.json"
    md_path = RESULTS_DIR / f"{args.output_prefix}_{ts}.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")

    md_lines = [
        f"# OpenAI Workspace Benchmark ({mode})",
        "",
        f"Generated at: `{payload['metadata']['generated_at']}`",
        "",
        f"Best combo: **{best.model} + {best.level}** (median `{best.median_tokens}` output tokens)",
        "",
        "## Matrix",
        "",
        markdown_table(rows),
        "",
        "## AGENTS vs SKILL vs HOOKS (workspace fit)",
        "",
        "| Surface | Score | Notes |",
        "|---|---:|---|",
    ]
    for surf in surfaces:
        note = (
            "Best for local, composable runtime control"
            if surf["surface"] == "SKILL"
            else "Good policy/governance anchor"
            if surf["surface"] == "AGENTS"
            else "Auto-start convenience with higher operational risk"
        )
        md_lines.append(f"| {surf['surface']} | {surf['score']} | {note} |")

    md_lines += [
        "",
        "## Recommendation",
        "",
        "- Primary: `SKILL` (lite/full/ultra switching + predictable blast radius)",
        "- Secondary: `AGENTS.md` for policy and task protocol",
        "- Optional: `HOOKS` only for session-start auto activation on supported platforms",
        "",
        "## Dry-run note",
        "",
        "- If `OPENAI_API_KEY` is missing, this benchmark computes deterministic token estimates via Python only.",
        "- Re-run with key to collect live response token usage from OpenAI models.",
        "",
    ]
    md_path.write_text("\n".join(md_lines))

    print(f"mode={mode}")
    print(f"json={json_path}")
    print(f"markdown={md_path}")
    print(f"best={best.model}+{best.level} median={best.median_tokens}")


if __name__ == "__main__":
    main()
