#!/usr/bin/env python3
"""Run Codex Cloud-compatible workspace load checks and capture a report."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT_DIR = ROOT / "benchmarks" / "results"

CHECKS = [
    ["python3", "tests/caveman/verify_repo.py"],
    ["python3", "-m", "unittest", "-v", "tests/caveman/test_hooks"],
]


def run_check(cmd: list[str]) -> dict:
    proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)
    return {
        "command": " ".join(cmd),
        "args": cmd,
        "returncode": proc.returncode,
        "stdout_tail": "\n".join(proc.stdout.strip().splitlines()[-20:]),
        "stderr_tail": "\n".join(proc.stderr.strip().splitlines()[-20:]),
    }


def main() -> None:
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    report_path = REPORT_DIR / f"codex_cloud_load_test_{ts}.json"
    report_md_path = REPORT_DIR / f"codex_cloud_load_test_{ts}.md"

    results = [run_check(cmd) for cmd in CHECKS]
    status = "pass" if all(r["returncode"] == 0 for r in results) else "fail"

    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "checks": results,
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    md_lines = [
        "# Codex Cloud Load Test",
        "",
        f"Generated at: `{payload['generated_at']}`",
        "",
        f"Overall status: **{status.upper()}**",
        "",
        "| Command | Return code |",
        "|---|---:|",
    ]
    for item in results:
        md_lines.append(f"| `{item['command']}` | {item['returncode']} |")
    md_lines += ["", "## Output tails", ""]
    for item in results:
        md_lines += [
            f"### `{item['command']}`",
            "",
            "**stdout (tail):**",
            "```text",
            item["stdout_tail"] or "(empty)",
            "```",
            "",
            "**stderr (tail):**",
            "```text",
            item["stderr_tail"] or "(empty)",
            "```",
            "",
        ]
    report_md_path.write_text("\n".join(md_lines))

    print(f"status={status}")
    print(f"report={report_path}")
    print(f"report_md={report_md_path}")
    for item in results:
        print(f"- {item['command']} => rc={item['returncode']}")
    if status != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
