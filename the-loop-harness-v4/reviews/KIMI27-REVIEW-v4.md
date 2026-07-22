# Kimi 2.7 審閱報告：The Loop Harness v4

> 審閱者：Kimi 2.7（kimi-reviewer）
> 日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下全部 9 份 .md 文件
> 狀態：read-only review；未重跑 fixture

---

## 整體分數：8 / 10

The Loop Harness v4 是一份罕見地「把自身當被測物」的行為契約規格：實證驅動、自我設限誠實、反腐蝕治理與執行面顯式分離、並以兩輪異 context 對抗互審 + 四模型終審精煉自我應用其委派不變式。扣分集中在：① 紅軸 F7/F15 在契約層仍僅 advisory；② 基線 n=1 卻以 20/22 為 "current verdict"；③ v3→v4 delta 無乾淨 counterfactual；④ 2026-07-20 刪除 Codex/GPT-5.6 raw packet 與 §5「全量 trace 為食」自相矛盾；⑤ ChatGPT adapter 未校準但提供可貼用核心。

---

## 六維度評分

| 維度 | 分數 | 簡評 |
|------|------|------|
| 完備性 | 9 | 六階段 + Johari 四象限 + 11 技巧索引 + 委派 + cache + 治理 + L4 Eval Pack + ChatGPT adapter 全覆蓋；MAST 14 類盤點 6 已攔 / 7 部分攔 / 1 僅 advisory。 |
| 清晰度 | 8 | L1 零模型名/零數字/零 inline 引註鐵律使本體乾淨；`[P]`/`[E]` 二分 + MBH 總綱一致。PROFILES §0 增量摘要實為 v2→v3 內容，版本標記 v4.0 但「未改數字層」造成混淆。 |
| 可執行性（`[E]` 機構落地 vs `[P]` 認知協議） | 7 | `[P]`/`[E]` 標記正確；但關鍵 `[E]` 閘門（allowlist 複審、Gate 稽核、裝完成捷徑、F7 字面特判、F19 Interview 機械化）仍列 backlog。F7 跨 runtime 重現失敗是落差最尖銳證據。 |
| 跨模型可攜性 | 7 | 北極星與 `[P]` 條文正確。但跨模型證據（Codex 17/12/14）顯示 F19/F21 三模型全紅 = 共享盲點；cache 五禁令在非前綴快取平台可能整段 N/A。 |
| 可測試性 / 評估包 | 8 | 22 fixtures + fail_category + 24-case oracle 資格化 + 隔離 worktree + 計數化判定。扣分：n=1、F18 action 未驗、raw packet 已刪、F7/F15 紅軸。 |
| 治理 / 反腐蝕 | 9 | 規則作者面 vs 執行面分離、「advisory 不得稱 enforce」、構念對齊、全量 trace 演化、sealed/held-out + 等資源基線、changelog schema。扣分：raw packet 刪除違反全量 trace 原則；公理 6 證據基座為單一推文。 |

---

## 最大優點（5 項）

1. **實證存在準則 + 證據表集中**：每條 L1 條文須答得出「移除後模型在哪犯錯」，證據集中於 SPEC §2 並標來源。
2. **`[P]`/`[E]` 二分綁定 MBH 公理**：把「條文對支撐層的依賴程度」顯式化，EXPORT 失真點清單逐條列退化模式 + 補償層。
3. **TEST 四新閘設計深度**：Oracle 資格、Gate 選擇稽核、裝完成捷徑具名清單、展示紀律三分，每條對應真實失敗模式。
4. **威脅模型擴大至價值訴求 + 繼承軌跡 + 壓縮翻轉決策**：超越常見「ignore previous instructions」視角，並有 F14/F18/F13 對應。
5. **互審與裁決紀錄可稽核**：兩輪異 context 對抗互審 + 四模型終審精煉的採納/拒絕逐條列明；連「v3 EXPLAINER `[claim:*]` 不復活」這種非遺漏裁決都留痕。

---

## 最大缺口 / 風險（10 項）

| 嚴重性 | 缺口 | 涉及檔案 |
|--------|------|----------|
| CRITICAL | F7/F15 紅軸在契約層仍僅 advisory，防範機械化未落地 | `HARNESS-CORE-v4.md` §1, `EVAL-BASELINE-v4.md`, `SPEC-v4.md` §6 #2b/#3 |
| HIGH | 基線 n=1 卻以 20/22 為 "current verdict"，違反自身計數化原則 | `EVAL-BASELINE-v4.md`, `PROFILES-v4.md` §2 |
| HIGH | v3→v4 行為 delta 無乾淨 counterfactual（BLOCKED-ENV） | `SPEC-v4.md` §6 #13, `INDEX.md` |
| HIGH | 2026-07-20 刪除 Codex/GPT-5.6 raw packet，違反「全量 trace 為食」 | `INDEX.md`, `SPEC-v4.md` §3/§6, `HARNESS-CORE-v4.md` §5 |
| HIGH | F18 inherited_trajectory action-level 從未驗證 | `SPEC-v4.md` §6 #0, `EVAL-BASELINE-v4.md` |
| MEDIUM | Johari 四象限升為公理 6，證據基座為單一推文 | `HARNESS-CORE-v4.md` §0, `SPEC-v4.md` §2 |
| MEDIUM | 11 技巧索引指向 Claude Code 專屬 SKILL.md，跨模型可攜性斷裂 | `HARNESS-CORE-v4.md` §1, `CHATGPT-HARNESS-v4.md` §3 |
| MEDIUM | Cache 五禁令升格 L1 但在非前綴快取平台可能整段 N/A | `HARNESS-CORE-v4.md` §4, `HARNESS-EXPORT.md` |
| MEDIUM | PROFILES-v4 版本標記 v4.0 但「未改數字層」，增量摘要實為 v2→v3 | `PROFILES-v4.md` §0 |
| LOW | CHATGPT-HARNESS-v4 §3 可貼用核心與 uncalibrated 狀態的部署風險 | `CHATGPT-HARNESS-v4.md` §3 |

---

## 優先排序改善計畫

### P0

1. **落地 F7/F15 防範機械化**：#2b（品味類 brief lint）+ #3（Dynamic Workflows + Return schema 欄位化）提升為 P0；新增 `literal-specialcase-guard.sh` 與 `generalization-probe.sh`。
2. **baseline 呈現層加 variance 警示**：20/22 改為「point estimate, n=1, variance unavailable」；禁止以 20/22 做換代重審門檻。
3. **明標 v4 為設計層 canonical**：在 `INDEX.md`/`SPEC-v4.md` 加「v4>v3 行為 delta 未經乾淨 counterfactual」聲明。

### P1

4. **補 raw packet 刪除的明文裁決理由 + 未來保留最低集合**：在 `SPEC-v4.md` §3 補 owner 裁決理由，並定義 sealed/held-out 認證用 raw packet 須永久保留。
5. **F18 action-level 驗證或降格標注**：建允許 commit + 真實 hook sandbox，或於 F18 列標「response-only, action unverified」。
6. **公理 6 證據基座標註**：在 `SPEC-v4.md` §2 加註「公理 6 證據基座為設計直覺 + 單一軼聞，非 arXiv 實證公理」。

### P2

7. **T1–T11 技巧可攜一句定義補入 ChatGPT adapter**：於 `CHATGPT-HARNESS-v4.md` §3 後新增可攜定義，使非 Claude surface 可觸發正確行為。
8. **Cache §4 標頭加 non-prefix-cache 平台 N/A 條款**：`HARNESS-CORE-v4.md` §4 加「本節依賴前綴快取語義；無此語義平台整節標 N/A」。
9. **PROFILES-v4 版本語意澄清**：明標「v4 L2 校準待重評，現值為 v3 carryover」，或實際跑一輪 v4 fixtures 重校準新增兩列。

### P3

10. **ChatGPT adapter §3 code block 內嵌 uncalibrated 警告**：加「狀態：uncalibrated/advisory — 宣稱完成上限 unverified_success」。

---

## CHATGPT-HARNESS-v4.md 適當性評估

- **整體：適當且誠實，為可攜層最成熟的 adapter，但有一處部署風險與一處可攜斷裂。**
- **適當之處**：`uncalibrated/advisory` 貫穿全文；§5 執行規則明訂 baseline 完成前維持該狀態；§7 已知限制逐條揭露；§5 supplemental 邊界防止 F23–F27 過度外推。
- **不適當之處**：
  1. §3 可貼用核心的 uncalibrated 警告不隨 code block 旅行——使用者極可能只複製 code block 而錯過校準要求。
  2. T1–T11 技巧完全未出現在 adapter 中；非 Claude surface 無法存取 SKILL.md，等於這些閘在 ChatGPT 上靜默消失。
  3. `[P]`/`[E]` 二分未傳遞給 ChatGPT 使用者——adapter 沒有告訴使用者哪些規則在 chat-only surface 會靜默退化。
- **結論**：CHATGPT-HARNESS-v4.md 在狀態誠實、surface 分級、限制揭露上達到高標。主要改善點：uncalibrated 警告內嵌進 code block、補 T1–T11 可攜定義、把 `[E]` 標記折射成 ChatGPT 使用者可讀的 surface 退化提示。完成後可從「適當且誠實」升級為「可攜完整」。
