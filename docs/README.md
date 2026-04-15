# docs 目錄整理與有效性狀態

> 最後整理：2026-04-15（UTC）  
> 目標：讓 Codex CLI / Codex Cloud 使用時，能快速判斷每份文件是否仍有效、該何時讀、如何驗證。

## 文件狀態總覽

| 文件 | 角色 | 狀態 | 最後檢視 | 驗證方式 |
| --- | --- | --- | --- | --- |
| `docs/codex-best-practices.md` | 官方最佳實踐落地摘要 | Active | 2026-04-15 | 對照 OpenAI `best-practices` 章節與四要素（Goal/Context/Constraints/Done when） |
| `docs/codex-migration-guide.md` | Claude → Codex 遷移判讀與不適用清單 | Active | 2026-04-15 | 對照 OpenAI `agents-md`、`customization`、`subagents`、`hooks`、`config-reference` |
| `docs/karpathy-codex-principles.md` | Codex-only 行為原則（硬性條款補充） | Active | 2026-04-15 | 交叉檢查 `AGENTS.md`、`prompts.md`、`karpathy-loop` skill |
| `docs/advisor-strategy.md` | Subagent 分工策略（實務版） | Active | 2026-04-15 | 對照 OpenAI `subagents` + `.codex/config.toml` |
| `docs/token-usage-report.md` | Token 與上下文成本追蹤報告 | Active | 2026-04-15 | 以 `scripts/run_subagent_checks.py` 的 session log 指標更新 |
| `docs/workspace-performance-report.md` | 操作層效能模型與 KPI | Active | 2026-04-15 | 對照現行模型分派與驗證閉環 |
| `docs/codex-workspace-blueprint.md` | 遷移/維護/發布藍圖（治理層） | Active | 2026-04-15 | 對照 AGENTS + Skills + CI 實際流程 |

## Codex Cloud 再驗證（本次）

本次以「可在 Codex Cloud runner 執行」為準，重跑以下檢查：

1. `python3 scripts/validate_codex_workspace.py`
2. `python3 -m unittest -v tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py`
3. `python3 scripts/run_subagent_checks.py`
4. `python3 scripts/compare_subagent_trends.py`
5. `rg -n "Goal|Context|Constraints|Done when" docs/codex-best-practices.md AGENTS.md`

## 官方來源（本次校對依據）

- <https://developers.openai.com/codex/learn/best-practices>
- <https://developers.openai.com/codex/guides/agents-md>
- <https://developers.openai.com/codex/concepts/customization#next-step>
- <https://developers.openai.com/codex/concepts/customization#skills>
- <https://developers.openai.com/codex/subagents>
- <https://developers.openai.com/codex/hooks>
- <https://developers.openai.com/codex/config-reference#configtoml>

## 維護規則（避免 docs 漂移）

1. 任何新增/修改規範，必須同步更新本頁「文件狀態總覽」的 `最後檢視`。
2. 若官方文件改版影響現行做法，先改 `docs/codex-migration-guide.md`，再回補其他文件。
3. 若一份文件連續兩輪未被引用且內容過時，將狀態改為 `Archive candidate` 並在 `Memory.md` 記錄。
