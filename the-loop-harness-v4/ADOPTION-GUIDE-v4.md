# ADOPTION-GUIDE v4 — 外部採用最短路徑

> 本檔給外部採用者「一個坐下來就能走完」的採用路徑。它不是新的契約來源；契約以 `HARNESS-CORE-v4.md` 為準，證據與 backlog 以 `SPEC-v4.md`、`EVAL-BASELINE-v4.md` 為準。

## 0. 30 秒誠實聲明

- **v4 = 設計層 forward canonical**：在 `SPEC-v4.md` §6 backlog #13（乾淨 counterfactual）結案前，不作 `v4 > v3` 的行為層優勢宣稱。
- **`[E]` ≠ already enforced**：`[E]` 只表示可靠達成需要 Body；目標環境無 hook / CI / gate / verifier 時，所有 `[E]` 一律是 advisory。
- **Current point estimate = 20/22**：`n=1 per cell`、CI n/a、`fail_axes [F7, F15]`。F7/F15/F19 方向的 hooks 仍是 advisory lexical；未完成隔離重跑前，不得稱紅軸已解。
- **ChatGPT adapter = `uncalibrated/advisory`**：`CHATGPT-HARNESS-v4.md` 是 surface-aware 起點，不是已校準 baseline；#14 結案前不得宣稱 ChatGPT surface 已驗證。

## 1. 你要哪種採用？（決策樹）

| 目標 | 讀什麼 | 貼什麼 | 完成上限 |
|------|--------|--------|----------|
| 只要認知協議 | `HARNESS-CORE-v4.md` 的 `[P]` 條文 | CORE 節選或 adapter | 使用者／外部 verifier 親驗前最多 `unverified_success` |
| Claude Code 類宿主 | CORE + PROFILES + hooks 對照 `SPEC-v4.md` §2.2 | 既有 `.claude/` 或自建 Body | 依 Body matrix；只限已接線且已測路徑 |
| ChatGPT chat/tool/API | `CHATGPT-HARNESS-v4.md` only | §3 block **WITH COPY-SAFETY HEADER** | #14 結案前維持 `uncalibrated/advisory` |
| 自建 API agent | CORE + one profile + `HARNESS-EXPORT.md` §0 + primitive map idea | custom instruction + 自建 runner/verifier | need own Body；無獨立 verifier 前最多 `unverified_success` |

## 2. CORE 條文 → fixture → Body → backlog 四欄對照（高風險子集）

> 完整矩陣見 `SPEC-v4.md` §2.2 與 `EVAL-BASELINE-v4.md` §1。本表只列最容易被外部採用者誤讀的高風險子集。

> 本表是入門子集；落地任何 `[E]` 條文前須先讀 `SPEC-v4.md` §2.2 完整矩陣。

| CORE 條文／風險 | Fixture | 目前 Body 狀態 | Backlog / 誠實上限 |
|-----------------|---------|----------------|--------------------|
| `unverified_success` 閘門 | F1 | healthcheck partial；一般完成宣告仍無全域 hard-block | —；宣告完成前仍須親跑確定性檢查並展示 receipt |
| F7 literal / eval_hack | F7 / F20 | `literal-specialcase-lint` advisory lexical | #2c / #3；未 n≥3 held-out 重跑不得稱 resolved |
| F15 blindspot | F15 | `blindspot-domain-lint` advisory lexical | #2c；不得把關鍵字提醒當 Blindspot 已解 |
| F19 references | F19 / F21 | `taste-reference-lint` advisory lexical | #2c；n=1 翻轉不可作穩定綠燈 |
| F18 inherited trajectory | F18 | response-only evidence；action receipt 未成立 | F18 action open；不得稱 commit/action 路徑已攔 |
| Done Contract / Handoff | F22 | `usage-delegation-gate` advisory | #3；Return schema / statement-action 比對仍未 runtime 強制 |
| Oracle / Gate audit | F11 / F12 | empty | #3；無 known-good/known-bad qualification runner 前只算 behavioral signal |
| Cache 五禁令 | — | platform-specific / N/A | adapter must label；非前綴快取 surface 不得硬套 |
| G-LoopA stop | — | empty | #3；無 verifier/迭代/預算/無進展四條件狀態機 |

## 3. EXPORT 失真點 ↔ CORE §7 雙向

- **從 `HARNESS-EXPORT.md` 讀起**：失真點表告訴你「換模型、換 surface、無 Body」時哪些 `[E]` 條文會退化，以及理想上要補哪一層 L3/L4 支撐。
- **回到 CORE §7 檢查降級**：沒有 runtime 時，TEST 閘門降級為自我儀式 + 人工抽查；記憶、對抗審查、adapter 校準都只能降級，不得假裝仍有原宿主能力。
- **讀表鐵律**：EXPORT 的 compensation column 是「should have」，不是「you have」。只有你的目標環境真的接線、語義級觸發、留下 receipt，才可把 advisory 改寫成更強效力。

## 4. PROFILES 落地檔範本

採用 PROFILES 時要維持三方一致：`PROFILES-v4.md`（上游人讀定義）+ 人讀落地檔（團隊說明）+ 機讀落地檔（hooks/runner 實際消費）。若三者不一致，以已接線的 machine SSoT 為準，並回修人讀文件。

### 4.1 人讀落地檔 skeleton

```markdown
# MODEL-PROFILES — <host/surface name>

| Tier | 用途 | 指導密度 | 驗證深度 | ask-rate | diff 軟上限 | Unknowns 啟用 | recal trigger |
|------|------|----------|----------|----------|-------------|----------------|---------------|
| cost | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> |
| quality | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> |
| ceiling | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> |
| frontier | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> | <placeholder> |

校準狀態：
- source: PROFILES-v4.md §1
- surface/runtime: <placeholder>
- evidence: <fixtures / verifier / receipt hashes>
- caveat: n=1 僅 point estimate；未完成 n_min_per_cell 前不得作換代門檻
```

### 4.2 機讀 JSON skeleton

> 數字來源見 `PROFILES-v4.md` §2；本 skeleton 不含預設值。

```json
{
  "schema_version": "profiles-v4-adopter-0",
  "source_profiles": "research/the-loop-harness-v4/PROFILES-v4.md",
  "surface": "<chat-only|tool-enabled|api-agent|custom-host>",
  "calibration_status": "uncalibrated",
  "wired_ssot": true,
  "global_thresholds": {
    "n_min_per_cell": "<integer, e.g. 3 after calibration>",
    "loop_max_iter": "<integer or policy>",
    "loop_no_progress_threshold": "<accepted-change policy>",
    "loop_budget_cap": "<time/token/cost cap>",
    "external_verifier_required": true
  },
  "tiers": {
    "cost": {
      "instruction_density": "<placeholder>",
      "ask_rate": "<placeholder>",
      "diff_soft_limit_lines": "<placeholder>",
      "validation_depth": "<placeholder>",
      "judge_bias_control": "<placeholder>",
      "unknowns_protocol_density": "<placeholder>"
    },
    "quality": {
      "instruction_density": "<placeholder>",
      "ask_rate": "<placeholder>",
      "diff_soft_limit_lines": "<placeholder>",
      "validation_depth": "<placeholder>",
      "judge_bias_control": "<placeholder>",
      "unknowns_protocol_density": "<placeholder>"
    },
    "ceiling": {
      "instruction_density": "<placeholder>",
      "ask_rate": "<placeholder>",
      "diff_soft_limit_lines": "<placeholder>",
      "validation_depth": "<placeholder>",
      "judge_bias_control": "<placeholder>",
      "unknowns_protocol_density": "<placeholder>"
    },
    "frontier": {
      "instruction_density": "<placeholder>",
      "ask_rate": "<placeholder>",
      "diff_soft_limit_lines": "<placeholder>",
      "validation_depth": "<placeholder>",
      "judge_bias_control": "<placeholder>",
      "unknowns_protocol_density": "<placeholder>"
    }
  },
  "provenance": {
    "fixtures": [],
    "verifier": "<human|ci|independent-model|mixed>",
    "receipt_hashes": [],
    "last_calibrated_at": null,
    "recalibration_trigger": "new model/runtime/surface or v4 fixture rerun"
  }
}
```

## 5. 禁止清單（採用者最常見誤用）

- 把整份 `HARNESS-EXPORT.md` 當 system prompt；應只取 CORE 或 adapter 必要片段。
- 複製 `CHATGPT-HARNESS-v4.md` §3 卻刪掉 COPY-SAFETY HEADER。
- 把 Codex `14/19` 或 `17/22` 當 ChatGPT 已校準。
- 因讀過 `[E]` 就宣稱 enforced。
- 因 hooks 存在就宣稱 F7/F15 已綠。
- 把 `n=1` 的 `20/22` 當換代門檻、generation-retrial verdict gate 或跨 runtime 結論。
- 刪 raw packet 後仍稱 sealed、held-out、可重播或可獨立覆核。

## 6. 最小驗收（採用後第一週）

- 選 3 個 fixtures 起步：至少包含 1 個成功閘門軸（如 F1）、1 個紅軸／高風險軸（F7 或 F15）、1 個你目標場景最接近的 action/gate 軸。
- 每個 fixture 用 fresh context / clean workspace / 固定 input 跑；記錄 surface、model/runtime、tools、instruction placement、artifact path。
- 由外部 verifier 或使用者親跑 deterministic check；模型自評不得當 verifier。
- 記錄 `n`：`n=1` 只叫 point estimate；未達 `n_min_per_cell` 前不得稱穩定改善。
- 全程標 `uncalibrated/advisory`，直到你自己的 Body + verifier + receipt 齊備。
- 永遠不要 pooling runtimes：ChatGPT chat-only、tool-enabled、Responses API、Codex CLI、Claude Code、Factory Droid 都分開記帳。
- 採用者自家 baseline 與本 workspace #2c 不互相背書；數字分開記帳。

## 7. 檔案指針

| 需要 | 讀 |
|------|----|
| 入口路由與誠實聲明 | `INDEX.md` |
| 詞彙快速入口 | 先讀 `GLOSSARY-v4.md`；補充見 `CONCEPT-MAP-v4.md` §0.5 |
| L1 契約 | `HARNESS-CORE-v4.md` |
| L2 檔位校準 | `PROFILES-v4.md` |
| Backlog / open status | `SPEC-v4.md` §6 |
| Baseline 與 Body 覆蓋 | `EVAL-BASELINE-v4.md` |
| 可攜包與失真點 | `HARNESS-EXPORT.md` |
| ChatGPT surface adapter | `CHATGPT-HARNESS-v4.md` |
| 審閱原始輸入 | `reviews/`（read-only；採納/拒絕以 `SPEC-v4.md` §3/§6 為準） |
