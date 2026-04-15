# Memory.md

> Codex 交接摘要（手動維護）

## 最新狀態（2026-04-15，Codex Cloud 再驗證 + docs 整理）

- 已新增 `docs/README.md`，建立 docs 有效性總覽：
  - 列出每份文件的角色、狀態（Active）、最後檢視日期與驗證方式。
  - 收斂本次「Codex Cloud 再驗證」命令清單，固定成可重跑批次。
  - 附上官方來源連結（best-practices / agents-md / customization / subagents / hooks / config-reference）。
- `README.md` 的「Codex 讀取入口」已新增 `docs/README.md`，讓 Agent 啟動時可先判斷 docs 是否最新有效。
- 更新文件時間戳記：
  - `docs/codex-workspace-blueprint.md` 更新基準改為 2026-04-15。
  - `docs/workspace-performance-report.md` 更新基準改為 2026-04-15。

## 驗證狀態（本輪）

- 已驗證：
  - `python3 scripts/validate_codex_workspace.py`
  - `python3 -m unittest -v tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py`
  - `python3 scripts/run_subagent_checks.py`
  - `python3 scripts/compare_subagent_trends.py`
  - `rg -n "Goal|Context|Constraints|Done when" docs/codex-best-practices.md AGENTS.md`
- 未驗證：
  - 真正由 Codex Cloud UI 觸發的遠端作業執行紀錄（本輪為在本地環境重跑 Cloud 相容命令）

## 最新狀態（2026-04-14，Terraform 使用手冊 + 介面驗證補強）

- 已新增 `terraform-optimized/README.md`，補齊方案 C 使用手冊（架構、快速啟動、安全預設、驗證流程、故障排除、後續作業）。
- 已新增 `scripts/validate_terraform_interface.py`：
  - 檢查 `environments/*/main.tf` 傳入的 module 參數是否在 `modules/platform_stack/variables.tf` 宣告。
  - 檢查 `environments/*/main.tf` 使用的 `var.*` 是否在同環境 `variables.tf` 宣告。
  - 檢查 `dev/staging/prod` 的 `main.tf` 參數映射是否一致，避免單一環境漏接新變數。
- 已新增 `tests/test_validate_terraform_interface.py`：
  - 驗證現有 repo 介面檢查可通過。
  - 以 fixture 驗證缺漏變數宣告時會正確報錯。
- `README.md` 已新增 Terraform 手冊入口與驗證指令。

## 驗證狀態（本輪）

- 已驗證：
  - `python3 scripts/validate_terraform_interface.py`
  - `python3 -m unittest -v tests/test_validate_terraform_interface.py`
- 未驗證：
  - Terraform 遠端 provider 實際 `plan/apply`（本輪僅做靜態介面一致性與單元測試）

## 最新狀態（2026-04-14，Anti-timeout 規範補強）

- 讀取 `docs/reports/session-issues-20260414.md` 後，已把「避免長時間無產出」規則正式寫入治理入口。
- `AGENTS.md` 新增三段：
  - `Agent 任務邊界（Anti-timeout）`：限制單 Agent 長文與混合任務，要求超限拆工。
  - `Session Repo 限制`：明確單 session 單 repo，跨 repo 需新 session。
  - `背景 Agent 管理原則`：指派前 commit+push、5 分鐘無回報主動追蹤、失敗不得靜默。
- `README.md` 新增 `Anti-timeout 實務（避免長時間無產出）` 區塊，提供可直接遵循的操作準則。

## 驗證狀態（本輪）

- 已驗證：
  - `rg -n "Agent 任務邊界（Anti-timeout）|Session Repo 限制|背景 Agent 管理原則" AGENTS.md`
  - `rg -n "Anti-timeout 實務（避免長時間無產出）|Session 預設僅能操作啟動時綁定的單一 repo" README.md`
- 未驗證：
  - 遠端推送到 `main`（目前流程採 PR/feature branch 守門）

## 最新狀態（2026-04-14，CI 守門 + token/trend follow-up）

- 重新加入 `.github/workflows/fetch-blog.yml` 作為 CI 守門，觸發包含 `push / pull_request / workflow_dispatch / schedule`。
- `scripts/run_subagent_checks.py` 已改為優先接入實際 session token log（`CODEX_SESSION_LOG` 或 `~/.codex/sessions/**/*.jsonl`）：
  - 輸出 `total_cached_input_tokens` / `uncached_input_tokens` / `last_turn_share_pct` 等真實指標。
  - 保留 repo 掃描（merge conflict、TODO、docs drift signals）並新增 security pattern baseline 比對。
- 新增 `scripts/compare_subagent_trends.py`：
  - 將最新報告追加到 `docs/reports/subagent-quality-history.json`。
  - 產生 `docs/reports/subagent-quality-trend.md`，比對最新與上一筆 delta，供定期追蹤 token 優化是否有效。
- 新增 `docs/reports/security-pattern-baseline.json` 管理安全樣式基線。
- `tests/test_subagent_checks.py` 擴充：
  - 驗證 session token log 載入與 uncached 計算。
  - 驗證趨勢腳本可產出 history 與 trend 報告。

## 驗證狀態（本輪）

- 已驗證：
  - `python3 scripts/validate_codex_workspace.py`
  - `python3 -m unittest -v tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py`
  - `python3 scripts/run_subagent_checks.py`
  - `python3 scripts/compare_subagent_trends.py`
- 未驗證：
  - GitHub Actions 遠端 schedule 實跑（僅本地驗證）

## 最新狀態（2026-04-14，Sub-agent workflow 強化）

- 新增 `scripts/run_subagent_checks.py`：以三個 worker（Research / Implement / Review）執行全 repo 檢查，輸出整合報告。
- `.github/workflows/fetch-blog.yml` 新增 sub-agent 檢查步驟與 artifact 上傳：
  - `docs/reports/subagent-quality-report.md`
  - `docs/reports/subagent-quality-report.json`
- 新增 `tests/test_subagent_checks.py` 驗證報告腳本可產出 Markdown 與 JSON。
- README 補上 sub-agent 檢查指令，將 token/reasoning 優化納入固定驗證流程。

## 驗證狀態

- 已驗證：
  - `python3 scripts/validate_codex_workspace.py`
  - `python3 -m unittest -v tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py`
  - `python3 scripts/run_subagent_checks.py`
- 未驗證：
  - GitHub Actions 遠端執行結果（僅本地驗證）

## 最新狀態（2026-04-14，Karpathy Cloud refresh）

- 新增「Karpathy notes 深度落地（Codex-only）」補強：
  - `docs/karpathy-codex-principles.md` 增補 IDE+Agent 並行、宣告式成功條件、Tenacity 停機條件、Anti-Bloat 衛生檢查、Codex CLI/Cloud 相容要求。
  - `README.md` 增補多 Agent 深度研究與優化流程（Research / Implement / Review）與完整適配檢查命令。
  - `prompts.md` 新增 #17 模板，固定三段分工 + Done when（validator + hooks test + 文件入口一致性）。
  - 內容維持 Codex-only，不引入非 Codex 領域敘述。

- 修正 CI 相容性：`.github/workflows/fetch-blog.yml` 的 README smoke checks 從 `rg` 改為 `grep -E`，避免 GitHub Actions runner 缺少 ripgrep 導致 `exit 127`。
- 新分支 `codex/karpathy-x-thread-practice-20260414`：依 Karpathy X 長文觀察新增「Codex-only 實踐矩陣」到 README，逐條對應 success criteria、assumption/pushback、anti-bloat、tenacity、review 分工。
- README 新增「Codex Cloud 驗證批次」一鍵指令，整合結構驗證、hooks 測試與規範關鍵字 smoke checks。
- README 新增「最新實踐分支」段落，固定保留此 branch 作為 PR merge 來源，符合 feature branch 工作流。

- 新分支 `codex/karpathy-cloud-refresh-20260414`：將 Karpathy 文章重新對照為可直接在 Codex Cloud 執行的「Codex-only」實踐清單。
- README 新增「Karpathy 文章落地（Codex-only，2026-04-14 refresh）」段落，明確對照 Success Criteria / Assumption Ledger / Naive-First / Tenacity Loop / Generation vs Discrimination。
- README 新增「Codex Cloud 執行指令（可直接複製）」區塊，整合結構驗證、hooks 測試與 smoke checks。
- Hook 推送策略更新：允許推送 `codex/*`、`feature/*` 分支；禁止 `main/master` 與未指定分支的 `git push`。
- 新分支 `codex/cloud-e2e-followup-20260414`：補齊先前「僅本地靜態檢查」缺口，新增可在遠端 CI 重跑的端到端驗證。
- 新增 `scripts/validate_codex_workspace.py`，把 workflow 內嵌 Python 驗證器抽離成可本地/雲端共用腳本。
- 新增 `tests/test_codex_hooks_behavior.py`，覆蓋 SessionStart / PreToolUse / PostToolUse 三個 hooks 的行為層測試。
- `.github/workflows/fetch-blog.yml` 改為執行：結構驗證 + hooks 行為測試 + README smoke checks。
- 新分支 `codex/karpathy-practice-20260414`：將 Karpathy 文章重點落地為 README「Codex Cloud 實踐對照」與「最小驗證清單」，方便 Agent 在雲端直接執行驗證。
- README 新增四個可執行對照面向（success criteria、assumption/pushback/anti-bloat、tenacity loop、IDE+Agent 分工），並附對應 `rg`/`test` 指令。

## 前一狀態（2026-04-14，分支整併）

- 新分支 `claude/karpathy-optimization-merged` 把 `codex-karpathy-optimization-M7POy` 與 `optimize-karpathy-repo-k6Vbz` 兩段歷史 `--no-ff` 收斂。
- 衝突檔案採 followup 優化版本（frontmatter 驗證 / prompt 索引 11+12~15 / CHANGELOG + Memory 最新狀態）。
- README 新增「分支整併紀錄」段落，後續 session 可直接從此處定位當前工作分支。

## 前一狀態（2026-04-14，Karpathy followup 優化）

- CI 驗證器 (`.github/workflows/fetch-blog.yml`) 納入 `karpathy-loop` 必備 skill 與 SKILL frontmatter/slug 一致性檢查，填補先前「只做文件層靜態檢查」的缺口。
- SessionStart hook 補一句 Karpathy 九條硬性守則提醒，避免單靠 AGENTS.md 才能生效。
- `docs/karpathy-codex-principles.md` 修正 prompt 索引為 11（一鍵套用）+ 12~15。
- Compliance report 與 CHANGELOG 同步更新。

## 前一狀態（2026-04-14，Karpathy 原則導入）

- Karpathy（2026）對 LLM coding workflow 的觀察，已翻譯為 Codex 專屬九條原則，落在 `docs/karpathy-codex-principles.md`。
- `AGENTS.md` / `AGENTS.full.md` 補入「Karpathy 實作原則（硬性條款）」段落，作為既有實作原則的延伸。
- 新增 skill `karpathy-loop` 作為宣告式驗證迴圈的執行標準（預設上限 5 輪 / 10 分鐘）。
- `prompts.md` 新增 Karpathy 相關模板：一鍵套用、Success-Criteria Loop、Naive-First、Pushback、Anti-Bloat 自檢。
- README 已同步 Karpathy 原則入口，Agent 啟動即可循序讀到新規範。

## 早前狀態（2026-04-14）

- 本 repo 已完成過往遷移並移除所有非 Codex 必要結構。
- Subagent 檔名已做嚴格一致化（檔名 = `name`，底線命名）：
  - `architecture_explorer.toml`
  - `docs_researcher.toml`
  - `implementer.toml`
  - `reviewer.toml`
  - `security_reviewer.toml`
  - `test_writer.toml`
- `.codex/config.toml` 與 CI workflow 已同步新檔名引用。
- `AGENTS.md` / `AGENTS.full.md` 已納入 Cookbook 導向分層調用（Tier 1/2/3）。

## 目前可依賴的核心檔案

1. `AGENTS.md`：日常執行的精簡規範入口。
2. `AGENTS.full.md`：完整治理規範與觸發條件。
3. `.codex/config.toml`：模型、sandbox、subagent mapping。
4. `.codex/agents/*.toml`：角色邊界與輸出契約。
5. `.agents/skills/*/SKILL.md`：可重用工作流。
6. `docs/`：策略與維護文件。

## 本輪關鍵決策

- 採用 Karpathy 九條原則作為 Codex 主 Agent 與 Subagents 的硬性守則，補足 Cookbook 沒明確講到的行為邊界（假設檢驗、顯化衝突、抗諂媚、抗肥大、最小半徑、生成/辨識分工）。
- Karpathy 原則不取代既有規範，而是掛在「實作原則」之後作為延伸；AGENTS.md / AGENTS.full.md 都有同步入口。
- Success-Criteria Loop 獨立成 skill（`karpathy-loop`），任務具備可自動驗證訊號時優先使用。
- 關閉 plugin 模式，僅保留 skills + subagents + hooks + automations（按需）。
- Subagent 嚴格命名一致化，避免配置與載入漂移。
- 將 Cookbook 規則按「使用頻率與實用性」分層：
  - Tier 1：`Codex Prompting Guide`
  - Tier 2：`Modernizing your Codebase with Codex`
  - Tier 3：其他治理/案例文章

## 驗證狀態

- 已驗證：
  - 非 Codex 結構不存在（`.claude`、`CLAUDE.md`、`plugins` 已移除）
  - subagent 檔案存在且配置引用正確
  - skills 結構完整
- 未驗證：
  - 未在遠端 CI 實跑（僅本地靜態檢查）

## 下一步建議

1. 在 CI 跑一次結構驗證（含 `.github/workflows/fetch-blog.yml`）。
2. 若新增技能，維持 `Use when` / `Do not use when` 邊界格式。
3. 定期用 `docs-drift-check` 檢查官方文件漂移。
