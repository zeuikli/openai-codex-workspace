# Repo Parity Report (Upstream vs Workspace)

Date: `2026-04-15`  
Workspace: `/workspace/openai-codex-workspace/caveman`  
Upstream: `https://github.com/JuliusBrussee/caveman`

## Goal

Confirm whether all files from upstream exist in this workspace, then document intentional differences for maintenance reference.

## Comparison Method

1. Clone upstream with `git clone --depth 1 https://github.com/JuliusBrussee/caveman.git`.
2. Compare file sets and file content hashes (`sha256`) between:
   - workspace: `caveman/`
   - upstream clone
3. Exclude non-source artifacts:
   - directory names: `.git`, `__pycache__`
   - suffixes: `.pyc`
   - generated result path: `benchmarks/results/*`

Machine-readable output: `docs/repo-parity-report.json`.

## Result Summary

- Upstream files: **102**
- Workspace files: **105**
- Missing from workspace: **0** ✅
- Extra in workspace: **3**
- Content differences on same path: **4**

## Differences

### A) Extra files in workspace (not in upstream)

1. `benchmarks/openai_workspace_benchmark.py`
2. `scripts/run_codex_cloud_load_test.py`
3. `docs/repo-parity-report.json`

Reason: workspace-specific benchmarking/load-test tooling and this parity report artifact.

### B) Files present in both but content differs

1. `.gitignore`
2. `README.md`
3. `hooks/caveman-activate.js`
4. `hooks/caveman-mode-tracker.js`

Reason: local workspace integration, hook compatibility fixes for local verification, and documentation updates.

## Conclusion

All upstream files are present in current workspace (no missing files).  
Current differences are additive or intentional workspace customizations.
