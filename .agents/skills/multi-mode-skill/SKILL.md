---
name: multi-mode-skill
description: 明確委派且具名效益成立時使用的 Codex orchestration 工作流，以受限 route ID 路由 GPT-5.6 Luna、Terra 或 Sol agent，並機械驗證 profile、model、effort、path 與 verifier。只有使用者明確要求 multi-mode、delegation、subagent 或平行 agent 工作時使用。一般單 thread 任務不要使用。
---

# Multi-Mode 工作流

## 不變式

- 主 thread 預設使用 `gpt-5.6-luna` + `xhigh`；這是 provisional 日常預設，不是已量測最優解。
- Profile 只描述工作與驗證強度；route 才解析新 agent 的模型身分，不改變執行中的主 thread。
- 不宣稱能在執行中的 thread 內切換模型。
- 使用者未明確要求 agent、委派或平行工作時不 spawn。
- 即使使用者明確要求，也必須先通過 benefit-gated 檢查：具名效益需是 context 隔離、真平行、對抗審查、低風險大量機械執行或降低主線噪音。
- Worker 自報成功一律是 `unverified_success` 中間態。
- 最終決策與驗收保留在主 thread。

## 選擇 Profile

| Profile | 用途 |
| --- | --- |
| `cost` | 最小化 context 與修改；執行一項關鍵測試及一項結構檢查 |
| `quality` | 保留 decision log、審查完整 diff，檢查 correctness、security、regression、maintainability 與 tests |
| `ceiling` | 至少比較兩個替代方案、標示 Control/Agency/Runtime，提供 rollback 或 containment |
| `frontier` | 建立 baseline、使用兩種獨立驗證、檢查 scope drift，記錄 rejected claims |

完整規則分別見 `chatgpt-fast-pilot`、`chatgpt-balanced-pilot`、`chatgpt-deep-pilot` 與 `chatgpt-frontier-pilot`。模型選擇只適用新 thread 或明確設定的 agent；profile 不會改變目前 thread 的模型。

GPT-5.6 escalation：微小變更可走 `cost_write` 的 Luna medium；一般 bug fix 與明確功能走 `quality_write` 的 Luna xhigh；不明確或廣泛探索走 `quality_explore` 的 Terra medium；架構、auth、migration 與高風險唯讀審查走 `ceiling_review` 的 Sol medium；前一步失敗或最高風險安全稽核走 `frontier_security_review` 的 Sol high。主 thread 不會依任務自動從 xhigh 降到 medium。

| Route | Profile | Target agent | Model / effort | Access |
| --- | --- | --- | --- | --- |
| `cost_write` | `cost` | `fast_implementer` | Luna medium | workspace-write |
| `quality_write` | `quality` | `multi_mode_agent` | Luna xhigh | workspace-write |
| `quality_explore` | `quality` | `researcher` | Terra medium | read-only |
| `ceiling_review` | `ceiling` | `reviewer` | Sol medium | read-only |
| `frontier_security_review` | `frontier` | `security_auditor` | Sol high | read-only |

Route allowlist 以 `.codex/profiles.json` 為準。呼叫者不得直接提供 `target_agent`、`model` 或 `reasoning_effort`；高風險角色只提供唯讀審查，修改與最終驗收保留在主 thread 或受限 Luna write route。

## 委派

1. 定義 Goal、non-goals、允許路徑、context、限制、return schema 與可執行 Done-when。
2. 選出一個可獨立驗證且不重疊寫入的工作單元。
3. 寫明具名效益；若只有少量給定文字機械編輯，固定開銷通常大於收益，主 thread 親做。
4. 建立 JSON task envelope，至少包含 `route`、`profile`、`profile_contract_id`、`goal`、`non_goals`、`allowed_paths`、`context`、`constraints`、`done_when`、`verification`、`return_schema` 與 `delegation_benefit`；write route 另需 `exact_change`。`allowed_paths` 必須是無 glob、無 traversal 的 repo-relative paths；一般 write route 不得指向 control-plane、Memory 或 secret paths；`verification` 只接受 `.codex/profiles.json` 的 verifier IDs。
5. Spawn 前執行 `python3 .agents/skills/multi-mode-skill/scripts/validate_task.py <task.json>`；exit `2` 時停止，不得委派。
6. 驗證通過後，只使用 validator 的完整 `resolved` dispatch，將 `ROUTE`、`PROFILE`、`PROFILE_CONTRACT_ID`、canonical `PROFILE_CONTRACT`、實際 model/effort、task contract 與 verifier argv 轉成 prompt，再 spawn resolved target agent。
7. 要求回報 scope、changes、evidence、open questions、deviations 與 residual risk。
8. 主 thread 重跑關鍵驗證；worker 回報是證據，不是完成判定。

只有完整 task envelope 與 validator 的 `resolved` 結果可宣稱具備 multi-mode route 保證；直接 agent invocation 不屬於此 route contract，也不得只傳 profile label。worker 的自然語言自檢不能取代 mechanical input gate。實際 spawn 與 model 身分仍是 host runtime 行為，必須回報 runtime resolved model/effort；repo validator 不宣稱能證明 host-level dispatch。

最多使用 config 設定的四個 concurrent threads，不要求 nested delegation；巢狀委派需使用者顯式授權。

## 長任務

Checkpoint 必須包含 Goal、已完成、驗證、風險與下一步。只有使用者明確要求排程或 recurring execution 時才建立 Codex automation；不輸出不支援的排程指令。

## 輸出

依序回覆：resolved route/profile/model/effort、worker scope/result、主 thread 驗證、未完成風險。
