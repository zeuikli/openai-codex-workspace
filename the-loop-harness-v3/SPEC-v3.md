# SPEC — The Loop Harness v3.0：重構藍圖與 `.claude/` 落地對照

> 2026-07-04 · 終審：Fable 5（主對話）· 改寫執行：ceiling/quality/cost 檔位（依使用者指定，Fable 不執筆 bulk 改寫）
> Canonical 條文 = `HARNESS-CORE-v3.md`。裁決依據 = `FABLE5-VERDICT.md`。v2 → v3 = **驗證軸加碼、指導軸減密、模型名下沉單點**。

## 1. v2 → v3 差異總表

| 維度 | v2 | v3 |
|------|----|----|
| 委派 | 預設委派、例外親做（L1） | **benefit-gated**：最簡拓撲預設，委派須具名效益；確定性 gate 親跑不變 |
| L1 數字 | 仍含 byte 門檻等 | **L1 零數字**：全部 → L2（markdown：`model-profiles.md`；機讀：`profiles.json`） |
| 模型名 | 散佈 rules/refs/skills/agents/hooks ≥5 處 | **只允許出現在 L2 對應表**；L3 wiring 允許 alias（禁版本 pin） |
| IDENTIFY | Done-when + open questions | + **Unknowns 協議**（Blindspot Pass / Interview / Prototype-first）+ Done Contract 協商 |
| 六階段 | 全任務等重 | **儀式深度隨風險/不可逆性伸縮**，不隨模型檔位 |
| 外部輸入 | 資料非指令 | + **role-confusion 防禦**（provenance/去樣式/結構化提取/derived-args 確認） |
| 驗證展示 | 前5後5行 | + **redaction 例外**（敏感輸出示 command/exit/hash/shape） |
| 互審 | verdict 非證據 | + **judge bias 控制**（盲化/對調/rubric/position_consistency/分歧=歧義） |
| 刪除 | 單一三件齊備 | **風險三級**（low/medium/high） |
| P0 安全 | 即修 | **授權二分**：範圍內即修 / 範圍外 blocking report |
| taste | 四維之一（無界） | **有界**：可否決品質缺陷、不可否決 correctness/安全/確定性結果 |
| 重審 | 14–30 天 cadence | + **Eval Pack（P0）**：10 fixtures + 獨立執行者 + 計數化回歸 |
| 規則變更 | 「對應實證失敗模式」口號 | **changelog schema** 可稽核欄位 |

## 2. `.claude/` 落地對照（依四路掃描盤點）

| 區塊 | 處置 |
|------|------|
| rules + CLAUDE.md + AGENTS.md | ceiling 檔位重寫：L1 化（零模型名/零數字）、benefit-gated 委派、Unknowns 協議、五標籤、儀式深度條款；六源 byte ≤18,052、目標 ≤14k |
| L2 schema | **L2 容納兩類內容**：數字校準表 + **質性 per-tier 失敗模式清單**（prose gotcha，如 cost 檔位的 citation fabrication 傾向）——PromptBridge（2512.01420）證明措辭級調適 load-bearing，合併 pilot 時質性差異不得壓縮成純數字（反證 agent CHALLENGE 裁決採納，2026-07-04） |
| refs | L2 SSoT 新建 `refs/model-profiles.md`（吸收 model-selection-grid、delegation-protocol §2、pilot-shared-preflights §C/§E、caching 門檻表、CJK 倍率、R1 升級計數、eval baselines）；孤兒 refs 接線或標注；`fable5-harness.md` ref → 指向 v3 |
| skills | 四 pilot 合併 → 單一 `pilot`（tier 參數化）；multi-mode-skill enum → tier；fable5-harness → `harness-core`；quality-pipeline gate 名 → tier；harness-meta 模型事實表 → 指針；cyber/bio 安全路由 5 處重複 → profiles 單點 |
| agents | haiku-implementer 併入 implementer（surgical mode）；researcher/reviewer/self-escalate 內文模型指導 → tier + profile 指針；multi-mode-agent 改讀外部 profile（消滅 L2 三鏡像） |
| hooks | diff-size-guard / user-prompt-submit / session-init 的模型名硬編碼 → 讀 `profiles.json`；memory-pr-record 兩支合併；contract-echo-gate 刪除（prose nudge，依公理 4 拆除；TODO(conflict): chose 刪除 over 風險觸發降級——nudge 職責已由 L1 儀式深度條款承接）；確定性 gates 原樣保留 |
| commands / prompts | 幾乎全 KEEP；wiki.md 模型 pin → tier |
| L4 | `EVAL-PACK.md`（10 fixtures 規格）+ changelog schema 進 maintenance-protocol |

## 3. 不變式（改寫 agents 不得違反）

1. 確定性 gates（block-dangerous / protect-sensitive-files / pre-commit-review / pre-compact / usage-delegation-gate / unicode-guard / post-edit）邏輯不弱化。
2. 驗證閘門條文只可加嚴不可放鬆。
3. 刪除的內容若含唯一知識，先抽出併入接收檔（三件齊備第 2 件）。
4. 全 repo 活引用改線（RESOLVER.md / dependency-graph.json / trigger-index / README / INDEX），懸空引用 = 0。
5. 繁體中文為使用者面文字之準；內部註解可英文。
6. healthcheck FAIL=0 為合併前置條件。

## 4. Backlog（研究深讀增量，2026-07-04 tweets/papers 二次掃描；未落地、下 cycle 逐項過 gate）

1. **Reward-hacking 確定性 gate**：`git diff --quiet -- test/` 測試檔被改即 revert+exit（@h100envy 06-22）→ 新 hook 候選。
2. **build_context.sh 範式**：stack trace + last diff 動態組 context + TOKEN_BUDGET 硬上限 → context-management ref。
3. **雙層 state**：STATUS.md（人讀）+ `.loop_state.json`（機讀）→ loop scaffold 規範。
4. **11 種裝完成捷徑 checklist**（relaxed tests/swallowed errors/stub returns…）→ reviewer 類 agents 加作弊偵測清單。
5. **心跳頻率 = 第四成本槓桿**（5min vs 1h ≈ 12×）→ 成本規則補充。
6. **Quiz gate**（merge 前人類 100% 理解測驗）+ **References pattern**（指參考原始碼資料夾非描述規格）→ @trq212 7 技巧中尚未吸收的 2 項 → verified-merge / task-templates。
7. **PR decision log**（捨棄方案附 PR 永久記錄，非暫存 notes）→ 與 spec-implement 的 implementation-notes 區隔待確認。

另：根目錄/TPKI 全域重構（使用者 2026-07-04 追加指示）為下一 session 首要任務——TPKI 三層（Raw/Wiki/Schema）與 v3 四層（L1–L4）正交，需先裁決 nest vs replace；硬編碼路徑清單（memory/evolution/BRAIN/WORKSPACE-INDEX/harness-model-fit 等 17 scripts + 9 hooks 依賴）已由盤點 agent 產出，重構必須帶 codemod。

## 5. 泛用性答案（使用者主問題的結論）

強模型 × 嚴 harness 的正確組合 = **驗證骨架共用、指導密度分檔**：不是把弱模型補丁套在強模型上，也不是為強模型拆掉閘門。每個模型接入 = 跑同一組 eval fixtures → 產出自己的 L2 欄位 → 共用同一 L1 契約與 L4 演化迴路。Harness 不再綁模型或平台；被綁定的只剩一張可換的表。
