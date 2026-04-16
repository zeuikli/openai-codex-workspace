# Memory History (歷史狀態存檔)

> 本檔為 Memory.md 的歷史記錄存檔，由主 Memory.md 拆分以降低強制載入 token 數。
> 按需讀取，不在 session 啟動時自動載入。

---

## 最新狀態（2026-04-16，latest caveman main 整合進 Codex skill 結構）

- 已從 upstream `https://github.com/JuliusBrussee/caveman` 抓取最新 `main`（`c2ed24b3e5d412cd0c25197b2bc9af587621fd99`）進行對照整合。
- 將 `caveman-compress` 從舊版缺件狀態改為真正可執行的 Codex repo skill：腳本現位於 `.agents/skills/caveman-compress/scripts/`。
- 壓縮流程已改為 OpenAI-first：優先 `OPENAI_API_KEY` + Responses API，保留 Anthropic / `claude` CLI fallback。
- caveman 驗證腳本已改寫為檢查目前 repo 的 Codex-native 佈局，不再依賴舊 caveman standalone 安裝面。

## 最新狀態（2026-04-15，upstream repo 比對與差異報告）

- 執行 upstream (`https://github.com/JuliusBrussee/caveman`) 與本地 workspace 的檔案完整性比對。
- 比對結論：
  - `missing_from_workspace_count = 0`
  - `extra_in_workspace_count = 3`（benchmark/load test/report 檔）
  - `content_differences_count = 4`（`.gitignore`、`README.md`、2 個 hooks 檔為預期差異）
- 新增：`docs/repo-parity-report.md` / `docs/repo-parity-report.json`

## 最新狀態（2026-04-15，修正載入測試失敗：caveman banner / mode tracker）

- 修正 `caveman/hooks/caveman-activate.js`：啟用訊息改回含 `CAVEMAN MODE ACTIVE.` 前綴。
- 修正 `caveman/hooks/caveman-mode-tracker.js`：預設 silent 模式，`CAVEMAN_REINFORCE=1` 才輸出 per-turn。
- 驗證：`verify_repo.py` ✅ / `run_codex_cloud_load_test.py` ✅ / `test_hooks.py` ✅

## 最新狀態（2026-04-15，Caveman benchmark 修補 + 安全性調整）

- `openai_workspace_benchmark.py`：新增 `.env.local` 自動載入、參數合法性檢查。
- `run_codex_cloud_load_test.py`：報告加入 `args` 欄位、失敗時非零退出碼。

## 最新狀態（2026-04-14，Anti-timeout 規範補強）

- `AGENTS.md` 新增：`Agent 任務邊界（Anti-timeout）` / `Session Repo 限制` / `背景 Agent 管理原則`。

## 最新狀態（2026-04-14，CI 守門 + token/trend follow-up）

- 重新加入 `.github/workflows/fetch-blog.yml`。
- 新增 `scripts/run_subagent_checks.py`（session token log 接入）。
- 新增 `scripts/compare_subagent_trends.py`。

## 最新狀態（2026-04-14，Karpathy Cloud refresh）

- `docs/karpathy-codex-principles.md` 增補 IDE+Agent 並行、宣告式成功條件、Tenacity 停機條件。
- `prompts.md` 新增 #17 模板。
- CI smoke checks 從 `rg` 改為 `grep -E`（避免 GitHub Actions runner 缺 ripgrep）。

## 前一狀態（2026-04-14，Karpathy 原則導入）

- `docs/karpathy-codex-principles.md` 新增九條原則。
- `AGENTS.md` / `AGENTS.full.md` 補入「Karpathy 實作原則（硬性條款）」。
- 新增 skill `karpathy-loop`。

## 早前狀態（2026-04-14）

- Subagent 檔名嚴格一致化（`architecture_explorer.toml` / `docs_researcher.toml` / `implementer.toml` / `reviewer.toml` / `security_reviewer.toml` / `test_writer.toml`）。

## 本輪關鍵決策（歷史）

- 採用 Karpathy 九條原則作為 Codex 主 Agent 與 Subagents 的硬性守則。
- Success-Criteria Loop 獨立成 skill（`karpathy-loop`）。
- 關閉 plugin 模式，僅保留 skills + subagents + hooks + automations（按需）。
- Cookbook 規則分層：Tier 1=Codex Prompting Guide / Tier 2=Modernizing Codebase / Tier 3=治理文章。

## 最新狀態（2026-04-15，Caveman × OpenAI token 效率研究）

- 新增 `scripts/research_caveman_openai_fit.py`。
- 新增：`docs/reports/caveman_openai_fit_20260415.json/.md` / `caveman_research_notes_20260415.md`。

## 最新狀態（2026-04-15，Caveman 研究流程二次驗證 + repo 效能優化）

- `scripts/run_subagent_checks.py` 新增 `--exclude` 參數。
- 新增 `scripts/benchmark_repo_scan_efficiency.py`。
- 量化：`scanned_repo_chars` 131,219 → 81,951（-37.5%）。
