# ChatGPT Codex Workspace 效能報告（操作版）

> 本報告聚焦「如何讓 Codex 工作更快、更穩、可驗證」，而非模型宣傳。更新基準：2026-04-15。

## 1) 效能定義（Codex 視角）

在 Codex workspace 中，效能不是單看回應速度，而是以下六項同時達標：

1. 任務完成時間（Lead Time）
2. 改動正確率（Correctness）
3. 驗證覆蓋率（Verification Coverage）
4. 上下文污染控制（Context Hygiene）
5. 平行工作衝突率（Parallel Conflict Rate）
6. 可重用程度（Skill Reuse）

## 2) 模型分派與吞吐策略

### 標準分派

- `gpt-5.4`：主 Agent 起手與整合決策。
- `gpt-5.4-mini`：輕量任務、探索型子任務、subagent 掃描與摘要。
- `gpt-5.3-codex`：複雜軟體工程實作、重構、測試修復與 cloud-friendly coding。

### 觀測重點

- 若主 Agent 長期承接大量讀檔與摘要，代表分派失衡。
- 若 `gpt-5.3-codex` 長期被用於 trivial triage，代表成本與吞吐未優化。
- 若 subagents 回傳原始雜訊而非摘要，代表上下文管線失效。

## 3) Skills：把高頻流程從對話變成資產

官方定位是以 skills 作為可重用流程資產。

### 對效能的實際影響

- 正向：
  - 降低每次重新描述流程的提示成本。
  - 提升步驟一致性，減少漏測與漏檢。
- 風險：
  - 描述寫太寬會誤觸發，反而增加迭代回合。
  - 技能久未維護會與現況脫節。

### 建議治理

- 每個 skill 單一職責。
- `description` 必須寫觸發與不觸發邊界。
- 先在本地穩定運作，再擴充 skill 的維護與測試。

## 4) Automations：Codex app 背景排程，不是一般腳本排程

Automations 在 Codex app 背景執行，適合週期性巡檢與追蹤任務。

### 適用場景

- 例行報告（風險盤點、回歸檢查、變更摘要）。
- 重複型檢查（某模組每日健康檢查）。

### 風險與控制

- 背景執行會放大權限設定風險。
- 建議優先使用 workspace-write 與精準 allowlist。
- 排程任務應輸出到可審閱 inbox/triage，而非直接自動發布。

## 5) Hooks：實驗功能，必須保守使用

目前官方狀態：hooks 為 experimental，且 `PreToolUse` / `PostToolUse` 目前只攔 Bash。

### 實務含義

- hooks 不是全面攔截層，不能當作完整安全邊界。
- 對 MCP、Write、WebSearch 等非 Bash 工具不可假設同等可控。
- 適合做 guardrail 與審計補強，不適合做唯一防線。

## 6) 驗證策略：以最小成本取得最大信心

標準順序：

1. 跑最小相關測試。
2. 補跑 lint / type check。
3. 需要時做端到端或人工驗證。
4. 無法驗證時，必須記錄缺口與風險。

### 失敗復盤欄位（建議固定）

- 失敗類型（測試/型別/執行期）
- 根因層級（需求/設計/實作/環境）
- 是否可由 skill 固化避免重演

## 7) 上下文管理：長任務穩定性的核心

### 高效模式

- 主線只保留需求、決策、結論。
- 子線只回傳摘要與證據索引。
- 長任務定期 compact/fork，降低歷史噪訊。

### 反模式

- 把所有命令輸出原封不動貼回主線。
- 多個 subagents 同時改同一寫入區塊。
- 未分層就把整個 repo 背景塞給主模型。

## 8) KPI 建議（給主 Agent 追蹤）

- `首次可用修正時間`（TTFF）
- `一次通過驗證率`
- `回歸缺陷率`
- `subagent 衝突率`
- `skill 重用率`
- `automation 有效訊號率`（有行動價值的執行結果比例）

## 9) 結論

這個 workspace 的效能上限，取決於「分派是否正確」而非「單一模型是否最強」。

- 用 `gpt-5.4` 做主線決策。
- 用 `gpt-5.4-mini` 吃下大量輕量與平行探索。
- 用 `gpt-5.3-codex` 扛複雜工程落地。
- 用 skills 建立可重用流程，用 automations 承接背景週期任務，對 hooks 保持實驗性心態與防呆設計。
