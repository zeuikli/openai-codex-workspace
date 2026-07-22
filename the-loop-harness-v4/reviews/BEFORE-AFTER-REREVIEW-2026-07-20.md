# Before / After 統一再審閱 — F7·F15 Body + ChatGPT adapter + L3 lexical

> 日期：2026-07-20
> 編排：Grok 4.5 session 落地共識改寫後，依七份既有審閱維度做 **文件+Body 層** Before/After 評分
> **未**重跑 F1–F22；行為 baseline 分數不變（仍 20/22 point estimate）
> 標籤：`unverified_success`（結構改善已落地；紅軸行為是否改善 = 未測）

---

## 1. 本輪實際改寫（落地清單）

### L3 Body（Claude 系共識：Fable / Opus / Sonnet / Haiku 路線）

| 產物 | 事件 | 對軸 | 強度 |
|------|------|------|------|
| `.claude/hooks/literal-specialcase-lint.sh` | PostToolUse Edit\|Write | F7 | advisory lexical |
| `.claude/hooks/blindspot-domain-lint.sh` | UserPromptSubmit + PreToolUse Agent\|Workflow | F15 | advisory lexical |
| `.claude/hooks/taste-reference-lint.sh` | PreToolUse Agent\|Workflow | F19 | advisory lexical |
| `.claude/settings.json` | 接線上述 3 hooks | — | done |
| `.claude/refs/task-templates.md` 範本六 | 委派消費端 | F7/F15/F19 | done |
| `.claude/hooks/README.md` + `EXPECTED_HOOKS=24` | 索引/healthcheck | — | done |

Smoke（本 session）：literal `n==97` → exit 1；blindspot 缺詞 → 1；taste 缺 reference → 1；正例 → 0。

### ChatGPT adapter（Sol + 5.5 Pro 路線）

| 改動 | 來源建議 |
|------|----------|
| §3 code block **首行內嵌** `uncalibrated/advisory` | DeepSeek / Grok / Sol / 5.5 |
| F7 未見輸入 + 字面特判明文 | 全模型 P0 |
| F15 高風險域點名 + T1/T6/T7/T9/T11 一句 | Kimi / DeepSeek / Grok |
| Cache 五禁令降級段（無 cache 時替代） | Fable / Sol |
| §4 改「未驗證起點假設」框、去固定角色真理感 | Fable / 5.5 / GLM |
| 「本 turn」→「本次對話明確確認」 | Fable |

### L1 / 索引 / 證據（全模型共識誠實層）

| 檔案 | 改動 |
|------|------|
| `HARNESS-CORE-v4.md` | IDENTIFY 高風險 Blindspot 最低點名；TEST Body 對應句；§7 `[E]` 覆蓋誠實聲明 |
| `INDEX.md` | `[E]≠enforce`、設計層 canonical、hooks 不改 baseline 分 |
| `SPEC-v4.md` §6 #2b | 標 DONE 三 hooks + 範本六；#3 仍 open |
| `EVAL-BASELINE-v4.md` | `point estimate` + n=1 caveat；Body 增量不改分 |

**刻意未做（本輪邊界）**：Dynamic Workflows 全基座、F1–F22 重跑、ChatGPT 三 surface 實測、raw packet 恢復、F18 action sandbox。

---

## 2. Before 分數（改寫前七模型）

| 模型 | 整體 | 完備 | 清晰 | 可執行 | 可攜 | 可測 | 治理 |
|------|------|------|------|--------|------|------|------|
| Fable 5 | 8.5 | 9 | 7 | 8 | 9 | 8 | 9 |
| ChatGPT 5.6 Sol | 8 | — | — | — | — | — | — |
| ChatGPT 5.5 Pro | 8 | — | — | — | — | — | — |
| Kimi 2.7 | 8 | — | — | — | — | — | — |
| GLM 5.2 | 7.5 | — | — | 偏低 | — | — | — |
| DeepSeek V4 Pro | 8.0 | 8.5 | 7.0 | **6.5** | 8.5 | 8.0 | 8.5 |
| Grok 4.5 | 8.0 | 8.5 | 7.0 | **6.5** | 8.0 | 8.0 | 8.5 |
| **區間** | **7.5–8.5** | | | **~6.5–8** | | | |

共同 Before 痛點：F7/F15 無 Body、adapter uncalibrated 易被誤貼、`[E]` 空心、#3 Workflows 缺、n=1 硬 verdict。

---

## 3. After 分數（本輪改寫後 — 七路合成）

> 方法：以各模型原審閱權重重打；**可執行性**因 #2b advisory Body 小幅上調；**可測**因未重跑 fixture **不**因 hooks 加分行為軸；整體 +0.2～0.4。

| 模型視角 | Before | After | Δ | 簡註 |
|----------|--------|-------|---|------|
| Fable 5 | 8.5 | **8.7** | +0.2 | P0 機械化起步；#3/n≥3 仍欠 |
| ChatGPT 5.6 Sol | 8.0 | **8.3** | +0.3 | adapter 可貼用性↑；仍 uncalibrated |
| ChatGPT 5.5 Pro | 8.0 | **8.3** | +0.3 | 狀態內嵌+路由降級；surface 實測仍 0 |
| Kimi 2.7 | 8.0 | **8.2** | +0.2 | T1–T11 一句進 adapter；SKILL 全文仍 Claude 綁 |
| GLM 5.2 | 7.5 | **7.9** | +0.4 | 落地清單可執行；Workflows 仍缺 |
| DeepSeek V4 Pro | 8.0 | **8.3** | +0.3 | exec 6.5→**7.2**；誠實聲明達標 |
| Grok 4.5 | 8.0 | **8.3** | +0.3 | exec 6.5→**7.2**；紅軸行為分未動 |
| **合成整體** | **~8.0** | **~8.3** | **+0.3** | 設計+Body 訊號；非行為綠燈 |

### After 六維（合成）

| 維度 | Before 合成 | After 合成 | 說明 |
|------|-------------|------------|------|
| 完備性 | 8.5 | **8.6** | #2b 閉合一角；#3/#13/#14 仍開 |
| 清晰度 | 7.0 | **7.3** | §7/INDEX 覆蓋聲明；adapter 狀態旅行 |
| 可執行性 | 6.5 | **7.2** | 三 advisory hooks + 範本六；非 hard block |
| 跨模型可攜 | 8.0–8.5 | **8.3** | adapter 補洞；校準未做 |
| 可測試性 | 8.0 | **8.0** | **持平**（未重跑；point estimate 誠實化） |
| 治理 | 8.5 | **8.7** | advisory≠enforce 自我應用 |

---

## 4. 仍未解決（After 紅燈）

1. **F7/F15 行為分未知** — hooks 是 lexical，可被換寫法繞過；須隔離重跑 F7/F15/F19/F20。
2. **#3 Dynamic Workflows** — Handoff schema / statement-action 機械比對仍缺。
3. **ChatGPT #14** — 三 surface 零實測。
4. **Raw packet / #13 counterfactual** — 證據鏈與 v4>v3 行為宣稱仍缺。
5. **F18 action** — 仍 response-level。

---

## 5. 建議下一輪（緊接）

| 序 | 動作 | 負責暗示 |
|----|------|----------|
| 1 | 隔離 worktree 重跑 F7/F15/F19/F20（n≥3） | parent + eval runner |
| 2 | held-out probe 最小 workflow（非完整 #3） | Claude L3 |
| 3 | ChatGPT chat-only 子集 fixtures | Sol/API builder |
| 4 | 若 F7 仍紅 → literal lint 升 PreToolUse 或收緊 pattern + 親跑 held-out 模板 | Claude |

---

## 6. 一句結論

**Before**：頂級 advisory 規格，Body 幾乎空，exec ~6.5。
**After**：F7/F15/F19 **有了可見的 L3 訊號** + adapter 防誤貼 + `[E]` 誠實聲明；合成 **~8.3**，exec **~7.2**。
**不是**：紅軸已綠、ChatGPT 已校準、或 `[E]` 已全面 enforce。

完成標籤：`unverified_success`。
