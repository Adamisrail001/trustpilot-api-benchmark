# Lobstr.io Trustpilot Reviews — Provisional Scorecard (/10 rubric)

Elimination result: **passed** (see `elimination-assessment.md`).

## Criterion 1: Success Rate & Reliability — 1.97 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Success rate | 1.0 | 1.00 | 1,000/1,000 = 100% |
| Empty/partial response rate | 0.4 | 0.40 | 0 empty/partial, 0 shortfall |
| Error handling quality | 0.3 | 0.29 | 62 real HTTP 429s occurred and were all correctly retried to success — the best-evidenced retry behavior of any tool in this project |
| Stability | 0.3 | 0.28 | Stable once correctly configured |

## Criterion 2: Data Quality & Completeness — 1.94 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Field coverage | 0.8 | 0.74 | 12/13 = 92.3% |
| Data accuracy | 0.5 | 0.50 | 0 unexplained mismatches |
| Schema consistency | 0.4 | 0.40 | 0 missing fields across 1,000 items |
| Freshness | 0.3 | 0.30 | Cross-confirmed by 2 other independent tools |

## Criterion 3: Cost Efficiency — 1.08 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Cost per 1K | 0.8 | 0.55 | $0.50/1,000 advertised — moderate, not the cheapest tested |
| Billing fairness | 0.3 | 0.28 | Perfectly confirmed 1:1 credit-to-review ratio, zero waste from setup errors or retries |
| Free tier | 0.2 | 0.10 | Concept exists but this account's real allowance mechanics under Super Admin terms are opaque |
| Pricing transparency | 0.2 | 0.15 | Credit ratio fully transparent; $ conversion not exposed via API |

## Criterion 4: Speed & Throughput — 1.24 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Median latency | 0.5 | 0.42 | 222 ms |
| Wall-clock for 1K batch | 0.5 | 0.35 | Split across two invocations due to the fix cycle — reconstructed estimate, not one clean measurement |
| p95 latency | 0.3 | 0.27 | 305 ms |
| Async/batch availability | 0.2 | 0.20 | 5 domains natively handled in one Run |

## Criterion 5: Scalability — 0.60 / 1.2

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Rate limits & concurrency | 0.5 | 0.40 | Directly tested this run (62 real 429s, confirmed ~2 req/sec limit, handled correctly) |
| Degradation at 10x volume | 0.4 | 0.00 | Not tested |
| Volume caps | 0.3 | 0.20 | Reached full 1,000-review target on a nominally "free" plan via Super Admin access; exact mechanics unclear |

## Criterion 6: Developer Experience — 0.63 / 1.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Time-to-first-successful-request | 0.3 | 0.15 | Required two separate fix iterations before success — real friction |
| Docs quality | 0.3 | 0.20 | Mostly accurate, but the results-page `limit` parameter didn't behave as documented |
| SDKs | 0.2 | 0.10 | Not tested |
| Error message clarity | 0.2 | 0.18 | Both real errors encountered (`DuplicateSquid`, `Throttled`) were clear and specific |

## Criterion 7: Input Flexibility & Coverage — 0.44 / 0.8

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Accepted input types | 0.3 | 0.18 | Trustpilot business URLs as task input |
| Endpoint breadth | 0.3 | 0.12 | Narrow crawler/squid/task/run model |
| Enrichment | 0.2 | 0.14 | Company-level fields embedded per review (trust score, category, total reviews) |

---

## Aggregate score: **7.90 / 10 → Strong — minor trade-offs**

| Criterion | Score |
|---|---:|
| 1. Success Rate & Reliability | 1.97/2.0 |
| 2. Data Quality & Completeness | 1.94/2.0 |
| 3. Cost Efficiency | 1.08/1.5 |
| 4. Speed & Throughput | 1.24/1.5 |
| 5. Scalability | 0.60/1.2 |
| 6. Developer Experience | 0.63/1.0 |
| 7. Input Flexibility & Coverage | 0.44/0.8 |

**The caveat to flag:** once correctly configured, data quality and reliability are excellent — best-in-class field coverage and a perfectly fair, fully-confirmed billing model. But getting there required two real bug fixes (a squid-naming collision and a pagination/attribution bug both caused by gaps between documented and actual API behavior), and scalability beyond 1,000 reviews remains untested.
