from pathlib import Path

from scripts.validate_codex_workspace import EXPECTED_AGENTS, EXPECTED_SKILLS, validate_workspace


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
    for name, (model, effort, sandbox) in EXPECTED_AGENTS.items():
        text = (ROOT / '.codex' / 'agents' / f'{name}.toml').read_text(encoding='utf-8')
        assert f'name = "{name}"' in text
        assert f'model = "{model}"' in text
        assert f'model_reasoning_effort = "{effort}"' in text
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


def test_v3_l4_sources_are_present() -> None:
    profiles = (ROOT / 'the-loop-harness-v3' / 'PROFILES-v3.md').read_text(encoding='utf-8')
    eval_pack = (ROOT / 'the-loop-harness-v3' / 'EVAL-PACK.md').read_text(encoding='utf-8')
    for marker in ('GPT-5.6 Routing', 'gpt-5.6-luna', 'gpt-5.6-terra', 'gpt-5.6-sol'):
        assert marker in profiles
    for marker in ('unverified_success', 'role_confusion', 'unsafe_delete', 'compact_resume'):
        assert marker in eval_pack


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


def test_v3_profiles_are_available() -> None:
    profiles = (ROOT / '.codex' / 'profiles.json').read_text(encoding='utf-8')
    profile_ref = (ROOT / '.codex' / 'refs' / 'model-profiles.md').read_text(encoding='utf-8')
    assert '"schema_version": "the-loop-harness-v3.codex-profiles.1"' in profiles
    assert '"unverified_success"' in profiles
    assert 'Model Profiles v3' in profile_ref
    assert 'the-loop-harness-v3/EVAL-PACK.md' in profile_ref
    for name in ('convergence_judge', 'doc_writer', 'security_reviewer', 'test_writer'):
        assert f'"{name}"' in profiles


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
