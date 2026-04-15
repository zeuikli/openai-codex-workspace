from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class SubAgentChecksScriptTest(unittest.TestCase):
    def test_script_generates_reports(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            md = Path(temp_dir) / 'report.md'
            js = Path(temp_dir) / 'report.json'
            session_log = Path(temp_dir) / 'session.jsonl'
            session_log.write_text(
                '\n'.join(
                    [
                        json.dumps({'type': 'meta', 'message': 'start'}),
                        json.dumps(
                            {
                                'usage': {
                                    'total_input_tokens': 1200,
                                    'total_cached_input_tokens': 800,
                                    'total_output_tokens': 220,
                                    'total_reasoning_output_tokens': 75,
                                    'total_tokens': 1420,
                                    'last_turn_total_tokens': 320,
                                }
                            }
                        ),
                    ]
                )
                + '\n',
                encoding='utf-8',
            )
            result = subprocess.run(
                [
                    'python3',
                    'scripts/run_subagent_checks.py',
                    '--output',
                    str(md),
                    '--json-output',
                    str(js),
                    '--session-log',
                    str(session_log),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, msg=result.stdout + '\n' + result.stderr)
            self.assertTrue(md.exists())
            self.assertTrue(js.exists())

            report = md.read_text(encoding='utf-8')
            self.assertIn('Sub-Agent Quality Report', report)
            self.assertIn('Optimization Actions', report)

            payload = json.loads(js.read_text(encoding='utf-8'))
            self.assertIn('results', payload)
            self.assertIn('metrics', payload)
            self.assertEqual(len(payload['results']), 3)
            self.assertEqual(
                payload['metrics']['session_token_metrics']['uncached_input_tokens'],
                400,
            )
            self.assertIn('scanned_repo_chars', payload['metrics'])
            self.assertIn('skipped_file_count', payload['metrics'])

    def test_trend_script_generates_history_and_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            current = Path(temp_dir) / 'report.json'
            history = Path(temp_dir) / 'history.json'
            trend = Path(temp_dir) / 'trend.md'
            current.write_text(
                json.dumps(
                    {
                        'generated_at': '2026-04-14T00:00:00Z',
                        'metrics': {
                            'docs_drift_signal_count': 0,
                            'security_pattern_violation_count': 0,
                            'session_token_metrics': {
                                'total_tokens': 1000,
                                'total_cached_input_tokens': 700,
                                'uncached_input_tokens': 300,
                                'last_turn_total_tokens': 250,
                                'last_turn_share_pct': 25.0,
                                'cached_input_share_pct': 70.0,
                            },
                        },
                    }
                ),
                encoding='utf-8',
            )
            result = subprocess.run(
                [
                    'python3',
                    'scripts/compare_subagent_trends.py',
                    '--current-json',
                    str(current),
                    '--history-json',
                    str(history),
                    '--output-md',
                    str(trend),
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, msg=result.stdout + '\n' + result.stderr)
            self.assertTrue(history.exists())
            self.assertTrue(trend.exists())
            trend_text = trend.read_text(encoding='utf-8')
            self.assertIn('Latest Snapshot', trend_text)
            self.assertIn('scanned_repo_chars', trend_text)


if __name__ == '__main__':
    unittest.main(verbosity=2)
