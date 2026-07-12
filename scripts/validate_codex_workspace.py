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
    'convergence_judge': 'read-only',
    'doc_writer': 'workspace-write',
    'fast_implementer': 'workspace-write',
    'implementer': 'workspace-write',
    'memory_compactor': 'workspace-write',
    'multi_mode_agent': 'workspace-write',
    'quick_code_reviewer': 'read-only',
    'researcher': 'read-only',
    'reviewer': 'read-only',
    'security_auditor': 'read-only',
    'security_reviewer': 'read-only',
    'senior_architect': 'read-only',
    'test_writer': 'workspace-write',
}

EXPECTED_ROUTES = {
    'cost_write': ('cost', 'fast_implementer'),
    'quality_write': ('quality', 'multi_mode_agent'),
    'quality_explore': ('quality', 'researcher'),
    'ceiling_review': ('ceiling', 'reviewer'),
    'frontier_security_review': ('frontier', 'security_auditor'),
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


def validate_calibration_runs(calibration: object) -> list[str]:
    if not isinstance(calibration, dict):
        return ['Calibration manifest must be a JSON object']
    requirements = calibration.get('requirements')
    runs = calibration.get('runs')
    if calibration.get('status') != 'complete' or not isinstance(runs, list) or not 5 <= len(runs) <= 10:
        return ['Stable migration requires a complete 5-10 task calibration manifest']
    if not isinstance(requirements, dict):
        return ['Calibration manifest requirements must be an object']

    required_arms = requirements.get('required_arms')
    required_metrics = requirements.get('metrics')
    required_fixtures = requirements.get('required_fixtures')
    if not all(isinstance(value, list) and value for value in (required_arms, required_metrics, required_fixtures)):
        return ['Calibration manifest run requirements are incomplete']

    errors: list[str] = []
    task_ids: set[str] = set()
    for index, run in enumerate(runs):
        prefix = f'Calibration runs[{index}]'
        if not isinstance(run, dict):
            errors.append(f'{prefix} must be an object')
            continue
        task_id = run.get('task_id')
        if not isinstance(task_id, str) or not task_id.strip():
            errors.append(f'{prefix} missing task_id')
        elif task_id in task_ids:
            errors.append(f'{prefix} duplicates task_id: {task_id}')
        else:
            task_ids.add(task_id)

        arms = run.get('arms')
        if not isinstance(arms, dict) or set(arms) != set(required_arms):
            errors.append(f'{prefix} arms must match required_arms')
        else:
            for arm_name in required_arms:
                arm = arms.get(arm_name)
                if not isinstance(arm, dict):
                    errors.append(f'{prefix} arm {arm_name} must be an object')
                    continue
                if not isinstance(arm.get('model'), str) or not isinstance(arm.get('reasoning_effort'), str):
                    errors.append(f'{prefix} arm {arm_name} missing model or reasoning_effort')
                metrics = arm.get('metrics')
                if not isinstance(metrics, dict) or set(metrics) != set(required_metrics):
                    errors.append(f'{prefix} arm {arm_name} metrics must match requirements')
                elif any(value is None for value in metrics.values()):
                    errors.append(f'{prefix} arm {arm_name} metrics must not contain null')

        fixtures = run.get('fixtures')
        if not isinstance(fixtures, dict) or set(fixtures) != set(required_fixtures):
            errors.append(f'{prefix} fixtures must match required_fixtures')
        else:
            for fixture_name in required_fixtures:
                fixture = fixtures.get(fixture_name)
                if (
                    not isinstance(fixture, dict)
                    or fixture.get('status') != 'passed'
                    or not isinstance(fixture.get('evidence'), str)
                    or not fixture['evidence'].strip()
                ):
                    errors.append(f'{prefix} fixture {fixture_name} requires passed status and evidence')

        if run.get('acceptance_decision') != 'promote':
            errors.append(f'{prefix} acceptance_decision must be promote')
        artifact_sha256 = run.get('artifact_sha256')
        if not isinstance(artifact_sha256, str) or re.fullmatch(r'[0-9a-f]{64}', artifact_sha256) is None:
            errors.append(f'{prefix} artifact_sha256 must be 64 lowercase hex characters')
    return errors


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
            for marker in (
                'benefit-gated',
                'delegation_benefit',
                'return_schema',
                'unverified_success',
                'profile_contract_id',
                'quality_explore',
                'ceiling_review',
                'frontier_security_review',
            ):
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
    agent_configs: dict[str, dict[str, object]] = {}
    for agent_file in sorted(expected_agent_files & actual_agent_files):
        name = agent_file.stem
        try:
            agent = tomllib.loads(agent_file.read_text(encoding='utf-8'))
        except (OSError, tomllib.TOMLDecodeError) as exc:
            errors.append(f'Invalid custom agent TOML {name}: {exc}')
            continue
        agent_configs[name] = agent
        sandbox = EXPECTED_AGENTS[name]
        for key, expected in (
            ('name', name),
            ('sandbox_mode', sandbox),
        ):
            if agent.get(key) != expected:
                errors.append(f'Custom agent {name} {key} must be {expected}')
        for key in ('model', 'model_reasoning_effort'):
            if not isinstance(agent.get(key), str) or not agent[key].strip():
                errors.append(f'Custom agent {name} missing key: {key}')
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
        for marker in ('multi-mode-skill/scripts/validate_task.py', 'ROUTE: quality_write', 'PROFILE_CONTRACT_ID:'):
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

    l4_sources = {
        root / 'the-loop-harness-v3' / 'PROFILES-v3.md': (
            'GPT-5.6 Routing',
            'gpt-5.6-luna',
            'gpt-5.6-terra',
            'gpt-5.6-sol',
        ),
        root / 'the-loop-harness-v3' / 'EVAL-PACK.md': (
            'unverified_success',
            'role_confusion',
            'unsafe_delete',
            'compact_resume',
        ),
        root / 'the-loop-harness-v3' / 'GPT-5.6-CALIBRATION.json': (
            'git:835c353',
            'compare_gpt56_at_prior_effort_and_one_lower',
            'representative_task_count',
        ),
    }
    for path, markers in l4_sources.items():
        if not path.exists():
            errors.append(f'Missing L4 harness source: {path.as_posix()}')
            continue
        text = path.read_text(encoding='utf-8')
        for marker in markers:
            if marker not in text:
                errors.append(f'L4 harness source {path.name} missing marker: {marker}')

    config_file = root / '.codex' / 'config.toml'
    config_runtime: dict[str, object] = {}
    if not config_file.exists():
        errors.append('Missing .codex/config.toml')
    else:
        config_text = config_file.read_text(encoding='utf-8')
        config = parse_simple_toml(config_text)
        try:
            config_runtime = tomllib.loads(config_text)
        except tomllib.TOMLDecodeError as exc:
            errors.append(f'Invalid .codex/config.toml: {exc}')
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
    profile_ref_text = ''
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
            elif set(mapping) != {'main_thread', *EXPECTED_AGENTS}:
                errors.append('.codex/profiles.json model_mapping must cover main_thread and every expected agent')
            elif isinstance(mapping, dict):
                for name in ('main_thread', *EXPECTED_AGENTS):
                    entry = mapping.get(name, {})
                    if not isinstance(entry, dict):
                        errors.append(f'.codex/profiles.json missing mapping: {name}')
                        continue
                    profile = entry.get('profile')
                    model = entry.get('model')
                    effort = entry.get('reasoning_effort')
                    expected_source = '.codex/config.toml' if name == 'main_thread' else f'.codex/agents/{name}.toml'
                    if profile not in expected_profiles:
                        errors.append(f'.codex/profiles.json invalid profile for {name}')
                    if entry.get('source') != expected_source:
                        errors.append(f'.codex/profiles.json invalid source for {name}')
                    if not isinstance(model, str) or not isinstance(effort, str):
                        errors.append(f'.codex/profiles.json missing model or effort for {name}')
                        continue
                    if name == 'main_thread':
                        if config_runtime.get('model') != model or config_runtime.get('model_reasoning_effort') != effort:
                            errors.append('.codex/profiles.json main_thread mapping mismatch with .codex/config.toml')
                    else:
                        agent = agent_configs.get(name, {})
                        if agent.get('model') != model or agent.get('model_reasoning_effort') != effort:
                            errors.append(f'.codex/profiles.json mapping mismatch with agent TOML for {name}')
                    label = 'main thread' if name == 'main_thread' else name
                    row = f'| {label} | {profile} | `{model}` | `{effort}` |'
                    if row not in profile_ref_text:
                        errors.append(f'.codex/refs/model-profiles.md mapping mismatch for {name}')

            delegation = profiles.get('delegation', {})
            routes = delegation.get('routes', {}) if isinstance(delegation, dict) else {}
            actual_routes = set(routes) if isinstance(routes, dict) else set()
            if actual_routes != set(EXPECTED_ROUTES):
                errors.append('.codex/profiles.json delegation routes must match the allowlist')
            elif isinstance(mapping, dict):
                for route_name, (profile, target_agent) in EXPECTED_ROUTES.items():
                    route = routes.get(route_name, {})
                    if route != {'profile': profile, 'target_agent': target_agent}:
                        errors.append(f'.codex/profiles.json invalid delegation route: {route_name}')
                        continue
                    target = mapping.get(target_agent, {})
                    if not isinstance(target, dict) or target.get('profile') != profile:
                        errors.append(f'.codex/profiles.json route profile mismatch: {route_name}')
            expected_verifiers = {
                'workspace_validation': ['python3', 'scripts/validate_codex_workspace.py'],
                'pytest': ['python3', '-m', 'pytest', 'tests/', '-q'],
                'diff_check': ['git', 'diff', '--check'],
            }
            verifiers = delegation.get('verifiers', {}) if isinstance(delegation, dict) else {}
            if verifiers != expected_verifiers:
                errors.append('.codex/profiles.json verifier catalog must match the safe allowlist')

            migration = profiles.get('migration', {})
            if not isinstance(migration, dict) or migration.get('status') not in {'provisional', 'stable', 'rolled_back'}:
                errors.append('.codex/profiles.json migration status must be provisional, stable, or rolled_back')
            elif any(not migration.get(key) for key in ('baseline', 'evidence_manifest', 'comparison_rule', 'owner', 'review_after', 'rollback_signal')):
                errors.append('.codex/profiles.json migration metadata is incomplete')
            else:
                manifest_value = migration['evidence_manifest']
                manifest_path = Path(manifest_value) if isinstance(manifest_value, str) else Path('/')
                if manifest_path.is_absolute() or '..' in manifest_path.parts:
                    errors.append('.codex/profiles.json evidence_manifest must be repo-relative')
                else:
                    calibration_file = root / manifest_path
                    if not calibration_file.exists():
                        errors.append(f'Missing calibration manifest: {manifest_value}')
                    else:
                        try:
                            calibration = json.loads(calibration_file.read_text(encoding='utf-8'))
                        except Exception as exc:
                            errors.append(f'Invalid calibration manifest: {exc}')
                            calibration = {}
                        requirements = calibration.get('requirements', {}) if isinstance(calibration, dict) else {}
                        runs = calibration.get('runs', []) if isinstance(calibration, dict) else []
                        if requirements.get('representative_task_count') != {'minimum': 5, 'maximum': 10}:
                            errors.append('Calibration manifest must require 5-10 representative tasks')
                        if requirements.get('compare_gpt56_at_prior_effort_and_one_lower') is not True:
                            errors.append('Calibration manifest must compare GPT-5.6 at prior effort and one lower')
                        if requirements.get('include_proposed_mapping') is not True:
                            errors.append('Calibration manifest must include the proposed mapping arm')
                        if migration.get('status') == 'stable':
                            errors.extend(validate_calibration_runs(calibration))

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
