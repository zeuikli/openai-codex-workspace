# CHANGELOG

## 2026-04-16（sync latest caveman main into Codex-native workspace）

- 新分支 `codex/integrate-caveman-main-20260416`：以 upstream `JuliusBrussee/caveman` `main@c2ed24b` 為基準，補齊最新 caveman-compress 工具鏈。
- `.agents/skills/caveman-compress/scripts/*` 新增 OpenAI-first 壓縮腳本，優先走 Responses API，保留 Anthropic / `claude` CLI fallback。
- `tests/caveman/verify_repo.py`、`tests/caveman/test_hooks.py` 改寫為檢查目前 repo 的 Codex-native caveman 結構，不再依賴舊版 standalone layout。
- 新增 `tests/test_caveman_compress.py` 與 `tests/caveman-compress/` fixture，讓壓縮 skill 有可重跑的本地驗證。

## 2026-04-14（Karpathy notes 深度落地：Codex CLI/Cloud）

- `docs/karpathy-codex-principles.md` 新增「2026 文章增補：Codex-only 深度落地」，補齊 IDE+Agent 並行、Tenacity 停機條件、Anti-Bloat 衛生檢查與 CLI/Cloud 相容要求。
- `README.md` 新增「多 Agent 深度研究與優化流程（Codex-only）」與「Codex CLI / Codex Cloud 完整適配檢查」段落，將文章觀察映射為可執行驗證閉環。
- `prompts.md` 新增 #17「Codex-only 多 Agent 深度研究 + CLI/Cloud 適配」模板，固定 Research / Implement / Review 三段分工與驗收條件。

## 2026-04-14（Karpathy Cloud refresh）

- 新分支 `codex/karpathy-cloud-refresh-20260414`：README 補上「Karpathy 文章落地（Codex-only）」可執行對照。
- 新增「Codex Cloud 執行指令（可直接複製）」段落，整合 workspace validator、hooks 單元測試與 smoke checks。
- 更新 hook 推送策略：允許推送 `codex/*` 與 `feature/*` 分支，禁止推送 `main/master`。
- 內容範圍維持 Codex-only，不加入非 Codex 主題。

## 2026-04-14（Codex Cloud E2E followup）

- 新增 `scripts/validate_codex_workspace.py`，將 CI 內嵌驗證器腳本化，支援本地與遠端一致執行。
- 新增 `tests/test_codex_hooks_behavior.py`，補上 hooks 行為層測試（SessionStart / PreToolUse / PostToolUse）。
- `.github/workflows/fetch-blog.yml` 改為三段驗證：workspace 結構檢查、hooks 單元測試、README smoke checks。
- README 補「遠端 CI / Codex Cloud pipeline（端到端）」段落，將驗證流程文件化。

## 2026-04-14（分支整併）

- 新分支 `claude/karpathy-optimization-merged` 整併 `claude/codex-karpathy-optimization-M7POy` 與 `claude/optimize-karpathy-repo-k6Vbz` 兩條優化線。
- 採 `--no-ff` merge 保留雙方歷史；衝突檔案（`CHANGELOG.md` / `Memory.md` / `docs/karpathy-codex-principles.md`）統一採納 followup 優化版本。
- README 補「分支整併紀錄」段落，避免之後迷路。

## 2026-04-14（Karpathy 優化 followup）

- `.github/workflows/fetch-blog.yml` 驗證器補上 `karpathy-loop` 與 SKILL frontmatter / slug 一致性檢查，填補新增 skill 未被 CI 守門的缺口。
- `.codex/hooks/session_start_note.sh` 追加一句 Karpathy 九條硬性守則的 session-level 提醒，避免單純依賴 AGENTS.md 被讀到。
- `docs/karpathy-codex-principles.md` 修正 prompt 索引（11 一鍵套用 + 12~15 Loop/Naive/Pushback/Anti-Bloat）。
- `CODEX_COMPLIANCE_REPORT.md` 同步 `karpathy-loop` 與 frontmatter 守門條目。

## 2026-04-14（Karpathy 原則導入）

- 新增 `docs/karpathy-codex-principles.md`：把 Karpathy 對 LLM coding workflow 的九條觀察翻譯為 Codex 專屬執行規範。
- `AGENTS.md` / `AGENTS.full.md` 同步加上「Karpathy 實作原則（硬性條款）」段落作為既有實作原則的延伸。
- `prompts.md` 新增四組 Karpathy 模式模板：一鍵套用、Success-Criteria Loop、Naive-First、Pushback、Anti-Bloat 自檢。
- 新增 skill `karpathy-loop`：把任務轉為宣告式驗證迴圈，附明確停機條件與 Output Contract。
- README.md 補上 Karpathy 原則入口，確保 Agent 啟動時能直接連到新規範。

## 2026-04-14

- 全面移除 Claude 專屬資產：`.claude/`、`CLAUDE.md`。
- 以 Codex 結構重整：保留 `AGENTS.md`、`.codex/agents/*.toml`、`.agents/skills/*/SKILL.md`。
- `docs/advisor-strategy.md` 改寫為 Codex Subagent + Advisor-style 實務規範。
- `.codex/config.toml` 補齊 `nickname_candidates` 與更明確的角色路由描述。
- 六個 subagent TOML 全數補齊邊界與統一輸出契約。
- 新增 Codex 版 skills：`agent-team`、`blog-analyzer`、`cost-tracker`。
- 修正文件命名與引用：以 `docs/codex-workspace-blueprint.md` 取代舊 `blog-analysis-report.md` 命名。

## 2026-04-13

- 初始 Codex 化遷移：新增 `AGENTS.md`、`.codex/`、`.agents/` 與相容文件。
