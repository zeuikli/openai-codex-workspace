from __future__ import annotations

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


SCRIPT = (
    Path(__file__).resolve().parents[1]
    / '.agents'
    / 'skills'
    / 'multi-mode-skill'
    / 'scripts'
    / 'validate_task.py'
)
SPEC = spec_from_file_location('multi_mode_task_validation', SCRIPT)
assert SPEC and SPEC.loader
MODULE = module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def valid_task() -> dict[str, object]:
    return {
        'profile': 'ceiling',
        'route': 'ceiling_review',
        'profile_contract_id': 'the-loop-harness-v3:ceiling:v1',
        'goal': '驗證架構選擇。',
        'context': '讀取架構 ADR 與目前 diff。',
        'constraints': ['保持唯讀'],
        'done_when': '回報有 file:line 的 findings。',
        'return_schema': 'scope, changes, evidence, open_questions, deviations, residual_risk',
        'delegation_benefit': '對抗審查',
        'non_goals': ['不修改 production'],
        'allowed_paths': ['src/'],
        'verification': ['pytest'],
    }


def test_valid_task_envelope_passes() -> None:
    assert MODULE.validate_task(valid_task()) == []


def test_missing_profile_contract_id_fails_closed() -> None:
    task = valid_task()
    task.pop('profile_contract_id')
    assert 'profile_contract_id must be a non-empty string' in MODULE.validate_task(task)


def test_missing_v3_handoff_fields_fail_closed() -> None:
    task = valid_task()
    task.pop('context')
    task.pop('return_schema')
    task.pop('delegation_benefit')
    errors = MODULE.validate_task(task)
    assert 'context must be a non-empty string' in errors
    assert 'return_schema must be a non-empty string' in errors
    assert 'delegation_benefit must be a non-empty string' in errors


def test_invalid_profile_is_rejected() -> None:
    task = valid_task()
    task['profile'] = 'unknown'
    assert MODULE.validate_task(task)[0] == 'profile must be cost, quality, ceiling, or frontier'


def test_empty_paths_and_verification_are_rejected() -> None:
    task = valid_task()
    task['allowed_paths'] = []
    task['verification'] = []
    errors = MODULE.validate_task(task)
    assert 'allowed_paths must be a non-empty array' in errors
    assert 'verification must be a non-empty array' in errors


def test_route_resolves_model_without_caller_selected_privilege() -> None:
    task = valid_task()
    resolved = MODULE.resolve_task(task, MODULE.load_profiles())
    assert resolved == {
        'route': 'ceiling_review',
        'profile': 'ceiling',
        'profile_contract_id': 'the-loop-harness-v3:ceiling:v1',
        'profile_contract': MODULE.load_profiles()['profiles']['ceiling'],
        'target_agent': 'reviewer',
        'model': 'gpt-5.6-sol',
        'reasoning_effort': 'medium',
        'source': '.codex/agents/reviewer.toml',
        'goal': '驗證架構選擇。',
        'non_goals': ['不修改 production'],
        'allowed_paths': ['src/'],
        'context': '讀取架構 ADR 與目前 diff。',
        'constraints': ['保持唯讀'],
        'done_when': '回報有 file:line 的 findings。',
        'return_schema': 'scope, changes, evidence, open_questions, deviations, residual_risk',
        'delegation_benefit': '對抗審查',
        'verification': [
            {'id': 'pytest', 'argv': ['python3', '-m', 'pytest', 'tests/', '-q']},
        ],
    }
    task['target_agent'] = 'security_auditor'
    assert 'target_agent is resolved by the validated route and must not be supplied' in MODULE.validate_task(task)


def test_route_profile_and_contract_must_match() -> None:
    task = valid_task()
    task['profile'] = 'frontier'
    task['profile_contract_id'] = 'the-loop-harness-v3:frontier:v1'
    errors = MODULE.validate_task(task)
    assert 'profile must match route profile: ceiling' in errors
    assert 'profile_contract_id must match route contract: the-loop-harness-v3:ceiling:v1' in errors


def test_paths_must_stay_scoped_to_repository() -> None:
    for path in ('/tmp', '../secrets', '.', 'src/*.py', 'src;rm'):
        task = valid_task()
        task['allowed_paths'] = [path]
        assert any('allowed path' in error for error in MODULE.validate_task(task)), path


def test_verification_uses_catalog_ids() -> None:
    task = valid_task()
    task['verification'] = ['rm -rf src']
    assert 'unknown verification ID: rm -rf src' in MODULE.validate_task(task)


def test_write_route_requires_exact_change_and_blocks_control_paths() -> None:
    task = valid_task()
    task.update(
        route='cost_write',
        profile='cost',
        profile_contract_id='the-loop-harness-v3:cost:v1',
        allowed_paths=['src/'],
    )
    assert 'exact_change must be a non-empty string for write routes' in MODULE.validate_task(task)
    task['exact_change'] = 'Rename one local symbol without behavior change.'
    assert MODULE.validate_task(task) == []
    for path in ('.codex/profiles.json', 'Memory.md', '.env.local', 'secrets/token.txt', 'certs/client.pem'):
        task['allowed_paths'] = [path]
        assert any('write route cannot target' in error for error in MODULE.validate_task(task)), path


def test_malformed_profiles_fail_closed() -> None:
    errors = MODULE.validate_task(valid_task(), {'delegation': []})
    assert 'route must resolve to an allowlisted agent mapping' in errors
