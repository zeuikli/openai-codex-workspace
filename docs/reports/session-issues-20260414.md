# Session 問題紀錄與優化建議

- **記錄日期**：2026-04-14
- **Session 目標**：方案 C Terraform 優化 + 使用手冊撰寫
- **分析者**：Claude Sonnet 4.6

---

## 問題一：Agent 逾時浪費 token（高優先）

### 發生情況
指派 Agent 撰寫完整使用手冊（12 章節繁體中文 + commit + push），Agent 執行 **29 分鐘後逾時**，消耗 7,950 tokens，**產出為零**。

### 根本原因
任務粒度過大，單一 Agent 被要求同時完成：
1. 讀取 40+ 個 `.tf` 檔案做內容分析
2. 撰寫 12 個章節的長篇文件
3. 執行 git commit + push

Agent 的強項是「工具密集型探索」，弱點是「長篇生成性寫作」。主 Claude 直接執行寫作任務反而更快且不會逾時。

### 建議優化
在 `.agents/skills/` 或 `AGENTS.md` 加入以下規則：

```markdown
## Agent 任務邊界（Anti-pattern）

- ❌ 不得指派 Agent 撰寫超過 200 行的文件
- ❌ 不得在單一 Agent prompt 同時包含「生成」+「git 操作」兩類任務
- ✅ 長文件由主 Claude 直接撰寫
- ✅ Agent 只做：探索、搜尋、平行讀取、單一函數實作
- ✅ 任務上限估算：預期工具呼叫 < 20 次 / 預期輸出 < 500 tokens
```

---

## 問題二：MCP 工具與 Git Proxy 限制在單一 Repo（中優先）

### 發生情況
使用者要求將分支 fork 到 `zeuikli/claude-code-workspace`，但：
- `mcp__github__*` 工具回傳：`Access denied: repository not configured for this session`
- Git proxy 回傳：`remote: Proxy error: repository not authorized`

Session 被硬性限制在 `zeuikli/openai-codex-workspace` 單一 repo。

### 影響
需要繞路改為「在同 repo 建立隔離分支」，增加溝通成本並限制架構選擇。

### 建議優化
在 `AGENTS.md` 或 `README.md` 加入明確說明：

```markdown
## Session Repo 限制

每個 Claude Code session 只能存取啟動時綁定的單一 repository。
跨 repo 操作（fork、cross-repo push）需在目標 repo 開新 session。

替代方案：在同 repo 建立 `claude/xxx-isolated` 隔離分支進行實驗性工作。
```

---

## 問題三：Stop Hook 在 Agent 執行期間觸發（中優先）

### 發生情況
背景 Agent 尚未 commit 時，stop hook (`~/.claude/stop-hook-git-check.sh`) 偵測到未提交變更並要求處理，導致主 Claude 需要插入 commit/push 流程，打斷作業連續性。

### 根本原因
Stop hook 無法感知「有背景 Agent 正在進行中」，誤判為遺漏提交。

### 建議優化
兩個方向擇一：

**方向 A**：Stop hook 加入 Agent 執行狀態感知
```bash
# ~/.claude/stop-hook-git-check.sh 建議邏輯
# 若有背景 agent 正在執行，跳過 uncommitted 檢查
```

**方向 B**：主 Claude 在指派背景 Agent 前，先 commit 現有變更
在 `AGENTS.md` 加入：
```markdown
## 背景 Agent 指派前置規則
指派背景 Agent 前，必須先 commit 並 push 當前所有變更，
避免 stop hook 在 Agent 執行期間誤觸發。
```

---

## 問題四：Agent 任務缺乏逾時保護與失敗通知機制（低優先）

### 發生情況
Agent 靜默執行 29 分鐘，使用者需要主動追問才知道是否仍在執行，過程中無進度訊號。

### 建議優化
在 `AGENTS.md` 加入以下規則：

```markdown
## 背景 Agent 管理原則

- 指派背景 Agent 後，立即告知使用者：任務內容、預計完成時間、失敗通知方式
- 超過 5 分鐘未完成的 Agent，主 Claude 主動確認狀態
- Agent 失敗（逾時/錯誤）必須立即通知使用者，不得靜默略過
- 複雜任務優先評估「主 Claude 直接執行」vs「指派 Agent」的 token 效益
```

---

## 問題五：環境層 variables.tf 缺乏與 platform_stack 的完整對應（已修正）

### 發生情況
原始 `environments/*/variables.tf` 缺少 `cloud_run_cpu`、`cloud_run_memory`、`mysql_tier`、`kafka_topics` 等重要變數，導致使用者無法從環境層客製化這些參數。

### 根本原因
平台模組（`platform_stack`）與環境層薄包裝（thin wrapper）之間的介面沒有系統性維護，新增 platform 變數時未同步更新環境層。

### 建議優化
在 `terraform-optimized/` 加入驗證腳本或 CI check：

```bash
# 檢查 platform_stack/variables.tf 與 environments/dev/variables.tf 的變數是否對齊
# 建議加入 scripts/validate_terraform_interface.py
```

---

## 摘要：建議加入 AGENTS.md 的三條規則

```markdown
## Agent 任務邊界（新增）
1. 長文件（> 200 行）由主 Claude 直接撰寫，不透過 Agent。
2. 背景 Agent 指派前，先 commit + push 當前所有變更。
3. Agent 超過 5 分鐘未回報，主 Claude 主動評估是否接手。
```

---

*紀錄生成時間：2026-04-14 | Claude Sonnet 4.6*
