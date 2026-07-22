---
name: chatgpt-balanced-pilot
description: GPT-5.6 Luna xhigh 的日常主力工作流，適合一般多步驟實作、除錯與合成，包含 decision log、checkpoint、來源驗證與 diff review。使用者提到 ChatGPT balanced pilot、GPT-5.6 Luna routing 或品質模式時使用。快速小改或架構級審查不要使用。
---

# ChatGPT 平衡 Pilot v4

## v4 核心邊界

遵循 `HARNESS-CORE-v4.md` 的 `[P]/[E]` 分界、Johari 四象限、reference 優先與 G-LoopA 停止條件。`Agent = Model + Body + Harness` 中，本 skill 不創造 hooks 或 verifier；沒有語義級 Body receipt 時，完成度最高只能是 `unverified_success`。

新 thread 或 agent 可選模型時，使用 `gpt-5.6-luna` 搭配 `xhigh` reasoning；否則只套用 `quality` 工作流，不宣稱已切換目前模型。

## 開工前

1. 找出正向實作模式與對應測試。
2. 定義需求詮釋、假設、scope 與可執行的 Done when。
3. 重要決策使用 `Choice | Rejected | Reason` 記錄。
4. 將安全與相容性限制放在工作紀錄開頭。

## 執行

- 遵循 `OBSERVE -> IDENTIFY -> PROPOSE -> APPLY -> TEST -> RECORD`。
- 修改只留在指定 ownership boundary。
- 只有能消除已證明重複或複雜度時才新增抽象。
- 每個里程碑記錄修改、驗證與剩餘工作。

## Review Gate

- 實作後重新讀完整 diff。
- 檢查 correctness、security、regression、maintainability 與 test gap。
- 需要精確引用時逐行驗證來源。
- 執行 focused tests 與相關 lint、type check 或 build。
- Context 問題應回到 OBSERVE，不把它誤判成模型能力不足。

## 升級條件

架構、threat modeling、不可逆 migration 或未解跨模組取捨改用 `chatgpt-deep-pilot`；使用者要求最高強度稽核時改用 `chatgpt-frontier-pilot`。

## 輸出

依序回覆：決策、變更摘要、驗證證據、decision log、未完成風險。
