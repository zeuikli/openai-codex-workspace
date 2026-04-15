# Codex Compliance Report

Generated: 2026-04-14 (Asia/Taipei)
Target: 本 repo 根目錄（使用者或 Agent 依實際 clone 路徑自行解析）

## Scope Checked

- AGENTS.md
- Skills
- Subagents
- Automations (repo-level readiness)
- Hooks
- Models / Config

## Result Summary

- Overall status: **Aligned with requested Codex structure**
- Blocking issues: **None**
- Notes:
  - Automations are created and managed in Codex app UI; repo can only provide prompts/skills/readiness artifacts.
  - Hooks are experimental in official docs; this workspace enables them explicitly.

## Checklist

1. AGENTS.md
- `AGENTS.md` exists at repo root.
- Content is project-instruction style and suitable for Codex instruction discovery.

2. Skills
- Repo skills exist under `.agents/skills/*/SKILL.md`.
- Each skill has `name` and `description` frontmatter keys (frontmatter + slug match enforced in CI).
- `karpathy-loop` skill ships the Success-Criteria Loop referenced by `docs/karpathy-codex-principles.md`.

3. Subagents
- Custom agent files exist under `.codex/agents/*.toml`.
- Each agent includes required keys: `name`, `description`, `developer_instructions`.
- Global agent controls present in `.codex/config.toml` (`max_threads`, `max_depth`, `job_max_runtime_seconds`).

4. Hooks
- Hooks definition exists: `.codex/hooks.json`.
- Feature flag enabled: `[features].codex_hooks = true`.
- Hook scripts are present and executable under `.codex/hooks/`.

5. Models / Config
- Default model set in `.codex/config.toml` (`gpt-5.4`).
- Sandbox / approval controls present and explicit.

## References

- https://developers.openai.com/codex/guides/agents-md
- https://developers.openai.com/codex/skills
- https://developers.openai.com/codex/subagents
- https://developers.openai.com/codex/app/automations
- https://developers.openai.com/codex/hooks
- https://developers.openai.com/codex/models
- https://developers.openai.com/codex/config-reference
