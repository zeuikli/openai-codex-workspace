# Repo Scan Efficiency Benchmark (2026-04-15)

| Variant | Elapsed ms | Scanned chars | Tracked files | Skipped files |
|---|---:|---:|---:|---:|
| baseline(no exclude) | 17.63 | 131219 | 47 | 0 |
| optimized(default exclude) | 15.54 | 81951 | 40 | 7 |

- Speedup: **11.88%**
- scanned_repo_chars_delta: **-49268** (negative is better)
