#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
from pathlib import Path

VARIABLE_PATTERN = re.compile(r'variable\s+"([^"]+)"')
ASSIGNMENT_PATTERN = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*=\s*var\.([a-zA-Z0-9_]+)\s*$', re.MULTILINE)
ENVIRONMENTS = ('dev', 'staging', 'prod')


def extract_declared_variables(path: Path) -> set[str]:
    return set(VARIABLE_PATTERN.findall(path.read_text(encoding='utf-8')))


def extract_module_var_assignments(path: Path) -> list[tuple[str, str]]:
    content = path.read_text(encoding='utf-8')
    return ASSIGNMENT_PATTERN.findall(content)


def validate_interface(root: Path) -> list[str]:
    errors: list[str] = []
    platform_vars_file = root / 'terraform-optimized' / 'modules' / 'platform_stack' / 'variables.tf'
    platform_vars = extract_declared_variables(platform_vars_file)

    env_assignments: dict[str, set[tuple[str, str]]] = {}

    for env in ENVIRONMENTS:
        env_dir = root / 'terraform-optimized' / 'environments' / env
        main_tf = env_dir / 'main.tf'
        env_vars_tf = env_dir / 'variables.tf'

        assignments = set(extract_module_var_assignments(main_tf))
        env_assignments[env] = assignments
        declared_env_vars = extract_declared_variables(env_vars_tf)

        for module_arg, source_var in sorted(assignments):
            if module_arg not in platform_vars:
                errors.append(
                    f'[{env}] main.tf passes "{module_arg}" but platform_stack/variables.tf does not declare it.'
                )
            if source_var not in declared_env_vars:
                errors.append(
                    f'[{env}] main.tf reads var.{source_var} but environments/{env}/variables.tf does not declare it.'
                )

    baseline_env = ENVIRONMENTS[0]
    baseline_assignments = env_assignments[baseline_env]
    for env in ENVIRONMENTS[1:]:
        missing = baseline_assignments - env_assignments[env]
        extra = env_assignments[env] - baseline_assignments
        for module_arg, source_var in sorted(missing):
            errors.append(
                f'[{env}] main.tf is missing assignment {module_arg} = var.{source_var} found in {baseline_env}.'
            )
        for module_arg, source_var in sorted(extra):
            errors.append(
                f'[{env}] main.tf has extra assignment {module_arg} = var.{source_var} not found in {baseline_env}.'
            )

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(
        description='Validate interface alignment between platform_stack and environment wrappers.'
    )
    parser.add_argument('--root', type=Path, default=Path('.'), help='Repository root path.')
    args = parser.parse_args()

    errors = validate_interface(args.root)
    if errors:
        print('Terraform interface validation failed:')
        for err in errors:
            print(f'- {err}')
        return 1

    print('Terraform interface validation passed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
