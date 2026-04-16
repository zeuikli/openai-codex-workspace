# Caveman Compression Benchmark Report

**Run at:** 2026-04-16 00:31 UTC
**Prompts:** 5 standard technical questions
**Compression levels:** none (baseline) · lite · full · ultra

## Architecture Decision: AGENTS vs SKILL vs Hooks

For this OpenAI Codex Workspace, **SKILL** is the right primitive for caveman:

| Primitive | Best for | Caveman fit |
|-----------|----------|-------------|
| **SKILL** | On-demand behaviour loaded per-task; user-invocable via `/caveman` | ✅ **Best** — loaded only when needed, supports multiple intensity variants, progressive disclosure |
| **Hooks** | Always-on session-start or per-turn side-effects | ⚠️ Partial — good for SessionStart flag + statusline, but Codex hooks still experimental |
| **AGENTS.md** | Persistent standing rules for every task | ⚠️ Too broad — bakes compression into every agent, wastes tokens when not wanted |

**Recommended pattern for Codex:** SKILL as primary interface + Hook for SessionStart flag write + AGENTS.md one-liner reference.

## Results by Model

### gpt-5.4

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 435.0 | 291.2 | 7509.2 | — | 0 |
| lite | 426.8 | 293.0 | 7472.0 | 1.9% | 0 |
| full | 430.6 | 265.8 | 6608.8 | 1.0% | 0 |
| ultra | 366.2 | 213.2 | 6553.2 | 15.8% | 0 |

### gpt-5.4-mini

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 426.6 | 290.0 | 2967.2 | — | 0 |
| lite | 345.8 | 233.0 | 2284.0 | 18.9% | 0 |
| full | 296.6 | 179.8 | 2183.4 | 30.5% | 0 |
| ultra | 186.8 | 108.0 | 1647.0 | 56.2% | 0 |

### gpt-5.4-nano

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 439.0 | 277.2 | 3145.8 | — | 0 |
| lite | 381.2 | 230.0 | 2709.2 | 13.2% | 0 |
| full | 411.6 | 251.8 | 2859.0 | 6.2% | 0 |
| ultra | 224.0 | 114.0 | 1787.0 | 49.0% | 0 |

### gpt-5.3-codex → gpt-5.2 (codex variants are completion-only models)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 468.6 | 280.2 | 7406.0 | — | 0 |
| lite | 430.6 | 263.0 | 8491.2 | 8.1% | 0 |
| full | 328.4 | 185.8 | 6244.0 | 29.9% | 0 |
| ultra | 254.2 | 128.6 | 4967.6 | 45.8% | 0 |

## Cross-Model Summary (full compression level)

| Model | Avg Output Tokens (full) | Token Reduction vs None | Avg Latency (ms) |
|-------|--------------------------|-------------------------|------------------|
| gpt-5.4 | 430.6 | 1.0% | 6608.8 |
| gpt-5.4-mini | 296.6 | 30.5% | 2183.4 |
| gpt-5.4-nano | 411.6 | 6.2% | 2859.0 |
| gpt-5.3-codex → gpt-5.2 (codex variants are completion-only models) | 328.4 | 29.9% | 6244.0 |

## Sample Outputs (first prompt)

**Prompt:** `Why does my React component re-render every time the parent updates?`

### gpt-5.4

**none:** Because in React, **when a parent renders, its children render too by default**.

That doesn’t always mean the DOM changes, but the child component function/class is usually called again unless React can **skip** it.

## Common reasons your child re-renders

### 1. The parent re-rendered
If the parent updates state or receives new props, React re-runs the parent render, and child components are re…

**full:** Common cause: parent render creates new props each time.

React re-renders child when:
- parent re-renders, and child not memoized
- prop identity changes
- state changes in child
- context value changes
- hook inside child triggers update

Big offenders in parent:
- inline object props  
  `style={{ color: 'red' }}`
- inline array props  
  `items={[1,2,3]}`
- inline function props  
  `onClick={…

**ultra:** Normal.

Parent render → child fn runs again.

Why:
- React re-evals subtree on parent update.
- Child props same ≠ child skipped, by default.
- Fn component call = render phase, not always DOM change.

Common triggers:
- New object/array literal props each parent render.
  - `{}` `[]` `() => {}`
- New callback identity.
- Context value changed.
- State changed in child.
- Key changed/remount.
- S…

### gpt-5.4-mini

**none:** Because in React, a parent re-render usually causes its children to be re-rendered too.

That does **not always mean the DOM is updated** — it just means React runs the child component function again to see if anything changed.

## Common reasons

### 1. Parent re-render triggers child re-render
If the parent updates state, React re-runs the parent, and by default its children are re-rendered as p…

**full:** Because parent render usually means child render too.

In React, when parent component updates, React re-runs parent function. That creates new child element tree. Child component gets rendered again unless React can skip it.

Common reasons:

- Parent state/props changed
- Child receives new prop reference each render:
  - inline object: `{}`  
  - inline array: `[]`
  - inline function: `() => {…

**ultra:** Because parent update → child fn runs again → React re-renders child by default.

Common causes:
- Parent state/props change
- New prop refs each render (`{}`, `[]`, `() => {}`) → shallow compare fails
- Context value changes
- Child not memoized

Fixes:
- `React.memo(Child)`
- `useMemo` / `useCallback` for stable refs
- Lift state less / split components
- Avoid passing inline objs/fns

Note: re-…

---
*Generated by `benchmarks/caveman_benchmark.py` · 2026-04-16 00:31 UTC*