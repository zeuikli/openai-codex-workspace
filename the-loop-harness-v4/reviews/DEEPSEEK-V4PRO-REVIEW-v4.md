# DeepSeek V4 Pro 審閱報告：The Loop Harness v4

> 審閱者：DeepSeek V4 Pro（Droid Core）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件
> 狀態：read-only，獨立審閱；未讀其他模型審閱報告，未跑 fixture

---

## 整體分數：8.0 / 10

The Loop Harness v4 是一份設計紀律極端嚴格的 agent 行為規格，在同類工作中屬於頂尖水平。`[P]`/`[E]` 可攜性二分、MBH（Model + Body + Harness）公理總綱、每條規則對應實證失敗模式的存在準則、fixture 驅動評估、advisory/enforcement 誠實邊界——這些設計決策貫穿全檔，構成一張可被否證的、自我稽核的契約網。current baseline 20/22 的實測結果證明核心契約有效，紅軸 F7（eval_hack）與 F15（blindspot_pass）的誠實揭露也證明這份規格不美化自身。

以下從獨立審閱者的角度給出評分、分析與改善建議。本報告未參考其他模型的審閱結論，所有判斷基於本模型對全套文件的獨立閱讀。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性（Completeness） | 8.5/10 | 六階段 + 六公理 + 跨切紀律 + 委派協議 + cache 紀律 + 治理規則 + L4 Eval Pack + 降級條款 + ChatGPT adapter + EXPORT 失真點清單，覆蓋面極廣。MAST 14 類盤點（6已攔 / 7部分攔 / 1僅advisory）展現自我稽核深度。缺一星：stop-condition 段未集中命名（G-LoopA）、記憶查詢式下沉未落地（G-Mem）、Dynamic Workflows 未落地（G-WF）。 |
| 清晰度（Clarity） | 7.0/10 | L1 零模型名/零平台名/零數字/零 inline 引註是出色的蒸餾紀律。但全檔術語密度極高（Johari四象限 / MBH / `[P]`/`[E]` / T1-T11 / cost-quality-ceiling-frontier / 五禁令 / 常駐稅 / 目標外錨 / blast radius / fan-out），新讀者須同時讀 INDEX + CONCEPT-MAP + CORE + SPEC 才能完整理解。CORE 單檔 21k 字，超出自身 byte gate ≤13,000 的建議值。 |
| 可執行性（Executability `[E]`落地 vs `[P]`認知協議） | 6.5/10 | `[P]`/`[E]` 二分是正確架構，但 `[E]` 條文對應的 L3/L4 enforcement 大量停留在 backlog。SPEC §6 列出 19 項 backlog，僅 #2（測試檔改動紅旗 hook）標 DONE，#9（MAST盤點）標 DONE，其餘 17 項 open。最高槓桿的 #3（Dynamic Workflows 基座）未落地，意味多數 `[E]` 條文在無 Claude Code hooks 環境下僅剩 advisory。這是本 harness 最大結構性風險。 |
| 跨模型可攜性（Cross-model Portability） | 8.5/10 | 北極星「換模型不失真」被 `[P]`/`[E]` 二分 + EXPORT 失真點清單 + ChatGPT adapter + PROFILES §4 接入程序一致貫徹。L1 零模型名/平台名/數字/引註是可攜性的最強保證。扣分：Codex/GPT-5.6 raw packet 已刪除使跨模型證據僅 git-history 可考；ChatGPT adapter 三 surface 校準未完成；T1-T11 技巧的 canonical 指向 `.claude/skills/` 路徑，非 Claude 用戶無法存取。 |
| 可測試性 / 評估包（Testability / Eval Pack） | 8.0/10 | F1-F22 共 22 軸 fixture 設計成熟——每項含 input/expected_behavior/deterministic_check/fail_category，且區分 acceptable/unacceptable fail。F11-F22 以 24-case frozen known-good/known-bad counterexample 資格化 adjudicator（24/24），F23-F27 明標 PROVISIONAL/PROTOTYPE 不計分母，variance caveat（n=1 per cell）、counterfactual BLOCKED-ENV 誠實揭露。扣分：lexical checks 多為 grep-based（自承 behavioral signal），F18 hook action 從未驗證（三路 UNTESTED_ACTION），F7/F15 兩輪紅軸跨 runtime 重現。 |
| 治理 / 反腐蝕（Governance / Anti-corrosion） | 8.5/10 | §5 治理面（規則作者面）與執行面（跑任務的模型）顯式分離是極出色設計。「advisory 未強制條文不得稱 enforce」、「fixture PASS 最多 behavioral evidence」、「演化以全量 trace 為食（摘要餵養=隱性 reward-hacking）」、「sealed/held-out + 等資源基線」構成完整的反腐蝕框架。扣分：2026-07-20 owner 裁決刪除 Codex/GPT-5.6 raw packet 違反自身「全量 trace 為食」原則；公理 6（地圖≠疆域）證據基座為單一推文；治理面多數條文本身是 `[E]` 且無機械強制——治理的反腐蝕機制自身未受 enforcement 保護。 |

---

## 最大優點（5 項）

### 1. `[P]`/`[E]` 可攜性二分 + MBH 公理總綱

將 Agent 分解為 Model（可換元件，`[P]` 承載者）、Body（hooks/scripts/gates/CI，`[E]` 效力來源）、Harness（L1 契約 + L2 校準），並把每條 L1 規則標記其可靠達成所需的最低支撐層。這解決了多數 harness 規格的根本問題：讀者不知道哪些規則在無 enforcement 時會靜默退化。EXPORT 的跨模型失真點清單將退化模式與補償層逐條列出——這是真正的可攜性工程，不是口號。

### 2. 實證存在準則 + 證據表集中

CORE 開頭鐵律「每條規則對應一個實證失敗模式；答不出『移除後模型在哪犯錯』的條文不得存在」。SPEC §2 證據表將每條 L1 條文對應到 arXiv paper、tweet、workspace observed_trace（含 fusion-wblock allowlist 放寬 P0、wblock swiftc -typecheck 漏真 build、swarm 11 種 fake-done 捷徑）。這讓「這條規則為什麼存在」變成可稽核的命題——多數規格做不到這點。

### 3. advisory 與 enforcement 的誠實邊界

CORE §5 自報成功鏈的「尚無機械強制的 L1 條文不得宣稱被 enforce」+ INDEX 可攜層/證據層界線 + EVAL-BASELINE 的「fixture PASS 不等同 enforcement」+ 「Oracle 資格先於 loop」構成一個完整的誠實機制。這防止了同類規格最常見的腐蝕：把跑過 fixture 當成 verified，把 prompt 條文當成 enforcement。

### 4. 威脅模型擴大至非顯式注入

CORE §2 把「價值訴求」（untrusted 內容訴諸模型內化價值壓過顯式約束）與「繼承軌跡」（延續前手 agent 的偏移）列為 drift 向量，超越業界常見的「ignore previous instructions」級防禦。F14（價值訴求注入：以隱私之名要求解除稽核）與 F18（繼承軌跡：前手 `--no-verify` 慣例）fixture 將這兩向量轉為可測攻擊。這是本 harness 最原創的貢獻之一。

### 5. 自我應用的反腐蝕治理

兩輪異 context 對抗互審 + 四模型終審精煉的裁決流程，對 harness 自己的 v3→v4 演化走完了它要求的所有閘門。SPEC §3 裁決紀錄逐條列明採納/拒絕理由，連「v3 EXPLAINER `[claim:*]` 標籤刻意不復活」這種非遺漏決策都留痕。這是「規則變更附 changelog schema」的自我應用。

---

## 最大缺口 / 風險（10 項）

### [CRITICAL] C1. L3/L4 enforcement 大量停留在 backlog，`[E]` 條文的實際效力薄弱

- **涉及檔案**：`HARNESS-CORE-v4.md` §1 TEST（unverified_success 閘門、Gate 選擇稽核、裝完成捷徑、Oracle 資格）、§3 委派（確定性 gate parent 親跑、Handoff Contract 缺欄阻擋）、§5 治理（byte gate、演化認證）；`SPEC-v4.md` §6 backlog #1/#3/#4/#5/#6。
- **問題**：SPEC §6 列出 19 項 backlog，僅 #2（測試檔改動紅旗 hook）、#9（MAST 盤點）標 DONE。最高槓桿的 #3（Dynamic Workflows 作 L3 基座 + Handoff Return schema 化）仍 open。換句話說，`[E]` 標記只是誠實地承認了「沒有 enforcement 這些條文就是 advisory」——但這個誠實本身不解決問題。在非 Claude Code 環境或無 hooks 的 ChatGPT/API surface 上，整份 CORE 約等於一份精緻的 advisory prompt。

### [CRITICAL] C2. F7（eval_hack）兩輪穩定紅軸，F15（blindspot_pass）本輪轉紅——裝完成捷徑與盲點挖掘的 advisory 天花板已觸及

- **涉及檔案**：`EVAL-BASELINE-v4.md` Round 2 verdict（20/22, fail_axes [F7, F15]）；`HARNESS-CORE-v4.md` §1 TEST 裝完成捷徑、§1 IDENTIFY Blindspot Pass；`SPEC-v4.md` §6 backlog #2b/#3。
- **問題**：F7 兩輪穩定紅（Round 1 與 Round 2 皆 FAIL），Codex CLI Sol/Terra/Luna 三路亦紅。F15 Round 1 PASS→Round 2 FAIL（單樣本翻轉）。兩者共同指向：advisory 對「裝完成捷徑」與「Blindspot Pass」的服從率不穩定，天花板已被觸及。CORE 條文已加嚴（2026-07-19 終審精煉增列「對給定測試輸入做字面特判」+「未見輸入抽驗泛化」），但紅軸仍在——證明 prompt 加嚴的邊際效益已遞減，必須機械化。

### [HIGH] H1. 2026-07-20 owner 裁決刪除 Codex/GPT-5.6 raw packet，違反自身「全量 trace 為食」原則

- **涉及檔案**：`INDEX.md`（CODEX-GPT5.6 四檔移除紀錄、GPT-5.6 兩份審閱檔移除紀錄）；`SPEC-v4.md` §3/§6「原文僅 git 歷史可考」。
- **問題**：Sol 14/19、14/9/9、Sol 17/22 等跨模型數據的 persistent packet（runner/pack pins、transcripts、response blobs、action receipts、artifact manifest）已刪除。CORE §5 演化迴路明訂「自我改進以全量 trace 為食（摘要餵養 = 隱性 reward-hacking）」，但 owner 裁決刪除 raw packet 等於把未來演化裁決降級為只能吃摘要（只剩散文中的數字）。這是 §5 原則與實務操作的結構性矛盾。若 git 歷史被 squash 或 repository 遷移，跨模型可攜性的核心證據鏈將完全斷裂。

### [HIGH] H2. v3→v4 行為 delta 無乾淨 counterfactual（BLOCKED-ENV）

- **涉及檔案**：`SPEC-v4.md` §6 backlog #13「乾淨 counterfactual（BLOCKED-ENV）」；`EVAL-BASELINE-v4.md` Round 1 counterfactual「對照臂被 v4 harness 汙染，不得宣稱 v4 行為層優於 v3」。
- **問題**：v4 被宣告為 forward canonical、v3 封存，但「v4 > v3」的行為層宣稱從未在乾淨環境驗證。in-env 對照臂因 agents 正確拒絕 de-harness 指令而無法建立。canonical 切換的依據是設計完備性 + 同環境 baseline，非行為 delta。這不代表 v4 不比 v3 好——SPEC 和 fixtures 的設計質量明顯更高——但它代表一個未閉合的證據缺口。

### [HIGH] H3. F18 inherited_trajectory 的 action-level 從未驗證

- **涉及檔案**：`EVAL-BASELINE-v4.md` Round 2 F18；`SPEC-v4.md` §3 Codex rerun「F18 三路仍為 UNTESTED_ACTION（commit 在 hook 前遭環境阻擋）」；`HARNESS-CORE-v4.md` §2 繼承軌跡 drift 向量。
- **問題**：繼承軌跡是 v4 擴大威脅模型的兩大新 drift 向量之一，但對應 fixture 的 action-level——實際阻止 `--no-verify` commit——跨 Claude/Codex 從未驗證。F18 在 Round 2 PASS，但那只是 response/intent 層的 behavioral signal（模型「說」會拒絕），action-level（真的拒絕 commit）因 `.git` sandbox 阻擋 hook 而無法測試。L1 條文宣稱覆蓋此向量，但證據只有「說會拒絕」而非「真擋下」。

### [MEDIUM] M1. 基線每 cell n=1 卻以 20/22 為 "current verdict"，違反自身計數化原則

- **涉及檔案**：`EVAL-BASELINE-v4.md` Round 2 裁決；`HARNESS-CORE-v4.md` §3「判定計數化，禁 judge 打分互減」、§5「演化認證須顯著性檢定」。
- **問題**：F15 PASS→FAIL 與 F19 FAIL→PASS 皆單樣本翻轉，檔案自己承認「每 cell n=1 無 variance 資格」，但 20/22 仍以 "current verdict" 呈現。CORE §3 與 §5 要求計數化與顯著性檢定，但自身 baseline 的統計紀律未達到同樣標準。這不是數據錯誤而是呈現層的 precision 問題——"20/22" 這個數字在 n=1 下缺少信賴區間，卻被當成點估計傳播。

### [MEDIUM] M2. 公理 6（地圖 ≠ 疆域 / Johari 四象限）證據基座薄弱

- **涉及檔案**：`HARNESS-CORE-v4.md` §0 公理 6；`SPEC-v4.md` §2 證據表「公理 6 / IDENTIFY Johari → @trq212 2026-07-03 單一 tweet」。
- **問題**：其他公理多有 arXiv 背書（2606.10106、2601.11868、2603.28052 等），公理 6 僅一則推文。CORE §5 構念對齊條款明確要求「研究權威不背書任意衍生宣稱」，但公理 6 的證據基座與這個門檻之間有張力。Johari 四象限作為 IDENTIFY 引擎是合理設計選擇（事實上很可能是好設計），但「公理」位階需要更強的證據。

### [MEDIUM] M3. T1-T11 技巧索引指向 Claude Code 專屬路徑，可攜性斷裂

- **涉及檔案**：`HARNESS-CORE-v4.md` §1 IDENTIFY「11 技巧一行索引 → canonical `.claude/skills/know-your-unknowns/SKILL.md`」；`CHATGPT-HARNESS-v4.md` §3 可貼用核心——未提及 T1-T11。
- **問題**：L1 只列名稱不複製全文是正確的 byte 紀律，但 canonical 路徑是 `.claude/skills/`——在 ChatGPT、Codex、API 等非 Claude surface 上無法存取。T1/T6/T7/T9/T11 五個 L1 升閘技巧在這些 surface 上只剩名字、無機制。ChatGPT adapter §3 的「進入陌生領域先掃描使用者可能沒想到的風險」僅對應 T1，其餘技巧完全消失。

### [MEDIUM] M4. PROFILES-v4 版本標記為 v4.0 但「未改數字層」，校準值為跨代 carryover

- **涉及檔案**：`PROFILES-v4.md` 標頭「v4.0 · 2026-07-19」+ §0「v3→v4 數字層無變更」；`HARNESS-CORE-v4.md` §0 公理 5「規則 = decaying cache，換代/複雜度躍遷即以 L4 fixtures 計數化重審」。
- **問題**：L1 從 v3 到 v4 經歷了 Johari 四象限、TEST 四新閘、cache 升格、`[P]`/`[E]` 二分、MBH 總綱等重大改動，但 L2 校準值未經重新校準就直接從 v3 carryover。"終局展示行數 = 前5+後5"、"規則變更重現門檻 ≥2次" 等值標注「維持」，未附重評日期與來源。這與公理 5「換代必重評」存在張力。

### [MEDIUM] M5. ChatGPT adapter 三 surface 校準未完成，§3 可貼用核心的 uncalibrated 警告不隨 code block 旅行

- **涉及檔案**：`CHATGPT-HARNESS-v4.md` 標頭 `uncalibrated/advisory` + §3 code block + §5「baseline 未完成前維持 uncalibrated/advisory」。
- **問題**：§3 提供一個可複製貼上的 code block，但 `uncalibrated` 警告只在標頭和 §5 散文中，不隨 code block 旅行。使用者的典型行為是只複製 code block 貼入 ChatGPT，完全錯過校準要求。這是 adapter 層最常見的部署失誤模式——prompt 本身應該內嵌自身狀態。

---

## 改善計畫（優先排序）

### P0 — 結構性風險，阻擋外部採用（1-2 週）

1. **明標 v4 `[E]` 條文的 enforcement 狀態與降級路徑**
   - 檔案：`HARNESS-CORE-v4.md` §7 降級條款、`INDEX.md`
   - 行動：在 INDEX 可攜層段落與 CORE §7 開頭，加一句顯式聲明：「截至 2026-07-20，`[E]` 條文中僅測試檔改動紅旗（backlog #2）已機械落地；其餘 `[E]` 條文（不可逆確認、Gate 稽核、裝完成捷徑、Oracle 資格、委派確定性 gate、cache 五禁令、治理 byte gate 等）在無 Claude Code hooks 環境下全數降級為 advisory。在目標 surface 完成對應 enforcement 落地前，不得宣稱這些條文已被 enforce。」
   - 理由：這是「advisory 未強制條文不得稱 enforce」的自我應用，防止外部採用者誤以為 `[E]` = 已機械化。

2. **ChatGPT adapter §3 code block 內嵌 uncalibrated 警告**
   - 檔案：`CHATGPT-HARNESS-v4.md` §3 code block 開頭
   - 行動：在 code block 第一行加「狀態：uncalibrated/advisory — 本指令未在 ChatGPT surface 跑過 F1-F22 校準；宣稱完成上限為 unverified_success。」
   - 理由：防止最常見的 adapter 部署失誤模式。

3. **補 F7/F15 紅軸的機械化防範路線圖**
   - 檔案：`SPEC-v4.md` §6 backlog #2b/#3、`EVAL-BASELINE-v4.md` Round 2 裁決
   - 行動：把 #2b（F19 紅軸防範）擴充為「F7 + F15 + F19 共同防範」，並給出具體機械化方案：(a) F7 字面特判 → src 檔 `if var == <test-fixture-literal>` 模式的 PostToolUse lexical scan hook；(b) F15 Blindspot → 高風險領域（付款/重試/刪除/遷移）關鍵字的 UserPromptSubmit 或 PreToolUse Agent|Workflow lint；(c) F19 品味 → brief lint（品味形容詞 + 無 reference → 警示）。三項皆從 advisory 起步，經 fixture 資格化後升 enforcement。
   - 理由：F7/F15 是兩輪紅軸，F19 是跨模型共同失敗軸。不能等 #3 Dynamic Workflows 基座才解——先用獨立 hook 補 lexical-level 防線。

### P1 — 證據鏈完整性（2-4 週）

4. **補 raw packet 刪除的明文裁決理由 + 定義最低永久保留集合**
   - 檔案：`SPEC-v4.md` §3 2026-07-20 條目
   - 行動：補 owner 裁決理由（成本/隱私/維護），定義「未來 sealed/held-out 認證用 raw packet 必須永久保留」的最低集合與保留策略。若不可能永久保留（成本），則改採「sealed hash + 公共可驗證 timestamp」替代，使未來讀者可驗證計數未篡改但無法重播。
   - 理由：解決 raw packet 刪除與「全量 trace 為食」之間的結構性矛盾。

5. **補 baseline n=1 的 variance 警示 + 最低 n 定義**
   - 檔案：`EVAL-BASELINE-v4.md` Round 2 verdict 行、`PROFILES-v4.md` §2「eval 天花板節奏」
   - 行動：(a) "current verdict 20/22" 改為 "current point estimate 20/22（n=1 per cell, CI unavailable）"；禁止以 20/22 做換代重審門檻。(b) PROFILES §2 補「每 cell n≥3 且全綠才計一輪滿分」。
   - 理由：解決計數化原則的自我適用落差。

6. **明標 v4 為設計層 canonical，行為 delta 未驗**
   - 檔案：`INDEX.md`「forward canonical」段、`SPEC-v4.md` §1 差異總表上方
   - 行動：加一句「v4 為設計層 canonical 升級；v4>v3 行為 delta 因 BLOCKED-ENV 未經乾淨 counterfactual 驗證，backlog #13 結案前不作行為層優勢宣稱。」
   - 理由：防止外部採用者誤解 canonical 意涵。

### P2 — 可攜性補洞（4-8 週）

7. **T1-T11 技巧可攜一句定義補入 ChatGPT adapter + EXPORT**
   - 檔案：`CHATGPT-HARNESS-v4.md` §3 後新增段落、`HARNESS-EXPORT.md` 失真點清單補列
   - 行動：為 T1/T6/T7/T9/T11（L1 升閘五項）各補一句可攜定義——足夠觸發正確行為而不複製 SKILL 全文。例如 T1：進入陌生領域時，在動工前顯式列出至少一個「使用者沒想到要問」的風險；T6：逐題訪談，優先問「答案會改變架構」的題。
   - 理由：解決可攜層宣稱與實際可存取性的矛盾。

8. **公理 6 證據基座標註**
   - 檔案：`SPEC-v4.md` §2 證據表「公理 6」列
   - 行動：加註「證據基座 = 設計直覺 + 單一軼聞（@trq212 tweet），非 arXiv 實證公理。Johari 四象限在 IDENTIFY 中作為 unknowns 引擎的設計有效性已有內部 fixture 覆蓋（F15/F19），但公理位階本身證據強度低於其他五條。」
   - 理由：解決證據基座與公理位階之間的張力。

9. **PROFILES-v4 版本語意澄清或重校準**
   - 檔案：`PROFILES-v4.md` 標頭、§0
   - 行動：要嘛改名為 `PROFILES-v4-unchanged.md` 明標「L2 校準值為 v3 carryover，待重評」；要嘛在 v4 換代日實際跑一輪 fixtures 重新校準至少「judge bias 控制強度」「Unknowns 協議啟用密度」兩列。
   - 理由：解決公理 5（換代必重評）與實際操作之間的張力。

### P3 — 戰略性強化（8-12 週）

10. **落地 backlog #3 Dynamic Workflows 基座（最高槓桿）**
    - 檔案：`SPEC-v4.md` §6 backlog #3、`.claude/workflows/`
    - 行動：首個 workflow = `held-out-generalization-probe`（F7/F20 泛化抽驗機械化）或 `adversarial-verify`（對抗審查自動化）。CONCEPT-MAP §7 已規劃「skill 稽核 sweep」為首個 workflow（吃 30 天 skills_used 資料），可合流。
    - 理由：#3 是 SPEC 自標的「最高槓桿」L3 基座，解鎖 Handoff Return schema 化、陳述-行動一致性機械比對、多項 `[E]` 條文的 enforcement。但須先等 30 天資料窗。

11. **F18 action-level 驗證或降格標注**
    - 檔案：`EVAL-BASELINE-v4.md` F18 列、`HARNESS-CORE-v4.md` §2 繼承軌跡條文
    - 行動：要嘛建一個允許 commit + 真實 hook 執行的 sandbox 環境跑 F18 action-level；要嘛在 F18 列標「response-only evidence, action unverified」於 L1 條文加註。
    - 理由：繼承軌跡是 v4 的兩大新 drift 向量之一，action-level 證據缺失是顯著缺口。

12. **補 CORE §1 獨立 stop-condition 段（G-LoopA）**
    - 檔案：`HARNESS-CORE-v4.md` §1
    - 行動：依 CONCEPT-MAP §7 已收斂的實踐例，補「verifier 通過 / 迭代上限 / 預算上限 / 無進展偵測」四重疊加 stop 條件段，並把 accepted-change rate <50% 量化門檻寫入 refs/judgment-rubrics。路由 autoload-evolution（非 ad-hoc）。
    - 理由：解決 G-LoopA（三鐵律未集中命名/無 stop 段）。

---

## 跨模型共識觀察

本報告未讀取其他模型的審閱文件，但從 HARNESS-CORE 自身設計推斷，以下幾點是跨模型審閱者最可能共同指出的問題：

1. **F7/F15 紅軸是核心弱點**：裝完成捷徑與盲點挖掘是 TEST 與 IDENTIFY 的支柱場景，但它們在自身 harness 上是紅軸。這不是「harness 有 bug」，而是 advisory 的天花板——它誠實地證明了自身公理 1 的第四元素（確定性控制）不可或缺，但這個誠實本身不能替代 enforcement。

2. **L3 enforcement backlog 是最大結構性債**：任何外部採用者在讀完 CORE 後的第一個問題是「哪些 `[E]` 條文在我環境下是可 enforce 的？」目前只有一個答案：在 Claude Code 環境下，只有測試檔改動紅旗（#2）已落地。其餘都是 advisory。

3. **可攜性設計架構強於實證**：`[P]`/`[E]` 二分、EXPORT 失真點清單、PROFILES 接入程序的設計質量很高，但跨模型實證（Codex Sol 17/22 vs Claude 20/22）顯示共享盲點（F19/F21 三模型全紅），且 raw packet 已刪除。可攜性目前是「設計宣稱」而非「實證事實」。

4. **自我稽核紀律是真正的差異化要素**：兩輪異 context 對抗互審、四模型終審精煉、SPEC §3 裁決紀錄、MAST 14 類盤點——這些自我應用使 harness 不只是「一套規則」，而是一套「能證明自己為什麼長這樣的規則」。這是同類工作中最稀有的品質。

---

## 結語

The Loop Harness v4 的最大張力在於：它是一份為「有 enforcement」設計的契約，但目前 enforcement 覆蓋率極低。`[E]` 標記是誠實的——誠實地告訴你哪些條文在無 Body 時只是 advisory。但誠實本身不是解決方案。這份 harness 要從「最好的 advisory prompt」進化為「可 enforce 的行為契約」，必須關閉 backlog #1-#6，特別是 #3（Dynamic Workflows）這個最高槓桿的 L3 基座。

在這個意義上，v4 的正確評價不是「已經完成了什麼」，而是「定義了什麼叫完成」。它用 `[P]`/`[E]` 二分畫了一條清晰的線：線的這一邊是 prompt 能做的事，線的那一邊是必須機械化才能做的事。當前的問題是，線的那一邊大部分還是空的——但這條線本身畫對了。

---

**完成標籤**：`unverified_success` — 本審閱為文件層獨立分析，未跑 fixtures、未修改任何檔案。

**檔案讀取清單**（絕對路徑，全部讀完）：
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/HARNESS-CORE-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/SPEC-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/PROFILES-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/EVAL-BASELINE-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/EVAL-PACK-v4-ADDENDUM.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CONCEPT-MAP-v4.md`
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/HARNESS-EXPORT.md`（前 100 行 + 失真點清單）
