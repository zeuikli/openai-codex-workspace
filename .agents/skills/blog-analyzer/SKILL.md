---
name: blog-analyzer
description: 分析 OpenAI Codex 官方文章或指定文件，提取可落地的規範變更建議並更新 repo 文件。
---

# Blog Analyzer

## Use when

- 你要追蹤 Codex 官方文件更新並評估是否需要調整 workspace。
- 你需要把文章內容轉成可執行的規範、技能或代理設定。
- 你要建立可審核的「來源 -> 變更建議」紀錄。

## Do not use when

- 任務與官方規範無關（純功能開發）。
- 無法取得可信來源（官方 docs 或可驗證原文）。
- 只是要快速摘要，無需落地改寫。

## Workflow

1. 讀取來源（官方頁面、release note、指定文章）。
2. 提取：新規範、變更點、棄用點、風險。
3. 映射到 repo：`AGENTS.md`、`.codex/agents/`、`.codex/config.toml`、`.agents/skills/`。
4. 產出最小修正方案與驗證步驟。

## Prioritization

- 高優先（先處理）：會直接影響日常 rollout 的文章（例如 prompting、tool 使用、任務閉環）。
- 中優先：中大型改造方法（例如 phased modernization、驗證產物策略）。
- 低優先：案例或治理文章，作為後續優化 backlog。

## Output Format

- Source Summary
- Actionable Changes
- File-level Patch Plan
- Risks and Verification
