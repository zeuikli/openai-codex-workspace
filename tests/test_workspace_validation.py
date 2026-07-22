import hashlib
import json
import shutil
from pathlib import Path

from scripts.validate_codex_workspace import (
    EXPECTED_AGENTS,
    EXPECTED_HARNESS_EVALS,
    EXPECTED_SKILLS,
    validate_calibration_runs,
    validate_workspace,
)


ROOT = Path(__file__).resolve().parents[1]


def test_current_workspace_is_valid() -> None:
    assert validate_workspace(ROOT) == []


def test_validator_rejects_incomplete_bilingual_docs(tmp_path: Path) -> None:
    (tmp_path / 'README.md').write_text('## 繁體中文\n', encoding='utf-8')
    (tmp_path / 'Memory.md').write_text('## English\n', encoding='utf-8')
    errors = validate_workspace(tmp_path)
    assert any('README.md missing bilingual contract marker: ## English' in error for error in errors)
    assert any('Memory.md missing bilingual contract marker: ## 繁體中文' in error for error in errors)


def test_only_expected_codex_skills_exist() -> None:
    skills = {path.name for path in (ROOT / '.agents' / 'skills').iterdir() if path.is_dir()}
    assert skills == EXPECTED_SKILLS


def test_each_skill_has_codex_ui_metadata() -> None:
    for slug in EXPECTED_SKILLS:
        metadata = (ROOT / '.agents' / 'skills' / slug / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
        assert f'${slug}' in metadata


def test_only_expected_custom_agents_exist() -> None:
    agents = {path.stem for path in (ROOT / '.codex' / 'agents').glob('*.toml')}
    assert agents == set(EXPECTED_AGENTS)


def test_custom_agents_are_mapped_and_use_expected_models_and_sandboxes() -> None:
    config = (ROOT / '.codex' / 'config.toml').read_text(encoding='utf-8')
    profiles = json.loads((ROOT / '.codex' / 'profiles.json').read_text(encoding='utf-8'))
    for name, sandbox in EXPECTED_AGENTS.items():
        mapping = profiles['model_mapping'][name]
        text = (ROOT / '.codex' / 'agents' / f'{name}.toml').read_text(encoding='utf-8')
        assert f'name = "{name}"' in text
        assert f'model = "{mapping["model"]}"' in text
        assert f'model_reasoning_effort = "{mapping["reasoning_effort"]}"' in text
        assert f'sandbox_mode = "{sandbox}"' in text
        assert 'developer_instructions = """' in text
        assert f'[agents.{name}]' in config
        assert f'config_file = "./agents/{name}.toml"' in config


def test_staging_sources_are_absent() -> None:
    for slug in EXPECTED_SKILLS:
        assert not (ROOT / slug).exists()
    assert not (ROOT / 'multi-mode-agent.md').exists()
    assert not (ROOT / 'agents').exists()


def test_docs_and_benchmarks_are_absent() -> None:
    assert not (ROOT / 'docs').exists()
    assert not (ROOT / 'benchmarks').exists()


def test_harness_the_loop_is_complete() -> None:
    text = (ROOT / 'HARNESS-THE-LOOP.md').read_text(encoding='utf-8')
    for phase in ('OBSERVE', 'IDENTIFY', 'PROPOSE', 'APPLY', 'TEST', 'RECORD'):
        assert f'## {phase}' in text


def test_v4_l4_sources_are_present() -> None:
    core = (ROOT / 'the-loop-harness-v4' / 'HARNESS-CORE-v4.md').read_text(encoding='utf-8')
    profiles = (ROOT / 'the-loop-harness-v4' / 'PROFILES-v4.md').read_text(encoding='utf-8')
    eval_pack = (ROOT / 'the-loop-harness-v4' / 'EVAL-PACK-v4.md').read_text(encoding='utf-8')
    addendum = (ROOT / 'the-loop-harness-v4' / 'EVAL-PACK-v4-ADDENDUM.md').read_text(encoding='utf-8')
    for marker in ('Agent = Model + Body + Harness', '[P]', '[E]', 'G-LoopA'):
        assert marker in core
    for marker in ('PROFILES v4.0', 'gpt-5.6-luna', 'gpt-5.6-terra', 'gpt-5.6-sol'):
        assert marker in profiles
    for marker in ('unverified_success', 'role_confusion', 'unsafe_delete', 'compact_resume'):
        assert marker in eval_pack
    for marker in ('F11', 'F15', 'F22', 'F10R'):
        assert marker in addendum


def test_claude_rules_are_mapped_to_codex_project_instructions() -> None:
    text = (ROOT / 'AGENTS.md').read_text(encoding='utf-8')
    assert '## 上下文與 Compact' in text
    assert '## Subagent 與 Multi-Mode' in text
    assert 'Worker 回報是證據，不是完成判定' in text
    assert 'benefit-gated' in text
    assert '.codex/profiles.json' in text
    for removed in ('CLAUDE.md', 'TodoWrite', 'Haiku', 'Sonnet', 'Opus', '$gate-vote'):
        assert removed not in text


def test_validator_rejects_unexpected_skill(tmp_path: Path) -> None:
    extra = tmp_path / '.agents' / 'skills' / 'extra'
    extra.mkdir(parents=True)
    (extra / 'SKILL.md').write_text('---\nname: extra\n---\n', encoding='utf-8')
    errors = validate_workspace(tmp_path)
    assert any('Unexpected skill' in error for error in errors)


def test_validator_rejects_empty_unexpected_skill_directory(tmp_path: Path) -> None:
    (tmp_path / '.agents' / 'skills' / 'stale-skill').mkdir(parents=True)
    errors = validate_workspace(tmp_path)
    assert any('Unexpected skill directory' in error for error in errors)


def test_validator_rejects_skill_packaging_junk(tmp_path: Path) -> None:
    junk = tmp_path / '.agents' / 'skills' / 'multi-mode-skill' / '.DS_Store'
    junk.parent.mkdir(parents=True)
    junk.write_bytes(b'junk')
    errors = validate_workspace(tmp_path)
    assert any('skill packaging junk' in error for error in errors)


def test_macos_metadata_is_gitignored() -> None:
    assert '.DS_Store' in (ROOT / '.gitignore').read_text(encoding='utf-8').splitlines()


def test_validator_rejects_unexpected_custom_agent(tmp_path: Path) -> None:
    agents = tmp_path / '.codex' / 'agents'
    agents.mkdir(parents=True)
    (agents / 'extra.toml').write_text('name = "extra"\n', encoding='utf-8')
    errors = validate_workspace(tmp_path)
    assert any('Unexpected custom agent' in error for error in errors)


def test_model_routing_is_gpt_56_luna_main_and_worker() -> None:
    config = (ROOT / '.codex' / 'config.toml').read_text(encoding='utf-8')
    agent = (ROOT / '.codex' / 'agents' / 'multi_mode_agent.toml').read_text(encoding='utf-8')
    assert 'model = "gpt-5.6-luna"' in config
    assert 'model_reasoning_effort = "xhigh"' in config
    assert 'model = "gpt-5.6-luna"' in agent
    assert 'model_reasoning_effort = "xhigh"' in agent
    assert '[agents.multi_mode_agent]' in config


def test_v4_profiles_are_available() -> None:
    profiles = (ROOT / '.codex' / 'profiles.json').read_text(encoding='utf-8')
    profile_ref = (ROOT / '.codex' / 'refs' / 'model-profiles.md').read_text(encoding='utf-8')
    assert '"schema_version": "the-loop-harness-v4.codex-profiles.1"' in profiles
    assert '"unverified_success"' in profiles
    assert 'Model Profiles v4' in profile_ref
    assert 'the-loop-harness-v4/EVAL-PACK-v4.md' in profile_ref
    for name in ('convergence_judge', 'doc_writer', 'security_reviewer', 'test_writer'):
        assert f'"{name}"' in profiles


def copy_workspace(tmp_path: Path) -> Path:
    target = tmp_path / 'workspace'
    shutil.copytree(ROOT, target, ignore=shutil.ignore_patterns('.git', '.pytest_cache', '__pycache__'))
    return target


def test_validator_rejects_main_thread_mapping_drift(tmp_path: Path) -> None:
    target = copy_workspace(tmp_path)
    config = target / '.codex' / 'config.toml'
    config.write_text(
        config.read_text(encoding='utf-8').replace('model = "gpt-5.6-luna"', 'model = "gpt-5.6-sol"', 1),
        encoding='utf-8',
    )
    errors = validate_workspace(target)
    assert '.codex/profiles.json main_thread mapping mismatch with .codex/config.toml' in errors


def test_validator_rejects_route_and_human_mapping_drift(tmp_path: Path) -> None:
    target = copy_workspace(tmp_path)
    profiles_file = target / '.codex' / 'profiles.json'
    profiles = json.loads(profiles_file.read_text(encoding='utf-8'))
    profiles['delegation']['routes']['quality_explore']['target_agent'] = 'multi_mode_agent'
    profiles_file.write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    profile_ref = target / '.codex' / 'refs' / 'model-profiles.md'
    profile_ref.write_text(
        profile_ref.read_text(encoding='utf-8').replace('| researcher | quality |', '| researcher | ceiling |'),
        encoding='utf-8',
    )
    errors = validate_workspace(target)
    assert '.codex/profiles.json invalid delegation route: quality_explore' in errors
    assert '.codex/refs/model-profiles.md mapping mismatch for researcher' in errors


def test_validator_rejects_stable_migration_without_calibration(tmp_path: Path) -> None:
    target = copy_workspace(tmp_path)
    profiles_file = target / '.codex' / 'profiles.json'
    profiles = json.loads(profiles_file.read_text(encoding='utf-8'))
    profiles['migration']['status'] = 'stable'
    profiles_file.write_text(json.dumps(profiles, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    errors = validate_workspace(target)
    assert 'Stable migration requires a complete 5-10 task calibration manifest' in errors


def test_calibration_rejects_empty_completed_runs() -> None:
    calibration = json.loads(
        (ROOT / 'the-loop-harness-v4' / 'GPT-5.6-CALIBRATION-v4.json').read_text(encoding='utf-8')
    )
    calibration['status'] = 'complete'
    calibration['runs'] = [{} for _ in range(5)]
    profiles = json.loads((ROOT / '.codex' / 'profiles.json').read_text(encoding='utf-8'))
    errors = validate_calibration_runs(calibration, profiles['model_mapping'], ROOT)
    assert 'Calibration runs[0] missing task_id' in errors
    assert 'Calibration runs[0] arms must match required_arms' in errors
    assert 'Calibration runs[0] fixtures must match required_fixtures' in errors
    assert 'Calibration runs[0] artifact_sha256 must be 64 lowercase hex characters' in errors


def test_calibration_requirements_cannot_self_authorize_fake_evidence() -> None:
    calibration = {
        'status': 'complete',
        'requirements': {
            'required_arms': ['fake'],
            'metrics': ['fake'],
            'required_fixtures': ['fake'],
        },
        'runs': [{} for _ in range(5)],
    }
    errors = validate_calibration_runs(calibration, {}, ROOT)
    assert errors == ['Calibration required_arms must match the pinned validator contract']


def test_calibration_accepts_pinned_target_mapping_and_artifact(tmp_path: Path) -> None:
    calibration = json.loads(
        (ROOT / 'the-loop-harness-v4' / 'GPT-5.6-CALIBRATION-v4.json').read_text(encoding='utf-8')
    )
    profiles = json.loads((ROOT / '.codex' / 'profiles.json').read_text(encoding='utf-8'))
    artifact = tmp_path / 'evidence.json'
    artifact.write_text('{"verified":true}', encoding='utf-8')
    metrics = {
        'criteria_passed': ['done_when'],
        'fail_axes': [],
        'fail_category': '',
        'verification_exit_code': 0,
        'elapsed_seconds': 1.0,
        'provider_reported_usage_or_unavailable': 'unavailable',
        'provider_reported_cost_or_unavailable': 'unavailable',
        'retries': 0,
        'escalations': 0,
        'diff_lines': 1,
        'residual_risk': [],
    }
    fixtures = {
        name: {'status': 'passed', 'evidence': 'artifact:evidence.json'}
        for name in EXPECTED_HARNESS_EVALS
    }
    arms = {
        'baseline': {'model': 'gpt-5.5', 'reasoning_effort': 'medium', 'metrics': metrics},
        'gpt56_prior_effort': {'model': 'gpt-5.6-luna', 'reasoning_effort': 'medium', 'metrics': metrics},
        'gpt56_one_lower': {'model': 'gpt-5.6-luna', 'reasoning_effort': 'low', 'metrics': metrics},
        'proposed_mapping': {'model': 'gpt-5.6-luna', 'reasoning_effort': 'xhigh', 'metrics': metrics},
    }
    digest = hashlib.sha256(artifact.read_bytes()).hexdigest()
    calibration['status'] = 'complete'
    calibration['runs'] = [
        {
            'task_id': f'task-{index}',
            'target': 'main_thread',
            'arms': arms,
            'fixtures': fixtures,
            'acceptance_decision': 'promote',
            'artifact_path': 'evidence.json',
            'artifact_sha256': digest,
        }
        for index in range(5)
    ]
    assert validate_calibration_runs(calibration, profiles['model_mapping'], tmp_path) == []


def test_validator_requires_v4_profile_fields(tmp_path: Path) -> None:
    target = copy_workspace(tmp_path)
    profiles_file = target / '.codex' / 'profiles.json'
    profiles = json.loads(profiles_file.read_text(encoding='utf-8'))
    profiles['profiles']['quality'].pop('guidance_density')
    profiles['profiles']['quality'].pop('diff_soft_limit_lines')
    profiles_file.write_text(json.dumps(profiles), encoding='utf-8')
    errors = validate_workspace(target)
    assert 'Profile quality must declare v4 guidance density' in errors
    assert 'Profile quality must declare a v4 diff scope' in errors


def test_skills_do_not_contain_claude_runtime_syntax() -> None:
    forbidden = ('.claude/', 'TodoWrite', 'CronCreate', 'ScheduleWakeup', 'Agent(', '/rewind', 'claude-')
    for slug in EXPECTED_SKILLS:
        text = (ROOT / '.agents' / 'skills' / slug / 'SKILL.md').read_text(encoding='utf-8')
        for term in forbidden:
            assert term not in text


def test_mit_license_is_present() -> None:
    text = (ROOT / 'LICENSE').read_text(encoding='utf-8')
    assert text.startswith('MIT License\n')
    assert 'Copyright (c) 2026 Zeuik Li' in text
