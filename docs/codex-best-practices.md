# Codex Best Practices（落地版）

來源：<https://developers.openai.com/codex/learn/best-practices>  
更新基準：2026-04-14

## 1) 先把任務講清楚（最小四段）

每次任務至少提供：

- Goal：要改什麼、達成什麼結果
- Context：相關檔案、錯誤訊息、範例或路徑
- Constraints：不可違反的規範、架構與安全要求
- Done when：完成判定（測試通過、行為改變、bug 不可重現）

## 2) 複雜任務先規劃，再實作

- 高不確定任務先用 `/plan`。
- 若需求含糊，先讓 Codex 反問你、澄清後再動工。
- 長流程可搭配執行計畫模板（例如 `PLANS.md` 類型文件）。

## 3) 把重複規則放進 `AGENTS.md`

- `AGENTS.md` 放持久規範，不要每次重打 prompt。
- 內容保持短、準、可執行：專案結構、測試命令、限制、完成定義。
- 規則要分層：全域（`~/.codex`）→ repo → 子目錄（越近越優先）。

## 4) 用 `config.toml` 提升一致性

- 個人預設放 `~/.codex/config.toml`。
- 專案行為放 `.codex/config.toml`。
- 一次性需求才用 CLI 覆寫。

建議先保守權限，再逐步放寬（approval / sandbox 以最小必要原則）。

## 5) 要求 Codex 完成「實作 + 驗證 + 審查」閉環

不要只要求「改完程式碼」，同時要求：

- 補或更新測試
- 跑相關檢查（test/lint/type/build）
- 檢查最終行為是否符合需求
- 審查 diff 的回歸風險與高風險模式

## 6) 外部上下文優先用 MCP

當資料在 repo 外且變動頻繁時，優先用 MCP，不要靠手動貼資料。

- 先接 1~2 個真正能省流程的工具
- 穩定後再擴充，不要一次接滿所有工具

## 7) 重複工作先 Skill，穩定後再 Automation

- 先把方法固化成 Skill（`SKILL.md`）。
- 流程穩定後再建立 Automation 排程。
- 記法：**Skills 定義方法，Automations 定義排程**。

## 8) 長任務管理：一個 thread 一個工作單元

- 同一問題持續在同 thread，保留推理脈絡。
- 真正分岔才 fork。
- 需要平行時用 subagents 做有邊界的小任務，把主線留給決策整合。

## 9) 常見錯誤（避免）

- 把持久規則塞在單次 prompt，沒寫進 `AGENTS.md`
- 沒提供可執行的 build/test 命令
- 多步驟任務不先規劃
- 過早給過寬權限
- workflow 還不穩就排程 automation
- 單一 thread 混太多不相干任務，造成上下文膨脹

