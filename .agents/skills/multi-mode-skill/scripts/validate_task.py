#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any


PROFILES = {'cost', 'quality', 'ceiling', 'frontier'}
ROOT = Path(__file__).resolve().parents[4]
PROFILES_FILE = ROOT / '.codex' / 'profiles.json'
PATH_META_RE = re.compile(r'[\\*?{}\[\]$`;&|<>\x00-\x1f]')
WRITE_ROUTES = {'cost_write', 'quality_write'}
PROTECTED_ROOTS = {
    '.agents', '.aws', '.azure', '.config', '.git', '.kube', '.ssh',
    '.codex', 'the-loop-harness-v3',
}
PROTECTED_FILES = {'AGENTS.md', 'HARNESS-THE-LOOP.md', 'Memory.md'}
SECRET_SUFFIXES = {'.key', '.pem', '.p12', '.pfx', '.crt', '.cer'}
SECRET_FILES = {
    '.netrc', '.npmrc', '.pypirc', 'auth.json', 'credentials.json',
    'id_ed25519', 'id_rsa', 'service-account.json', 'token.json',
}
SECRET_NAME_RE = re.compile(r'(^|[-_.])(credential|password|private[-_]?key|secret|token)([-_.]|$)', re.I)


def load_profiles() -> dict[str, Any]:
    return json.loads(PROFILES_FILE.read_text(encoding='utf-8'))


def resolve_task(payload: dict[str, Any], profiles: dict[str, Any]) -> dict[str, Any] | None:
    delegation = profiles.get('delegation')
    mapping = profiles.get('model_mapping')
    profile_defs = profiles.get('profiles')
    if not isinstance(delegation, dict) or not isinstance(mapping, dict) or not isinstance(profile_defs, dict):
        return None
    routes = delegation.get('routes')
    verifier_catalog = delegation.get('verifiers')
    if not isinstance(routes, dict) or not isinstance(verifier_catalog, dict):
        return None
    route = routes.get(payload.get('route'))
    if not isinstance(route, dict):
        return None
    target = mapping.get(route.get('target_agent'))
    contract = profile_defs.get(route.get('profile'))
    if not isinstance(target, dict) or not isinstance(contract, dict):
        return None
    verification = payload.get('verification', [])
    resolved = {
        'route': payload.get('route'),
        'profile': route.get('profile'),
        'profile_contract_id': contract.get('contract_id'),
        'profile_contract': contract,
        'target_agent': route.get('target_agent'),
        'model': target.get('model'),
        'reasoning_effort': target.get('reasoning_effort'),
        'source': target.get('source'),
        'goal': payload.get('goal'),
        'non_goals': payload.get('non_goals'),
        'allowed_paths': payload.get('allowed_paths'),
        'context': payload.get('context'),
        'constraints': payload.get('constraints'),
        'done_when': payload.get('done_when'),
        'return_schema': payload.get('return_schema'),
        'delegation_benefit': payload.get('delegation_benefit'),
        'verification': [
            {'id': verifier, 'argv': verifier_catalog.get(verifier)}
            for verifier in verification
            if isinstance(verifier, str)
        ],
    }
    if payload.get('route') in WRITE_ROUTES:
        resolved['exact_change'] = payload.get('exact_change')
    return resolved


def validate_allowed_path(raw_path: str, route: str | None) -> str | None:
    if PATH_META_RE.search(raw_path):
        return f'allowed path contains forbidden metacharacter or control byte: {raw_path}'
    path = PurePosixPath(raw_path)
    if path.is_absolute() or raw_path in {'', '.'} or '..' in path.parts:
        return f'allowed path must be a scoped repo-relative path: {raw_path}'
    try:
        (ROOT / path).resolve(strict=False).relative_to(ROOT.resolve())
    except ValueError:
        return f'allowed path escapes repository root: {raw_path}'
    if route in WRITE_ROUTES:
        first = path.parts[0]
        basename = path.name
        lowered_parts = {part.lower() for part in path.parts}
        if first in PROTECTED_ROOTS or basename in PROTECTED_FILES:
            return f'write route cannot target protected control path: {raw_path}'
        if any(part.startswith('.env') for part in path.parts):
            return f'write route cannot target secret path: {raw_path}'
        if (
            basename.lower() in SECRET_FILES
            or path.suffix.lower() in SECRET_SUFFIXES
            or lowered_parts & {'credentials', 'secrets', 'private-keys'}
            or SECRET_NAME_RE.search(basename)
        ):
            return f'write route cannot target secret path: {raw_path}'
    return None


def validate_task(payload: Any, profiles: dict[str, Any] | None = None) -> list[str]:
    if not isinstance(payload, dict):
        return ['task envelope must be a JSON object']

    profiles = profiles or load_profiles()
    errors: list[str] = []
    if payload.get('profile') not in PROFILES:
        errors.append('profile must be cost, quality, ceiling, or frontier')

    for key in (
        'route',
        'profile_contract_id',
        'goal',
        'context',
        'done_when',
        'return_schema',
        'delegation_benefit',
    ):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{key} must be a non-empty string')

    for key in ('target_agent', 'model', 'reasoning_effort', 'profile_contract'):
        if key in payload:
            errors.append(f'{key} is resolved by the validated route and must not be supplied')

    for key in ('non_goals', 'allowed_paths', 'constraints'):
        value = payload.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f'{key} must be a non-empty array')
        elif any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f'{key} entries must be non-empty strings')

    paths = payload.get('allowed_paths')
    if isinstance(paths, list):
        for raw_path in paths:
            if isinstance(raw_path, str) and raw_path.strip():
                error = validate_allowed_path(raw_path, payload.get('route'))
                if error:
                    errors.append(error)

    if payload.get('route') in WRITE_ROUTES:
        exact_change = payload.get('exact_change')
        if not isinstance(exact_change, str) or not exact_change.strip():
            errors.append('exact_change must be a non-empty string for write routes')

    verifiers = payload.get('verification')
    delegation = profiles.get('delegation')
    verifier_catalog = delegation.get('verifiers', {}) if isinstance(delegation, dict) else {}
    if not isinstance(verifiers, list) or not verifiers:
        errors.append('verification must be a non-empty array')
    elif any(not isinstance(item, str) or not item.strip() for item in verifiers):
        errors.append('verification entries must be non-empty verifier IDs')
    elif isinstance(verifier_catalog, dict):
        for verifier in verifiers:
            if verifier not in verifier_catalog:
                errors.append(f'unknown verification ID: {verifier}')

    resolved = resolve_task(payload, profiles)
    if resolved is None:
        errors.append('route must resolve to an allowlisted agent mapping')
    else:
        if payload.get('profile') != resolved['profile']:
            errors.append(f"profile must match route profile: {resolved['profile']}")
        if payload.get('profile_contract_id') != resolved['profile_contract_id']:
            errors.append(
                f"profile_contract_id must match route contract: {resolved['profile_contract_id']}"
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description='Validate a multi-mode task envelope.')
    parser.add_argument('task_file', type=Path)
    args = parser.parse_args()

    try:
        payload = json.loads(args.task_file.read_text(encoding='utf-8'))
    except Exception as exc:
        result = {'valid': False, 'errors': [f'invalid task JSON: {exc}']}
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
        return 2

    try:
        profiles = load_profiles()
    except Exception as exc:
        result = {'valid': False, 'errors': [f'invalid routing profiles: {exc}']}
        print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
        return 2

    errors = validate_task(payload, profiles)
    result = {'valid': not errors, 'errors': errors}
    if not errors:
        result['resolved'] = resolve_task(payload, profiles)
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
