# Memory.md

## 繁體中文

### 最後紀錄（2026-07-13）

- 已依 OpenAI GPT-5.6 官方模型分級與使用者提供的任務效益表，將主線、五個 pilot skills、`multi-mode-skill`、十三個 custom agents、`.codex/profiles.json`、`.codex/refs/model-profiles.md`、README、validator 與測試的模型 mapping 從 GPT-5.4/5.5 更新為 GPT-5.6。
- 新 mapping：微小/低風險任務使用 `gpt-5.6-luna` + `medium`；日常實作、測試、review 與 multi-mode worker 使用 `gpt-5.6-luna` + `xhigh`；廣泛唯讀探索使用 `gpt-5.6-terra` + `medium`；架構、auth、migration 與高風險 review 使用 `gpt-5.6-sol` + `medium`；完整安全稽核與最高風險情境使用 `gpt-5.6-sol` + `high`。
- `HARNESS-THE-LOOP.md` 的 v3 L1 契約維持模型無關；L2 模型分級集中在 `.codex/profiles.json` 與 `.codex/refs/model-profiles.md`。
- 殘餘風險：本次是 routing、文件與 validator/test 更新；尚未用 5-10 個代表任務量測新 mapping 的實際成功率、成本與 latency。

### 最後紀錄（2026-07-09）

- 已將 `the-loop-harness-v3/` 改寫進 workspace：`HARNESS-THE-LOOP.md` 升級為 v3 L1 行為契約，`AGENTS.md` 改為 v3-aware 持久規範，`README.md` 補上 L1/L2/L4 分層。
- 已新增 L2 對應：`.codex/refs/model-profiles.md`（人讀）與 `.codex/profiles.json`（機讀 wired SSoT），映射 v3 profiles 與 `the-loop-harness-v3/EVAL-PACK.md` fixtures。
- 已加嚴 `multi-mode-skill` task envelope：新增 `context`、`return_schema`、`delegation_benefit`，並明定 worker 自報成功是 `unverified_success`。
- 已同步 validator 與測試，要求 v3 profile 檔、benefit-gated marker、eval fixtures 與新 task envelope 欄位。
- 殘餘風險：本次未合併四個 pilot skill，也未全面重寫十三個 custom agent 的 developer instructions；若要完全落地 `SPEC-v3.md` 的 agent/skill 合併，需另開工作單元並跑完整 eval/validator。

### 最後紀錄（2026-07-03）

- 已將簡報中的 Instant prompt 模板製作成可攜帶附件：`outputs/pdf/instant-prompt-template-card.pdf`、`outputs/pdf/instant-prompt-template-card.png`、`outputs/instant-prompt-template.txt`。
- 2026-07-03 已依使用者提供的 OpenAI Help Center `ChatGPT Rate Card (Business, Enterprise/Edu)` 更新簡報與隨身卡：GPT-5.5 Instant 為 `N/A - Unlimited`，但複雜任務可能 auto-select Thinking，按 GPT-5.5 Thinking rate `10 credits/message` 計；已把「為什麼要善用 ChatGPT 5.5 Instant」納入簡報第 8 頁。
- PDF 已用 Poppler 渲染成 PNG 並視覺檢查；2026-07-03 已修正左側說明卡跑版，純文字版已確認可直接貼用。
- 已 fast-forward `main` 到 `origin/main` commit `6157b5e`，確認舊 caveman skills/scripts/tests 已從 main 移除。
- 已重新製作 main branch 版簡報：`outputs/codex-workspace-how-to-main.pptx`。
- 新版內容依據目前 main：`AGENTS.md`、`HARNESS-THE-LOOP.md`、`README.md`、`.codex/config.toml`、五個 `.agents/skills/*/SKILL.md`、十三個 `.codex/agents/*.toml`，以及 OpenAI Codex manual / pricing / speed / models 官方文件。
- 驗證完成：Artifact Tool 匯出 PPTX；`slides_test.py` 通過無 overflow；`render_slides.py` 成功渲染 10 張；contact sheet 已視覺抽查。
- 注意：上一版簡報與 Memory 修改已暫存在 git stash `codex-stash-old-workspace-deck-before-main-refresh`，未回套，以避免舊內容污染 main。

### 最後紀錄（2026-06-19）

- Workspace 只保留五個 repo-scoped Skills：`chatgpt-fast-pilot`、`chatgpt-balanced-pilot`、`chatgpt-deep-pilot`、`chatgpt-frontier-pilot` 與 `multi-mode-skill`。
- 保留十三個 custom agents；`multi-mode-skill` 採合約驅動委派，主 thread 使用 `gpt-5.5`，明確要求委派時才由固定 `gpt-5.4` 的 `multi_mode_agent` 執行完整 `PROFILE_CONTRACT`。
- 專案採用 MIT License，Copyright (c) 2026 Zeuik Li。
- 五個 Skills 均通過官方 `quick_validate.py`；workspace validator、hook syntax、`git diff --check` 與完整測試 `36 passed`。
- 發布 repo 是 `zeuikli/openai-codex-workspace`，分支為 `codex/publish-five-skill-workspace`，並透過 Draft PR 合併至 `main`。

### 待辦與殘餘風險

- 無新增待辦；需保留或刪除舊 stash 可由使用者後續決定。

## English

### Last Record (2026-07-13)

- Updated model mappings from GPT-5.4/5.5 to GPT-5.6 across the main thread, five pilot skills, `multi-mode-skill`, thirteen custom agents, `.codex/profiles.json`, `.codex/refs/model-profiles.md`, README, validator, and tests, using OpenAI GPT-5.6 model guidance plus the user's task-benefit routing table.
- New mapping: tiny/low-risk tasks use `gpt-5.6-luna` + `medium`; daily implementation, testing, review, and the multi-mode worker use `gpt-5.6-luna` + `xhigh`; broad read-only exploration uses `gpt-5.6-terra` + `medium`; architecture, auth, migration, and high-risk review use `gpt-5.6-sol` + `medium`; full security audits and maximum-risk work use `gpt-5.6-sol` + `high`.
- `HARNESS-THE-LOOP.md` remains the model-agnostic v3 L1 contract; L2 model routing is centralized in `.codex/profiles.json` and `.codex/refs/model-profiles.md`.
- Residual risk: this is a routing, documentation, validator, and test update. The new mapping has not yet been measured on 5-10 representative tasks for success rate, cost, or latency.

### Last Record (2026-07-09)

- Rewrote `the-loop-harness-v3/` into the workspace: upgraded `HARNESS-THE-LOOP.md` to the v3 L1 behavior contract, made `AGENTS.md` v3-aware, and added the L1/L2/L4 layering to `README.md`.
- Added L2 mapping files: `.codex/refs/model-profiles.md` for humans and `.codex/profiles.json` as the machine-readable wired SSoT, mapping v3 profiles and `the-loop-harness-v3/EVAL-PACK.md` fixtures.
- Tightened the `multi-mode-skill` task envelope with `context`, `return_schema`, and `delegation_benefit`, and recorded worker self-reported success as `unverified_success`.
- Updated the validator and tests to require v3 profile files, benefit-gated markers, eval fixtures, and the new task envelope fields.
- Residual risk: this pass did not merge the four pilot skills or fully rewrite the thirteen custom agent developer instructions. Full `SPEC-v3.md` agent/skill consolidation should be handled as a separate work unit with full eval and validator coverage.

### Last Record (2026-07-03)

- Converted the Instant prompt template into portable artifacts: `outputs/pdf/instant-prompt-template-card.pdf`, `outputs/pdf/instant-prompt-template-card.png`, and `outputs/instant-prompt-template.txt`.
- On 2026-07-03, updated the deck and card using the user-provided OpenAI Help Center `ChatGPT Rate Card (Business, Enterprise/Edu)`: GPT-5.5 Instant is `N/A - Unlimited`, but complex tasks may auto-select Thinking and be charged at the GPT-5.5 Thinking rate of `10 credits/message`; added "why to use ChatGPT 5.5 Instant well" to slide 8.
- Rendered the PDF through Poppler for visual inspection; fixed the left-side card layout overflow on 2026-07-03; verified the text template is directly pasteable.
- Fast-forwarded `main` to `origin/main` commit `6157b5e`; confirmed old caveman skills/scripts/tests are removed from main.
- Recreated the main-branch presentation at `outputs/codex-workspace-how-to-main.pptx`.
- New deck is based on current main: `AGENTS.md`, `HARNESS-THE-LOOP.md`, `README.md`, `.codex/config.toml`, five `.agents/skills/*/SKILL.md` files, thirteen `.codex/agents/*.toml` files, and official OpenAI Codex manual / pricing / speed / models docs.
- Verification completed: Artifact Tool exported the PPTX; `slides_test.py` passed with no overflow; `render_slides.py` rendered 10 slides; contact sheet was visually inspected.
- Note: the prior deck and Memory changes were stashed as `codex-stash-old-workspace-deck-before-main-refresh` and not reapplied, to avoid reintroducing stale content.

### Last Record (2026-06-19)

- The workspace retains only five repo-scoped skills: `chatgpt-fast-pilot`, `chatgpt-balanced-pilot`, `chatgpt-deep-pilot`, `chatgpt-frontier-pilot`, and `multi-mode-skill`.
- Thirteen custom agents remain. `multi-mode-skill` uses contract-driven delegation: the main thread runs `gpt-5.5`, and only an explicit delegation request may send a complete `PROFILE_CONTRACT` to the fixed `gpt-5.4` `multi_mode_agent`.
- The project uses the MIT License, Copyright (c) 2026 Zeuik Li.
- All five skills pass the official `quick_validate.py`; the workspace validator, hook syntax, `git diff --check`, and the full test suite with `36 passed` all succeed.
- The publishing repository is `zeuikli/openai-codex-workspace`, the branch is `codex/publish-five-skill-workspace`, and changes merge into `main` through a draft pull request.

### Remaining Actions and Risks

- No new follow-up. Keep or drop the old stash by user decision.
