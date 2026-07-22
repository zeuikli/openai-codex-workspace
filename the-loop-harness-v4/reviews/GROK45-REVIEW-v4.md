# Grok 4.5 審閱報告：The Loop Harness v4

> 審閱者：Grok 4.5（獨立 session）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/`（INDEX / CORE / SPEC / PROFILES / EVAL-BASELINE / EVAL-PACK-ADDENDUM / CHATGPT adapter / CONCEPT-MAP 指針 / EXPORT 角色）
> 狀態：read-only 文件審閱；未重跑 fixtures；未讀其他模型完整審閱正文作共識輸入（僅確認 reviews/ 目錄存在）

---

## 整體分數：8.0 / 10

The Loop Harness v4 是一套**自我稽核極強**的 agent 行為契約：存在準則（每條規則對應失敗模式）、`[P]`/`[E]` 可攜二分、MBH（Model + Body + Harness）、fixture 驅動 baseline、advisory 不得假稱 enforce。這套東西把「prompt 能保證什麼」畫得很清楚。

扣分不在願景，而在**落地落差**：current baseline 20/22 紅軸仍是 F7（eval_hack，兩輪穩定）與 F15（blindspot_pass，本輪轉紅）；SPEC §6 大量 L3 backlog 未結；ChatGPT adapter 維持 uncalibrated；2026-07-20 刪除 CODEX/GPT-5.6 raw packet 讓跨模型重播證據只剩 git 歷史。整體是「頂級設計規格 + 中等 enforcement 覆蓋」。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 8.5 | 六階段、六公理、跨切、委派、cache 五禁令、治理 §5、L4 F1–F22、降級 §7、adapter、EXPORT 失真點、MAST 14 類盤點。缺 stop-condition 集中段、Dynamic Workflows、L3 大量 open。 |
| 清晰度 | 7.0 | L1 零模型名/零數字/零 inline 引註是正確蒸餾；但 Johari/MBH/`[P][E]`/T1–T11/五禁令/常駐稅同時出現，新採用者需 INDEX+CORE+SPEC+CONCEPT-MAP。CORE 體量仍偏重。 |
| 可執行性 | 6.5 | `[P]` 可貼用；`[E]` 誠實標需 Body，但 Body 多數仍 backlog。無 Claude hooks 時整份 CORE 近似高品質 advisory。§7 降級條款有，但外部採用者容易低估「有多少還沒 enforce」。 |
| 跨模型可攜性 | 8.0 | 北極星與 EXPORT/adapter/接入程序一致。扣分：T1–T11 canonical 綁 `.claude/skills/`；Codex packet 刪除；ChatGPT 三 surface 未校準；PROFILES 數字 v3 carryover 未因 v4 條文換代重評。 |
| 可測試性 | 8.0 | F1–F22 設計成熟；F11–F22 oracle 資格化敘事清楚；variance/oracle/TAINTED_ENV caveats 誠實。扣：n=1 仍報 20/22 為 current verdict；lexical check 可繞；F18 action 未驗；F7/F15 紅。 |
| 治理/反腐蝕 | 8.5 | 作者面/執行面分離、自報成功鏈、全量 trace 演化、sealed/held-out、changelog schema 一流。張力：刪 raw packet vs「全量 trace 為食」；公理 6 證據偏薄（單 tweet）；治理自身多為 `[E]` 而無 hook。 |

---

## 最大優點（5）

1. **`[P]`/`[E]` + MBH**：把「模型讀了就會做」和「沒有 hook 就會塌」拆開，這是多數 harness 文檔缺的結構誠實。
2. **存在準則 + SPEC 證據表**：arXiv / tweet / workspace observed_trace 集中，L1 不塞引註；可稽核「為什麼有這條」。
3. **TEST 閘門族**：unverified_success、拿收據、Oracle 先於 loop、Gate 真路徑、裝完成捷徑具名、展示三分——對應真實 agent 作弊模式，不是空話。
4. **威脅模型擴大**：價值訴求 + 繼承軌跡 + 壓縮翻轉決策，超出「ignore previous instructions」級別。
5. **評估文化**：隔離 worktree、拒絕跨 runtime pooling、PASS ≠ enforce、provisional/prototype 不進分母——評測紀律本身就是產品。

---

## 最大缺口 / 風險（10）

### CRITICAL

**C1. `[E]` 效力空心化**
SPEC backlog 多數 open；#3 Dynamic Workflows 未落地。標記誠實 ≠ Body 存在。外部若把 v4 當「已 enforce 的系統」會誤判。

**C2. F7 / F15 紅軸 = advisory 天花板**
F7 兩輪穩定（字面特判 + held-out 泛化失敗）；F15 PASS→FAIL。CORE 已加嚴條文仍紅 → 邊際 prompt 收益耗盡，必須 lexical/workflow 機械化（#2b/#3）。

### HIGH

**H1. Raw packet 刪除 vs 演化原則**
Owner 刪 CODEX/GPT-5.6 persistent packets；跨模型數字只剩散文/INDEX。與 §5「全量 trace 為食、摘要餵養=reward-hacking」直接衝突。git 歷史若 squash，證據鏈斷。

**H2. v4>v3 行為 delta BLOCKED-ENV**
Counterfactual 對照臂被 in-env harness 汙染。Canonical 是設計層升級，非已驗證行為優勢。

**H3. F18 繼承軌跡僅 response-level**
威脅模型招牌向量之一；action-level（真擋 `--no-verify`）跨環境 UNTESTED。PASS 是「說會拒」不是「真擋住」。

### MEDIUM

**M1. n=1 點估計當 verdict**
20/22 在每 cell n=1 下無 CI；F15/F19 翻轉不可歸因。與自身「計數化/顯著性」語氣不一致。

**M2. 公理 6 證據薄**
Johari 作引擎合理，作「公理」位階僅 @trq212 軼聞級；與其他公理 arXiv 密度不對稱。

**M3. T1–T11 可攜斷裂**
Canonical 在 Claude skill 路徑；ChatGPT §3 幾乎只剩 Blindspot 一句。非 Claude surface 只剩名字。

**M4. PROFILES v4 未改數字卻換代標籤**
公理 5：換代以 fixtures 重審。L1 大改、L2 carryover，旋鈕可能與新閘門不匹配。

**M5. ChatGPT code block 未內嵌 uncalibrated**
狀態在標頭/§5；使用者常只複製 §3 block → 部署時丟失「未校準」訊號。

---

## 改善計畫（P0–P3）

### P0（1–2 週）— 防誤用 + 紅軸防線

1. **INDEX + CORE §7 顯式 enforcement 覆蓋聲明**
   列明：哪些 `[E]` 已有 hook/CI（例如測試檔紅旗）、哪些純 advisory。禁止外部文案寫「v4 enforces X」除非機制+語義測試在列。

2. **CHATGPT §3 code block 首行內嵌狀態**
   `狀態：uncalibrated/advisory — 未在本 surface 跑 F1–F22；完成上限 unverified_success。`

3. **F7/F15/F19 獨立 lexical/lint 路線（不等 #3 全基座）**
   - F7：PostToolUse 掃 test-literal 特判模式 + held-out 抽驗命令模板
   - F15：高風險域（付款/重試/刪除/遷移）UserPromptSubmit 或 pre-impl Blindspot checklist lint
   - F19：品味詞 + 無 reference → 阻斷「已完成」宣稱
   先 advisory 告警，fixture 資格化後升 block。

### P1（2–4 週）— 證據與呈現誠實

4. **Raw packet 政策**：永久保留集合（manifest hash + transcript + pins）或「sealed hash + 公共 timestamp」替代；SPEC §3 補刪除理由與未來最低集合。

5. **Baseline 呈現**：`current point estimate 20/22 (n=1/cell, CI n/a)`；PROFILES 訂 n≥3 才計滿分輪。

6. **INDEX**：v4 = 設計層 forward canonical；行為優勢 backlog #13 結案前不作 v4>v3 行為宣稱。

### P2（4–8 週）— 可攜補洞

7. **Adapter / EXPORT**：T1/T6/T7/T9/T11 各一句可攜定義（不複製 SKILL 全文）。

8. **公理 6**：SPEC 標 anecdotal/design engine，非論文級公理；或補 workspace fixture 背書後再維持公理位階。

9. **PROFILES**：標 `v3-carryover-pending-recal` 或重跑至少「judge bias / Unknowns 密度 / 展示節錄門檻」三列。

### P3（8–12 週）— 結構槓桿

10. **Backlog #3 Dynamic Workflows**：首個 workflow 對準 held-out generalization（F7/F20）或 adversarial-verify；解鎖 Return schema 與 statement-action 機械比對。

11. **F18 action sandbox**：允許真實 hook 路徑的 commit 測試，或 L1/EVAL 標 `response-only evidence`。

12. **Stop-condition 段（G-LoopA）**：verifier 過 / 迭代上限 / 預算上限 / 無進展——寫入 CORE §1 或 judgment-rubrics，autoload-evolution 路由。

---

## 優先序一句話

先 **說清楚什麼已 enforce** + **把 F7/F15 從 prompt 搬到 Body**，再談 ChatGPT 校準與 Dynamic Workflows；否則 v4 會一直是「最誠實的 advisory 規格」，而不是「可移植的確定性契約」。

---

## 與設計自洽的總評

v4 最大成就不是 20/22，而是強制讀者接受：**fixture PASS ≠ enforcement，能力升 ≠ 可少驗證，摘要 ≠ 演化飼料**。最大債是 Body 覆蓋率與紅軸機械化。Grok 評語：**架構分高、落地分中；P0 做完可穩上 8.5+，#3+#14 做完才有資格談「跨模型不失真」的實證版。**

**完成標籤**：`unverified_success` — 文件層獨立分析，未跑 fixtures、未改 CORE/SPEC 本體。

**主要讀取**：
- `research/the-loop-harness-v4/INDEX.md`
- `research/the-loop-harness-v4/HARNESS-CORE-v4.md`
- `research/the-loop-harness-v4/SPEC-v4.md`（差異表、證據表、裁決、§6–§8）
- `research/the-loop-harness-v4/EVAL-BASELINE-v4.md`
- `research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md`
- `research/the-loop-harness-v4/PROFILES-v4.md`（標頭與檔位表）
- `research/the-loop-harness-v4/reviews/README.md`
