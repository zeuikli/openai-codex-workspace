---
name: session-handoff
description: 產出可交接的 session 摘要，讓下一位 Agent 或人類維護者能在最短時間接手。
---

# Session Handoff

## Use when

- 任務需跨班接手、跨 thread 延續，或交由另一位 Agent 續作。
- 改動範圍大，且有未完成事項、風險或待決策項。
- 你即將結束 session，但希望保留高品質上下文。

## Do not use when

- 任務已完整結束且無後續追蹤必要。
- 只有單一小改動，閱讀 diff 即可理解全貌。
- 沒有任何可驗證輸出（未改檔、未執行檢查、無結論）。

## Handoff Template

1. Goal：本輪要達成的目標與範圍。
2. Changes：已完成的核心變更（以結果導向，不列流水帳）。
3. Verification：已執行與未執行的驗證，以及原因。
4. Risks：目前已知風險與影響面。
5. Next Actions：下一位接手者可直接執行的步驟。

## Quality Rules

- 必須標示「已驗證」與「未驗證」項目。
- 對未完成事項提供具體起手點，不留模糊指令。
- 避免貼長篇原始輸出，優先提供可行結論。
