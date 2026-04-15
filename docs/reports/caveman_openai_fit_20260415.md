# Caveman × OpenAI Model Fit (2026-04-15)

- Baseline token estimate: **77**
- Sub-agent style parallel run time: **4.48 ms**

## Level compression (vs baseline)

| Level | Tokens | Save vs baseline |
|---|---:|---:|
| lite | 36 | 53.25% |
| full | 26 | 66.23% |
| ultra | 17 | 77.92% |

## Top model+level combinations (fitness)

| Rank | Model | Level | Est. output cost (USD/msg) | Quality×Perf | Fitness |
|---:|---|---|---:|---:|---:|
| 1 | gpt-5.4-nano | ultra | 0.00002125 | 0.4143 | 19496.00 |
| 2 | gpt-5.4-nano | full | 0.00003250 | 0.4484 | 13797.17 |
| 3 | gpt-5.4-nano | lite | 0.00004500 | 0.4777 | 10614.49 |
| 4 | gpt-5-mini | ultra | 0.00003400 | 0.3502 | 10300.00 |
| 5 | gpt-5-mini | full | 0.00005200 | 0.3790 | 7289.23 |

## Activation efficiency: Skills vs AGENTS vs Hooks vs Rules

| Mechanism | Autoload | Manual steps | Payload chars | Activation latency score (↓ better) |
|---|---:|---:|---:|---:|
| agents | 1 | 0 | 120 | -24.00 |
| hooks | 1 | 0 | 405 | -9.75 |
| rules | 0 | 1 | 380 | 119.00 |
| skills | 0 | 1 | 2800 | 240.00 |

Fastest-to-activate ranking: agents > hooks > rules > skills

## Assumptions

- Token count uses offline approximation; not API usage meter.
- Cost uses OpenAI public output-token prices only.
- Load test compares activation friction (steps + payload), not network latency.
