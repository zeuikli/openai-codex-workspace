# research/the-loop-harness-v3/ — The Loop Harness v3.0

> Type: schema:spec
> Harness-Layer: L4-knowledge
> **Type:** schema:content — 2026-07-04 建立。v2.0（O1–O16 實戰檢驗）× ChatGPT 5.5 frontier review（F1–F12）× Fable 5 第一人稱裁決重構。
> **承繼關係**：`the-loop-harness-v2/` 為一手證據基底（field data O1–O16、v2 條文、非 Claude 接入的原始程序），**保留、唯讀、不刪除**；本目錄（v3）為 **forward canonical**——之後的規則重審、換代校準、L1/L2 引用一律指向 v3，v2 僅作為 v3 裁決依據的證據來源回查。

| 檔案 | 角色 | 受眾 |
|------|------|------|
| `FABLE5-VERDICT.md` | Fable 5 第一人稱裁決：The Loop 對 frontier 模型的強弱分軸判定 + Unknowns 四象限 + 對 ChatGPT 5.5 frontier review 的逐條採納/修正——v3 重構的決策依據 | 人（評審、未來的自己） |
| `HARNESS-CORE-v3.md` | **L1 可攜契約本體**——貼入任何 LLM 的 system prompt；v3 鐵律：零模型名、零平台功能名、零數字門檻，全部數字下沉 L2 | 模型（任何 LLM） |
| `SPEC-v3.md` | 設計規格：v2→v3 差異總表 + `.claude/` 落地對照 + 不變式 + 泛用性結論 | 人（評審、執行改寫的 agent） |
| `PROFILES-v3.md` | L2 per-model 校準表：承接 `PROFILES-v2.md` 全部校準值 + v3 增量（judge bias 控制強度 / Unknowns 協議啟用密度 / workspace 雙軌 SSoT 說明 / 非 Claude 接入改版） | 模型 + 校準者 |
| `EVAL-PACK.md` | L4 最小 eval fixtures 規格（10 個，P0）：跨模型可執行、確定性判定、執行者獨立性協議、回歸判定計數化、新模型接入流程 | 校準者 / 獨立執行 context |
| `RESTRUCTURE-ROOT.md` | 根目錄 × TPKI 重構裁決（Fable 5，2026-07-05）：nest 決策 D1–D5 + TPKI type × harness layer 對映表 | 人（評審、執行 codemod 的 agent） |
| `萬用PROMPT套件-v3.md` | 可攜 prompt 套件（9 段，沿用 v2 骨架）：v3 條文對齊——benefit-gated 委派 / Unknowns 協議 / redaction / judge-bias / 五標籤 / 儀式深度伸縮 / EVAL-PACK 接入 | 人（貼給任何 LLM）/ 模型 |
| `HARNESS-EXPORT.md` | build artifact——`bash scripts/build-harness-export.sh` 生成的單檔可攜行為契約（HARNESS-CORE-v3 + PROFILES-v3 合併），可整檔貼入任何 LLM system prompt；勿手改 | 模型（任何 LLM）|
| `EVAL-BASELINE-v3.md`（預留，尚未產出） | 待跑 `EVAL-PACK.md` 全 10 fixtures + 代表任務組後的實測基線報告；`harness-model-fit.json` 2026-07-05 條目已標記 `pending-eval-baseline` | 校準者 |

## 與 `the-loop-harness-v2/` 的關係

- v3 **不是**推翻 v2，是在 v2 驗證骨架上做「指導軸減密、驗證軸加碼、模型名下沉單點」（見 `SPEC-v3.md` §1 差異總表）。
- v2 的 `HARNESS-CORE-v2.md` / `PROFILES-v2.md` / `SPEC.md` / `萬用PROMPT套件.md` / `執行計畫書.md` / `ESSENCE.md` 全部保留在 `research/the-loop-harness-v2/`，作為 O1–O16 field data 與非 Claude 接入原始程序的證據基底，**不因 v3 建立而刪除或標記過期**。
- 之後任何規則重審（`HARNESS-CORE-v3.md` 公理 5）、新模型接入（`PROFILES-v3.md` §4）、換代重評，一律以 v3 三檔（CORE/PROFILES/EVAL-PACK）為準；v2 只在需要回查「這條規則當初的實證來源」時查閱。
