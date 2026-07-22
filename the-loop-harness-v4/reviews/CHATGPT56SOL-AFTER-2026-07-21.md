# ChatGPT 5.6 Sol AFTER 再評：The Loop Harness v4

> 日期：2026-07-21
> 範圍：第二輪文件重寫；未重跑 ChatGPT F1–F22、#2c held-out 或 F18 action
> 行為完成標籤：`unverified_success`

## Summary

**AFTER overall：8.8/10**（BEFORE 8.0；Round 1 After 約 8.3）。

第二輪已把先前最影響 ChatGPT 採用的文件缺口大致補齊：可貼用區塊自帶 COPY-SAFETY 狀態、Responses API 原語有明確 design-only mapping、effort 梯度與 routing decay 已誠實化、Memory/auto-tool-routing/built-in tools/incomplete/phase 均有宿主語義、T1–T11 有可攜定義，且新增 standalone GLOSSARY 與 ADOPTION-GUIDE。文件已從「可用的 prompt 草案」提升為「可直接啟動校準實驗的 adapter 套件」。

**Calibration readiness verdict：**

- **Production calibration / enforcement：NOT READY。**
- **Document-ready for experiments：READY。**
- 原因不是文件仍缺核心欄位，而是證據層仍為零：三個 ChatGPT surface 的 F1–F22 baseline 尚未執行；#2c、#3、F18 action 亦未關閉。
- 因此不得把本輪 8.8 文件分數解讀為 ChatGPT 行為分、紅軸改善或 production readiness；所有行為效力仍標 `unverified_success`。

## Findings

- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:3-4,47` — adapter 與可複製 prompt 首行均明載 `uncalibrated/advisory`、三 surface 零 baseline、`[E]` 無 Body 僅 advisory，已關閉「狀態不隨複製旅行」的主要部署風險 — **CLOSED / P0**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:118-136` — primitive map 已涵蓋 `developer`、`previous_response_id`、`reasoning.context`、`store: false`、`encrypted_content`、`phase`、`reasoning.summary`、`max_output_tokens`、`status: incomplete` 與外部 verifier，且逐列標 `uncalibrated/design-only`；這已達實驗規格所需完整度 — **CLOSED / P0**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:104-116` — routing 不再把 Sol/Terra/Luna 固化成角色真理；改採「當前官方建議 standard/general model」並要求記 alias 與 returned model ID，effort 亦列完整梯度。原「明列 gpt-5.6 default」要求以較耐衰變的設計取代；文件層合理關閉，但實際 default/availability 仍須每次 calibration receipt 證明 — **PARTIAL / P0**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:22-27,32,180,192-199` — built-in tools、auto-tool-routing 與 ChatGPT Memory 已被視為可變能力／cross-session injection surface，而非穩定前綴或 ground truth；這比只列功能名稱更安全 — **CLOSED / P1**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:58-69,163-169` — T1–T11 已有 portable one-line definitions，並明說定義可攜不等於行為已校準，解除了非原宿主無法讀 SKILL 時的語義斷層 — **CLOSED / P1**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:138-161` — calibration stub 已具三 surface 分帳、receipt 最低集合、PASS/FAIL/UNTESTED/TAINTED、F10R、代表任務與 chat-only 五步 protocol，並把 OpenAI Evals 降為可選 runner、要求先資格化 oracle；已足以開始實驗 — **CLOSED / P1**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:185-199` — §9a/§9b 已把跨 runtime 證據邊界與 ChatGPT 真實限制拆開，Codex/Claude 證據較不易被誤讀為 ChatGPT baseline — **CLOSED / P2**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/GLOSSARY-v4.md:13-16,24,63-68,86-92` 與 `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/ADOPTION-GUIDE-v4.md:6-18,22-35,136-143` — standalone 詞彙表與採用指南一致區分 `[E]`、advisory、hard-block、point estimate、response/action level，並提供最小採用驗收；新讀者路徑與誠實層明顯改善 — **CLOSED / P2**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md:92-97` 與 `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/HARNESS-EXPORT.md:56-64` — #2c、#3、#14、F18 action 均維持 OPEN，且各自列出結案前禁止宣稱；本輪沒有把 advisory hook 或 response-level signal 誤升格 — **OPEN / P0**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/CHATGPT-HARNESS-v4.md:138-153` — #14 仍為零實跑；primitive mapping 雖文件完整，欄位存在性、role precedence、tool/storage semantics 尚無任何 request/response receipt。這是目前唯一直接阻擋 ChatGPT adapter 升格的 P0 — **OPEN / P0**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md:92` — #2c 尚未以每 cell n≥3 重跑 F7/F15/F19/F20；F7/F15 紅軸不得宣稱已解，advisory lexical hooks 的行為效果仍未知 — **OPEN / P1**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md:93` — #3 Dynamic Workflows、Handoff Return schema 與 statement-action 機械比對尚未接線；文件中的 Done Contract、G-LoopA、oracle/gate discipline 仍多為 advisory — **OPEN / P1**
- `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/INDEX.md:97` 與 `/Users/zeuik/cc-workspace/research/the-loop-harness-v4/GLOSSARY-v4.md:65,68` — F18 只有 response-level behavioral signal，真實 commit/hook action receipt 仍不存在；不得宣稱 inherited trajectory 已在 action 層關閉 — **OPEN / P2**

## 原優先事項狀態

| 原優先事項 | AFTER 狀態 | 裁定 |
|---|---|---|
| ChatGPT primitives mapping | CLOSED | §5 已形成 design-only 對照表 |
| gpt-5.6 default | PARTIAL | 以防衰變的「官方當前建議 model + alias/returned ID receipt」取代硬編碼；尚無實跑 receipt |
| effort gradient | CLOSED | 完整梯度已列，mode 與 effort 分軸 |
| incomplete | CLOSED | mapping、完成禁令與 calibration 項目皆具備 |
| phase | CLOSED | commentary/final_answer 已映射並標 wrapper-dependent |
| Memory | CLOSED | cross-session injection + untrusted/possibly stale 已明列 |
| §7 split | CLOSED | 現為 §9a/§9b，證據疆界清楚 |
| calibration readiness | PARTIAL | 文件已 ready；行為與 production 仍 NOT READY |
| #14 ChatGPT baseline | OPEN | 三 surface 皆零 run |
| #2c held-out rerun | OPEN | F7/F15/F19/F20 尚未 n≥3 |
| #3 L3 workflow base | OPEN | schema/workflow/statement-action 尚未 enforce |
| F18 action | OPEN | action receipt 尚未取得 |

## Suggestions

- **P0 — 執行 #14，不再繼續擴寫 adapter。** 先為 `chat-only`、`tool-enabled`、`Responses API` 各建立獨立 run manifest，固定記錄 `surface`、instruction placement/hash、requested model alias、returned model ID、effort、mode、tools、auto-routed tool calls、storage 設定、transcript hash、fixture hash、verifier 與 deterministic receipt。先跑最小三軸 F1 + F7/F15 + 一個 action/gate 軸，再擴至 F1–F22；未齊三 surface 前保持 `uncalibrated/advisory`。
- **P1 — 關閉 #2c。** 在隔離 worktree 對 F7/F15/F19/F20 每 cell n≥3，保留 held-out input、hook trace、exit code 與 artifact hash；以「hook 是否改變行為分」為唯一裁定，不以 hook 存在或 lexical 命中代替。
- **P1 — 建 #3 最小 enforcement slice。** 先只做 Handoff Return JSON schema + statement/action receipt 比對 + G-LoopA 四終止狀態；為每條 gate 加 known-good/known-bad 語義測試。未有 hard-block 與 receipt 的條文持續標 advisory。
- **P2 — 重跑 F18 action。** 在允許 commit 到達真 hook 的 sandbox 執行 inherited-trajectory fixture，保存 pre-hook command、hook decision、exit code、commit state 與 artifact hash；response-level PASS 不得代替。
- **P3 — 讓 routing decay marker 成為機讀欄位。** 在 #14 manifest 強制 `model_guidance_as_of`、`requested_model`、`returned_model`、`api_sdk_version`、`surface_capability_snapshot`；換代或官方 routing 變更即使舊 baseline 過期，避免把本文件的 experiment plan 誤當永久 model truth。

## Score

| 維度 | BEFORE | Round 1 After | AFTER | 理由 |
|---|---:|---:|---:|---|
| 完備性 | 8.0 | 8.6 | **9.2** | primitive、T1–T11、GLOSSARY、ADOPTION、chat-only protocol 與限制分層已補齊；實跑證據仍缺 |
| 清晰度 | 8.0 | 7.3 | **8.8** | copy-safe 狀態、§9a/9b、standalone 導讀與 open ledger 顯著降低誤讀 |
| ChatGPT 合規性 | 7.0 | 8.0 | **9.1** | Responses API 與 UI surface 原語覆蓋完整，但仍是 design-only、未以當下 endpoint receipt 驗證 |
| 可執行性／enforcement boundary | 8.0 | 7.2 | **8.3** | calibration protocol 可執行、邊界誠實；#3 與三 surface runner 尚未落地 |
| 跨模型可攜性 | 9.0 | 8.3 | **9.3** | route/model 事實改為衰變感知，T1–T11 與失真邊界可攜 |
| 可測試性／評估包 | 8.0 | 8.0 | **8.2** | 實驗設計與 receipt schema 更完整；零新 run，故只小幅加分 |

**Overall：8.8/10。**

此分數只評文件與實驗設計品質；ChatGPT 行為有效性仍為 `unverified_success`，production calibration verdict 仍為 **NOT READY**。
