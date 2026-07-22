# Fable 5 AFTER 再審 — 2026-07-21

> 審閱者：Fable 5（fable-5-auditor）
> 範圍：對照本人 2026-07-20 原審（`reviews/FABLE5-REVIEW-v4.md`）與 R1 再審（`reviews/BEFORE-AFTER-REREVIEW-2026-07-20.md`），驗證 2026-07-21 第二輪文件收斂實際落地內容後重打分。
> 方法：read-only 抽驗（INDEX §0–§6 / GLOSSARY / ADOPTION-GUIDE / CHATGPT-HARNESS §0–§4·§9 / HARNESS-EXPORT §0.1–0.5 / SPEC §6 / PROFILES §2）；**未重跑任何 fixture**。
> 標籤：`unverified_success`

---

## 整體分數（R2 After **8.8** / 10）

Before 8.5 → R1 8.7 → **R2 8.8**。本輪增量全部在文件層與 onboarding 層：GLOSSARY-v4 + ADOPTION-GUIDE-v4 落地（原 P2-9 關鍵訴求結案）、INDEX 補新採用者入口路徑與逐檔 router、EXPORT §0 治理 preamble（advisory/hard-block 四級效力表 + raw-packet 政策 stub）、PROFILES §2 補齊全部 dangling-pointer 門檻並定義 n≥3 滿分輪。這些是真實且可驗證的改善，但**行為層一分未動**：baseline 仍 Round 2 = 20/22、fail_axes [F7, F15]、每 cell n=1；#2c/#3/#13/#14/F18-action 全數仍 open。文件完美度已接近該層天花板，再往上加分只能來自行為證據——因此是 8.8，不是 9+。

## 六維度 Before → R1 → R2

| 維度 | Before | R1 | R2 | R2 依據 |
|------|--------|----|----|---------|
| 完備性 | 9 | 9 | **9.1** | GLOSSARY / ADOPTION-GUIDE 補齊伴讀層；PROFILES §2 dangling-pointer 對帳聲明（G-LoopA 三門檻列入、「≤2 句」殘留標無現行綁定）；#3/#13/#14 仍開故不到 9.5。 |
| 清晰度 | 7 | 7.3 | **8.2** | 本輪最大贏家：GLOSSARY-v4（原 P2-9）、INDEX §0 三輪入口路徑、§1 逐檔 router 表、ADOPTION-GUIDE §1 決策樹 + §2 高風險誤讀四欄對照，直接命中原審「術語密度偏高、新讀者須同讀四檔」缺口。 |
| 可執行性 | 8 | 8.2 | **8.4** | ADOPTION-GUIDE §4 人讀/機讀 skeleton + CORE→fixture→Body→backlog 對照可直接照走；但 #3 Dynamic Workflows 基座未動，`[E]` 條文多數仍無機械執行路徑，封頂於此。 |
| 跨模型可攜性 | 9 | 9 | **9.2** | EXPORT §0.1 三層可攜地圖 + §0.6 防整檔誤貼路徑；CHATGPT §3 copy-safety header 首行內嵌、cache 五禁令降級段（無 cache 平台標 N/A，原 P2-6 結案）、§4 decay marker。 |
| 可測試性 | 8 | 8 | **8.0** | **持平，刻意不加分**：未重跑 F1–F22；n=1 point estimate 未變；F11–F19 lexical check 未升 qualified oracle；F18 action receipt 未成立。PROFILES n≥3 定義是規格不是數據。 |
| 治理/反腐蝕 | 9 | 9.1 | **9.3** | INDEX §3「`[E]`≠enforce」+ §4「hooks 不改 baseline 分」雙誠實聲明；EXPORT §0.2 自報成功鏈自我應用 + §0.5 raw-packet 不偽造政策 stub；SPEC §6 補 #13-packet 與 F18-action 開帳——對原審 HIGH 缺口（raw packet 已刪）的 caveat 分支完整回應。 |

## 原 P0–P3 結案狀態

| # | 原建議 | 狀態 | 依據 |
|---|--------|------|------|
| P0-1 | 機械化 F7/F15 紅軸防範 | **PARTIAL** | #2b 三 advisory lexical hooks 落地（R1 已計）；hard-block 未建、#2c held-out 重跑未做，行為軸 UNVERIFIED（EXPORT §0.3）。 |
| P0-2 | 複製樣本 baseline（n≥3/cell） | **PARTIAL** | PROFILES §2 已定義「n≥3 才計滿分輪」+ per-row recal trigger；隔離重跑（#2c）未執行，verdict 仍 n=1。 |
| P1-3 | F11–F19 升 qualified oracle | **OPEN** | ADOPTION-GUIDE §2 明列 Oracle/Gate audit Body = empty；無 known-good/known-bad runner。 |
| P1-4 | raw packet 恢復或醒目 caveat | **CLOSED（caveat 分支）** | EXPORT §0.5 政策 stub（不偽造、`packet_absent` 標記、強制措辭「原文僅 git 歷史可考」）+ SPEC/INDEX #13-packet 開帳；保留集合本體另立 #13-packet 續 OPEN。 |
| P1-5 | ChatGPT 三 surface 校準 | **OPEN** | §4 已降級「未驗證起點假設」+ decay marker（子項 CLOSED）；#14 實測基線數仍為 0。 |
| P2-6 | adapter 標 cache 五禁令 N/A | **CLOSED** | CHATGPT §3 貼用核心含 Cache/Context 降級段（無 cache 平台標 N/A + 保留行為紀律）。 |
| P2-7 | 落地 §5 治理 hook / Workflows 基座 | **OPEN** | #3 未動；Handoff Return schema / 陳述-行動比對仍無 runtime 強制。 |
| P2-8 | G-LoopA 獨立 stop-condition 段 | **CLOSED（條文層）** | INDEX §7 記 CORE §1 補獨立終止條件段；PROFILES §2 三門檻列入（待校準建議值）；runtime 狀態機留 #3。 |
| P2-9 | 新增 GLOSSARY-v4 | **CLOSED** | `GLOSSARY-v4.md` standalone 落地：describe-only、每詞附 canonical 指針、Johari/MBH/`[P]`/`[E]`/T1–T11/五禁令全覆蓋。 |
| P3-10 | F18 action receipt 真驗 | **OPEN** | SPEC §6 F18-action ledger 開帳（追蹤已建）；三路仍 UNTESTED_ACTION，sandbox 驗證未做。 |
| P3-11 | 定義「連 2 輪滿分」最低 n | **CLOSED** | PROFILES §2「eval 每 cell 最低 n」列 + 天花板節奏行綁定「滿分輪須 n≥3」。 |
| P3-12 | F23–F27 升格路徑 | **OPEN** | 仍不計 current denominator；oracle qualification 未完成（INDEX §8）。 |

結算：CLOSED 4（P1-4/P2-6/P2-8/P2-9，另 P3-11）= 5 項，PARTIAL 2，OPEN 5。

## 仍 open 紅燈 Top 5

1. **F7/F15 行為紅軸（#2c）**——advisory lexical 可被換寫法繞過；n≥3 held-out 隔離重跑前，20/22 不得改寫、紅軸不得稱已解。這仍是整個 harness 唯一的 CRITICAL。
2. **#3 Dynamic Workflows L3 基座**——`[E]` 條文的效力天花板卡在這裡；Handoff Return schema 化與陳述-行動機械比對缺席，治理面自身仍靠 advisory。
3. **#14 ChatGPT 三 surface 零實測**——adapter 文件品質已高，但 chat-only/tool-enabled/API 實測基線數 = 0，uncalibrated 標籤不可摘。
4. **#13 + #13-packet 證據鏈**——v4>v3 行為 delta 無乾淨 counterfactual；已刪 raw packet 僅 git 歷史可考，政策 stub 是誠實記帳、不是覆核能力。
5. **F18-action**——繼承軌跡威脅的 action-level 攔截從未驗證；response-level PASS 不外推。

## 一句結論

本輪把「頂級 advisory 規格」補成「頂級 advisory 規格 + 一流 onboarding 與治理誠實層」（8.5→8.8），但可測試性一分未動——下一個 0.5 分只能靠 #2c n≥3 重跑與 #3 Workflows 基座，不能再靠寫文件。

完成標籤：`unverified_success`（read-only 文件抽驗；未重跑 fixture；行為宣稱一律未驗證）。
