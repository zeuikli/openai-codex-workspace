#!/usr/bin/env python3
"""Unit tests for caveman_auto_level.py prompt classifier."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from caveman_auto_level import classify  # type: ignore


class AutoLevelClassifierTest(unittest.TestCase):

    # ── lite ─────────────────────────────────────────────────────────────────
    def test_lite_simple_definition(self):
        self.assertEqual(classify("What is TCP?").level, "lite")

    def test_lite_yes_no_question(self):
        self.assertEqual(classify("Is Python interpreted?").level, "lite")

    def test_lite_short_confirmation(self):
        self.assertEqual(classify("ok").level, "lite")

    def test_lite_what_does_mean(self):
        self.assertEqual(classify("what does idempotent mean?").level, "lite")

    # ── full ──────────────────────────────────────────────────────────────────
    def test_full_explain_technical(self):
        self.assertEqual(classify("Explain database connection pooling.").level, "full")

    def test_full_debug_question(self):
        self.assertEqual(classify("Why does my React component re-render every time?").level, "full")

    def test_full_how_to(self):
        self.assertEqual(classify("How do I fix a memory leak in Node.js?").level, "full")

    def test_full_code_review(self):
        self.assertEqual(classify("Review this authentication middleware for security issues.").level, "full")

    def test_full_difference_between(self):
        self.assertEqual(classify("What's the difference between TCP and UDP?").level, "full")

    # ── ultra ─────────────────────────────────────────────────────────────────
    def test_ultra_summarize(self):
        self.assertEqual(classify("Summarize all the changes in this PR.").level, "ultra")

    def test_ultra_list_all(self):
        self.assertEqual(classify("List all environment variables in this project.").level, "ultra")

    def test_ultra_tl_dr(self):
        self.assertEqual(classify("tl;dr what does this code do?").level, "ultra")

    def test_ultra_brief(self):
        self.assertEqual(classify("Brief overview of the architecture.").level, "ultra")

    def test_ultra_be_brief(self):
        self.assertEqual(classify("Be brief: how does Kubernetes work?").level, "ultra")

    def test_ultra_long_prompt(self):
        long = "Please analyze and summarize all files in the repository. " * 10
        self.assertEqual(classify(long).level, "ultra")

    # ── off ───────────────────────────────────────────────────────────────────
    def test_off_drop_table(self):
        self.assertEqual(classify("DROP TABLE users;").level, "off")

    def test_off_rm_rf(self):
        self.assertEqual(classify("rm -rf /var/data").level, "off")

    def test_off_delete_all(self):
        self.assertEqual(classify("delete all database records").level, "off")

    def test_off_irreversible(self):
        self.assertEqual(classify("This action is irreversible and will delete everything.").level, "off")

    # ── confidence bounds ─────────────────────────────────────────────────────
    def test_confidence_is_float_between_0_and_1(self):
        for prompt in ["ok", "Explain TCP", "Summarize all logs", "DROP TABLE users"]:
            r = classify(prompt)
            self.assertIsInstance(r.confidence, float, f"not float for: {prompt}")
            self.assertGreater(r.confidence, 0.0, f"confidence 0 for: {prompt}")
            self.assertLessEqual(r.confidence, 1.0, f"confidence >1 for: {prompt}")

    # ── as_dict ───────────────────────────────────────────────────────────────
    def test_as_dict_has_required_keys(self):
        d = classify("Explain Python").as_dict()
        for key in ("level", "confidence", "reasons", "scores"):
            self.assertIn(key, d)


if __name__ == "__main__":
    unittest.main()
