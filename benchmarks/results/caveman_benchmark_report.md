# Caveman Compression Benchmark Report

**Run at:** 2026-04-16 00:13 UTC
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

### gpt-5.4 (→ gpt-4.1)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 448.8 | 287.6 | 5553.2 | — | 0 |
| lite | 151.6 | 101.6 | 3056.8 | 66.2% | 0 |
| full | 156.0 | 87.0 | 2636.6 | 65.2% | 0 |
| ultra | 123.6 | 67.2 | 1871.2 | 72.5% | 0 |

### gpt-5.4-mini (→ gpt-4.1-mini)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 409.0 | 286.4 | 6771.6 | — | 0 |
| lite | 204.0 | 138.4 | 3256.2 | 50.1% | 0 |
| full | 200.2 | 130.4 | 3252.6 | 51.1% | 0 |
| ultra | 95.4 | 58.8 | 1525.2 | 76.7% | 0 |

### gpt-5.4-nano (→ gpt-4.1-nano)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 434.4 | 291.4 | 2492.4 | — | 0 |
| lite | 73.8 | 57.6 | 596.2 | 83.0% | 0 |
| full | 99.4 | 64.8 | 711.2 | 77.1% | 0 |
| ultra | 35.8 | 10.8 | 415.8 | 91.8% | 0 |

### gpt-5.3-codex (→ gpt-4o)

| Level | Avg Output Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|-------------------|-----------|------------------|-------------------------|--------|
| none | 459.0 | 338.8 | 3823.8 | — | 0 |
| lite | 151.6 | 102.2 | 1592.6 | 67.0% | 0 |
| full | 193.2 | 116.0 | 3179.2 | 57.9% | 0 |
| ultra | 156.6 | 81.8 | 1651.8 | 65.9% | 0 |

## Cross-Model Summary (full compression level)

| Model | Avg Output Tokens (full) | Token Reduction vs None | Avg Latency (ms) |
|-------|--------------------------|-------------------------|------------------|
| gpt-5.4 (→ gpt-4.1) | 156.0 | 65.2% | 2636.6 |
| gpt-5.4-mini (→ gpt-4.1-mini) | 200.2 | 51.1% | 3252.6 |
| gpt-5.4-nano (→ gpt-4.1-nano) | 99.4 | 77.1% | 711.2 |
| gpt-5.3-codex (→ gpt-4o) | 193.2 | 57.9% | 3179.2 |

## Sample Outputs (first prompt)

**Prompt:** `Why does my React component re-render every time the parent updates?`

### gpt-5.4 (→ gpt-4.1)

**none:** When a parent React component updates (i.e., re-renders), its child components will also re-render by default. This is a fundamental part of how React's rendering model works. Here’s why this happens and what you can do about it:

## Why does this happen?

1. **React’s Rendering Model:**  
   When a parent component re-renders, React will also re-render all of its children, unless you explicitly p…

**full:** Parent re-renders → child re-renders by default. React re-renders all children when parent renders, unless child is memoized.

Reasons:
- Props change → child re-renders.
- Parent state/props change → triggers parent render → triggers child render.
- Functions/objects/arrays passed as props → new reference each render → child sees props as changed.

Solutions:
- Use `React.memo` for functional com…

**ultra:** Parent re-render → child re-render (default React).  
Reason:  
- New props (even if same value) → child re-render.  
- Parent state/props change → parent re-render → child re-render.  
- No memoization (React.memo) → always re-render.

Fix:  
- Use React.memo(child) → shallow prop compare → skip re-render if props same.  
- Use useCallback/useMemo for stable fn/obj/array props.  
- Minimize paren…

### gpt-5.4-mini (→ gpt-4.1-mini)

**none:** In React, a child component re-renders whenever its parent re-renders by default. This happens because React's rendering process is top-down: when a parent component updates (due to state or props changes), React will re-render that parent and all of its children to ensure the UI stays consistent.

Here are the main reasons why your React component re-renders every time the parent updates:

1. **P…

**full:** React re-renders child components when parent re-renders by default. Reasons:

1. Parent state/props change → parent re-renders → child re-renders.
2. Child receives new props (even if values same, new object/array reference triggers re-render).
3. No memoization on child component.

Solutions:

- Use React.memo on child to memoize output, skip re-render if props shallow equal.
- Use useCallback/u…

**ultra:** React re-renders child if parent re-renders by default. Parent update → new props/context → child re-render.

Reasons:
- Parent state/props change → parent re-render → child re-render.
- Child props shallow compare fail (new object/array inline).
- Context value change.
- No React.memo/useMemo/useCallback to memoize child/props/fns.

Fix:
- Use React.memo(child) → skip if props same.
- Memoize pro…

---
*Generated by `benchmarks/caveman_benchmark.py` · 2026-04-16 00:13 UTC*