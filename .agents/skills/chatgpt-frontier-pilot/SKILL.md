---
name: chatgpt-frontier-pilot
description: GPT-5.6 Sol high 的最高強度稽核與優化工作流，包含 trace-first diagnosis、對抗式檢查與兩種獨立驗證。使用者提到 ChatGPT frontier pilot、GPT-5.6 Sol high、最強稽核或全面優化時使用。例行程式修改或快速小改不要使用。
---

# ChatGPT Frontier Pilot

新 thread 可選模型時，使用 `gpt-5.6-sol` 搭配 `high` reasoning；極端複雜才在新任務中評估 `xhigh` 或 `max`。否則只套用 `frontier` 工作流，不宣稱已切換目前模型。

## 執行契約

1. 讀取 `AGENTS.md`、`HARNESS-THE-LOOP.md`、目標、caller、測試與目前 diff。
2. 修改前建立可量測 baseline。
3. 定義成功條件與能推翻成功宣稱的證據。
4. 一次只做一個有邊界的變更。
5. 使用兩種獨立方法驗證，例如 focused test 加結構檢查。
6. 最終結果記錄被推翻宣稱與未完成風險。

## 稽核模式

- 以精確檔案與行號指出矛盾。
- 分開目前證據、歷史報告與模型記憶。
- 採信重大 finding 前重跑其依據命令。
- 將被目前檔案推翻的 finding 記入 rejected-claims ledger。
- 刪除只提出建議；破壞性變更仍需明確授權。

## 優化模式

- 先記錄 metric 與 baseline。
- 依 `change -> measure -> keep or discard` 迭代。
- 降低 bytes、tokens 或 latency 前先保住 correctness 與 mechanical checks。
- 無法量測改善或下一步提高風險時停止。

## 驗證紀律

- Agent 或工具摘要在主 thread 驗證 artifact 前都只是未驗證證據。
- 檢查 `git diff` 是否 scope drift 或弱化測試。
- 相同輸入與狀態下重複同一命令三次，應診斷而非繼續重試。
- 三次有證據的失敗後停止並重新 framing，不誇大完成度。

## 輸出

依序回覆：結論、baseline、變更、驗證證據、rejected claims、未完成風險。
