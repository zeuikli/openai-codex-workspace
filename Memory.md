# Memory.md

> Codex 交接摘要（手動維護）。歷史記錄：`docs/reports/memory-history.md`（按需載入）。

## 最新狀態（2026-04-23，模型路由更新）

- 預設模型改為 `gpt-5.4`：`.codex/config.toml`、`AGENTS.md`、`AGENTS.full.md`、`README.md` 已同步。
- 三層 Agent 分派改依先前測試結果：探索/文件用 `gpt-5.4-mini`，主 Agent 用 `gpt-5.4`，工程/測試/review/security 用 `gpt-5.3-codex`。
- `.codex/agents/*.toml` 已同步：`architecture_explorer` / `docs_researcher` → `gpt-5.4-mini`；`implementer` / `test_writer` / `reviewer` / `security_reviewer` → `gpt-5.3-codex`。

## 最新狀態（2026-04-16，load simulator + workspace 優化）

- 新增 `scripts/simulate_codex_load.py`：7 階段本地 Codex 載入模擬，含計時、hook 執行測試、token 估算、優化建議，輸出 JSON + Markdown 報告至 `benchmarks/results/`。
- 修正 `.agents/skills/caveman-compress/SKILL.md`：`name` 欄位從 `compress` 改為 `caveman-compress`，補入 `Use when` / `Do not use when` section。
- 補入所有 caveman skills 缺少的 `Use when` / `Do not use when` section（`caveman` / `caveman-commit` / `caveman-help` / `caveman-review`）。
- 移除 `.claude/` 目錄（Claude Code 專屬 artifact），加入 `.gitignore`。
- Memory.md 拆分：歷史記錄移至 `docs/reports/memory-history.md`，主檔降至 ~500 tokens。

## 最新狀態（2026-04-16，實際 API benchmark 完成 + README 統整）

- **80 次 live API calls** 完成，4 models × 4 levels × 5 prompts，無 dry-run。
- `gpt-5.3-codex` 改用 Responses API（`/v1/responses`）測試，成功。
- 結果（full level token reduction）：gpt-5.4=5.7%、gpt-5.4-mini=26.7%、gpt-5.4-nano=11.8%、gpt-5.3-codex=6.2%。
- ultra level 最佳：gpt-5.4-mini=51.4%（成本最優）、gpt-5.4-nano=51.2%（速度最快）。
- API key 儲存於 `.env.local`（已 gitignore），未推送至 GitHub。
- 已推送：`origin/codex/integrate-caveman-main-20260416`。

## 最新狀態（2026-04-16，caveman 整合驗證閉環完成）

- 分支：`codex/integrate-caveman-main-20260416`（基於 `claude/codex-workspace-benchmarks-EC65U`）
- upstream HEAD：`c2ed24b`（`chore: sync SKILL.md copies and auto-activation rules`，2026-04-15）
- 修正 `tests/caveman/verify_repo.py`：`node` 不存在時優雅 skip。
- 新增 `tests/test_caveman_compress.py`：5 個 compress/detect/validate 純 Python 單元測試。
- 已 push 到遠端：`origin/codex/integrate-caveman-main-20260416`。

## 驗證狀態（2026-04-16）

| 驗證項目 | 狀態 |
|---|---|
| `validate_codex_workspace.py` | ✅ |
| `simulate_codex_load.py` | ✅（issues=0 為目標） |
| `verify_repo.py`（caveman）| ✅（JS 段 skip：無 node） |
| `test_caveman_compress.py` | ✅（5 ok） |
| `test_codex_hooks_behavior.py` | ✅（5 ok） |
| `test_subagent_checks.py` | ✅（2 ok） |
| JS hook syntax（node --check）| ⏭️ 需 Node.js 環境才可驗 |
| OpenAI live API | ⏭️ 需 OPENAI_API_KEY |

## 目前可依賴的核心檔案

1. `AGENTS.md` — 日常執行的精簡規範入口
2. `.codex/config.toml` — 模型、sandbox、subagent mapping
3. `.codex/agents/*.toml` — 角色邊界與輸出契約
4. `.agents/skills/*/SKILL.md` — 可重用工作流（按需載入）
5. `docs/` — 策略與維護文件
6. `docs/reports/memory-history.md` — 歷史狀態（按需載入）

## 下一步建議

1. 從 `codex/integrate-caveman-main-20260416` 建立 PR → `main`。
2. 若需驗 JS hooks，安裝 Node.js 後直接重跑 `python3 tests/caveman/verify_repo.py`。
3. 定期用 `docs-drift-check` skill 檢查官方文件漂移。
4. 定期跑 `python3 scripts/simulate_codex_load.py` 監控載入 token 消耗。
