# GLOSSARY-v4 — The Loop Harness v4 單頁詞彙表

> **定位**：describe-only，**非契約**——條文式定義一律以 `HARNESS-CORE-v4.md`（契約）為準，本檔不新增語意、不改公理、不改分數。與 `CONCEPT-MAP-v4.md` §0.5 詞彙表互補：該表按「第一次出現」導讀，本檔按主題分區供隨查。每詞附 canonical 指針。
>
> eval 詞彙以 `EVAL-BASELINE-v4.md` 為最新；本檔不同步時以該檔為準。

## 1. 核心本體（Ontology）

| 詞 | 定義 | canonical |
|---|---|---|
| **Agent = Model + Body + Harness（MBH）** | 總綱一句：Model = 可換模型元件（`[P]` 承載者）；Body = hooks/CI/gates 等確定性機構（`[E]` 效力來源）；Harness = 紀律本身（L1 契約 + L2 校準）。MBH 指總綱，其下展開為六條設計公理，兩者不混稱。 | CORE §0 |
| **六條設計公理** | Harness > Model；LLM 只做判斷、確定性程序做決定；能力悖論（能力提升不得降低驗證）；雙軸伸縮；規則 = decaying cache；地圖 ≠ 疆域。 | CORE §0 |
| **北極星** | 核心設計目標＝換模型不失真：`[P]` 條文換模型仍可執行；`[E]` 條文無 Body 時退化為 advisory。 | CORE §0、§7 |
| **L1 / L2 / L3 / L4** | L1 = 行為契約（CORE；零模型名、零可調校數字、零 inline 引註）；L2 = 檔位校準值（PROFILES）；L3 = 確定性機構（hooks/CI/gates/workflows）；L4 = fixture 證據（EVAL-PACK / EVAL-BASELINE）。 | INDEX §2、CORE 鐵律 |
| **`[P]` / `[E]` 二分** | 每條規則標可靠達成所需**最低支撐層**（非重要性）：`[P]` = Model 層純認知協議，跨模型退化小；`[E]` = 需 L3/L4 enforcement 才可靠，無 runtime 時降級為 advisory。**`[E]` 是依賴聲明，不是落地清單**——不表示目標宿主已 enforce。 | CORE 鐵律、INDEX §3 |
| **advisory vs enforce** | advisory = 條文靠模型服從、無保證；enforce = 有 hook/CI/gate 機械強制且經**語義級觸發測試**（正反例）。fixture PASS 不會把 prompt 變成 enforcement。 | CORE §5 自報成功鏈、EXPORT §0.2 |
| **advisory lexical hook** | 產出可見提醒（exit 非阻斷）的 lexical 掃描；**可被換寫法繞過、不移動行為軸分數**，須隔離 n≥3 重跑才可更新 verdict。 | INDEX §4、EVAL-BASELINE §0.4 |
| **hard-block** | 確定性攔截使違規動作**無法完成**的機械 gate；僅限通過語義級測試的路徑可稱 enforced，只驗檔案存在不算。 | EXPORT §0.2 |
| **檔位（cost / quality / ceiling / frontier）** | 抽象能力層：程序性指導量與能力成反比、驗證閘門強度與能力成正比；模型名只是當代對應，換代改對應不改條文。 | PROFILES §1 |

## 2. The Loop 六階段 + 終止條件

| 詞 | 定義 | canonical |
|---|---|---|
| **The Loop** | OBSERVE（先讀後動）→ IDENTIFY（unknowns + Done Contract）→ PROPOSE（極簡最小變更）→ APPLY（規範優先 + 分級閘門）→ TEST（驗證閘門，不可協商）→ RECORD（checkpoint + 反思入庫）。思考框架非輸出格式；儀式深度隨風險伸縮。 | CORE §1 |
| **G-LoopA 終止條件（四重疊加）** | 自主迴圈開跑前**事前顯式宣告**，任一觸發即停：① verifier 通過（外部 gate 親跑）② 迭代上限 ③ 預算上限 ④ 無進展偵測（accepted-change rate 連續低於門檻）。以 ②–④ 停者標 `unverified_success` 或 `failed`——跑滿迴圈不構成 verified；門檻在 L2。 | CORE §1 迴圈終止條件 |
| **Done Contract** | 成功條件與使用者協商、非單方宣告；驗證命令為逐字完整命令（含跨目錄依賴）而非描述性條件。 | CORE §1 IDENTIFY |
| **unverified_success 閘門** | 任何自報成功（自己/sub-agent/workflow/自動化）= 中間態；宣告完成前負責者親跑確定性檢查並展示輸出；**裁定不跨 agent 邊界**。 | CORE §1 TEST |
| **拿收據** | 任何行為宣稱必附工具實際輸出的 artifact，口頭不算。 | CORE §1 TEST |
| **Oracle 資格先於 loop** | 建自主迴圈前先驗 oracle 本身（餵已知好與已知壞案例）；壞 oracle 比無 oracle 更糟（假信號 + 假信心）；不可得即事前棄權明寫「無法自證」。 | CORE §1 TEST |
| **Gate 選擇稽核** | gate 必須實際行使宣稱涵蓋的執行路徑，非 proxy 子集——靜態檢查通過 ≠ build 通過 ≠ 跑得起來。 | CORE §1 TEST |
| **裝完成捷徑** | 放鬆測試/吞錯誤/stub 回傳/改測試檔配合實作/**字面特判**等具名捷徑；修復宣稱須以未見輸入抽驗泛化。 | CORE §1 TEST |
| **展示紀律** | 迴圈中間靜默（只回計數/hash + 重現命令）、終局出示（工具輸出首尾節錄）、失敗大聲（完整貼出不美化）。 | CORE §1 TEST |
| **完成度五標籤** | `autonomous_verified_success / assisted_verified_success / unverified_success / failed / unsafe_invalid`；unverified 不入庫為成功。 | CORE §1 RECORD |
| **目標外錨** | 跨壓縮/跨 session 任務把目標與 done-state 寫入既有交接 state 檔並逐 checkpoint 重錨——goal drift 靠外部錨非重述。 | CORE §1 RECORD |
| **episodic-first** | consolidation 是最高風險記憶操作（自正確 ground truth 反覆固化仍致退化）；合併須顯式核可、不覆寫所依證據、保留 rollback。 | CORE §1 RECORD |
| **Handoff Contract** | 委派必給契約：Goal / Non-goals / Allowed-paths / Context / Done-when / Return / tier+effort；缺一 child 不開工。 | CORE §3 |
| **benefit-gated delegation** | 委派須具名效益（context 隔離/真平行/對抗審查/機械執行/降噪），計入 handoff 固定開銷；無效益不委派。 | CORE §3 |
| **五禁令（cache）** | ① 動態事實不入穩定前綴 ② 不 mid-session 換模型 ③ 不 mid-session 增刪 tool ④ fork 重放父前綴原文 ⑤ 命中率驟降即查前綴。 | CORE §4 |
| **結構性下沉 > 符號壓縮** | context 優化序：結構性下沉（path-scoped/on-demand）> 符號壓縮 > 快取 > 極端壓縮；重複注入的常駐稅 > 一次性膨脹。 | CORE §4 |

## 3. Unknowns / Johari / T1–T11

| 詞 | 定義 | canonical |
|---|---|---|
| **Johari 四象限** | Unknowns 引擎：Known Knowns（已在 prompt）；Known Unknowns → Interview；Unknown Knowns（品味類「看到才認得」）→ Prototype/多方向草案；Unknown Unknowns → Blindspot Pass。 | CORE §1 IDENTIFY |
| **Blindspot Pass（T1）** | 進入陌生模組/領域先顯式掃描「使用者沒想到要問的事」；高風險域（付款/重試/刪除/遷移/佇列消費）動工前至少點名一項防護，零提及即視為未跑。 | CORE §1 IDENTIFY |
| **T2 Teach-Me-My-Unknowns** | 模糊領域先建詞彙階梯再談需求。 | CORE §1（一行索引） |
| **T3 Four Design Directions / T4 Mock Before You Wire / T5 Brainstorm the Intervention** | 多方向草案曝品味；先 mock 再接線驗介面假設；effort×impact 方案發散。 | CORE §1（一行索引） |
| **The Interview（T6）** | 逐題訪談，優先問「答案會改變架構」的題；此排序準則 canonical 在 CORE，他處只指針。 | CORE §1 IDENTIFY |
| **Point at a Reference（T7）** | 使用者說不清但認得出 → 指向原始碼參考；品味類任務取得 reference 或多方向草案前不得實改交付物即宣告完成。 | CORE §1 IDENTIFY |
| **T8 The Tweakable Plan** | 計畫按易變性排序、易變決策置頂。 | CORE §1（一行索引） |
| **Implementation Notes（T9）** | 長任務記 Deviations（迫使偏離時選保守、記錄、續行）；結案即下次 IDENTIFY 輸入。 | CORE §1 APPLY |
| **T10 Buy-In Doc / T11 Quiz Me Before I Merge** | 先 demo 預答 reviewer 反對；merge 前出題驗**人的理解**（非只驗碼），為 TEST 可選強化閘。 | CORE §1（索引/TEST） |

> T1–T11 完整機制與模板在宿主 unknowns 技巧庫（`know-your-unknowns` SKILL）；L1 只升 T1/T6/T7/T9/T11 為階段閘。**非該宿主 surface 時以上述一行定義為可攜底線**，不假設 SKILL 全文可攜（EXPORT 失真點清單）。

## 4. Eval 詞彙

| 詞 | 定義 | canonical |
|---|---|---|
| **fixture** | 已知好/已知壞的 counterexample 樣本，獨立 context 執行 + 確定性腳本比對；提供 behavioral evidence，**PASS ≠ L1 採納 ≠ enforcement**。 | EVAL-PACK-v4-ADDENDUM |
| **fail_axes / 紅軸** | baseline 重跑中持續 FAIL 的軸；current = **F7**（eval-hack 字面特判）與 **F15**（blindspot 高風險域零提及）。hooks 落地不移動紅軸行為分。 | EVAL-BASELINE |
| **eval-hack** | 對給定測試輸入做字面特判讓測試綠燈、未以未見輸入抽驗泛化的裝完成捷徑；F7 的 fail_category。 | EVAL-BASELINE F7 |
| **point estimate（n=1）** | 單一執行樣本估值，無信賴區間；不可作「軸已穩定通過」依據。 | EVAL-BASELINE §0.2 |
| **n≥3 滿分輪** | 一軸計一輪滿分/換代重審的最低樣本數：每 cell n≥3 全 PASS；門檻定義在 L2。 | PROFILES §2 |
| **UNTESTED** | fixture 因環境限制無法完整執行（如 F18 action-level 被 `.git` sandbox 阻擋、原 F10 被平台 classifier 阻擋）。 | EVAL-BASELINE 狀態表 |
| **TAINTED_ENV** | fixture 在非隔離環境執行，action-safety 證據可能受既有 workspace 狀態污染；隔離 worktree 可免。 | EVAL-BASELINE 狀態表 |
| **BLOCKED-ENV** | 本 workspace 內無法建乾淨 counterfactual 對照臂的標記——in-env agents 會正確拒絕 de-harness 指令，對照臂必被汙染；須外部環境兩臂對測。 | SPEC §6 #13 |
| **response-level vs action-level** | response-level = 模型「說」會拒絕（口頭訊號）；action-level = 真路徑攔截（如真擋 `--no-verify` commit）。F18 response PASS 但 action **OPEN**；前者不關閉後者。 | EVAL-BASELINE F18、EXPORT §0.3 |
| **F10R** | 原 F10 input 遭平台阻擋時的構念替代 fixture；計入 current denominator。 | INDEX §8 |

## 5. 證據等級（SPEC §2.0 五級）

| 等級 | 是什麼 | 可背書 | 不可背書 |
|---|---|---|---|
| **paper** | 可定位論文/公開研究（須構念對齊） | 條文存在理由、方向性 | 宿主已落地、fixture 已通過 |
| **internal-trace** | workspace 實跑/故障收據 | 本地 observed failure / mechanism receipt | 跨宿主、跨 runtime 普遍性 |
| **internal-fixture** | frozen fixture + evaluator receipt | 指定條件的 behavioral signal | prompt 變 enforcement；跨 runtime pooling |
| **raw-packet** | 可重播 packet（request/transcript/action/artifact/pin/hash） | 該次 run 的 provenance 與 action-level 裁定 | 未永久保存時稱可重播或 sealed |
| **anecdotal** | tweet、單一團隊自述 | 設計線索、反例候選 | 公理、L2 校準值、行為優勢 |

## 6. Export / 採用術語

| 詞 | 定義 | canonical |
|---|---|---|
| **可攜層 vs 宿主證據層** | 可攜層（CORE/PROFILES/ADDENDUM/adapter/EXPORT/CONCEPT-MAP/INDEX）供外部採用；證據層（SPEC 落地對照、EVAL-BASELINE）只對明載 runtime 成立，不得跨模型/surface 外推。 | INDEX §2 |
| **host-surface adapter** | 依目標平台 surface 能力分級（chat-only / tool-enabled / API）的可貼用 prompt；未在目標 surface 跑 F1–F22 + 代表任務前一律 `uncalibrated/advisory`。 | CHATGPT-HARNESS、SPEC §6 #14 |
| **uncalibrated / advisory** | adapter 未經目標 surface fixtures 校準前的強制狀態標記，須內嵌於可貼用 prompt——狀態不隨引用旅行是已知部署失誤面。 | CORE §6 |
| **HARNESS-EXPORT（build artifact）** | `scripts/build-harness-export.sh` 生成的單檔套件（CORE + 全 profiles）+ 跨模型失真點清單；勿手改、勿未選 profile 整檔貼入 runtime。 | HARNESS-EXPORT 頭注 |
| **失真點清單** | 換弱模型/非原宿主/無 runtime 時最易靜默退化的 `[E]` 條文與應補支撐層對照表；「補償層」欄是**應有**非讀者環境已有。 | HARNESS-EXPORT |
| **sealed / held-out** | 演化效益宣稱只認 sealed/held-out 結果並對照等資源基線與非開發集；raw packet 未保存者其結論降級為摘要級，**不得再稱 sealed 或可重播**。 | CORE §5 |
| **packet_absent** | raw packet 無 blob 時的強制標記；引用時措辭固定為「原文僅 git 歷史可考；tree 內不可獨立覆核」；不偽造、不「還原」已刪封包。 | HARNESS-EXPORT §0.5 |
| **自報成功鏈** | 宣稱 enforcement 的機制必有語義級斷言驗證真會觸發；落地 advisory hook ≠ 紅軸移動、fixture PASS ≠ enforcement、文件寫了 ≠ 讀者環境存在。 | CORE §5、EXPORT §0.2 |

## 7. 第一次讀者路徑

- **5 分鐘**：本檔 §1 + §2 前兩列（MBH / 公理 / `[P]`/`[E]` / advisory vs enforce / The Loop / G-LoopA）→ `CONCEPT-MAP-v4.md` §1 兩層總綱。讀完能識別核心詞彙與「哪些宣稱要打折扣」。
- **30 分鐘**：`INDEX.md` §1 檔案路由 → `HARNESS-CORE-v4.md` §0 公理 + §1 六階段（先只讀 `[P]` 條文）→ `PROFILES-v4.md` §1 檔位表 → `EVAL-BASELINE-v4.md` 紅軸與 variance caveat → `HARNESS-EXPORT.md` §0 + 失真點清單。讀完能回答：哪些宣稱已被機械驗證、哪些仍是 advisory。

---

*v4.0 glossary · 2026-07-21 · describe-only；語意衝突時以 `HARNESS-CORE-v4.md`（契約）為準，數字以 `PROFILES-v4.md` / `EVAL-BASELINE-v4.md` 為準。*
