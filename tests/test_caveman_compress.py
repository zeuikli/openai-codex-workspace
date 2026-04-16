from __future__ import annotations

import importlib.util
import tempfile
import unittest
from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SKILL_DIR = ROOT / ".agents" / "skills" / "caveman-compress"


def _load_skill_package():
    """Load caveman-compress/scripts/ as a package to support relative imports."""
    pkg_name = "caveman_compress_scripts"
    if pkg_name in sys.modules:
        pkg = sys.modules[pkg_name]
        return pkg.compress, pkg.detect, pkg.validate

    import types

    # Create the package namespace
    pkg = types.ModuleType(pkg_name)
    pkg.__path__ = [str(SKILL_DIR / "scripts")]
    pkg.__package__ = pkg_name
    sys.modules[pkg_name] = pkg

    def _load(name: str):
        key = f"{pkg_name}.{name}"
        spec = importlib.util.spec_from_file_location(
            key, SKILL_DIR / "scripts" / f"{name}.py",
            submodule_search_locations=[]
        )
        mod = importlib.util.module_from_spec(spec)
        mod.__package__ = pkg_name
        sys.modules[key] = mod
        spec.loader.exec_module(mod)
        return mod

    detect   = _load("detect")
    compress = _load("compress")
    validate = _load("validate")
    return compress, detect, validate


compress, detect, validate = _load_skill_package()


class CavemanCompressTests(unittest.TestCase):
    def test_detect_identifies_markdown_and_skips_code(self) -> None:
        with tempfile.TemporaryDirectory(prefix="caveman-detect-") as tmp:
            root = Path(tmp)
            note = root / "notes.md"
            script = root / "script.py"
            note.write_text("# Notes\nUse this file for prose.\n", encoding="utf-8")
            script.write_text("print('hi')\n", encoding="utf-8")

            self.assertEqual(detect.detect_file_type(note), "natural_language")
            self.assertTrue(detect.should_compress(note))
            self.assertEqual(detect.detect_file_type(script), "code")
            self.assertFalse(detect.should_compress(script))

    def test_validate_preserves_headings_urls_and_code_blocks(self) -> None:
        with tempfile.TemporaryDirectory(prefix="caveman-validate-") as tmp:
            root = Path(tmp)
            original = root / "orig.md"
            compressed = root / "comp.md"
            text = (
                "# Title\n\n"
                "- Read `README.md`\n"
                "- Visit https://developers.openai.com/codex/learn/best-practices\n\n"
                "```bash\npytest -q\n```\n"
            )
            original.write_text(text, encoding="utf-8")
            compressed.write_text(text.replace("Visit", "Keep"), encoding="utf-8")

            result = validate.validate(original, compressed)
            self.assertTrue(result.is_valid)
            self.assertEqual(result.errors, [])

    def test_sensitive_path_detection_blocks_credentials(self) -> None:
        self.assertTrue(compress.is_sensitive_path(Path("/tmp/credentials.md")))
        self.assertTrue(compress.is_sensitive_path(Path("/home/me/.ssh/id_rsa")))
        self.assertFalse(compress.is_sensitive_path(Path("/tmp/project-notes.md")))

    def test_strip_llm_wrapper_removes_outer_markdown_fence_only(self) -> None:
        wrapped = "```markdown\n# Title\n\nBody\n```"
        plain = "# Title\n\nBody"
        self.assertEqual(compress.strip_llm_wrapper(wrapped), plain)
        self.assertEqual(compress.strip_llm_wrapper(plain), plain)

    def test_build_prompts_preserve_fixing_contract(self) -> None:
        compress_prompt = compress.build_compress_prompt("# Notes\nKeep `code`\n")
        self.assertIn("Do NOT modify anything inside ``` code blocks", compress_prompt)
        self.assertIn("Return ONLY the compressed markdown body", compress_prompt)

        fix_prompt = compress.build_fix_prompt(
            "# Title\n",
            "# Title\n",
            ["URL mismatch: lost={'https://example.com'}, added=set()"],
        )
        self.assertIn("DO NOT recompress or rephrase the file", fix_prompt)
        self.assertIn("ONLY fix the listed errors", fix_prompt)


if __name__ == "__main__":
    unittest.main()
