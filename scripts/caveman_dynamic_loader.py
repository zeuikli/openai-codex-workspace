#!/usr/bin/env python3
"""
caveman_dynamic_loader.py

Dynamic caveman mode loading engine.

比較兩種載入策略：
  STATIC  — 目前 session_start_note.sh 的做法：每次 session 注入全套規則 (~431 tokens)。
  DYNAMIC — 按需注入：共用精簡規則 (~130 tokens) + 按分類結果補注差量 (~35-50 tokens)。

架構：
  - PROMPT_REGISTRY   : 各版本 system prompt 定義及 token 計量
  - DynamicLoader     : 分類 + 按需組合 + 省量計算
  - LoadDecision      : 單次載入決策的結構化結果

CLI Usage:
  python3 scripts/caveman_dynamic_loader.py "List all endpoints in the API"
  echo "What is TCP?" | python3 scripts/caveman_dynamic_loader.py
  python3 scripts/caveman_dynamic_loader.py --show-prompts
  python3 scripts/caveman_dynamic_loader.py --benchmark-mode
"""
from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from caveman_auto_level import classify, ClassificationResult  # type: ignore

# ─────────────────────────────────────────────────────────────────────────────
# Prompt Registry
# Each entry: {"text": str, "label": str, "purpose": str}
# ─────────────────────────────────────────────────────────────────────────────

CHARS_PER_TOKEN = 4  # standard approximation


def _tok(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


# ── Static (current production) ───────────────────────────────────────────────
# Extracted from .codex/hooks/session_start_note.sh additionalContext.
# Contains ALL level rules + selection logic simultaneously.
STATIC_PROMPT = (
    "This repository is Codex-native. Use .codex/agents for subagents and .agents/skills "
    "for reusable workflows. Prefer safe Bash commands and avoid destructive operations without "
    "approval. Treat the nine Karpathy principles (AGENTS.md → Karpathy 實作原則) as hard rules: "
    "surface assumptions, push back on conflicts, naive-first before optimize, declare Done when "
    "criteria before acting, keep blast radius minimal.\n\n"
    "CAVEMAN AUTO-LEVEL ACTIVE. Respond in caveman compression mode. Select level automatically "
    "based on incoming prompt—do NOT wait for user to specify. Switch silently (no announcement).\n\n"
    "Level selection rules:\n"
    "- lite: simple Q&A, one-line answers, confirmations, definitions, yes/no questions, casual chat\n"
    "- full: technical explanation, code review, debugging, architecture discussion, multi-step "
    "procedures (DEFAULT)\n"
    "- ultra: summarization requests, batch/list operations, large multi-file tasks, token-budget "
    "signals (\"be brief\", \"summarize\", \"list all\"), repetitive tool loops\n"
    "- OFF (normal prose): security warnings, irreversible destructive actions "
    "(delete/drop/rm -rf), user asks to clarify after confusion, multi-step sequences where "
    "fragment order risks misread\n\n"
    "Rules for all levels: drop pleasantries/hedging/filler. Technical terms exact. Code blocks "
    "unchanged. Errors quoted exact. Pattern: [thing] [action] [reason]. [next step].\n"
    "- lite: keep articles + full sentences. Professional but tight.\n"
    "- full: drop articles (a/an/the), fragments OK, short synonyms (big not extensive).\n"
    "- ultra: abbreviate (DB/auth/config/req/res/fn/impl), arrows for causality (X→Y), "
    "one word when enough.\n\n"
    "Persistence: active every response. No revert mid-session. Off only: user says "
    "\"stop caveman\" / \"normal mode\"."
)

# ── Lean Shared Base (new design, session start) ──────────────────────────────
# Contains: auto-select logic + common rules + concrete Not/Yes examples.
# Injected ONCE at session start regardless of mode.
# v2: added Not/Yes examples (from JuliusBrussee/caveman) for stronger model anchoring.
#     Research shows concrete examples prevent mid-session drift better than abstract rules.
LEAN_SHARED_PROMPT = (
    "CAVEMAN AUTO-LEVEL: pick level per prompt, switch silently.\n"
    "lite  → Q&A / definitions / yes-no: full sentences, drop filler only.\n"
    "full  → technical / debug / multi-step (DEFAULT): drop articles, fragments OK.\n"
    "ultra → summarize / list / batch / 'be brief': abbreviate, X→Y arrows, one word OK.\n"
    "off   → security / destructive ops (rm -rf / DROP TABLE): normal prose only.\n"
    "\n"
    "Rules: no pleasantries/hedging. Tech terms exact. Code blocks unchanged.\n"
    "Not: \"Sure! Happy to help. The issue you're experiencing is likely...\"\n"
    "Yes: \"Auth token expiry uses < not <=. Fix:\""
)

# ── Original-Filtered Prompt (benchmark comparison baseline) ──────────────────
# Simulates JuliusBrussee/caveman's approach: inject full rules for ONE level only.
# The original filters SKILL.md at runtime to the active level (~200-250 tokens).
# We use "full" (the default level) as the representative case.
# Purpose: benchmark comparison only — not used in production injection.
ORIGINAL_FILTERED_PROMPT = (
    "CAVEMAN MODE ACTIVE — level: full\n\n"
    "Respond terse like smart caveman. All technical substance stay. Only fluff die.\n\n"
    "ACTIVE EVERY RESPONSE. No revert after many turns. No filler drift. "
    "Off only: \"stop caveman\" / \"normal mode\".\n\n"
    "Rules: Drop articles (a/an/the), filler (just/really/basically/actually/simply), "
    "pleasantries, hedging. Fragments OK. Short synonyms (big not extensive, "
    "fix not \"implement a solution for\"). Technical terms exact. Code blocks unchanged. "
    "Errors quoted exact.\n\n"
    "Pattern: [thing] [action] [reason]. [next step].\n"
    "Not: \"Sure! I'd be happy to help you with that.\"\n"
    "Yes: \"Bug in auth middleware. Token expiry check use `<` not `<=`. Fix:\"\n\n"
    "Auto-Clarity: drop caveman for security warnings, irreversible actions. Resume after.\n"
    "Boundaries: code/commits/PRs write normal."
)

# ── Per-Turn Reinforcement (from JuliusBrussee/caveman mode-tracker.js) ───────
# Original uses UserPromptSubmit hook to inject this every turn (~28 tokens).
# Prevents mid-session drift when other plugins inject competing style instructions.
# In Codex (no UserPromptSubmit hook), this is documented but not auto-injected.
PER_TURN_REINFORCEMENT = (
    "CAVEMAN ACTIVE (auto). Drop articles/filler/pleasantries/hedging. "
    "Fragments OK. Security/destructive: write normal."
)

# ── Level Delta Prompts (appended on explicit override or first message) ──────
# Added ON TOP OF lean shared when user explicitly requests a level
# or when the classifier has high confidence and the session wants to lock in.
# v2: added Not/Yes concrete examples per level (research from JuliusBrussee/caveman).
#     Benchmark showed original_filtered (examples-based) achieves 11.7% better output
#     compression than abstract-rule-only deltas. Examples anchor model behavior more
#     reliably than equivalent-length abstract descriptions.
LEVEL_DELTA_PROMPTS: dict[str, str] = {
    "lite": (
        "Current mode: CAVEMAN lite. Keep articles + full sentences. "
        "Drop filler/hedging/pleasantries.\n"
        "Not: \"Sure! Basically yes, it should work.\"\n"
        "Yes: \"Yes. Use async for I/O-bound tasks.\""
    ),
    "full": (
        "Current mode: CAVEMAN full. Drop articles/filler/hedging. "
        "Fragments OK. Short synonyms.\n"
        "Not: \"Sure! Happy to help. The issue is likely caused by...\"\n"
        "Yes: \"Token expiry uses < not <=. Fix: change to <=.\""
    ),
    "ultra": (
        "Current mode: CAVEMAN ultra. Max compression. "
        "Abbreviate (DB/auth/cfg/fn/req/res). X→Y causality. One word OK.\n"
        "Not: \"The connection pool is being exhausted by too many requests.\"\n"
        "Yes: \"Pool exhausted → max_pool too low. Fix: max_pool=20.\""
    ),
    "off": (
        "Current mode: normal prose. No caveman compression. "
        "Write complete clear sentences."
    ),
}

# ── Sizing table ──────────────────────────────────────────────────────────────
PROMPT_SIZES: dict[str, dict[str, int]] = {
    "static": {
        "chars": len(STATIC_PROMPT),
        "tokens": _tok(STATIC_PROMPT),
    },
    "lean_shared": {
        "chars": len(LEAN_SHARED_PROMPT),
        "tokens": _tok(LEAN_SHARED_PROMPT),
    },
    "original_filtered": {
        "chars": len(ORIGINAL_FILTERED_PROMPT),
        "tokens": _tok(ORIGINAL_FILTERED_PROMPT),
    },
    "per_turn_reinforcement": {
        "chars": len(PER_TURN_REINFORCEMENT),
        "tokens": _tok(PER_TURN_REINFORCEMENT),
    },
    **{
        f"delta_{level}": {
            "chars": len(text),
            "tokens": _tok(text),
        }
        for level, text in LEVEL_DELTA_PROMPTS.items()
    },
}


# ─────────────────────────────────────────────────────────────────────────────
# LoadDecision
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class LoadDecision:
    """Result of a single dynamic load decision."""
    prompt: str
    level: str                    # lite | full | ultra | off
    confidence: float
    reasons: list[str]
    clf_scores: dict[str, float]

    # Static strategy (current baseline)
    static_tokens: int = field(default=0)
    static_text: str = field(default="")

    # Dynamic strategy (lean shared + delta)
    lean_tokens: int = field(default=0)
    lean_text: str = field(default="")
    delta_tokens: int = field(default=0)
    delta_text: str = field(default="")
    dynamic_total_tokens: int = field(default=0)

    # Savings
    tokens_saved: int = field(default=0)
    pct_saved: float = field(default=0.0)

    def as_dict(self) -> dict:
        return {
            "prompt": self.prompt[:120],
            "level": self.level,
            "confidence": round(self.confidence, 3),
            "reasons": self.reasons,
            "scores": {k: round(v, 3) for k, v in self.clf_scores.items()},
            "static_tokens": self.static_tokens,
            "dynamic_total_tokens": self.dynamic_total_tokens,
            "lean_tokens": self.lean_tokens,
            "delta_tokens": self.delta_tokens,
            "tokens_saved": self.tokens_saved,
            "pct_saved": round(self.pct_saved, 2),
        }


# ─────────────────────────────────────────────────────────────────────────────
# DynamicLoader
# ─────────────────────────────────────────────────────────────────────────────

class DynamicLoader:
    """
    Dynamic caveman prompt loader.

    Static strategy  : always injects STATIC_PROMPT (all rules, all levels).
    Dynamic strategy : injects LEAN_SHARED_PROMPT at session start;
                       adds LEVEL_DELTA for the detected level on first turn
                       (or when level changes).

    Token savings come from eliminating the per-level detail that the model
    never needs for a given turn.
    """

    def __init__(
        self,
        static_prompt: str = STATIC_PROMPT,
        lean_shared: str = LEAN_SHARED_PROMPT,
        level_deltas: Optional[dict[str, str]] = None,
    ) -> None:
        self._static = static_prompt
        self._lean = lean_shared
        self._deltas = level_deltas or LEVEL_DELTA_PROMPTS

    # ── Public API ────────────────────────────────────────────────────────────

    def decide(self, prompt: str, include_delta: bool = True) -> LoadDecision:
        """
        Classify prompt and return a LoadDecision with both strategies measured.

        include_delta: if True, lean prompt includes the level-specific delta.
                       Set False to model lean-only (shared rules, no delta lock-in).
        """
        clf = classify(prompt)

        static_tok = _tok(self._static)
        lean_tok = _tok(self._lean)
        delta_text = self._deltas.get(clf.level, "")
        delta_tok = _tok(delta_text) if (include_delta and delta_text) else 0
        dynamic_total = lean_tok + delta_tok

        saved = static_tok - dynamic_total
        pct = (saved / static_tok * 100) if static_tok > 0 else 0.0

        return LoadDecision(
            prompt=prompt,
            level=clf.level,
            confidence=clf.confidence,
            reasons=clf.reasons,
            clf_scores=clf.scores,
            static_tokens=static_tok,
            static_text=self._static,
            lean_tokens=lean_tok,
            lean_text=self._lean,
            delta_tokens=delta_tok,
            delta_text=delta_text,
            dynamic_total_tokens=dynamic_total,
            tokens_saved=saved,
            pct_saved=pct,
        )

    def get_static_system(self) -> str:
        """Return the full static system prompt (current production approach)."""
        return self._static

    def get_dynamic_system(self, prompt: str, include_delta: bool = True) -> str:
        """Return the minimal dynamic system prompt for the given user prompt."""
        decision = self.decide(prompt, include_delta=include_delta)
        if include_delta and decision.delta_text:
            return self._lean + "\n" + decision.delta_text
        return self._lean

    def size_report(self) -> dict[str, dict[str, int]]:
        """Return all prompt sizes for reporting."""
        return dict(PROMPT_SIZES)

    def session_savings(
        self,
        prompt_distribution: dict[str, float],
        turns: int = 10,
        include_delta: bool = True,
    ) -> dict[str, float]:
        """
        Model token savings across a multi-turn session.

        prompt_distribution: {"lite": 0.2, "full": 0.6, "ultra": 0.2, "off": 0.0}
        turns: expected number of turns in the session

        Static model: static tokens injected at session start (counts once but primes all turns).
        Dynamic model: lean tokens at session start + delta for first detected level.
        """
        static_tok = _tok(self._static)
        lean_tok = _tok(self._lean)

        # Most likely level (max distribution)
        dominant_level = max(prompt_distribution, key=lambda k: prompt_distribution[k])
        delta_tok = _tok(self._deltas.get(dominant_level, ""))
        dynamic_total = lean_tok + (delta_tok if include_delta else 0)

        saved = static_tok - dynamic_total
        pct = (saved / static_tok * 100) if static_tok > 0 else 0.0

        return {
            "turns": turns,
            "dominant_level": dominant_level,
            "static_tokens": static_tok,
            "dynamic_tokens": dynamic_total,
            "tokens_saved_per_session": saved,
            "pct_saved": round(pct, 2),
            "tokens_saved_per_100_sessions": saved * 100,
        }


# ─────────────────────────────────────────────────────────────────────────────
# CLI
# ─────────────────────────────────────────────────────────────────────────────

def _show_prompts() -> None:
    loader = DynamicLoader()
    sizes = loader.size_report()
    print("\n=== Prompt Registry ===\n")
    print(f"{'Variant':<25} {'Chars':>7} {'Tokens':>8}")
    print("-" * 45)
    for name, info in sizes.items():
        print(f"{name:<25} {info['chars']:>7} {info['tokens']:>8}")
    print()
    static_tok = sizes["static"]["tokens"]
    lean_tok = sizes["lean_shared"]["tokens"]
    print(f"Lean-only savings vs static: {static_tok - lean_tok} tokens "
          f"({(static_tok - lean_tok) / static_tok * 100:.1f}%)")
    for level in ("lite", "full", "ultra", "off"):
        key = f"delta_{level}"
        if key in sizes:
            combined = lean_tok + sizes[key]["tokens"]
            saved = static_tok - combined
            print(f"Lean+{level:<5} savings vs static: {saved} tokens "
                  f"({saved / static_tok * 100:.1f}%)")


def _benchmark_mode() -> None:
    """Quick offline benchmark summary over the standard 20-prompt suite."""
    loader = DynamicLoader()
    prompts = [
        # lite
        ("What is TCP?", "lite"),
        ("Is Python interpreted?", "lite"),
        ("What does idempotent mean?", "lite"),
        ("Define connection pooling.", "lite"),
        # full
        ("Explain database connection pooling.", "full"),
        ("Why does my React component re-render every time?", "full"),
        ("How does garbage collection work in Python?", "full"),
        ("What's the difference between TCP and UDP?", "full"),
        ("How do I fix a memory leak in Node.js?", "full"),
        ("What does the SQL EXPLAIN command tell me?", "full"),
        ("Why is my Docker container running out of memory?", "full"),
        ("How do I debug a 502 Bad Gateway error in nginx?", "full"),
        # ultra
        ("Summarize the key differences between REST and GraphQL.", "ultra"),
        ("List all HTTP status codes briefly.", "ultra"),
        ("Give me a quick overview of microservices vs monolith.", "ultra"),
        ("tl;dr: what is Kubernetes?", "ultra"),
        ("Be brief: explain CI/CD pipeline stages.", "ultra"),
        # off
        ("Warning: this command will drop all tables. Are you sure?", "off"),
        ("The rm -rf command will permanently delete the directory.", "off"),
        ("This action is irreversible and cannot be undone.", "off"),
    ]

    correct = 0
    total_static = 0
    total_dynamic = 0
    savings_list: list[int] = []

    print(f"\n{'Prompt':<50} {'Expect':>7} {'Got':>7} {'OK':>4} "
          f"{'Static':>8} {'Dynamic':>9} {'Saved':>7}")
    print("-" * 105)

    for text, expected in prompts:
        d = loader.decide(text, include_delta=True)
        ok = "✓" if d.level == expected else "✗"
        if d.level == expected:
            correct += 1
        total_static += d.static_tokens
        total_dynamic += d.dynamic_total_tokens
        savings_list.append(d.tokens_saved)
        print(f"{text[:48]:<50} {expected:>7} {d.level:>7} {ok:>4} "
              f"{d.static_tokens:>8} {d.dynamic_total_tokens:>9} {d.tokens_saved:>7}")

    n = len(prompts)
    total_saved = total_static - total_dynamic
    print("-" * 105)
    print(f"\n{'Accuracy:':<20} {correct}/{n} = {correct/n*100:.1f}%")
    print(f"{'Static total:':<20} {total_static} tokens ({total_static} tokens × {n} prompts)")
    print(f"{'Dynamic total:':<20} {total_dynamic} tokens")
    print(f"{'Total saved:':<20} {total_saved} tokens "
          f"({total_saved/total_static*100:.1f}% reduction)")
    print(f"{'Avg per prompt:':<20} {sum(savings_list)/n:.1f} tokens saved")


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(
        description="Caveman Dynamic Loader — classify prompt and show load decision",
    )
    parser.add_argument("prompt", nargs="*", help="Prompt text to classify")
    parser.add_argument("--show-prompts", action="store_true",
                        help="Show all prompt variants and token sizes")
    parser.add_argument("--benchmark-mode", action="store_true",
                        help="Run offline benchmark over standard prompt suite")
    parser.add_argument("--no-delta", action="store_true",
                        help="Use lean-only (no level delta appended)")
    args = parser.parse_args()

    if args.show_prompts:
        _show_prompts()
        return 0

    if args.benchmark_mode:
        _benchmark_mode()
        return 0

    # Single prompt classification
    if args.prompt:
        text = " ".join(args.prompt)
    elif not sys.stdin.isatty():
        text = sys.stdin.read().strip()
    else:
        parser.print_help()
        return 1

    loader = DynamicLoader()
    decision = loader.decide(text, include_delta=not args.no_delta)
    print(json.dumps(decision.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
