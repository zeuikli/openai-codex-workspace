#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from validate_codex_workspace import validate_workspace


@dataclass
class WorkerResult:
    name: str
    status: str
    summary: str
    details: list[str]


@dataclass
class SessionTokenMetrics:
    log_path: str
    total_input_tokens: int
    total_cached_input_tokens: int
    uncached_input_tokens: int
    total_output_tokens: int
    total_reasoning_output_tokens: int
    total_tokens: int
    last_turn_total_tokens: int
    last_turn_share_pct: float
    cached_input_share_pct: float


def _tail(text: str, lines: int = 20) -> str:
    content = [line for line in text.strip().splitlines() if line.strip()]
    if not content:
        return '(no output)'
    return '\n'.join(content[-lines:])


def _run_command(cmd: list[str], root: Path) -> tuple[bool, str]:
    result = subprocess.run(cmd, cwd=root, capture_output=True, text=True, check=False)
    ok = result.returncode == 0
    combined = '\n'.join(part for part in [result.stdout, result.stderr] if part).strip()
    return ok, _tail(combined)


def _find_latest_session_log(explicit: str | None) -> Path | None:
    if explicit:
        candidate = Path(explicit).expanduser().resolve()
        return candidate if candidate.exists() else None

    env_path = os.getenv('CODEX_SESSION_LOG')
    if env_path:
        candidate = Path(env_path).expanduser().resolve()
        return candidate if candidate.exists() else None

    sessions_root = Path('~/.codex/sessions').expanduser()
    if not sessions_root.exists():
        return None
    logs = sorted(sessions_root.glob('**/*.jsonl'), key=lambda p: p.stat().st_mtime, reverse=True)
    return logs[0] if logs else None


def _extract_usage_snapshot(obj: Any) -> dict[str, int] | None:
    if isinstance(obj, dict):
        required = {
            'total_input_tokens',
            'total_cached_input_tokens',
            'total_output_tokens',
            'total_reasoning_output_tokens',
            'total_tokens',
            'last_turn_total_tokens',
        }
        if required.issubset(obj.keys()):
            try:
                return {key: int(obj[key]) for key in required}
            except (TypeError, ValueError):
                return None
        for value in obj.values():
            nested = _extract_usage_snapshot(value)
            if nested:
                return nested
    elif isinstance(obj, list):
        for item in obj:
            nested = _extract_usage_snapshot(item)
            if nested:
                return nested
    return None


def load_session_token_metrics(session_log: Path | None) -> SessionTokenMetrics | None:
    if not session_log or not session_log.exists():
        return None

    latest_usage: dict[str, int] | None = None
    for line in session_log.read_text(encoding='utf-8').splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError:
            continue
        usage = _extract_usage_snapshot(payload)
        if usage:
            latest_usage = usage

    if not latest_usage:
        return None

    total_input_tokens = latest_usage['total_input_tokens']
    total_cached_input_tokens = latest_usage['total_cached_input_tokens']
    uncached_input_tokens = max(total_input_tokens - total_cached_input_tokens, 0)
    total_tokens = max(latest_usage['total_tokens'], 1)
    last_turn_total_tokens = latest_usage['last_turn_total_tokens']

    return SessionTokenMetrics(
        log_path=session_log.as_posix(),
        total_input_tokens=total_input_tokens,
        total_cached_input_tokens=total_cached_input_tokens,
        uncached_input_tokens=uncached_input_tokens,
        total_output_tokens=latest_usage['total_output_tokens'],
        total_reasoning_output_tokens=latest_usage['total_reasoning_output_tokens'],
        total_tokens=latest_usage['total_tokens'],
        last_turn_total_tokens=last_turn_total_tokens,
        last_turn_share_pct=round(last_turn_total_tokens / total_tokens * 100, 2),
        cached_input_share_pct=round(total_cached_input_tokens / max(total_input_tokens, 1) * 100, 2),
    )


def research_worker(root: Path) -> WorkerResult:
    errors = validate_workspace(root)
    if errors:
        return WorkerResult(
            name='Research Worker (docs_researcher)',
            status='failed',
            summary='Workspace baseline validation failed.',
            details=errors,
        )

    expected_models = {
        'docs_researcher.toml': 'gpt-5.4-mini',
        'architecture_explorer.toml': 'gpt-5.4-mini',
        'implementer.toml': 'gpt-5.3-codex',
        'reviewer.toml': 'gpt-5.3-codex',
        'security_reviewer.toml': 'gpt-5.3-codex',
        'test_writer.toml': 'gpt-5.3-codex',
    }
    mismatches: list[str] = []
    for filename, expected in expected_models.items():
        content = (root / '.codex' / 'agents' / filename).read_text(encoding='utf-8')
        marker = f'model = "{expected}"'
        if marker not in content:
            mismatches.append(f'{filename} expected {expected}')

    if mismatches:
        return WorkerResult(
            name='Research Worker (docs_researcher)',
            status='failed',
            summary='Agent model routing drift detected.',
            details=mismatches,
        )

    return WorkerResult(
        name='Research Worker (docs_researcher)',
        status='passed',
        summary='Baseline structure and model routing are aligned with AGENT/SKILL policy.',
        details=['validate_codex_workspace.py passed (in-process check).'],
    )


def implement_worker(root: Path) -> WorkerResult:
    checks = [
        ['python3', 'scripts/validate_codex_workspace.py'],
        ['python3', '-m', 'unittest', '-v', 'tests/test_codex_hooks_behavior.py'],
    ]
    failures: list[str] = []
    details: list[str] = []
    for cmd in checks:
        ok, tail = _run_command(cmd, root)
        rendered = f"$ {' '.join(cmd)}\n{tail}"
        if ok:
            details.append(rendered)
        else:
            failures.append(rendered)

    if failures:
        return WorkerResult(
            name='Implement Worker (implementer)',
            status='failed',
            summary='Implementation quality gate has failing checks.',
            details=failures,
        )

    return WorkerResult(
        name='Implement Worker (implementer)',
        status='passed',
        summary='Implementation quality gate passed (validate + hook tests).',
        details=details,
    )


def review_worker(root: Path, token_metrics: SessionTokenMetrics | None) -> tuple[WorkerResult, dict[str, Any]]:
    tracked = subprocess.run(
        ['git', 'ls-files'], cwd=root, capture_output=True, text=True, check=False
    )
    files = [line.strip() for line in tracked.stdout.splitlines() if line.strip()]

    total_tokens = 0
    unreadable = 0
    conflict_files: list[str] = []
    todo_files: list[str] = []
    hot_files: list[tuple[str, int]] = []
    docs_drift_signals: list[str] = []
    security_hits: dict[str, int] = {}

    security_patterns = {
        'hardcoded_password': re.compile(r'password\s*=\s*["\'][^"\']+["\']', re.IGNORECASE),
        'private_key_marker': re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----'),
        'aws_access_key_id': re.compile(r'AKIA[0-9A-Z]{16}'),
    }
    security_scan_suffixes = {'.py', '.sh', '.bash', '.yml', '.yaml', '.toml', '.json'}

    for rel in files:
        path = root / rel
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding='utf-8')
        except UnicodeDecodeError:
            unreadable += 1
            continue

        chars = len(text)
        total_tokens += chars
        hot_files.append((rel, chars))

        if re.search(r'^(<{7}|={7}|>{7})', text, flags=re.MULTILINE):
            conflict_files.append(rel)
        if 'TODO' in text or 'FIXME' in text:
            todo_files.append(rel)
        if path.suffix in security_scan_suffixes:
            for pattern_name, regex in security_patterns.items():
                matches = len(regex.findall(text))
                if matches:
                    security_hits[pattern_name] = security_hits.get(pattern_name, 0) + matches

    hot_files.sort(key=lambda item: item[1], reverse=True)
    top_hot = hot_files[:10]

    docs_alignment_checks = [
        ('README.md', 'scripts/run_subagent_checks.py'),
        ('README.md', 'scripts/validate_codex_workspace.py'),
        ('prompts.md', 'Done when'),
        ('AGENTS.md', 'Karpathy 實作原則'),
    ]
    for rel, needle in docs_alignment_checks:
        text = (root / rel).read_text(encoding='utf-8')
        if needle not in text:
            docs_drift_signals.append(f'{rel} missing marker: {needle}')

    security_baseline_file = root / 'docs' / 'reports' / 'security-pattern-baseline.json'
    security_baseline: dict[str, int] = {}
    if security_baseline_file.exists():
        try:
            security_baseline = json.loads(security_baseline_file.read_text(encoding='utf-8'))
        except json.JSONDecodeError:
            docs_drift_signals.append('security-pattern-baseline.json is not valid JSON')

    security_violations: list[str] = []
    for pattern_name, hits in sorted(security_hits.items()):
        threshold = int(security_baseline.get(pattern_name, 0))
        if hits > threshold:
            security_violations.append(f'{pattern_name}: hits={hits} > baseline={threshold}')

    details = [
        f'tracked_text_files={len(hot_files)} unreadable_files={unreadable}',
        f'total_repo_chars={total_tokens}',
        'top_context_hotspots_by_chars=' + ', '.join(f'{name}({tok})' for name, tok in top_hot),
    ]
    if token_metrics:
        details.extend(
            [
                f'session_log={token_metrics.log_path}',
                f'total_input_tokens={token_metrics.total_input_tokens}',
                f'total_cached_input_tokens={token_metrics.total_cached_input_tokens}',
                f'uncached_input_tokens={token_metrics.uncached_input_tokens}',
                f'total_output_tokens={token_metrics.total_output_tokens}',
                f'total_reasoning_output_tokens={token_metrics.total_reasoning_output_tokens}',
                f'total_tokens={token_metrics.total_tokens}',
                f'last_turn_total_tokens={token_metrics.last_turn_total_tokens}',
                f'last_turn_share_pct={token_metrics.last_turn_share_pct}',
                f'cached_input_share_pct={token_metrics.cached_input_share_pct}',
            ]
        )
    else:
        details.append('session_token_log=unavailable')

    if conflict_files:
        details.append('merge_conflict_markers=' + ', '.join(conflict_files))
    if todo_files:
        details.append('todo_or_fixme_files=' + ', '.join(todo_files[:20]))
    if docs_drift_signals:
        details.append('docs_drift_signals=' + '; '.join(docs_drift_signals))
    if security_violations:
        details.append('security_pattern_violations=' + '; '.join(security_violations))

    blocking_findings = bool(conflict_files or docs_drift_signals or security_violations)
    status = 'failed' if blocking_findings else 'passed'
    summary = 'Repository-wide scan passed.' if status == 'passed' else 'Repository-wide scan found blocking issues.'

    metrics = {
        'tracked_text_files': len(hot_files),
        'unreadable_files': unreadable,
        'total_repo_chars': total_tokens,
        'top_context_hotspots_by_chars': [{'path': name, 'chars': tok} for name, tok in top_hot],
        'todo_or_fixme_file_count': len(todo_files),
        'merge_conflict_file_count': len(conflict_files),
        'docs_drift_signal_count': len(docs_drift_signals),
        'security_pattern_violation_count': len(security_violations),
        'security_pattern_hits': security_hits,
        'session_token_metrics': token_metrics.__dict__ if token_metrics else None,
    }
    return WorkerResult('Review Worker (reviewer+security_reviewer)', status, summary, details), metrics


def optimization_actions(metrics: dict[str, Any]) -> list[str]:
    hotspots = metrics.get('top_context_hotspots_by_chars', [])
    first_three = [item['path'] for item in hotspots[:3]]
    actions = [
        '保持 skills 按需載入，避免在每個任務預讀全部 SKILL.md。',
        '將高讀取低修改的研究任務優先分派給 gpt-5.4-mini。',
        '將實作與測試集中到 gpt-5.3-codex，降低主模型上下文負擔。',
    ]
    if first_three:
        actions.append('優先摘要高 token 檔案後再進入最終回覆：' + ', '.join(first_three))
    actions.append('若最終收斂任務無高風險決策，reasoning 建議維持 medium；僅在衝突收斂時升級 high/xhigh。')
    return actions


def render_markdown(results: list[WorkerResult], metrics: dict[str, Any], actions: list[str]) -> str:
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%SZ')
    lines = [
        '# Sub-Agent Quality Report',
        '',
        f'- Generated at: `{now}`',
        '- Goal: 以 sub-agent 觀點執行全 repo 檢查，降低 workflow 錯誤與 token 成本。',
        '',
        '## Worker Results',
    ]
    for result in results:
        lines.extend(
            [
                '',
                f"### {result.name}",
                f"- Status: **{result.status.upper()}**",
                f'- Summary: {result.summary}',
            ]
        )
        if result.details:
            lines.append('- Details:')
            lines.extend([f'  - {detail}' for detail in result.details])

    lines.extend(
        [
            '',
            '## Token Efficiency Snapshot (Session Log)',
            f"- tracked_text_files: {metrics['tracked_text_files']}",
            f"- total_repo_chars: {metrics['total_repo_chars']}",
            f"- todo_or_fixme_file_count: {metrics['todo_or_fixme_file_count']}",
            f"- merge_conflict_file_count: {metrics['merge_conflict_file_count']}",
            f"- docs_drift_signal_count: {metrics['docs_drift_signal_count']}",
            f"- security_pattern_violation_count: {metrics['security_pattern_violation_count']}",
        '',
            '## Optimization Actions',
        ]
    )
    session_metrics = metrics.get('session_token_metrics')
    if session_metrics:
        lines.extend(
            [
                '',
                '### Session Token Metrics',
                f"- session_log: `{session_metrics['log_path']}`",
                f"- total_input_tokens: {session_metrics['total_input_tokens']}",
                f"- total_cached_input_tokens: {session_metrics['total_cached_input_tokens']}",
                f"- uncached_input_tokens: {session_metrics['uncached_input_tokens']}",
                f"- total_output_tokens: {session_metrics['total_output_tokens']}",
                f"- total_reasoning_output_tokens: {session_metrics['total_reasoning_output_tokens']}",
                f"- total_tokens: {session_metrics['total_tokens']}",
                f"- last_turn_total_tokens: {session_metrics['last_turn_total_tokens']}",
                f"- last_turn_share_pct: {session_metrics['last_turn_share_pct']}",
                f"- cached_input_share_pct: {session_metrics['cached_input_share_pct']}",
            ]
        )
    else:
        lines.extend(['', '### Session Token Metrics', '- session_log: unavailable'])

    lines.extend([f'- {action}' for action in actions])

    lines.extend(
        [
            '',
            '## Done/Blocked/Cancelled',
            '- Done: Research/Implement/Review 三個 worker 檢查皆有輸出。',
            '- Blocked: 無。',
            '- Cancelled: 無。',
        ]
    )
    return '\n'.join(lines) + '\n'


def main() -> int:
    parser = argparse.ArgumentParser(description='Run sub-agent quality checks and build a consolidated report.')
    parser.add_argument('--root', default='.', help='Repository root path')
    parser.add_argument(
        '--output',
        default='docs/reports/subagent-quality-report.md',
        help='Output markdown report path',
    )
    parser.add_argument(
        '--json-output',
        default='docs/reports/subagent-quality-report.json',
        help='Output JSON report path',
    )
    parser.add_argument(
        '--session-log',
        default=None,
        help='Codex session JSONL log path. If omitted, auto-detect from CODEX_SESSION_LOG or ~/.codex/sessions.',
    )
    args = parser.parse_args()

    root = Path(args.root).resolve()
    md_out = (root / args.output).resolve()
    json_out = (root / args.json_output).resolve()

    research = research_worker(root)
    implement = implement_worker(root)
    token_metrics = load_session_token_metrics(_find_latest_session_log(args.session_log))
    review, metrics = review_worker(root, token_metrics)
    actions = optimization_actions(metrics)

    results = [research, implement, review]
    markdown = render_markdown(results, metrics, actions)

    md_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.write_text(markdown, encoding='utf-8')

    payload = {
        'results': [result.__dict__ for result in results],
        'metrics': metrics,
        'optimization_actions': actions,
        'generated_at': datetime.now(timezone.utc).isoformat(),
    }
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8')

    has_failure = any(result.status != 'passed' for result in results)
    try:
        md_display = md_out.relative_to(root)
    except ValueError:
        md_display = md_out
    try:
        json_display = json_out.relative_to(root)
    except ValueError:
        json_display = json_out

    print(f'Report written: {md_display}')
    print(f'Report written: {json_display}')
    return 1 if has_failure else 0


if __name__ == '__main__':
    raise SystemExit(main())
