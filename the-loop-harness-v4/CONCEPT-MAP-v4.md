# Harness Concept Map v4 — 7 概念 × 「最新思路 / 本 harness 實現 / gap」

> **產出**：2026-07-20 一次實戰任務（Loop Engineering 教學 + 自我稽核）的 Phase 1 交付，2026-07-21 為落地可讀性重寫。
> **方法**：多個 fresh-context agent（discovery 檔位盤點 + 多個執行檔位概念 mapper）併行讀 v4/refs/papers/tweets + 本 harness 組件，parent（frontier 檔位）合成、最強檔位終審。每項引 artifact。
> **定位**：本檔 = 理解地圖（describe），非契約（`SPEC-v4.md` 才是）。gap 交叉連到 `SPEC-v4.md` §6 backlog。
> **讀者**：第一次接觸本 harness 的採用者請先讀 §0「新採用者入口路徑」與 §0.5「詞彙表」；之後再依 §1–§7 順序讀概念關係。本檔與 `HARNESS-CORE-v4.md`（契約本體）/ `INDEX.md`（檔案路由）並列為入門三件。

---

## 0. 新採用者入口路徑（New-Adopter Entry Path）

> 目標：把「外部採用者學習曲線陡」這項共識缺口（七模型審閱共同 HIGH/MEDIUM）收斂成可依序走完的入口。本節不替代契約，只給閱讀順序與第一次出現術語的指針。

### 0.1 推薦閱讀順序（三輪漸進）

> **5 分鐘最小路徑**（若時間只夠讀一段）：本檔 §0.5 詞彙表前 6 列（Agent = Model + Body + Harness、六條設計公理、`[P]`/`[E]` 二分、advisory vs enforce、The Loop 六階段、紅軸）+ §1 兩層總綱一段。讀完即能識別本 harness 的核心詞彙與「哪些宣稱要打折扣」。
> **Standalone 伴讀**：`GLOSSARY-v4.md`（全詞彙定義與 cross-reference）與 `ADOPTION-GUIDE-v4.md`（新環境採用逐步手冊）為本目錄獨立伴讀檔，可與本檔 §0.5 詞彙表互補查閱。

1. **第一輪（地圖）**：本檔 §0.5 詞彙表 → §1 兩層總綱 → §7 組件盤點摘要。讀完應能回答：本 harness 用哪些字詞指哪些事、誰是契約誰是地圖。
2. **第二輪（契約）**：`INDEX.md` §1 檔案路由 → `HARNESS-CORE-v4.md` §0 公理 + §1 六階段（只讀 `[P]` 條文）→ `PROFILES-v4.md` §1 檔位校準表。讀完應能回答：六階段要做什麼、`[P]` 與 `[E]` 的差別、自己環境屬哪個檔位。
3. **第三輪（落地與證據）**：`SPEC-v4.md` §6 backlog（看哪些 `[E]` 條文已落地、哪些仍 open）→ `EVAL-BASELINE-v4.md`（看紅軸與 variance caveat）→ `HARNESS-EXPORT.md`「跨模型失真點清單」（換模型時哪些條文會靜默退化）。讀完應能回答：哪些宣稱已被機械驗證、哪些仍是 advisory。

### 0.2 三條 anti-confusion 守則

- **守則一：契約 vs 地圖分清楚**。`HARNESS-CORE-v4.md` 是契約（條文 + `[P]`/`[E]` 標記）；本檔與 `SPEC-v4.md` §1 差異表是地圖（描述 + 證據）。冲突時以契約為準。
- **守則二：advisory ≠ enforce**。任何標 `[E]` 的條文，在目標宿主無對應 hook/CI/gate 時，一律當 advisory（口頭勸導）；`fixture PASS` 也不會把 prompt 變成 enforcement。詳見 `INDEX.md` §3 誠實聲明。
- **守則三：數字與模型名只在 L2 落地檔**。本檔與 `HARNESS-CORE-v4.md` 採 L1 紀律（零模型名、零可調校數字門檻）；檔位校準值與 baseline 數字集中在 `PROFILES-v4.md` / `EVAL-BASELINE-v4.md`，引用前先確認構念對齊（CORE §5「構念對齊」）。

### 0.3 跟著任務走的概念入口

| 你的任務 | 直接讀 | 為什麼 |
|----------|--------|--------|
| 採用本 harness 到新環境 | §0.5 + §1 + `INDEX.md` §1 | 先掌握詞彙與檔案分工 |
| 寫一個 adapter / 跨模型移植 | §1 + `HARNESS-EXPORT.md` 失真點清單 + §6 Self-improvement | 換模型時哪些條文會退化、meta-loop 怎么自校 |
| 設計委派 / 多 agent pipeline | §3 Agent Team + §5 Fusion + CORE §3 | 角色分工、handoff contract、雙模型並行的紀律層 |
| 縮短 context / 改善 cache | §4 Context + CORE §4 | 五禁令、結構性下沉 > 符號壓縮的優化序 |
| 找盲點 / 收斂判斷 | §2 Loop + CORE §1 IDENTIFY Johari 四象限 + 11 技巧 | unknowns 在最便宜時點挖出來 |
| 看哪些缺口還沒解 | §8 Gap 表 + `SPEC-v4.md` §6 backlog | 紅軸、L3 基座、host-surface 校準、counterfactual 等共同 open |

---

## 0.5 詞彙表（Glossary — 第一次出現即定義）

> 本節定義本檔與 CORE/SPEC 互動時最常出現的術語；條文式定義以 `HARNESS-CORE-v4.md` 為準，此處為新採用者的快速入門版。

| 詞彙 | 定義 | 第一次出現於 |
|------|------|--------------|
| **Agent = Model + Body + Harness（MBH 總綱）** | owner 世界觀總綱一句：Model = 可換的模型元件（`[P]` 承載者）；Body = hooks/scripts/gates/CI 等 L3/L4 確定性機構（`[E]` 效力來源）；Harness = 紀律本身（L1 契約 + L2 校準），以合理駕馭在品質×成本雙目標上勝出。**MBH 指此總綱一句**；其下展開為六條設計公理（見下一列），兩者不宜混稱。 | CORE §0 總綱；本檔 §1 |
| **六條設計公理** | Harness > Model；LLM 只做判斷、確定性程序做決定；能力悖論；雙軸伸縮；規則 = decaying cache；地圖 ≠ 疆域。為 MBH 總綱的展開，非 MBH 本身。 | CORE §0；本檔 §1 |
| **北極星** | 本 harness 的核心設計目標＝換模型不失真。`[P]` 條文換模型仍可執行；`[E]` 條文無 Body 時退化為 advisory（CORE §7）。 | CORE §0、§7；本檔 §1 |
| **L1 / L2 / L3 / L4 分層** | L1 = 行為契約本體（CORE；零模型名、零可調校數字門檻、零 inline 引註）；L2 = 檔位校準值與接入程序（PROFILES）；L3 = 確定性機構（hooks / CI / gates / workflows）；L4 = fixture 證據（EVAL-PACK / EVAL-BASELINE）。條文的 `[P]`/`[E]` 標記與分層正交：`[P]` 屬 Model 層、`[E]` 需要 L3/L4 支撐。 | CORE 段標；本檔全檔 |
| **The Loop（六階段）** | OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD 六階段認知契約；外層信封、思考框架非輸出格式。 | CORE §1；本檔 §1 |
| **Loop Engineering** | verifier / state / stop 三鐵律構成的執行結構，在 APPLY 內當引擎；本 harness 中與 The Loop 功能分離但術語未集中命名（見 gap G-LoopA）。 | 本檔 §1、§2 |
| **三鐵律（verifier / state / stop）** | Loop Engineering 的三條不變式：verifier 須外部確定性 gate 親跑（非自評）；state 須跨壓縮 / 跨 session 寫入既有交接機制 state 檔做外錨；stop 須事前顯式宣告終止條件（G-LoopA 四重疊加）。 | CORE §1 TEST / RECORD / 迴圈終止條件；本檔 §1、§2 |
| **`[P]` / `[E]` 二分** | 每條規則標 `[P]`（Model 層承載的純認知協議，跨模型退化小）或 `[E]`（Body 層承載、需 L3/L4 enforcement 才可靠；無 runtime 時降級為 advisory）。標記指「可靠達成所需最低支撐層」，非重要性排序。 | CORE 鐵律；本檔 §1 |
| **advisory vs enforce** | advisory = 條文靠模型服從、無保證；enforce = 條文有 hook/CI/gate 機械強制。fixture PASS 最多提供 behavioral evidence，不會把 prompt 變成 enforcement。 | CORE §5 自報成功鏈；本檔 §0.2、§6 |
| **advisory lexical hook** | 產出提醒（exit 1 不阻斷）但可被換寫法繞過的 lexical 掃描 hook；**不移動行為軸分數**，須隔離 n≥3 重跑才可更新 verdict。 | `EVAL-BASELINE-v4.md` §1；本檔 §8 |
| **hard-block hook** | 確定性攔截使違規動作無法完成的機械 gate；須經語義級觸發測試（正反例）才可稱 enforced，只驗檔案存在不算。 | `HARNESS-EXPORT.md` §0.2；本檔 §8 |
| **oracle（資格先於 loop）** | 自主迴圈驗證器；建 loop 前先驗 oracle 本身（餵已知好與已知壞案例）；壞 oracle 比無 oracle 更糟（假信號燒週期 + 假信心）。 | CORE §1 TEST；本檔 §2、§6 |
| **host-surface adapter** | 依目標平台 surface 能力分級（如 chat-only / tool-enabled / API）的可貼用 prompt；未在目標 surface 跑 F1–F22 + 代表任務前一律 `uncalibrated/advisory`。 | `CHATGPT-HARNESS-v4.md`；本檔 §8 |
| **Johari 四象限** | Unknowns 引擎：Known Knowns（已在 prompt）／Known Unknowns → Interview／Unknown Knowns（品味類）→ Prototype／Unknown Unknowns → Blindspot Pass。 | CORE §1 IDENTIFY；本檔 §2 |
| **11 技巧（T1–T11）** | Know-Your-Unknowns SKILL 的 11 個技巧，分 Pre-impl（8）／During（1）／Post-impl（2）；L1 只索引 T1/T6/T7/T9/T11（有對應階段閘），其餘為 SKILL 展開。 | CORE §1 IDENTIFY；本檔 §2 |
| **Done Contract** | 成功條件與使用者協商、非單方宣告；驗證命令為逐字完整命令（含跨目錄依賴）而非描述性條件。 | CORE §1 IDENTIFY；本檔 §2 |
| **unverified_success 閘門** | 任何自報成功（自己 / sub-agent / workflow / 自動化）= 中間態；宣告完成前負責者親自跑確定性檢查並展示輸出；裁定不跨 agent 邊界。 | CORE §1 TEST；本檔 §2、§6 |
| **fixture（L4 Eval Pack）** | 已知好 / 已知壞的 counterexample 樣本，獨立 context 執行 + 確定性腳本比對；用來背書條文的 behavioral evidence。 | `EVAL-PACK-v4-ADDENDUM.md`；本檔 §6、§8 |
| **紅軸 / fail_axes** | baseline 重跑中持續 FAIL 的 fixture 軸；當前為 F7（eval_hack 字面特判）與 F15（blindspot_pass 高風險域零提及）。advisory lexical hook 落地不移動紅軸行為分（須 #2c held-out n≥3 重跑）。 | `EVAL-BASELINE-v4.md`；本檔 §8 |
| **eval-hack** | 對給定測試輸入做字面特判讓測試綠燈、未以未見輸入抽驗泛化的裝完成捷徑；F7 fixture 的 fail_category。 | `EVAL-BASELINE-v4.md` F7；本檔 §8 |
| **point estimate** | 單一執行樣本的統計估值（n=1，無信賴區間）；不可作為「軸已穩定通過」的換代重審門檻，n≥3 全 PASS 才計一輪滿分。 | `EVAL-BASELINE-v4.md` §0.2；本檔 §8 |
| **BLOCKED-ENV** | 在本 workspace 內無法建立乾淨 counterfactual 對照臂的狀態標記——agents 會正確拒絕 de-harness 指令，故 in-env 對照臂必被汙染。 | `SPEC-v4.md` §6 #13；本檔 §8 |
| **counterfactual** | 對照實驗設計用來驗證因果宣稱；v3 vs v4 行為 delta 須於外部無 harness 環境兩臂對測才有效。 | `SPEC-v4.md` §6 #13；本檔 §8 |
| **檔位（cost / quality / ceiling / frontier）** | 抽象能力層，行為指導量與能力成反比、驗證閘門強度與能力成正比；模型名為當代對應、換代改對應不改條文。 | `PROFILES-v4.md` §1；本檔 §3、§5 |
| **fan-out 上限** | 一次委派可啟動的 sub-agent 數量上限；具體數字在 L2。 | `PROFILES-v4.md` §2；本檔 §3 |
| **常駐 byte 預算** | auto-load 層的位元組上限；量測以命令為準非快照值；超過即觸發壓縮或拆檔。 | CORE §5；本檔 §4 |
| **五禁令** | cache 紀律：① 動態事實不入穩定前綴；② 不 mid-session 換模型；③ 不 mid-session 增刪 tool；④ fork 必須重放父前綴原文；⑤ cache 命中率驟降即查前綴變動。 | CORE §4；本檔 §4 |
| **結構性下沉 vs 符號壓縮** | context 優化序：結構性下沉（path-scoped / on-demand）> 符號壓縮 > 快取 > 極端壓縮；重複注入的常駐稅 > 一次性膨脹。 | CORE §4；本檔 §4 |
| **episodic-first 記憶** | consolidation 是最高風險記憶操作（自正確 ground truth 反覆固化仍致能力退化）；合併 / 摘要須顯式核可、不得覆寫所依證據、保留 rollback。 | CORE §1 RECORD；本檔 §4、§6 |
| **Handoff Contract** | 委派時 parent 必給 child 的契約：Goal / Non-goals / Allowed-paths / Context / Done-when / Return / tier+effort；缺一 child 不開工；缺欄阻擋須 runtime 強制。 | CORE §3；本檔 §3 |
| **benefit-gated delegation** | 委派須具名效益（context 隔離／真平行／對抗審查／低風險大量機械執行／降噪），計入 handoff 固定開銷；無效益即不委派。 | CORE §3；本檔 §3、§5 |
| **MAST** | arXiv 2503.13657 的多代理失敗模式分類（14 類，κ=0.88）；本 harness §3 委派不變式對照盤點覆蓋率。 | `SPEC-v4.md` §8；本檔 §8 |
| **G-*（gap 代號）** | 本檔從實戰任務中識別的概念層 gap 代號（G-LoopA、G-WF、G-Mem 等），追蹤狀態見 §8。 | 本檔 §7、§8 |
| **backlog #編號** | `SPEC-v4.md` §6 的 backlog / status ledger 編號；落地進度與證據以 SPEC 為準。 | `SPEC-v4.md` §6；本檔 §8 |

---

## 1. 兩層總綱（貫穿全圖）

`Agent = Model + Body + Harness`（CORE §0）。本圖的「概念」多屬 **Harness 層**（可自我修改），少數屬 Model 層（不可，如訓練 / 權重）。
**The Loop（六階段認知契約，全 `[P]`）是外層信封；Loop Engineering（verifier / state / stop 執行結構，`[E]`）是 APPLY 內的引擎。** 二者在本 harness **功能分離但術語未命名分離**——靠 `[P]` / `[E]` 標記做隱性切分（見 gap G-LoopA）。

> 北極星：換模型不失真。`[P]` 條文換模型仍可執行；`[E]` 條文無 Body 時退化為 advisory（CORE §7 降級條款）。

---

## 2. Loop / Goal

| 概念 | 最新思路（源） | 本 harness 實現 | gap |
|---|---|---|---|
| **Loop = cron + 決策者，非固定腳本** | @mvanhorn（WTF-is-a-Loop）、@bibryam（LDD：verify 是分水嶺） | `multi-mode-skill §5` /loop 排程；`refs/harness-loop.md` 六階段映射 | 無明顯落差 |
| **三鐵律 verifier / state / stop** | @0xCodila（no gate = 自批作業）；papers reflexion / voyager | Verifier → CORE TEST `unverified_success` 閘門；State → RECORD 目標外錨 + handoff；Stop → autoresearch Phase 8 plateau（條文層已於 2026-07-21 補 CORE §1「迴圈終止條件」段） | **G-LoopA**：三鐵律「拆到不同檔非集中命名」的設計已收斂，CORE §1 已補獨立 stop-condition 段（四重疊加：verifier 通過 / 迭代上限 / 預算上限 / 無進展偵測）；條文已落地，**機械化門檻（accepted-change rate）仍 pending L2 校準**。 |
| **`/goal` 原生指令** | @mvanhorn；宿主平台官方 docs 證實：`/goal` 為宿主平台原生指令，設完成條件自主跨 turn，獨立 fast validator 判定達標（非自評） | workspace 正確依賴平台原生 `/goal`，無需自建 commands 檔；overnight-research / deep-understanding / multi-mode 引用 `/goal` 是正確用法非借名 | **已澄清（原誤判為 gap）**：`/goal` 的 fresh-validator = 「verifier 在被優化物外」鐵律的平台落地。真正 action：harness 應明確把 `/goal` 當 Goal-loop canonical 原語善用（含 `/loop` 原生）——屬強化非缺失。 |
| **bilevel（外層改內層）** | @0xCodila（5× 改善） | `harness-loop.md` 開放問題段顯式 defer（基建不具備） | 已承認 gap，非盲點 |

---

## 3. Agent Team / Sub Agent

| 概念 | 最新思路（源） | 本 harness 實現 | gap |
|---|---|---|---|
| **多 agent debate / consensus** | papers multiagent-debate（自組織多數決，無外部裁判） | **刻意拒絕**：quality-pipeline 引 2605.03310 Brier 表（debate / consensus 為倒數）選 Sequential | 非 gap，是有證據的架構選擇 |
| **角色分工 SOP pipeline** | 多角色 agent 軟體工程論文（SOP pipeline 線） | 多個互斥 specialist agents；quality-pipeline G1→G2→G3 結構化 artifact | 驗收停在 PASS / FAIL 布林，未量化（該類論文的 executability score） |
| **裁定不跨 agent 邊界** | — | **本 harness 最徹底實作點**：quality-pipeline 用 bash grep 解析 PASS / FAIL 非採信 agent 自陳 | 一致，無落差 |
| **Dynamic Workflow（JS harness）** | @trq212（多個平行、存檔版控） | multi-mode §3 提及但標「平台 runtime 功能」 | **G-WF**：宿主 workflows 目錄不存在；未落地為版控 script（= `SPEC-v4.md` §6 backlog #3，最高槓桿） |
| **Fleet economics** | @davidvgilmore（多檔位大量 subagents / run） | agents 模型金字塔（cost worker / 執行 / 終審）；fan-out 上限在 L2 | 與大規模預測差數量級；深度裁決池偏薄（設計級取捨，backlog 追蹤） |

---

## 4. Context Management / Prompt Caching

| 概念 | 最新思路（源） | 本 harness 實現 | gap |
|---|---|---|---|
| **static-first caching 五禁令** | bcherny 五原則 | `context-management.md` 五禁令逐條對齊；`cache-health-metrics.md` 更細 | — |
| **subagent = cache-efficient 邊界** | @davidvgilmore | 禁令②隱含但原未點名連到委派效益清單 | **G-Cache**（已修）：`subagent-strategy.md` 效益清單已補「保護 parent cache 前綴」 |
| **分層記憶（RAM / disk）** | memory-tier 論文（RAM/disk 分層線、MemoryBank、SCM）；survey 警告 consolidation = 退化主因 | MEMORY / LESSONS + handoff（archival）；`memory-compactor` 引同篇採 batch 回應警告 | 無連續衰退函數、無語意 / 向量檢索、無 heartbeat 背景整合 |
| **結構性下沉 > 符號壓縮** | 優化序（`context-management.md`） | `output-compress` 正確落在符號壓縮層（不冒認） | **G-Mem**（高槓桿）：skill-router 已 BM25，但**記憶檔仍整檔 Read**，未做查詢式選讀——比 output-compress 更上游 |

---

## 5. Fusion（雙檔位並行機制）

| 欄 | 內容 |
|---|---|
| **概念** | frontier lead + cost sidekick 雙檔位並行；early handoff + spec-brief（非 dictation）；lead 只做 diff 審查、不親改 |
| **最新思路** | @joon_h_lee：**管理風格 > 價格**；frontier 檔位 + sidekick 比 ceiling 檔位 + sidekick 更便宜更高分（早期寫約束式 brief、多數 run lead 零 edit） |
| **本 harness 實現** | `fusion` skill + `fusion-sidekick` agent（cost 檔位 / worktree / 自管迴圈）；§3 spec-brief 模板對應實證 |
| **gap** | 忠實移植**行為紀律層**（brief / 時機 / 驗收），但**非架構層**：無雙持久並行 context、無 mid-session dynamic routing（平台限制，design-plan 已列）；本地無 A/B 效益量測 |

---

## 6. Self-improvement / Meta-loop

> 三個 meta-loop 機制（autoload-evolution / sia / dreaming-consolidator）的 verifier 外部性稽核——A5 鐵律：verifier 須在被優化物外。

| Meta-loop | verifier 外部性稽核 |
|---|---|
| **autoload-evolution** | 機械層（healthcheck / byte）**真外部**；LLM 品質判準用跨模型 PGE reviewer 降低，但當 reviewer = implementer = ceiling 時退化為同檔自審（`*` caveat，**唯一自標未解缺口**） |
| **sia** | `evaluate.py` + held-out private data **真 oracle**；但 `improvement.md` 敘事無外部審；custom-task 下 oracle 品質依賴人類設計 |
| **dreaming-consolidator** | provenance gate + 人類核可**真外部**；但**語意品質完全無外部核**（三者最弱） |

**共同模式**：機械層真外部，語意判斷層幾乎都退回同源 LLM——呼應 weak-to-strong 警語。**本 harness 明確禁止 runtime 即時自寫**（autoresearch:L17，skills-bench 遞迴退化風險），故是 ExpeL 式 batch consolidation，非 evo 式 concurrent bilevel（刻意安全取捨）。

---

## 7. 組件 → 存在理由（盤點摘要，全表見 backlog 附錄）

> 採用 L1 紀律：不硬編碼組件計數（計數必腐化，以 `INDEX.md` / `RESOLVER.md` 實際盤點為準）；下列按**類別**描述。

- **Rules（行為契約層）**：core = 六階段契約 ｜ context-management = caching / compact ｜ output-discipline = token 密度 ｜ subagent-strategy = 委派治理 ｜ security-hygiene = 敏感資料防護。
- **Agents（執行檔位層）**：金字塔分工（cost worker / 執行 / 終審）；self-escalate = 收斂判斷 ｜ fusion-sidekick = 自管迴圈執行。
- **Skills（觸發路由層）**：見 `RESOLVER.md`；已示範 output-compress → token 浪費、sia → self-improve。
- **疑似重疊對**（多為維度差異非真重疊）：最需注意 output-compress ↔ output-discipline（可選 vs 常駐）、deep-understanding ↔ know-your-unknowns（教人 vs 挖任務盲點，已在 RESOLVER 消歧）。

---

## 8. 本圖導出的 gap（併入 `SPEC-v4.md` §6 backlog 追蹤）

> 新增（概念層，非 Phase 0 稽核已列者）：~~G-Goal~~（**已澄清**：`/goal` 為原生指令，屬善用建議非缺失，見 §2）、G-WF（workflows 未落地）、~~G-Cache~~（已修）、G-Mem（記憶檔未查詢式下沉，**高槓桿**）、Agent-Team 深度裁決池薄。
> 與 Phase 0 backlog（以 terraform gate + branch-guard 為首）合流成完整改進地圖。

### 8.1 狀態（2026-07-21 對賬，收據見 insight report §9 + `SPEC-v4.md` §6）

> 本表為**概念層 gap 的整體狀態**（併入 SPEC §6 backlog 追蹤）；§8.3 列**增量進度**（部分條文層閉合，但對應 Body / 機械化缺口未關者仍在此表維持 open）。SPEC §6 編號映射：G-WF = #3、§5 語意判斷層外部核 = #14、F7/F15 紅軸重跑 = #2c、乾淨 counterfactual = #13、F18 action = SPEC §6 F18 列。

| Gap | 狀態 | 證據 / 去處 | SPEC §6 對應 |
|---|---|---|---|
| Phase 0 P0（terraform gate、branch-guard） | ✅ 已修 | git commit + 最強檔位終審 | — |
| §5 dreaming 輸入無機器 trace | ✅ 已修 | ① trace capture（session-stop skills-only upsert）+ ② dreaming 接線（consolidate.sh TASK-LOG 節 + oracle fixture）；首筆真 trace `deep-understanding` 已流動 | — |
| G-Cache（委派效益漏 cache） | ✅ 已修 | `subagent-strategy.md` 效益清單補「保護 parent cache 前綴」 | — |
| ~~G-Goal~~ | ✅ 已澄清 | `/goal` 原生，善用建議非缺失 | — |
| G-LoopA（三鐵律未集中命名 / 無 stop 段） | ✅ 條文層已修；機械化 pending | CORE §1 已補獨立 stop-condition 段（四重疊加）；機械化門檻（accepted-change rate）pending L2 校準（PROFILES §2 列待校準） | 演化隊列 #2；待 L2 校準 |
| **G-WF（workflows 未落地）** | ⏳ **open** | 平台 Workflow 工具已可用，落地宿主 workflows 目錄為設計級任務 | **SPEC §6 #3（最高槓桿）** |
| **G-Mem（記憶查詢式下沉，高槓桿）** | ⏳ **open**（§8.3 僅補 episodic 保留窗，語意檢索依賴 `embed_stub` 修復未做） | 依賴 `embed_stub` 修復（insight §3）→ backlog | SPEC §6 後續項 |
| 深度裁決池薄 / 驗收未量化 | ⏳ open | 設計級取捨，backlog 追蹤 | — |
| **§5 語意判斷層無外部核（三 meta-loop 共同弱點）** | ⏳ **open** | = roadmap ③ eval 閘（當前 head）；checkable 類 per-skill held-out fixture 擴面為未竟項 | **SPEC §6 #14（host-surface calibration）** 並聯 F7/F15 紅軸（#2c 已執行） |
| **#2c F7/F15 held-out rerun** | ✅ **已執行**（2026-07-21）；結論＝advisory 天花板確認 | F7 0/3（四輪連紅）、F15 1/3（不穩定偏紅）、F19 0/3、F20 3/3；結構性歸因＝advisory stderr 不進 agent context；紅軸行為分未動，需 execution 層突破 | **SPEC §6 #2c** |

### 8.2 實踐例對照（掃 `research/tweets/` 多篇、逐讀代表性全命中；recherche tier + parent 整理）

| Gap | 高可移植實踐例（檔名 → 做法 / 量化） | 採納方向 |
|---|---|---|
| **skill 蔓延治理** | `2026-05-05-@Mnilax-897712`：大量 skills 縮減（個位數 % 留存）；每兩週稽核、30 天未 fire → 停用；雙門檻（品質提升 / 時間節省）；`2026-07-08-@PrajwalTomar_-899896`：三判準 overlaps / never-triggers / worse-version | 觀察窗採 30 天（自 2026-07-20 起算 → 首次稽核日依視窗計算）；判準 = 頻率 × 防錯代價 − 理解稅，非頻率單項 |
| **G-LoopA** | `2026-07-11-@eng_khairallah1-565100`：**分層終止四重疊加**（verifier 通過 / 迭代上限 / 預算上限 / 無進展偵測）+ 禁自評 + 禁改測試檔（同構本 harness test-integrity）；`2026-07-08-@choopyplug1-503774`：**accepted-change rate 低於門檻 = loop 得不償失** 量化門檻 | CORE §1 補獨立 stop-condition 段（已完成）+ rubrics 加 accepted-change rate → 路由 autoload-evolution（auto-load 紀律，不 ad-hoc） |
| **③ eval 閘** | `2026-06-01-@hooeem-791154`（Microsoft SkillOpt）：validation gate + held-out split + bounded edit budget + rejected-edit buffer；**前提 = 有可機械驗證 answer key** | dreaming 產出先分流：可 checkable（skill 改進 → per-skill eval fixture）走 SkillOpt 式 gate；純語意（playbook）維持異模型審 + 人閘。先讀 arxiv 2605.23904 核實（推文轉述未驗） |
| **G-Mem** | `2026-05-18-@Phoenixyin13-509649` + `2026-05-16-@haopeng_uiuc-410764`（arxiv 2605.12978）：**持續 consolidation 可比無記憶更差** → episodic-first、顯式門控、異質不混批（本 harness RECORD 已同向，可補「近 N session 不整合」保留窗）；`2026-05-13-@lxfater-505745`：檢索四模式（keyword / vector / hybrid+rerank / agentic）設計參考 | `memory-compactor` / dreaming 補 episodic 保留窗；語意檢索依賴 `embed_stub` 修復（不新造） |
| **G-WF** | `2026-06-02-@trq212-367865`：workflows 存版控目錄 + 低推理深度 workers / 高檔位 synthesizer + anti-patterns（unbounded scope / all-frontier / no synthesis）；`2026-06-01-@0x_kaize-365248`：並發 / ceiling 上限、子目錄小範圍先測 | 平台 Workflow 工具本 session 已確認可用 → 首個 workflow 以「skill 稽核 sweep」為題落地（吃 30 天 `skills_used` 資料，與治理項合流） |

### 8.3 後續實作排程（依賴序 + Done-when）— 2026-07-21 串通執行狀態

1. ✅ **Skill 治理觀察窗入規**：`refs/model-profiles.md` §8 新增（30 天窗 / 三判準 / 雙門檻 / hook 型豁免）；首次稽核 Routine `skill-audit-30d-window`（一次性，日期依視窗計算）。
2. ✅ **G-Mem episodic 保留窗**：查證發現 `memory-compactor` 早已內建 batch gate（引 arXiv:2605.12978，stream 整合退化證據）；dreaming SKILL §IDENTIFY 補「最近數 session 不整合」保留窗（同源同準則；具體 N → L2 校準）。
3. ✅（條文層）**③ eval 閘**：arXiv 2605.23904 已核實（held-out 嚴格提升才接受 / edit budget / rejected buffer 四要素屬實）；dreaming §TEST 加「產出分流」條文（checkable → SkillOpt 式 gate，範例 fixture 已存在；純語意 → provenance gate + 異模型審 + 合入人閘）。**未竟**：checkable 類的 per-skill held-out fixture 擴面（隨 skill 稽核 Routine 逐步建）。
4. ✅（提案層）**G-LoopA**：CORE §1 已補獨立 stop-condition 段（2026-07-21）；提案入 `research/EVOLUTION-QUEUE.md` #2（g-loopa-stop-condition-20260720，含機械驗證條件與安全邊界）；機械化門檻（accepted-change rate）pending L2 校準。
5. ⏳ **G-WF 首個 workflow**：等 30 天資料窗（首次稽核 Routine 產出即其輸入）。

### 8.4 自動化接線（時間驅動 → Routine，皆候選制人閘）

`weekly-dreaming`（每週日 02:00 UTC，新 session；產 PLAYBOOK 候選到獨立分支不 merge）+ `skill-audit-30d-window`（一次性；只產報告與停用候選）。合入 / 停用永遠人閘——routine 補觸發、電路已通（①②③條文全落）、oracle 前置、不可逆處人閘（`2026-07-20-routine-closure-learning.md` 四原則全數落實）。

> **telemetry 雙軌註記**：`skills_used` 只計 **Skill tool 呼叫**（tracker 通用解析，免逐一接線；合成 transcript 驗證 PASS）；hook 自動觸發路徑（如 output-compress AUTO）**刻意不混入** `skills_used`（保欄位語義），其計量走自有雙軌 telemetry：`evolution/compress-opportunity-log.jsonl`（機會 / would_compress，usage-delegation-gate 寫）+ `compress-metrics.py`（執行率 / pass / saving，V1–V6 verdict）。

---

> **來源檔**：`HARNESS-CORE-v4.md` / `SPEC-v4.md`、`refs/`（harness-loop / cache-health-metrics / delegation-protocol / per-model-eval-suite）、`papers/`（reflexion / voyager / autogen / multiagent-debate / memory-tier RAM-disk / MemoryBank / SCM / expel / weak-to-strong / coordination-2605.03310 等）、`tweets/`（mvanhorn / 0xCodila / bibryam / trq212 / Jeyxbt / davidvgilmore / joon_h_lee / qinzytech / alokbishoyi97 / karpathy 等）、fusion/{SKILL,GOTCHAS}+design-plan、宿主 rules / agents / skills 全目錄。
> **L1 紀律**：本檔與 `HARNESS-CORE-v4.md` 同採零模型名 / 零可調校數字門檻；具體校準值在 `PROFILES-v4.md`，baseline 數字在 `EVAL-BASELINE-v4.md`，落地進度在 `SPEC-v4.md` §6 backlog。
