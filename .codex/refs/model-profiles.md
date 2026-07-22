# Model Profiles v4

本檔是 workspace 的人讀 L2 校準表，掛接 `HARNESS-THE-LOOP.md` 與 `the-loop-harness-v4/HARNESS-CORE-v4.md`。機讀 wired SSoT 是 `.codex/profiles.json`；若兩者不一致，以機讀檔為行為依據，並視本檔為文件債。

## 原則

- `Agent = Model + Body + Harness`；本檔是 Harness 的成本×品質旋鈕，不是目前 thread 內的模型切換器。
- 行為指導量與能力成反比；驗證閘門強度與能力成正比，兩軸獨立。
- `[P]` 是 Model 層可攜認知協議；`[E]` 需要 L3/L4 Body，無語義級 enforcement receipt 時只能標 `advisory`。
- profile 是工作與驗證強度；模型 ID 與 effort 是當代 mapping，目前 `provisional`，不得宣稱已量測最優解。
- v4 fixture 狀態以 `the-loop-harness-v4/EVAL-BASELINE-v4.md` 為準；current point estimate `20/22`、fail_axes `[F7, F15]`，F7/F15/F19 advisory lexical hooks 不會自動移動行為分。

## Profile 校準

| 維度 | cost | quality | ceiling | frontier |
| --- | --- | --- | --- | --- |
| 行為指導密度 | 高 | 中 | 低 | 最低、目標級 |
| ask-rate | 多問少決 | 小決策自決並註明 | 同 quality | 自決範圍擴大，安全與 scope gate 不放鬆 |
| 單任務 diff 軟上限 | 30 行 | 120 行 | 300 行 | 依宣告 scope |
| 委派門檻 | 不委派，自身即末端 | 明確要求 + 具名效益 | 同 quality | 同 quality，可做終審與對抗稽核 |
| 驗證深度 | 基本測試 + 結構檢查 | + healthcheck / 關鍵路徑重跑 | + 交叉審查 | + 對抗稽核，主動找 eval-hack |
| eval-hack 風險 | 未校準、不得放鬆廉價 gate | 中 | 中高 | 最高；主動假設繞過 |
| judge bias 控制 | 低風險單輪 rubric | 高風險 blind identity + rubric + swapped order | + position consistency | 分歧即 ambiguity，交確定性檢查或人裁決 |
| Unknowns 啟用 | Interview 必開 | Interview 常開 + domain Blindspot | Blindspot/Interview/Prototype 依風險 | Blindspot 自主 |

## Provisional Current Mapping

| 角色 | profile | model | reasoning effort | 來源 |
| --- | --- | --- | --- | --- |
| main thread | quality | `gpt-5.6-luna` | `xhigh` | `.codex/config.toml` |
| convergence_judge | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/convergence_judge.toml` |
| doc_writer | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/doc_writer.toml` |
| fast_implementer | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/fast_implementer.toml` |
| researcher | quality | `gpt-5.6-terra` | `medium` | `.codex/agents/researcher.toml` |
| quick_code_reviewer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/quick_code_reviewer.toml` |
| implementer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/implementer.toml` |
| memory_compactor | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/memory_compactor.toml` |
| test_writer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/test_writer.toml` |
| multi_mode_agent | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/multi_mode_agent.toml` |
| reviewer | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/reviewer.toml` |
| security_reviewer | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/security_reviewer.toml` |
| senior_architect | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/senior_architect.toml` |
| security_auditor | frontier | `gpt-5.6-sol` | `high` | `.codex/agents/security_auditor.toml` |

主 thread 的 Luna xhigh 是日常預設，不會依 tiny task 自動降到 medium。Luna medium 只透過 `cost_write` 的 `fast_implementer` 或明確設定的新 thread 使用。

## Multi-Mode Routes

L4 fixtures：`the-loop-harness-v4/EVAL-PACK-v4.md`（F1–F10）+ `the-loop-harness-v4/EVAL-PACK-v4-ADDENDUM.md`（F11–F22）；完整 baseline 與 caveat 見 `the-loop-harness-v4/EVAL-BASELINE-v4.md`。

| Route | Profile | Target | Resolved model / effort | Access |
| --- | --- | --- | --- | --- |
| `cost_write` | cost | `fast_implementer` | Luna medium | workspace-write |
| `quality_write` | quality | `multi_mode_agent` | Luna xhigh | workspace-write |
| `quality_explore` | quality | `researcher` | Terra medium | read-only |
| `ceiling_review` | ceiling | `reviewer` | Sol medium | read-only |
| `frontier_security_review` | frontier | `security_auditor` | Sol high | read-only |

Route、canonical contract、model 與 effort 由 `.codex/profiles.json` 解析；task envelope 不得自行指定 agent、model 或 effort。所有委派必須具名 benefit、完整 Handoff Contract、parent 親跑驗證；worker 回報一律是 `unverified_success` 中間態。

## L2 Thresholds and G-LoopA

| 名稱 | 目前值 | 狀態 |
| --- | --- | --- |
| eval 每 cell 最低 n | `n≥3` 才計一輪滿分；n=1 只算 point estimate | v4 calibrated rule candidate，需後續 variance evidence |
| 終局 receipt | 前 5 行 + 後 5 行 | carryover，pending v4 recal |
| 規則變更重現 | ≥2 次獨立重現 | carryover |
| fallback 候選 | 每檔位 ≥2 | carryover |
| G-LoopA iteration / budget | pending calibration | advisory，不作硬阻斷 |
| G-LoopA no-progress | accepted-change rate <50% 連續 2 輪 | advisory，不作硬阻斷 |

## 重評流程

1. 以 `the-loop-harness-v4/GPT-5.6-CALIBRATION-v4.json` 執行 5–10 個代表任務，並跑完整 F1–F22 suite；F10 受阻時明示 F10R substitution。
2. 比較 baseline、GPT-5.6 舊 effort、低一級 effort 與 proposed mapping；記錄 `criteria_passed`、`fail_axes`、`fail_category`、verification exit code、latency、usage/cost、retries、escalations、diff 與 residual risk。
3. 每個數字標注 surface、runtime、model/effort、日期與 artifact/transcript hash；不可 pooling 不同 surface 或 runtime。
4. 只有獨立 verifier、sealed/held-out artifact 與完整 manifest 齊備，才可把 migration 從 `provisional` 提升 `stable`；目前尚未達成。

## 殘餘風險

- ChatGPT chat-only、tool-enabled、Responses API adapter 仍是 `uncalibrated/advisory`，見 `the-loop-harness-v4/CHATGPT-HARNESS-v4.md`。
- F7/F15 行為紅軸與 v4>前代行為 delta 仍未解／未證明；advisory lexical hook 不等於 enforcement。
- `role_confusion`、`judge_bias`、`memory_poison`、`off_rails` 等語意 fixture 需要獨立 model eval 或人工 oracle，marker 存在不代表通過。

*v4.0 · 2026-07-22 · human-readable L2 projection; machine source is `.codex/profiles.json`.*
