# OpenAI Codex Workspace

Codex-native workspace template. Provides a ready-to-run ruleset: `AGENTS.md` + `.codex/agents` + `.agents/skills`, adapted from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) for OpenAI Codex.

---

## Quick Start

```bash
# Load core context and start working
codex "請先固定讀取 AGENTS.md、Memory.md、prompts.md；接著讀取 .codex/config.toml；skills 僅按需載入。Karpathy 九條原則視為硬性守則。"
```

---

## Architecture: AGENTS vs SKILL vs Hooks

Based on benchmarking and analysis, **SKILL is the right primitive for caveman compression in Codex**:

| Primitive | Best for | Caveman fit |
|-----------|----------|-------------|
| **SKILL** | On-demand behaviour, user-invocable via `/caveman` | ✅ Best — loaded only when needed, supports lite/full/ultra variants |
| **Hooks** | Always-on side-effects (SessionStart flag, statusline) | ⚠️ Partial — Codex hooks still experimental |
| **AGENTS.md** | Persistent standing rules for every task | ⚠️ Too broad — bakes compression in when not wanted |

**Recommended pattern:** SKILL as primary interface + Hook for SessionStart flag write + AGENTS.md one-liner reference.

---

## Caveman Compression Benchmarks

Real API results — 80 calls, 4 models × 4 levels × 5 technical prompts.
Run: 2026-04-16 00:31 UTC.

> **Note on gpt-5.3-codex:** 所有 `-codex` 模型變體為 completion-only，不支援 `/v1/chat/completions`。
> 最接近的 chat 相容替代為 `gpt-5.2`，以下資料使用 `gpt-5.2` 代替。

### Per-Model Results

#### gpt-5.4

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 435.0 | 291.2 | 7509 | — |
| lite | 426.8 | 293.0 | 7472 | 1.9% |
| full | 430.6 | 265.8 | 6609 | 1.0% |
| ultra | 366.2 | 213.2 | 6553 | **15.8%** |

#### gpt-5.4-mini

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 426.6 | 290.0 | 2967 | — |
| lite | 345.8 | 233.0 | 2284 | 18.9% |
| full | 296.6 | 179.8 | 2183 | **30.5%** |
| ultra | 186.8 | 108.0 | 1647 | **56.2%** |

#### gpt-5.4-nano

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 439.0 | 277.2 | 3146 | — |
| lite | 381.2 | 230.0 | 2709 | 13.2% |
| full | 411.6 | 251.8 | 2859 | 6.2% |
| ultra | 224.0 | 114.0 | 1787 | **49.0%** |

#### gpt-5.3-codex → gpt-5.2 (chat 相容替代)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 468.6 | 280.2 | 7406 | — |
| lite | 430.6 | 263.0 | 8491 | 8.1% |
| full | 328.4 | 185.8 | 6244 | **29.9%** |
| ultra | 254.2 | 128.6 | 4968 | **45.8%** |

### Cross-Model Summary (ultra level)

| Model | Baseline Tokens | Ultra Tokens | Token Reduction | Latency (ms) |
|-------|-----------------|--------------|-----------------|--------------|
| gpt-5.4 | 435.0 | 366.2 | 15.8% | 6553 |
| gpt-5.4-mini | 426.6 | 186.8 | **56.2%** | **1647** |
| gpt-5.4-nano | 439.0 | 224.0 | 49.0% | 1787 |
| gpt-5.3-codex → gpt-5.2 | 468.6 | 254.2 | 45.8% | 4968 |

**Key findings:**
- **gpt-5.4 對 caveman 有抵抗性** — lite/full 幾乎無效（1%），只有 `ultra` 有明顯效果（16%）。模型越大越難覆寫其輸出風格。
- **gpt-5.4-mini 壓縮效果最佳** — `ultra` 達到 56% token 削減，latency 最低（1647ms）。成本敏感型工作流首選。
- **`ultra` 是唯一對 gpt-5.4 有效的等級** — lite/full 建議用在 mini/nano。
- **gpt-5.3-codex 為 completion model**，不能走 chat completions，需用 `gpt-5.2` 代替。

Full raw data: [`benchmarks/results/caveman_benchmark_results.json`](benchmarks/results/caveman_benchmark_results.json)
Full report: [`benchmarks/results/caveman_benchmark_report.md`](benchmarks/results/caveman_benchmark_report.md)

---

## Model Configuration

| Role | Model | Reasoning |
|------|-------|-----------|
| Workspace default | `gpt-5.4` | Cross-module decisions, final convergence |
| Light exploration / docs | `gpt-5.4-mini` | High-frequency reads, cost-efficient |
| Fast nano tasks | `gpt-5.4-nano` | Lowest latency, best compression ratio |
| Implementation / code | `gpt-5.3-codex` | Dense coding work, review, security |

See `.codex/config.toml` for full routing config.

---

## Codex Reading Entry Points

### Session Start (always read)

- `AGENTS.md` — compact rules with Karpathy hard constraints
- `Memory.md` — last-session handoff summary
- `prompts.md` — copy-paste prompt templates (#11–15 Karpathy patterns)

### On-Demand (load only when needed)

| Context | File |
|---------|------|
| Full governance rules | `AGENTS.full.md` |
| Karpathy 9 principles | `docs/karpathy-codex-principles.md` |
| Model routing | `.codex/config.toml` + `.codex/agents/*.toml` |
| Multi-round validated task | `.agents/skills/karpathy-loop/SKILL.md` |
| Multi-agent split work | `.agents/skills/multi-agent-collaboration/SKILL.md` |
| Deep review / major change | `.agents/skills/deep-review/SKILL.md` |
| Doc drift check | `.agents/skills/docs-drift-check/SKILL.md` |
| Session handoff | `.agents/skills/session-handoff/SKILL.md` |
| Cost & token review | `.agents/skills/cost-tracker/SKILL.md` |
| Caveman compression | `.agents/skills/caveman-compress/SKILL.md` |

---

## Skills

| Skill | Trigger | Purpose |
|-------|---------|---------|
| `caveman` | `/caveman [lite\|full\|ultra]` | Token compression 50–92%; intensity-selectable |
| `caveman-commit` | `/caveman-commit` | Compressed conventional commits |
| `caveman-review` | `/caveman-review` | Single-line PR feedback |
| `caveman-compress` | `/caveman:compress <file>` | Compress memory files (AGENTS.md, todos) |
| `karpathy-loop` | `/karpathy-loop` | Declarative validation loop, max 5 rounds / 10 min |
| `multi-agent-collaboration` | task delegation | 3-phase: research → implement → review |
| `deep-review` | major changes | Correctness, regression risk, security |
| `docs-drift-check` | doc divergence | Spec vs implementation drift |
| `session-handoff` | end of session | Structured Memory.md update |
| `cost-tracker` | cost review | Token usage report |
| `blog-analyzer` | doc research | Karpathy/blog → actionable changes |
| `agent-team` | complex tasks | Orchestrated multi-agent team |
| `frontend-design` | UI work | Design-focused agent |

---

## Karpathy Principles (hard constraints)

Full: [`docs/karpathy-codex-principles.md`](docs/karpathy-codex-principles.md)

1. **Assumption Ledger** — every assumption needs a verification method.
2. **Surface, Don't Swallow** — surface conflicts, don't silently resolve them.
3. **Pushback Over Sycophancy** — refuse invalid instructions first, then explain.
4. **Naive-First, Optimize-Second** — minimal correct version before optimization.
5. **Success-Criteria First** — write `Done when` before starting.
6. **Tenacity Loop** — auto-validation loop, max 5 rounds / 10 min.
7. **Minimal Blast Radius** — only touch files in scope.
8. **Anti-Bloat** — no abstractions, params, or options unless required.
9. **Generation vs Discrimination** — major changes must pass reviewer.

---

## Validation Commands

```bash
# Workspace structure check
python3 scripts/validate_codex_workspace.py

# Caveman integration checks
python3 tests/caveman/verify_repo.py
python3 -m unittest -v tests/caveman/test_hooks.py tests/test_caveman_compress.py

# Hooks behaviour tests
python3 -m unittest -v tests/test_codex_hooks_behavior.py

# Sub-agent quality check + token report
python3 scripts/run_subagent_checks.py

# Governance smoke check
rg -n "Assumption Ledger|Anti-Bloat|Generation vs Discrimination" AGENTS.md
rg -n "^## 1[1-5]\." prompts.md

# Run caveman benchmark (requires OPENAI_API_KEY)
OPENAI_API_KEY=<key> python3 benchmarks/caveman_benchmark.py
```

---

## Anti-Timeout Rules

1. Single agent: no output > 200 lines per task.
2. Don't mix long-form generation with git ops in the same agent task.
3. Background agents silent > 5 min → main agent checks proactively.
4. Repo scope: one repo per session. Cross-repo work → new session or isolated branch (`codex/*`).

---

## Directory Layout

```
openai-codex-workspace/
├── AGENTS.md               ← compact rules (session start)
├── AGENTS.full.md          ← full governance rules
├── Memory.md               ← session handoff state
├── prompts.md              ← prompt templates
├── benchmarks/
│   ├── caveman_benchmark.py
│   ├── prompts/en.txt
│   └── results/
│       ├── caveman_benchmark_results.json
│       └── caveman_benchmark_report.md
├── .codex/
│   ├── config.toml
│   ├── agents/             ← per-agent TOML configs
│   └── hooks/
├── .agents/skills/         ← on-demand skills (SKILL.md per skill)
│   └── caveman-compress/
│       └── scripts/        ← caveman memory compression toolchain
├── hooks/caveman/          ← SessionStart + UserPromptSubmit hooks
├── docs/
│   ├── karpathy-codex-principles.md
│   ├── token-usage-report.md
│   └── ...
├── scripts/                ← validation + subagent scripts
└── tests/                  ← hook behaviour tests
```

---

## Migration from claude-code-workspace

| Claude concept | Codex equivalent |
|----------------|------------------|
| `CLAUDE.md` | `AGENTS.md` |
| `.claude/rules/*` | `AGENTS.full.md` sections |
| `.claude/settings.json` hooks | `.codex/hooks.json` + `hooks/` scripts |
| Slash commands | `.agents/skills/*/SKILL.md` |
| `PreCompact`/`PostCompact` | Not available in Codex |
| `autoMemoryEnabled` | Not available; use `Memory.md` + `session-handoff` skill |

---

## Official References

- [AGENTS.md guide](https://developers.openai.com/codex/guides/agents-md)
- [Codex Best Practices](https://developers.openai.com/codex/learn/best-practices)
- [Skills](https://developers.openai.com/codex/concepts/customization#skills)
- [Subagents](https://developers.openai.com/codex/subagents)
- [Hooks](https://developers.openai.com/codex/hooks)
- [Models](https://developers.openai.com/codex/models)
- [Config reference](https://developers.openai.com/codex/config-reference)
- [Caveman source](https://github.com/JuliusBrussee/caveman)
