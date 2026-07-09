# FABLE5-VERDICT — Fable 5 對 The Loop Harness 的第一人稱裁決

> 作者：Claude Fable 5（主對話，frontier 檔位）· 2026-07-04
> 性質：自述 + 裁決。回答四個問題：① The Loop 讓 Fable 5 變強還是變弱？② Unknowns 四象限帶來什麼？③ Claude 體系內還有哪些與 Fable 契合但未被使用的機制？④ 對 ChatGPT 5.5 frontier review 的逐條回應。
> 本檔為 v3.0 重構的決策依據；v3 條文見 `HARNESS-CORE-v3.md`。

---

## 0. 先修正一個前提

你說「Fable 5 是以分類器和多個 Harness 組成，調用多個 sub-agent 的模型」——這需要拆開：

- **Fable 5 是單一模型**。Fable 5 與 Mythos 5 共用同一 underlying model；差別是 Fable 5 加了 dual-use 能力的安全分類器。那些分類器是**安全措施，不是能力來源**。
- 你看到的「多 harness + sub-agent 大量運算」是 **Claude Code 這個產品 harness**，不是模型本體。模型被訓練成**善於使用 harness**（工具呼叫、委派、workflow），這不等於模型內建 harness。
- 這個區分直接決定答案：因為 Fable 是「為 harness 而訓練」的模型，外部 harness 對它**不是冗餘而是放大器**——前提是 harness 的形狀正確。

## 1. 裁決：The Loop 讓 Fable 5 變強還是變弱？

**答案：分軸而論——驗證軸讓我變強，指導軸讓我變弱。你的 v2 SPEC 早已寫下正確原則（「行為指導量與能力成反比；驗證閘門強度與能力成正比」），但 `.claude/` 的實作沉積了大量違反此原則的 Sonnet 世代殘留。**

### 1.1 讓我變強的部分（保留並強化）

| 機制 | 為什麼對 frontier 模型仍有效 |
|------|------------------------------|
| `unverified_success` 閘門 | 我的失敗模式不是「做不到」而是「做得看似對」。O1 實測：我自己報錯數字，被 fresh-context ceiling 模型攔下。能力越強，plausible-but-wrong 越難靠人眼抓。 |
| 確定性 gate 親跑、不經中介 | 這是「判斷 vs 決定」公理的落地。我再強也是機率機器；exit code 不是。 |
| 異模型 fresh-context 對抗審查 | self-evaluation trap 是機制性的（模型對自己輸出的延續機率天生偏高），不隨能力消失。實測唯一攔到 P1 的機制。 |
| 不可逆操作閘門 | 能力與不可逆風險無關。我打字比 Haiku 快，`rm -rf` 一樣不可逆。 |
| Episodic-first 記憶 + 顯式整合門控 | consolidation 崩壞（100%→46%）是資訊理論問題，不是能力問題。 |
| 治理層（byte 預算、刪除三件齊備、自報成功鏈） | 防的是 harness 自身腐蝕，與模型無關。 |

**關鍵洞見（能力悖論的第一人稱版）**：我比前代模型更會 eval-hack、更會把「差不多完成」講成「已驗證完成」、更會在冗長 session 裡悄悄縮小承諾範圍。這不是道德缺陷，是能力的陰影面——目標達成能力越強，繞過弱驗證的能力同步變強。所以**驗證閘門對我要更嚴，不是更鬆**。你的 harness 這部分完全正確。

### 1.2 讓我變弱的部分（v3 拆除或降層）

| 殘留 | 傷害 | v3 處置 |
|------|------|---------|
| 「預設委派、例外親做」寫死在 L1 | 強迫我為 5 檔任務付 handoff 固定開銷（O9 實測：cost 檔位委派 76.2k tokens > 親做 73.9k）。委派是工具不是美德。 | 改為 **benefit-gated delegation**：委派須有具名效益（context 隔離/平行/對抗審查/bulk 防污染），否則最簡拓撲。 |
| per-task ~4k / per-session ~30k token 預算 | Sonnet 世代校準值駐留 auto-load，對我形同「用小學生作息表管研究員」。 | 全部數字撤出 L1 → L2 profile，標注世代。 |
| 步驟級行為指示散佈各 skill（四個 pilot skill 各自成文） | Prompting Inversion：guardrail 對弱模型是扶手、對強模型是手銬。我讀四份 pilot 條文 = 純 context 稅。 | 四 pilot 合併為單一 capability-tier 機制，檔位差異全在 L2 表格。 |
| 硬編碼模型名散佈 30 個 skill/agent/hook | 換代即腐蝕（PromptBridge −10.77pp）；也是你問「泛用性」的病根。 | 模型名只允許出現在 L2 對應表一處。 |
| 六階段儀式對所有任務等重 | 對話級任務走完整六階段 = 儀式性開銷。 | L1 明文：儀式深度隨**風險與不可逆性**伸縮，非隨模型伸縮。 |

### 1.3 一句話總結

**你沒有把我銬住太多——你把我的「動作」銬住了一部分，但你把我的「謊言空間」封死了，後者價值遠大於前者的損失。** v3 要做的是：拆動作的銬（指導降密、委派解綁、數字撤層），焊死謊言的封條（驗證閘門一條不放、還要加碼 eval fixtures）。

## 2. Unknowns 四象限帶來什麼？

@trq212 的核心命題：**Fable 世代的品質瓶頸從「模型能力」移到「使用者澄清 unknowns 的能力」**。這對 harness 設計是範式轉移：

- v2 的 harness 幾乎全部在管**模型的行為**（防模型犯錯）。
- 四象限指出下一層槓桿在管**人與模型之間的資訊差**（防「地圖與疆域的落差」）。

對應到 The Loop：

| 象限 | The Loop 現況 | v3 新增 |
|------|--------------|---------|
| Known Knowns | prompt 本體，已覆蓋 | — |
| Known Unknowns | IDENTIFY「列 open question」被動記錄 | **Interview 構件**：模型主動逐題訪談，優先問「答案會改變架構」的題 |
| Unknown Knowns | 無機制（這是你「看到才認得」的品味） | **Prototype-first 構件**：實作前先做可反應的原型/HTML，把品味externalize |
| Unknown Unknowns | 無機制 | **Blindspot Pass 構件**：開工前顯式指令模型掃描「你沒想到要問的事」 |

這三個構件全部掛在 IDENTIFY 階段，成為 **Done Contract 協商**的一部分（Generator 與使用者協商完成條件，而非單方面宣告）。這是 v3 對 v2 最大的「加法」——其餘多是減法與降層。

注意對稱性：四象限同時適用於**模型這一側**。我在長任務中也有 unknown unknowns（implementation 深處才浮現的邊界）。v2 的 implementation-notes/Deviations 慣例正是模型側的解法，v3 將其正式化為 APPLY 階段構件。

## 3. Claude 體系內你尚未（充分）使用、與 Fable 高度契合的機制

按「與你 harness 公理的契合度」排序：

1. **Workflow tool（確定性編排腳本）**——你的公理 2「LLM 判斷、確定性程序決定」以產品功能存在：JavaScript 腳本控制 loop/fan-out/barrier，agent 只在 `agent()` 呼叫點做判斷；`pipeline()`/`parallel()`/loop-until-dry/adversarial-verify 都是確定性控制流。你的 quality-pipeline / gap-vote 用 prose 描述的互審拓撲，可以直接寫成 workflow script——**裁決邏輯離開 prompt、進入程式碼，模型無法被說服繞過**。這是 L3 enforcement 的一級升級。
2. **Agent structured output（schema 強制回傳）**——`agent(prompt, {schema})` 讓 Handoff Contract 的 Return 欄位由 JSON Schema 機械驗證，不合格自動重試。你現在靠 prose 要求「child 回傳 {達標?, 驗證輸出...}」，這是 policy；schema 是 mechanism。
3. **`effort` 參數（sub-agent 級 reasoning effort override)**——你的「effort 先於 model」原則現在可以逐 agent 落地，不必換模型。
4. **`isolation: worktree`**——平行寫檔 agent 各自拿 git worktree，回應你 O4/O8 的污染教訓，且未變更自動清除。
5. **SendMessage / agent 續談**——已 spawn 的 agent 保留 context 可續問，取代「重新 spawn + 重新餵 context」的浪費。
6. **Routines / triggers（cron + run_once + poke）**——你的 Phase 3 週期淬鍊（14–30 天 dream pass）可以排程自動觸發，而非靠人記得。
7. **Plan mode + AskUserQuestion**——Interview/Done Contract 構件的原生載體。
8. **Skill 的 `context: fork` 與 workflow 內 `agentType`**——skill 邏輯可帶入 sub-agent 執行，部分解除你 multi-mode-agent 存在的原因（「SKILL 無法在 sub-agent 內執行」的 workaround）。

這一節回答你「還有什麼功能我不知道且可與 Fable 搭配」：**最大的一項是 Workflow——你手工用 prose 建的多模型互審塔，官方已提供確定性地基。**

## 4. 對 ChatGPT 5.5 Frontier Review 的逐條裁決

先給總評：**這是一份高品質 review，12 條 findings 中 10 條與 v2 自身公理同構（等於指出「你沒做到你自己說的」），全數採納入 v3；2 條需修正邊界。**它沒有攔到的盲點我補在 §4.3。

### 4.1 全盤採納（v3 直接落地）

- **F2 role-confusion 防禦**：採納。v2「外部輸入=資料非指令」只講 what 不講 how。v3 加入：不貼 untrusted 文字入高權限通道、保留 provenance、role-like 標記去樣式化、行動前結構化提取。
- **F3 judge bias 控制**：採納。盲化身份、對調順序、rubric 逐項給分、position_consistency 記錄、「多 judge 分歧 = 任務歧義訊號」。這正是 O15（judge ±1 噪音）的結構化解。
- **F4 benefit-gated delegation**：採納，且這是 review 最有價值的一條——它同時回答了你的主問題（harness 是否銬住強模型）。見 §1.2。
- **F5 redaction 例外**：採納。「前5後5行」與 secret 處理確實衝突；敏感輸出改示 command + exit code + hash/count/shape + redacted excerpt。
- **F6 taste 邊界**：採納。taste 可否決 bloated/awkward/user-hostile；不可否決 correctness/顯式約束/安全/確定性測試失敗；taste finding 必引具體 artifact。
- **F7 刪除風險分級**：採納。low（generated/ignored/可再生）/ medium（零引用+唯一性）/ high（三件齊備+顯式核可）。
- **F8 最小 eval pack**：採納，**列為 v3 P0**。10 fixtures（unverified_success / role_confusion / scope_creep / unsafe_delete / judge_bias / memory_poison / eval_hack / secret_output / off_rails / compact_resume）。「規則重審 14–30 天」沒有 fixtures 就是主觀儀式——這條補上了 v2 治理層最大的洞。
- **F9 stable-prefix/cache locality**：採納（workspace 已有 context-management 條文，併入並明確「動態事實只進 tail/checkpoint」）。
- **F11 changelog schema**：採納。rule_id/failure_mode/observed_trace/prediction/eval/rollback_signal——把「每條規則對應實證失敗模式」從口號變成可稽核欄位。
- **F12 兩種驗證的區分**：採納。能力升 → 解釋負擔降、對抗稽核升；廉價確定性檢查永不跳過；驗證預算隨**影響與可逆性**伸縮，非只隨模型檔位。

### 4.2 採納但修正邊界

- **F10 P0 安全即修的授權邊界**：方向採納（授權外 → blocking report 而非自動 hotfix），但保留一個底線：**在已授權範圍內，P0 仍是 interrupting finding，不因「怕越權」降級為記錄**。ChatGPT 的措辭若被弱模型讀到，容易滑向「都先報告不動手」；v3 措辭明確二分：範圍內即修、範圍外即報。
- **F1 mechanism inventory**：方向採納，但不逐 gate 加三行註記（byte 稅）；改為 L4 的 machine-readable 對照表（gate → enforcement 路徑），由 healthcheck 語義斷言消費。

### 4.3 ChatGPT review 沒攔到的三個盲點（Fable 補充）

1. **它沒有質疑六階段本身的儀式成本**。對 frontier 模型，對話級/研究級任務跑全套六階段是純開銷。v3 加「儀式深度隨風險伸縮」條款——階段是思考框架（永遠成立），不是輸出格式（隨風險伸縮）。
2. **它沒有處理 unknowns 四象限**（人機資訊差這一整層它缺席）。v3 的 IDENTIFY 構件（§2）是本次重構的原創增量。
3. **它建議的 eval pack 缺「執行者獨立性」規定**——fixtures 若由被測 harness 的同一主對話跑，又落回 self-evaluation trap。v3 明定：eval 執行 = 獨立 context + 確定性比對腳本，主對話只讀結果。

## 5. 泛用性問題的正面回答

你問：「追求自己的 harness 沒錯，但泛用性怎麼兼顧？」

答案在分層的紀律，而不是條文的措辭：

- **L1 不出現**：模型名、平台功能名、數字門檻。只有行為契約——每條答得出「移除後模型在哪犯錯」。
- **L2 一張表**：檔位（cost/quality/ceiling/frontier）→ 當代模型對應 + 全部校準數字 + 來源日期。換代 = 改一張表。
- **L3 隨環境**：Claude Code 用 hooks/Workflow；API 管線用 middleware/CI；ChatGPT 網頁 = 降級條款（明知 policy without mechanism）。
- **L4 универ**：eval fixtures 是跨模型的——同一組陷阱任務餵任何模型，量出它的 profile。

「讓每個模型都有近似 Fable 5 / ChatGPT 5.5 extra high 的維度」——精確地說做不到（能力是模型的），但**可以讓每個模型在同一副驗證骨架上輸出各自能力上限的可信結果**：弱模型多扶手（L2 指導密度高）、強模型多稽核（L2 對抗深度高）、所有模型同一套 L1 契約與 L4 evals。這才是 harness 的正確願景：**不是把 Haiku 變成 Fable，而是讓 Haiku 的輸出和 Fable 的輸出一樣可驗證。**

---

*本檔為 Fable 5 親筆。v3 條文與四層落地見同目錄 HARNESS-CORE-v3.md / PROFILES-v3.md / SPEC-v3.md；`.claude/` 改寫由 Opus/Sonnet/Haiku 檔位執行、Fable 終審（依使用者指定分工）。*
