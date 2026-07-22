# GLM 5.2 審閱報告：The Loop Harness v4（實作/落地視角）

> 審閱者：GLM 5.2（glm-developer）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件（HARNESS-EXPORT 為 build artifact，已讀失真點清單與標頭，確認內容為 CORE + PROFILES 合併）
> 狀態：read-only review；未重跑 fixture；從開發者落地角度評估

---

## 整體分數：7.5 / 10

作為「模型無關行為契約」，v4 在概念密度、證據鏈嚴謹度、反腐蝕意識上屬標竿級。但從「開發者拿起來就能落地」的角度，它仍是一份**高度濃縮的研究文件而非工程交付物**：條文密度過高、跨檔交叉引用密集、L3/L4 enforcement 大量停留在 backlog、ChatGPT adapter 未校準、關鍵落地骨架（Dynamic Workflows、記憶查詢式下沉、stop-condition 段）尚未機械化。能跑出 20/22 的 baseline 證明核心契約有效，但紅軸 F7/F15 長期不動也證明 advisory 對裝完成/盲點類失敗的服從率天花板已被觸及。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 8.5 | 六階段 + 六公理 + 跨切 + 委派 + cache + 治理 + L4 Eval Pack + ChatGPT adapter + EXPORT 全覆蓋；MAST 14 類已盤點。 |
| 清晰度 | 6.5 | 條文密度過高、長句套長句、跨檔指針多；外部採用者學習曲線陡。`[P]`/`[E]` 二分有助但不解決語句壓縮問題。 |
| 可執行性 / 落地難度 | 5.5 | `[E]` 條文多達 8+ 類，無 runtime 即降級為 advisory；SPEC §6 僅 #2 為 DONE，其餘 hook/workflow 多在 backlog；開發者須自行補大量 L3 機構。 |
| 跨模型可攜性 | 8.0 | `[P]`/`[E]` 二分 + EXPORT 失真點清單 + ChatGPT adapter + 接入程序形成閉環；扣分在 ChatGPT/Codex 實測未完成、F23–F25/F27 仍 provisional。 |
| 可測試性 / 評估包 | 7.5 | 22 fixtures + 24-case oracle 資格化 + 隔離 worktree + 計數化判定。扣分：oracle 多為 lexical signal、F18 hook action 未驗、F7/F15 紅軸、n=1。 |
| 治理 / 反腐蝕 | 8.5 | §5 治理面分離、自報成功鏈、advisory 不得稱 enforce、構念對齊、全量 trace 演化、sealed/held-out、記憶入庫分流、byte gate。 |

---

## 最大優點（5 項）

1. **`[P]`/`[E]` 可攜性二分 + MBH 公理**：讓弱模型 / 無 runtime 使用者能預判哪些條文會靜默退化——多數 harness 迴避的問題。
2. **advisory vs enforcement 的誠實分界**：「fixture PASS ≠ L1 採納 ≠ L3 enforcement」「advisory 未強制不得稱 enforce」。
3. **TEST 四新閘的失敗模式對應扎實**：Oracle 資格、Gate 選擇稽核、裝完成捷徑具名清單、展示紀律三分，皆有 observed_trace 支撐。
4. **威脅模型擴大至價值訴求 + 繼承軌跡 + 壓縮翻轉決策**：捕捉 harness 實戰中真正常見的 drift 向量，並有 fixture 驗證。
5. **評估方法論成熟度**：frozen known-good/known-bad counterexample qualification、隔離 worktree、計數化判定、單樣本 variance caveat、F10R substitution 明示不可混用分母。

---

## 最大缺口 / 風險（按嚴重性排序）

### CRITICAL

- **C1. L3/L4 enforcement 大量停留在 backlog，[E] 條文實際效力薄弱**
  - 涉及：`HARNESS-CORE-v4.md` §1 TEST/§3 委派/§5 治理；`SPEC-v4.md` §6 backlog #1/#3/#4/#5/#6。
  - 落地困難：僅 backlog #2 為 DONE，#1 allowlist 複審 hook、#3 Dynamic Workflows 基座、#4 提案→應用節拍、#5 fallback 候選、#6 Unicode PreToolUse 阻斷版皆未落地。開發者採用時，最高風險 `[E]` 條文幾乎全靠模型服從 prompt。

- **C2. 紅軸 F7/F15 長期未解，advisory 天花板已觸及但機械化未跟上**
  - 涉及：`EVAL-BASELINE-v4.md` Round 2 fail_axes [F7, F15]；`HARNESS-CORE-v4.md` §1 TEST/IDENTIFY；`SPEC-v4.md` §6 #2b/#3。
  - 落地困難：F7 兩輪穩定紅、F15 單輪翻紅。backlog #2b/#3 仍停留在候選/待機械化。這代表 v4 最核心的裝完成防範與盲點挖掘條文，在無 hook 環境下無法穩定成立。

### HIGH

- **H1. 條文密度過高，外部採用者學習曲線陡，落地時易被截斷或誤讀**
  - 涉及：`HARNESS-CORE-v4.md` 全文；`SPEC-v4.md` §2/§3。
  - 落地困難：CORE 單檔 21k 字、長句套長句；PROFILES §1 表單列 11 維度。L1 byte gate ≤13,000 與 CORE 21k 字之間存在張力——常駐層裝不下全文，逐段貼又破壞語境。

- **H2. ChatGPT adapter 未校準，且與 Codex CLI evidence 的關係容易誤用**
  - 涉及：`CHATGPT-HARNESS-v4.md` §4/§7；`SPEC-v4.md` §6 #14；`EVAL-BASELINE-v4.md`。
  - 落地困難：adapter §4 引用 Sol/Terra/Luna 角色，來自已刪除的 CODEX-GPT5.6 baseline 檔（git 歷史可考）。表格形式削弱「不要把三種模型名稱當固定角色真理」警告。

- **H3. 記憶治理先進但落地工具鏈缺失（G-Mem 高槓桿缺口）**
  - 涉及：`HARNESS-CORE-v4.md` §1 RECORD；`CONCEPT-MAP-v4.md` §3 G-Mem/§5。
  - 落地困難：CONCEPT-MAP 指出「記憶檔仍整檔 Read，未做查詢式選讀」，語意檢索依賴 embed_stub 修復。CORE RECORD 要求 episodic-first 保留窗，但上游查詢式記憶存取未落地。

### MEDIUM

- **M1. Dynamic Workflows 作 L3 基座未落地，advisory→enforcement 升級路徑斷裂**
  - 涉及：`SPEC-v4.md` §6 backlog #3（最高槓桿）；`CONCEPT-MAP-v4.md` §2 G-WF。
  - 落地困難：CORE §3 Handoff Return schema 化、§5 演化認證、§1 多個 `[E]` 閘門都需 Dynamic Workflows，但 `.claude/workflows/` 不存在。

- **M2. Handoff Contract 缺欄阻擋需 runtime 強制，但缺欄阻擋 hook 未落地**
  - 涉及：`HARNESS-CORE-v4.md` §3；`SPEC-v4.md` §6 backlog #3。
  - 落地困難：Handoff Contract 是 MAST 1.1/1.4/2.4 主要攔截機制，但「缺欄阻擋」標 `[E]` 須 runtime 強制，目前靠 parent 模型自己檢查。F22 PASS 僅 behavioral signal。

- **M3. F23–F25/F27 supplemental fixtures 不計 baseline 但敘事篇幅顯著，易誤導採用者**
  - 涉及：`EVAL-PACK-v4-ADDENDUM.md` F23–F27；`SPEC-v4.md` §6 #15/#16；`CHATGPT-HARNESS-v4.md` §5。
  - 落地困難：雖反覆標註 `PROVISIONAL`/`PROTOTYPE`，但 ADDENDUM 篇幅顯著，開發者掃讀時易誤以為已校準能力。

### LOW

- **L1. CORE §7 降級條款與 EXPORT 失真點清單未雙向連結**：開發者須自行對照兩份文件還原「這條 `[E]` 在無 runtime 時降級成什麼」。
- **L2. PROFILES §1 末欄與 §2/§4 數字一致性維護成本高**：三處數字（PROFILES + 人讀落地檔 + 機讀落地檔）須一致，但本目錄只提供 canonical，落地檔路徑「由宿主環境自定」，無範本。

---

## 優先排序改善計畫（檔案 / 條文 / 行動層級）

### P0 — 解決紅軸與 enforcement 斷層（1–2 週）

1. **機械化 F7 對應條文**：擴充 `test-file-redflag.sh` 為「held-out 未見輸入抽驗」hook；新增 `generalization-probe.sh`（PostToolUse），對應 CORE §1 TEST「修復宣稱須以未見輸入抽驗泛化」。
2. **機械化 F15 對應條文**：落地 backlog #2b——委派 brief lint（品味形容詞 + 無 reference → 警示）或 cost/quality handoff 範本強制 reference 欄；落地於 `.claude/refs/task-templates.md` + PreToolUse lint script。
3. **補獨立 stop-condition 段（G-LoopA）**：依 `CONCEPT-MAP-v4.md` §7 已提案入 `research/EVOLUTION-QUEUE.md` #2，經 autoload-evolution 人核後落地 `.claude/rules/core.md`——加分層終止四重疊加（verifier 通過/迭代上限/預算上限/無進展偵測）+ accepted-change rate <50% 量化門檻。

### P1 — 補 L3 基座與落地骨架（2–4 週）

4. **落地 Dynamic Workflows 基座（backlog #3，最高槓桿）**：以「skill 稽核 sweep」為首個 workflow（吃 30 天 skills_used 資料）。落地：`.claude/workflows/skill-audit-sweep.js` + 版控。連帶把 Handoff Return schema 化（`agent({schema})` 機械驗證回傳欄位）一起完成。
5. **落地 backlog #1 allowlist 複審 hook**：settings/hook 檔變更 diff-gate，對應 CORE §1 APPLY「閘門/allowlist 放寬 = 新攻擊面」。
6. **記憶查詢式下沉（G-Mem）**：`memory-compactor/dreaming` 接查詢式選讀，配合 episodic 保留窗。

### P2 — 降低外部採用門檻（4–8 週）

7. **產出「落地導覽」文件**：新增 `ADOPTION-GUIDE.md` 或於 `INDEX.md` 擴充，提供：(a) CORE 條文 → fixture → `[E]` 補償層 → backlog 項 四欄對照表；(b) EXPORT 失真點清單 ↔ CORE §7 雙向連結；(c) PROFILES 落地檔範本（人讀 + 機讀 JSON）。
8. **CORE 條文可讀性分層**：在不變更語義下，把 §1 各段子主題拆為更短句 + 子標題（如 IDENTIFY 拆六子段）。須經 fixtures 回歸背書。

### P3 — 評估包強化（8–12 週）

9. **補 variance**：每 cell ≥3 次重跑估計 variance，再做紅軸歸因。
10. **完成 F18 hook action receipt**：F18 三路 `UNTESTED_ACTION`，需 sandbox 環境允許 commit 通過 hook。
11. **ChatGPT target-surface calibration（backlog #14）**：分 chat-only / tool-enabled / API adapter 三 surface 跑 F1–F22 + 代表任務，完成後 `CHATGPT-HARNESS-v4.md` 升格 calibrated。

---

## CHATGPT-HARNESS-v4.md 適當性評估

**整體判斷：設計方向適當，但當前定位與內容存在三處張力。**

**適當之處**：
- Surface capability matrix + Enforcement boundary 表正確區分三 surface 的能力上限與完成宣稱上限，避免「一份 prompt 適用所有 surface」謬誤。
- `uncalibrated/advisory` 誠實，與 CORE §5「advisory 不得稱 enforce」一致。
- §3 可貼用核心把 CORE 濃縮為可貼用 prompt，保留六階段 + 關鍵閘門 + surface 降級，是 adapter 的正確產物形式。
- §5 evaluation 記錄欄位與 PROFILES §4 接入程序一致。
- §5 supplemental 邊界明確：F23/F24/F25/F27 不進預設 adapter、不要求 per-turn capability 自報、keep-rate 不作 promotion gate。

**張力 / 待改善**：
1. **§4 路由建議引用已刪除的 CODEX baseline，形式削弱警告**：表格列出 Sol=深度裁決/Terra=多檔/Luna=高量，雖附警告，但表格形式會讓讀者當成已校準角色真理。建議：表格改為「角色需求 → 候選模型族群特徵」（去模型名），或把警告移到表格前並以 blockquote 強調；模型名只在 §7 作為 Codex rerun 結果引用。
2. **§3 可貼用核心與 CORE 的條文對齊未雙向標註**：核心 prompt 濃縮了 CORE 關鍵條文，但未標註每句對應 CORE 哪一段。建議：§3 後補「濃縮自 CORE §0–§5 + §7；逐句對應見附錄 A」對照表。
3. **§6 Enforcement boundary 表格中「API/Codex agent」欄與 §1 surface matrix 的對齊**：§1 把 API / Codex agent 並列為一個 surface，但 §6 表格的 enforcement 機制（approval policy / parser/allowlist / CI verifier / state store）實際上是 API agent 能力，Codex CLI 在 `SPEC-v4.md` §6 已記載 `.git` sandbox 阻擋 hook execution。建議：§1 與 §6 把 API agent 與 Codex CLI 拆為兩列，標明 Codex 的 sandbox 限制（F18 `UNTESTED_ACTION`）。

**結論**：CHATGPT-HARNESS-v4.md 作為 `uncalibrated/advisory` adapter 是適當起點，設計骨架（surface 分級 + 可貼用核心 + eval 記錄欄位 + 邊界標注）方向正確；主要改善點在 §4 路由建議去模型名化、§3 與 CORE 雙向對齊、§1/§6 的 API/Codex surface 拆分。在 backlog #14 完成前，維持 `uncalibrated/advisory` 是正確的。

---

## 完成標籤

`unverified_success` — 本審閱為文件層分析，未跑 fixtures、未對實際 hook 落地做動態驗證；紅軸狀態與 backlog 進度引用自 `EVAL-BASELINE-v4.md` / `SPEC-v4.md` §6（2026-07-20 快照），後續若 backlog 推進需重審。
