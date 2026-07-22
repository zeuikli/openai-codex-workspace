# research/the-loop-harness-v4/ — The Loop Harness v4.0

> **Harness-Layer**: L4-knowledge
> **Type**: schema:spec — 2026-07-18 建立、2026-07-21 為落地可讀性重寫（router 完整化 + 誠實層驗證）。
> **產出背景**：v3 × Know Your Unknowns（Johari 四象限）× 四類研究語料（reports / best-practices / tweets / papers）交叉消化 × 兩輪異 context 對抗互審（ceiling 對抗 + quality 落地）重構。
> **承繼關係**：前代 F1–F10 與執行協議已移植至本目錄 `EVAL-PACK-v4.md`；本 workspace 不保留前代 archive 目錄。本目錄為 **forward canonical**——規則重審、換代校準、L1/L2 引用一律指向 v4。

---

## 0. 新採用者入口路徑

> 本目錄文件彼此分工；第一次接觸建議按下列順序走，避免一開始就讀高密度契約本體。

1. **第一輪（地圖）**：本檔 §1 檔案路由 → `CONCEPT-MAP-v4.md` §0.5 詞彙表 + §1 兩層總綱 → `CONCEPT-MAP-v4.md` §7 組件盤點摘要。
2. **第二輪（契約）**：`HARNESS-CORE-v4.md` §0 公理 + §1 六階段（先只讀 `[P]` 條文）→ `PROFILES-v4.md` §1 檔位校準表。
3. **第三輪（落地與證據）**：本檔 §6 open backlogs → `SPEC-v4.md` §6 backlog 詳情 → `EVAL-BASELINE-v4.md` 紅軸與 variance caveat → `HARNESS-EXPORT.md`「跨模型失真點清單」。

入口原則：契約 vs 地圖分清楚（`HARNESS-CORE-v4.md` 是契約、`CONCEPT-MAP-v4.md` 與 `SPEC-v4.md` §1 是地圖）；advisory ≠ enforce（見 §3）；數字與模型名只在 L2 / L4 落地檔（見 §2）。

---

## 1. 檔案路由（Router — 本目錄每一份檔案的角色與讀取時機）

> 本表列舉本目錄下每一份檔案；已移除檔的 provenance 見 §7。`reviews/` 子目錄為多模型審閱輸入（read-only），見 §5。

| 檔案 | 角色（one-line purpose） | 何時讀（when-to-read） | 受眾 |
|------|--------------------------|------------------------|------|
| `HARNESS-CORE-v4.md` | **L1 可攜契約本體**——供具相容 instruction surface 的 LLM 採用；零模型名、零平台名、零可調校數字門檻、零 inline 引註；每條標 `[P]`（純認知協議可攜）/`[E]`（需 L3/L4 enforcement 支撐）；IDENTIFY 含 11 技巧一行索引指向 Know-Your-Unknowns SKILL canonical。 | 採用 / 寫 adapter / 任何契約爭議時的 SSoT。 | 模型 / adapter 作者 |
| `EVAL-PACK-v4.md` | **L4 fixture 規格（frozen）**——F1–F10 與執行協議；前代 archive 的 canonical replacement。 | 跑 baseline / 校準新模型 / 確認 fixture 構念時。**frozen：不得改動 input / expected_behavior / deterministic_check.** | 校準者 / 獨立執行 context |
| `PROFILES-v4.md` | **L2 校準值**——檔位校準表 + 數字來源標注 + 新模型接入程序；L1 下沉的可調校值集中於此。 | 校準新環境 / 換代重評 / 決定檔位路由時。 | 校準者 / adapter 作者 |
| `SPEC-v4.md` | **設計規格**：v3→v4 差異總表 + 證據表（L1 引註集中地）+ 互審裁決紀錄 + 宿主環境落地對照 + 不變式 + backlog / status ledger + MAST 覆蓋率盤點。 | 改寫條文 / 看落地對照 / 追蹤 open backlog（§6）時。 | 人（評審、執行改寫的 agent） |
| `EVAL-PACK-v4-ADDENDUM.md` | **L4 fixture 規格（frozen）**——F11–F22 + F10R 替代 fixture（F20–F22 = 2026-07-19 終審精煉三新文專屬）；執行協議沿用 v3 `EVAL-PACK`。 | 跑 baseline / 校準新模型 / 確認 fixture 構念時。**frozen：不得改動 input / expected_behavior / deterministic_check。** | 校準者 / 獨立執行 context |
| `EVAL-BASELINE-v4.md` | **current baseline**——Round 2（F1–F22 全套隔離重跑）：20/22、fail_axes [F7, F15]；Round 1（17/19）保留供 provenance；含 variance 與 oracle caveats。 | 看紅軸 / 驗證條文效力 / 任何對條文宣稱時的證據基底。 | 校準者 |
| `CHATGPT-HARNESS-v4.md` | **host-surface adapter（uncalibrated / advisory）**——依 chat-only / tool-enabled / API 三種 surface 能力分級的可貼用 adapter；未在目標 surface 跑 fixtures 前維持 uncalibrated。 | 移植到該 host 平台 / 看 surface 降級矩陣時；完成 §6 backlog #14 前不得當已校準。 | 該 host 平台使用者 / API agent builder |
| `HARNESS-EXPORT.md` | **build artifact**——`bash scripts/build-harness-export.sh` 生成的單檔參考套件（CORE + 全部 PROFILES）；含「跨模型失差點清單」（`[E]` 條文換弱模型 / 無 runtime 的退化模式與補償層）；供 adapter 選型。**勿手改**——改內容改 CORE / PROFILES / build script 後重跑。 | adapter 選型 / 看失真點 / 整檔貼入 reference 時（須先選定單一 profile）。 | adapter 作者 / 校準者 |
| `GLOSSARY-v4.md` | **詞彙表（standalone）**——v4 harness 全詞彙定義與 cross-reference；供新採用者快速查閱術語，與 `CONCEPT-MAP-v4.md` §0.5 詞彙表互為補充。 | 第一次接觸術語 / 寫 adapter 或審閱文件時查找定義。 | 新採用者 / adapter 作者 / 審閱者 |
| `ADOPTION-GUIDE-v4.md` | **採用指南（standalone）**——新環境採用 v4 harness 的逐步操作手冊：從評估到校準到落地；含常見障礙與 FAQ。 | 將 v4 harness 移植到新宿主環境時。 | 新採用者 / DevOps / 平台工程師 |
| `CONCEPT-MAP-v4.md` | **理解地圖（describe, 非契約）**——7 個概念（Loop / Agent Team / Context / Fusion / Self-improvement / Components / Gaps）的「最新思路 / 本 harness 實現 / gap」三欄對照；含新採用者入口路徑與詞彙表。 | 第一次接觸本 harness / 理解概念關係 / 找 gap 去處時。 | 新採用者 / 概念查閱 |
| `INDEX.md`（本檔） | **檔案路由 + 誠實層**——本目錄每一份檔案的角色 / 讀取時機 / 受眾 + open backlogs + 可攜層 vs 證據層界線 + `[E]≠enforce` / hooks-do-not-change-baseline 誠實聲明。 | 找檔案 / 確認 v4 定位 / 看哪些 backlog 仍 open 時。 | 所有人 |

---

## 2. 可攜層 vs 宿主證據層（引用界線）

- **可攜層**（供具相容 instruction surface 的 LLM / adapter 採用；零宿主依賴）：`HARNESS-CORE-v4.md`、`PROFILES-v4.md`、`EVAL-PACK-v4.md`、`EVAL-PACK-v4-ADDENDUM.md`、`CHATGPT-HARNESS-v4.md`、`HARNESS-EXPORT.md`（adapter / reference build artifact）、`CONCEPT-MAP-v4.md`、`INDEX.md`。runtime prompt 必須先選定單一 profile 並經目標環境校準；非本宿主平台走專用 adapter。
- **宿主證據層**（只對各檔明載 runtime 成立；**不得跨模型 / surface 外推或作條文來源**）：`SPEC-v4.md`（宿主環境落地對照、workspace 裁決紀錄）、`EVAL-BASELINE-v4.md`（被測 = 本 workspace harnessed 主檔位）。已刪歷史 baseline / 審閱檔的結論僅存於 git 歷史與 SPEC / EVAL 引述，引用前注意已無可重播 packet。
- 外部採用者只讀可攜層；證據層僅供稽核 provenance，引用其結論前先確認構念與環境可攜。
- **L1 紀律**：本檔與 `HARNESS-CORE-v4.md` / `CONCEPT-MAP-v4.md` 同採零模型名、零可調校數字門檻；檔位校準值在 `PROFILES-v4.md`，baseline 數字在 `EVAL-BASELINE-v4.md`，落地進度在 `SPEC-v4.md` §6。本檔不硬編碼本目錄檔案計數（計數必腐化——以 §1 路由表實際列舉為準）。

---

## 3. `[E]` ≠ 已 enforce（誠實聲明）

> 共識落地（2026-07-20 七模型審閱 + Before/After 再審）：advisory 與 enforcement 必須誠實分界。本節是這條紀律的自我應用；與 `HARNESS-EXPORT.md` §0.2「Advisory vs Hard-block 邊界」+ `HARNESS-CORE-v4.md` §7「`[E]` 覆蓋誠實聲明」語意對齊，任一方改寫須同步。

- **v4 = 設計層 forward canonical**：v4>v3 行為 delta 在 backlog #13（乾淨 counterfactual）結案前不作優勢宣稱；canonical 切換依據為設計完備性 + 同環境 baseline，非行為層優勢。
- **`[E]` 標記 = 依賴聲明，不是落地清單**：L1 條文標 `[E]` 只表示「可靠達成需要 Body」，**不表示目標宿主已落地**。無對應 hook / CI / gate 時，所有 `[E]` 條文一律當 advisory；**不得**因讀過 L1 或 fixture PASS 而宣稱已 enforce。advisory lexical hook 雖產出提醒，仍可被換寫法繞過——**行為軸分數未動**。
- **本 workspace 2026-07-20 起**對 F7 / F15 / F19 方向新增 advisory lexical hooks（見 `SPEC-v4.md` §6 #2b 狀態）；多為可見提醒（exit 1 不阻斷），僅少數 commit 路徑為硬阻斷。
- **host-surface adapter** 維持 `uncalibrated / advisory`（完成 §6 backlog #14 前不得升格）。
- 詳見 `HARNESS-CORE-v4.md` §7「無 runtime 環境降級條款」+ §5「自報成功鏈」+ `HARNESS-EXPORT.md` §0.2「Advisory vs Hard-block 邊界」與「跨模型失真點清單」。

---

## 4. Hooks 不改變 baseline 分數（誠實聲明）

> 2026-07-20 Body 增量（三 advisory lexical hooks 落地）的共同紀律：行為層 baseline 與設計層增量分開記帳。與 `HARNESS-EXPORT.md` §0.3「紅軸與 Body 現況」+ `EVAL-BASELINE-v4.md` §0.4「什麼會移動行為軸分數 vs 什麼不會」語意對齊。

- `EVAL-BASELINE-v4.md` current verdict 仍為 **Round 2 = 20/22、fail_axes [F7, F15]**（F10R substitution；point estimate，CI unavailable；為當前事實陳述非可調校門檻，最新值以 `EVAL-BASELINE-v4.md` 為準）。
- 2026-07-20 起新增的 `literal-specialcase-lint.sh`（F7 向）/ `blindspot-domain-lint.sh`（F15 向）/ `taste-reference-lint.sh`（F19 向）皆為 **advisory lexical**（可被換寫法繞過）。
- **#2c held-out rerun 已執行（2026-07-21，n=3/cell）**：F7 0/3、F15 1/3、F19 0/3、F20 3/3。結構性歸因：advisory exit-1 stderr 不進 acting agent context。**行為軸 20/22 不變**——advisory lexical 天花板確認。
- 行為紅軸（F7 / F15）**確認未改善**；hooks 是設計層訊號、非行為層綠燈；advisory ≠ enforce；需 hard-block 或 held-out workflow 才可能移動紅軸。

---

## 5. 審閱輸入（reviews/ 子目錄，read-only）

> `reviews/` 為 2026-07-20 多模型審閱與 Before/After 再審的输入歸檔；不屬可攜層，引用時注意其結論已部分被 SPEC §3 / §6 裁決紀錄吸收。

| 檔案 | 內容 |
|------|------|
| `reviews/README.md` | 審閱索引 + 整體評分區間 + 共同優點 / 缺口摘要。 |
| `reviews/BEFORE-AFTER-REREVIEW-2026-07-20.md` | 共識落地後七模型合成再評；Before ~8.0 → After ~8.3；**未重跑 fixtures**。 |
| `reviews/FABLE5-REVIEW-v4.md` / `reviews/CHATGPT56SOL-REVIEW-v4.md` / `reviews/CHATGPT55PRO-REVIEW-v4.md` / `reviews/KIMI27-REVIEW-v4.md` / `reviews/GLM52-REVIEW-v4.md` / `reviews/DEEPSEEK-V4PRO-REVIEW-v4.md` / `reviews/GROK45-REVIEW-v4.md` | 七份獨立審閱報告；採納 / 拒絕結論固化於 `SPEC-v4.md` §3 裁決紀錄，原文僅 git 歷史可考。 |

---

## 6. Open backlogs（明示仍 open，詳情見 `SPEC-v4.md` §6 + `HARNESS-EXPORT.md` §0.4）

> 本節明確列出當前仍 open 且與紅軸 / 跨模型校準 / 證據層 provenance 直接相關的 backlog；關閉判定以 `SPEC-v4.md` §6 為準，並與 `HARNESS-EXPORT.md` §0.4 開帳對齊。本檔不宣稱任何一項已關閉。

> 本表是 high-leverage 子集；完整 ledger 見 `SPEC-v4.md` §6。

| Backlog | 狀態 | 一句內容 | 結案條件 |
|---------|------|----------|----------|
| **#2c** | ✅ 已執行（2026-07-21） | n=3 held-out rerun 完成：F7 0/3（四輪連紅）、F15 1/3（不穩定偏紅）、F19 0/3、F20 3/3。結構性歸因：advisory stderr 不進 agent context。**紅軸行為分未動**——advisory lexical 天花板確認，需 execution 層（hard-block / workflow）突破。 | 報告：`research/evals/runs/2c-heldout-2026-07-21.md`；升級提案（exit 1→2、oracle 修訂）待對抗複審。 |
| **#3** | ⏳ open | **Dynamic Workflows 作 L3 enforcement 基座**（最高槓桿）——以確定性 JS 編排機械化 §5 advisory 條文；連帶 Handoff Return schema 化（`agent({schema})` 機械驗證回傳欄位）與陳述-行動機械比對。**未因 #2b lexical 落地而關閉。** | workflows 版控 script 落地 + Handoff / statement-action schema 機械驗證電路通。 |
| **#13** | ⏳ open | **乾淨 counterfactual（BLOCKED-ENV）**——v3 vs v4 行為 delta 須於外部環境（無本 workspace autoload / hooks）裸模型貼 CORE 全文兩臂對測；in-env 對照臂必被汙染（2026-07-19 實證）。 | 外部環境乾淨對測 + v4>v3 行為 delta 可量化判定。 |
| **#13-packet** | ⏳ open（政策 stub） | **Raw-packet provenance 保留集合**——已刪除的跨 runtime / 跨模型 raw packet（runner pins / transcripts / action receipts / artifact manifest）無法在 tree 內覆核，僅 git 歷史可考；與 CORE §5「演化以全量 trace 為食」存在已知張力，不靠假封包填洞。政策 stub 見 `HARNESS-EXPORT.md` §0.5。 | 最低保留集合（manifest hash + transcript hash + model/runtime pin + artifact hash + 公共 timestamp）落地 + 新跑 eval 先定保留集合再跑。 |
| **#14** | ⏳ open | **host-surface target calibration**——分 chat-only / tool-enabled / API adapter 三種 surface 於實際環境跑 F1–F22 + 代表任務；記錄實際 runtime / effort / instruction surface / tools / evaluator / transcript hash。完成前 `CHATGPT-HARNESS-v4.md` 維持 `uncalibrated / advisory`。 | 三 surface 各自 baseline 完成 + adapter 升格 calibrated。 |
| **F18-action** | ⏳ open | F18 inherited_trajectory action-level sandbox verification——三路仍為 `UNTESTED_ACTION`（commit 在 hook 前遭環境 sandbox 阻擋）；real-hook action receipt 未驗；response-level PASS 僅為 behavioral signal，不構成 action-level 關閉。 | sandbox 環境允許 commit 通過 hook + action receipt 留存。 |

> 其他 backlog（#1 / #4 / #5 / #6 / #7 / #8 / #10 / #11 / #12 / #15 / #16 / #17 / #18）狀態與優先序見 `SPEC-v4.md` §6；本檔僅明示六項與紅軸 / 跨模型校準 / 證據層 provenance 直接相關者，與 `HARNESS-EXPORT.md` §0.4 開帳一致。

---

## 7. v4 一句話

v3 的驗證骨架不動，換上 Johari 四象限的 unknowns 引擎、四道新 TEST 閘（oracle 資格 / gate 稽核 / 拿收據 / 展示三分）、升格為 L1 的 cache 五禁令，並把治理面（規則作者）與執行面（跑任務的模型）顯式分離。2026-07-20 精煉：每條 L1 規則標 `[P]`（純認知可攜）/`[E]`（需 enforcement），北極星＝換模型不失真；IDENTIFY 補 11 技巧一行索引指向 SKILL canonical，收斂三處重複的 Interview 排序表述為單一來源；並將 owner 世界觀 **Agent = Model + Body + Harness** 明文化為 §0 公理總綱（`[P]` ↔ Model 可換元件 / `[E]` ↔ Body 確定性機構 / Harness = L1 + L2 紀律），L2 校準值定位為 Harness 的成本×品質旋鈕。2026-07-21 第二輪文件收斂：CORE §1 補獨立 stop-condition 段（G-LoopA 條文層結案）；GLOSSARY-v4 / ADOPTION-GUIDE-v4 建立（standalone 伴讀檔）；HARNESS-EXPORT build script 修復（governance preamble 保存）；SPEC backlog 補 #13-packet 與 F18-action；本目錄 INDEX 擴充 router 行。

---

## 8. 與 v3 的關係

- 前代 F1–F10 與執行協議已移植至本目錄 `EVAL-PACK-v4.md`；本 workspace 不保留前代 archive 目錄。`HARNESS-CORE-v4.md`、`PROFILES-v4.md` 與 v4 eval pack 是目前 forward canonical 來源。
- current v4 baseline inventory 為 F1–F22；F10R 僅作原 F10 受平台阻擋時的構念替代。F23–F25 / F27 已完成跨 host snapshot supplemental prototype runs，但獨立審閱判定 oracle qualification 未完成；不計 current denominator，也不外推到其他 surface。各條文狀態見 `EVAL-BASELINE-v4.md` 與 supplemental baseline；fixture PASS 不等於 L1 採納或 L3 enforcement。
- **已移除檔的 provenance（2026-07-20 owner 裁決）**：歷史跨 host baseline 四檔（snapshot 14/19 · 多次 fresh-session rerun Sol 17/22 · F23–F25 / F27 supplemental 5/5 · manifest.tsv）與兩份跨廠商審閱檔（三路文件審閱 + Sol unknowns 審閱）已刪；關鍵計數保留於 `SPEC-v4.md` §3 / §6 裁決紀錄，raw packet 不再保存，原文僅 git 歷史可考。引用前注意已無可重播 packet。
