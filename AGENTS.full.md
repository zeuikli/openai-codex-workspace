# AGENTS.md

## 語言

- 使用者以中文互動時，一律使用台灣繁體中文。
- 使用者以英文互動時，使用英文。

## 回覆格式

- 先給結論，再給證據與風險。
- 回覆至少包含：變更摘要、驗證狀態（已驗證/未驗證）、下一步建議（如有）。

## 任務輸入模板（預設採用）

每次任務都優先補齊以下四項：

- Goal：目標與預期改變。
- Context：相關檔案、錯誤訊息、範例或路徑。
- Constraints：不可違反的規範與邊界。
- Done when：完成條件與驗收方式。

## 啟動順序

- 固定啟動載入：`AGENTS.md`、`Memory.md`、`prompts.md`。
- 再讀與任務直接相關的檔案，不憑印象改動。
- `SKILL.md` 僅按需載入：只載入當前任務需要的 skill，避免全量預讀。
- 涉及 Codex 規範、Claude → Codex 遷移、hooks、skills、subagents 或 config 能力判讀時，優先讀 `docs/codex-migration-guide.md` 與 OpenAI 官方文件。
- 需求不清時先澄清，再實作。
- 預設採「先執行再回報」：除非任務本質是規劃題，避免只停在分析。

## 規劃優先

- 複雜、模糊、多步驟任務先規劃（可用 `/plan`）。
- 任務有高風險或跨模組影響時，先列分步計畫與檢查點，再動手改。
- 規劃不是終點：有明確可做步驟時要直接進入實作與驗證。

## Rollout 與中途訊息

- 避免強制模型在 rollout 前提供冗長 preamble、upfront plan 或重複承諾，這會降低執行效率。
- 中途訊息以「現在在做什麼、為何要做、是否遇到阻塞」為核心，保持精簡。
- 若無阻塞，不以「待你確認計畫」作為預設結尾。

## Cookbook 導向調用分層（頻率 x 實用性）

### Tier 1：預設啟用（高頻 + 高實用）

來源：`Codex Prompting Guide`  
規則：
- 預設直接執行，不停在分析或提案階段。
- 優先使用結構化工具與最小可驗證修改。
- 讀取/盤點可平行就平行，縮短等待。
- `update_plan` 僅保留執行必要步驟，收尾必須閉環。

### Tier 2：條件啟用（中頻 + 高實用）

來源：`Modernizing your Codebase with Codex`  
觸發條件：
- 任務跨多模組、涉及遷移或長週期重構。
- 需要多階段產物與 parity 驗證。
執行方式：
- 以「階段 + 產物」管理（計畫、盤點、設計、驗證、測試）。
- 每階段後更新執行計畫與驗證狀態，避免文件與實作漂移。

### Tier 3：按需啟用（低頻 + 中實用）

來源：Cookbook 治理型文章與案例。  
用途：
- 週期性治理（規範漂移、成本/流程回顧）。
- 不得阻塞主線交付，僅在明確需求或排程任務時執行。

## 模型與代理策略

- 預設用 `gpt-5.4`。
- 讀多寫少、快速探索與摘要優先用 `gpt-5.4-mini`。
- 文檔查證預設使用 `docs_researcher`（`gpt-5.4-mini`）；僅在規格衝突、證據不足或高風險決策時升級 `gpt-5.4`。
- 複雜工程、測試補強、深度審查與安全審查優先用 `gpt-5.3-codex`。
- 只有在明確要求或任務可平行拆分時才啟用 subagents。

### 建議配置

- 日常任務：主 Agent 用 `gpt-5.4` + `medium` reasoning。
- 全面審查、跨檔案治理、整體優化：主 Agent 用 `gpt-5.4` + `high` reasoning。
- 最終驗收、高風險決策、安全或規範衝突收斂：主 Agent 用 `gpt-5.4` + `xhigh` reasoning；工程細節可交 `gpt-5.3-codex` 複核。
- 架構盤點、文件查證、成本分析、handoff：優先用 `gpt-5.4-mini` + `medium` reasoning。
- 純實作與測試補強：優先用 `gpt-5.3-codex` + `medium` reasoning。
- 深度 review 與 security review：優先用 `gpt-5.3-codex` + `high` reasoning。

### 分流原則

- 跨模組決策與最後收斂交給 `gpt-5.4`。
- 高頻讀取、盤點、整理與子任務交給 `gpt-5.4-mini`。
- 主線工程實作、測試補強、深度 review 與 security review 交給 `gpt-5.3-codex`。
- `gpt-5.4-nano`、`gpt-5.1-codex`、`gpt-5.1-codex-mini`、`gpt-5.1-codex-max`、`gpt-5.2-codex` 不納入目前預設主路由。
- 若成本壓力高，先優化上下文載入與摘要節奏，再降低模型或 reasoning。

## 結構邊界

- `AGENTS.md`：持久規範（短、準、可執行）。
- `.agents/skills/`：可重用工作流（每個 skill 聚焦一件事）。
- `.codex/agents/*.toml`：custom agents（每檔一個 agent）。
- `docs/codex-migration-guide.md`：Claude 設計如何落到 Codex、以及哪些功能不直接對應。
- Automations：Codex app 背景排程（先手動穩定再排程）。
- `.codex/hooks.json`：experimental（可輔助，不作唯一核心依賴）。

## 實作原則

- 只改與需求直接相關檔案，避免順手大重構。
- 不回退他人既有變更；衝突時採最小差異整合。
- 先做最小可驗證變更，再擴大範圍。
- 先用結構化工具完成檔案操作（例如 `apply_patch`），再用 shell 補足驗證或批次動作。
- 讀取階段優先平行化（多檔搜尋/比對/盤點），降低單線等待時間。

## Karpathy 實作原則（2026 導入）

> 完整內容：`docs/karpathy-codex-principles.md`。以下為硬性條款。

1. **Assumption Ledger**：推測性決策必須寫成假設並附檢驗方式；無法檢驗就改成澄清問題，不得硬上。
2. **Surface, Don't Swallow**：文件或程式碼衝突先顯化兩版本並附建議與風險，不挑一邊硬做。
3. **Pushback Over Sycophancy**：指令與規範/測試/風險牴觸時先反駁再動手；禁止空洞「已完成」結尾。
4. **Naive-First, Optimize-Second**：先寫幾乎一定正確的樸素版 → 補正確性測試 → 才優化；優化每步要重跑測試。
5. **Success-Criteria First**：接到任務先把需求改寫為可執行的 `Done when`；條件不齊時先補，不先實作。
6. **Tenacity Loop**：可自動驗證的任務建立 reproducible 指令自動 loop，預設 5 輪或 10 分鐘上限，超過則升級 reasoning 或回報。
7. **Minimal Blast Radius**：只改相關檔案；看不懂的註解、死程式碼、測試先記為 `Followup`，不得擅自刪改。
8. **Anti-Bloat**：抽象/參數/選項的預設答案是不要加；實作超出預估複雜度 2 倍要自問「有沒有 1/10 行的做法」並於回覆中記錄。
9. **Generation vs Discrimination**：單一 Agent 不得自寫自審自過重大變更；跨模組或高風險變更必經 `reviewer` / `security_reviewer`。

## 驗證閉環

- 要求並執行必要驗證：測試、lint、type check、build（按任務最小集合）。
- 若不能執行，必須明確寫出：未執行原因、風險、補驗方式。
- 完成時確認結果是否符合 `Done when`。
- 任何計畫項目在收尾前都要落到狀態：`completed`、`blocked` 或 `cancelled`。

## 技能與自動化

- 重複流程先做成 Skill。
- Skill 穩定後再做 Automation（技能定義方法，自動化定義排程）。

## 長任務管理

- 一個 thread 聚焦一個工作單元。
- 真正分岔才 fork。
- 每完成一個里程碑即輸出短摘要（結論、已驗證、風險、下一步），避免重複貼回完整舊上下文。
- 大型任務結束時更新 `Memory.md`：完成事項、關鍵決策、待辦、驗證狀態。
