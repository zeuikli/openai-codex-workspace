# Codex Subagent Advisor Strategy（實務版）

> 更新日期：2026-04-14  
> 依據：OpenAI Codex 官方 `subagents`、`config-reference`，並吸收 `advisor-strategy` 的分工精神。

## 1) 必守官方規範

1. Subagent 只在「明確要求」才啟動。  
2. Subagent 會額外消耗 token，不可為了形式而 fan-out。  
3. 自訂 agent 檔案至少要有 `name`、`description`、`developer_instructions`。  
4. `agents.max_threads` 預設為 6、`agents.max_depth` 預設為 1，除非有強需求，不提高深度。  
5. `nickname_candidates` 僅是顯示名稱，識別仍以 `name` 為準。

## 2) Advisor-style 在 Codex 的落地

核心做法不是「最強模型全程主控」，而是把主迴圈與顧問職責拆開：

- 主 Agent（Lead）負責目標對齊、風險裁決、結果整合。
- 探索型子代理負責讀取、盤點、蒐證。
- 實作型子代理只在需求與邊界已清楚時改檔。
- 審查/安全子代理像「顧問」，提供高價值判斷，不做不必要寫入。

## 3) 模型與角色分派

| 角色 | 建議模型 | Sandbox | 用途 |
|---|---|---|---|
| Lead / 主 Agent | `gpt-5.4` | `workspace-write` | 任務拆解、衝突裁決、最終輸出 |
| Explorer / Docs Researcher | `gpt-5.4-mini` | `read-only` | 快速讀取、規範查證、證據整理 |
| Implementer / Test Writer | `gpt-5.3-codex` | `workspace-write` | 實作、補測試、執行驗證 |
| Reviewer / Security Reviewer | `gpt-5.3-codex` 或 `gpt-5.4` | `read-only` | 回歸風險、漏洞、品質把關 |

## 4) 啟動與禁止條件

### 啟動條件（任一成立）

1. 使用者明確要求分派 subagents。  
2. 任務可切成互不阻塞的子工作。  
3. 每個子任務都能定義清楚輸入、輸出、完成條件。

### 禁止條件

1. 小改動（單檔或單命令即可完成）。  
2. 多個 worker 需要同時改同一檔案。  
3. 尚未定義驗證方式與收斂標準。

## 5) 標準回報格式（所有 subagent 一致）

每個 subagent 回報都必須包含：

1. `範圍`：處理到的檔案/模組。  
2. `發現`：重點結論與風險。  
3. `建議`：下一步可執行動作。  
4. `證據`：路徑、符號、命令結果（精簡）。  
5. `驗證狀態`：已驗證/未驗證與原因。

## 6) 控制平面（Lead Agent 必做）

1. 先分讀寫邊界，再派工。  
2. 指定每個 agent 的「不做事項」。  
3. 只回收摘要，避免上下文污染。  
4. 若結論衝突，由 Lead 做單一裁決。  
5. 對外回覆前先做最終驗證與風險揭露。

## 7) 反模式（避免）

1. 為了平行而平行，導致 token 成本失控。  
2. 提高 `max_depth` 做遞迴派工，造成不可預期 fan-out。  
3. 讓 read-only 角色做實作決策。  
4. 只回報「看起來沒問題」但沒有證據。  
5. 把未驗證輸出直接當最終答案。

## 8) 建議執行流程

```text
需求進入
  -> Lead 定義成功條件與驗證門檻
  -> 判斷是否需要 subagents
     -> 否：單線處理
     -> 是：先派 read-only agent 蒐證
  -> 需要改檔時再派 implementer/test-writer
  -> reviewer/security-reviewer 做獨立把關
  -> Lead 收斂衝突、驗證、交付
```

## 9) 對應本專案設定

- `.codex/config.toml` 維持 `max_depth = 1`，避免遞迴派工風險。
- `.codex/agents/*.toml` 使用窄職責、明確輸出格式與可讀暱稱。
- 預設先讀後寫，先證據後結論，先驗證後交付。
