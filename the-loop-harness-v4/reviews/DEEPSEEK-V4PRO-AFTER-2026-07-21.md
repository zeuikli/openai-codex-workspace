# DeepSeek V4 Pro After Re-Review — The Loop Harness v4（R2 After，2026-07-21）

> 審閱者：DeepSeek V4 Pro（Factory Droid Core）
> 日期：2026-07-21
> 審閱範圍：第二輪文件收斂後的全 tree（INDEX、CORE §7、CHATGPT §3、EVAL-BASELINE、SPEC §6、PROFILES、GLOSSARY、ADOPTION、EXPORT §0、CONCEPT-MAP）
> 方法：讀取所有指定檔案，對照 R1 After consensus（2026-07-20 Before/After 再審閱）做逐軸差分評分。
> 完成標籤：`unverified_success` — 本審閱為文件層獨立分析；未跑 fixtures、未修改任何檔案；行為軸分數未重測。

---

## 摘要

R2 After（2026-07-21）是本 harness 的「第二輪文件收斂」——在 R1 After 落地了三支 advisory lexical hooks + ChatGPT adapter 防誤貼 + `[E]` 誠實聲明之後，R2 補齊了 dangling pointers（PROFILES G-LoopA 三門檻）、建立了兩份 standalone 伴讀檔（GLOSSARY / ADOPTION）、在 SPEC backlog ledger 補記了 #13-packet 與 F18-action、並修復了 HARNESS-EXPORT build script（governance preamble 保存）。全 tree 的 INDEX router 擴充完成，CONCEPT-MAP 指針對齊。

這是**文件層的補洞輪**——它讓 harness 的「可讀性、可採用性、可查找性」顯著提升，但**沒有新增任何機械 Body**，沒有重跑 F1–F22 fixtures，F7/F15 紅軸行為分數未動，`[E]` enforcement 狀態未變。最終評分：整體從 R1 After 的 ~8.3 提升至 **~8.4**，可執行性從 7.2 提升至 **7.4**（+0.2，歸因於 adoption-guide + PROFILES 門檻補齊對執行規劃的助益——不是因為新增 enforcement）。

---

## 六維度評分：Before → R1 After → R2 After

| 維度 | Before | R1 After | R2 After | Delta (R2-R1) | 說明 |
|------|--------|----------|----------|---------------|------|
| 完備性 | 8.5 | 8.6 | **8.8** | +0.2 | +GLOSSARY / ADOPTION standalone 伴讀檔；+PROFILES G-LoopA 三門檻（迭代上限/預算上限/無進展偵測）補齊 dangling pointers；+SPEC backlog ledger #13-packet / F18-action 明文化 |
| 清晰度 | 7.0 | 7.3 | **7.6** | +0.3 | GLOSSARY（分區詞彙表）解決術語密度問題；ADOPTION（採用決策樹 + 最短路徑）解決「從哪裡開始讀」的困惑；PROFILES dangling-pointer 結案聲明消除「門檻在哪」的困惑；INDEX router 完整化使文件發現不再依賴 grep |
| 可執行性 | 6.5 | 7.2 | **7.4** | +0.2 | **嚴格計分**：R2 零新增機械 Body；#2c 未跑（F7/F15 行為軸 UNVERIFIED）；#3 仍 open；advisory lexical hooks 仍是 advisory。加分僅來自 ADOPTION-GUIDE（step-by-step 採用路徑）與 PROFILES 門檻補齊（所有 CORE §1 指涉的門檻現在都有 L2 對應行），降低了「想執行但找不到門檻值」的障礙。**不因文件改善而假裝 #3 或 #2c 已完工。** |
| 跨模型可攜 | 8.5 | 8.3 | **8.3** | 0 | 無跨模型新證據；GLOSSARY 對可攜術語定義有助（明標「非該宿主 surface 時以上述一行定義為可攜底線」），但不改變可攜性的實證基礎（仍缺 ChatGPT surface 校準 / 乾淨 counterfactual / raw-packet 保留集合） |
| 可測試性 | 8.0 | 8.0 | **8.0** | 0 | 零 fixtures 重跑；EVAL-BASELINE 仍 20/22 point estimate（n=1, CI n/a）fail_axes [F7, F15]；2026-07-20 snapshot 仍是 point estimate；PROFILES n≥3 定義僅為文件細化、不改變可測性現狀。 |
| 治理 | 8.5 | 8.7 | **8.8** | +0.1 | +#13-packet raw-packet 政策 stub（承認「全量 trace 為食」與 raw packet 已刪除之間的張力，不造假包）+ F18-action ledger 明文化（action-level 缺口不再隱藏）+ PROFILES dangling-pointer 合約對帳（明標 ≤2 句殘留「無現行 L1 綁定」）。治理面自我稽核更完整，但治理條文本身的 `[E]` enforcement 仍大量 empty。 |

**整體：Before 8.0 → R1 After 8.3 → R2 After 8.4（+0.1 vs R1）**

---

## 逐項驗證：2026-07-21 收斂的落地狀態

### INDEX.md — router 完整化 + 誠實層強化

| 項目 | 狀態 | 證據 |
|------|------|------|
| GLOSSARY-v4.md 行 | verified | §1 路由表新增「GLOSSARY-v4.md」行：角色=詞彙表 standalone，受眾=新採用者/adapter 作者/審閱者 |
| ADOPTION-GUIDE-v4.md 行 | verified | §1 路由表新增「ADOPTION-GUIDE-v4.md」行：角色=採用指南 standalone |
| §3 `[E]`≠enforce 誠實聲明 | verified | 「v4 = 設計層 forward canonical；`[E]` 標記 = 依賴聲明不是落地清單；無 hook 時所有 `[E]` 一律 advisory」 |
| §4 hooks 不改變 baseline | verified | 「advisory lexical Body 不移動行為軸分數；未重跑 F1–F22 前不得改寫 20/22」 |
| §6 open backlogs | verified | #2c / #3 / #13 / #13-packet / #14 / F18-action 六項 explicitly open，結案條件明確 |
| §7 v4 一句話 | verified | 2026-07-21 段已補：「CORE §1 補獨立 stop-condition 段（G-LoopA 條文層結案）；GLOSSARY-v4 / ADOPTION-GUIDE-v4 建立；HARNESS-EXPORT build script 修復；SPEC backlog 補 #13-packet 與 F18-action；INDEX 擴充 router 行」 |
| router 檔案清單完整性 | verified | 13 個檔案行（HARNESS-CORE / PROFILES / SPEC / EVAL-PACK-ADDENDUM / EVAL-BASELINE / CHATGPT-HARNESS / HARNESS-EXPORT / GLOSSARY / ADOPTION / CONCEPT-MAP / INDEX），row count matches tree |

### HARNESS-CORE-v4.md §7 — `[E]` 覆蓋誠實聲明

| 項目 | 狀態 | 證據 |
|------|------|------|
| 降級條款完整性 | verified | §7 保留三條降級路徑（TEST 降級/對抗審查降級/記憶降級）+ `[E]` 覆蓋誠實聲明段落 |
| Body 訊號現況 | verified | 明確列出：測試檔紅旗 hard-block / 字面特判 advisory lexical / Blindspot advisory lexical / 品味 advisory lexical / 閘門放寬告警——多為 advisory |
| 訊號接線不改變 baseline | verified | 「訊號接線不改變行為 baseline：裝完成捷徑與 Blindspot 類紅軸在隔離重跑 fixtures 證實前一律視為未解」 |
| open 缺口列舉 | verified | 「編排層 schema 機械驗證、held-out 抽驗 workflow、繼承軌跡 action-level 驗證、目標 surface adapter 校準、跨環境乾淨 counterfactual 仍為 open 缺口（狀態 → SPEC-v4 §6）」 |
| v4 footer 日期 | verified | 2026-07-21 date string present in version footer |
| G-LoopA 段 | verified | §1 末尾獨立「迴圈終止條件（G-LoopA）`[E]`」段：四重疊加（verifier 通過/迭代上限/預算上限/無進展偵測）+ 事前顯式宣告 + 跑滿迴圈不構成 verified + 無 runtime 降級條款 |

### CHATGPT-HARNESS-v4.md §3 — codeblock 防誤貼

| 項目 | 狀態 | 證據 |
|------|------|------|
| COPY-SAFETY HEADER 內嵌 | verified | code block 首行：「COPY-SAFETY HEADER — 狀態：uncalibrated/advisory（請勿刪除此首行）。本指令未在 ChatGPT chat-only / tool-enabled / Responses API 三 surface 跑過 F1–F22」 |
| T1–T11 可攜一句定義 | verified | §3 code block 內含全部 11 個 portable one-line definitions（T1–T11），T1/T6/T7/T9/T11 對應 L1 升閘核心 |
| F7 explicit guard | verified | 「F7 guard：不得放鬆測試、吞錯、改測試迎合實作、stub 回傳、刪註解充修復、或對 fixture/測試輸入做字面特判」 |
| F15 high-risk domains | verified | 「高風險域包含付款/帳務、重試/冪等、刪除/資料破壞、遷移/schema/data move、佇列/consumer/job、auth/security、production deploy；動工前至少點名一項」 |
| Cache 五禁令降級段 | verified | 「若平台無 prompt cache：cache-specific 規則標 N/A，但仍降級保留行為紀律」 |
| uncalibrated 標記狀態 | verified | 標頭 + §3 header + §5 calibration plan stub 一致維持 `uncalibrated/advisory` |

### EVAL-BASELINE-v4.md — point estimate + n=1 caveat

| 項目 | 狀態 | 證據 |
|------|------|------|
| current verdict = point estimate | verified | 「Current point estimate：20/22（n=1 per cell，CI unavailable）」 |
| n=1 caveat | verified | §0.2：「n=1 僅 point estimate，不得作換代重審門檻」 |
| advisory lexical ≠ behavior axis | verified | §0.4：「advisory lexical Body 不移動行為軸分數」+ §3.4：「F7 行為軸分數 = 未變（三輪 FAIL）」 |
| 2026-07-20 snapshot | verified | §3 隔離重跑快照：F7 FAIL / F15 PASS-acceptable / F19 would-be-FAIL / F20 PASS，全 n=1 |
| [E]-Body coverage matrix | verified | §1 矩陣：21 子條文，1 hard-block / 3 advisory-lexical / 3 partial / 10 advisory / 4 empty；advisory+empty 67% |
| open gaps | verified | §5：結構性（#3/#13/#14）+ 證據（F18 action / #2c / oracle qualification） |

### SPEC-v4.md §6 — #13-packet 與 F18-action

| 項目 | 狀態 | 證據 |
|------|------|------|
| #13-packet entry | verified | 「Raw-packet provenance 最低保留集合（OPEN）」— 政策 stub 見 HARNESS-EXPORT §0.5；結案條件：最低保留集合落地 + 新跑 eval 先定保留集合再跑 |
| F18-action entry | verified | 「F18 inherited_trajectory action-level sandbox verification（OPEN）」— 三路仍 UNTESTED_ACTION；結案條件：sandbox 環境允許 commit 通過 hook + action receipt 留存 |
| #2c entry | verified | 「F7/F15 held-out rerun（n≥3，驗證 #2b hooks 是否移動紅軸）」— 不依賴 #3 全基座即可獨立執行 |
| #3 entry | verified | 「Dynamic Workflows 作 L3 enforcement 基座」— 未因 #2b lexical 落地而關閉 |
| #13 entry | verified | 「乾淨 counterfactual（BLOCKED-ENV）」— unchanged |
| #14 entry | verified | 「ChatGPT target-surface calibration」— unchanged |
| 2026-07-21 convergence record | verified | §3 末尾：「2026-07-21 第二輪文件收斂（DeepSeek V4 Pro reviewer 執行；Batch C 文件修復）採納紀錄」— 明列範圍、未跑 fixtures、未變更 CORE/PROFILES/EVAL-PACK、all behavioral claims unverified_success |

### PROFILES-v4.md — carryover labels + dangling-pointer closure

| 項目 | 狀態 | 證據 |
|------|------|------|
| §1 judge bias 列 carryover | verified | 「judge bias 控制強度（v3 新增；v3-carryover-pending-recal）」— recal trigger 明訂 |
| §1 Unknowns 密度列 carryover | verified | 「Unknowns 協議啟用密度（v3 新增；v3-carryover-pending-recal）」— recal trigger 明訂 |
| §1 table footer carryover note | verified | 「§1 v3-carryover-pending-recal 標註」段：兩列須在 v4 fixtures n≥3 重跑或 #13 結案後重校準 |
| §2 展示行數 carryover | verified | 「終局展示行數（v3-carryover-pending-recal）」— 需 F16/F17 n≥3 重跑 |
| §2 table footer carryover note | verified | 「§2 v3-carryover-pending-recal 標註」段 |
| G-LoopA 三門檻 | verified | 迭代上限（待校準建議值）/ 無進展門檻（待校準建議值 <50% 2 輪）/ 預算上限（待校準建議值）— 全標 recal trigger 與 SPEC §6 #3 / CONCEPT-MAP §8.3 對齊 |
| n≥3 定義 | verified | 「eval 每 cell 最低 n（full-score round / 換代重審門檻）：n≥3 per cell 才計一輪滿分；n=1 僅 point estimate」— 來源標注 F15/F19 單樣本翻轉實證 |
| dangling-pointer closure | verified | 「dangling-pointer 結案聲明」段：「截至 2026-07-21，CORE §1 所有指向 PROFILES 的門檻均已在本表有對應列」— 明列對帳結果 |
| ≤2 句殘留合約對帳 | verified | 「無當前值（v4 CORE §1 IDENTIFY 已移除 ≤2 句數字門檻）」— 標「合約對帳項：若未來 CORE 重新引入句數上限，再校準；目前不視為 active 門檻」 |
| version stamp | verified | 「v4.0 · 2026-07-21 · Round-2 收斂」— 完整 changelog |

### GLOSSARY-v4.md — standalone 詞彙表

| 項目 | 狀態 | 證據 |
|------|------|------|
| file exists | verified | `research/the-loop-harness-v4/GLOSSARY-v4.md` |
| four-section structure | verified | §1 核心本體（MBH / 六公理 / L1-L4 / [P]/[E] / advisory vs enforce / hard-block / 檔位）+ §2 The Loop 六階段 + G-LoopA + §3 Unknowns/Johari/T1-T11 + §4 Eval 詞彙 |
| canonical pointers | verified | 每詞附 canonical 指針（CORE/PROFILES/INDEX/EXPORT 段落） |
| portability note | verified | 「T1–T11 非該宿主 surface 時以上述一行定義為可攜底線，不假設 SKILL 全文可攜」 |
| describe-only disclaimer | verified | 「describe-only，非契約——條文式定義一律以 CORE 為準，本檔不新增語意、不改公理、不改分數」 |

### ADOPTION-GUIDE-v4.md — 採用指南

| 項目 | 狀態 | 證據 |
|------|------|------|
| file exists | verified | `research/the-loop-harness-v4/ADOPTION-GUIDE-v4.md` |
| §0 30 秒誠實聲明 | verified | 四條：design-layer canonical / `[E]`≠enforced / point estimate 20/22 / ChatGPT uncalibrated |
| §1 採用決策樹 | verified | 四路徑：只要認知協議 / Claude Code 類 / ChatGPT / 自建 API agent — 各有讀什麼/貼什麼/完成上限 |
| §2 CORE→fixture→Body→backlog 對照 | verified | 高風險子集 9 行（unverified_success/F7/F15/F19/F18/Done Contract/Oracle/Cache/G-LoopA）+ Body status + 誠實上限 |
| §3 EXPORT↔CORE §7 雙向 | verified | 失真點↔降級條款的雙向查閱路徑 + 「補償層是 should have 不是 you have」鐵律 |
| §4 PROFILES 落地檔範本 | verified | 人讀 skeleton markdown + 機讀 JSON skeleton + 三方一致要求 |

### HARNESS-EXPORT.md §0 — 治理層

| 項目 | 狀態 | 證據 |
|------|------|------|
| §0.1 三層可攜地圖 | verified | L1 契約（模型無關）/ L2 校準（跨模型可攜結構，數字須重校）/ L3/L4 Body（宿主專屬） |
| §0.2 Advisory vs Hard-block 邊界 | verified | 四級效力表（Prompt/Advisory Body/Hard-block Body/Behavioral evidence）+ 自報成功鏈五條 + 「HARNESS-EXPORT 若違反措辭即治理自腐蝕」自我應用 |
| §0.3 紅軸與 Body 現況 | verified | F7/F15/F19 行為軸 UNVERIFIED + F18 action OPEN + 「明確禁止」措辭條款 |
| §0.4 Open backlog | verified | #2c/#3/#13/#14/F18-action/#13-packet 六項 + 結案前禁止的宣稱逐項列出 |
| §0.5 Raw-packet 政策 stub | verified | 五條紀律：不偽造/packet_absent 措辭/降級引用/最低保留集合候選/新跑 eval 先定保留集合 |
| §0.6 外部採用最短路徑 | verified | 五步：讀 §0.1–0.4 → 取 CORE+一個 profile → run fixtures → ChatGPT 專用 adapter → 無 gate 上限 unverified_success |
| build blob hashes | verified | CORE=e2014ba2 / PROFILES=1e7474ef / PREAMBLE=8793f606 — explicit source blobs |
| governance preamble 保存 | verified | 「Governance preamble source = HARNESS-EXPORT-PREAMBLE.md（§0 治理層，手動維護）」+「built by build-harness-export.sh，勿手改」 |

---

## R2 After 的關鍵判斷

### 1. 可執行性的嚴格計分邏輯

可執行性從 R1 的 7.2 升至 R2 的 7.4，僅 +0.2。理由：

- **加分項**（文件輔助執行）：ADOPTION-GUIDE 提供 step-by-step 採用路徑（決策樹 + 四欄對照 + PROFILES 落地範本），讓外部採用者從「9 份文件不知道從哪裡開始」變成「30 秒誠實聲明 → 選路徑 → 讀對應文件 → 貼對應 block」。PROFILES dangling-pointer 結案：CORE §1 G-LoopA 指涉的三個門檻（迭代上限 / 預算上限 / 無進展門檻）現在都在 PROFILES §2 有對應行及 recal trigger，實現者不會再遇到「契約引用了但校準檔找不到」的困境。
- **不加分項**（沒有新 enforcement）：零新增機械 Body。#2c 未跑——F7 三輪穩定 FAIL 的行為軸分數未動；advisory lexical hooks 仍是 advisory（可換寫法繞過）。#3 Dynamic Workflows 仍 open——Handoff Return schema 機械驗證 / 陳述-行動機械比對 / held-out 泛化抽驗 workflow 均未落地。G-LoopA 四重疊加條件的統一狀態機不存在（PROFILES 三門檻標「待校準（建議值）」）。Oracle 資格 / Gate 選擇稽核仍 empty。F18 action-level 仍 UNTESTED。
- **結論**：R2 讓「如何執行」的路徑更清晰，但沒有新增任何能「強制執行」的機構。7.2→7.4 反映的是「執行規劃文件的完善」，不是「執行能力的提升」。

### 2. R2 的獨特貢獻：dangling-pointer 結案 + standalone 伴讀檔

R1 After 的最大遺留問題之一是：CORE 大量指涉 PROFILES 的門檻（G-LoopA 三項、展示紀律行數、規則變更重現門檻）在 PROFILES 中沒有對應行——形成 dangling pointers。R2 補齊了全部 dangling pointers 並以「dangling-pointer 結案聲明」做了合約對帳。這是**文件基礎設施的完整性修復**，對 harness 的長期維護價值高。

GLOSSARY + ADOPTION 兩份 standalone 檔解決了 R1 之前新讀者必須同時讀 INDEX + CONCEPT-MAP + CORE + SPEC 才能理解術語的困境。現在新讀者可以：GLOSSARY 查詞 → ADOPTION 選路徑 → 按路徑讀對應文件。清晰度從 7.3→7.6（+0.3）是合理的。

### 3. 仍未解決的紅燈（與 R1 After 相同，但更完整地明文化）

| 紅燈 | R1 狀態 | R2 狀態 | 變化 |
|------|---------|---------|------|
| F7/F15 行為軸 UNVERIFIED | #2c open | #2c open（更明確：不依賴 #3 即可獨立執行） | 僅文件細化 |
| #3 Dynamic Workflows | open | open | 無變化 |
| #14 ChatGPT surface calibration | open | open | 無變化 |
| #13 counterfactual BLOCKED-ENV | open | open | 無變化 |
| F18 action-level UNTESTED | 存在但未明文化於 backlog | 已明文化為 F18-action backlog 項 | 治理改善（缺口不再隱藏） |
| Raw-packet 已刪 vs 全量 trace 張力 | 存在但無政策 | #13-packet 政策 stub 建立（承認張力、不造假包） | 治理改善（張力被文檔化） |

### 4. 與 R1 After consensus 的一致性

R2 After 與 R1 After consensus（BEFORE-AFTER-REREVIEW-2026-07-20.md）的結論一致：
- 「F7/F15 行為分未知 — hooks 是 lexical，可被換寫法繞過；須隔離重跑」
- 「#3 Dynamic Workflows — Handoff schema / statement-action 機械比對仍缺」
- 「ChatGPT #14 — 三 surface 零實測」
- 「Raw packet / #13 counterfactual — 證據鏈與 v4>v3 行為宣稱仍缺」
- 「F18 action — 仍 response-level」

R2 沒有解決任何上述紅燈——它把它們**寫得更清楚、更難被忽略**。這是治理改善，不是行為改善。

---

## 建議（最低優先序，延續 R1 路線）

### P0 — 結構性風險（1-2 週，承接 R1 P0）

1. **#2c held-out rerun（F7/F15/F19/F20，n≥3 per cell）**：這是 R1 After 的 P0 建議、R2 仍未執行。advisory lexical hooks 落地後從未在隔離條件下驗證是否改善紅軸行為。F7 三輪穩定 FAIL（跨 Round 1/2/snapshot）強烈暗示 advisory 天花板已觸及——只有 hard-block hook 或 held-out workflow 才可能移動此軸。#2c 是驗證「hooks 是否值得升 hard-block」的唯一證據來源。SPEC 已明標 #2c 不依賴 #3 全基座即可獨立執行。

2. **F18 action-level sandbox 建置或 L1 降格**：繼承軌跡是 v4 擴大威脅模型的兩大新 drift 向量之一，對應 fixture 的 action-level 從未驗證。要嘛建一個允許 commit + 真實 hook 執行的 sandbox 環境，要嘛在 CORE §2 繼承軌跡條文加註「action-level evidence unverified」。

### P1 — 證據鏈完整性（2-4 週）

3. **#13-packet 最低保留集合落地**：政策 stub 已存在（EXPORT §0.5），但最低保留集合（manifest hash + transcript hash + model/runtime pin + artifact hash + public timestamp）仍未落地。在下次跨模型 eval 之前落地，避免重蹈「跑完即刪、只剩摘要」的 reward-hacking 路徑。

4. **PROFILES G-LoopA 三門檻從「待校準」升為「已校準」**：目前三門檻（迭代上限 / 預算上限 / 無進展門檻）全部標「待校準（建議值）」。需要至少 n≥3 自主 loop 數據（如 skill-audit 自動化 Routine）來賦值。在此之前，G-LoopA 的終止條件仍是「有條文、無可操作門檻」的半成品。

### P2 — 可攜性補洞（4-8 週）

5. **#14 ChatGPT 三 surface 校準（至少 chat-only 子集）**：ADOPTION §1 已提供清晰的採用路徑，CHATGPT §3 有可貼用 block + COPY-SAFETY HEADER。下一步是實際跑 chat-only 子集 fixtures 並記錄 receipt。chat-only 無法自行產生 action artifact 的問題已在 CHATGPT §6.1 有 protocol 設計——需要外部 runner 或人工操作員執行 deterministic_check。

### P3 — 戰略性強化（8-12 週）

6. **#3 Dynamic Workflows 最小可行版本**：首個 workflow 建議為 `held-out-generalization-probe`（F7/F20 泛化抽驗機械化）。即使不建完整基座，一個能獨立執行「貼 fixture input → 收 agent 產出 → 跑 deterministic_check → 記錄結果」的 workflow 腳本也能解決 #2c 的手動重跑瓶頸，並作為 #3 的 incremental proof-of-concept。

---

## 結語

R2 After 是一次**乾淨的文件收斂**——它沒有試圖用文件改寫來偽裝行為改善（unverified_success 的自我應用），而是在不改變任何行為軸分數的前提下，把 harness 的「地圖」畫得更完整：GLOSSARY 讓術語可查、ADOPTION 讓路徑可走、PROFILES 讓門檻可找、SPEC 讓缺口可見、INDEX 讓檔案可發現。

這輪收斂的正確評價不是「R2 解決了什麼」，而是「R2 讓還沒解決的東西更難被忽略」。#2c / #3 / #13 / #14 / F18-action / #13-packet 六項 open backlog 現在全部在 INDEX / SPEC / EXPORT / ADOPTION / EVAL-BASELINE 五處交叉引用——任何讀者都會撞到它們。這是治理面的誠實改善，它讓「設計層 forward canonical」這個定位有了更完整的文檔支撐。

但 harness 的最大結構性問題（`[E]` 條文三分之二無 hard-block Body）仍然存在。G-LoopA 的終止條件仍然是「條文已寫、門檻待校準」。F7 仍然三輪紅。v4 仍然是「最好的 advisory prompt」，距離「可 enforce 的行為契約」還差 backlog #2c 的行為證據 + #3 的機械基座。

R2 把地圖畫清楚了。下一步是走路。

---

**完成標籤**：`unverified_success` — 本審閱為文件層差分分析，未跑 fixtures，未修改任何檔案。行為軸分數來自既有 EVAL-BASELINE（20/22 point estimate，n=1 per cell，CI n/a），非本輪重測。

**檔案讀取清單**（絕對路徑，全部讀完）：
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/HARNESS-CORE-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/SPEC-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/PROFILES-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/EVAL-BASELINE-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/GLOSSARY-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/ADOPTION-GUIDE-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/HARNESS-EXPORT.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/reviews/DEEPSEEK-V4PRO-REVIEW-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/reviews/BEFORE-AFTER-REREVIEW-2026-07-20.md`

---

*DeepSeek V4 Pro · After Re-Review · 2026-07-21*
