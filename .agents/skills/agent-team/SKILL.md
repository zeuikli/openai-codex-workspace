---
name: agent-team
description: 將大型任務拆成可平行執行的子任務，由主 Agent 協調多個 subagents 並收斂結果。
---

# Agent Team

## Use when

- 任務可切成多個互不重疊的模組或責任區。
- 你需要同時做探索、實作、測試與審查。
- 你希望用平行分工縮短整體交付時間。

## Do not use when

- 任務非常小，拆分成本高於收益。
- 多個 worker 必須同時改同一檔案。
- 完成條件與驗證方式尚未定義清楚。

## Workflow

1. 主 Agent 先定義目標、邊界、驗證門檻。
2. 依「不重疊寫入範圍」拆工。
3. 每個 subagent 固定回報：範圍、發現、建議、證據、驗證狀態。
4. 主 Agent 收斂衝突並做最終驗證。

## Quality Gate

- 任一 subagent 未驗證完成，主 Agent 不宣告完成。
- 發現衝突時回到規格與證據，不以直覺決策。
