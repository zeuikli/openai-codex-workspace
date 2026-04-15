# OpenAI Codex Workspace

這個 repo 是 **Codex App / Codex CLI 原生可讀** 的 workspace 範本。
目標是提供一套可直接執行的規範：`AGENTS.md` + `.codex/agents` + `.agents/skills`。

## 目前狀態

- 已導入 Cookbook 分層調用（Tier 1/2/3）。
- 已採用 **Karpathy 原則 × Codex 實踐手冊** 作為硬性守則（見 `docs/karpathy-codex-principles.md`）。
- Subagents 已做嚴格命名一致化（檔名對齊 `name`）。
- 新增 skill：`karpathy-loop`（宣告式驗證迴圈）。
- CI 守門（`.github/workflows/fetch-blog.yml`）延伸到 SKILL.md frontmatter 與 slug 一致性，封堵 Codex CLI 靜默載入失敗的風險。
- SessionStart hook 內嵌 Karpathy 九條硬性守則的一句話提醒，減少對 AGENTS.md 被讀到的單點依賴。

## 官方基線

這個 workspace 目前以 OpenAI 官方 Codex 文件作為第一手規範來源，並把 `claude-code-workspace` 視為遷移樣本，而不是直接照搬的設定來源。

- `AGENTS.md` 分層與覆寫順序：<https://developers.openai.com/codex/guides/agents-md>
- Codex 最佳實踐：<https://developers.openai.com/codex/learn/best-practices>
- Customization 建議導入順序：<https://developers.openai.com/codex/concepts/customization#next-step>
- Skills 結構與 progressive disclosure：<https://developers.openai.com/codex/concepts/customization#skills>
- Subagents 與自訂 agent schema：<https://developers.openai.com/codex/subagents>
- Hooks 能力與限制：<https://developers.openai.com/codex/hooks>
- `.codex/config.toml` 參數定義：<https://developers.openai.com/codex/config-reference#configtoml>

對 `claude-code-workspace` 的遷移判準與不適用項目，統一整理在 `docs/codex-migration-guide.md`。

## Anti-timeout 實務（避免長時間無產出）

依 `docs/reports/session-issues-20260414.md`，已將「長任務拆分 + Agent 邊界」納入規範：

1. **任務邊界**
   - 單一 Agent 不承接 > 200 行長文輸出。
   - 不在同一個 Agent 任務混合「長文生成」與「git 操作」。
2. **進度與失敗可觀測**
   - 背景 Agent 超過 5 分鐘未回報，主 Agent 必須主動檢查。
   - 逾時/錯誤不得靜默，需立即通知。
3. **Repo 限制先說清楚**
   - Session 預設僅能操作啟動時綁定的單一 repo。
   - 跨 repo 工作要在目標 repo 另開 session；短期替代是同 repo 隔離分支（`codex/*`、`feature/*`）。

## Codex Cloud 實踐對照（2026-04-14）

以下對照來自 Karpathy 近期 LLM coding 筆記，且僅保留 **Codex 實務** 相關內容：

1. **Success criteria first（宣告式任務）**
   - 以 `prompts.md` 的 11（Karpathy 一鍵套用）與 12（Success-Criteria Loop）為預設入口。
2. **Assumption / pushback / anti-bloat（防錯與減肥）**
   - 由 `AGENTS.md` 的「Karpathy 實作原則」與 `docs/karpathy-codex-principles.md` 強制執行：
     - 先列假設與驗證方式
     - 規格衝突先顯化，不盲目迎合
     - 先做樸素正確版，再優化
3. **Tenacity + 驗證閉環（連續修補直到可驗證）**
   - 使用 `karpathy-loop` skill，預設上限 `5 輪 / 10 分鐘`，每輪都必須有可觀測驗證輸出。
4. **IDE + Agent 並行工作流**
   - 本 repo 預設「Agent 實作 + 人類審閱」分工：主流程由 Codex 執行，人工聚焦在 reviewer / security reviewer 的辨識與風險收斂。

### Karpathy X 文章實踐矩陣（Codex-only，2026-04-14）

> 來源：Karpathy 的 X 貼文（連結見下方「官方參考」）。
> 本段僅保留可在 Codex Cloud 直接執行與驗證的內容，不擴展到非 Codex 議題。

| 文章觀察 | Codex Workspace 實踐 | 可執行驗證 |
| --- | --- | --- |
| 不要只下命令，改給 success criteria | 任務啟動預設使用 `prompts.md` #11/#12，先定義 `Done when` 再實作 | `rg -n "^## 1[12]\\." prompts.md` |
| 模型常見問題是錯誤假設、少澄清、不會 pushback | `AGENTS.md` 強制 `Assumption Ledger`、`Surface, Don't Swallow`、`Pushback Over Sycophancy` | `rg -n "Assumption Ledger|Surface, Don't Swallow|Pushback Over Sycophancy" AGENTS.md` |
| 模型容易 over-engineering、抽象膨脹 | 以 `Naive-First` 與 `Anti-Bloat` 做硬性守則，先最小正確版再優化 | `rg -n "Naive-First|Anti-Bloat" AGENTS.md docs/karpathy-codex-principles.md` |
| Agent 的核心優勢是 tenacity（反覆嘗試直到過） | 使用 `karpathy-loop` skill 跑 `5 輪 / 10 分鐘` 驗證迴圈 | `rg -n "5 輪 / 10 分鐘|Tenacity Loop" .agents/skills/karpathy-loop/SKILL.md docs/karpathy-codex-principles.md` |
| Generation vs Discrimination 應分工 | 重大變更要求 reviewer / security reviewer，避免自寫自審 | `rg -n "Generation vs Discrimination|reviewer|security_reviewer" AGENTS.md .codex/agents/*.toml` |

### 多 Agent 深度研究與優化流程（Codex-only）

依 `multi-agent-collaboration` + `blog-analyzer` + `deep-review` 的最小組合，建議固定拆成三段：

1. **Research worker（docs_researcher / gpt-5.4-mini）**
   - 任務：把文章觀察轉成「可執行規範變更」。
   - 交付：Source Summary / Actionable Changes / 風險列表。
2. **Implementation worker（implementer / gpt-5.3-codex）**
   - 任務：依最小修改半徑更新文件與腳本。
   - 交付：diff 摘要 + 可執行驗證命令。
3. **Review worker（reviewer + security_reviewer / gpt-5.3-codex）**
   - 任務：聚焦概念錯誤、越權行為、回歸風險。
   - 交付：Findings（含 file:line）、Residual risk、是否可合併。

> 目的：保留 Agent tenacity 優勢，同時以辨識分工抑制錯誤假設與 over-engineering。

### Codex CLI / Codex Cloud 完整適配檢查

> 本段對應「文章中提到模型會做錯假設、需要嚴格驗證閉環」的落地做法。

```bash
# 1) Workspace 規範結構檢查
python3 scripts/validate_codex_workspace.py

# 2) Hooks 行為測試（安全邊界 / 提示行為）
python3 -m unittest -v tests/test_codex_hooks_behavior.py


# 2.5) Sub-Agent 全域檢查 + Token/Reasoning 優化報告
python3 scripts/run_subagent_checks.py

# 報告輸出
# - docs/reports/subagent-quality-report.md
# - docs/reports/subagent-quality-report.json
# - docs/reports/subagent-quality-trend.md
# - docs/reports/subagent-quality-history.json

# 2.6) 歷史趨勢比對（token/速度優化）
python3 scripts/compare_subagent_trends.py

# 3) 文件可讀性與入口 smoke checks
rg -n "Karpathy 實作原則|Assumption Ledger|Anti-Bloat|Generation vs Discrimination" AGENTS.md docs/karpathy-codex-principles.md
rg -n "多 Agent 深度研究與優化流程|Codex CLI / Codex Cloud 完整適配檢查|官方基線" README.md
```

#### Codex Cloud 驗證批次（建議直接貼上）

```bash
python3 scripts/validate_codex_workspace.py && \
python3 -m unittest -v tests/test_codex_hooks_behavior.py && \
rg -n "^## 1[12]\\." prompts.md && \
rg -n "Assumption Ledger|Surface, Don't Swallow|Pushback Over Sycophancy|Naive-First|Anti-Bloat|Generation vs Discrimination" AGENTS.md && \
rg -n "Tenacity Loop|5 輪 / 10 分鐘" docs/karpathy-codex-principles.md .agents/skills/karpathy-loop/SKILL.md
```

#### 最新實踐分支（保留作為 PR merge 來源）

- `codex/karpathy-x-thread-practice-20260414`
- 建議流程：在此分支持續實作與驗證 → 發 PR → merge 後再從 `main` 開下一條 `codex/*` 分支。

### 本 repo 的最小驗證清單（可直接在 Codex Cloud 跑）

```bash
# 1) 基礎結構完整性（關鍵檔案存在）
test -f AGENTS.md && test -f Memory.md && test -f prompts.md && test -f docs/karpathy-codex-principles.md

# 2) Karpathy 原則是否掛載到治理入口
rg -n "Karpathy 實作原則|Tenacity Loop|Generation vs Discrimination" AGENTS.md AGENTS.full.md

# 3) Prompt 模板是否含 11~15
rg -n "^## 1[1-5]\\." prompts.md

# 4) README 是否提供 Agent 可讀入口與對照說明
rg -n "Codex 讀取入口|Codex Cloud 實踐對照|最小驗證清單|官方基線" README.md
```

### 遠端 CI / Codex Cloud pipeline（端到端）

本 repo 以 `.github/workflows/fetch-blog.yml` 作為遠端守門，會在 `push / pull_request / workflow_dispatch` 執行，並以 `schedule` 每日定期追蹤趨勢。

固定檢查：

1. `python3 scripts/validate_codex_workspace.py`：結構與治理規範檢查。
2. `python3 -m unittest -v tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py`：hook 與 sub-agent 腳本測試。
3. `python3 scripts/run_subagent_checks.py`：輸出 sub-agent 全域檢查，接入實際 session token log（cached/uncached、last-turn share）。
4. `python3 scripts/compare_subagent_trends.py`：追加歷史資料點並產生趨勢比對報告。

本次 followup 變更維護分支：`codex/cloud-e2e-followup-20260414`（用於追蹤 E2E 驗證補強）。 

#### 本分支已落地項目

- `scripts/validate_codex_workspace.py`：抽離自 workflow 的可重用驗證器（可本地/CI 共用）。
- `tests/test_codex_hooks_behavior.py`：覆蓋 SessionStart / PreToolUse / PostToolUse 的 hooks 行為測試。
- `scripts/compare_subagent_trends.py`：比較最新與上一筆趨勢，產生 `subagent-quality-trend.md` + `subagent-quality-history.json`。
- `.github/workflows/fetch-blog.yml`：固定執行「結構驗證 → 測試 → sub-agent 全域檢查 → 趨勢比對」，並上傳 `subagent-quality-report` artifact。

### Karpathy 文章落地（Codex-only，2026-04-14 refresh）

> 只保留 Codex 實務，不引入非 Codex 主題。

對照 Karpathy 筆記，本 repo 的可執行落地如下：

1. **Success Criteria First（先驗收條件）**
   - 任務開始先寫 `Done when`，再實作。
   - 推薦 prompt：`prompts.md` 的 11（Karpathy 一鍵套用）與 12（Success-Criteria Loop）。
2. **Assumption Ledger + Pushback（假設清冊與反諂媚）**
   - 每個假設都要附檢驗方式；遇衝突先顯化，不盲從。
   - 治理入口：`AGENTS.md`「Karpathy 實作原則」與 `docs/karpathy-codex-principles.md`。
3. **Naive-First, Optimize-Second（先正確後優化）**
   - 先寫最小正確版 + 驗證，再進行優化。
4. **Tenacity Loop（可觀測驗證迴圈）**
   - 以 `karpathy-loop` 的 `5 輪 / 10 分鐘` 為預設停機條件，避免無限迴圈。
5. **Generation vs Discrimination（寫作與審查分工）**
   - 重大變更必經 reviewer / security reviewer，不自寫自審。

#### Codex Cloud 執行指令（可直接複製）

```bash
# A) 結構與治理規範驗證
python3 scripts/validate_codex_workspace.py

# B) hooks 行為層測試
python3 -m unittest -v tests/test_codex_hooks_behavior.py

# C) README / Prompt / AGENTS smoke checks
test -f AGENTS.md && test -f Memory.md && test -f prompts.md && test -f docs/karpathy-codex-principles.md
rg -n "Karpathy 實作原則|Tenacity Loop|Generation vs Discrimination" AGENTS.md AGENTS.full.md
rg -n "^## 1[1-5]\\." prompts.md
rg -n "Codex Cloud 實踐對照|Karpathy 文章落地|Codex Cloud 執行指令" README.md
```

#### Hook 推送策略（feature branch only）

- `pre_tool_use_guard.sh` 現在允許 `git push <remote> codex/*` 與 `git push <remote> feature/*`。
- 仍禁止推送到 `main` / `master`，且未指定分支的 `git push` 也會被拒絕。
- 目標是讓 Codex Cloud 可直接推送功能分支，同時保護預設分支安全邊界。

## Codex 讀取入口

> 使用者或 Agent 依「情境」讀取對應檔案，避免全量預讀。所有路徑皆以 **本 repo 根目錄** 為基準（相對路徑）。

### 啟動固定讀（每次 session 開頭）

- `AGENTS.md`：精簡規範入口（含 Karpathy 實作原則硬性條款）。
- `Memory.md`：上輪交接摘要與最新狀態。
- `prompts.md`：可直接貼上的常用 prompt 模板（含 Karpathy 模式 11–15）。

### 情境按需讀

| 情境 | 要讀的檔案 |
| --- | --- |
| 需要完整治理規範 | `AGENTS.full.md` |
| 要套用 Karpathy 九條硬性守則 | `docs/karpathy-codex-principles.md` |
| 角色分工 / 模型路由 | `.codex/config.toml` + `.codex/agents/*.toml` |
| 執行可自動驗證的多輪任務 | `.agents/skills/karpathy-loop/SKILL.md` |
| 多 Agent 協作拆工 | `.agents/skills/multi-agent-collaboration/SKILL.md` |
| 深度審查 / 重大變更守門 | `.agents/skills/deep-review/SKILL.md` |
| 文件與規格漂移檢查 | `.agents/skills/docs-drift-check/SKILL.md` |
| 長任務交接 | `.agents/skills/session-handoff/SKILL.md` |
| 成本與 token 回顧 | `.agents/skills/cost-tracker/SKILL.md` + `docs/token-usage-report.md` |
| 其他治理策略 | `docs/advisor-strategy.md`、`docs/codex-workspace-blueprint.md`、`docs/codex-best-practices.md` |
| 做 Claude → Codex 遷移判讀 | `docs/codex-migration-guide.md` |

### 通則

- `SKILL.md` 採按需載入：只在任務需要時讀對應 skill，不全量預讀。
- 長任務每個里程碑做一次短摘要，降低上下文重複成本。
- 任務收尾前更新 `Memory.md`（完成事項、驗證狀態、Followup）。

## CLI 快速啟動（載入 AGENTS + SKILL + Karpathy 原則）

在 **本 repo 根目錄** 執行（路徑依你本機 clone 位置自行替換；以下用 `$WORKSPACE` 代表）：

```bash
# 若已在 repo 根目錄，可直接：
codex "請先固定讀取 AGENTS.md、Memory.md、prompts.md 與 docs/karpathy-codex-principles.md；接著讀取 .codex/config.toml 與 .codex/agents/*.toml；skills 僅按需載入（不要全量預讀），並於長任務每個里程碑輸出短摘要。Karpathy 九條原則視為硬性守則。"

# 或指定工作目錄：
codex -C "$WORKSPACE" "<同上 prompt>"
```

> 提示：使用者或 Agent 請依「Codex 讀取入口」章節列出的順序與條件，按需讀取檔案，不要全量預讀。

## 目前模型配置

- 主模型（workspace 預設）：`gpt-5.4`（見 `.codex/config.toml`）。
- Subagent 輕量探索/文件：`gpt-5.4-mini`（`architecture_explorer`、`docs_researcher`）。
- Subagent 實作/審查/測試：`gpt-5.3-codex`（`implementer`、`reviewer`、`security_reviewer`、`test_writer`）。

## 建議模型策略

- 日常任務：`gpt-5.4` + `medium` reasoning
- 全面審查與整體優化：`gpt-5.4` + `high` reasoning
- 最終驗收與高風險收斂：`gpt-5.4` + `xhigh` reasoning
- 架構盤點 / 文件查證 / 成本分析：`gpt-5.4-mini` + `medium` reasoning
- 純實作 / 測試補強：`gpt-5.3-codex` + `medium` reasoning
- 深度 code review / security review：`gpt-5.3-codex` + `high` reasoning

核心原則：
- 跨模組決策與最後收斂交給 `gpt-5.4`
- 高頻讀取與整理交給 `gpt-5.4-mini`
- coding 密集工作交給 `gpt-5.3-codex`

## Token 報表

- 本次測試與優化前後比較：[`docs/token-usage-report.md`](docs/token-usage-report.md)

## 目錄

```text
openai-codex-workspace/
├── AGENTS.md
├── AGENTS.full.md
├── Memory.md
├── prompts.md
├── .codex/
│   ├── config.toml
│   ├── agents/
│   │   ├── architecture_explorer.toml
│   │   ├── docs_researcher.toml
│   │   ├── implementer.toml
│   │   ├── reviewer.toml
│   │   ├── security_reviewer.toml
│   │   └── test_writer.toml
│   ├── hooks.json
│   └── hooks/
├── .agents/
│   └── skills/
│       ├── karpathy-loop/
│       └── ...（其他 skills）
└── docs/
    ├── karpathy-codex-principles.md
    └── ...
```

## 內建 Skills

- `multi-agent-collaboration`
- `deep-review`
- `frontend-design`
- `docs-drift-check`
- `session-handoff`
- `agent-team`
- `blog-analyzer`
- `cost-tracker`
- `karpathy-loop`（宣告式驗證迴圈；Success-Criteria → 自動修補 → 停機條件）

## Karpathy 原則速查

> 完整說明：[`docs/karpathy-codex-principles.md`](docs/karpathy-codex-principles.md)

1. Assumption Ledger：假設必須附檢驗方式。
2. Surface, Don't Swallow：衝突先顯化。
3. Pushback Over Sycophancy：違規指令先反駁。
4. Naive-First, Optimize-Second：先正確再優化。
5. Success-Criteria First：先寫 `Done when`。
6. Tenacity Loop：自動驗證迴圈，5 輪 / 10 分鐘上限。
7. Minimal Blast Radius：只改相關檔案。
8. Anti-Bloat：抽象/參數/選項預設不加。
9. Generation vs Discrimination：重大變更必經 reviewer。

## Cookbook 分層調用

- Tier 1（高頻）：`Codex Prompting Guide`
- Tier 2（中頻）：`Modernizing your Codebase with Codex`
- Tier 3（低頻）：其他治理/案例文章（不阻塞主線）

## 遷移策略

- `claude-code-workspace` 的 `CLAUDE.md`、`.claude/rules/*`、`.claude/settings.json`、hooks 與 skills，已改寫為 Codex 原生的 `AGENTS.md`、`.codex/config.toml`、`.codex/hooks.json`、`.codex/agents/*.toml` 與 `.agents/skills/`。
- Claude 專屬能力，例如 `PreCompact`、`PostCompact`、`InstructionsLoaded`、`autoMemoryEnabled` 與 `SubagentStart/Stop`，不再視為 Codex 的既有能力。
- 官方文件有明確限制的區塊，像是 Hooks 目前仍屬 experimental，且 `PreToolUse` / `PostToolUse` 實際上只保證 Bash matcher，已在本 repo 實作與驗證層同步對齊。

## 官方參考

- [Codex Best practices](https://developers.openai.com/codex/learn/best-practices)
- [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Subagents](https://developers.openai.com/codex/subagents)
- [Skills](https://developers.openai.com/codex/skills)
- [Hooks](https://developers.openai.com/codex/hooks)
- [Models](https://developers.openai.com/codex/models)
- [Config reference](https://developers.openai.com/codex/config-reference)
- [Codex Prompting Guide](https://developers.openai.com/cookbook/examples/gpt-5/codex_prompting_guide)
- [Modernizing your Codebase with Codex](https://developers.openai.com/cookbook/examples/codex/code_modernization)
