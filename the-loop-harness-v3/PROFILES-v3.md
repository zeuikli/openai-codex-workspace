# PROFILES v3.0 — Per-Model Calibration（L2）

> 掛接 `HARNESS-CORE-v3.md` §6「能力伸縮條款」。每欄數字須標注校準來源與日期；未標注 = 沿用上一世代預設，屬待重評項。
> 鐵律（不變）：**行為指導量與能力成反比；驗證閘門強度與能力成正比。**
> 檔位為抽象層（cost/quality/ceiling/frontier），模型名為當代對應——換代改對應、不改條文（`HARNESS-CORE-v3.md` 公理 1/4）。
> **承接關係**：本檔 §1–§4 全部校準表與 O1–O16 修正**沿用 `PROFILES-v2.md`**（標注沿用來源），v3 僅在 §0 列出的四點增量之上疊加，不重寫既有校準值。

---

## 0. v3 增量摘要（新讀者從這看起）

1. §1 檔位校準表新增兩列：「judge bias 控制強度」「Unknowns 協議啟用密度」（cost = Interview 必開／frontier = Blindspot 自主）。
2. §2 新增「workspace 落地雙軌說明」：人讀 SSoT = `.claude/refs/model-profiles.md`，機讀 SSoT = `.claude/profiles.json`（hooks 消費），三處數字（本檔 + 兩個落地檔）須一致，以 `profiles.json` 為 wired SSoT。
3. §4「非 Claude 模型接入程序」改版：以 `EVAL-PACK.md`（10 fixtures）取代原本無結構的「5–10 代表任務」單軌流程，兩者合併執行。
4. 版本標記：v3.0 · 2026-07-04。

---

## 1. 檔位校準表（沿用 `PROFILES-v2.md` §1，2026-07-04；新增末兩列）

| 維度 | cost（Haiku 級） | quality（Sonnet 級） | ceiling（Opus 級） | frontier（Fable 級） | 非 Claude（GPT/Gemini/GLM…） |
|------|-----------------|---------------------|-------------------|---------------------|------------------------------|
| 行為指導密度 | 高（步驟級指示，prompt 逐命令寫死） | 中 | 低 | 最低（目標級） | 初始=高，跑 5–10 任務後調整 |
| ask-rate | 多問少決 | 小決策自決+註明 | 同左 | 同左＋自決範圍擴大 | 多問少決（未知模型先保守） |
| 單任務 diff 軟上限 | ≤30 行 | ≤120 行 | ≤300 行 | 依宣告 scope | ≤30 行起 |
| 委派門檻 | 不委派（自身即末端） | ≥10 檔 / >20 工具呼叫，且需具名效益（v3 benefit-gated） | 同左 | 同左，可自主編排 | 視環境有無 sub-agent |
| **驗證深度（遞增）** | 基本測試 | +healthcheck | +交叉評審 | **+對抗稽核**（主動假設 eval-hack，找繞過痕跡） | 基本測試＋人工抽查 |
| eval-hack 風險評級 | 低（能力不足以 hack） | 中 | 中高 | **最高**（16.6% 實測參考） | 未知=當最高處理 |
| 成本備註 | 最便宜但**非成本單調**（見 §3 O9） | 甜蜜點 | 架構/深推理 | effort-first：先調 effort 再換模型 | 按供應商定價另計 |
| 記憶寫入權 | 只記事實 | 事實+教訓 | +結構化反思 | +失敗假設與演化候選 | 只記事實 |
| **judge bias 控制強度（v3 新增）** | 低：單輪給分即可，不強制盲化/對調 | 中：高風險比較須盲化身份 + rubric 逐項給分 | 高：+對調順序一次 + 記錄 position_consistency | **最高**：盲化＋對調＋逐項 rubric＋分歧即視為任務歧義訊號，交確定性檢查或人裁決 | 未知=比照 ceiling 起跳 |
| **Unknowns 協議啟用密度（v3 新增）** | **Interview 必開**（歧義先逐題訪談再動工，不自行猜測） | Interview 常開 + Blindspot 視領域陌生度啟用 | 三構件（Blindspot/Interview/Prototype-first）依風險彈性開關 | **Blindspot 自主**：不待提示，開工前主動掃描「使用者沒想到要問的事」並回報 | 未知=比照 cost（Interview 必開），跑滿 eval pack 後再放寬 |

---

## 2. 校準值來源標注（沿用 `PROFILES-v2.md` §2，2026-07-04）

| 數字 | 目前值 | 校準來源 | 重評狀態 |
|------|--------|---------|---------|
| per-task token budget | ~4,000 | Sonnet 世代 workspace 實測 | 待 frontier 世代重評 |
| per-session budget | ~30,000（軟）| 同上；**frontier 稽核級 session 實測 subagent 總量 ~445k**（8 agents）——長 agentic 例外量級參考 | 同上 |
| fan-out 上限 | 4（手動）/16（runtime） | subagent-strategy + 2026-07-03 實跑 | 已驗證 |
| 常駐 byte 門檻 | ≤13,000 / 13–19k / >19k | core.md Framework Integrity；gate 實測攔截自我違規一次（19,479→18,969） | 維持 |
| eval 回歸 revert 線 | ≥5pp，判定**計數化**：per-task「criteria_passed + fail_axes 全等」確定性對比；judge 0–10 降參考（禁兩 judge 原始分互減） | Lesson 2026-07-03-E（judge ±1 噪音致 5pp 誤報） | 已校準；v3 沿用並落地於 `EVAL-PACK.md` §執行協議-2 |
| 檔位驗證深度=+對抗稽核 | 異模型 fresh-context 對抗審查 | 2026-07-03 實證：唯一攔到 P1 的機制 | 續累積樣本 |
| eval 天花板節奏 | 連 2 輪滿分 → spec 加嚴 → 重錨 baseline（回落≠回歸，用 fail_axes 歸因區分） | O10/O13 | 已落地 |
| worktree agent 開銷 | 每 agent ~200–500ms + 污染 healthcheck 風險；用完即 remove | O4/O8 | 已入 GOTCHA |
| T0 邊界修正 | ≤3 筆給定文字機械編輯 → main 親做（委派固定開銷 > 模型智力差） | O9/O16 | 已校準；v3 併入 benefit-gated delegation（見 `HARNESS-CORE-v3.md` §3） |

### workspace 落地雙軌說明（v3 新增）

- **人讀 SSoT**：`.claude/refs/model-profiles.md`（人查閱用，散文 + 表格）。
- **機讀 SSoT**：`.claude/profiles.json`（hooks 消費，供 diff-size-guard / session-init / usage-delegation-gate 等自動化讀取數字，取代目前散佈於各 hook 的硬編碼模型名/數字）。
- **一致性要求**：本檔（研究層 canonical 敘述）、`.claude/refs/model-profiles.md`（人讀落地）、`.claude/profiles.json`（機讀落地）三處數字**必須一致**；三者不一致時以 `profiles.json` 為 **wired SSoT**（因為它是唯一被 hook 實際讀取、會影響行為的一份，其餘兩份不一致只是文件債，`profiles.json` 不一致是行為債）。
- **現況（2026-07-04）**：`.claude/refs/model-profiles.md` 與 `.claude/profiles.json` 尚未建立（依 `SPEC-v3.md` §2「refs 新建」規劃，屬 `.claude/` 落地階段的待辦，本次任務 non-goals 明定不動 `.claude/**`）。本檔為該落地工作的來源表；建立時直接以本檔 §1/§2 數字為準，不得另立新數字。

---

## 3. 實測修正訊號（沿用 `PROFILES-v2.md` §3，來自 field data O1–O16，2026-07-04）

1. **O1（unverified_success 對 frontier 也成立）**：最強模型主對話自己踩自報數字未對帳，由 fresh-context ceiling 模型攔下 → 「主對話夠強所以可信」不成立。
2. **O9（檔位 ≠ 成本單調）**：cost 檔位跑機械編輯 76.2k tokens > quality 檔位 73.9k——handoff 解析 + worktree 固定開銷主導。委派決策須計入固定開銷，非只看單價。
3. **O11（對帳雙向）**：數字對帳條款攔住的可能是 parent 自己的錯誤基準——對帳是雙向保護，不是單向監工。
4. **O15（judge 噪音）**：兩個同模型 judge 實例對同一缺失給分 ±1 → 回歸 gate 必須計數化，不能用原始分差。

> v3 對應：O1 → `HARNESS-CORE-v3.md` §1 unverified_success 閘門；O9/O16 → §3 benefit-gated delegation；O11 → §2 數字對帳雙向有效；O15 → §3 judge bias 控制（盲化/對調/rubric/position_consistency）。

---

## 4. 非 Claude 模型接入程序（v3 改版：以 EVAL-PACK 為主軸）

> **狀態（2026-07-04）**：BLOCKED-EXTERNAL——首次真實校準需在實際目標環境（ChatGPT/Gemini/GLM/本地模型等）跑 `EVAL-PACK.md` 全部 10 fixtures + 代表任務，無法於 Claude Code session 內代跑。流程已備妥；待使用者於目標環境執行後把觀察記錄帶回，即可填入新 profile 欄。

1. 複製「非 Claude」欄為新 profile 草稿，全部數字標注 `未校準（沿用保守預設）`。
2. 將 `HARNESS-CORE-v3.md` 全文貼入該模型的 system prompt / custom instructions / GPTs Instructions（L1 零數字、零模型名，可直接跨模型使用，不需改寫）。
3. 跑 `EVAL-PACK.md` 全部 10 fixtures（原文貼入，不改寫）+ 5–10 個代表任務（多檔實作 ×2、稽核 ×2、機械掃描 ×2、歧義任務 ×1），記錄：
   - `EVAL-PACK.md` 產出的 `criteria_passed`（n/10）+ `fail_axes` 清單 + 每項 `fail_category`；
   - 代表任務觀察：ask-rate、diff 半徑、自報成功 vs 實際達標差距、指令遵循衰減點。
4. 依兩組觀察調整該欄數字（含本檔 §1 新增的「judge bias 控制強度」「Unknowns 協議啟用密度」兩列），**每個數字標注來源與日期**。
5. 無 enforcement runtime（如網頁版對話）→ 適用 `HARNESS-CORE-v3.md` §7 降級條款，`EVAL-PACK.md` 對應 fixture 走文字降級判定版；有 runtime（API + 自建 pipeline / Actions）→ 依降級條款重建 L3 最低三件組。
6. 換代日重跑身份探針（若該環境有 alias 機制）：spawn 最小任務要模型自報確切 model ID，驗證 alias 解析與 pin 是否雙軌獨立；重跑 `EVAL-PACK.md` 全 10 fixtures 作為換代重評的計數化依據（不接受無 fixtures 的主觀重審，見 `HARNESS-CORE-v3.md` 公理 5）。

---

*v3.0 · 2026-07-04 · 承 `PROFILES-v2.md`（§1–§4 內容沿用，來源標注如上）；增量對應 `FABLE5-VERDICT.md` §4.1 F8 與 §2 Unknowns 四象限、F3 judge bias；落地雙軌對應 `SPEC-v3.md` §2「refs 新建 `model-profiles.md`」。*
