# The Loop Harness v4 — 多模型審閱報告索引

> 審閱日期：2026-07-20
> 審閱範圍：`research/the-loop-harness-v4/` 目錄下核心 .md 文件

## 報告檔案

| 模型 | 檔案 | 整體分 | 審閱重點 |
|------|------|--------|----------|
| Fable 5 | `FABLE5-REVIEW-v4.md` | 8.5 | 整體架構/安全；F7/F15、raw packet、治理 hook |
| ChatGPT 5.6 Sol | `CHATGPT56SOL-REVIEW-v4.md` | 8 | ChatGPT 合規；Responses API 原語映射 |
| ChatGPT 5.5 Pro | `CHATGPT55PRO-REVIEW-v4.md` | 8 | 跨廠商合規；Chat-only fixture、API role precedence |
| Kimi 2.7 | `KIMI27-REVIEW-v4.md` | 8 | 契約完整性與可攜；Johari 證據、SKILL 可攜斷裂 |
| GLM 5.2 | `GLM52-REVIEW-v4.md` | 7.5 | 落地可行性；L3 backlog、Dynamic Workflows |
| DeepSeek V4 Pro | `DEEPSEEK-V4PRO-REVIEW-v4.md` | 8.0 | 獨立全檔；exec 6.5 最嚴；P0–P3 計畫 |
| Grok 4.5 | `GROK45-REVIEW-v4.md` | 8.0 | 獨立全檔；enforce 空心化、紅軸機械化、packet 政策 |

## Before / After（2026-07-20 改寫輪）

| 檔案 | 說明 |
|------|------|
| `BEFORE-AFTER-REREVIEW-2026-07-20.md` | 共識落地後七模型合成再評；Before ~8.0 → After ~8.3；exec 6.5→7.2；**未重跑 fixtures** |

落地摘要：`literal-specialcase-lint` / `blindspot-domain-lint` / `taste-reference-lint` + task-templates 範本六 + CORE/INDEX/SPEC/EVAL 誠實層 + CHATGPT adapter 內嵌 uncalibrated。

## 通用結論摘要

- 整體評分區間：**7.5 – 8.5 / 10**（七份初審）；改寫後合成 **~8.3**。
- 共同最大優點：`[P]`/`[E]` 可攜性二分、MBH 公理、實證存在準則、advisory/enforcement 誠實分界、fixture 驅動評估。
- 初審共同缺口：F7/F15 無 Body、adapter 易誤貼、L3 backlog、raw packet、n=1。
- 改寫後：F7/F15/F19 **advisory lexical Body 已接線**；行為紅軸是否改善 **未測**；#3 Workflows / ChatGPT 實測仍 open。

詳細評分、依據與改善計畫請見各模型報告與 Before/After 檔。
