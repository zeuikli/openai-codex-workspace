# Claude Code Workspace → OpenAI Codex Workspace 遷移指南

這份文件的目的不是逐字搬運 `claude-code-workspace`，而是把可保留的工作方法，依照 OpenAI 官方 Codex 文件重新落地到 `openai-codex-workspace`。

## 一級來源

以下是本文件採用的官方規範來源：

- `AGENTS.md` 載入、覆寫與 fallback：<https://developers.openai.com/codex/guides/agents-md>
- Codex 整體最佳實踐：<https://developers.openai.com/codex/learn/best-practices>
- Customization 的建議建置順序：<https://developers.openai.com/codex/concepts/customization#next-step>
- Skills 結構、目錄與 progressive disclosure：<https://developers.openai.com/codex/concepts/customization#skills>
- Subagents 的啟用方式、限制與自訂 agent schema：<https://developers.openai.com/codex/subagents>
- Hooks 的事件模型與限制：<https://developers.openai.com/codex/hooks>
- `.codex/config.toml` 支援欄位：<https://developers.openai.com/codex/config-reference#configtoml>

## 遷移基線

原始參考樣本：

- 指定遷移說明：`claude/karpathy-optimization-merged/docs/codex-migration-guide.md`
- 行為基線：`claude-code-workspace` `main` 分支的 `CLAUDE.md`、`.claude/rules/*`、`.claude/settings.json`、`.claude/hooks/*`

本 repo 採用的做法是：

1. 保留工作流意圖
2. 以 Codex 官方術語與能力重寫
3. 將 Claude 專屬事件明確排除
4. 將可重複流程收斂到 `AGENTS.md`、skills、custom agents、hooks 與驗證腳本

## 遷移對照表

| Claude 結構 | Codex 對應 | 狀態 | 說明 |
| --- | --- | --- | --- |
| `CLAUDE.md` | `AGENTS.md` | 已採用 | 依官方建議改為 repo 級持久規範 |
| `.claude/rules/*.md` | `AGENTS.md` + `AGENTS.full.md` | 已採用 | 模組化規則改為可執行段落與補充文件 |
| `.claude/settings.json` | `.codex/config.toml` | 已採用 | 依官方 `config.toml` schema 改寫 |
| `.claude/agents/*.md` | `.codex/agents/*.toml` | 已採用 | 每個 agent 一個 TOML 檔，欄位對齊官方 schema |
| `.claude/skills/*` | `.agents/skills/*` | 已採用 | 依 Skills 結構與 progressive disclosure 重寫 |
| `SessionStart` / `UserPromptSubmit` / `Stop` hooks | `.codex/hooks.json` + `.codex/hooks/*.sh` | 部分採用 | 只保留 Codex 有明確支援的事件 |
| `PreToolUse:Bash` / `PostToolUse:Bash` | `.codex/hooks.json` + hook scripts | 已採用 | 依官方限制，僅以 Bash matcher 實作 |
| `PreCompact` / `PostCompact` | 無直接對應 | 不採用 | 屬 Claude 專屬壓縮生命週期 |
| `InstructionsLoaded` | 無直接對應 | 不採用 | Codex hooks 無此事件 |
| `SubagentStart` / `SubagentStop` | 無官方穩定事件 | 不採用 | 官方文件未列為可依賴事件 |
| `autoMemoryEnabled` | 不直接對應 repo 設定 | 不採用 | Codex 不用這個 Claude 專屬設定鍵 |

## 目前 openai-codex-workspace 的實作原則

### 1. `AGENTS.md` 是主要治理入口

依官方最佳實踐，`AGENTS.md` 應保持短、準、可執行，描述：

- repo layout
- build / test / lint 命令
- 工程規範與 PR expectations
- do-not rules
- `Done when`

所以目前 repo 採兩層做法：

- `AGENTS.md`：精簡可執行規範
- `AGENTS.full.md`：較完整的補充規範

### 2. Skills 採 repo 級 `.agents/skills`

依官方 Customization 文件，skills 是比長 prompt 更適合承載可重複工作流的單位，且採 progressive disclosure：

- 先載入 metadata
- 被選到才讀 `SKILL.md`
- 需要時才讀 references 或執行 scripts

因此目前 repo 的流程型規範，以 skills 承載：

- `multi-agent-collaboration`
- `deep-review`
- `docs-drift-check`
- `karpathy-loop`
- `session-handoff`
- 其他專案工作流 skills

### 3. Subagents 只在明確需求或可平行拆分時啟用

官方 `subagents` 文件明確指出：Codex 只會在使用者明確要求時才 spawn subagent，而且 token 成本與執行開銷會提高。

因此目前 repo 的規則不是「所有能委派都強制委派」，而是：

- 明確要求平行化時才用
- 探索、實作、審查這三類角色保持分工
- 預設 `max_depth = 1`，避免遞迴 fan-out

### 4. Hooks 視為實驗性輔助，不作唯一依賴

官方 Hooks 文件明確標示：

- hooks 仍在 active development
- Windows 暫不支援
- `PreToolUse` / `PostToolUse` 目前只保證 Bash matcher

因此本 repo 採用的 hook 原則是：

- 用來做 guardrail 與額外提示
- 不把核心規範只放在 hook
- 所有 hook 限制都要在 `AGENTS.md` 與驗證腳本中有對應

### 5. `.codex/config.toml` 僅使用官方支援欄位

與 Claude 的 JSON 設定不同，Codex 的 repo 級設定應放在 `.codex/config.toml`。

目前 repo 採用的重點欄位：

- `model`
- `approval_policy`
- `sandbox_mode`
- `[features]`
- `[agents]`
- `[agents.<name>]`

這些都以官方 `config-reference` 為準，不保留 Claude 專屬鍵。

## 不直接移植的項目

以下內容在 `claude-code-workspace` 裡有價值，但不直接視為 Codex 內建能力：

### 1. Claude 專屬 Hook 事件

- `InstructionsLoaded`
- `PreCompact`
- `PostCompact`
- `SubagentStart`
- `SubagentStop`

理由：

- OpenAI 官方 hooks 文件沒有把這些列為目前可依賴事件
- 直接移植會造成 repo 規範與實際平台能力不一致

### 2. 強制把所有可委派任務都交給 subagents

理由：

- 官方 `subagents` 文件明確說明只有在明確要求時才會 spawn
- 若將這件事寫成硬性規範，會和 Codex 的真實執行模型產生摩擦

### 3. Claude 的 Auto Memory 設定鍵

理由：

- `autoMemoryEnabled` 是 Claude 設定鍵，不是 Codex 的 repo 級設定欄位
- Codex 端目前應以官方 `AGENTS.md`、config、skills、hooks 與 session 管理策略為主

## 建議維護順序

依官方 Customization 的建議順序，後續治理請固定照以下順序進行：

1. `AGENTS.md`
2. skills
3. MCP
4. subagents

這代表：

- 先把 repo 規範寫清楚
- 再把重複流程變成 skills
- 外部資訊需求再透過 MCP 補
- 真正需要委派時才強化 subagents

## 本 repo 目前已對齊的重點

- `AGENTS.md` 與 `AGENTS.full.md` 已改為 Codex 原生結構
- `.codex/config.toml` 已採 TOML 與官方 schema
- `.codex/agents/*.toml` 已採自訂 agent 檔案模式
- `.agents/skills/` 已承載可重複工作流
- `.codex/hooks.json` 與 hooks scripts 已限制在官方可依賴的事件範圍
- `scripts/validate_codex_workspace.py` 會持續檢查 repo 不要回滲 `CLAUDE.md`、`.claude/` 等非 Codex artifact

## 後續建議

1. 持續把 repo 說明中的每個關鍵治理規則，對應回官方 Codex 文件。
2. 若官方 hooks 或 skills 文件更新，優先更新 `docs-drift-check` skill 與 `docs/codex-migration-guide.md`。
3. 有新增工作流時，先問自己它應該落在：
   - `AGENTS.md`
   - skill
   - MCP
   - custom agent
   - automation

不要直接照 Claude 的舊目錄結構加檔。
