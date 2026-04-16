#!/usr/bin/env python3
"""
Unit tests for caveman_dynamic_loader.py

Tests:
  - Prompt size assertions (lean must be < static; deltas must be < lean)
  - DynamicLoader.decide() routing accuracy (20 prompts)
  - Savings always positive when dynamic total < static
  - Session savings model arithmetic
  - get_dynamic_system() returns shorter text than get_static_system()
  - Level-to-delta routing (lite→delta_lite, etc.)
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from caveman_dynamic_loader import (  # type: ignore
    DynamicLoader,
    LoadDecision,
    STATIC_PROMPT,
    LEAN_SHARED_PROMPT,
    LEVEL_DELTA_PROMPTS,
    PROMPT_SIZES,
    _tok,
)


class PromptSizeTest(unittest.TestCase):
    """Verify token budgets are within design targets."""

    def test_static_tokens_above_300(self):
        """Static prompt must be substantial (current ~431 tok)."""
        tok = PROMPT_SIZES["static"]["tokens"]
        self.assertGreater(tok, 300, f"static_tokens={tok} expected > 300")

    def test_lean_shared_under_200_tokens(self):
        """Lean shared must be compact (target ≤ 200 tok)."""
        tok = PROMPT_SIZES["lean_shared"]["tokens"]
        self.assertLessEqual(tok, 200, f"lean_shared tokens={tok} expected ≤ 200")

    def test_lean_smaller_than_static(self):
        """Lean shared must be strictly smaller than static."""
        self.assertLess(
            PROMPT_SIZES["lean_shared"]["tokens"],
            PROMPT_SIZES["static"]["tokens"],
        )

    def test_all_deltas_under_100_tokens(self):
        """Each level delta must be compact (≤ 100 tok)."""
        for level in ("lite", "full", "ultra", "off"):
            key = f"delta_{level}"
            tok = PROMPT_SIZES[key]["tokens"]
            self.assertLessEqual(tok, 100, f"delta_{level} tokens={tok} expected ≤ 100")

    def test_lean_plus_delta_under_static(self):
        """Lean shared + any delta must be less than static."""
        lean = PROMPT_SIZES["lean_shared"]["tokens"]
        static = PROMPT_SIZES["static"]["tokens"]
        for level in ("lite", "full", "ultra", "off"):
            key = f"delta_{level}"
            combined = lean + PROMPT_SIZES[key]["tokens"]
            self.assertLess(combined, static, (
                f"lean+delta_{level}={combined} is not < static={static}"
            ))

    def test_savings_at_least_40_pct_for_all_levels(self):
        """Dynamic strategy must save ≥ 40% vs static for every level."""
        static = PROMPT_SIZES["static"]["tokens"]
        lean = PROMPT_SIZES["lean_shared"]["tokens"]
        for level in ("lite", "full", "ultra", "off"):
            key = f"delta_{level}"
            combined = lean + PROMPT_SIZES[key]["tokens"]
            pct = (static - combined) / static * 100
            self.assertGreaterEqual(pct, 40.0, (
                f"lean+delta_{level} savings={pct:.1f}% < 40%"
            ))


class DynamicLoaderDecideTest(unittest.TestCase):
    """Verify classify-and-decide routing is correct."""

    CASES: list[tuple[str, str]] = [
        # ── English ──────────────────────────────────────────────────────────
        # lite
        ("What is TCP?", "lite"),
        ("Is Python interpreted?", "lite"),
        ("What does idempotent mean?", "lite"),
        ("Define connection pooling.", "lite"),
        ("ok", "lite"),
        # full
        ("Explain database connection pooling.", "full"),
        ("Why does my React component re-render?", "full"),
        ("How do I fix a memory leak in Node.js?", "full"),
        ("What's the difference between TCP and UDP?", "full"),
        ("How does garbage collection work in Python?", "full"),
        # ultra
        ("Summarize the key differences between REST and GraphQL.", "ultra"),
        ("List all HTTP status codes briefly.", "ultra"),
        ("Give me a quick overview of microservices vs monolith.", "ultra"),
        ("Be brief: explain CI/CD pipeline stages.", "ultra"),
        ("tl;dr what is Kubernetes?", "ultra"),
        # off
        ("Warning: this command will drop all tables.", "off"),
        ("rm -rf /var/data", "off"),
        ("DROP TABLE users;", "off"),
        ("This action is irreversible and cannot be undone.", "off"),
        ("delete all database records", "off"),
        # ── Traditional Chinese (繁體中文) ────────────────────────────────────
        # lite
        ("什麼是 TCP？", "lite"),
        ("好", "lite"),
        ("這樣對嗎？", "lite"),
        ("需要重啟嗎？", "lite"),
        ("TCP 是什麼？", "lite"),
        # full
        ("解釋一下 connection pooling", "full"),
        ("為什麼 React 每次都重新渲染？", "full"),
        ("如何修復 memory leak？", "full"),
        ("如何設定 nginx 反向代理？", "full"),
        ("比較 TCP 和 UDP 的差異", "full"),
        # ultra
        ("摘要一下 REST 和 GraphQL 的差異", "ultra"),
        ("列出所有 HTTP 狀態碼", "ultra"),
        ("簡短說明 CI/CD 流程", "ultra"),
        ("重點整理微服務的優缺點", "ultra"),
        ("一句話解釋 Kubernetes", "ultra"),
        # off
        ("警告：執行此命令將刪除所有資料表", "off"),
        ("清空資料庫", "off"),
        ("格式化硬碟", "off"),
        ("不可逆操作，請確認", "off"),
        ("無法復原，是否繼續？", "off"),
    ]

    def setUp(self):
        self.loader = DynamicLoader()

    def _classify_all(self) -> tuple[int, int]:
        correct = 0
        for prompt, expected in self.CASES:
            d = self.loader.decide(prompt)
            if d.level == expected:
                correct += 1
        return correct, len(self.CASES)

    def test_overall_accuracy_at_least_90_pct(self):
        correct, total = self._classify_all()
        accuracy = correct / total * 100
        self.assertGreaterEqual(
            accuracy, 90.0,
            f"Classifier accuracy {accuracy:.1f}% < 90% on {total} prompts"
        )

    def test_off_level_always_detected(self):
        """Security/destructive prompts must always map to 'off'."""
        off_cases = [(p, e) for p, e in self.CASES if e == "off"]
        for prompt, _ in off_cases:
            d = self.loader.decide(prompt)
            self.assertEqual(d.level, "off", f"Expected off for: {prompt!r}")

    def test_ultra_level_detected(self):
        """Summarize/list/brief prompts should mostly map to 'ultra'."""
        ultra_cases = [(p, e) for p, e in self.CASES if e == "ultra"]
        correct = sum(1 for p, _ in ultra_cases if self.loader.decide(p).level == "ultra")
        self.assertGreaterEqual(correct, len(ultra_cases) - 1,
                                "At most 1 ultra case may misclassify")

    def test_lite_level_detected(self):
        """Simple Q&A should mostly map to 'lite'."""
        lite_cases = [(p, e) for p, e in self.CASES if e == "lite"]
        correct = sum(1 for p, _ in lite_cases if self.loader.decide(p).level == "lite")
        self.assertGreaterEqual(correct, len(lite_cases) - 1,
                                "At most 1 lite case may misclassify")


class LoadDecisionArithmeticTest(unittest.TestCase):
    """Verify LoadDecision fields are arithmetically consistent."""

    def setUp(self):
        self.loader = DynamicLoader()

    def _decide(self, prompt: str) -> LoadDecision:
        return self.loader.decide(prompt, include_delta=True)

    def test_dynamic_total_equals_lean_plus_delta(self):
        for prompt in ["What is TCP?", "Explain pooling.", "Summarize REST vs GraphQL."]:
            d = self._decide(prompt)
            self.assertEqual(
                d.dynamic_total_tokens,
                d.lean_tokens + d.delta_tokens,
                f"dynamic_total mismatch for: {prompt!r}",
            )

    def test_tokens_saved_equals_static_minus_dynamic(self):
        for prompt in ["What is TCP?", "Explain pooling.", "Summarize REST vs GraphQL."]:
            d = self._decide(prompt)
            self.assertEqual(
                d.tokens_saved,
                d.static_tokens - d.dynamic_total_tokens,
                f"tokens_saved mismatch for: {prompt!r}",
            )

    def test_tokens_saved_always_positive(self):
        """Dynamic must always be cheaper than static."""
        for prompt, _ in DynamicLoaderDecideTest.CASES:
            d = self._decide(prompt)
            self.assertGreater(
                d.tokens_saved, 0,
                f"tokens_saved={d.tokens_saved} ≤ 0 for: {prompt!r}",
            )

    def test_pct_saved_between_40_and_100(self):
        for prompt, _ in DynamicLoaderDecideTest.CASES:
            d = self._decide(prompt)
            self.assertGreaterEqual(d.pct_saved, 40.0,
                                    f"pct_saved={d.pct_saved:.1f}% < 40% for: {prompt!r}")
            self.assertLessEqual(d.pct_saved, 100.0)

    def test_confidence_between_0_and_1(self):
        for prompt, _ in DynamicLoaderDecideTest.CASES:
            d = self._decide(prompt)
            self.assertGreater(d.confidence, 0.0)
            self.assertLessEqual(d.confidence, 1.0)


class DynamicSystemPromptTest(unittest.TestCase):
    """Verify get_dynamic_system returns shorter text than static."""

    def setUp(self):
        self.loader = DynamicLoader()

    def test_dynamic_always_shorter_than_static(self):
        static = self.loader.get_static_system()
        for prompt, _ in DynamicLoaderDecideTest.CASES:
            dynamic = self.loader.get_dynamic_system(prompt, include_delta=True)
            self.assertLess(
                len(dynamic), len(static),
                f"dynamic system longer than static for: {prompt!r}",
            )

    def test_off_level_produces_lean_only_system(self):
        """Off-level should return lean shared only (delta adds 'normal prose' note)."""
        dynamic = self.loader.get_dynamic_system("rm -rf /data", include_delta=True)
        # Should be lean + off delta — NOT the big static blob
        self.assertLess(len(dynamic), len(STATIC_PROMPT))

    def test_no_delta_option(self):
        """With include_delta=False, system prompt should be just lean shared."""
        lean_text = LEAN_SHARED_PROMPT
        for prompt, _ in DynamicLoaderDecideTest.CASES[:5]:
            dynamic = self.loader.get_dynamic_system(prompt, include_delta=False)
            self.assertEqual(dynamic, lean_text,
                             f"no-delta system ≠ lean_shared for: {prompt!r}")


class SessionSavingsModelTest(unittest.TestCase):
    """Verify session savings model arithmetic."""

    def setUp(self):
        self.loader = DynamicLoader()

    def test_session_savings_positive(self):
        dist = {"lite": 0.2, "full": 0.6, "ultra": 0.2, "off": 0.0}
        result = self.loader.session_savings(dist, turns=10)
        self.assertGreater(result["tokens_saved_per_session"], 0)

    def test_100_sessions_is_100x_single(self):
        dist = {"lite": 0.2, "full": 0.6, "ultra": 0.2, "off": 0.0}
        r = self.loader.session_savings(dist, turns=10)
        self.assertEqual(
            r["tokens_saved_per_100_sessions"],
            r["tokens_saved_per_session"] * 100,
        )

    def test_pct_saved_reasonable(self):
        dist = {"lite": 0.2, "full": 0.6, "ultra": 0.2, "off": 0.0}
        r = self.loader.session_savings(dist, turns=10)
        self.assertGreater(r["pct_saved"], 30.0)
        self.assertLess(r["pct_saved"], 100.0)


class AsDistTest(unittest.TestCase):
    """Verify as_dict() completeness."""

    def test_as_dict_has_required_keys(self):
        loader = DynamicLoader()
        d = loader.decide("Explain TCP").as_dict()
        required = {"prompt", "level", "confidence", "reasons", "scores",
                    "static_tokens", "dynamic_total_tokens", "lean_tokens",
                    "delta_tokens", "tokens_saved", "pct_saved"}
        for key in required:
            self.assertIn(key, d, f"Missing key: {key}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
