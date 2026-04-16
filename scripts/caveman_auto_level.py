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
#
# NOTE: \b word-boundary anchors do NOT work with Chinese/CJK characters.
# Chinese patterns use explicit anchors (^/$) or rely on character context.
# _count_matches() calls text.lower() — harmless for CJK (no case change).

# OFF: security / destructive — highest priority, checked first
OFF_PATTERNS = [
    # English
    r"\bdrop\s+table\b",
    r"\brm\s+-rf?\b",
    r"\bdelete\s+(all|everything|database|db|table|users)\b",
    r"\btruncate\b",
    r"\birreversible\b",
    r"\bcannot\s+be\s+undone\b",
    r"\b(warning|caution|danger)\s*:",
    r"\bdestructive\b",
    r"\bformat\s+(disk|drive|partition)\b",
    # Traditional Chinese
    r"刪除(所有|全部|資料庫|資料表|用戶|帳號|所有資料)",
    r"清空(資料庫|資料表|所有|全部)",
    r"格式化(硬碟|磁碟|分區|系統磁碟)",
    r"不可逆",
    r"無法復原",
    r"(警告|注意|危險)\s*[：:]",
    r"(危險|破壞性)(操作|指令|命令)",
]

# ULTRA: high-compression signals
ULTRA_PATTERNS = [
    # English
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
    r"\ball\s+\w+\s+in\s+",            # "all files in", "all tests in"
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
    # Traditional Chinese
    r"(摘要|摘錄|總結)(一下|說明|這個|以下)?",
    r"列出(所有|全部|每個|每一個)",
    r"(簡短|簡要|扼要)(說明|解釋|介紹|描述)",
    r"(快速|速速)(說明|概述|介紹|解釋)",
    r"(概述|概覽|概要)",
    r"重點(整理|列出|說明|條列)",
    r"(一句話|幾個字)(說明|解釋|描述|介紹)",
    r"用(一句話|幾個字)(說明|解釋|描述)",
    r"條列(式|出)",
]

# LITE: simple / conversational signals
LITE_PATTERNS = [
    # English
    r"^yes$",
    r"^no$",
    r"^ok$",
    r"^sure$",
    r"^thanks?",
    r"\bwhat\s+is\s+\w+\??$",
    r"\bdefine\s+\w+",
    r"\bmeaning\s+of\b",
    r"\bwhat\s+does\s+\w+\s+mean",
    r"\bwhat\s+does\s+\w+\s+stand\s+for",  # "What does REST stand for?"
    r"\bwhat's\s+\w+",
    r"^how\s+(many|much|old|long)\b",
    r"\bconfirm\b",
    r"\byes\s+or\s+no\b",
    r"\bdo\s+you\b",
    r"\bdo\s+i\s+need\s+to\b",             # "Do I need to restart the server?"
    r"\bcan\s+you\b",
    r"\bis\s+(this|that|it)\b",
    r"\bshould\s+i\b",
    r"^is\s+\w[\w\s]{0,40}\??\s*$",        # "Is Python interpreted?" (short is-question)
    r"^are\s+\w[\w\s]{0,40}\??\s*$",       # "Are hooks experimental?"
    r"\bwhat\s+language\b",
    # Traditional Chinese — single-char confirmations
    r"^[是否好對不嗯喔唷]$",
    r"^(好的|是的|對的|沒問題|可以|不用|不必|不需要)[。！]?\s*$",
    r"^(好啊|好喔|好呀|嗯嗯|嗯啊)[。！]?\s*$",
    # Traditional Chinese — thank-you / acknowledgment
    r"謝謝",
    r"感謝",
    # Traditional Chinese — definition / what-is
    # Note: use \s* to handle space between Chinese and ASCII (e.g. 什麼是 TCP？)
    r"什麼是\s*[\u4e00-\u9fff\w]",
    r"是什麼[？?]?\s*$",                   # "TCP 是什麼？" ends with 是什麼
    r"定義[\u4e00-\u9fff\w\s]+",
    r"[\u4e00-\u9fff\w]+的定義",
    r"是啥[？?]?\s*$",
    # Traditional Chinese — yes/no / confirm
    r"需要[\u4e00-\u9fff\w]*嗎[？]?\s*$",  # allow content between 需要 and 嗎
    r"(可以|能)(嗎|不可以|不能)[？]?\s*$",
    r"確認(一下)?[？]?\s*$",
    r"(這樣)?對(嗎|不對)[？]?\s*$",
    r"(是或否|是還是否)[？]?\s*$",
    r"(正確|對)(嗎|不)[？]?\s*$",
]

# FULL: default technical signals (explicit, not just "not lite or ultra")
FULL_PATTERNS = [
    # English
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
    # Traditional Chinese
    # Note: complement is NON-OPTIONAL to avoid matching 簡短說明/快速說明 (those are ultra)
    r"(解釋|說明)(一下|為什麼|如何|這個|原因|步驟)",
    r"為(什麼|何)[\u4e00-\u9fff\w\s]{0,30}(會|是|有|不|產生|發生)",
    r"如何(做|實作|設定|配置|修復|除錯|使用|建立|部署)",
    r"(怎麼|怎樣)(做|修|設定|除錯|實作|部署|配置)",
    r"(步驟|流程|程序)(是什麼|有哪些)",   # require complement; standalone 流程 is ambiguous
    r"比較[\u4e00-\u9fff\w\s]+[和與跟][\u4e00-\u9fff\w\s]+",
    r"(設計|架構)(模式|說明|概念|原則)",
    r"(除錯|調試)",
    r"(錯誤|問題)(原因|怎麼|如何|在哪)",
    r"(優化|效能|性能)(調整|改善|問題)",
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
