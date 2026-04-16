#!/usr/bin/env python3
"""
Caveman Auto-Level Prompt Classifier.

Analyzes an incoming prompt and recommends the appropriate caveman
compression level (lite / full / ultra / off) based on content signals.

This mirrors the auto-selection rules injected into session_start_note.sh
and AGENTS.md, providing a testable, measurable Python implementation.

Usage:
    python3 scripts/caveman_auto_level.py "Why does React re-render?"
    echo "Summarize all logs" | python3 scripts/caveman_auto_level.py

Exit codes:
    0  classification succeeded
    1  error
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field


# ── Signal tables ─────────────────────────────────────────────────────────────

# OFF: security / destructive — highest priority, checked first
OFF_PATTERNS = [
    r"\bdrop\s+table\b",
    r"\brm\s+-rf?\b",
    r"\bdelete\s+(all|everything|database|db|table|users)\b",
    r"\btruncate\b",
    r"\birreversible\b",
    r"\bcannot\s+be\s+undone\b",
    r"\b(warning|caution|danger)\s*:",
    r"\bdestructive\b",
    r"\bformat\s+(disk|drive|partition)\b",
]

# ULTRA: high-compression signals
ULTRA_PATTERNS = [
    r"\bsummarize\b",
    r"\bsummar[yi]",
    r"\blist\s+(all|every)",
    r"\bbrief(ly)?\b",
    r"\bshort(ly)?\b",
    r"\btl;?dr\b",
    r"tl;dr\s*:",                       # "tl;dr: what is..."

    r"\boverview\b",
    r"\bquick(ly)?\b",
    r"\bbatch\b",
    r"\bmulti[- ]file\b",
    r"\ball\s+\w+\s+in\s+",  # "all files in", "all tests in"
    r"\benumerate\b",
    r"\bcompact\b",
    r"\bcondense\b",
    r"\btoken\s+(budget|limit|sav)",
    r"\bgist\b",
    r"\bkey\s+points?\b",
    r"\bhighlights?\b",
    r"be\s+brief",
    r"keep\s+it\s+short",
    r"less\s+words?",
    r"fewer\s+words?",
]

# LITE: simple / conversational signals
LITE_PATTERNS = [
    r"^yes$",
    r"^no$",
    r"^ok$",
    r"^sure$",
    r"^thanks?",
    r"\bwhat\s+is\s+\w+\??$",
    r"\bdefine\s+\w+",
    r"\bmeaning\s+of\b",
    r"\bwhat\s+does\s+\w+\s+mean",
    r"\bwhat's\s+\w+",
    r"^how\s+(many|much|old|long)\b",
    r"\bconfirm\b",
    r"\byes\s+or\s+no\b",
    r"\bdo\s+you\b",
    r"\bcan\s+you\b",
    r"\bis\s+(this|that|it)\b",
    r"\bshould\s+i\b",
    r"^is\s+\w[\w\s]{0,40}\??\s*$",      # "Is Python interpreted?" (short is-question)
    r"^are\s+\w[\w\s]{0,40}\??\s*$",     # "Are hooks experimental?"

    r"\bwhat\s+language\b",
]

# FULL: default technical signals (explicit, not just "not lite or ultra")
FULL_PATTERNS = [
    r"\bexplain\b",
    r"\bhow\s+(does|do|to)\b",
    r"\bwhy\s+(does|do|is|are)\b",
    r"\bdebug\b",
    r"\berror\b",
    r"\bbug\b",
    r"\bfix\b",
    r"\bimplements?\b",
    r"\brefactor\b",
    r"\breview\b",
    r"\barchitecture\b",
    r"\bdesign\b",
    r"\bdifference\s+between\b",
    r"\bcompare\b",
    r"\bsteps?\b",
    r"\bprocedure\b",
    r"\bsetup\b",
    r"\bconfigure\b",
    r"\binstall\b",
    r"\bintegrate\b",
    r"\boptimize\b",
    r"\bperformance\b",
    r"\bsecurity\b",
    r"\btest\b",
    r"\bvalidate\b",
]


# ── Complexity signals ────────────────────────────────────────────────────────

def _count_matches(text: str, patterns: list[str]) -> int:
    t = text.lower()
    return sum(1 for p in patterns if re.search(p, t))


def _prompt_length_signal(prompt: str) -> str:
    """Map prompt character length to a tier hint."""
    n = len(prompt.strip())
    if n <= 60:
        return "lite"
    if n <= 300:
        return "full"
    return "ultra"


# ── Main classifier ───────────────────────────────────────────────────────────

@dataclass
class ClassificationResult:
    level: str          # lite | full | ultra | off
    confidence: float   # 0.0 – 1.0
    reasons: list[str] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {
            "level":      self.level,
            "confidence": round(self.confidence, 3),
            "reasons":    self.reasons,
            "scores":     {k: round(v, 3) for k, v in self.scores.items()},
        }


def classify(prompt: str) -> ClassificationResult:
    """
    Classify a prompt into a caveman compression level.

    Priority order: off > ultra > lite > full (default)
    """
    reasons: list[str] = []

    # ── 1. OFF check (highest priority) ──────────────────────────────────────
    off_hits = _count_matches(prompt, OFF_PATTERNS)
    if off_hits > 0:
        reasons.append(f"destructive/security pattern ({off_hits} match)")
        return ClassificationResult(
            level="off",
            confidence=0.95,
            reasons=reasons,
            scores={"off": 1.0, "ultra": 0.0, "lite": 0.0, "full": 0.0},
        )

    # ── 2. Score each level ───────────────────────────────────────────────────
    ultra_hits = _count_matches(prompt, ULTRA_PATTERNS)
    lite_hits  = _count_matches(prompt, LITE_PATTERNS)
    full_hits  = _count_matches(prompt, FULL_PATTERNS)
    len_hint   = _prompt_length_signal(prompt)

    # Normalize (avoid division by zero)
    total = ultra_hits + lite_hits + full_hits + 1  # +1 baseline for full

    ultra_score = ultra_hits / total
    lite_score  = lite_hits  / total
    full_score  = (full_hits + 1) / total  # full has +1 bias (default)

    # Length hint adjustments — suppress lite boost if any ultra signal present
    if len_hint == "ultra":
        ultra_score += 0.15
    elif len_hint == "lite" and ultra_hits == 0:   # don't boost lite when ultra signals exist
        lite_score  += 0.15


    scores = {"ultra": ultra_score, "lite": lite_score, "full": full_score}

    # ── 3. Decision ───────────────────────────────────────────────────────────
    # ultra wins if score is clearly dominant or ≥ 2 ultra signals
    if ultra_score > 0.35 or ultra_hits >= 2:
        level = "ultra"
        confidence = min(0.55 + ultra_score * 0.4, 0.95)
        reasons.append(f"ultra signals: {ultra_hits} matches, length={len_hint}")

    # lite wins if dominant and few technical signals
    elif lite_score > full_score and lite_hits >= 1 and full_hits == 0:
        level = "lite"
        confidence = min(0.50 + lite_score * 0.4, 0.90)
        reasons.append(f"lite signals: {lite_hits} matches, length={len_hint}")

    # default: full
    else:
        level = "full"
        confidence = min(0.50 + full_score * 0.3, 0.85)
        reasons.append(
            f"default tech level: full_hits={full_hits}, "
            f"lite_hits={lite_hits}, ultra_hits={ultra_hits}, length={len_hint}"
        )

    return ClassificationResult(level=level, confidence=confidence,
                                reasons=reasons, scores=scores)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    import json

    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    elif not sys.stdin.isatty():
        prompt = sys.stdin.read().strip()
    else:
        print("Usage: python3 scripts/caveman_auto_level.py <prompt>", file=sys.stderr)
        return 1

    result = classify(prompt)
    print(json.dumps(result.as_dict(), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
