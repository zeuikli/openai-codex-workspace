---
name: karpathy-loop
description: 把任務轉為「宣告式成功條件 + 自動驗證迴圈」的執行流程，用最少回合壓到 Done when 全綠。
---

# Karpathy Loop

## Use when

- 任務具備可自動化的驗證訊號（tests / lint / typecheck / build / e2e）。
- 需求可以用可執行指令或可觀測行為表達為 `Done when`。
- 任務可能需要多輪修補，但不涉及高風險單點變更。

## Do not use when

- 沒有可自動驗證的訊號，只能靠人眼判斷。
- 變更觸及資料遷移、金鑰、生產設定，需要單線謹慎控管。
- 需求仍模糊 → 先走 `docs-drift-check` 或澄清問答。

## Workflow

1. **把需求翻成 Done when**
   - 列出每個條件對應的驗證指令或觀測點。
   - 條件不可執行就不能進 loop，回頭澄清或補測試。
2. **建立 reproducible 指令**
   - 指令應能在乾淨環境一次完成（`make test` / `pnpm test` / `pytest -q` 等）。
   - 記錄輸出尾段作為「失敗指紋」比對，避免誤判通過。
3. **進入迴圈**
   - 上限：預設 5 輪或 10 分鐘（以先到者為準）。
   - 每輪回報：`diff 摘要` + `驗證輸出尾段 (≤20 行)` + 下一步假設。
   - 禁止回貼完整舊上下文；上下文靠 Memory.md 與回合摘要維護。
4. **停機條件**
   - 所有 Done when 綠燈 → 進入收尾。
   - 連續兩輪錯誤指紋相同 → 停下並升級 reasoning 或回報人類。
   - 發現需求本身有誤 → 停下並顯化衝突（Surface, Don't Swallow）。
5. **收尾**
   - 列出「最後一次綠燈」的驗證輸出摘要。
   - 更新 `Memory.md`：本輪結論、剩餘風險、Followup。
   - 若出現任何 Followup（看不懂的註解、死碼、意外耦合），記下不處理。

## Quality Gate

- 禁止以修改測試預期、`@skip`、改錯誤訊息的方式讓驗證變綠。
- 每輪 diff 必須貼合一個語意；混雜多目的的 diff 要拆 commit。
- 超出上限仍未綠燈時，不得宣告完成；必須回報阻塞。
- 與 `reviewer` 搭配：重大變更在 loop 結束後強制走 `deep-review`。

## Output Contract

```text
## Loop Summary
- Goal: <一句話>
- Done when:
  - [x] <條件 1> (驗證指令 / 觀測點)
  - [ ] <條件 2>
- Rounds used: <N/5>
- Final verification tail:
  ```
  <測試輸出最後 10~20 行>
  ```
- Assumptions:
  - Verified: ...
  - Unverified: ...
- Followups:
  - ...
- Risks:
  - ...
```
