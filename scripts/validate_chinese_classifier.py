#!/usr/bin/env python3
"""
Traditional Chinese Classifier Validation Script.

Runs a curated 44-prompt Traditional Chinese test suite through
caveman_auto_level.classify() and reports accuracy, confidence,
and misclassification details.

Usage:
    python3 scripts/validate_chinese_classifier.py
    python3 scripts/validate_chinese_classifier.py --verbose
    python3 scripts/validate_chinese_classifier.py --verbose --failures-only
    python3 scripts/validate_chinese_classifier.py --verbose --show-reasons
    python3 scripts/validate_chinese_classifier.py --json

Exit codes:
    0  all checks pass  (OFF=100%, overall ≥ 90%)
    1  OFF level has any failure  (safety-critical)
    2  overall accuracy < 90%
"""
from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

from caveman_auto_level import classify, ClassificationResult  # type: ignore


# ── Test suite ────────────────────────────────────────────────────────────────
# Each entry: (prompt, expected_level, note)
# note: short label for why this case is interesting

TEST_SUITE: list[tuple[str, str, str]] = [
    # ── OFF: destructive / security (10) ──────────────────────────────────────
    ("警告：執行此命令將刪除所有資料表", "off", "句首警告"),
    ("不可逆操作，請確認是否繼續", "off", "不可逆"),
    ("清空資料庫", "off", "清空"),
    ("格式化硬碟", "off", "格式化"),
    ("無法復原，是否繼續？", "off", "無法復原"),
    ("危險操作：刪除所有用戶資料", "off", "危險+刪除"),
    ("刪除全部資料表", "off", "刪除全部"),
    ("注意：這是破壞性指令", "off", "注意+破壞性"),
    ("警告：rm -rf 將永久刪除資料", "off", "中英混合 off"),
    ("刪除所有 database records", "off", "中英混合 delete"),

    # ── ULTRA: summarize / list / compress (12) ───────────────────────────────
    ("摘要一下 REST 和 GraphQL 的差異", "ultra", "摘要"),
    ("列出所有 HTTP 狀態碼", "ultra", "列出所有"),
    ("簡短說明 CI/CD 流程", "ultra", "簡短說明"),
    ("重點整理微服務的優缺點", "ultra", "重點整理"),
    ("一句話解釋 Kubernetes", "ultra", "一句話"),
    ("給我一個概述", "ultra", "概述"),
    ("快速說明 connection pooling", "ultra", "快速說明"),
    ("條列式列出 SOLID 原則", "ultra", "條列式"),
    ("概覽一下這個架構", "ultra", "概覽"),
    ("用幾個字描述 REST", "ultra", "幾個字"),
    ("摘要 REST vs GraphQL", "ultra", "中英混合 ultra"),
    ("列出所有 Python built-in exceptions", "ultra", "中英混合 list"),

    # ── LITE: Q&A / yes-no / definition (12) ─────────────────────────────────
    ("什麼是 TCP？", "lite", "什麼是+ASCII"),
    ("TCP 是什麼？", "lite", "X是什麼"),
    ("好", "lite", "單字確認"),
    ("是", "lite", "單字 yes"),
    ("對", "lite", "單字 agree"),
    ("好的", "lite", "短語確認"),
    ("這樣對嗎？", "lite", "是非問句"),
    ("需要重啟嗎？", "lite", "需要…嗎中間有詞"),
    ("可以嗎？", "lite", "可以嗎"),
    ("確認一下", "lite", "確認"),
    ("好，謝謝", "lite", "謝謝"),
    ("TCP 是什麼", "lite", "無問號結尾"),

    # ── FULL: explain / debug / multi-step (10) ───────────────────────────────
    ("解釋一下 connection pooling", "full", "解釋一下"),
    ("為什麼 React 每次都重新渲染？", "full", "為什麼"),
    ("如何修復 memory leak？", "full", "如何修復"),
    ("如何設定 nginx 反向代理？", "full", "如何設定"),
    ("比較 TCP 和 UDP 的差異", "full", "比較"),
    ("怎麼設定 GitHub Actions？", "full", "怎麼設定"),
    ("除錯：為什麼這個 API 回傳 502？", "full", "除錯"),
    ("步驟：如何部署 FastAPI 到 AWS？", "full", "步驟+如何"),
    ("如何 debug 這個 502 error？", "full", "中英混合 debug"),
    ("解釋一下 connection pooling 的原理", "full", "中英混合 explain"),

    # ── EDGE: boundary / false-positive guard (extra) ─────────────────────────
    # These are included in the suite to verify NO false off-triggers.
    # Expected: full (how-to containing 刪除 without mass-delete qualifiers)
    ("如何刪除 Docker container？", "full", "邊界：刪除無限定詞"),
]

# Split edge cases out so they don't count against level-specific accuracy.
_EDGE_PROMPTS = {"如何刪除 Docker container？"}
CORE_SUITE = [(p, e, n) for p, e, n in TEST_SUITE if p not in _EDGE_PROMPTS]
EDGE_SUITE  = [(p, e, n) for p, e, n in TEST_SUITE if p in _EDGE_PROMPTS]


# ── Data structures ───────────────────────────────────────────────────────────

@dataclass
class CaseResult:
    prompt:   str
    expected: str
    got:      str
    note:     str
    passed:   bool
    confidence: float
    reasons:  list[str]

@dataclass
class LevelStats:
    level:     str
    total:     int = 0
    correct:   int = 0
    conf_sum:  float = 0.0
    failures:  list[CaseResult] = field(default_factory=list)

    @property
    def accuracy(self) -> float:
        return self.correct / self.total * 100 if self.total else 0.0

    @property
    def avg_conf(self) -> float:
        return self.conf_sum / self.total if self.total else 0.0

@dataclass
class ValidationReport:
    timestamp:    str
    per_level:    dict[str, LevelStats]
    edge_results: list[CaseResult]
    total:        int
    correct:      int

    @property
    def overall_accuracy(self) -> float:
        return self.correct / self.total * 100 if self.total else 0.0

    @property
    def off_accuracy(self) -> float:
        s = self.per_level.get("off")
        return s.accuracy if s else 0.0

    @property
    def all_failures(self) -> list[CaseResult]:
        out = []
        for s in self.per_level.values():
            out.extend(s.failures)
        return out

    def exit_code(self) -> int:
        if self.off_accuracy < 100.0:
            return 1
        if self.overall_accuracy < 90.0:
            return 2
        return 0


# ── Runner ────────────────────────────────────────────────────────────────────

def run_validation() -> ValidationReport:
    levels = ["off", "ultra", "lite", "full"]
    per_level: dict[str, LevelStats] = {lv: LevelStats(lv) for lv in levels}
    total = correct = 0

    for prompt, expected, note in CORE_SUITE:
        r: ClassificationResult = classify(prompt)
        passed = (r.level == expected)
        cr = CaseResult(
            prompt=prompt, expected=expected, got=r.level,
            note=note, passed=passed,
            confidence=r.confidence, reasons=r.reasons,
        )
        s = per_level[expected]
        s.total    += 1
        s.conf_sum += r.confidence
        if passed:
            s.correct += 1
            correct   += 1
        else:
            s.failures.append(cr)
        total += 1

    # Edge cases
    edge_results = []
    for prompt, expected, note in EDGE_SUITE:
        r = classify(prompt)
        passed = (r.level == expected)
        edge_results.append(CaseResult(
            prompt=prompt, expected=expected, got=r.level,
            note=note, passed=passed,
            confidence=r.confidence, reasons=r.reasons,
        ))

    return ValidationReport(
        timestamp=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        per_level=per_level,
        edge_results=edge_results,
        total=total,
        correct=correct,
    )


# ── Formatters ────────────────────────────────────────────────────────────────

_PASS = "PASS"
_FAIL = "FAIL"
_W    = 52   # prompt column width


def _trunc(s: str, n: int) -> str:
    return s if len(s) <= n else s[: n - 1] + "…"


def print_summary(report: ValidationReport) -> None:
    print()
    print("繁體中文分類器驗證報告")
    print("═" * 62)
    hdr = f"{'Level':<7}  {'Expected':>8}  {'Correct':>7}  {'Accuracy':>9}  {'Avg Conf':>9}"
    print(hdr)
    print("─" * 62)
    for lv in ("off", "ultra", "lite", "full"):
        s = report.per_level[lv]
        print(f"{lv:<7}  {s.total:>8}  {s.correct:>7}  "
              f"{s.accuracy:>8.1f}%  {s.avg_conf:>9.3f}")
    print("─" * 62)
    print(f"{'TOTAL':<7}  {report.total:>8}  {report.correct:>7}  "
          f"{report.overall_accuracy:>8.1f}%")
    print()

    # Edge cases
    if report.edge_results:
        print("邊界案例")
        print("─" * 62)
        for cr in report.edge_results:
            tag = _PASS if cr.passed else _FAIL
            note = f"  [{cr.note}]"
            print(f"[{tag}]  {cr.got:<5}  {cr.confidence:.2f}  "
                  f"{_trunc(cr.prompt, 38)}{note}")
        print()

    # Verdict
    off_ok     = report.off_accuracy >= 100.0
    overall_ok = report.overall_accuracy >= 90.0
    print(f"OFF level  : {'✓ PASS (零容忍 100%)' if off_ok else '✗ FAIL — 安全風險'}")
    print(f"整體準確率  : {'✓ PASS' if overall_ok else '✗ FAIL'} "
          f"({report.overall_accuracy:.1f}% {'≥' if overall_ok else '<'} 90%)")
    print()


def print_verbose(report: ValidationReport, failures_only: bool, show_reasons: bool) -> None:
    print()
    print("詳細結果")
    print("─" * 62)
    for lv in ("off", "ultra", "lite", "full"):
        s = report.per_level[lv]
        print(f"\n── {lv.upper()} ({s.correct}/{s.total}) ──")
        for prompt, expected, note in CORE_SUITE:
            if expected != lv:
                continue
            r = classify(prompt)
            passed = r.level == expected
            if failures_only and passed:
                continue
            tag  = _PASS if passed else _FAIL
            line = f"[{tag}]  {r.level:<5}  {r.confidence:.2f}  {_trunc(prompt, _W)}"
            if not passed:
                line += f"  → expected: {expected}"
            if note:
                line += f"  [{note}]"
            print(line)
            if show_reasons:
                for reason in r.reasons:
                    print(f"       reason: {reason}")

    if report.edge_results:
        print(f"\n── EDGE CASES ──")
        for cr in report.edge_results:
            tag  = _PASS if cr.passed else _FAIL
            line = f"[{tag}]  {cr.got:<5}  {cr.confidence:.2f}  {_trunc(cr.prompt, _W)}"
            if not cr.passed:
                line += f"  → expected: {cr.expected}"
            line += f"  [{cr.note}]"
            print(line)
            if show_reasons:
                for reason in cr.reasons:
                    print(f"       reason: {reason}")
    print()


def print_json(report: ValidationReport) -> None:
    out = {
        "timestamp": report.timestamp,
        "overall_accuracy": round(report.overall_accuracy / 100, 4),
        "off_accuracy": round(report.off_accuracy / 100, 4),
        "total": report.total,
        "correct": report.correct,
        "exit_code": report.exit_code(),
        "per_level": {
            lv: {
                "total":    s.total,
                "correct":  s.correct,
                "accuracy": round(s.accuracy / 100, 4),
                "avg_conf": round(s.avg_conf, 4),
                "failures": [
                    {
                        "prompt":   cr.prompt,
                        "expected": cr.expected,
                        "got":      cr.got,
                        "note":     cr.note,
                        "confidence": round(cr.confidence, 4),
                        "reasons":  cr.reasons,
                    }
                    for cr in s.failures
                ],
            }
            for lv, s in report.per_level.items()
        },
        "edge_cases": [
            {
                "prompt":   cr.prompt,
                "expected": cr.expected,
                "got":      cr.got,
                "passed":   cr.passed,
                "note":     cr.note,
                "confidence": round(cr.confidence, 4),
            }
            for cr in report.edge_results
        ],
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate Traditional Chinese caveman classifier",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Show per-prompt results")
    parser.add_argument("--failures-only", action="store_true",
                        help="With --verbose: show only failures")
    parser.add_argument("--show-reasons", action="store_true",
                        help="With --verbose: show classifier reasons")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON report (suppresses summary)")
    args = parser.parse_args()

    report = run_validation()

    if args.json:
        print_json(report)
    else:
        print_summary(report)
        if args.verbose:
            print_verbose(report, args.failures_only, args.show_reasons)

    return report.exit_code()


if __name__ == "__main__":
    sys.exit(main())
