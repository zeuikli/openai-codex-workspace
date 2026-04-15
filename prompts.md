# Codex Prompts（App / CLI）

> 可直接貼到 Codex App 或 Codex CLI 使用。

## 1. 啟動檢查（推薦）

```text
請先固定讀取 AGENTS.md、Memory.md、prompts.md，回報：
1) 目前規範摘要
2) 尚未完成事項
3) 你將先執行的第一個可驗證步驟
```

## 2. 直接執行模式（避免只給計畫）

```text
請不要只提供計畫，直接執行任務並完成最小可驗證修改。
若遇阻塞，再回報阻塞原因、風險與替代方案。
```

## 3. Tier 1 高頻模式（Prompting Guide）

```text
請依 Codex Prompting Guide 的高頻規則處理：
- 直接行動、端到端完成
- 優先工具化與最小修改
- 可平行的讀取工作請平行化
- 收尾時逐項對照 Done when
```

## 4. Tier 2 中大型改造模式（Modernization）

```text
這是中大型任務，請用分階段產物執行：
1) 計畫與範圍
2) 盤點與發現
3) 設計與規格
4) 驗證與測試
每個階段結束都更新狀態（completed/blocked/cancelled）後再進入下一階段。
```

## 5. 多代理模式（僅在任務足夠大時）

```text
請只在必要時啟用 subagents：
- 任務拆分為不重疊寫入範圍
- 每個 worker 直接執行，不輸出冗長前置計畫
- 回報固定格式：範圍、發現、建議、證據、驗證狀態
- 主 Agent 最後做風險收斂與整體驗證
```

## 6. 文檔漂移檢查

```text
請用 docs-drift-check 檢查目前 repo 與官方文件的一致性，
優先比對：Codex Prompting Guide、Modernizing your Codebase with Codex。
文檔查證請優先使用 gpt-5.4-mini，只有在規格衝突或高風險決策時才升級到 gpt-5.4。
輸出：Drift Summary、Proposed Fix、Verification Plan。
```

## 7. Skills 按需載入

```text
請不要全量預讀 .agents/skills/*/SKILL.md。
先判斷目前任務需要哪一個 skill，再只載入該 skill 的 SKILL.md 後執行。
若本任務不需要 skill，請直接使用核心規範執行。
```

## 8. 長任務上下文摘要

```text
這是長任務，請每個里程碑輸出一次短摘要：
1) 目前結論
2) 已完成驗證
3) 剩餘風險
4) 下一步
請避免重複貼上完整舊上下文，只保留決策所需最小資訊。
```

## 9. 結束前交接

```text
請更新 Memory.md，至少包含：
- 本次完成事項
- 修改檔案清單
- 驗證結果（已驗證/未驗證）
- 下一步待辦
```

## 10. 全面審查與優化

```text
請用全面審查模式執行：
- 主 Agent 視為 gpt-5.4 + high reasoning
- 若進入最終驗收或高風險收斂，升級為 gpt-5.4 + xhigh reasoning
- 架構盤點、文件查證、成本分析優先派給 gpt-5.4-mini + medium reasoning
- 純實作、測試、code review、安全審查優先派給 gpt-5.3-codex
輸出：審查結論、最高風險問題、優化順序、驗證計畫。
```

## 11. Karpathy 原則啟用（一鍵套用）

```text
請全程遵守 docs/karpathy-codex-principles.md：
1) 先把需求改寫為可驗證 Done when，條件齊全再進實作。
2) 每個推測性決策寫成假設清冊（Assumptions / Verified / Unverified）。
3) 遇規格衝突先顯化兩版本與建議，不挑邊硬上。
4) 先寫正確樸素版 → 補正確性測試 → 才做優化。
5) 只改與需求相關檔案；看不懂的註解/死碼記為 Followup。
回覆格式：結論 → 變更摘要 → 驗證狀態 → 假設清冊 → 未決風險 / Followup。
```

## 12. Success-Criteria Loop（宣告式驗證迴圈）

```text
這個任務採宣告式驗證迴圈執行：
- 我會給你 Done when（可執行的驗證指令或可觀測行為）。
- 請你自動 loop：實作 → 跑驗證 → 讀錯誤 → 修正 → 再跑。
- 上限 5 輪或 10 分鐘；超過請停下並回報阻塞原因、已嘗試方案、剩餘風險。
- 每輪只回報：diff 摘要 + 驗證輸出尾段，不要回貼完整舊上下文。
```

## 13. Naive-First 實作策略

```text
請先用最樸素、幾乎一定正確的做法完成功能並跑通驗證；
確認正確後再進行優化，優化每一步都要重跑正確性測試。
不得把優化與功能實作混在同一個 commit。
```

## 14. Pushback 模式（拒絕 sycophancy）

```text
如果我的指令與下列任一項衝突，請先停下並指出衝突，再請我確認：
- AGENTS.md / AGENTS.full.md 既有規範
- 既有測試或 CI 檢查
- 安全邊界或資料遷移風險
- 最小影響半徑原則
禁止以「好的，已完成」結尾；要嘛有可驗證產物，要嘛有阻塞原因。
```

## 15. Anti-Bloat 自檢

```text
實作前先回答三題：
1) 這個抽象/參數/選項現在就有使用者嗎？沒有就不加。
2) 同樣行為有沒有 1/10 行的寫法？
3) 我是否動了與 Goal 不直接相關的程式碼？若有，改為 Followup。
實作後若超出預估複雜度 2 倍，請暫停並在回覆中記錄「更簡版替代方案」。
```

## 16. 省成本日常模式

```text
請用省成本模式執行：
- 主 Agent 用 gpt-5.4 + medium reasoning
- 讀多寫少任務優先交給 gpt-5.4-mini + medium reasoning
- 純實作與測試交給 gpt-5.3-codex + medium reasoning
- 深度 review / security review 才升到 gpt-5.3-codex + high reasoning
- 先優化上下文與摘要，不要一開始就提高 reasoning
輸出：本次分流策略、預期節省點、風險與驗證方式。
```

## 17. Codex-only 多 Agent 深度研究 + CLI/Cloud 適配

```text
請把任務拆成三個 worker（Research / Implement / Review）並收斂：
1) Research：只萃取與 Codex 直接相關的規範變更，禁止加入非 Codex 內容。
2) Implement：先做最小可驗證修改，遵守 Minimal Blast Radius。
3) Review：用 deep-review 格式回報 Findings、Residual risk、可否合併。

Done when：
- `python3 scripts/validate_codex_workspace.py` 通過
- `python3 -m unittest -v tests/test_codex_hooks_behavior.py` 通過
- README / AGENTS / docs 皆有對應到同一套 Codex CLI + Codex Cloud 驗證入口

輸出順序：
結論 → 變更摘要 → 驗證狀態 → 未完成風險 → 下一步。
```
