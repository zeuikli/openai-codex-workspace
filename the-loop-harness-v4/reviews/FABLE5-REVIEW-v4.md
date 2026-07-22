# Fable 5 審閱報告：The Loop Harness v4

> 審閱者：Fable 5（fable-5-auditor）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件
> 狀態：read-only audit；未重跑 fixture

---

## 整體分數：8.5 / 10

理由：這是一份紀律最嚴格的 agent harness 規格之一。實證存在準則、`[P]`/`[E]` 可攜性二分、MBH（Model + Body + Harness）公理、fixture 驅動驗證、誠實狀態標籤（`uncalibrated/advisory`、`provisional`、`TAINTED_ENV`）、拒絕跨 runtime pooling 等設計，構成罕見的智識誠實。扣分集中在：F7/F15 兩輪紅軸顯示 advisory 服從不穩定而對應 L3 hook 未落地；F11–F19 `deterministic_check` 多為 lexical grep；2026-07-20 刪除 CODEX/GPT-5.6 raw packet 使跨模型 baseline 淪為 git-history-only；ChatGPT adapter 三 surface 校準未完成；術語密度對新採用者偏高。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 9/10 | 六階段 + 六公理 + 跨切 + 委派 + cache + 治理 + L4 Eval Pack + 降級 + ChatGPT adapter 全覆蓋；MAST 14 類覆蓋率盤點 6 已攔 / 7 部分攔 / 1 僅 advisory。 |
| 清晰度 | 7/10 | 結構嚴謹，但術語密度高（Johari / MBH / `[P]`/`[E]` / T1–T11 / 五禁令 / 常駐稅），新讀者須同時讀 INDEX + CONCEPT-MAP + CORE + SPEC。 |
| 可執行性 | 8/10 | `[P]` 條文可逐字貼入；`[E]` 條文明示需 L3/L4 支撐，§7 降級條款 + EXPORT 失真點清單給出退化模式。多個 `[E]` 條文對應 hook 仍列 backlog。 |
| 跨模型可攜性 | 9/10 | `[P]`/`[E]` 二分 + EXPORT build artifact（blob hash 已驗同步）+ ChatGPT adapter + 新模型接入程序 + 拒絕跨 runtime pooling = 同類最佳。 |
| 可測試性 | 8/10 | 22 fixtures + F11–F22 24-case oracle 資格化 + F23–F27 正確範式。扣分：lexical check 可被語句繞過；F7/F15 紅軸；F18 action 未驗；n=1 無 variance。 |
| 治理/反腐蝕 | 9/10 | §5 顯式分離規則作者面、byte gate、自報成功鏈、構念對齊、全量 trace 演化、sealed/held-out、changelog schema。治理面本身未機械強制。 |

---

## 最大優點（5 項）

1. **實證驅動的存在準則**：每條規則須對應實證失敗模式；SPEC §2 證據表逐列引用 arXiv / tweets / workspace observed_trace。
2. **`[P]`/`[E]` 二分 + MBH 公理**：北極星「換模型不失真」落實到條文層級，明示哪些規則在無 enforcement 時會靜默退化。
3. **能力悖論公理 + 對抗審查優先異模型**：拒絕「模型夠強所以可信」，並要求異質性審查解相關性錯誤。
4. **Fixture 驅動驗證 + 誠實狀態標籤**：`uncalibrated/advisory`、`provisional`、`TAINTED_ENV`、`substitution:{F10:F10R}`、拒絕跨 runtime pooling。
5. **反腐蝕治理面 §5**：自報成功鏈、「advisory 未強制不得稱 enforce」、演化以全量 trace 為食、sealed/held-out 認證。

---

## 最大缺口 / 風險（10 項）

| 嚴重性 | 缺口 | 涉及檔案 |
|--------|------|----------|
| CRITICAL | F7 eval_hack 兩輪穩定紅，advisory 防範未機械化 | `EVAL-BASELINE-v4.md`, `HARNESS-CORE-v4.md` §1 TEST, `SPEC-v4.md` §6 #2b/#3 |
| HIGH | F15 blindspot_pass 單樣本翻轉，趨勢不可歸因 | `EVAL-BASELINE-v4.md`, `HARNESS-CORE-v4.md` §1 IDENTIFY |
| HIGH | F11–F19 deterministic_check 為 lexical grep，可被語句繞過 | `EVAL-PACK-v4-ADDENDUM.md`, `EVAL-BASELINE-v4.md` |
| HIGH | CODEX/GPT-5.6 raw packet 已刪，跨模型證據僅 git-history 可考 | `INDEX.md`, `SPEC-v4.md` §3/§6, `EVAL-BASELINE-v4.md` |
| HIGH | ChatGPT adapter 三 surface 校準未完成，路由表可能誤導 | `CHATGPT-HARNESS-v4.md` §4/§5/§7, `SPEC-v4.md` §6 #14 |
| MEDIUM | 術語密度對新採用者偏高 | `HARNESS-CORE-v4.md`, `CONCEPT-MAP-v4.md` |
| MEDIUM | §5 治理面本身多為 `[E]`，反腐蝕機制未機械強制 | `HARNESS-CORE-v4.md` §5, `SPEC-v4.md` §6 #1/#3/#11 |
| MEDIUM | Cache 五禁令在 ChatGPT adapter 靜默 drop | `HARNESS-CORE-v4.md` §4, `HARNESS-EXPORT.md`, `CHATGPT-HARNESS-v4.md` §3 |
| MEDIUM | F18 inherited_trajectory action receipt 從未驗證 | `EVAL-BASELINE-v4.md`, `EVAL-PACK-v4-ADDENDUM.md` F18 |
| LOW | Round 2 每 cell n=1，「連 2 輪滿分」加嚴節奏無法啟動 | `EVAL-BASELINE-v4.md`, `PROFILES-v4.md` §2 |

---

## 優先排序改善計畫

### P0

1. **機械化 F7/F15 紅軸防範**：擴充 `test-file-redflag.sh` 對 literal-patch 模式的靜態偵測；新增 held-out 輸入抽驗腳本；以 Dynamic Workflow 的 `agent({schema})` 機械驗證 Handoff Return 欄位（陳述-行動一致性）。落地：`.claude/hooks/`、`.claude/workflows/`、`settings.json`。
2. **複製樣本 baseline（n≥3 per cell）**：更新 `EVAL-BASELINE-v4.md` 加 variance band；`PROFILES-v4.md` §2 定義最低 n 才能觸發加嚴。

### P1

3. **升級 F11–F19 deterministic_check 為 qualified oracle**：每 fixture 建立 ≥4 known-good + ≥4 known-bad counterexample。
4. **恢復或重跑跨模型 persistent packet**：或在 `INDEX.md`/`SPEC-v4.md` 加醒目 caveat「結論不可獨立覆核」。
5. **完成 ChatGPT 三 surface 校準**：chat-only / tool-enabled / API 各跑 F1–F22 + 代表任務；§4 路由表降級為「未驗證起點假設」。

### P2

6. **ChatGPT adapter 顯式標 §4 cache 五禁令 N/A**：§3 補一段說明無前綴快取時的替代做法。
7. **落地 §5 治理 hook**：allowlist-widening 複審 hook、auto-load post-edit cache-invalidation 提示 hook、Dynamic Workflows 基座。
8. **解決 G-LoopA**：`.claude/rules/core.md` 補獨立 stop-condition 段。
9. **新增 `GLOSSARY-v4.md`**：單頁定義 Johari / MBH / `[P]`/`[E]` / T1–T11 / 五禁令等術語。

### P3

10. **F18 action receipt 真驗**：設計允許 hook execution 的 fixture runtime。
11. **定義「連 2 輪滿分」最低 n**：`PROFILES-v4.md` §2 補「每 cell n≥3 且全綠才計一輪滿分」。
12. **F23–F27 升格路徑**：multi-case corpus + 等資源 baseline + 結構化 tool event + seeded mutation known-bad。

---

## ChatGPT 適配評估（`CHATGPT-HARNESS-v4.md`）

- **適當性：good**。Surface capability matrix、enforcement boundary 表、可貼用核心皆正確映射 CORE 不變式。
- **限制說明充分性：strong，但有 3 處弱點**：
  1. §4 路由表格式暗示穩定角色分配，建議改為「未驗證起點假設」框起或摺疊。
  2. §3 完全未提及 cache 五禁令（連 N/A 標記都沒有），靜默 drop 違反 EXPORT 失真點清單指示。
  3. §6 中「本 turn 確認」在非同步 chat 語境模糊，建議改「本次對話明確確認」。
- **結論**：ChatGPT adapter 在誠實標記與限制揭露上做得比多數 adapter 好；主要風險是路由表被誤讀、cache 靜默 drop、用語模糊。`uncalibrated/advisory` 狀態應維持至三 surface 校準完成。
