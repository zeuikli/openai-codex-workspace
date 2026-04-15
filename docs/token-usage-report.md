# Token Usage Report (2026-04-14)

## Scope

- 目標：比較 `claude-code-workspace` 舊結構與目前 `openai-codex-workspace` 在「啟動時需要讀取的核心治理檔案」之 token 成本。
- 另外補充目前 Codex session 的實際 token 使用紀錄（來自本機 session log）。

## 測試方法

- 比較集合（優化前 / 優化後）：
  - 優化前：`CLAUDE.md`、`Memory.md`、`prompts.md`、`.claude/settings.json`、`.claude/agents/*`、`.claude/skills/*/SKILL.md`
  - 優化後：`AGENTS.md`、`Memory.md`、`prompts.md`、`.codex/config.toml`、`.codex/agents/*.toml`、`.agents/skills/*/SKILL.md`
- 計算方式：
  - 先統計 UTF-8 字元數（`chars`）與位元組數（`bytes`）。
  - 估算 token 公式：`est_tokens = ceil(chars / 3.6)`。
- 注意：
  - 此為可重現估算，不是 API billing 精算值。
  - 真實 token 會依模型 tokenizer、語言分布、快取命中而變動。

## 結果（優化前後）

| 指標 | 優化前 (Claude) | 優化後 (Codex) | 差異 |
|---|---:|---:|---:|
| 檔案數 | 15 | 18 | +3 |
| 字元數 | 14,097 | 12,976 | -1,121 |
| 位元組數 | 21,648 | 23,342 | +1,694 |
| 估算 Tokens (`ceil(chars/3.6)`) | 3,916 | 3,605 | **-311 (-7.94%)** |

解讀：
- 雖然 Codex 版檔案數較多，但核心治理文字更精簡，啟動估算 token 下降約 7.94%。
- 後續若改成「分層載入 skills（只按任務載入）」，可再進一步降低初始 token。

## 目前 Session 實際紀錄（本機 log）

來源檔：`~/.codex/sessions/2026/04/14/rollout-2026-04-14T10-21-04-019d89ca-d2f5-7d03-86e1-2df933a07057.jsonl`  
最後一筆 token 時間：`2026-04-14T02:23:14.887Z`

### Usage Snapshot

| 摘要卡 | 數值 | 解讀 |
|---|---:|---|
| Total Tokens | **149,354** | 這是本次 session 到最後一筆紀錄的總用量。 |
| Cached Input | 91,008 | 已有相當比例來自快取，代表前文重用有發揮效果。 |
| Uncached Input | 53,709 | 這部分才是每次重新餵入、最值得優化的輸入成本。 |
| Cache Hit Ratio | **62.89%** | 快取命中率偏健康，但仍有約 37% 輸入是新成本。 |
| Last Turn Share | **35.32%** | 最後一回合就佔了超過三分之一，代表尾段上下文膨脹明顯。 |
| Context Window Utilization | **57.80%** | 尚未逼近上限，但長任務若不摘要，後段成本會繼續上升。 |

### Efficiency Dashboard

| 指標 | 數值 |
|---|---:|
| total_input_tokens | 144,717 |
| total_cached_input_tokens | 91,008 |
| uncached_input_tokens | 53,709 |
| total_output_tokens | 4,637 |
| total_reasoning_output_tokens | 1,872 |
| reasoning_share_of_output | 40.37% |
| total_tokens | 149,354 |
| last_turn_total_tokens | 52,751 |
| output_share_total | 3.10% |
| model_context_window | 258,400 |
| context_window_utilization | 57.80% |

### Cost Drivers

- 最主要成本來自輸入而不是輸出；`output_share_total` 只有 `3.10%`。
- 最後一回合成本偏大；`last_turn_total_tokens` 佔整體 `35.32%`。
- 推理輸出佔輸出 `40.37%`，表示這段任務後期需要較多思考與收斂。

### Optimization Actions

1. 把長任務切成里程碑，每輪結束只保留短摘要與決策，不重貼完整歷史。
2. 文檔查證與讀多寫少工作優先派 `gpt-5.4-mini`，減少高價主模型輸入。
3. 技能檔只按需載入，避免把無關 `SKILL.md` 一起送進上下文。
4. 若最後階段是整理/報告任務，先做一次摘要再進入最終輸出，可壓低尾段 token 峰值。

## 建議的持續優化

1. 啟動指令固定先載入：`AGENTS.md` + `Memory.md` + `prompts.md`。
2. 將 `.agents/skills/*/SKILL.md` 改為按需載入，不做全量預讀。
3. 文檔查證類工作優先派給 `gpt-5.4-mini`，只在需要時升級到 `gpt-5.4`。
4. 長任務中定期摘要上下文，避免重複把舊內容重新塞回 prompt。
