# OpenWeb Ninja Trustpilot Reviews API — Provisional Scorecard (/10 rubric)

Rubric source: `docs/testing-criteria.md` §4. Elimination result: **passed** (see `elimination-assessment.md`).

## Criterion 1: Success Rate & Reliability — 1.98 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Success rate on 1K-request benchmark | 1.0 | 1.00 | Measured: 1,000/1,000 = 100% |
| Empty/partial response rate | 0.4 | 0.40 | Measured: 0/50 pages empty or partial |
| Error handling quality | 0.3 | 0.28 | Measured directly this time (unlike prior tools): one HTTP 500 occurred with a clear structured error body and was correctly retried to success per policy |
| Stability during test window | 0.3 | 0.30 | Measured: no degradation across the ~3 min run |

## Criterion 2: Data Quality & Completeness — 1.82 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Field coverage vs ground truth | 0.8 | 0.62 | Calculated: 10/13 strict = 76.9% (see field-coverage.md) |
| Data accuracy | 0.5 | 0.50 | Measured: 0 unexplained mismatches (the 4 `company_replied` cases were investigated and attributed to genuine same-day freshness, not extraction error) |
| Schema consistency | 0.4 | 0.40 | Measured: 0 missing-field occurrences across 1,000 raw items |
| Freshness | 0.3 | 0.30 | Measured and directly evidenced — 4 owner replies appeared that postdated the ground-truth capture by ~1 day |

## Criterion 3: Cost Efficiency — 0.70 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Cost per 1K successful records | 0.8 | 0.30 | Range $0–$0.25/1,000 depending on tier, but the account's actual "Basic" tier rate is unpublished — genuine uncertainty on the number that matters |
| Billing fairness | 0.3 | 0.10 | Whether the retried HTTP 500 consumed quota twice is undocumented and unverified |
| Free tier for evaluation | 0.2 | 0.20 | Concretely documented (100 requests/month) |
| Pricing transparency | 0.2 | 0.10 | 4/5 tiers fully transparent, but the account's actual tier is absent from the published card |

## Criterion 4: Speed & Throughput — 0.98 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Median latency per request | 0.5 | 0.30 | Measured: 1,870 ms |
| Wall-clock time for 1K-record batch | 0.5 | 0.38 | Measured: 180,749 ms (~3 min) for 1,000 reviews via 50 sequential requests |
| p95 latency | 0.3 | 0.22 | Measured: 3,684 ms, consistent with the vendor's own published 1–5s claim |
| Async/batch endpoint availability | 0.2 | 0.08 | None documented — synchronous, one domain per request, no multi-query batching |

## Criterion 5: Scalability — 0.50 / 1.2

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Rate limits & concurrency | 0.5 | 0.35 | Clearly documented per plan (10–20 req/sec); this run stayed well under any tier's limit without issue |
| Degradation at 10x volume | 0.4 | 0.00 | Not tested this run |
| Volume caps blocking production use | 0.3 | 0.15 | Free plan hard-capped at 100/month with no overage; "Basic" plan's cap unknown |

## Criterion 6: Developer Experience — 0.89 / 1.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Time-to-first-successful-request | 0.3 | 0.27 | Worked correctly on the very first live call after doc verification |
| Docs quality | 0.3 | 0.28 | Precise, interactive, example-driven; matched live behavior exactly (minor friction: requires a real browser to render, not a plain fetch) |
| SDKs & code examples | 0.2 | 0.18 | Official Shell/Ruby/Node.js/PHP/Python client examples — broadest official language coverage of any tool tested |
| Error message clarity | 0.2 | 0.16 | The one real error had a clean, structured body (`status`, `error.message`, `error.code`) |

## Criterion 7: Input Flexibility & Coverage — 0.60 / 0.8

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Accepted input types | 0.3 | 0.15 | `company-reviews` accepts `company_domain` only (no direct company-ID or URL param on this endpoint) |
| Endpoint breadth | 0.3 | 0.27 | Broadest of any tool tested — 9 distinct endpoints spanning company, category, and consumer data |
| Enrichment/related endpoints | 0.2 | 0.18 | Genuine enrichment: consumer-details/reviews, category search/details/company-list |

---

## Aggregate score: **7.47 / 10**

This sits right at the boundary between "Usable with caveats" (6.0–7.4) and "Strong" (7.5–8.9) per `docs/testing-criteria.md` §5. Presented as measured (7.47), not pre-rounded to avoid obscuring the boundary — it falls just under 7.5, so the honest classification is:

### **Usable with caveats — flag them**

| Criterion | Score | /5 stars |
|---|---:|---:|
| 1. Success Rate & Reliability | 1.98/2.0 | ★★★★★ (4.95) |
| 2. Data Quality & Completeness | 1.82/2.0 | ★★★★★ (4.55) |
| 3. Cost Efficiency | 0.70/1.5 | ★★☆☆☆ (2.3) |
| 4. Speed & Throughput | 0.98/1.5 | ★★★☆☆ (3.3) |
| 5. Scalability | 0.50/1.2 | ★★☆☆☆ (2.1) |
| 6. Developer Experience | 0.89/1.0 | ★★★★☆ (4.5) |
| 7. Input Flexibility & Coverage | 0.60/0.8 | ★★★★☆ (3.8) |

**The caveat to flag: outstanding reliability and data quality, undermined by real cost uncertainty (the account's actual "Basic" plan rate is absent from the published pricing) and a hard free/low-tier monthly cap (100 requests) that leaves no room for a repeat run without either upgrading or waiting for the next billing cycle.**
