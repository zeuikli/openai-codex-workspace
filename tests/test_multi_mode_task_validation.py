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
        'profile_contract': '比較替代方案並提供 rollback。',
        'goal': '驗證架構選擇。',
        'non_goals': ['不修改 production'],
        'allowed_paths': ['src/'],
        'verification': ['pytest -q'],
    }


def test_valid_task_envelope_passes() -> None:
    assert MODULE.validate_task(valid_task()) == []


def test_missing_profile_contract_fails_closed() -> None:
    task = valid_task()
    task.pop('profile_contract')
    assert 'profile_contract must be a non-empty string' in MODULE.validate_task(task)


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
