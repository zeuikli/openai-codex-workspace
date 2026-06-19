# OpenAI Codex Workspace

## 繁體中文

### 概覽

這是一個精簡的 Codex 專案工作區，保留持久指令、Harness、五個 repo-scoped skills、十三個 project-scoped custom agents、hooks 與驗證工具。

唯一執行契約是 [Harness The Loop](HARNESS-THE-LOOP.md)：`OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD`。

模型路由：

- 主線：`gpt-5.5` + `medium`
- Worker：`multi_mode_agent`，固定 `gpt-5.4` + `medium`
- Router skill：`.agents/skills/multi-mode-skill/SKILL.md`

### Skills 與 Agent

只保留五個 skills：

- ChatGPT pilots：`chatgpt-fast-pilot`、`chatgpt-balanced-pilot`、`chatgpt-deep-pilot`、`chatgpt-frontier-pilot`
- Multi-mode：`multi-mode-skill`

十三個 custom agents 依角色採用 `gpt-5.4-mini`、`gpt-5.4` 或 `gpt-5.5`。研究、審查、安全與架構角色固定 `read-only`；實作、測試、文件、Memory 壓縮與 multi-mode worker 使用 `workspace-write`。

`multi-mode-skill` 使用合約驅動委派。委派前必須以 `scripts/validate_task.py` 驗證完整 task envelope，不支援直接叫用 worker。

### 核心結構

```text
.
├── AGENTS.md
├── Memory.md
├── HARNESS-THE-LOOP.md
├── LICENSE
├── .codex/
│   ├── config.toml
│   ├── hooks.json
│   ├── agents/*.toml
│   └── hooks/
├── .agents/skills/
│   ├── chatgpt-{fast,balanced,deep,frontier}-pilot/
│   └── multi-mode-skill/
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

This is a focused Codex project workspace containing persistent instructions, a Harness, five repo-scoped skills, thirteen project-scoped custom agents, hooks, and validation tooling.

Its sole execution contract is [Harness The Loop](HARNESS-THE-LOOP.md): `OBSERVE → IDENTIFY → PROPOSE → APPLY → TEST → RECORD`.

Model routing:

- Main thread: `gpt-5.5` + `medium`
- Worker: `multi_mode_agent`, fixed to `gpt-5.4` + `medium`
- Router skill: `.agents/skills/multi-mode-skill/SKILL.md`

### Skills and Agents

Only five skills are retained:

- ChatGPT pilots: `chatgpt-fast-pilot`, `chatgpt-balanced-pilot`, `chatgpt-deep-pilot`, and `chatgpt-frontier-pilot`
- Multi-mode: `multi-mode-skill`

The thirteen custom agents use `gpt-5.4-mini`, `gpt-5.4`, or `gpt-5.5` according to role. Research, review, security, and architecture roles are fixed to `read-only`; implementation, test, documentation, memory-compaction, and multi-mode workers use `workspace-write`.

`multi-mode-skill` uses contract-driven delegation. Before delegation, `scripts/validate_task.py` must validate the complete task envelope; direct worker invocation is unsupported.

### Core Layout

```text
.
├── AGENTS.md
├── Memory.md
├── HARNESS-THE-LOOP.md
├── LICENSE
├── .codex/
│   ├── config.toml
│   ├── hooks.json
│   ├── agents/*.toml
│   └── hooks/
├── .agents/skills/
│   ├── chatgpt-{fast,balanced,deep,frontier}-pilot/
│   └── multi-mode-skill/
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
