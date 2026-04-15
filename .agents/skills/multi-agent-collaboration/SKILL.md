---
name: multi-agent-collaboration
description: 將任務拆成可平行處理的子任務，指派多個 subagents 並回收結果，由主 Agent 做審閱與合併。
---

# Multi-Agent Collaboration

## Use when

- 任務可被拆成多個互不衝突的模組、目錄或責任區。
- 你需要同時做探索、實作、測試、審查，並縮短整體交付時間。
- 你希望主 Agent 保持小上下文，改由 workers 回報摘要再整合。
- 任務屬於 `Tier 2`（中大型改造、長週期實作）而非單點小修。

## Do not use when

- 任務只有單一檔案或單一步驟，分工成本高於收益。
- 涉及高風險單點變更（例如資料遷移、金鑰輪替）且需要單線控管。
- 需求仍未穩定，拆工後很可能反覆返工。

## Workflow

1. 先由主 Agent 定義共同目標、完成條件、禁止行為與交付格式。
2. 以「檔案範圍不重疊」為優先原則拆工，避免 merge 衝突。
3. 每個 worker 直接執行子任務，不先輸出冗長前置計畫。
4. 每個 worker 回報：變更摘要、檔案清單、驗證結果、未決議題。
5. 主 Agent 只收斂關鍵發現，統一做風險審閱與最後合併。
6. 合併後至少執行一次整體驗證（lint/test/build 或等價檢查）。

## Quality Gate

- 若任一 worker 無法驗證，主 Agent 不得宣告完成。
- 若多 worker 結論衝突，先回到需求與規格再決策，不以直覺選邊。
- 合併摘要必須包含相依關係與後續追蹤項目。
- 任務收尾時，每個子任務都要標記狀態（completed/blocked/cancelled）。
- 若任務實際規模落回 `Tier 1`，應停用平行分工並回到單線處理。
