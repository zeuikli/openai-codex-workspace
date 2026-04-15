from __future__ import annotations

import json
import subprocess
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

    def test_session_start_includes_karpathy_notice(self) -> None:
        result = self.run_hook('session_start_note.sh')
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        message = body['hookSpecificOutput']['additionalContext']
        self.assertIn('nine Karpathy principles', message)

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

    def test_post_tool_use_emits_commit_note(self) -> None:
        result = self.run_hook('post_tool_use_note.sh', {'tool_input': {'command': 'git commit -m "x"'}})
        self.assertEqual(result.returncode, 0)
        body = json.loads(result.stdout)
        self.assertIn('A commit was created', body['hookSpecificOutput']['additionalContext'])


if __name__ == '__main__':
    unittest.main(verbosity=2)
