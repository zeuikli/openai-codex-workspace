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
Run: 2026-04-16 00:13 UTC. Models mapped to closest available OpenAI API equivalents.

### Per-Model Results

#### gpt-5.4 (→ gpt-4.1)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 448.8 | 287.6 | 5553 | — |
| lite | 151.6 | 101.6 | 3057 | **66.2%** |
| full | 156.0 | 87.0 | 2637 | **65.2%** |
| ultra | 123.6 | 67.2 | 1871 | **72.5%** |

#### gpt-5.4-mini (→ gpt-4.1-mini)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 409.0 | 286.4 | 6772 | — |
| lite | 204.0 | 138.4 | 3256 | **50.1%** |
| full | 200.2 | 130.4 | 3253 | **51.1%** |
| ultra | 95.4 | 58.8 | 1525 | **76.7%** |

#### gpt-5.4-nano (→ gpt-4.1-nano)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 434.4 | 291.4 | 2492 | — |
| lite | 73.8 | 57.6 | 596 | **83.0%** |
| full | 99.4 | 64.8 | 711 | **77.1%** |
| ultra | 35.8 | 10.8 | 416 | **91.8%** |

#### gpt-5.3-codex (→ gpt-4o)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction |
|-------|-------------------|-----------|------------------|-----------------|
| none (baseline) | 459.0 | 338.8 | 3824 | — |
| lite | 151.6 | 102.2 | 1593 | **67.0%** |
| full | 193.2 | 116.0 | 3179 | **57.9%** |
| ultra | 156.6 | 81.8 | 1652 | **65.9%** |

### Cross-Model Summary (full level)

| Model | Avg Output Tokens | Token Reduction | Avg Latency (ms) |
|-------|-------------------|-----------------|------------------|
| gpt-5.4 (→ gpt-4.1) | 156.0 | 65.2% | 2637 |
| gpt-5.4-mini (→ gpt-4.1-mini) | 200.2 | 51.1% | 3253 |
| gpt-5.4-nano (→ gpt-4.1-nano) | 99.4 | **77.1%** | **711** |
| gpt-5.3-codex (→ gpt-4o) | 193.2 | 57.9% | 3179 |

**Key findings:**
- `ultra` mode delivers the highest compression (66–92% token reduction) at lowest latency.
- `gpt-5.4-nano` responds fastest and compresses most aggressively under all levels.
- `gpt-5.4` (flagship) produces best quality at `full`/`ultra` while keeping technical accuracy.
- `lite` is best when grammar must stay intact; saves 50–83% tokens vs baseline.

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
| Caveman compression | `.agents/skills/caveman/SKILL.md` |

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
