# ChatGPT 5.6 Sol 審閱報告：The Loop Harness v4

> 審閱者：ChatGPT 5.6 Sol（chatgpt-5.6-sol-coordinator）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件；並針對 `CHATGPT-HARNESS-v4.md` 進行 OpenAI 官方文件合規性比對
> 狀態：read-only audit；未重跑 fixture

---

## 整體分數：8 / 10

The Loop Harness v4 是一份工程紀律嚴格、智識誠實度高的行為契約。北極星「換模型不失真」在 L1/L2 分層、`[P]`/`[E]` 二分、MBH 公理與跨模型失真點清單中被一致貫徹。eval pack 22 軸 + 兩輪 baseline + supplemental 牆 + counterfactual blocked 標記，展現了同類工作中罕見的自我稽核深度。CHATGPT-HARNESS-v4.md 在大方向上正確（surface 分級、advisory 定位、reasoning.effort vs reasoning.mode 獨立、tools 須 request-provided、Sol/Terra/Luna 角色起點），但對 ChatGPT/Responses API 平台原語的具體映射偏薄，且尚未在任一 ChatGPT surface 實跑 fixtures——這是它自報 `uncalibrated/advisory` 的原因，也是尚未 ready 的主因。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 8 | 六階段 + Johari 四象限 + 11 技巧索引 + cache 五禁令 + 治理 + 22 fixtures 齊備。開口：core.md 無獨立 stop-condition 段（G-LoopA）、`.claude/workflows/` 未落地（G-WF）。 |
| 清晰度 | 8 | L1/L2/L3/L4 分層清楚；`[P]`/`[E]` 標記與 MBH 總綱一致。代價：文件密度高，預設讀者已吸入大量 context。 |
| ChatGPT 合規性 | 7 | 核心宣稱（Sol/Terra/Luna、effort≠mode、max=effort/pro=mode、tools 需 request-provided、surface-aware 降級、uncalibrated）逐一對照 OpenAI 官方文件屬實。缺口：未涵蓋 `reasoning.context` / `previous_response_id` / `phase` / `reasoning.summary` / `max_output_tokens` 等關鍵平台原語。 |
| 可執行性（enforcement boundary 區分） | 8 | `[P]`/`[E]` 二分 + adapter §6 enforcement boundary 表 + CORE §7 降級條款一致。缺一星：ChatGPT adapter §6 表比 CORE 的 `[E]` 標記抽象，未逐一對應平台原語。 |
| 跨模型可攜性 | 9 | L1 零模型名/零平台名/零數字/零 inline 引註；PROFILES 用 cost/quality/ceiling/frontier 抽象檔位；HARNESS-EXPORT 跨模型失真點清單逐條列補償層。 |
| 可測試性 / 評估包 | 8 | 22 軸 fixture + 24-case oracle 資格化 + F23–F27 正確範式。扣分：F7 兩輪穩定紅、F15 本輪轉紅、F18 action 未驗、n=1 無 variance。 |

---

## 最大優點（5 項）

1. **可攜性紀律落到字句層**：L1 鐵律「零模型名、零平台功能名、零可調校數字門檻、零 inline 引註」並附顯式豁免範圍，是可稽核的條文而非口號。
2. **智識誠實的 eval 自評**：自報 baseline 20/22 並列紅軸；明寫 F15 為單樣本翻轉、不宣稱 F19 轉綠係新條文所致；F23–F27 嚴格牆外；counterfactual 標 BLOCKED-ENV 不外推 v4>v3。
3. **威脅模型擴大到非顯式注入**：價值訴求（F14）與繼承軌跡（F18）兩大 drift 向量，超越業界常見的「ignore previous instructions」級防禦。
4. **CHATGPT-HARNESS-v4.md 的核心合規判斷正確**：Sol=flagship、Terra 平衡、Luna 高量（confirmed）；`reasoning.effort` 與 `reasoning.mode` 獨立（verbatim confirmed）；API tools 須 request-provided（confirmed）。
5. **裝完成捷徑具名清單 + 未見輸入泛化抽驗**：TEST 段把 11 種 fake-done 捷徑逐項列名，並加「對給定測試輸入做字面特判」+ 未見輸入泛化抽驗；F7/F20 直接測此。

---

## 最大缺口 / 風險（10 項）

| 嚴重性 | 缺口 | 涉及檔案 |
|--------|------|----------|
| HIGH | 漏掉 `reasoning.context` / `previous_response_id` / `store=false` / `encrypted_content`——CORE 目標外錨/cache-safe fork 在 API surface 的天然落地點 | `CHATGPT-HARNESS-v4.md` §1, §6 |
| HIGH | 漏掉 `phase: "commentary" / "final_answer"`——與 CORE 展示紀律 1:1 對應的平台原語 | `CHATGPT-HARNESS-v4.md` §3 |
| HIGH | 漏掉 `max_output_tokens` / `incomplete` status 作為裝完成捷徑向量 | `CHATGPT-HARNESS-v4.md` §3 |
| HIGH | 路由表漏掉預設 `gpt-5.6`（standard），直接跳 Sol/Terra/Luna | `CHATGPT-HARNESS-v4.md` §4 |
| MEDIUM | 「Using GPT-5.6」連結標籤與目標頁不符（實為 Model guidance） | `CHATGPT-HARNESS-v4.md` §1, §4 |
| MEDIUM | effort 梯度只列 `max`/`high`，漏 `none/minimal/low/medium/xhigh` | `CHATGPT-HARNESS-v4.md` §4 |
| MEDIUM | 未命名 ChatGPT 內建工具目錄與 Memory 功能 | `CHATGPT-HARNESS-v4.md` §1, §6 |
| MEDIUM | F7/F15 紅軸，harness 自身 TEST 閘在無 enforcement 時不可靠 | `EVAL-BASELINE-v4.md`, `HARNESS-CORE-v4.md` §1 TEST, `SPEC-v4.md` §6 #2b/#3 |
| MEDIUM | ChatGPT target-surface calibration 從未實跑（backlog #14 OPEN） | `CHATGPT-HARNESS-v4.md` §5/§7, `SPEC-v4.md` §6 #14 |
| LOW | §7 已知限制混入 Codex CLI 證據，易誤讀為 ChatGPT surface 證據 | `CHATGPT-HARNESS-v4.md` §7 |

---

## 優先排序改善計畫

### P0（直接阻擋 ChatGPT surface calibration）

1. **CHATGPT-HARNESS-v4.md §6 新增「平台原語映射表」**：goal anchor → `previous_response_id` + `reasoning.context: all_turns` / `store=false` + `encrypted_content`；展示紀律中間靜默 → `phase: "commentary"`；終局出示 → `phase: "final_answer"`；記憶治理 → ChatGPT Memory + `reasoning.summary`；裝完成捷徑向量 → `status: incomplete` + `max_output_tokens` 偵測。
2. **§4 路由表補預設 `gpt-5.6`（standard）列**：明引 OpenAI 官方「Start with gpt-5.6 for most reasoning workloads」，並補 effort 7 階清單（none/minimal/low/medium/high/xhigh/max）。

### P1（合規性與可執行性）

3. **§1 Surface 矩陣補 ChatGPT 內建工具目錄**：web search / Code Interpreter / file search / image generation / computer use，註明 plan-gating 與 rollout 變動性。
4. **§6 記憶治理列命名 ChatGPT Memory**：Chat-only 欄改「不把 ChatGPT Memory 當 ground truth；Memory 可被使用者清除/關閉」；API 欄補 `reasoning.summary` 作可稽核推理摘要來源（非 ground truth）。
5. **§3 可貼用核心補 `incomplete` 偵測條文**：API/Codex agent 宣告完成前檢查 `response.status !== 'incomplete'`；對應補 F26 候選 fixture。

### P2（一致性與可讀性）

6. **§7 拆段**：「§7a 跨 runtime 證據邊界（Codex CLI，不可外推 ChatGPT）」與「§7b ChatGPT surface 真實已知限制（無 baseline）」。
7. **§4 連結標籤修正**：「Using GPT-5.6」改標「Model guidance（含 GPT-5.6）」或指向 `/guides/reasoning`。
8. **針對 F7/F15 紅軸加 surface-specific 警示**：chat-only / tool-enabled surface 對 F7/F15 類任務預期紅軸，須人工覆核。

### P3（harness 整體）

9. **CORE §1 補獨立 stop-condition 段（G-LoopA）**：補 verifier 通過 / 迭代上限 / 預算上限 / 無進展偵測四重疊加 stop 條件。
10. **執行 ChatGPT target-surface calibration（backlog #14）**：三 surface 各跑 F1–F22 + 代表任務，產出第一份 ChatGPT baseline；完成前 adapter 維持 `uncalibrated/advisory`。

---

## CHATGPT-HARNESS-v4.md 是否 ready for ChatGPT surface calibration？

**結論：尚未 ready；可作為 calibration 實驗的 prompt 起點，但缺三件前置物。**

已具備：
- 正確的 surface 分級與降級語義；
- 正確的 advisory 定位與「未跑 fixtures 不得宣稱驗證」紅線；
- 核心平台事實（Sol/Terra/Luna、effort≠mode、tools 需 request-provided）經官方文件比對屬實；
- 可貼用核心 prompt（§3）可直接作為 calibration 被測 prompt。

尚缺（必須補完）：
1. **平台原語映射表**（P0-1）：把 CORE `[E]` 條文逐一映射到 Responses API 原語。沒有這張表，calibration 跑的是「advisory prompt 在 ChatGPT 上的服從率」，不是「advisory prompt + 平台 Body 的完整 harness」。
2. **預設 `gpt-5.6`（standard）+ effort 7 階完整梯度的路由起點**（P0-2）：現表只列三模型 × 兩 effort，實驗設計會漏軸。
3. **針對 harness 自身紅軸（F7/F15）的 surface-specific 預期標註**（P2-8）：否則 calibration 結果會被誤讀為「ChatGPT 特有退化」而非「harness 已知紅軸的跨 surface 重現」。

補完上述三項後，adapter 即可進入 backlog #14 實跑流程；實跑產出第一份 ChatGPT 三 surface baseline 後，status 始可從 `uncalibrated/advisory` 改為 `calibrated/<date>`。在那一刻之前，任何「ChatGPT/GPT-5.6 已驗證本 harness」的讀法均不成立。
