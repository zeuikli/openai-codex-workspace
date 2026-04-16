import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path
from typing import Optional

_NODE_AVAILABLE = shutil.which("node") is not None
_SKIP_NODE = unittest.skipUnless(_NODE_AVAILABLE, "node not in PATH; install Node.js to run JS hook tests")


REPO_ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = REPO_ROOT / "hooks" / "caveman"


class HookScriptTests(unittest.TestCase):
    def hook_env(self, home: Path) -> dict[str, str]:
        env = os.environ.copy()
        env["HOME"] = str(home)
        env["USERPROFILE"] = str(home)
        return env

    def run_node(self, script: str, home: Path, *, input_text: str = "", extra_env: Optional[dict[str, str]] = None) -> subprocess.CompletedProcess[str]:
        env = self.hook_env(home)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["node", str(HOOKS_DIR / script)],
            cwd=REPO_ROOT,
            env=env,
            input=input_text,
            text=True,
            capture_output=True,
            check=True,
        )

    @_SKIP_NODE
    def test_activate_writes_default_flag_and_banner(self):
        with tempfile.TemporaryDirectory(prefix="caveman-hooks-activate-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)
            (claude_dir / "settings.json").write_text("{}\n")

            result = self.run_node("caveman-activate.js", home)

            self.assertIn("CAVEMAN MODE ACTIVE. level: full", result.stdout)
            self.assertIn("STATUSLINE SETUP NEEDED", result.stdout)
            self.assertEqual((claude_dir / ".caveman-active").read_text(), "full")

    @_SKIP_NODE
    def test_activate_skips_statusline_nudge_when_statusline_exists(self):
        with tempfile.TemporaryDirectory(prefix="caveman-hooks-statusline-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)
            (claude_dir / "settings.json").write_text(
                json.dumps({"statusLine": {"type": "command", "command": "bash /tmp/custom.sh"}}) + "\n"
            )

            result = self.run_node("caveman-activate.js", home)

            self.assertNotIn("STATUSLINE SETUP NEEDED", result.stdout)
            self.assertEqual((claude_dir / ".caveman-active").read_text(), "full")

    @_SKIP_NODE
    def test_mode_tracker_updates_and_clears_flag(self):
        with tempfile.TemporaryDirectory(prefix="caveman-hooks-track-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)
            flag = claude_dir / ".caveman-active"
            flag.write_text("full")

            result = self.run_node(
                "caveman-mode-tracker.js",
                home,
                input_text=json.dumps({"prompt": "/caveman ultra"}),
            )
            self.assertEqual(result.stdout, "")
            self.assertEqual(flag.read_text(), "ultra")

            self.run_node(
                "caveman-mode-tracker.js",
                home,
                input_text=json.dumps({"prompt": "normal mode"}),
            )
            self.assertFalse(flag.exists())

    @_SKIP_NODE
    def test_mode_tracker_supports_natural_language_activation(self):
        with tempfile.TemporaryDirectory(prefix="caveman-hooks-natural-") as tmp:
            home = Path(tmp)
            claude_dir = home / ".claude"
            claude_dir.mkdir(parents=True)

            self.run_node(
                "caveman-mode-tracker.js",
                home,
                input_text=json.dumps({"prompt": "please talk like caveman for this session"}),
                extra_env={"CAVEMAN_DEFAULT_MODE": "lite"},
            )
            self.assertEqual((claude_dir / ".caveman-active").read_text(), "lite")


if __name__ == "__main__":
    unittest.main()
