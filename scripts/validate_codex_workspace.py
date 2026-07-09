#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import subprocess
import tomllib
from pathlib import Path


EXPECTED_SKILLS = {
    'chatgpt-balanced-pilot',
    'chatgpt-deep-pilot',
    'chatgpt-fast-pilot',
    'chatgpt-frontier-pilot',
    'multi-mode-skill',
}

EXPECTED_AGENTS = {
    'convergence_judge': ('gpt-5.4-mini', 'low', 'read-only'),
    'doc_writer': ('gpt-5.4-mini', 'low', 'workspace-write'),
    'fast_implementer': ('gpt-5.4-mini', 'low', 'workspace-write'),
    'implementer': ('gpt-5.4', 'medium', 'workspace-write'),
    'memory_compactor': ('gpt-5.4-mini', 'medium', 'workspace-write'),
    'multi_mode_agent': ('gpt-5.4', 'medium', 'workspace-write'),
    'quick_code_reviewer': ('gpt-5.4-mini', 'medium', 'read-only'),
    'researcher': ('gpt-5.4-mini', 'medium', 'read-only'),
    'reviewer': ('gpt-5.5', 'high', 'read-only'),
    'security_auditor': ('gpt-5.5', 'high', 'read-only'),
    'security_reviewer': ('gpt-5.4', 'high', 'read-only'),
    'senior_architect': ('gpt-5.5', 'high', 'read-only'),
    'test_writer': ('gpt-5.4', 'medium', 'workspace-write'),
}

CLAUDE_RUNTIME_TERMS = (
    '.claude/',
    'TodoWrite',
    'CronCreate',
    'ScheduleWakeup',
    'permissionMode:',
    'isolation: worktree',
    'Agent(',
    '/rewind',
    'claude-',
)


def is_gitignored(path: Path, root: Path) -> bool:
    result = subprocess.run(
        ['git', 'check-ignore', '-q', str(path)],
        cwd=root,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def parse_simple_toml(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current: dict[str, object] | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue
        section = re.match(r'^\[([^\]]+)\]$', line)
        if section:
            current = data
            for part in section.group(1).split('.'):
                value = current.get(part)
                if not isinstance(value, dict):
                    value = {}
                    current[part] = value
                current = value
            continue
        key = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.+)$', line)
        if key:
            (current if current is not None else data)[key.group(1)] = key.group(2).strip()
    return data


def validate_workspace(root: Path) -> list[str]:
    errors: list[str] = []

    bilingual_docs = {
        'README.md': (
            '## 繁體中文',
            '## English',
            'The Loop Harness v3',
            '五個 repo-scoped skills',
            'five repo-scoped skills',
            '十三個 project-scoped custom agents',
            'thirteen project-scoped custom agents',
            '.codex/profiles.json',
            'scripts/validate_task.py',
            'MIT License',
        ),
        'Memory.md': (
            '## 繁體中文',
            '## English',
            'benefit-gated',
            'contract-driven delegation',
            '待辦與殘餘風險',
            'Remaining Actions and Risks',
        ),
    }
    for filename, markers in bilingual_docs.items():
        path = root / filename
        if not path.exists():
            errors.append(f'Missing {filename}')
            continue
        text = path.read_text(encoding='utf-8')
        for marker in markers:
            if marker not in text:
                errors.append(f'{filename} missing bilingual contract marker: {marker}')

    license_file = root / 'LICENSE'
    if not license_file.exists():
        errors.append('Missing LICENSE')
    else:
        license_text = license_file.read_text(encoding='utf-8')
        for marker in ('MIT License', 'Copyright (c) 2026 Zeuik Li', 'Permission is hereby granted'):
            if marker not in license_text:
                errors.append(f'LICENSE missing MIT marker: {marker}')

    agents_file = root / 'AGENTS.md'
    if not agents_file.exists():
        errors.append('Missing AGENTS.md')
    else:
        agents_text = agents_file.read_text(encoding='utf-8')
        for marker in (
            '## 上下文與 Compact',
            '## Subagent 與 Multi-Mode',
            '五個 `.agents/skills/` 與十三個 `.codex/agents/*.toml`',
            'benefit-gated',
            'Worker 回報是證據，不是完成判定',
            '.codex/profiles.json',
            '跨 session 的架構決策、驗證基線與殘餘風險記入 `Memory.md`',
        ):
            if marker not in agents_text:
                errors.append(f'AGENTS.md missing Codex rule marker: {marker}')
        for forbidden in ('CLAUDE.md', 'TodoWrite', 'Haiku', 'Sonnet', 'Opus', '$gate-vote'):
            if forbidden in agents_text:
                errors.append(f'AGENTS.md contains removed or Claude-only term: {forbidden}')

    forbidden_paths = [
        root / '.claude',
        root / 'CLAUDE.md',
        root / 'docs',
        root / 'benchmarks',
        root / 'AGENTS.full.md',
        root / 'agents',
        root / 'multi-mode-agent.md',
        root / 'references',
        root / 'fable-pilot',
        root / 'haiku-pilot',
        root / 'opus-pilot',
        root / 'sonnet-pilot',
        root / 'autoresearch',
        root / 'gate-vote',
        root / 'media-research',
        root / 'media-transcribe',
        root / 'overnight-research',
        root / 'quality-pipeline',
        root / 'research-hub',
        root / 'review-hub',
    ]
    for path in forbidden_paths:
        if path.exists():
            errors.append(f'Forbidden workspace artifact exists: {path.as_posix()}')

    skills_root = root / '.agents' / 'skills'
    expected_skill_dirs = {skills_root / slug for slug in EXPECTED_SKILLS}
    actual_skill_dirs = {path for path in skills_root.iterdir() if path.is_dir()} if skills_root.exists() else set()
    for path in sorted(expected_skill_dirs - actual_skill_dirs):
        errors.append(f'Missing required skill directory: {path.as_posix()}')
    for path in sorted(actual_skill_dirs - expected_skill_dirs):
        errors.append(f'Unexpected skill directory: {path.as_posix()}')

    if skills_root.exists():
        for path in sorted(skills_root.rglob('*')):
            if (path.name in {'.DS_Store', '__pycache__'} or path.suffix == '.pyc') and not is_gitignored(path, root):
                errors.append(f'Unignored skill packaging junk exists: {path.as_posix()}')

    expected_skill_files = {path / 'SKILL.md' for path in expected_skill_dirs}
    actual_skill_files = set(skills_root.glob('*/SKILL.md')) if skills_root.exists() else set()
    for path in sorted(expected_skill_files - actual_skill_files):
        errors.append(f'Missing required skill: {path.as_posix()}')
    for path in sorted(actual_skill_files - expected_skill_files):
        errors.append(f'Unexpected skill: {path.as_posix()}')
    for skill_file in sorted(expected_skill_files & actual_skill_files):
        slug = skill_file.parent.name
        skill_text = skill_file.read_text(encoding='utf-8')
        frontmatter = re.match(r'^---\n(.*?)\n---\n', skill_text, re.DOTALL)
        if not frontmatter:
            errors.append(f'Skill has invalid frontmatter: {skill_file.as_posix()}')
        else:
            fields = {
                line.split(':', 1)[0].strip(): line.split(':', 1)[1].strip()
                for line in frontmatter.group(1).splitlines()
                if ':' in line
            }
            if set(fields) != {'name', 'description'}:
                errors.append(f'Skill frontmatter must contain only name and description: {slug}')
            if fields.get('name') != slug:
                errors.append(f'Skill name must match directory: {slug}')
            if not fields.get('description'):
                errors.append(f'Skill description is empty: {slug}')

        metadata_file = skill_file.parent / 'agents' / 'openai.yaml'
        if not metadata_file.exists():
            errors.append(f'Skill missing agents/openai.yaml: {slug}')
        else:
            metadata = metadata_file.read_text(encoding='utf-8')
            for marker in ('display_name:', 'short_description:', 'default_prompt:'):
                if marker not in metadata:
                    errors.append(f'Skill metadata missing {marker} {slug}')
            if f'${slug}' not in metadata:
                errors.append(f'Skill default prompt must mention ${slug}')

        for forbidden in CLAUDE_RUNTIME_TERMS:
            if forbidden in skill_text:
                errors.append(f'Skill contains Claude-only runtime term {forbidden}: {slug}')

        references_dir = skill_file.parent / 'references'
        if references_dir.exists() and any(references_dir.iterdir()):
            errors.append(f'Retained skill must not contain unexpected references: {slug}')

        if slug == 'multi-mode-skill':
            task_validator = skill_file.parent / 'scripts' / 'validate_task.py'
            if 'scripts/validate_task.py' not in skill_text:
                errors.append('Multi-mode skill must invoke scripts/validate_task.py')
            for marker in ('benefit-gated', 'delegation_benefit', 'return_schema', 'unverified_success'):
                if marker not in skill_text:
                    errors.append(f'Multi-mode skill missing v3 marker: {marker}')
            if not task_validator.exists():
                errors.append('Multi-mode skill missing scripts/validate_task.py')
            elif not os.access(task_validator, os.X_OK):
                errors.append('Multi-mode task validator is not executable')

    agents_dir = root / '.codex' / 'agents'
    expected_agent_files = {agents_dir / f'{name}.toml' for name in EXPECTED_AGENTS}
    actual_agent_files = set(agents_dir.glob('*.toml')) if agents_dir.exists() else set()
    for path in sorted(expected_agent_files - actual_agent_files):
        errors.append(f'Missing required custom agent: {path.as_posix()}')
    for path in sorted(actual_agent_files - expected_agent_files):
        errors.append(f'Unexpected custom agent: {path.as_posix()}')
    for agent_file in sorted(expected_agent_files & actual_agent_files):
        name = agent_file.stem
        try:
            agent = tomllib.loads(agent_file.read_text(encoding='utf-8'))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f'Invalid custom agent TOML {name}: {exc}')
            continue
        model, effort, sandbox = EXPECTED_AGENTS[name]
        for key, expected in (
            ('name', name),
            ('model', model),
            ('model_reasoning_effort', effort),
            ('sandbox_mode', sandbox),
        ):
            if agent.get(key) != expected:
                errors.append(f'Custom agent {name} {key} must be {expected}')
        for key in ('description', 'developer_instructions'):
            if not isinstance(agent.get(key), str) or not agent[key].strip():
                errors.append(f'Custom agent {name} missing key: {key}')
        agent_text = agent_file.read_text(encoding='utf-8')
        for forbidden in CLAUDE_RUNTIME_TERMS:
            if forbidden in agent_text:
                errors.append(f'Custom agent {name} contains Claude-only runtime term: {forbidden}')

    multi_mode_agent = agents_dir / 'multi_mode_agent.toml'
    if multi_mode_agent.exists():
        text = multi_mode_agent.read_text(encoding='utf-8')
        for marker in ('multi-mode-skill/scripts/validate_task.py', 'PROFILE: <name>', 'PROFILE_CONTRACT:'):
            if marker not in text:
                errors.append(f'Custom agent missing contract marker: {marker}')

    loop_file = root / 'HARNESS-THE-LOOP.md'
    if not loop_file.exists():
        errors.append('Missing HARNESS-THE-LOOP.md')
    else:
        loop_text = loop_file.read_text(encoding='utf-8')
        for phase in ('OBSERVE', 'IDENTIFY', 'PROPOSE', 'APPLY', 'TEST', 'RECORD'):
            if f'## {phase}' not in loop_text:
                errors.append(f'Harness The Loop missing phase: {phase}')

    config_file = root / '.codex' / 'config.toml'
    if not config_file.exists():
        errors.append('Missing .codex/config.toml')
    else:
        config = parse_simple_toml(config_file.read_text(encoding='utf-8'))
        for key in ('model', 'model_reasoning_effort', 'approval_policy', 'sandbox_mode'):
            if key not in config:
                errors.append(f'Missing config key: {key}')
        agents = config.get('agents', {})
        if not isinstance(agents, dict):
            errors.append('Missing [agents] configuration')
        else:
            if agents.get('max_threads') != '4':
                errors.append('agents.max_threads must be 4')
            if agents.get('max_depth') != '1':
                errors.append('agents.max_depth must be 1')
            mapped_agents = {key for key, value in agents.items() if isinstance(value, dict)}
            if mapped_agents != set(EXPECTED_AGENTS):
                errors.append('Configured custom agent mappings must exactly match the allowlist')
            for name in EXPECTED_AGENTS:
                worker = agents.get(name, {})
                expected_path = f'"./agents/{name}.toml"'
                if not isinstance(worker, dict) or worker.get('config_file') != expected_path:
                    errors.append(f'Missing agents.{name} config mapping')
        features = config.get('features', {})
        if not isinstance(features, dict) or 'hooks' not in features:
            errors.append('Missing canonical features.hooks in .codex/config.toml')
        if isinstance(features, dict) and 'multi_agent' in features:
            errors.append('features.multi_agent must remain absent')

    profiles_file = root / '.codex' / 'profiles.json'
    profiles_ref = root / '.codex' / 'refs' / 'model-profiles.md'
    if not profiles_ref.exists():
        errors.append('Missing .codex/refs/model-profiles.md')
    else:
        profile_ref_text = profiles_ref.read_text(encoding='utf-8')
        for marker in ('Model Profiles v3', 'wired SSoT', 'the-loop-harness-v3/EVAL-PACK.md'):
            if marker not in profile_ref_text:
                errors.append(f'.codex/refs/model-profiles.md missing marker: {marker}')
    if not profiles_file.exists():
        errors.append('Missing .codex/profiles.json')
    else:
        try:
            profiles = json.loads(profiles_file.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'Invalid .codex/profiles.json: {exc}')
            profiles = {}
        expected_profiles = {'cost', 'quality', 'ceiling', 'frontier'}
        actual_profiles = set(profiles.get('profiles', {})) if isinstance(profiles, dict) else set()
        if actual_profiles != expected_profiles:
            errors.append('.codex/profiles.json profiles must be cost, quality, ceiling, frontier')
        if isinstance(profiles, dict):
            fixtures = profiles.get('eval_pack', {}).get('fixtures', []) if isinstance(profiles.get('eval_pack'), dict) else []
            for fixture in ('unverified_success', 'role_confusion', 'unsafe_delete', 'eval_hack', 'compact_resume'):
                if fixture not in fixtures:
                    errors.append(f'.codex/profiles.json missing eval fixture: {fixture}')
            mapping = profiles.get('model_mapping', {})
            if not isinstance(mapping, dict) or 'main_thread' not in mapping or 'multi_mode_agent' not in mapping:
                errors.append('.codex/profiles.json missing model mapping anchors')

    hooks_file = root / '.codex' / 'hooks.json'
    if not hooks_file.exists():
        errors.append('Missing .codex/hooks.json')
        hooks: dict[str, object] = {}
    else:
        try:
            payload = json.loads(hooks_file.read_text(encoding='utf-8'))
            hooks = payload.get('hooks', {}) if isinstance(payload, dict) else {}
        except Exception as exc:
            errors.append(f'Invalid .codex/hooks.json: {exc}')
            hooks = {}

    expected_matchers = {
        'PreToolUse': {'Bash'},
        'PostToolUse': {'Edit|Write'},
        'PreCompact': {'manual|auto'},
        'PostCompact': {'manual|auto'},
    }
    for event, expected in expected_matchers.items():
        groups = hooks.get(event, []) if isinstance(hooks, dict) else []
        actual = {group.get('matcher') for group in groups if isinstance(group, dict)}
        for matcher in sorted(expected - actual):
            errors.append(f'Missing {event} matcher: {matcher}')

    for removed_event in ('SessionStart', 'UserPromptSubmit', 'SubagentStart', 'SubagentStop'):
        if isinstance(hooks, dict) and removed_event in hooks:
            errors.append(f'Removed event must stay absent: {removed_event}')

    for name in ('pre_tool_use_guard.sh', 'post_tool_use_validate.sh', 'context_checkpoint.sh'):
        script = root / '.codex' / 'hooks' / name
        if not script.exists():
            errors.append(f'Missing hook script: {script.as_posix()}')
        elif not os.access(script, os.X_OK):
            errors.append(f'Hook script is not executable: {script.as_posix()}')

    return errors


def main() -> int:
    errors = validate_workspace(Path('.'))
    if errors:
        print('Codex workspace validation failed:')
        for error in errors:
            print(f'- {error}')
        return 1
    print('Codex workspace validation passed (five skills, thirteen agents).')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
