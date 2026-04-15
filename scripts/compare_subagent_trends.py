#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding='utf-8'))


def _metric(payload: dict[str, Any], key: str, default: int = 0) -> int:
    session = payload.get('metrics', {}).get('session_token_metrics') or {}
    return int(session.get(key, default))


def main() -> int:
    parser = argparse.ArgumentParser(description='Persist and compare sub-agent quality trend metrics.')
    parser.add_argument('--current-json', default='docs/reports/subagent-quality-report.json')
    parser.add_argument('--history-json', default='docs/reports/subagent-quality-history.json')
    parser.add_argument('--output-md', default='docs/reports/subagent-quality-trend.md')
    args = parser.parse_args()

    current_path = Path(args.current_json)
    history_path = Path(args.history_json)
    output_md = Path(args.output_md)

    current = _read_json(current_path)
    now = datetime.now(timezone.utc).isoformat()
    row = {
        'generated_at': current.get('generated_at', now),
        'total_tokens': _metric(current, 'total_tokens'),
        'total_cached_input_tokens': _metric(current, 'total_cached_input_tokens'),
        'uncached_input_tokens': _metric(current, 'uncached_input_tokens'),
        'last_turn_total_tokens': _metric(current, 'last_turn_total_tokens'),
        'last_turn_share_pct': float((current.get('metrics', {}).get('session_token_metrics') or {}).get('last_turn_share_pct', 0.0)),
        'cached_input_share_pct': float((current.get('metrics', {}).get('session_token_metrics') or {}).get('cached_input_share_pct', 0.0)),
        'docs_drift_signal_count': int(current.get('metrics', {}).get('docs_drift_signal_count', 0)),
        'security_pattern_violation_count': int(current.get('metrics', {}).get('security_pattern_violation_count', 0)),
        'tracked_text_files': int(current.get('metrics', {}).get('tracked_text_files', 0)),
        'scanned_repo_chars': int(current.get('metrics', {}).get('scanned_repo_chars', 0)),
        'skipped_file_count': int(current.get('metrics', {}).get('skipped_file_count', 0)),
    }

    history: list[dict[str, Any]] = []
    if history_path.exists():
        history = json.loads(history_path.read_text(encoding='utf-8'))
        if not isinstance(history, list):
            history = []

    history.append(row)
    history = history[-60:]
    history_path.parent.mkdir(parents=True, exist_ok=True)
    history_path.write_text(json.dumps(history, ensure_ascii=False, indent=2), encoding='utf-8')

    previous = history[-2] if len(history) > 1 else None
    if previous:
        total_delta = row['total_tokens'] - previous['total_tokens']
        last_turn_delta = row['last_turn_share_pct'] - float(previous.get('last_turn_share_pct', 0.0))
        scanned_chars_delta = row['scanned_repo_chars'] - int(previous.get('scanned_repo_chars', 0))
        tracked_files_delta = row['tracked_text_files'] - int(previous.get('tracked_text_files', 0))
    else:
        total_delta = 0
        last_turn_delta = 0.0
        scanned_chars_delta = 0
        tracked_files_delta = 0

    lines = [
        '# Sub-Agent Quality Trend',
        '',
        f"- Updated at: `{now}`",
        f"- Data points: {len(history)}",
        '',
        '## Latest Snapshot',
        f"- total_tokens: {row['total_tokens']}",
        f"- total_cached_input_tokens: {row['total_cached_input_tokens']}",
        f"- uncached_input_tokens: {row['uncached_input_tokens']}",
        f"- last_turn_total_tokens: {row['last_turn_total_tokens']}",
        f"- last_turn_share_pct: {row['last_turn_share_pct']}",
        f"- cached_input_share_pct: {row['cached_input_share_pct']}",
        f"- docs_drift_signal_count: {row['docs_drift_signal_count']}",
        f"- security_pattern_violation_count: {row['security_pattern_violation_count']}",
        f"- tracked_text_files: {row['tracked_text_files']}",
        f"- scanned_repo_chars: {row['scanned_repo_chars']}",
        f"- skipped_file_count: {row['skipped_file_count']}",
        '',
        '## Delta vs Previous',
        f'- total_tokens_delta: {total_delta}',
        f'- last_turn_share_pct_delta: {round(last_turn_delta, 2)}',
        f'- scanned_repo_chars_delta: {scanned_chars_delta}',
        f'- tracked_text_files_delta: {tracked_files_delta}',
    ]

    output_md.parent.mkdir(parents=True, exist_ok=True)
    output_md.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Trend report written: {output_md}')
    print(f'Trend history written: {history_path}')

    if row['docs_drift_signal_count'] > 0 or row['security_pattern_violation_count'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
