#!/usr/bin/env python3
"""Local verification runner for the Codex-native caveman integration."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Optional


ROOT = Path(__file__).resolve().parents[2]
HOOKS_DIR = ROOT / "hooks" / "caveman"
COMPRESS_SKILL_DIR = ROOT / ".agents" / "skills" / "caveman-compress"
FIXTURES_DIR = ROOT / "tests" / "caveman-compress"


class CheckFailure(RuntimeError):
    pass


def section(title: str) -> None:
    print(f"\n== {title} ==")


def ensure(condition: bool, message: str) -> None:
    if not condition:
        raise CheckFailure(message)


def run(
    args: list[str],
    *,
    cwd: Path = ROOT,
    env: Optional[dict[str, str]] = None,
    input_text: Optional[str] = None,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)
    result = subprocess.run(
        args,
        cwd=cwd,
        env=merged_env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise CheckFailure(
            f"Command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def load_compress_modules():
    sys.path.insert(0, str(COMPRESS_SKILL_DIR))
    import scripts.benchmark  # noqa: F401
    import scripts.cli as cli
    import scripts.compress as compress
    import scripts.detect as detect
    import scripts.validate as validate

    return cli, compress, detect, validate


def verify_repo_layout() -> None:
    section("Repo Layout")
    required_paths = [
        ROOT / ".agents" / "skills" / "caveman" / "SKILL.md",
        ROOT / ".agents" / "skills" / "caveman-commit" / "SKILL.md",
        ROOT / ".agents" / "skills" / "caveman-review" / "SKILL.md",
        ROOT / ".agents" / "skills" / "caveman-help" / "SKILL.md",
        ROOT / ".agents" / "skills" / "caveman-compress" / "SKILL.md",
        ROOT / ".codex" / "hooks.json",
        HOOKS_DIR / "caveman-activate.js",
        HOOKS_DIR / "caveman-mode-tracker.js",
        HOOKS_DIR / "caveman-config.js",
        HOOKS_DIR / "caveman-statusline.sh",
    ]
    for path in required_paths:
        ensure(path.exists(), f"Missing required caveman asset: {path}")
    print("Codex-native caveman assets present")


def verify_manifest_and_syntax() -> None:
    section("Manifest And Syntax")
    json.loads((ROOT / ".codex" / "hooks.json").read_text())
    node_bin = shutil.which("node")
    if node_bin:
        run(["node", "--check", str(HOOKS_DIR / "caveman-config.js")])
        run(["node", "--check", str(HOOKS_DIR / "caveman-activate.js")])
        run(["node", "--check", str(HOOKS_DIR / "caveman-mode-tracker.js")])
        print("Hooks JSON and JS syntax OK")
    else:
        print("[SKIP] node not found — JS syntax checks skipped (install Node.js to enable)")
    run(["bash", "-n", str(HOOKS_DIR / "caveman-statusline.sh")])
    print("Shell syntax OK")


def verify_compress_fixtures() -> None:
    section("Compress Fixtures")
    _, _, detect, validate = load_compress_modules()
    fixtures = sorted(FIXTURES_DIR.glob("*.original.md"))
    ensure(fixtures, "No caveman-compress fixtures found")
    for original in fixtures:
        compressed = original.with_name(original.name.replace(".original.md", ".md"))
        ensure(compressed.exists(), f"Missing compressed fixture for {original.name}")
        result = validate.validate(original, compressed)
        ensure(result.is_valid, f"Fixture validation failed for {compressed.name}: {result.errors}")
        ensure(detect.should_compress(compressed), f"Fixture should be compressible: {compressed.name}")
    print(f"Validated {len(fixtures)} caveman-compress fixture pairs")


def verify_compress_cli() -> None:
    section("Compress CLI")
    skip_target = ROOT / "hooks" / "caveman" / "caveman-activate.js"
    skip_result = run(
        ["python3", "-m", "scripts", str(skip_target)],
        cwd=COMPRESS_SKILL_DIR,
        check=False,
    )
    ensure(skip_result.returncode == 0, "compress CLI skip path should exit 0")
    ensure("Detected: code" in skip_result.stdout, "compress CLI skip path missing detection output")
    ensure("Skipping: file is not natural language" in skip_result.stdout, "compress CLI skip path missing skip output")

    missing_result = run(
        ["python3", "-m", "scripts", str(ROOT / "does-not-exist.md")],
        cwd=COMPRESS_SKILL_DIR,
        check=False,
    )
    ensure(missing_result.returncode == 1, "compress CLI missing-file path should exit 1")
    ensure("File not found" in missing_result.stdout, "compress CLI missing-file output mismatch")
    print("Compress CLI skip/error paths OK")


def verify_hook_flow() -> None:
    section("Hook Flow")
    if shutil.which("node") is None:
        print("[SKIP] node not found — hook flow checks skipped (install Node.js to enable)")
        return
    ensure(shutil.which("bash") is not None, "bash is required for hook verification")

    with tempfile.TemporaryDirectory(prefix="caveman-verify-") as temp_root:
        home = Path(temp_root)
        claude_dir = home / ".claude"
        claude_dir.mkdir(parents=True)
        (claude_dir / "settings.json").write_text(
            json.dumps({"statusLine": {"type": "command", "command": "bash /tmp/custom.sh"}}) + "\n"
        )

        activate = run(
            ["node", str(HOOKS_DIR / "caveman-activate.js")],
            env={"HOME": str(home), "USERPROFILE": str(home)},
        )
        ensure("CAVEMAN MODE ACTIVE. level: full" in activate.stdout, "activation output missing banner")
        ensure("STATUSLINE SETUP NEEDED" not in activate.stdout, "activation should stay quiet with custom statusline")
        ensure((claude_dir / ".caveman-active").read_text() == "full", "activation should write default flag")

        tracker = run(
            ["node", str(HOOKS_DIR / "caveman-mode-tracker.js")],
            env={"HOME": str(home), "USERPROFILE": str(home)},
            input_text=json.dumps({"prompt": "/caveman ultra"}),
        )
        ensure(tracker.stdout == "", "mode tracker should stay silent by default")
        ensure((claude_dir / ".caveman-active").read_text() == "ultra", "mode tracker should update active mode")

        run(
            ["node", str(HOOKS_DIR / "caveman-mode-tracker.js")],
            env={"HOME": str(home), "USERPROFILE": str(home)},
            input_text=json.dumps({"prompt": "normal mode"}),
        )
        ensure(not (claude_dir / ".caveman-active").exists(), "normal mode should clear caveman flag")
        print("Activation and mode tracking OK")


def main() -> int:
    verify_repo_layout()
    verify_manifest_and_syntax()
    verify_compress_fixtures()
    verify_compress_cli()
    verify_hook_flow()
    print("\nAll caveman checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
