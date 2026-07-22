# ChatGPT 5.5 Pro AFTER 再審 — 2026-07-21

## 整體分數

**R2 After：8.6/10**（文件就緒度；可進 controlled experiments，不是 production / calibration-complete 分數）。

核心理由：原先 8 個 ChatGPT surface blocker 已在 `CHATGPT-HARNESS-v4.md` 內被明確拆分、降級或補上操作協議；`ADOPTION-GUIDE-v4.md` 與 `GLOSSARY-v4.md` 也補齊採用與詞彙入口。但 `CHATGPT-HARNESS-v4.md:3`、`:138`、`:194` 仍明確標示三個 ChatGPT surface 實跑 baseline = 0，所以 calibration completion 仍不可過關。

## Before → R1 → R2

| Round | Overall | 判讀 |
|---|---:|---|
| BEFORE | 8.0/10 | 架構方向正確，但 ChatGPT chat-only/API surface 校準、role precedence、Codex/Responses 邊界、Memory/tool/privacy/Evals 等容易過度外推。 |
| R1 After | ~8.3/10 | 已開始補 surface-aware 邊界與降級語言，但仍需確認 8 個 blocker 是否都落到可引用條文。 |
| R2 After | 8.6/10 | 8 個 blocker 文件層大多 CLOSED；剩下主要是 #14 zero-run baseline，故只達「實驗文件就緒」，不到「校準完成／production-ready」。 |

## Calibration readiness 判決 (still NOT READY / document-ready for experiments?)

**Still NOT READY for calibration completion.**
**Document-ready for controlled experiments.**

判決依據：

- `CHATGPT-HARNESS-v4.md:3` 開宗明義標 `uncalibrated/advisory`，且三 surface 實測基線數 = 0。
- `CHATGPT-HARNESS-v4.md:155-162` 已補上 chat-only operational calibration protocol，可操作性已足以啟動 transcript + external runner 實驗。
- `CHATGPT-HARNESS-v4.md:138-153` 把 #14 明確留 open，並要求三 surface 分開 baseline、外部 verifier receipt、PASS/FAIL/UNTESTED/TAINTED 分離與 Evals oracle qualification。
- `ADOPTION-GUIDE-v4.md` 已明確告知 ChatGPT adapter 是 `uncalibrated/advisory`，#14 結案前不得宣稱 ChatGPT surface 已驗證。
- `GLOSSARY-v4.md` 已補齊 `[P]/[E]`、advisory/enforce、`unverified_success`、fixture、紅軸等詞彙入口。

## 原改善項 CLOSED/PARTIAL/OPEN table

| # | 原改善項 | R2 狀態 | 佐證與殘餘風險 |
|---:|---|---|---|
| 1 | chat-only calibration protocol operational | CLOSED（文件層） | `CHATGPT-HARNESS-v4.md:155-162` 已列 5 步 protocol；但未實跑，仍歸 #14。 |
| 2 | developer role placement | CLOSED | `CHATGPT-HARNESS-v4.md:32-43` 與 `:123-126` 明確將 Responses API stable core 放 `developer`，`user/tool/memory` 降為資料。 |
| 3 | Codex vs Responses split | CLOSED | `CHATGPT-HARNESS-v4.md:11`、`:22`、`:136`、`:187-189` 明確禁止把 Codex/CLI baseline pooling 到 ChatGPT/Responses。 |
| 4 | routing overconfident → uncalibrated experiment + `as_of` decay | CLOSED | `CHATGPT-HARNESS-v4.md:104-117` 改成未校準 experiment plan，並要求 `as_of` 與 decay 重評。 |
| 5 | Memory cross-session injection | CLOSED | `CHATGPT-HARNESS-v4.md:32`、`:42`、`:180`、`:196` 將 Memory 定義為 untrusted cross-session injection surface。 |
| 6 | auto-tool-routing | CLOSED（文件層） | `CHATGPT-HARNESS-v4.md:12`、`:19`、`:116`、`:143`、`:195` 要求只採信實際 receipt；實際 tool trace 仍待 calibration run。 |
| 7 | secrets/PII | CLOSED | `CHATGPT-HARNESS-v4.md:35`、`:127`、`:197` 已加入資料保留/訓練政策確認與 redaction/storage guard。 |
| 8 | OpenAI Evals pointer | CLOSED（pointer-only） | `CHATGPT-HARNESS-v4.md:144`、`:153` 已指向 Evals 可作外部 runner，但明確不等於已整合，oracle 仍需 qualification。 |
| 9 | ADOPTION-GUIDE exists | CLOSED | `ADOPTION-GUIDE-v4.md` 存在，且開頭說明採用路徑與誠實聲明。 |
| 10 | GLOSSARY exists | CLOSED | `GLOSSARY-v4.md` 存在，且定位為 describe-only 詞彙入口。 |

## 仍 open

- **#14 zero runs**：ChatGPT `chat-only`、`tool-enabled`、`Responses API` 三 surface 仍無 F1–F22 baseline；這是 calibration completion 的硬 blocker。
- **Production readiness**：目前只可說 document-ready for experiments；不得宣稱 ChatGPT/GPT-5.6 已校準、紅軸已解或可 production adoption。
- **Runtime receipts**：auto-tool-routing、Responses API primitive mapping、OpenAI Evals runner 與 oracle qualification 都還需要實際 request/response、tool trace、artifact hash、exit code 與 verifier receipt。

## 一句結論

R2 我給 **8.6/10**：文件已足夠啟動 ChatGPT surface 實驗，但因 #14 三 surface zero-run baseline 仍 open，校準完成判決仍是 **NOT READY**。

`unverified_success`
