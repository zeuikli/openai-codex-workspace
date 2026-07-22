# OpenAI Codex Workspace

## 繁體中文

### 概覽

這是一個精簡的 Codex 專案工作區，保留持久指令、The Loop Harness v4、五個 repo-scoped skills、十三個 project-scoped custom agents、hooks 與驗證工具。

唯一 L1 執行契約入口是 [Harness The Loop v4](HARNESS-THE-LOOP.md)，完整 canonical core 在 `the-loop-harness-v4/HARNESS-CORE-v4.md`：`OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD`。L2 校準集中在 `.codex/refs/model-profiles.md` 與 `.codex/profiles.json`，L4 eval 來源是 `the-loop-harness-v4/EVAL-PACK-v4.md` 與 `EVAL-PACK-v4-ADDENDUM.md`。

v4 核心採用 `Agent = Model + Body + Harness`、`[P]/[E]` 可攜性二分、Johari Unknowns、G-LoopA stop conditions 與 cache 五禁令。`[E]` 只代表需要確定性 Body；沒有語義級 hook/CI/gate receipt 時仍是 advisory。

模型路由：

- 主線：provisional `gpt-5.6-luna` + `xhigh` 日常預設；不會依 tiny task 自動降 effort
- Write routes：`cost_write` 使用 Luna medium；`quality_write` 使用 Luna xhigh
- Read-only routes：`quality_explore` 使用 Terra medium；`ceiling_review` 使用 Sol medium；`frontier_security_review` 使用 Sol high
- Router skill：`.agents/skills/multi-mode-skill/SKILL.md`
- GPT-5.5：只保留為 migration calibration baseline，不在 production agent mapping 中。

### Skills 與 Agent

只保留五個 skills：

- ChatGPT pilots：`chatgpt-fast-pilot`、`chatgpt-balanced-pilot`、`chatgpt-deep-pilot`、`chatgpt-frontier-pilot`
- Multi-mode：`multi-mode-skill`

十三個 custom agents 依角色採用 `gpt-5.6-luna`、`gpt-5.6-terra` 或 `gpt-5.6-sol`。研究、審查、安全與架構角色固定 `read-only`；實作、測試、文件、Memory 壓縮與 multi-mode worker 使用 `workspace-write`。

`multi-mode-skill` 使用 benefit-gated 合約驅動委派。必須先有明確使用者要求與具名效益，再以 `scripts/validate_task.py` 驗證 route、canonical contract、repo-relative paths 與 verifier IDs；直接 agent invocation 不具 route 保證。Worker 回報是證據，不是完成判定，主 thread 必須重跑關鍵驗證。

### 核心結構

```text
.
├── AGENTS.md
├── Memory.md
├── HARNESS-THE-LOOP.md
├── LICENSE
├── .codex/
│   ├── config.toml
│   ├── profiles.json
│   ├── refs/model-profiles.md
│   ├── hooks.json
│   ├── agents/*.toml
│   └── hooks/
├── .agents/skills/
│   ├── chatgpt-{fast,balanced,deep,frontier}-pilot/
│   └── multi-mode-skill/
├── the-loop-harness-v4/
├── scripts/validate_codex_workspace.py
└── tests/
```

### 驗證

```bash
python3 scripts/validate_codex_workspace.py
python3 -m pytest tests/ -q
bash -n .codex/hooks/*.sh
git diff --check
```

Validator 會確認只有白名單內五個 skills 與十三個 custom agents 存在，並檢查 Skill metadata、agent model/sandbox、multi-mode deterministic validator、hooks、MIT License，以及阻止 Claude-only runtime 語法與暫存來源回滲。

### 授權

本專案採用 [MIT License](LICENSE)，Copyright (c) 2026 Zeuik Li。

## English

### Overview

This is a focused Codex project workspace containing persistent instructions, The Loop Harness v4, five repo-scoped skills, thirteen project-scoped custom agents, hooks, and validation tooling.

Its sole L1 execution-contract entrypoint is [Harness The Loop v4](HARNESS-THE-LOOP.md), with the canonical core in `the-loop-harness-v4/HARNESS-CORE-v4.md`: `OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD`. L2 calibration lives in `.codex/refs/model-profiles.md` and `.codex/profiles.json`; L4 eval sources are `the-loop-harness-v4/EVAL-PACK-v4.md` and `EVAL-PACK-v4-ADDENDUM.md`.

The v4 core uses `Agent = Model + Body + Harness`, a `[P]/[E]` portability split, Johari unknowns, G-LoopA stop conditions, and cache discipline. `[E]` states a Body dependency; without semantic hook/CI/gate receipts it remains advisory.

Model routing:

- Main thread: provisional `gpt-5.6-luna` + `xhigh` daily default; tiny tasks do not automatically lower effort
- Write routes: Luna medium through `cost_write`; Luna xhigh through `quality_write`
- Read-only routes: Terra medium through `quality_explore`; Sol medium through `ceiling_review`; Sol high through `frontier_security_review`
- Router skill: `.agents/skills/multi-mode-skill/SKILL.md`
- GPT-5.5 is retained only as the migration calibration baseline, not as a production agent mapping.

### Skills and Agents

Only five skills are retained:

- ChatGPT pilots: `chatgpt-fast-pilot`, `chatgpt-balanced-pilot`, `chatgpt-deep-pilot`, and `chatgpt-frontier-pilot`
- Multi-mode: `multi-mode-skill`

The thirteen custom agents use `gpt-5.6-luna`, `gpt-5.6-terra`, or `gpt-5.6-sol` according to role. Research, review, security, and architecture roles are fixed to `read-only`; implementation, test, documentation, memory-compaction, and multi-mode workers use `workspace-write`.

`multi-mode-skill` uses benefit-gated contract-driven delegation. Delegation requires an explicit user request plus a named benefit, then `scripts/validate_task.py` validates the route, canonical contract, repo-relative paths, and verifier IDs; direct agent invocation has no route guarantee. Worker output is evidence, not completion, and the main thread must rerun key verification.

### Core Layout

```text
.
├── AGENTS.md
├── Memory.md
├── HARNESS-THE-LOOP.md
├── LICENSE
├── .codex/
│   ├── config.toml
│   ├── profiles.json
│   ├── refs/model-profiles.md
│   ├── hooks.json
│   ├── agents/*.toml
│   └── hooks/
├── .agents/skills/
│   ├── chatgpt-{fast,balanced,deep,frontier}-pilot/
│   └── multi-mode-skill/
├── the-loop-harness-v4/
├── scripts/validate_codex_workspace.py
└── tests/
```

### Validation

```bash
python3 scripts/validate_codex_workspace.py
python3 -m pytest tests/ -q
bash -n .codex/hooks/*.sh
git diff --check
```

The validator enforces the allowlist of five skills and thirteen custom agents. It also checks skill metadata, agent model/sandbox settings, the deterministic multi-mode validator, hooks, the MIT License, and prevents Claude-only runtime syntax and staging sources from returning.

### License

This project is licensed under the [MIT License](LICENSE), Copyright (c) 2026 Zeuik Li.
