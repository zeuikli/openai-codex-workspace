---
name: deep-review
description: 對變更做深度審查，優先檢查正確性、安全性、回歸風險與測試覆蓋，輸出可執行修正建議。
---

# Deep Review

## Use when

- 準備合併 PR 前，需要高信號的風險審查。
- 修改涉及 auth、payment、資料一致性、並發、檔案系統操作。
- 變更跨多個模組，擔心行為回歸或隱性相依。

## Do not use when

- 只是排版、註解、文案等非功能性小改動。
- 沒有可審查的 diff 或無法取得修改內容。
- 你只需要快速 style feedback，不需要深度風險分析。

## Review Order

1. 正確性：需求是否被正確實作，是否有邊界條件遺漏。
2. 安全性：注入、授權繞過、敏感資訊暴露、危險命令。
3. 回歸風險：既有流程是否被破壞，是否影響相依模組。
4. 測試品質：是否有對應測試、斷言是否有效、失敗案例是否覆蓋。

## Output Format

- Findings（依嚴重度排序）
- 每項包含：`file:line`、問題描述、影響面、修正建議
- Open questions（若有）
- Residual risk（即使修正後仍存在的風險）
