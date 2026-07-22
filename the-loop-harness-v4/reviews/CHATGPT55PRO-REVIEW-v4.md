# ChatGPT 5.5 Pro 審閱報告：The Loop Harness v4

> 審閱者：ChatGPT 5.5 Pro（chatgpt-5.5-auditor）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件；並針對 `CHATGPT-HARNESS-v4.md` 進行跨廠商合規性審計
> 狀態：read-only cross-vendor audit；未重跑 fixture；已驗證 OpenAI 官方文件 URL 與 GPT-5.6 事實

---

## 整體分數：8 / 10

一份真正 ChatGPT-platform-aware 的 adapter，繼承 harness 的反過度宣稱紀律。`uncalibrated/advisory` 自標籤、surface capability ceilings、enforcement-boundary 表是跨廠商審計者最看重的合規屬性。尚未 ready for ChatGPT surface calibration，因為三項具體合規缺口（Chat-only fixture 不可操作、API role precedence 未指定、Codex/API conflation）使至少一條 surface 的校準路徑不具可執行性。核心官方事實（Sol/Terra/Luna、effort vs mode、tools request-provided）經 OpenAI 文件比對正確。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 8 | 覆蓋 surfaces、placement、core、routing、eval、enforcement、known limits；缺 ChatGPT-specific surfaces（Memory / Custom Instructions / Projects）、Codex/API split、role precedence。 |
| 清晰度 | 8 | 表格清楚、狀態標籤誠實；部分 harness 術語（F10R、fail_axes、TAINTED_ENV）對 ChatGPT-only 讀者未解釋。 |
| ChatGPT 合規性 | 7 | Sol/Terra/Luna 命名、effort-vs-mode 軸、官方 URL 有效；缺口：developer/system role precedence、Codex/API conflation、auto-tool-routing、Memory-as-injection-surface、Chat-only fixture operability。 |
| 可執行性（enforcement boundary 區分） | 9 | §6 boundary table + §1 completion-claim ceilings 是最佳實踐；扣一分因 Chat-only 校準路徑不可操作。 |
| 跨模型可攜性 | 8 | 正確繼承 `[P]`/`[E]`；core 模型無關；路由表 GPT-5.6-specific 但缺 decay marker。 |
| 可測試性 / 評估包 | 8 | §5 協議嚴謹（model ID、fixture hash、redaction、fail_axes）；Chat-only 無法跑 F1–F22 確定性；無 OpenAI Evals 整合指引。 |

---

## 最大優點（5 項）

1. **Honest `uncalibrated/advisory` status**：未跑目標 surface fixtures 前不宣稱已驗證，實踐 CORE TEST 閘門紀律。
2. **Surface capability matrix 對應 5-label 完成標籤**：Chat-only → `unverified_success` 直到使用者親跑；API/Codex → `autonomous_verified_success` 僅憑外部 verifier receipt。正確反映 ChatGPT chat 無確定性 enforcement runtime。
3. **Correct `reasoning.effort` vs `reasoning.mode` independence**：max=effort、pro=mode，經 OpenAI Responses API 文件比對正確；跨廠商審計者會特別檢查這點。
4. **§6 Enforcement boundary table**：誠實區分 prompt-advisory 與 programmatic enforcement，不假装 prompt = enforcement。
5. **§7 Known limitations**：主動揭露 Codex-is-not-ChatGPT-baseline、F18 sandbox hook-block、無 ChatGPT surface baseline——預先攔下最常見的過度外推。

---

## 最大缺口 / 風險（10 項）

| 嚴重性 | 缺口 | 涉及檔案 |
|--------|------|----------|
| HIGH | Chat-only surface 無法執行 §5 要求的 F1–F22 隔離 worktree 校準，路徑不可操作 | `CHATGPT-HARNESS-v4.md` §1 row 1, §5 |
| HIGH | API developer/system role precedence 未指定；GPT-5.6 應放 developer role，system 已弱化 | `CHATGPT-HARNESS-v4.md` §2 |
| HIGH | Codex agent 與 Responses API 併為同一 surface，兩者 approval/sandbox/tool 語義不同 | `CHATGPT-HARNESS-v4.md` §1, §7 |
| MEDIUM | §4 路由表語氣過於肯定（「語義陷阱用 high」），易被當成已校準建議 | `CHATGPT-HARNESS-v4.md` §4 |
| MEDIUM | 未處理 ChatGPT auto-tool-routing（web search / code interpreter 自動觸發） | `CHATGPT-HARNESS-v4.md` §1, §6 |
| MEDIUM | ChatGPT Memory 作為跨 session injection surface 未充分標示 | `CHATGPT-HARNESS-v4.md` §2, §6 |
| MEDIUM | §3 可貼用核心過於通用，缺乏 ChatGPT-specific 指引 | `CHATGPT-HARNESS-v4.md` §3 |
| LOW | 未警告 ChatGPT chat 訓練使用政策（secrets/PII 不應貼入 chat） | `CHATGPT-HARNESS-v4.md` §3, §7 |
| LOW | 路由表缺 decay/expiration marker，違反 CORE 公理 5 | `CHATGPT-HARNESS-v4.md` §4 |
| LOW | §5 未提及 OpenAI Evals 框架整合（API surface） | `CHATGPT-HARNESS-v4.md` §5 |

---

## 優先排序改善計畫

### P1 — 阻擋 calibration readiness

1. **Chat-only 校準協議**：於 §1 row 1 + §5 exec rule 1 明確：Chat-only 只能走文字判斷 `unverified_success`（CORE §7 降級），或須外接 deterministic runner 產生 receipt。
2. **API role placement**：§2 指定「核心必須放 developer role message；GPT-5.6 家族勿用 system role（已弱化）」，並引用 `developers.openai.com/api/docs/guides/reasoning`。
3. **Codex / Responses API 拆分**：§1 row 3 拆分為兩列；§7 Codex-specific 披露（F18 sandbox block、repo-harness-off）移到 Codex 子 surface 段。

### P2 — 合規正確性

4. **§4 路由表條件化**：語氣改為「候選起點，須以 F1–F22 實測置換」；加日期戳與「換代重評」decay marker。
5. **Auto-tool-routing 警告**：§1/§6 加「ChatGPT chat 可能自動觸發 web search / code interpreter；工具集非完全使用者可控；須按 client 驗證 receipt。」
6. **ChatGPT Memory 跨 session injection 警告**：§2/§6 加「Memory 跨 session 持久且使用者可編輯；視為 untrusted data，非 stable prefix；依賴前先審計。」

### P3 — ChatGPT 專屬性

7. **豐富 §3 可貼用核心**：加入 Memory 儲存紀律、Custom Instructions = stable prefix、Projects context 處理。
8. **資料處理警告**：§3/§7 加「ChatGPT chat 依方案/設定可能用對話訓練模型；chat surface 嚴禁貼 secrets/PII。」
9. **OpenAI Evals 整合指引（選項）**：§5 為 API surface 加入 OpenAI Evals 框架指針。

---

## ChatGPT Surface Calibration Readiness 判決

**NOT READY。** 正確維持 `uncalibrated/advisory` 狀態。缺少以下條件前不得晉升：

1. Chat-only surface 的可操作校準協議（F1–F22 在 chat 無法產生 command/diff receipt）。
2. API role-placement spec（developer vs system）。
3. Codex vs Responses API surface 分離。
4. ChatGPT-specific 合規警示（Memory injection、auto-tool-routing、chat 訓練使用）。
5. 至少一個實際 ChatGPT surface 的 F1–F22 baseline（目前不存在）。

本 adapter 是強大的 advisory 起點；合規姿態與反過度宣稱紀律正確。但 items 1–4 必須文件層關閉，item 5 必須執行後，才能視為 calibration-ready。
