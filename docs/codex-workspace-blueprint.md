# ChatGPT Codex Workspace 遷移 / 維護 / 發布藍圖

> 文件用途：可直接執行的 Codex workspace 遷移與維護藍圖。更新基準：2026-04-13。

## A. 目標與範圍

本藍圖用於把既有工作區內容改造成可長期運作的 ChatGPT Codex workspace，並確保以下規範落地：

- 以 `gpt-5.4` 作為預設起手模型。
- 以 `gpt-5.4-mini` 承接輕量與可平行子任務。
- 以 `gpt-5.3-codex` 承接複雜軟體工程與 cloud-friendly coding。
- subagents 僅在「明確要求」或「高度可平行」時啟用。
- automations 視為 Codex app 背景排程能力，不等同本地 cron 腳本。
- hooks 視為 experimental，且目前 `PreToolUse` / `PostToolUse` 只攔 Bash。
- skills 是作者編寫格式，作為本 repo 的唯一可重用流程資產。

## B. 三階段遷移策略

### Phase 1：規範落地（Foundation）

1. 清理舊工具耦合字詞，統一改為 Codex 名詞體系。
2. 建立模型分派準則（主 Agent、探索 worker、工程 worker）。
3. 釐清 AGENTS 與 Skills 的責任邊界：
   - `AGENTS.md` 管全域/目錄規範。
   - `SKILL.md` 管可重用流程。

### Phase 2：可運維化（Operations）

1. 補齊標準驗證流程：測試、lint、型別、必要人工檢視。
2. 建立 subagent 啟動門檻與回報模板，避免濫開平行 worker。
3. 針對高頻任務定義 skills，先在本地驗證再考慮外發。
4. 需要固定追蹤時，再以 automations 建立背景排程。

### Phase 3：可發佈化（Release）

1. 定義版本節奏：`draft -> internal -> stable`。
2. 發布前執行一次主 Agent 最終審閱：
   - 規範一致性
   - 風險揭露完整度
   - 驗證紀錄完整度

## C. 維護節奏（Maintenance Cadence）

- 每週：更新模型分派建議與常見失敗案例。
- 每雙週：檢查 skills 觸發描述是否仍準確。
- 每月：審查 hooks 與 automations 是否仍符合最新安全邊界。
- 每次大改版：重新驗證 `gpt-5.4` / `gpt-5.4-mini` / `gpt-5.3-codex` 任務對照。

## D. 發布前檢查清單（Go / No-Go）

1. 文件是否明確標註目前官方行為與限制（尤其 hooks、subagents）？
2. 是否避免把 experimental 能力描述成穩定承諾？
3. subagents 是否只有在可平行且有明確邊界時才被建議使用？
4. 是否有明確指出 skills 的作者與維護責任邊界？
5. 是否保留必要驗證步驟與未驗證風險聲明？

## E. 交付物定義

每次遷移或維護工作，至少輸出：

- `變更摘要`：改了什麼、為何要改。
- `模型分派紀錄`：哪些任務由哪個模型處理。
- `驗證結果`：已做/未做項目與原因。
- `風險清單`：主 Agent 後續需追蹤的議題。

## F. 給主 Agent 的整合建議

- 把本藍圖視為治理層文件，不放具體實作細節。
- 實作細節請下沉到對應 skill 或任務文件。
- 若發現官方規範變動，先更新本藍圖，再分派各文件同步修訂。
