# AGENTS.md (Team Compact)

## 語言

- 中文一律回覆台灣繁體中文。
- 英文需求以英文回覆。

## 回覆原則

- 先結論，後證據與風險。
- 回覆至少包含：變更摘要、驗證狀態、未完成風險。

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
5. 長任務每完成一個里程碑要做一次上下文摘要，避免重複回灌舊上下文。
6. 複雜任務先規劃，再實作。
7. 先做最小可驗證修改，再擴大範圍。
8. 除非被阻塞，不以「只給計畫」結束回合。

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

- 預設：`gpt-5.4`
- 輕量探索/摘要：`gpt-5.4-mini`
- 複雜工程/深度審查：`gpt-5.3-codex`
- 文檔查證預設：`gpt-5.4-mini`，僅在必要時升級 `gpt-5.4`。
- subagents 只在明確要求或可平行拆分時使用。
- 全面審查與整體優化：主 Agent 用 `gpt-5.4` 搭配 `high` reasoning。
- 最終驗收或高風險收斂：主 Agent 用 `gpt-5.4` 搭配 `xhigh` reasoning。
- 日常高頻任務：主 Agent 用 `gpt-5.4` 搭配 `medium` reasoning。
- 架構盤點與文件查證：`gpt-5.4-mini` 搭配 `medium` reasoning。
- 純實作/測試：`gpt-5.3-codex` 搭配 `medium` reasoning。
- 深度 code review / security review：`gpt-5.3-codex` 搭配 `high` reasoning。

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
- `.agents/skills/`：可重用 workflow。
- `.codex/agents/*.toml`：custom agents 定義。
- Automations：排程單位。
- Hooks 為 experimental，不作唯一核心依賴。

## 長任務管理

- 一個 thread 聚焦一個工作單元。
- 真分岔再 fork。
- 每個里程碑結束時輸出「短摘要」：目前結論、已驗證、剩餘風險、下一步。
- 任務結束更新 `Memory.md`：完成事項、決策、待辦、驗證狀態。

---

完整版規範：`AGENTS.full.md`
