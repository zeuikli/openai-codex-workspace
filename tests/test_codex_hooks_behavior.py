from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HOOKS_DIR = ROOT / '.codex' / 'hooks'


class CodexHooksBehaviorTest(unittest.TestCase):
    def run_hook(self, script_name: str, payload: dict[str, object] | None = None) -> subprocess.CompletedProcess[str]:
        input_data = ''
        if payload is not None:
            input_data = json.dumps(payload)
        return subprocess.run(
            ['bash', str(HOOKS_DIR / script_name)],
            input=input_data,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_pre_tool_use_blocks_git_push_to_main(self) -> None:
        result = self.run_hook('pre_tool_use_guard.sh', {'tool_input': {'command': 'git push origin main'}})
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        self.assertEqual(body['hookSpecificOutput']['permissionDecision'], 'deny')
        self.assertIn('protected branch', body['hookSpecificOutput']['permissionDecisionReason'])

    def test_pre_tool_use_allows_git_push_to_feature_branch(self) -> None:
        result = self.run_hook(
            'pre_tool_use_guard.sh',
            {'tool_input': {'command': 'git push origin codex/karpathy-cloud-refresh-20260414'}},
        )
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '')

    def test_pre_tool_use_allows_safe_command(self) -> None:
        result = self.run_hook('pre_tool_use_guard.sh', {'tool_input': {'command': 'echo hello'}})
        self.assertEqual(result.returncode, 0)
        self.assertEqual(result.stdout.strip(), '')

    def test_post_tool_use_validates_json(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json') as handle:
            handle.write('{invalid')
            handle.flush()
            result = self.run_hook(
                'post_tool_use_validate.sh',
                {'tool_input': {'file_path': handle.name}},
            )
        self.assertNotEqual(result.returncode, 0)

    def test_post_tool_use_ignores_unknown_file_type(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt') as handle:
            handle.write('anything')
            handle.flush()
            result = self.run_hook(
                'post_tool_use_validate.sh',
                {'tool_input': {'file_path': handle.name}},
            )
        self.assertEqual(result.returncode, 0)

    def test_post_tool_use_validates_toml_on_python_39(self) -> None:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.toml') as handle:
            handle.write('[broken')
            handle.flush()
            result = self.run_hook(
                'post_tool_use_validate.sh',
                {'tool_input': {'file_path': handle.name}},
            )
        self.assertNotEqual(result.returncode, 0)

    def test_compact_checkpoint_uses_codex_context(self) -> None:
        result = subprocess.run(
            ['bash', str(HOOKS_DIR / 'context_checkpoint.sh'), 'pre'],
            input='{}',
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        self.assertEqual(body['hookSpecificOutput']['hookEventName'], 'PreCompact')
        self.assertNotIn('Auto Memory', result.stdout)
        self.assertNotIn('TodoWrite', result.stdout)


if __name__ == '__main__':
    unittest.main(verbosity=2)
