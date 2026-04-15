---
name: cost-tracker
description: 追蹤 Codex 任務的 token 與成本，提供可操作的降本建議（模型分派、subagent 使用量、上下文控制）。
---

# Cost Tracker

## Use when

- 你要評估一次任務或一段開發週期的成本。
- 你要比較不同模型分派（`gpt-5.4` vs `gpt-5.4-mini` vs `gpt-5.3-codex`）。
- 你需要提出具體的 token 降耗方案。

## Do not use when

- 任務目標是功能正確性且成本不是決策因子。
- 你沒有任何可參照的用量資訊。
- 你只能得到非常粗略估計且可能誤導決策。

## Workflow

1. 收集可得數據：模型、回合數、工具調用、是否平行 subagents。
2. 拆分成本來源：讀取探索、實作、審查。
3. 先換算使用者可讀指標：
   - `uncached_input_tokens = total_input_tokens - total_cached_input_tokens`
   - `cache_hit_ratio = total_cached_input_tokens / total_input_tokens`
   - `output_share = total_output_tokens / total_tokens`
   - `context_window_utilization = total_tokens / model_context_window`
   - `last_turn_share = last_turn_total_tokens / total_tokens`
4. 提出降本動作：
   - 把讀多寫少任務降到 `gpt-5.4-mini`
   - 把重工程實作集中在 `gpt-5.3-codex`
   - 限制不必要 subagent fan-out
5. 輸出「不影響品質」前提下的調整方案。

## Output Format

- Usage Snapshot
- Efficiency Dashboard
- Cost Drivers
- Optimization Actions
- Expected Tradeoffs

## Display Guidance

- 優先顯示「摘要卡」而不是只貼原始 token 表。
- 至少要有：
  - `Total Tokens`
  - `Cached Input`
  - `Uncached Input`
  - `Cache Hit Ratio`
  - `Last Turn Share`
  - `Context Window Utilization`
- 每個指標後面都要附一句短解讀，讓使用者能立即判斷是否健康。
- 若資料不足以精算成本，明確標示為 `usage efficiency report`，不要假裝是 billing report。
