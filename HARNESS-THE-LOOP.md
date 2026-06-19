# Harness The Loop

改進、稽核、除錯與迭代任務的唯一執行契約：

**OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD**

每一階段都對應常見失敗模式，並盡量以可機械驗證的證據完成。

## OBSERVE — 先讀後動

- 修改前讀取目標範圍、直接 caller、共用 utility、測試與目前 git diff。
- 不清楚現有設計原因時先查證，不用「應該沒問題」代替證據。
- 工具輸出被截斷時分段續讀，標示尚未檢查的範圍。
- 生產環境操作先取得 plan 或 diff，不直接 apply、deploy 或 delete。

## IDENTIFY — 顯露假設與成功條件

- 用不超過兩句話寫出需求詮釋，不複述 prompt。
- 列出會改變結果的假設，並為每項附上檢驗方式。
- 小型等價決策自行採保守預設；scope、資料或不可逆決策必須顯化。
- 開工前定義可執行或可觀測的 Done when。
- 成功條件同時考量 correctness、security、reliability、maintainability。

## PROPOSE — 最小且可驗證

- 選擇能解決問題的最小方案，不投機加入功能或未來抽象。
- 單次使用不抽 helper；重複與複雜度確實存在時才抽象。
- 主動檢查 bloated、copy-paste、brittle 與 awkward abstraction。
- 任務外問題只記錄為 Followup，不混入本次修改。
- 安全敏感邏輯使用標準且集中管理的實作，不自行發明原語。

## APPLY — 慣例優先與破壞性 Gate

- Codebase 既有慣例優先於個人偏好；有害慣例另行揭露，不靜默分叉。
- 只改需求直接涉及的最小範圍，保留使用者既有工作樹修改。
- `DELETE`、`DROP`、prod deploy、key rotation、`rm -rf`、force push 等不可逆操作，執行前顯示摘要並取得明確同意。
- 執行中若證據否定原方向，回到失敗階段重新判斷，不硬撐原方案。

## TEST — 驗證意圖並 Fail Loud

- 測試必須能在目標行為錯誤時失敗；優先測業務意圖而非實作細節。
- 靜態檢查、lint 或 type check 不等於端到端執行。
- 宣告完成前親自執行最相關的確定性驗證，不能只引用自述成功。
- 失敗時保留完整錯誤與重現命令；搜尋截斷時標示顯示數量與總範圍。

## RECORD — Checkpoint 與可接續狀態

- 每個重要里程碑記錄：做了什麼、驗了什麼、剩下什麼。
- 任務失敗時記錄失敗模式、被否證假設與下次可機械檢查的改善。
- 完成時更新 `Memory.md`：結果、決策、驗證、殘餘風險。
- 無法清楚描述當前狀態時，先停止並重建 checkpoint。

## 跨階段紀律

- 模型適合判斷、摘要與生成；確定性程式負責路由、計算、驗證與狀態碼。
- 兩個模式互相矛盾時不混用：先列證據、選擇理由與風險。
- 優先序：明確規格與 ADR → repo 規範 → 測試與近期程式慣例。
- Done when 未達成就不宣告完成；無法達成時標記 Blocked 並說明證據。
