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

Real API results — **80 calls total**, 4 models × 4 levels × 5 technical prompts.
Run: **2026-04-16 01:12 UTC** (live, no dry-run).

> **gpt-5.3-codex** 為 completion model，透過 **Responses API** (`/v1/responses`) 測試，其餘模型走 Chat Completions API。

### Per-Model Results

#### gpt-5.4

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|----------------|-----------|------------------|-----------------|
| none (baseline) | 434.8 | 283.2 | 8080 | — |
| lite | 420.6 | 291.4 | 7708 | 3.3% |
| full | 410.0 | 257.0 | 7541 | 5.7% |
| ultra | 377.8 | 229.4 | 7323 | **13.1%** |

#### gpt-5.4-mini

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|----------------|-----------|------------------|-----------------|
| none (baseline) | 403.4 | 270.8 | 2950 | — |
| lite | 355.2 | 241.2 | 2853 | 11.9% |
| full | 295.8 | 182.6 | 2538 | **26.7%** |
| ultra | 196.0 | 106.4 | 2409 | **51.4%** |

#### gpt-5.4-nano

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|----------------|-----------|------------------|-----------------|
| none (baseline) | 445.2 | 279.0 | 3670 | — |
| lite | 357.2 | 220.4 | 2892 | 19.8% |
| full | 392.6 | 240.4 | 3488 | 11.8% |
| ultra | 217.2 | 120.4 | 2014 | **51.2%** |

#### gpt-5.3-codex (Responses API)

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|----------------|-----------|------------------|-----------------|
| none (baseline) | 369.8 | 227.2 | 6640 | — |
| lite | 346.2 | 211.6 | 6726 | 6.4% |
| full | 347.0 | 203.6 | 6524 | 6.2% |
| ultra | 296.8 | 150.4 | 6292 | **19.7%** |

### Cross-Model Summary

| Model | None (baseline) | lite | full | ultra | Best reduction | Latency@full |
|-------|----------------|------|------|-------|----------------|---------------|
| gpt-5.4 | 435 tok | 3.3% | 5.7% | 13.1% | **13.1%** | 7541ms |
| gpt-5.4-mini | 403 tok | 11.9% | 26.7% | 51.4% | **51.4%** | 2538ms |
| gpt-5.4-nano | 445 tok | 19.8% | 11.8% | 51.2% | **51.2%** | 3488ms |
| gpt-5.3-codex | 370 tok | 6.4% | 6.2% | 19.7% | **19.7%** | 6524ms |

**Key findings:**
- 🏆 **gpt-5.4-mini + ultra** 最佳壓縮（51.4%）且延遲第二低（2409ms）。
- ⚡ **gpt-5.4-nano + ultra** 壓縮相近（51.2%）且延遲最低（2014ms）——速度優先選擇。
- 🧠 **gpt-5.4 對 caveman 較有抵抗性**，lite/full 效果有限（3–6%），ultra 才達 13%。
- 📡 **gpt-5.3-codex** 須用 Responses API，壓縮響應弱於其他模型（ultra 才 19.7%）。
- 💡 **成本＋壓縮最優解**：`gpt-5.4-mini + ultra` 或 `gpt-5.4-nano + ultra`。

Full report: [`benchmarks/results/caveman_benchmark_report.md`](benchmarks/results/caveman_benchmark_report.md)
Raw JSON: [`benchmarks/results/caveman_benchmark_results.json`](benchmarks/results/caveman_benchmark_results.json)

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

## Validation & Commands

```bash
# ── Session bootstrap ──────────────────────────────────────────────────────
# Standard Codex session start
codex "請先固定讀取 AGENTS.md、Memory.md、prompts.md；再讀 .codex/config.toml；skills 按需載入。"

# ── Workspace structure ────────────────────────────────────────────────────
python3 scripts/validate_codex_workspace.py

# ── Caveman integration ────────────────────────────────────────────────────
python3 tests/caveman/verify_repo.py              # repo layout + compress + CLI checks
python3 -m unittest -v tests/caveman/test_hooks.py  # JS hook tests (requires Node.js)
python3 -m unittest -v tests/test_caveman_compress.py  # Python compress unit tests

# ── Core behaviour tests ───────────────────────────────────────────────────
python3 -m unittest -v tests/test_codex_hooks_behavior.py
python3 -m unittest -v tests/test_subagent_checks.py

# ── Subagent quality & token report ───────────────────────────────────────
python3 scripts/run_subagent_checks.py
python3 scripts/compare_subagent_trends.py

# ── Governance smoke checks ────────────────────────────────────────────────
rg -n "Assumption Ledger|Anti-Bloat|Generation vs Discrimination" AGENTS.md
rg -n "^## 1[1-5]\." prompts.md

# ── Caveman benchmark (real API, requires key) ─────────────────────────────
# Key loaded automatically from .env.local (gitignored)
# Or: OPENAI_API_KEY=<key> python3 benchmarks/caveman_benchmark.py
python3 benchmarks/caveman_benchmark.py

# ── Full one-liner validation suite ───────────────────────────────────────
python3 scripts/validate_codex_workspace.py \
  && python3 tests/caveman/verify_repo.py \
  && python3 -m unittest tests/test_caveman_compress.py tests/test_codex_hooks_behavior.py tests/test_subagent_checks.py
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
