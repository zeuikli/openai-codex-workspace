# The Loop Harness v3 Profiles

本檔是 L4 source，用來支撐 `.codex/refs/model-profiles.md` 與 `.codex/profiles.json`。L1 行為契約仍以 `HARNESS-THE-LOOP.md` 為準；本檔只描述模型分級、委派與驗證預算的校準來源。

## GPT-5.6 Routing

| Workload | Model | Reasoning | Profile |
| --- | --- | --- | --- |
| 微小變更、rename、tiny UI、低風險文件更新 | `gpt-5.6-luna` | `medium` | `cost` |
| 一般 bug fix、明確功能、日常實作、測試與 diff review | `gpt-5.6-luna` | `xhigh` | `quality` |
| 不明確任務、廣泛 repo 探索、唯讀背景蒐集 | `gpt-5.6-terra` | `medium` | `quality` |
| 複雜 bug、架構設計、auth、migration、高風險 review | `gpt-5.6-sol` | `medium` | `ceiling` |
| 前一步失敗、安全稽核、最高風險或需要對抗檢查 | `gpt-5.6-sol` | `high` | `frontier` |

## Escalation

`gpt-5.6-luna` + `xhigh` 是日常主力。若代表任務證據顯示不足，先升到 `gpt-5.6-terra` + `medium` 做探索或平衡檔，再升到 `gpt-5.6-sol` + `medium`。只有前一步失敗、高風險或最高強度稽核才使用 `gpt-5.6-sol` + `high`；`xhigh` 或 `max` 留給另行定義且可量測的極端任務。

## Calibration Rule

任何新 mapping 都必須先通過 `EVAL-PACK.md` 的回歸 fixtures，再以 5-10 個代表任務記錄成功率、成本、latency、失敗模式與 residual risk。沒有量測前，只能稱為 routing update，不得宣稱模型切換已證明更好。
