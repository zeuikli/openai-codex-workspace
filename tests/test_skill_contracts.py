from __future__ import annotations

import re
from pathlib import Path

from scripts.validate_codex_workspace import EXPECTED_SKILLS


ROOT = Path(__file__).resolve().parents[1]
SKILLS_ROOT = ROOT / '.agents' / 'skills'
CJK_RE = re.compile(r'[\u3400-\u4dbf\u4e00-\u9fff]')

REQUIRED_MARKERS = {
    'chatgpt-fast-pilot': (
        'gpt-5.6-luna',
        '`medium` reasoning',
        '`cost`',
        'git diff --check',
        '使用者未明確要求 agent 或平行工作時不委派',
    ),
    'chatgpt-balanced-pilot': (
        'gpt-5.6-luna',
        '`xhigh` reasoning',
        '`quality`',
        'Choice | Rejected | Reason',
        'Review Gate',
    ),
    'chatgpt-deep-pilot': (
        'gpt-5.6-sol',
        '`medium` reasoning',
        'Control',
        'rollback',
        'multi_mode_agent',
    ),
    'chatgpt-frontier-pilot': (
        'gpt-5.6-sol',
        '`high` reasoning',
        'baseline',
        '兩種獨立方法驗證',
        'rejected-claims ledger',
        'scope drift',
    ),
    'multi-mode-skill': (
        'multi_mode_agent',
        '使用者未明確要求 agent、委派或平行工作時不 spawn',
        'benefit-gated',
        '`cost`',
        '`quality`',
        '`ceiling`',
        '`frontier`',
        'PROFILE_CONTRACT_ID',
        'quality_explore',
        'ceiling_review',
        'frontier_security_review',
        'delegation_benefit',
        'return_schema',
        'scripts/validate_task.py',
        '直接 agent invocation 不屬於此 route contract',
        '主 thread 重跑關鍵驗證',
    ),
}

GOTCHA_MARKERS = {
    'chatgpt-balanced-pilot': ('scope', '安全與相容性限制'),
    'chatgpt-deep-pilot': ('rollback', '主 thread'),
    'chatgpt-fast-pilot': ('不用擴大 scope', 'git diff --check'),
    'chatgpt-frontier-pilot': ('scope drift', 'rejected-claims ledger'),
    'multi-mode-skill': ('benefit-gated', '主 thread 重跑關鍵驗證'),
}


def read_skill(slug: str) -> str:
    return (SKILLS_ROOT / slug / 'SKILL.md').read_text(encoding='utf-8')


def frontmatter_description(text: str) -> str:
    match = re.match(r'^---\n(.*?)\n---\n', text, re.DOTALL)
    assert match
    return next(
        line.split(':', 1)[1].strip()
        for line in match.group(1).splitlines()
        if line.startswith('description:')
    )


def metadata_value(text: str, key: str) -> str:
    match = re.search(rf'^\s*{re.escape(key)}:\s*"(.*)"\s*$', text, re.MULTILINE)
    assert match
    return match.group(1)


def test_every_skill_uses_taiwan_traditional_chinese_presentation() -> None:
    simplified_only = ('软件', '文件夹', '默认', '信息', '链接', '视频', '用户')
    for slug in EXPECTED_SKILLS:
        text = read_skill(slug)
        description = frontmatter_description(text)
        body = text.split('\n---\n', 1)[1]
        assert len(CJK_RE.findall(description)) >= 12, slug
        assert len(CJK_RE.findall(body)) >= 30, slug
        for term in simplified_only:
            assert term not in text, (slug, term)


def test_every_skill_preserves_its_execution_contract() -> None:
    assert set(REQUIRED_MARKERS) == EXPECTED_SKILLS
    for slug, markers in REQUIRED_MARKERS.items():
        text = read_skill(slug)
        for marker in markers:
            assert marker in text, (slug, marker)


def test_every_skill_has_localized_ui_metadata() -> None:
    for slug in EXPECTED_SKILLS:
        metadata = (SKILLS_ROOT / slug / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
        display_name = metadata_value(metadata, 'display_name')
        short_description = metadata_value(metadata, 'short_description')
        default_prompt = metadata_value(metadata, 'default_prompt')
        assert CJK_RE.search(display_name), slug
        assert 25 <= len(short_description) <= 64, slug
        assert len(CJK_RE.findall(short_description)) >= 12, slug
        assert f'${slug}' in default_prompt
        assert len(CJK_RE.findall(default_prompt)) >= 8, slug
        assert len(default_prompt) <= 128, slug


def test_multi_mode_cannot_trigger_implicitly() -> None:
    metadata = (SKILLS_ROOT / 'multi-mode-skill' / 'agents' / 'openai.yaml').read_text(encoding='utf-8')
    assert 'allow_implicit_invocation: false' in metadata


def test_retained_gotcha_defenses_are_present() -> None:
    assert set(GOTCHA_MARKERS) == EXPECTED_SKILLS
    for slug, markers in GOTCHA_MARKERS.items():
        text = read_skill(slug)
        for marker in markers:
            assert marker in text, (slug, marker)


def test_multi_mode_task_validator_is_executable() -> None:
    script = SKILLS_ROOT / 'multi-mode-skill' / 'scripts' / 'validate_task.py'
    assert script.is_file()
    assert script.stat().st_mode & 0o111


def test_multi_mode_agent_contract_and_language() -> None:
    agent = (ROOT / '.codex' / 'agents' / 'multi_mode_agent.toml').read_text(encoding='utf-8')
    config = (ROOT / '.codex' / 'config.toml').read_text(encoding='utf-8')
    for marker in (
        'name = "multi_mode_agent"',
        'model = "gpt-5.6-luna"',
        'model_reasoning_effort = "xhigh"',
        'multi-mode-skill/scripts/validate_task.py',
        'ROUTE: quality_write',
        'PROFILE_CONTRACT_ID:',
        'Contract isolation 是 hard gate',
        '中文任務使用台灣繁體中文；英文任務使用英文',
        '不 spawn agents',
        '不得為取得 pass 而弱化測試',
    ):
        assert marker in agent, marker
    assert '[agents.multi_mode_agent]' in config
    assert 'config_file = "./agents/multi_mode_agent.toml"' in config
