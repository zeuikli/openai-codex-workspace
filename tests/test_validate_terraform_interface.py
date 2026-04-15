from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from scripts.validate_terraform_interface import validate_interface


class ValidateTerraformInterfaceTest(unittest.TestCase):
    def test_validate_interface_passes_for_current_repo(self) -> None:
        repo_root = Path(__file__).resolve().parents[1]
        errors = validate_interface(repo_root)
        self.assertEqual(errors, [])

    def test_detects_missing_environment_variable_declaration(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            self._write_fixture(root)

            dev_vars = root / 'terraform-optimized' / 'environments' / 'dev' / 'variables.tf'
            dev_vars.write_text('variable "project_id" { type = string }\n', encoding='utf-8')

            errors = validate_interface(root)
            self.assertTrue(
                any('environments/dev/variables.tf does not declare it' in err for err in errors),
                msg='Expected missing variable error not found.',
            )

    @staticmethod
    def _write_fixture(root: Path) -> None:
        platform = root / 'terraform-optimized' / 'modules' / 'platform_stack'
        platform.mkdir(parents=True, exist_ok=True)
        (platform / 'variables.tf').write_text(
            '\n'.join(
                [
                    'variable "project_id" { type = string }',
                    'variable "cloud_run_image" { type = string }',
                ]
            )
            + '\n',
            encoding='utf-8',
        )

        for env in ('dev', 'staging', 'prod'):
            env_dir = root / 'terraform-optimized' / 'environments' / env
            env_dir.mkdir(parents=True, exist_ok=True)
            (env_dir / 'main.tf').write_text(
                '\n'.join(
                    [
                        'module "platform" {',
                        '  source = "../../modules/platform_stack"',
                        '  project_id = var.project_id',
                        '  cloud_run_image = var.cloud_run_image',
                        '}',
                    ]
                )
                + '\n',
                encoding='utf-8',
            )
            (env_dir / 'variables.tf').write_text(
                '\n'.join(
                    [
                        'variable "project_id" { type = string }',
                        'variable "cloud_run_image" { type = string }',
                    ]
                )
                + '\n',
                encoding='utf-8',
            )


if __name__ == '__main__':
    unittest.main(verbosity=2)
