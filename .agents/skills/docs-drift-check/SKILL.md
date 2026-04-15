---
name: docs-drift-check
description: 比對 repo 內操作規範與官方文件是否漂移，優先檢查 AGENTS、skills、subagents、hooks、models 與 automations。
---

# Docs Drift Check

## Use when

- 你懷疑現有規範已落後官方文件。
- 專案剛升級模型、hooks、subagents 或 automation 策略。
- 你要建立「定期驗證規範」的維護流程。

## Do not use when

- 任務是純功能開發且不涉及流程/規範更新。
- 你沒有可信來源（官方文件或既有規範）可做比對。
- 當前需求急迫，應先修復 production 問題再做治理。

## Scope

- AGENTS.md 載入與覆寫順序
- Skills 結構與觸發邊界
- Subagents 自訂 agent schema 與模型分派
- Hooks 限制（experimental、Bash matcher）
- Models 推薦與角色分工
- Automations 執行環境與風險
- Claude 專屬能力是否被誤當成 Codex 既有能力

## Cookbook Priority

優先比對以下官方文章與其落地規則：
1. `Codex Prompting Guide`（高頻優先，執行策略基準）
2. `Modernizing your Codebase with Codex`（中大型任務與分階段產物）
3. 其他 cookbook 案例（僅在與本 repo 直接相關時納入）

## Official Sources

- `Best practices`: https://developers.openai.com/codex/learn/best-practices
- `AGENTS.md`: https://developers.openai.com/codex/guides/agents-md
- `Customization / next step`: https://developers.openai.com/codex/concepts/customization#next-step
- `Customization / skills`: https://developers.openai.com/codex/concepts/customization#skills
- `Subagents`: https://developers.openai.com/codex/subagents
- `Hooks`: https://developers.openai.com/codex/hooks
- `Config reference`: https://developers.openai.com/codex/config-reference#configtoml

## Output Format

- Drift Summary：目前不一致點（按風險排序）
- Proposed Fix：每一點的最小修正方案
- Verification Plan：如何在 CI 或例行流程驗證已修正
