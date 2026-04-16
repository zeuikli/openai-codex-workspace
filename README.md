# OpenAI Codex Workspace

Codex-native workspace template. Provides a ready-to-run ruleset: `AGENTS.md` + `.codex/agents` + `.agents/skills`, adapted from [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman) for OpenAI Codex with dynamic auto-level loading.

---

## Quick Start

```bash
# Load core context and start working
codex "請先固定讀取 AGENTS.md、Memory.md、prompts.md；接著讀取 .codex/config.toml；skills 僅按需載入。Karpathy 九條原則視為硬性守則。"
```

---

## Caveman Dynamic Auto-Level System

Caveman mode is injected automatically at session start — no manual `/caveman` command needed. The classifier routes each prompt to the right compression level with zero API dependency.

### Architecture

```
SessionStart hook (139 tokens, once)
  ↓
User prompt → regex classifier (0.044ms, no API)
  ↓
Classify: lite / full / ultra / off
  ↓
Append level delta (45–59 tokens, with Not/Yes examples)
  ↓
Model responds at correct compression level
```

### Compression Levels

| Level | Trigger | Rules |
|-------|---------|-------|
| `lite` | Q&A / definitions / yes-no | Keep articles + full sentences, drop filler only |
| `full` | Technical / debug / multi-step (**DEFAULT**) | Drop articles, fragments OK, short synonyms |
| `ultra` | Summarize / list / batch / "be brief" | Abbreviate (DB/auth/cfg), X→Y arrows, one word OK |
| `off` | Security warnings / destructive ops | Normal prose, no compression |

### Token Budget (per session)

| Strategy | Session tokens | vs static (retired) |
|----------|---------------|---------------------|
| `static` (retired) | 427 tok | baseline — **net cost loss** |
| `lean + full delta` (current) | 189 tok | **-55.7%** |
| `lean + lite delta` | 184 tok | -56.9% |
| `lean + ultra delta` | 198 tok | -53.6% |

---

## Dynamic Loading Benchmark

**Model:** gpt-5.4-mini · **Prompts:** 16 · **5 strategies**
Run: **2026-04-16 03:47 UTC** — Phase 1 (offline) + Phase 2 (API) + Phase 3 (hooks)

### Total Token Cost (Input + Output = Real API Cost)

| Strategy | Avg Input | Avg Output | **Total** | vs none | Output reduction |
|----------|-----------|------------|-----------|---------|-----------------|
| `none` (baseline) | 25.6 | 283.9 | **309.5** | +0.0% | — |
| `forced_ultra` | 229.6 | 114.9 | **344.5** | +11.3% | **+59.5%** |
| `original_filtered`* | 213.6 | 133.1 | **346.7** | +12.0% | +53.1% |
| **`dynamic_auto`** | **209.1** | **139.7** | **348.8** | **+12.7%** | **+50.8%** |
| `static` (retired) | 391.6 | 86.9 | **478.5** | +54.6% | +69.4% |

> \* `original_filtered` = JuliusBrussee/caveman approach: single-level static rules (~196 tokens). Requires manual level selection. Our `dynamic_auto` is 0.7 pp behind in total cost while maintaining **automatic classification**.

### Classifier Performance

| Metric | Value |
|--------|-------|
| Accuracy (40 prompts, 8 categories) | **100%** (40/40) |
| Latency | **0.044ms** avg (pure Python regex, zero API) |
| Hook correctness | **10/10** (100%) |
| Test suite | **55/55** passing |

### Key Finding: Static Strategy is a Net Loss

Static caveman (+54.6% total cost) injects 392 tokens of system prompt but only saves ~197 output tokens per call — input overhead outweighs output savings. Dynamic auto-level costs only +12.7% above baseline while compressing output by 50.8%.

Full reports: [`benchmarks/results/`](benchmarks/results/)

---

## Benchmark History

### Optimization Timeline

| Version | Key change | `dynamic_auto` total cost vs none |
|---------|-----------|-----------------------------------|
| v1 static | 427-token all-level injection | +60.3% |
| v2 lean migration | 132-token lean shared | +8.0% |
| v3 lean + examples | Added Not/Yes to lean prompt | +18.6% |
| **v4 delta + examples** | Added Not/Yes to each delta | **+12.7%** |
| `original_filtered` ref | JuliusBrussee filtered approach | +12.0% |

### Original Caveman Model Benchmark

Real API results — **80 calls**, 4 models × 4 levels × 5 technical prompts.
Run: **2026-04-16 01:12 UTC**

| Model | None (baseline) | lite | full | ultra | Best reduction |
|-------|----------------|------|------|-------|----------------|
| gpt-5.4 | 435 tok | 3.3% | 5.7% | **13.1%** | 13.1% |
| gpt-5.4-mini | 403 tok | 11.9% | 26.7% | **51.4%** | 51.4% |
| gpt-5.4-nano | 445 tok | 19.8% | 11.8% | **51.2%** | 51.2% |
| gpt-5.3-codex | 370 tok | 6.4% | 6.2% | **19.7%** | 19.7% |

Full report: [`benchmarks/results/caveman_benchmark_report.md`](benchmarks/results/caveman_benchmark_report.md)

---

## Hook Architecture

```
.codex/hooks.json
├── SessionStart    → session_start_note.sh       (139-token lean prompt, once)
├── PreToolUse      → pre_tool_use_guard.sh        (blocks rm-rf, push main, curl|sh)
├── PostToolUse     → post_tool_use_note.sh        (post-bash notes)
└── UserPromptSubmit→ user_prompt_submit_caveman.sh (28-token per-turn reinforcement)
                                                    ↑ registered, activates when Codex
                                                      adds UserPromptSubmit support
```

**Per-turn reinforcement** (from JuliusBrussee/caveman research): prevents mid-session model drift caused by competing plugin instructions. Codex CLI currently exposes `SessionStart`, `PreToolUse`, `PostToolUse` only — the `UserPromptSubmit` hook is registered and ready to activate when support is added.

---

## Architecture: AGENTS vs SKILL vs Hooks

| Primitive | Best for | Caveman fit |
|-----------|----------|-------------|
| **Hooks (SessionStart)** | Always-on context injection | ✅ Primary — lean 139-token prompt auto-active |
| **Hooks (UserPromptSubmit)** | Per-turn reinforcement | ✅ Registered, pending Codex support |
| **SKILL** | On-demand overrides via `/caveman` | ✅ Manual level override when needed |
| **AGENTS.md** | Persistent standing rules | ⚠️ Too broad for per-prompt adaptation |

**Current pattern:** SessionStart hook (lean) + per-prompt classifier + delta append + SKILL for manual overrides.

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
| `caveman` | `/caveman [lite\|full\|ultra]` | Manual level override; auto-level is always-on via hook |
| `caveman-commit` | `/caveman-commit` | Compressed conventional commits |
| `caveman-review` | `/caveman-review` | Single-line PR feedback |
| `caveman-compress` | `/caveman-compress <file>` | Compress memory files (AGENTS.md, todos) |
| `karpathy-loop` | `/karpathy-loop` | Declarative validation loop, max 5 rounds / 10 min |
| `multi-agent-collaboration` | task delegation | 3-phase: research → implement → review |
| `deep-review` | major changes | Correctness, regression risk, security |
| `docs-drift-check` | doc divergence | Spec vs implementation drift |
| `session-handoff` | end of session | Structured Memory.md update |
| `cost-tracker` | cost review | Token usage report |

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
# ── Test suite (55 tests) ───────────────────────────────────────────────────
python3 -m pytest tests/ -q

# ── Workspace structure ────────────────────────────────────────────────────
python3 scripts/validate_codex_workspace.py

# ── Core behaviour tests ───────────────────────────────────────────────────
python3 -m pytest tests/test_codex_hooks_behavior.py -v
python3 -m pytest tests/test_subagent_checks.py -v
python3 -m pytest tests/test_caveman_dynamic_loader.py -v

# ── Auto-level classifier (offline, no API key needed) ─────────────────────
python3 scripts/caveman_auto_level.py "Summarize all PRs"     # → ultra
python3 scripts/caveman_auto_level.py "What is TCP?"           # → lite
python3 scripts/caveman_auto_level.py "DROP TABLE users"       # → off

# ── Dynamic loader (inspect prompt sizes + decisions) ─────────────────────
python3 scripts/caveman_dynamic_loader.py --show-prompts
python3 scripts/caveman_dynamic_loader.py "Explain connection pooling"
python3 scripts/caveman_dynamic_loader.py --benchmark-mode

# ── Codex workspace load simulator ────────────────────────────────────────
python3 scripts/simulate_codex_load.py

# ── Full benchmark (Phase 1+3 offline; Phase 2 requires API key) ──────────
python3 benchmarks/caveman_dynamic_load_benchmark.py --phases 1,3
OPENAI_API_KEY=sk-... python3 benchmarks/caveman_dynamic_load_benchmark.py

# ── Subagent quality & token report ───────────────────────────────────────
python3 scripts/run_subagent_checks.py
python3 scripts/compare_subagent_trends.py

# ── Governance smoke checks ────────────────────────────────────────────────
rg -n "Assumption Ledger|Anti-Bloat|Generation vs Discrimination" AGENTS.md
rg -n "^## 1[1-5]\." prompts.md
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
├── AGENTS.md                    ← compact rules (session start)
├── AGENTS.full.md               ← full governance rules
├── Memory.md                    ← session handoff state (~500 tokens)
├── prompts.md                   ← prompt templates
├── benchmarks/
│   ├── caveman_benchmark.py                    ← model × level benchmark
│   ├── caveman_dynamic_load_benchmark.py       ← 3-phase dynamic load benchmark
│   └── results/                                ← all benchmark reports (JSON + MD)
├── .codex/
│   ├── config.toml
│   ├── hooks.json               ← SessionStart / PreToolUse / PostToolUse / UserPromptSubmit
│   ├── agents/                  ← per-agent TOML configs
│   └── hooks/
│       ├── session_start_note.sh           ← lean 139-token prompt
│       ├── pre_tool_use_guard.sh           ← blocks dangerous commands
│       ├── post_tool_use_note.sh           ← post-bash notes
│       └── user_prompt_submit_caveman.sh   ← per-turn reinforcement (pending Codex support)
├── .agents/skills/              ← on-demand skills (SKILL.md per skill)
├── docs/
│   ├── karpathy-codex-principles.md
│   ├── reports/                 ← memory history, subagent quality reports
│   └── ...
├── scripts/
│   ├── caveman_auto_level.py        ← regex classifier (0.044ms, no API)
│   ├── caveman_dynamic_loader.py    ← dynamic loading engine + prompt registry
│   ├── simulate_codex_load.py       ← 7-phase workspace load simulator
│   ├── validate_codex_workspace.py  ← workspace structure validator
│   └── run_subagent_checks.py       ← subagent quality checks
└── tests/                       ← 55 unit tests
    ├── test_caveman_dynamic_loader.py
    ├── test_codex_hooks_behavior.py
    └── test_subagent_checks.py
```

---

## Migration from claude-code-workspace

| Claude concept | Codex equivalent |
|----------------|------------------|
| `CLAUDE.md` | `AGENTS.md` |
| `.claude/rules/*` | `AGENTS.full.md` sections |
| `.claude/settings.json` hooks | `.codex/hooks.json` + `.codex/hooks/` scripts |
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
