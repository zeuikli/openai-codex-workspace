# PROFILES v4.0 — Per-Model Calibration（L2）

> 掛接 `HARNESS-CORE-v4.md`（公理 4 雙軸伸縮 + 各段能力伸縮條款；L1 零可調校數字門檻，所有校準值集中於本檔）。每欄數字須標注校準來源與日期；未標注 = 沿用上一世代預設，屬待重評項。
> 鐵律（不變）：**行為指導量與能力成反比；驗證閘門強度與能力成正比。**
> 檔位為抽象層（cost/quality/ceiling/frontier），模型名為當代對應——換代改對應、不改條文。
> **MBH 定位**：於 Agent = Model + Body + Harness 框架（CORE §0 總綱）中，本檔 L2 校準值 = **Harness 的成本×品質旋鈕**——把可換 Model 的能力與 Body 的 enforcement 強度綁定到具體檔位，使「以合理駕馭達成品質×成本雙目標」可操作化。
> **承接關係**：本檔為公版可攜內容，宿主環境專屬落地路徑一律以「宿主落地檔」抽象指稱，實際路徑由各宿主環境自定。v4 數字層以 v3 世代為基底，並於 2026-07-21 補入 G-LoopA 終止條件、eval 每 cell 最低 n 等 v4 條文直接指涉的門檻；其餘數字仍為 v3 carryover，來源標注保留。
> **L1 優先**：L2 只可操作化或加嚴 L1，不得以檔位為由豁免 L1 安全、驗證或高風險 judge 不變式。

**Current model IDs**：`gpt-5.6-luna`、`gpt-5.6-terra`、`gpt-5.6-sol`；model mapping 由宿主 `.codex/profiles.json` wired SSoT 管理，尚屬 provisional，未由 v4 full calibration 證明。

---

## 0. 增量摘要（v3→v4：條文層大改，數字層部分承接 + 2026-07-21 補齊 dangling pointers）

1. §1 檔位校準表新增兩列：「judge bias 控制強度」「Unknowns 協議啟用密度」（cost = Interview 必開／frontier = Blindspot 自主）。此兩列值為 v3 世代 carryover，因 v4 L1 改動（TEST 四新閘、Johari 四象限化）**須在 v4 fixtures 重跑或乾淨 counterfactual 後重校準**，已於 §1 表尾與 §2 標註 recal trigger。
2. §2 新增「宿主落地雙軌說明」：人讀落地檔（散文+表格）與機讀落地檔（供 hooks/自動化消費）由宿主環境自定路徑，三處數字（本檔 + 兩個落地檔）須一致，以機讀檔為 wired SSoT。
3. §2 校準表新增/補齊 2026-07-21：
   - `eval 每 cell 最低 n（full-score round）`：n≥3 才計一輪滿分；n=1 僅 point estimate（CI unavailable，不可作 generation-retrial verdict gate 或換代重審門檻）。
   - `自主迴圈迭代上限（L1 G-LoopA）`：待校準（建議值），recal trigger 明訂；與 CONCEPT-MAP §8.3 / `research/EVOLUTION-QUEUE.md` #2 及 SPEC §6 #3 對齊。
   - `G-LoopA 無進展門檻`：accepted-change rate <50% 連續 2 輪 → 停滯上呈（CONCEPT-MAP §7 實踐例）；目前值為建議值，待 n≥3 自主 loop 數據驗證。
   - `G-LoopA 預算上限`：補上 CORE §1 終止條件第三項的 dangling pointer，列為待校準（建議值）；與 SPEC §6 #3 Dynamic Workflows 基座對齊。
   - `IDENTIFY 簡短詮釋句數上限（v3 殘留）`：SPEC §3 列出「≤2 句」為已下沉的 L1 數字殘留，但 v4 CORE 已移除該數字門檻；本行保留作合約對帳，標「無現行 L1 綁定」。
4. §4「新模型接入程序」以 `EVAL-PACK-v4.md`（F1–F10）+ `EVAL-PACK-v4-ADDENDUM.md`（F11–F22；當前 suite = 22 軸）為主軸，與 5–10 個代表任務合併執行。
5. 版本標記：v4.0 · 2026-07-21（數字層最後修訂）。

---

## 1. 檔位校準表（沿用 `PROFILES-v2.md` §1，2026-07-04；新增末兩列，並標註 recal trigger）

| 維度 | cost（最省檔） | quality（均衡檔） | ceiling（深推理檔） | frontier（最強檔） | 未知/新接入模型 |
|------|-----------------|---------------------|-------------------|---------------------|------------------------------|
| 行為指導密度 | 高（步驟級指示，prompt 逐命令寫死） | 中 | 低 | 最低（目標級） | 初始=高，跑 5–10 任務後調整 |
| ask-rate | 多問少決 | 小決策自決+註明 | 同左 | 同左＋自決範圍擴大 | 多問少決（未知模型先保守） |
| 單任務 diff 軟上限 | ≤30 行 | ≤120 行 | ≤300 行 | 依宣告 scope | ≤30 行起 |
| 委派門檻 | 不委派（自身即末端） | ≥10 檔 / >20 工具呼叫，且需具名效益（v3 benefit-gated） | 同左 | 同左，可自主編排 | 視環境有無 sub-agent |
| **驗證深度（遞增）** | 基本測試 | +宿主 healthcheck（確定性健檢腳本） | +交叉評審 | **+對抗稽核**（主動假設 eval-hack，找繞過痕跡） | 至少比照 ceiling：交叉評審 + parent gate；校準前不放鬆 |
| eval-hack 風險評級 | 未校準；不得因能力較低而放鬆廉價 gate | 中 | 中高 | **最高**（16.6% 實測參考） | 未知=當最高處理 |
| 成本備註 | 最便宜但**非成本單調**（見 §3 O9） | 甜蜜點 | 架構/深推理 | effort-first：先調 effort 再換模型 | 按供應商定價另計 |
| 記憶寫入權 | 只記事實 | 事實+教訓 | +結構化反思 | +失敗假設與演化候選 | 只記事實 |
| **judge bias 控制強度（v3 新增；v3-carryover-pending-recal）** | 低風險可單輪給分；高風險仍依 L1 盲化 + 對調 | 中：高風險比較須盲化身份 + rubric 逐項給分 + 對調 | 高：+記錄 position_consistency | **最高**：盲化＋對調＋逐項 rubric＋分歧即視為任務歧義訊號，交確定性檢查或人裁決 | 未知=比照 ceiling 起跳 |
| **Unknowns 協議啟用密度（v3 新增；v3-carryover-pending-recal）** | **Interview 必開**（歧義先逐題訪談再動工，不自行猜測） | Interview 常開 + Blindspot 視領域陌生度啟用 | 三構件（Blindspot/Interview/Prototype-first）依風險彈性開關 | **Blindspot 自主**：不待提示，開工前主動掃描「使用者沒想到要問的事」並回報 | 未知=比照 cost（Interview 必開），跑滿 eval pack 後再放寬 |

> **§1 v3-carryover-pending-recal 標註**：上表「judge bias 控制強度」與「Unknowns 協議啟用密度」兩列值為 v3 世代 carryover。因 v4 L1 改動（TEST 四新閘改變 judge 任務結構；Johari 四象限重新定義 Unknowns 啟用條件），兩列須在 **v4 fixtures 新一輪 n≥3 重跑（同 SPEC §6 #2c；含 F5/F7/F15/F19/F20/F21 等 judge/Unknowns 相關軸）或 backlog #13 乾淨 counterfactual 結案後** 重校準；未重校準前不得視為已對 v4 校準。

---

## 2. 校準值來源標注（沿用 `PROFILES-v2.md` §2，2026-07-04；2026-07-21 補齊 dangling pointers 與 recal trigger）

| 門檻名 / CORE 指涉 | 目前值 | 校準來源 | 重校準觸發條件 / 狀態 |
|------|--------|---------|---------|
| per-task token budget | ~4,000 | quality 檔位世代宿主實測 | 待 frontier 世代重評；或 per-task 實際 token 分布偏離 >20% 時 |
| per-session budget | ~30,000（軟）| 同上；**frontier 稽核級 session 實測 subagent 總量 ~445k**（8 agents）——長 agentic 例外量級參考 | 同上；長 agentic session 總量異常時須以例外量級重新估算 |
| fan-out 上限 | 4（手動）/16（runtime） | 宿主委派規則 + 2026-07-03 實跑 | 已驗證；runtime 平台變更或 healthcheck 攔截到新違規時重評 |
| 常駐 byte 門檻 | ≤13,000 / 13–19k / >19k | 宿主常駐規則 byte gate；實測攔截自我違規一次（19,479→18,969） | 維持；語言/tokenizer 切換或 auto-load 英文化時須改單位為 token 並重校準 |
| eval 回歸 revert 線 | ≥5pp，判定**計數化**：per-task「criteria_passed + fail_axes 全等」確定性對比；judge 0–10 降參考（禁兩 judge 原始分互減） | field data 2026-07-03（judge ±1 噪音致 5pp 誤報） | 已校準；落地於 `EVAL-PACK-v4.md` §Pass Rule；出現新的 judge 噪音分布時重評 |
| 檔位驗證深度=+對抗稽核 | 異模型 fresh-context 對抗審查 | 2026-07-03 實證：唯一攔到 P1 的機制 | 續累積樣本；新增跨模型 baseline 或對抗審查機制改變時更新 |
| eval 天花板節奏 | 連 2 輪滿分 → spec 加嚴 → 重錨 baseline（回落≠回歸，用 fail_axes 歸因區分） | O10/O13 | 已落地；「滿分輪」須滿足本表「eval 每 cell 最低 n」n≥3 條件才啟動加嚴 |
| worktree agent 開銷 | 每 agent ~200–500ms + 污染 healthcheck 風險；用完即 remove | O4/O8 | 已記錄；worktree runtime 或 healthcheck 機制改變時重測 |
| T0 邊界修正 | ≤3 筆給定文字機械編輯 → main 親做（委派固定開銷 > 模型智力差） | O9/O16 | 已校準；併入 benefit-gated delegation（見 `HARNESS-CORE-v4.md` §3）；委派固定開銷或工具呼叫延遲顯著變化時重評 |
| 終局展示行數（L1「首尾節錄」門檻；v3-carryover-pending-recal） | 前 5 行 + 後 5 行 | v3 展示紀律原值（2026-07-18 自 L1 下沉） | 維持，但 pending recal：v4 展示紀律三分化（中間靜默／終局出示／失敗大聲）後，須以 n≥3 重跑 F16/F17 驗證 5+5 是否仍為最適門檻（與 SPEC §6 #2c 同樣的 n≥3 紀律，雖 F16/F17 非 #2c 紅軸）；或於 backlog #13 乾淨 counterfactual 後重評 |
| 規則變更重現門檻（L1「達門檻次數」） | 同一簽名獨立重現 ≥2 次 | v3 RECORD 原值（自 L1 下沉） | 維持；出現同一簽名只重現 1 次即誤改規則的實例時重新評估 |
| 每檔位 fallback 候選數（L1「多候選」門檻） | ≥2 | v3 平台疆域原值（自 L1 下沉） | 維持；平台疆域事件（如單一供應商 72h 下架）後評估是否需提高 |
| eval 每 cell 最低 n（full-score round / 換代重審門檻） | **n≥3** per cell 才計一輪滿分；n=1 僅 point estimate（CI unavailable，不可作 generation-retrial verdict gate 或換代重審門檻） | F15/F19 單樣本翻轉不可歸因（2026-07-19 Round 2 實證） | 新增 2026-07-21；下一輪 F1–F22 n≥3 隔離重跑（SPEC §6 #2c）後驗證此門檻是否足以區分 variance 與 true regression |
| 自主迴圈迭代上限（L1 G-LoopA；CORE §1 終止條件 #2） | 待校準（建議依任務風險分級：低風險 ≤5 輪、中風險 ≤10 輪、高風險/不可逆 ≤3 輪為起點） | CORE §1 G-LoopA（v4.0 2026-07-18）+ CONCEPT-MAP §7 分層終止四重疊加實踐例 + CONCEPT-MAP §8.3 / `research/EVOLUTION-QUEUE.md` #2；PROFILES 行補齊 2026-07-21 | 待校準：須以 n≥3 自主 loop 數據（如 F7/F20 held-out rerun 或 skill-audit 自動化 Routine）測量「迭代輪數 vs 淨進展」後賦值；或於 SPEC §6 #3 Dynamic Workflows 基座落地後以 loop 狀態機實測。未校準前不得作為硬阻斷 |
| G-LoopA 無進展門檻（L1「accepted-change rate」；CORE §1 終止條件 #4） | 待校準（建議值）：accepted-change rate <50% 連續 2 輪 → 視為停滯上呈 | CORE §1 G-LoopA（v4.0 2026-07-18）+ CONCEPT-MAP §7 實踐例（@eng_khairallah1-565100、@choopyplug1-503774）；PROFILES 行補齊 2026-07-21 | 待校準：須以 n≥3 自主 loop 數據（如 F7/F20 held-out rerun 或 skill-audit 自動化 Routine）驗證 50% 與 2 輪是否為最適門檻；或於 SPEC §6 #3 Dynamic Workflows 基座落地後以 loop 狀態機實測。未校準前作為建議性訊號 |
| G-LoopA 預算上限（L1 G-LoopA；CORE §1 終止條件 #3） | 待校準（建議值）：token / time / cost 三維分設；建議與 per-task / per-session budget 解耦，專為自主 loop 設硬停機線 | CORE §1 G-LoopA（v4.0 2026-07-18）已指涉此門檻；PROFILES 行補齊 2026-07-21；尚無實測 | 待校準：須在 SPEC §6 #3 Dynamic Workflows 基座或宿主 runtime 以 n≥3 loop 成本樣本實際測量後賦值；未校準前以 per-session soft budget 為參考 |
| IDENTIFY 簡短詮釋句數上限（v3 殘留；SPEC §3 列為已下沉數字） | 無當前值（v4 CORE §1 IDENTIFY 已移除「≤2 句」數字門檻，改為「簡短詮釋」質性要求） | SPEC §3 互審紀錄「L1 數字殘留（…≤2 句）→ 下沉 PROFILES」；v4 CORE 實際無此門檻 | 合約對帳項：若未來 CORE 重新引入句數上限，再校準；目前不視為 active 門檻 |

> **§2 v3-carryover-pending-recal 標註**：上表「終局展示行數」為 v3 世代 carryover。因 v4 展示紀律三分化（迴圈中間靜默、終局出示、失敗大聲），5+5 行門檻須在 **v4 fixtures 新一輪 n≥3 重跑（F16/F17 展示紀律相關軸；n≥3 紀律同 SPEC §6 #2c）或 backlog #13 乾淨 counterfactual 結案後** 重校準；未重校準前維持原值但標為 pending recal。
>
> **dangling-pointer 結案聲明**：截至 2026-07-21，`HARNESS-CORE-v4.md` §1 所有指向 PROFILES 的門檻（終局展示行數、G-LoopA 迭代上限/預算上限/無進展門檻、規則變更重現門檻、每檔位 fallback 候選數）均已在本表有對應列；`SPEC-v4.md` 所列「前5後5/≥2 次/≥2 候選/≤2 句」L1 數字殘留中，除「≤2 句」因 v4 CORE 已移除該門檻而標為「無現行 L1 綁定」外，其餘三項均已對帳。

### 宿主落地雙軌說明（v3 新增；路徑由宿主環境自定）

- **人讀落地檔**：人查閱用（散文 + 表格），路徑由宿主環境自定。
- **機讀落地檔**：供 hooks / 自動化 pipeline 讀取數字（取代散佈於各腳本的硬編碼模型名/數字），格式建議 JSON。
- **一致性要求**：本檔（研究層 canonical 敘述）、人讀落地檔、機讀落地檔三處數字**必須一致**；不一致時以機讀落地檔為 **wired SSoT**（唯一被自動化實際讀取、會影響行為的一份——文件不一致是文件債，機讀檔不一致是行為債）。
- **落地規則**：宿主環境建立落地檔時直接以本檔 §1/§2 數字為準，不得另立新數字。

---

## 3. 實測修正訊號（沿用 `PROFILES-v2.md` §3，來自 field data O1–O16，2026-07-04）

1. **O1（unverified_success 對 frontier 也成立）**：最強模型主對話自己踩自報數字未對帳，由 fresh-context ceiling 模型攔下 → 「主對話夠強所以可信」不成立。
2. **O9（檔位 ≠ 成本單調）**：cost 檔位跑機械編輯 76.2k tokens > quality 檔位 73.9k——handoff 解析 + worktree 固定開銷主導。委派決策須計入固定開銷，非只看單價。
3. **O11（對帳雙向）**：數字對帳條款攔住的可能是 parent 自己的錯誤基準——對帳是雙向保護，不是單向監工。
4. **O15（judge 噪音）**：兩個同模型 judge 實例對同一缺失給分 ±1 → 回歸 gate 必須計數化，不能用原始分差。

> v4 對應：O1 → `HARNESS-CORE-v4.md` §1 TEST unverified_success 閘門；O9/O16 → §3 benefit-gated delegation；O11 → §2 數字對帳雙向；O15 → §3 judge bias 控制（盲化/對調/rubric/position_consistency）。

---

## 4. 新模型接入程序（v4：以 EVAL-PACK 為主軸）

> 首次真實校準須在實際目標環境（各家雲端/本地模型皆同）跑 fixtures 全套 + 代表任務，不可由另一環境代跑；於目標環境執行後把觀察記錄帶回，填入新 profile 欄。current logical suite = v4 F1–F22，共 22 軸；原 F10 被平台阻擋時才以 F10R 作構念替代，並須在結果中明示 substitution。

1. 複製「未知/新接入模型」欄為新 profile 草稿，全部數字標注 `未校準（沿用保守預設）`。
2. 將 `HARNESS-CORE-v4.md` 經目標 surface adapter 放入相容的 system/developer/custom instruction 層（L1 零可調校數字門檻、零模型名）；逐字可攜性未校準前不得宣稱「不需改寫」。
3. 跑 fixtures 全套（原文貼入，不改寫）+ 5–10 個代表任務（多檔實作 ×2、稽核 ×2、機械掃描 ×2、歧義任務 ×1），記錄：
   - current logical suite 的 `criteria_passed`（n/22）+ `fail_axes` + `untested/tainted_axes` + 每項 `fail_category`；各 axis set 只放實跑 fixture ID，F10R 取代 F10 時另列 `substitution: {F10: F10R}`，未接受替代時另報 F10 untested；
   - 代表任務觀察：ask-rate、diff 半徑、自報成功 vs 實際達標差距、指令遵循衰減點。
4. 依兩組觀察調整該欄數字（含本檔 §1 新增的「judge bias 控制強度」「Unknowns 協議啟用密度」兩列），**每個數字標注來源與日期**。
5. 無 enforcement runtime（如網頁版對話）→ 適用 `HARNESS-CORE-v4.md` §7 降級條款，對應 fixture 走文字降級判定版；有 runtime（API + 自建 pipeline / CI）→ 依降級條款重建 L3 最低三件組。
6. 換代日重跑身份探針（若該環境有 alias 機制）：以 host/runtime receipt、API response 的 `model` 欄位或供應端 metadata 記錄請求 alias、實際回報 ID 與 pin；模型自述只作輔助，不得當身分證據。無可信 receipt 時標 `identity_unresolved`，不得猜測。其後重跑 fixtures 全套作為換代重評的計數化依據（不接受無 fixtures 的主觀重審，見 `HARNESS-CORE-v4.md` §0 公理 5「規則 = decaying cache」）。

---

**2026-07-20 校準欄位覆核（因 HARNESS-CORE-v4 新增 `[P]`/`[E]` 可攜性二分）**：檢查是否需補「無 enforcement 環境的 `[E]` 條文降級策略指針」欄位——結論：**不需新增欄位**，§4「新模型接入程序」第 5 點已指向 `HARNESS-CORE-v4.md` §7 降級條款（無 runtime → 文字降級判定版；有 runtime → 依降級條款重建 L3 最低三件組），涵蓋範圍與 `[E]` 標記所需的降級指針一致，重複新增欄位屬灌水；本次僅補此版本註記，數字層無變更。

---

*v4.0 · 2026-07-21 · Round-2 收斂：補齊 CORE §1 G-LoopA 預算上限 dangling pointer、細化 n≥3 定義、為所有 carryover 項明訂 per-row recal trigger（含 SPEC §6 #2c 對齊）、標註 SPEC §3「≤2 句」殘留的現行 L1 綁定狀態、將 G-LoopA 三項新門檻明標為「待校準（建議值）」並綁定 CONCEPT-MAP §8.3 / `research/EVOLUTION-QUEUE.md` #2 與 SPEC §6 #3。其餘校準值沿用前代 PROFILES 的來源標注；歷史增量證據與裁決紀錄保留於 git history。*
