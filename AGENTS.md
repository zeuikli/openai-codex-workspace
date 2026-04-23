# AGENTS.md (Team Compact)

## 語言

- 中文一律回覆台灣繁體中文。
- 英文需求以英文回覆。

## 回覆原則

- 先結論，後證據與風險。
- 回覆至少包含：變更摘要、驗證狀態、未完成風險。

## Caveman 自動選擇（硬性守則）

**CAVEMAN AUTO-LEVEL 常態啟用**。根據 prompt 特徵自動選擇等級，靜默切換，不宣告：
- `lite`：簡單問答、確認、定義、單行回覆
- `full`：技術解釋、debug、code review、多步驟程序（**預設**）
- `ultra`：摘要請求、批次操作、多檔任務、「簡短說」、大型工具迴圈
- **關閉**：安全警告、不可逆操作（delete/drop/rm -rf）、用戶要求釐清時

所有等級：去掉 pleasantries/hedging/filler。技術術語精確。程式碼不更動。


## 任務四要素（預設補齊）

- Goal：要達成的結果。
- Context：相關檔案/錯誤/路徑。
- Constraints：不可違反的限制。
- Done when：可驗收條件。

## 執行順序

1. 啟動固定先讀：`AGENTS.md`、`Memory.md`、`prompts.md`。
2. 再讀與任務直接相關的程式與設定檔。
3. `SKILL.md` 採按需載入：只讀與當前任務直接相關的 skill，禁止全量預讀。
4. 文檔查證預設優先交由 `docs_researcher`（`gpt-5.4-mini`）；只有在多文件衝突、規格不一致或高風險決策時才升級 `gpt-5.4`。
5. 若任務涉及 Codex 規範、Claude → Codex 遷移、hooks、skills、subagents 或官方能力判讀，優先查 `docs/codex-migration-guide.md` 與 OpenAI 官方文件。
6. 長任務每完成一個里程碑要做一次上下文摘要，避免重複回灌舊上下文。
7. 複雜任務先規劃，再實作。
8. 先做最小可驗證修改，再擴大範圍。
9. 除非被阻塞，不以「只給計畫」結束回合。

## Rollout 溝通

- 避免要求模型在實作前輸出冗長 preamble 或 upfront plan。
- 中途進度更新保持精簡且與風險相關，避免干擾實作連續性。

## Agent 任務邊界（Anti-timeout）

- ❌ 不指派單一 Agent 產生超過 200 行文件（長文件改由主 Agent 分段產出）。
- ❌ 不在同一個 Agent 任務同時要求「大量生成寫作」與「git 提交/推送」。
- ✅ Agent 優先處理：探索、搜尋、平行讀取、最小程式修改與可驗證修補。
- ✅ 任務預估上限：工具呼叫 < 20 次、輸出 < 500 tokens；超出就拆子任務。

## Session Repo 限制

- 每個 session 預設只綁定啟動時的單一 repository。
- 需要跨 repo（fork / cross-repo push）時，必須在目標 repo 開新 session。
- 替代方案：先在同 repo 建立隔離分支（`codex/*` 或 `feature/*`）完成實驗。

## 背景 Agent 管理原則

- 指派背景 Agent 前，先 commit + push 目前變更，避免 stop hook 誤判未提交狀態。
- 指派後立即回報：任務內容、預估時間、失敗通知方式。
- 逾 5 分鐘未回報進度時，主 Agent 必須主動檢查狀態與是否接手。
- 發生逾時/錯誤時必須立即告知，不得靜默略過。

## Cookbook 分層調用（頻率 x 實用性）

- `Tier 1`（高頻，高實用）：`Codex Prompting Guide`
  - 直接行動、端到端完成、工具優先、平行讀取、`apply_patch` 優先單檔編輯。
- `Tier 2`（中頻，高實用）：`Modernizing your Codebase with Codex`
  - 大型改造時採分階段產物（計畫、設計、驗證、對比測試）與持續更新執行計畫。
- `Tier 3`（低頻，中實用）：Cookbook 治理/追蹤型文章
  - 用於流程治理、漂移檢查與週期性優化，不阻塞主線交付。

## 模型與分工

- 三層分派：
  `Layer 1` 輕量高頻/讀多寫少：`gpt-5.4-mini`
  `Layer 2` 主線交付/一般實作：`gpt-5.4`
  `Layer 3` 複雜工程/測試/審查/安全收斂：`gpt-5.3-codex`
- 預設：`gpt-5.4`
- 文檔查證預設：`gpt-5.4-mini`，僅在多文件衝突、規格不一致或高風險決策時升級 `gpt-5.4`。
- subagents 只在明確要求或可平行拆分時使用。
- 日常高頻任務：主 Agent 用 `gpt-5.4` 搭配 `medium` reasoning。
- 架構盤點、文件查證、成本分析、handoff：優先用 `gpt-5.4-mini` 搭配 `medium` reasoning。
- 純實作、測試補強、code review、安全審查：優先用 `gpt-5.3-codex`。
- 全面審查與整體優化：主 Agent 用 `gpt-5.4` 搭配 `high` reasoning。
- 最終驗收或高風險決策：主 Agent 用 `gpt-5.4` 搭配 `xhigh` reasoning；工程細節交 `gpt-5.3-codex` 複核。
- 非預設且不建議納入主路由：`gpt-5.4-nano`、`gpt-5.1-codex`、`gpt-5.1-codex-mini`、`gpt-5.1-codex-max`、`gpt-5.2-codex`

## 驗證閉環（必做）

- 依任務執行最小必要驗證：test/lint/type/build。
- 若無法驗證，必須寫明原因、風險、補驗方式。
- 完成時回對 `Done when` 逐項確認。
- 計畫中的項目在收尾時必須標記為：Done / Blocked / Cancelled。

## Karpathy 實作原則（硬性條款）

> 完整內容：`docs/karpathy-codex-principles.md`。

1. Assumption Ledger：每條假設都要附檢驗方式；驗證不了就先澄清。
2. Surface, Don't Swallow：規格/程式碼衝突必須顯化，不挑邊硬上。
3. Pushback Over Sycophancy：指令違規先反駁；禁止空洞「已完成」結尾。
4. Naive-First, Optimize-Second：先寫正確樸素版 → 補測試 → 才優化。
5. Success-Criteria First：先把需求改寫為可驗證 `Done when`，條件齊了才動手。
6. Tenacity Loop：可自動驗證的任務進 loop，預設 5 輪 / 10 分鐘上限。
7. Minimal Blast Radius：只改相關檔案；看不懂的註解/死碼記為 `Followup`。
8. Anti-Bloat：抽象/參數/選項預設不加；超出預估 2 倍要自問「能不能 1/10 行」。
9. Generation vs Discrimination：重大變更必經 `reviewer` / `security_reviewer`，不得自寫自審自過。

## 結構邊界

- `AGENTS.md`：持久規範（短、準、可執行）。
- `AGENTS.full.md`：完整治理規範與補充說明。
- `.agents/skills/`：可重用 workflow。
- `.codex/agents/*.toml`：custom agents 定義。
- `docs/codex-migration-guide.md`：Claude → Codex 遷移判讀與不適用清單。
- Automations：排程單位。
- Hooks 為 experimental，不作唯一核心依賴。

## 官方對齊規則

- `AGENTS.md` 應保持實用、精簡、可驗證；若規範變得太長，改把細節轉移到補充文件或 skill。
- Skills 使用 `.agents/skills`，並遵循 progressive disclosure：先 metadata、再 `SKILL.md`、最後才讀 references 或 scripts。
- Hooks 目前只把 `PreToolUse` / `PostToolUse` 視為 Bash matcher guardrail，不假設 Claude 專屬事件存在。
- Subagents 只在使用者明確要求或任務可平行拆分時啟用，不把「所有能委派都先委派」寫成硬規則。

## 長任務管理

- 一個 thread 聚焦一個工作單元。
- 真分岔再 fork。
- 每個里程碑結束時輸出「短摘要」：目前結論、已驗證、剩餘風險、下一步。
- 任務結束更新 `Memory.md`：完成事項、決策、待辦、驗證狀態。

---

完整版規範：`AGENTS.full.md`
