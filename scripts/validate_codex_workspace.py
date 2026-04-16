#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
from pathlib import Path


def parse_simple_toml(text: str) -> dict[str, object]:
    data: dict[str, object] = {}
    current: dict[str, object] | None = None

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith('#'):
            continue

        section_match = re.match(r'^\[([^\]]+)\]$', line)
        if section_match:
            path = section_match.group(1).split('.')
            current = data
            for part in path:
                next_value = current.get(part)
                if not isinstance(next_value, dict):
                    next_value = {}
                    current[part] = next_value
                current = next_value
            continue

        key_match = re.match(r'^([A-Za-z0-9_]+)\s*=\s*(.+)$', line)
        if key_match:
            target = current if current is not None else data
            target[key_match.group(1)] = key_match.group(2).strip()

    return data


def _is_gitignored(path: Path, root: Path) -> bool:
    """Return True if `path` is ignored by git (not tracked and covered by .gitignore)."""
    import subprocess as _sp
    result = _sp.run(
        ['git', 'check-ignore', '-q', str(path)],
        cwd=root,
        capture_output=True,
    )
    return result.returncode == 0


def validate_workspace(root: Path) -> list[str]:
    errors: list[str] = []

    forbidden = [
        root / '.claude',
        root / 'CLAUDE.md',
        root / 'plugins',
        root / '.agents' / 'plugins',
    ]
    for path in forbidden:
        if path.exists() and not _is_gitignored(path, root):
            errors.append(f'Forbidden non-Codex artifact still exists: {path.as_posix()}')

    required_skills = [
        'multi-agent-collaboration',
        'deep-review',
        'frontend-design',
        'docs-drift-check',
        'session-handoff',
        'agent-team',
        'blog-analyzer',
        'cost-tracker',
        'karpathy-loop',
    ]
    for slug in required_skills:
        skill_file = root / '.agents' / 'skills' / slug / 'SKILL.md'
        if not skill_file.exists():
            errors.append(f'Missing skill file: {skill_file.as_posix()}')
            continue
        content = skill_file.read_text(encoding='utf-8')
        if 'Use when' not in content:
            errors.append(f'Skill missing "Use when" boundary: {skill_file.as_posix()}')
        if 'Do not use when' not in content:
            errors.append(f'Skill missing "Do not use when" boundary: {skill_file.as_posix()}')

        if not content.startswith('---'):
            errors.append(f'Skill missing frontmatter delimiter: {skill_file.as_posix()}')
            continue
        fm_end = content.find('\n---', 3)
        if fm_end == -1:
            errors.append(f'Skill frontmatter not closed: {skill_file.as_posix()}')
            continue
        frontmatter = content[3:fm_end]
        for key in ('name:', 'description:'):
            if key not in frontmatter:
                errors.append(f'Skill frontmatter missing "{key}" in {skill_file.as_posix()}')
        for line in frontmatter.splitlines():
            if line.strip().startswith('name:'):
                declared = line.split(':', 1)[1].strip()
                if declared != slug:
                    errors.append(
                        f'Skill name "{declared}" does not match folder slug "{slug}" in {skill_file.as_posix()}'
                    )
                break

    required_agents = [
        'architecture_explorer.toml',
        'docs_researcher.toml',
        'implementer.toml',
        'reviewer.toml',
        'security_reviewer.toml',
        'test_writer.toml',
    ]
    for filename in required_agents:
        agent_file = root / '.codex' / 'agents' / filename
        if not agent_file.exists():
            errors.append(f'Missing custom agent: {agent_file.as_posix()}')
            continue
        try:
            data = parse_simple_toml(agent_file.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'Invalid TOML ({agent_file.as_posix()}): {exc}')
            continue
        for key in ['name', 'description', 'developer_instructions', 'model']:
            if key not in data:
                errors.append(f'Agent missing required field "{key}": {agent_file.as_posix()}')

    config_file = root / '.codex' / 'config.toml'
    if not config_file.exists():
        errors.append('Missing .codex/config.toml')
    else:
        try:
            config = parse_simple_toml(config_file.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'Invalid TOML (.codex/config.toml): {exc}')
            config = {}

        if 'agents' not in config:
            errors.append('Missing [agents] in .codex/config.toml')

        feature_flags = config.get('features', {})
        if 'codex_hooks' not in feature_flags:
            errors.append('Missing features.codex_hooks in .codex/config.toml')
        if 'web_search' not in config:
            errors.append('Missing top-level web_search in .codex/config.toml')
        if 'model_reasoning_effort' not in config:
            errors.append('Missing top-level model_reasoning_effort in .codex/config.toml')

        for role in [
            'architecture_explorer',
            'docs_researcher',
            'implementer',
            'reviewer',
            'security_reviewer',
            'test_writer',
        ]:
            section = config.get('agents', {}).get(role)
            if not isinstance(section, dict):
                errors.append(f'Missing [agents.{role}] mapping in .codex/config.toml')
                continue
            if 'config_file' not in section:
                errors.append(f'Missing config_file in [agents.{role}]')

    hooks_json_file = root / '.codex' / 'hooks.json'
    if not hooks_json_file.exists():
        errors.append('Missing .codex/hooks.json')
    else:
        try:
            hooks_data = json.loads(hooks_json_file.read_text(encoding='utf-8'))
        except Exception as exc:
            errors.append(f'Invalid JSON (.codex/hooks.json): {exc}')
            hooks_data = {}

        hooks = hooks_data.get('hooks', {}) if isinstance(hooks_data, dict) else {}
        for event in ['PreToolUse', 'PostToolUse']:
            groups = hooks.get(event, [])
            if not groups:
                errors.append(f'Missing hook event: {event}')
                continue
            for group in groups:
                matcher = group.get('matcher')
                if matcher != 'Bash':
                    errors.append(f'{event} matcher must be "Bash" for current Codex runtime')

    required_hook_scripts = [
        root / '.codex' / 'hooks' / 'session_start_note.sh',
        root / '.codex' / 'hooks' / 'pre_tool_use_guard.sh',
        root / '.codex' / 'hooks' / 'post_tool_use_note.sh',
    ]
    for script in required_hook_scripts:
        if not script.exists():
            errors.append(f'Missing hook script: {script.as_posix()}')
            continue
        if not os.access(script, os.X_OK):
            errors.append(f'Hook script is not executable: {script.as_posix()}')

    caveman_compress_dir = root / '.agents' / 'skills' / 'caveman-compress'
    if caveman_compress_dir.exists():
        required_compress_files = [
            caveman_compress_dir / 'SKILL.md',
            caveman_compress_dir / 'scripts' / 'cli.py',
            caveman_compress_dir / 'scripts' / 'compress.py',
            caveman_compress_dir / 'scripts' / 'detect.py',
            caveman_compress_dir / 'scripts' / 'validate.py',
        ]
        for file_path in required_compress_files:
            if not file_path.exists():
                errors.append(f'Missing caveman-compress asset: {file_path.as_posix()}')

    migration_guide = root / 'docs' / 'codex-migration-guide.md'
    if not migration_guide.exists():
        errors.append('Missing docs/codex-migration-guide.md')
    else:
        content = migration_guide.read_text(encoding='utf-8')
        for marker in [
            'developers.openai.com/codex/guides/agents-md',
            'developers.openai.com/codex/learn/best-practices',
            'developers.openai.com/codex/subagents',
            'developers.openai.com/codex/hooks',
            'developers.openai.com/codex/config-reference#configtoml',
        ]:
            if marker not in content:
                errors.append(f'Migration guide missing official source: {marker}')

    return errors


def main() -> int:
    errors = validate_workspace(Path('.'))
    if errors:
        print('Codex workspace validation failed:')
        for err in errors:
            print(f'- {err}')
        return 1
    print('Codex workspace validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
