# Codex Cloud Load Test

Generated at: `2026-04-16T02:22:49.505879+00:00`

Overall status: **PASS**

| Command | Return code |
|---|---:|
| `python3 -m pytest tests/ -v --tb=short` | 0 |
| `python3 scripts/validate_codex_workspace.py` | 0 |
| `python3 tests/caveman/verify_repo.py` | 0 |

## Output tails

### `python3 -m pytest tests/ -v --tb=short`

**stdout (tail):**
```text
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_be_brief PASSED [ 54%]
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_brief PASSED [ 56%]
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_list_all PASSED [ 59%]
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_long_prompt PASSED [ 62%]
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_summarize PASSED [ 64%]
tests/test_caveman_auto_level.py::AutoLevelClassifierTest::test_ultra_tl_dr PASSED [ 67%]
tests/test_caveman_compress.py::CavemanCompressTests::test_build_prompts_preserve_fixing_contract PASSED [ 70%]
tests/test_caveman_compress.py::CavemanCompressTests::test_detect_identifies_markdown_and_skips_code PASSED [ 72%]
tests/test_caveman_compress.py::CavemanCompressTests::test_sensitive_path_detection_blocks_credentials PASSED [ 75%]
tests/test_caveman_compress.py::CavemanCompressTests::test_strip_llm_wrapper_removes_outer_markdown_fence_only PASSED [ 78%]
tests/test_caveman_compress.py::CavemanCompressTests::test_validate_preserves_headings_urls_and_code_blocks PASSED [ 81%]
tests/test_codex_hooks_behavior.py::CodexHooksBehaviorTest::test_post_tool_use_emits_commit_note PASSED [ 83%]
tests/test_codex_hooks_behavior.py::CodexHooksBehaviorTest::test_pre_tool_use_allows_git_push_to_feature_branch PASSED [ 86%]
tests/test_codex_hooks_behavior.py::CodexHooksBehaviorTest::test_pre_tool_use_allows_safe_command PASSED [ 89%]
tests/test_codex_hooks_behavior.py::CodexHooksBehaviorTest::test_pre_tool_use_blocks_git_push_to_main PASSED [ 91%]
tests/test_codex_hooks_behavior.py::CodexHooksBehaviorTest::test_session_start_includes_karpathy_notice PASSED [ 94%]
tests/test_subagent_checks.py::SubAgentChecksScriptTest::test_script_generates_reports PASSED [ 97%]
tests/test_subagent_checks.py::SubAgentChecksScriptTest::test_trend_script_generates_history_and_report PASSED [100%]

======================== 33 passed, 4 skipped in 0.42s =========================
```

**stderr (tail):**
```text
(empty)
```

### `python3 scripts/validate_codex_workspace.py`

**stdout (tail):**
```text
Codex workspace validation passed.
```

**stderr (tail):**
```text
(empty)
```

### `python3 tests/caveman/verify_repo.py`

**stdout (tail):**
```text
== Repo Layout ==
Codex-native caveman assets present

== Manifest And Syntax ==
[SKIP] node not found — JS syntax checks skipped (install Node.js to enable)
Shell syntax OK

== Compress Fixtures ==
Validated 1 caveman-compress fixture pairs

== Compress CLI ==
Compress CLI skip/error paths OK

== Hook Flow ==
[SKIP] node not found — hook flow checks skipped (install Node.js to enable)

All caveman checks passed.
```

**stderr (tail):**
```text
(empty)
```
