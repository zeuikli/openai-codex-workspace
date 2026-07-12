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

`gpt-5.6-luna` + `xhigh` 是 provisional 日常預設。主 thread 不做自動 effort 切換；tiny task 的 Luna medium 需走 `cost_write` 或明確新 thread。廣泛探索可走 Terra medium 的 `quality_explore`，架構審查走 Sol medium 的 `ceiling_review`，最高風險安全稽核走 Sol high 的 `frontier_security_review`。高風險 routes 為 read-only，修改與最終驗收保留在主 thread 或 Luna write route。

## Calibration Rule

任何新 mapping 都必須先通過 `EVAL-PACK.md` 中可確定性執行的回歸 fixtures，再依 `GPT-5.6-CALIBRATION.json` 以 5-10 個代表任務比較舊模型 baseline、GPT-5.6 在舊 effort、GPT-5.6 低一級，以及不同時的 proposed mapping effort，記錄成功率、成本或 unavailable、latency、失敗模式與 residual risk。沒有量測前，migration status 必須是 `provisional`，不得宣稱模型切換已證明更好。
