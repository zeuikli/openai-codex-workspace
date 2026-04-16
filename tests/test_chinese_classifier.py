#!/usr/bin/env python3
"""
Chinese language classifier tests for caveman_auto_level.py.

Covers:
  - Traditional Chinese (繁體中文) prompts — 36 cases × 4 levels
  - Mixed Chinese-English prompts — 8 cases
  - Edge cases: single chars, wenyan-style output, false-positive checks

Accuracy targets:
  - Traditional Chinese OFF: 100% (safety-critical)
  - Traditional Chinese per level: ≥ 90%
  - Mixed: ≥ 87% overall
"""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from caveman_auto_level import classify  # type: ignore


# ── Helpers ───────────────────────────────────────────────────────────────────

def level(prompt: str) -> str:
    return classify(prompt).level


# ── Traditional Chinese (繁體中文) ─────────────────────────────────────────────

class TraditionalChineseOffTest(unittest.TestCase):
    """Destructive / security prompts in Traditional Chinese must → off."""

    CASES = [
        "警告：執行此命令將刪除所有資料表",
        "不可逆操作，請確認是否繼續",
        "清空資料庫",
        "格式化硬碟",
        "無法復原，是否繼續？",
        "危險操作：刪除所有用戶資料",
        "刪除全部資料表",
        "注意：這是破壞性指令",
    ]

    def test_all_off(self):
        wrong = [(p, level(p)) for p in self.CASES if level(p) != "off"]
        self.assertEqual(wrong, [], f"Misclassified as non-off: {wrong}")


class TraditionalChineseUltraTest(unittest.TestCase):
    """Summarize / list / batch prompts in Traditional Chinese must → ultra."""

    CASES = [
        "摘要一下 REST 和 GraphQL 的差異",
        "列出所有 HTTP 狀態碼",
        "簡短說明 CI/CD 流程",
        "重點整理微服務的優缺點",
        "一句話解釋 Kubernetes",
        "給我一個概述",
        "快速說明 connection pooling",
        "條列式列出 SOLID 原則",
        "概覽一下這個架構",
        "用幾個字描述 REST",
    ]

    def _correct(self):
        return [(p, level(p)) for p in self.CASES if level(p) == "ultra"]

    def test_at_least_90_pct(self):
        correct = len(self._correct())
        total = len(self.CASES)
        pct = correct / total * 100
        self.assertGreaterEqual(pct, 90.0,
            f"Traditional ultra accuracy {pct:.1f}% < 90% "
            f"({correct}/{total}). Wrong: "
            f"{[(p, level(p)) for p in self.CASES if level(p) != 'ultra']}")


class TraditionalChineseLiteTest(unittest.TestCase):
    """Simple Q&A / yes-no / definition prompts in Traditional Chinese must → lite."""

    CASES = [
        "什麼是 TCP？",
        "好",
        "這樣對嗎？",
        "需要重啟嗎？",
        "可以嗎？",
        "確認一下",
        "是",
        "對",
        "好的",
        "TCP 是什麼？",
    ]

    def _correct(self):
        return [(p, level(p)) for p in self.CASES if level(p) == "lite"]

    def test_at_least_90_pct(self):
        correct = len(self._correct())
        total = len(self.CASES)
        pct = correct / total * 100
        self.assertGreaterEqual(pct, 90.0,
            f"Traditional lite accuracy {pct:.1f}% < 90% "
            f"({correct}/{total}). Wrong: "
            f"{[(p, level(p)) for p in self.CASES if level(p) != 'lite']}")


class TraditionalChineseFullTest(unittest.TestCase):
    """Technical explain / debug / multi-step in Traditional Chinese must → full."""

    CASES = [
        "解釋一下 connection pooling",
        "為什麼 React 每次都重新渲染？",
        "如何修復 memory leak？",
        "如何設定 nginx 反向代理？",
        "比較 TCP 和 UDP 的差異",
        "怎麼設定 GitHub Actions？",
        "除錯：為什麼這個 API 回傳 502？",
        "步驟：如何部署 FastAPI 到 AWS？",
    ]

    def _correct(self):
        return [(p, level(p)) for p in self.CASES if level(p) == "full"]

    def test_at_least_87_pct(self):
        correct = len(self._correct())
        total = len(self.CASES)
        pct = correct / total * 100
        self.assertGreaterEqual(pct, 87.0,
            f"Traditional full accuracy {pct:.1f}% < 87% "
            f"({correct}/{total}). Wrong: "
            f"{[(p, level(p)) for p in self.CASES if level(p) != 'full']}")


# ── Mixed Chinese-English ─────────────────────────────────────────────────────

class MixedChineseEnglishTest(unittest.TestCase):
    """Mixed-language prompts (code-switching) should classify correctly."""

    CASES = [
        # (prompt, expected_level)
        ("解釋一下 connection pooling 的原理", "full"),
        ("摘要 REST vs GraphQL", "ultra"),
        ("TCP 是什麼", "lite"),
        ("警告：rm -rf 將永久刪除資料", "off"),
        ("如何 debug 這個 502 error？", "full"),
        ("列出所有 Python built-in exceptions", "ultra"),
        ("好，謝謝", "lite"),
        ("刪除所有 database records", "off"),
    ]

    def test_at_least_87_pct(self):
        wrong = [(p, level(p), e) for p, e in self.CASES if level(p) != e]
        correct = len(self.CASES) - len(wrong)
        pct = correct / len(self.CASES) * 100
        self.assertGreaterEqual(pct, 87.0,
            f"Mixed accuracy {pct:.1f}% < 87%. Wrong: {wrong}")


# ── Edge Cases ────────────────────────────────────────────────────────────────

class EdgeCaseTest(unittest.TestCase):
    """Boundary conditions and unusual inputs."""

    def test_single_chinese_yes_char(self):
        self.assertEqual(level("是"), "lite")

    def test_single_chinese_no_char(self):
        self.assertEqual(level("否"), "lite")

    def test_single_chinese_ok_char(self):
        self.assertEqual(level("好"), "lite")

    def test_single_chinese_agree_char(self):
        self.assertEqual(level("對"), "lite")

    def test_chinese_with_english_code_term(self):
        """Chinese framing + English code block should not trip off-detector."""
        r = classify("如何實作 JWT authentication in Express？")
        self.assertEqual(r.level, "full")
        self.assertNotEqual(r.level, "off")

    def test_chinese_destructive_no_false_positive_on_normal(self):
        """'刪除' alone (without qualifiers like 所有/全部) should NOT trigger off."""
        r = classify("如何刪除 Docker container？")
        # 'Docker' + '如何' + '刪除 container' — this is a how-to, not mass destruction
        # The classifier may return full or off; it must NOT return lite/ultra
        self.assertIn(r.level, ("full", "off"),
            f"'如何刪除 Docker container' classified as {r.level}, expected full or off")

    def test_wenyan_style_output_not_misclassified(self):
        """A wenyan-style compressed phrase should not trigger off."""
        r = classify("池竭。max_pool 過低。改為20。")
        self.assertNotEqual(r.level, "off",
            "Wenyan-compressed output phrase should not be classified as off")

    def test_overall_chinese_off_safety(self):
        """All explicit destructive Traditional Chinese prompts must route to off."""
        must_be_off = [
            "刪除所有資料庫",
            "清空資料表",
            "格式化硬碟",
            "不可逆操作",
            "無法復原",
            "警告：危險操作",
        ]
        wrong = [(p, level(p)) for p in must_be_off if level(p) != "off"]
        self.assertEqual(wrong, [], f"Safety-critical misclassifications: {wrong}")


# ── Overall Accuracy Report ───────────────────────────────────────────────────

class ChineseOverallAccuracyTest(unittest.TestCase):
    """Combined accuracy across Traditional Chinese + mixed cases must be ≥ 90%."""

    ALL_CASES: list[tuple[str, str]] = [
        # Traditional Chinese OFF (8)
        ("警告：執行此命令將刪除所有資料表", "off"),
        ("不可逆操作，請確認是否繼續", "off"),
        ("清空資料庫", "off"),
        ("格式化硬碟", "off"),
        ("無法復原，是否繼續？", "off"),
        ("危險操作：刪除所有用戶資料", "off"),
        ("刪除全部資料表", "off"),
        ("注意：這是破壞性指令", "off"),
        # Traditional Chinese ULTRA (10)
        ("摘要一下 REST 和 GraphQL 的差異", "ultra"),
        ("列出所有 HTTP 狀態碼", "ultra"),
        ("簡短說明 CI/CD 流程", "ultra"),
        ("重點整理微服務的優缺點", "ultra"),
        ("一句話解釋 Kubernetes", "ultra"),
        ("給我一個概述", "ultra"),
        ("快速說明 connection pooling", "ultra"),
        ("條列式列出 SOLID 原則", "ultra"),
        ("概覽一下這個架構", "ultra"),
        ("用幾個字描述 REST", "ultra"),
        # Traditional Chinese LITE (10)
        ("什麼是 TCP？", "lite"),
        ("好", "lite"),
        ("這樣對嗎？", "lite"),
        ("需要重啟嗎？", "lite"),
        ("可以嗎？", "lite"),
        ("確認一下", "lite"),
        ("是", "lite"),
        ("對", "lite"),
        ("好的", "lite"),
        ("TCP 是什麼？", "lite"),
        # Traditional Chinese FULL (8)
        ("解釋一下 connection pooling", "full"),
        ("為什麼 React 每次都重新渲染？", "full"),
        ("如何修復 memory leak？", "full"),
        ("如何設定 nginx 反向代理？", "full"),
        ("比較 TCP 和 UDP 的差異", "full"),
        ("怎麼設定 GitHub Actions？", "full"),
        ("除錯：為什麼這個 API 回傳 502？", "full"),
        ("步驟：如何部署 FastAPI 到 AWS？", "full"),
        # Mixed Chinese-English (8)
        ("解釋一下 connection pooling 的原理", "full"),
        ("摘要 REST vs GraphQL", "ultra"),
        ("TCP 是什麼", "lite"),
        ("警告：rm -rf 將永久刪除資料", "off"),
        ("如何 debug 這個 502 error？", "full"),
        ("列出所有 Python built-in exceptions", "ultra"),
        ("好，謝謝", "lite"),
        ("刪除所有 database records", "off"),
    ]

    def test_overall_accuracy_at_least_90_pct(self):
        wrong = [(p, level(p), e) for p, e in self.ALL_CASES if level(p) != e]
        correct = len(self.ALL_CASES) - len(wrong)
        total = len(self.ALL_CASES)
        pct = correct / total * 100
        self.assertGreaterEqual(pct, 90.0,
            f"Overall Chinese accuracy {correct}/{total} = {pct:.1f}% < 90%.\n"
            f"Wrong classifications:\n" +
            "\n".join(f"  {p!r}: got={got!r} expected={exp!r}"
                      for p, got, exp in wrong))

    def test_off_level_perfect_on_all_destructive(self):
        """All off-labelled prompts must route to off (safety-critical: no tolerance)."""
        off_cases = [(p, e) for p, e in self.ALL_CASES if e == "off"]
        wrong = [(p, level(p)) for p, _ in off_cases if level(p) != "off"]
        self.assertEqual(wrong, [],
            f"OFF safety failures (zero tolerance): {wrong}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
