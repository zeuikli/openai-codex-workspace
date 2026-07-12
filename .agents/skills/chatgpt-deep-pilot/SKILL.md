---
name: chatgpt-deep-pilot
description: GPT-5.6 Sol medium 的架構與高風險決策工作流，使用多重假設、Control-Agency-Runtime 分析、明確取捨與對抗式審查。使用者提到 ChatGPT deep pilot、GPT-5.6 Sol、架構審查、threat modeling 或 migration design 時使用。例行實作不要使用。
---

# ChatGPT 深度 Pilot

新 thread 可選模型時，使用 `gpt-5.6-sol` 搭配 `medium` reasoning；否則只套用 `ceiling` 工作流，不宣稱已切換目前模型。

## 建立決策框架

- 定義 decision、non-goals、invariants、stakeholders 與 rollback boundary。
- 選擇方向前建立至少兩個合理假設。
- 將系統議題標為 `Control`（政策）、`Agency`（工具與動作）或 `Runtime`（狀態、觀測與復原）。
- 每個重要選擇以 `Choice | Rejected | Reason` 記錄。

## Reasoning Sandwich

1. Plan：列出依賴、失敗模式與所需證據。
2. Implement：只做最小可回復切片，或產出決策文件。
3. Verify：以反例與確定性檢查挑戰所選方向。

## 審查

- 重建最強的被拒方案，說明它為何不符合目前限制。
- 檢查 security、reliability、operability、maintainability 與 migration risk。
- 分開標示事實、推論與尚未驗證假設。
- 不可逆或 production-facing 工作必須有 rollback 或 containment plan。

## 委派邊界

只有使用者明確要求時才委派。架構、安全決策與最終驗收留在主 thread；只將邊界明確的探索或確定性驗證交給 `multi_mode_agent`。

## 輸出

先給建議，再列替代方案、decision log、證據、rollout/rollback plan 與未完成風險。
