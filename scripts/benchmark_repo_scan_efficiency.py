#!/usr/bin/env python3
from __future__ import annotations

import json
import statistics
import time
from pathlib import Path

from run_subagent_checks import review_worker

ROOT = Path(__file__).resolve().parents[1]
OUT_MD = ROOT / 'docs' / 'reports' / 'repo_scan_efficiency_20260415.md'
OUT_JSON = ROOT / 'docs' / 'reports' / 'repo_scan_efficiency_20260415.json'


def _run(exclude_patterns: tuple[str, ...], rounds: int = 5) -> tuple[float, dict]:
    elapsed_samples: list[float] = []
    last_payload: dict = {}
    for _ in range(rounds):
        elapsed_ms, payload = _run_once(exclude_patterns)
        elapsed_samples.append(elapsed_ms)
        last_payload = payload
    return statistics.median(elapsed_samples), last_payload


def _run_once(exclude_patterns: tuple[str, ...]) -> tuple[float, dict]:
    start = time.perf_counter()
    _, metrics = review_worker(ROOT, None, exclude_patterns=exclude_patterns)
    elapsed_ms = (time.perf_counter() - start) * 1000
    return elapsed_ms, {'metrics': metrics}


def main() -> None:
    baseline_ms, baseline = _run(tuple())  # no exclusions
    optimized_ms, optimized = _run(
        (
            'docs/reports/*.json',
            'docs/reports/*.md',
            'Memory.md',
            'README.md',
            'AGENTS.full.md',
            'scripts/run_subagent_checks.py',
        )
    )

    b = baseline['metrics']
    o = optimized['metrics']
    scanned_delta = o['scanned_repo_chars'] - b['scanned_repo_chars']
    speedup_pct = (baseline_ms - optimized_ms) / max(baseline_ms, 1e-9) * 100

    data = {
        'baseline_elapsed_ms': round(baseline_ms, 2),
        'optimized_elapsed_ms': round(optimized_ms, 2),
        'speedup_pct': round(speedup_pct, 2),
        'baseline_scanned_repo_chars': b['scanned_repo_chars'],
        'optimized_scanned_repo_chars': o['scanned_repo_chars'],
        'scanned_repo_chars_delta': scanned_delta,
        'baseline_tracked_text_files': b['tracked_text_files'],
        'optimized_tracked_text_files': o['tracked_text_files'],
        'optimized_skipped_file_count': o['skipped_file_count'],
    }

    OUT_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

    lines = [
        '# Repo Scan Efficiency Benchmark (2026-04-15)',
        '',
        '| Variant | Elapsed ms | Scanned chars | Tracked files | Skipped files |',
        '|---|---:|---:|---:|---:|',
        f"| baseline(no exclude) | {data['baseline_elapsed_ms']} | {data['baseline_scanned_repo_chars']} | {data['baseline_tracked_text_files']} | 0 |",
        f"| optimized(default exclude) | {data['optimized_elapsed_ms']} | {data['optimized_scanned_repo_chars']} | {data['optimized_tracked_text_files']} | {data['optimized_skipped_file_count']} |",
        '',
        f"- Speedup: **{data['speedup_pct']}%**",
        f"- scanned_repo_chars_delta: **{data['scanned_repo_chars_delta']}** (negative is better)",
    ]
    OUT_MD.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Wrote: {OUT_MD}')
    print(f'Wrote: {OUT_JSON}')


if __name__ == '__main__':
    main()
