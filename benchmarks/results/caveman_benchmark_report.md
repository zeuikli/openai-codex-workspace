# Caveman Compression Benchmark Report

**Run at:** 2026-04-16 01:12 UTC
**Prompts:** 5 standard technical questions
**Models:** gpt-5.4 · gpt-5.4-mini · gpt-5.4-nano · gpt-5.3-codex
**Compression levels:** none (baseline) · lite · full · ultra

## Architecture Decision: AGENTS vs SKILL vs Hooks

| Primitive | Best for | Caveman fit |
|-----------|----------|-------------|
| **SKILL** | On-demand, user-invocable via `/caveman` | ✅ **Best** — loaded only when needed, multi-level, progressive disclosure |
| **Hooks** | SessionStart flag + statusline | ⚠️ Partial — good for activation, hooks still experimental |
| **AGENTS.md** | Persistent standing rules | ⚠️ Too broad — bakes compression into every agent |

> **Recommended pattern:** SKILL as primary interface + Hook for SessionStart flag + AGENTS.md one-liner reference.

## Results by Model

### gpt-5.4

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|----------------|-----------|------------------|-------------------------|--------|
| none | 434.8 | 283.2 | 8079.8 | — (baseline) | 0 |
| lite | 420.6 | 291.4 | 7707.8 | 3.3% | 0 |
| full | 410.0 | 257.0 | 7540.8 | 5.7% | 0 |
| ultra | 377.8 | 229.4 | 7323.4 | 13.1% | 0 |

### gpt-5.4-mini

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|----------------|-----------|------------------|-------------------------|--------|
| none | 403.4 | 270.8 | 2949.8 | — (baseline) | 0 |
| lite | 355.2 | 241.2 | 2853.0 | 11.9% | 0 |
| full | 295.8 | 182.6 | 2537.8 | 26.7% | 0 |
| ultra | 196.0 | 106.4 | 2409.4 | 51.4% | 0 |

### gpt-5.4-nano

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|----------------|-----------|------------------|-------------------------|--------|
| none | 445.2 | 279.0 | 3669.8 | — (baseline) | 0 |
| lite | 357.2 | 220.4 | 2891.6 | 19.8% | 0 |
| full | 392.6 | 240.4 | 3488.4 | 11.8% | 0 |
| ultra | 217.2 | 120.4 | 2013.8 | 51.2% | 0 |

### gpt-5.3-codex (Responses API)

| Level | Avg Out-Tokens | Avg Words | Avg Latency (ms) | Token Reduction vs None | Errors |
|-------|----------------|-----------|------------------|-------------------------|--------|
| none | 369.8 | 227.2 | 6639.8 | — (baseline) | 0 |
| lite | 346.2 | 211.6 | 6726.2 | 6.4% | 0 |
| full | 347.0 | 203.6 | 6523.6 | 6.2% | 0 |
| ultra | 296.8 | 150.4 | 6291.6 | 19.7% | 0 |

## Cross-Model Summary

### Token Reduction at Each Compression Level vs None (baseline)

| Model | None (baseline) | lite | full | ultra | Best reduction |
|-------|----------------|------|------|-------|----------------|
| gpt-5.4 | 435 | 3.3% | 5.7% | 13.1% | **13.1%** |
| gpt-5.4-mini | 403 | 11.9% | 26.7% | 51.4% | **51.4%** |
| gpt-5.4-nano | 445 | 19.8% | 11.8% | 51.2% | **51.2%** |
| gpt-5.3-codex (Responses API) | 370 | 6.4% | 6.2% | 19.7% | **19.7%** |

### Average Latency at `full` Level (ms)

| Model | Avg Latency (ms) |
|-------|-----------------|
| gpt-5.4 | 7540.8 |
| gpt-5.4-mini | 2537.8 |
| gpt-5.4-nano | 3488.4 |
| gpt-5.3-codex (Responses API) | 6523.6 |

## Sample Outputs (first prompt)

**Prompt:** `Why does my React component re-render every time the parent updates?`

### gpt-5.4

**none:** Because in React, a parent re-render normally causes its children to render too.

Common reasons your child component re-renders when the parent updates:

1. Parent rendered again
- By default, React calls the child component function again whenever the parent renders.
- This is normal behavior.

2. Props are changing by reference
Even if the “values” look the same, React sees new references as changed.

Examples:
- New object each render:
```jsx
<Child style={{ color: 'red' }} />
```

- New arr…

**full:** Common cause: parent render triggers child render.

Why:
- In React, when parent renders, React calls child function again too.
- Child can skip work only if React can prove props/context/state unchanged in way it can compare.

Main reasons child re-renders on parent update:

1. Child not memoized
- Function component re-runs whenever parent re-runs.
- Fix: wrap with `React.memo`.

```jsx
const Child = React.memo(function Child({ value }) {
  console.log('child render');
  return <div>{value}</d…

**ultra:** Because parent render → child fn runs again.

Key points:

- In React, parent re-render usually → all children re-render.
- "Re-render" ≠ DOM update always. React may diff → no real DOM change.
- Child re-renders unless memoization / bailout.

Common causes:

1. Normal behavior  
   - Parent state/props change → parent renders → child renders.

2. New prop references  
   - Parent creates new obj/arr/fn each render.
   - Example:
     ```jsx
     <Child style={{ color: 'red' }} onClick={() => do…

### gpt-5.4-mini

**none:** Because in React, a parent re-render usually causes its children to be re-rendered too.

A few common reasons:

1. **Normal React behavior**
   - When a parent component renders again, React will by default call the child component function again as part of reconciling the tree.
   - This does **not always mean the DOM updates**; it just means the component function runs again.

2. **New props or new references**
   - If the parent passes props like:
     ```jsx
     <Child onClick={() => doSome…

**full:** Because parent render usually means child render too.

In React, when parent component updates, React re-runs parent function. That creates new JSX for children. Unless React can skip child, child component function runs again.

Common reasons:

- Child is inside parent render tree
- Props changed by reference
  - new object `{}` each render
  - new array `[]` each render
  - new function `() => {}` each render
- Context value changed
- State in child changed
- No memoization

How to stop extra …

**ultra:** Because parent update → child fn runs again → React re-evals JSX → child re-renders.

Common causes:
- Parent state/props change
- New prop refs each render: `{}`, `[]`, `() => {}` → new identity
- Context value changes
- Child not memoized

Fixes:
- `React.memo(Child)`
- `useMemo` for objects/arrays
- `useCallback` for fns
- Split state: keep unrelated state out of parent
- Avoid changing context value unless needed

Note: re-render ≠ DOM update. React may re-render cheaply.

---
*Generated by `benchmarks/caveman_benchmark.py` · 2026-04-16 01:12 UTC*
*gpt-5.3-codex benchmarked via OpenAI Responses API*