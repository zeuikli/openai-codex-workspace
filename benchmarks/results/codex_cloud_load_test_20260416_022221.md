# Codex Cloud Load Test

Generated at: `2026-04-16T02:22:21.285365+00:00`

Overall status: **FAIL**

| Command | Return code |
|---|---:|
| `python3 tests/caveman/verify_repo.py` | 0 |
| `python3 -m unittest -v tests/caveman/test_hooks` | 1 |

## Output tails

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

### `python3 -m unittest -v tests/caveman/test_hooks`

**stdout (tail):**
```text
(empty)
```

**stderr (tail):**
```text
tests/caveman/test_hooks (unittest.loader._FailedTest) ... ERROR

======================================================================
ERROR: tests/caveman/test_hooks (unittest.loader._FailedTest)
----------------------------------------------------------------------
ImportError: Failed to import test module: tests/caveman/test_hooks
Traceback (most recent call last):
  File "/Library/Developer/CommandLineTools/Library/Frameworks/Python3.framework/Versions/3.9/lib/python3.9/unittest/loader.py", line 154, in loadTestsFromName
    module = __import__(module_name)
ModuleNotFoundError: No module named 'tests/caveman/test_hooks'


----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)
```
