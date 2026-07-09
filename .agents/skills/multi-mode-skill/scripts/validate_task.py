#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


PROFILES = {'cost', 'quality', 'ceiling', 'frontier'}


def validate_task(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ['task envelope must be a JSON object']

    errors: list[str] = []
    if payload.get('profile') not in PROFILES:
        errors.append('profile must be cost, quality, ceiling, or frontier')

    for key in ('profile_contract', 'goal', 'context', 'return_schema', 'delegation_benefit'):
        value = payload.get(key)
        if not isinstance(value, str) or not value.strip():
            errors.append(f'{key} must be a non-empty string')

    for key in ('non_goals', 'allowed_paths', 'verification'):
        value = payload.get(key)
        if not isinstance(value, list) or not value:
            errors.append(f'{key} must be a non-empty array')
        elif any(not isinstance(item, str) or not item.strip() for item in value):
            errors.append(f'{key} entries must be non-empty strings')

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

    errors = validate_task(payload)
    result = {'valid': not errors, 'errors': errors}
    print(json.dumps(result, ensure_ascii=True, indent=2, sort_keys=True))
    return 0 if not errors else 2


if __name__ == '__main__':
    raise SystemExit(main())
