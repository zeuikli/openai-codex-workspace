---
name: multi-mode-skill
description: 明確委派時使用的 Codex orchestration 工作流，在 GPT-5.5 主 thread 與專案 GPT-5.4 multi_mode_agent 間路由 cost、quality、ceiling 或 frontier profile。只有使用者明確要求 multi-mode、delegation、subagent 或平行 agent 工作時使用。一般單 thread 任務不要使用。
---

# Multi-Mode 工作流

## 不變式

- 主 thread 固定使用 `gpt-5.5`；custom worker 固定使用 `gpt-5.4`。
- Profile 只改變工作與驗證強度，不改變模型身分。
- 不宣稱能在執行中的 thread 內切換模型。
- 使用者未明確要求 agent、委派或平行工作時不 spawn。
- 最終決策與驗收保留在主 thread。

## 選擇 Profile

| Profile | 用途 |
| --- | --- |
| `cost` | 最小化 context 與修改；執行一項關鍵測試及一項結構檢查 |
| `quality` | 保留 decision log、審查完整 diff，檢查 correctness、security、regression、maintainability 與 tests |
| `ceiling` | 至少比較兩個替代方案、標示 Control/Agency/Runtime，提供 rollback 或 containment |
| `frontier` | 建立 baseline、使用兩種獨立驗證、檢查 scope drift，記錄 rejected claims |

完整規則分別見 `chatgpt-fast-pilot`、`chatgpt-balanced-pilot`、`chatgpt-deep-pilot` 與 `chatgpt-frontier-pilot`。模型選擇只適用新 thread 或明確設定的 agent；profile 不會改變目前 thread 的模型。

## 委派

1. 定義 Goal、non-goals、允許路徑、限制與可執行 Done when。
2. 選出一個可獨立驗證且不重疊寫入的工作單元。
3. 建立 JSON task envelope，至少包含 `profile`、`profile_contract`、`goal`、`non_goals`、`allowed_paths` 與 `verification`。
4. Spawn 前執行 `python3 .agents/skills/multi-mode-skill/scripts/validate_task.py <task.json>`；exit `2` 時停止，不得委派。
5. 驗證通過後，將 envelope 內容轉成 prompt 的 `PROFILE`、`PROFILE_CONTRACT`、Goal、non-goals、paths 與驗證命令，再 spawn `multi_mode_agent`。
6. 要求回報 scope、changes、evidence、open questions 與 residual risk。
7. 主 thread 重跑關鍵驗證。

不得直接叫用 `multi_mode_agent`，也不得只傳 profile label。完整 task envelope 是 mechanical gate；worker 的自然語言自檢不能取代它。

最多使用 config 設定的四個 concurrent threads，不要求 nested delegation。

## 長任務

Checkpoint 必須包含 Goal、已完成、驗證、風險與下一步。只有使用者明確要求排程或 recurring execution 時才建立 Codex automation；不輸出不支援的排程指令。

## 輸出

依序回覆：所選 profile、worker scope/result、主 thread 驗證、未完成風險。
