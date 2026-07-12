# Model Profiles v3

本檔是 workspace 的人讀 L2 校準表，掛接 `HARNESS-THE-LOOP.md` 的能力伸縮條款。機讀 wired SSoT 是 `.codex/profiles.json`；若兩者不一致，以 `.codex/profiles.json` 為行為依據，並視本檔為文件債。

## 原則

- 行為指導量與能力成反比。
- 驗證閘門強度與能力成正比。
- profile 是工作與驗證強度，不代表在目前 thread 內切換模型。
- 所有模型 ID 與數字門檻集中在 L2；L1 契約維持模型無關。
- GPT-5.6 路由依官方模型分級與 2026-07-13 任務效益表：Luna 處理日常與高效率工作，Terra 處理廣泛探索的平衡檔，Sol 處理架構、安全與高風險決策。

## Profile 校準

| 維度 | cost | quality | ceiling | frontier |
| --- | --- | --- | --- | --- |
| 行為指導密度 | 高，步驟級指示 | 中 | 低 | 最低，目標級 |
| ask-rate | 多問少決 | 小決策自決並註明 | 同 quality | 自決範圍擴大，但安全與 scope gate 不放鬆 |
| 單任務 diff 軟上限 | 30 行 | 120 行 | 300 行 | 依宣告 scope |
| 委派門檻 | 不委派，自身即末端 | 需明確使用者要求與具名效益 | 同 quality | 同 quality，可做終審與對抗稽核 |
| 驗證深度 | 基本測試 + 結構檢查 | + healthcheck 或關鍵路徑重跑 | + 交叉審查 | + 對抗稽核，主動找 eval-hack 痕跡 |
| eval-hack 風險 | 低 | 中 | 中高 | 最高 |
| 記憶寫入權 | 只記事實 | 事實 + 教訓 | + 結構化反思 | + 失敗假設與演化候選 |
| judge bias 控制 | 單輪 rubric 即可 | 高風險比較盲化身份 + rubric 逐項給分 | + 對調順序一次 + 記錄 position consistency | + 分歧視為任務歧義訊號，交確定性檢查或人裁決 |
| Unknowns 協議 | Interview 必開 | Interview 常開，Blindspot 視陌生度啟用 | 三構件依風險彈性啟用 | Blindspot 自主，開工前主動掃描使用者可能沒想到要問的事 |

## Current Mapping

| 角色 | profile | model | reasoning effort | 來源 |
| --- | --- | --- | --- | --- |
| main thread | quality | `gpt-5.6-luna` | `xhigh` | `.codex/config.toml`，2026-07-13 盤點 |
| convergence_judge | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/convergence_judge.toml`，2026-07-13 盤點 |
| doc_writer | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/doc_writer.toml`，2026-07-13 盤點 |
| fast_implementer | cost | `gpt-5.6-luna` | `medium` | `.codex/agents/fast_implementer.toml`，2026-07-13 盤點 |
| researcher | quality | `gpt-5.6-terra` | `medium` | `.codex/agents/researcher.toml`，2026-07-13 盤點 |
| quick_code_reviewer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/quick_code_reviewer.toml`，2026-07-13 盤點 |
| implementer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/implementer.toml`，2026-07-13 盤點 |
| memory_compactor | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/memory_compactor.toml`，2026-07-13 盤點 |
| test_writer | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/test_writer.toml`，2026-07-13 盤點 |
| multi_mode_agent | quality | `gpt-5.6-luna` | `xhigh` | `.codex/agents/multi_mode_agent.toml`，2026-07-13 盤點 |
| reviewer | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/reviewer.toml`，2026-07-13 盤點 |
| security_reviewer | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/security_reviewer.toml`，2026-07-13 盤點 |
| senior_architect | ceiling | `gpt-5.6-sol` | `medium` | `.codex/agents/senior_architect.toml`，2026-07-13 盤點 |
| security_auditor | frontier | `gpt-5.6-sol` | `high` | `.codex/agents/security_auditor.toml`，2026-07-13 盤點 |

## 重評流程

1. 以 `the-loop-harness-v3/EVAL-PACK.md` 全部 fixtures 加代表任務組執行。
2. 產出 `criteria_passed`、`fail_axes`、每項 `fail_category` 與代表任務觀察。
3. 更新 `.codex/profiles.json`，再同步本檔。
4. 換代或模型 alias 改變時重跑；沒有 fixture 的重審不得作為行為依據。

## 殘餘風險

- `the-loop-harness-v3/PROFILES-v3.md` 原始文字中的 `.claude/**` 對應已映射到 `.codex/**`；若未來導入新的 hook 消費欄位，需先擴充 `.codex/profiles.json` schema 與 validator。
- 本次已將四個 pilot skill、十三個 custom agent、主線 config 與 validator/test 的模型 mapping 更新到 GPT-5.6 分級；尚未實跑 5-10 個代表任務量測新 mapping 的實際勝率與成本。
