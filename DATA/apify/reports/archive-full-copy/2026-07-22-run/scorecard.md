# Apify (automation-lab/trustpilot) — Provisional Scorecard (/10 rubric)

Rubric source: `docs/testing-criteria.md` §4. Elimination result: **passed** (see `elimination-assessment.md`).

## Criterion 1: Success Rate & Reliability — 1.38 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Success rate on 1K-request benchmark | 1.0 | 0.80 | Measured: 798/1,000 = 79.8% |
| Empty/partial response rate | 0.4 | 0.20 | Measured: 1 of 5 domains (SHEIN) returned completely empty; the other 4 were essentially perfect |
| Error handling quality | 0.3 | 0.10 | **Penalized**: the SHEIN failure produced zero error signal anywhere (no HTTP error, no error object in the dataset, no flag on the Run object) — a well-behaved system should surface a per-input failure, not silently omit it |
| Stability during test window | 0.3 | 0.28 | Measured: clean run stats, no crashes/migrations/restarts |

## Criterion 2: Data Quality & Completeness — 1.94 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Field coverage vs ground truth | 0.8 | 0.74 | Calculated: 12/13 = 92.3% — highest of any tool tested |
| Data accuracy | 0.5 | 0.50 | Measured: 0 unexplained mismatches (the 4 `company_replied` cases confirmed as genuine freshness, cross-validated against OpenWeb Ninja's independent finding) |
| Schema consistency | 0.4 | 0.40 | Measured: 0 missing-field occurrences across all 800 returned items |
| Freshness | 0.3 | 0.30 | Measured and cross-confirmed against a second tool's independent freshness discovery |

## Criterion 3: Cost Efficiency — 1.20 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Cost per 1K successful records | 0.8 | 0.55 | Measured $0.5827/1,000 — moderate, pricier than DataForSEO's $0.0375 |
| Billing fairness | 0.3 | 0.25 | Measured cost tracked the actual unique count returned (798), not the requested 1,000 — did not overcharge for the shortfall |
| Free tier for evaluation | 0.2 | 0.20 | Concrete published tiers (Free through Diamond) with a clear formula |
| Pricing transparency | 0.2 | 0.20 | Published formula predicted the real measured charge within 0.3% |

## Criterion 4: Speed & Throughput — 1.17 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Median latency per request | 0.5 | 0.35 | Measured: 1,429 ms (our polling calls) |
| Wall-clock time for near-1K batch | 0.5 | 0.40 | Measured: ~7 min for 798 reviews across 5 domains, all within one Actor run |
| p95 latency | 0.3 | 0.22 | Measured: 2,256 ms |
| Async/batch endpoint availability | 0.2 | 0.20 | Best of any tool tested: one native Actor run handles multiple companies directly via `companyUrls` |

## Criterion 5: Scalability — 0.52 / 1.2

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Rate limits & concurrency | 0.5 | 0.30 | Not stress-tested; no rate-limit errors encountered in this run |
| Degradation at 10x volume | 0.4 | 0.00 | Not tested |
| Volume caps blocking production use | 0.3 | 0.22 | Actor documents `maxReviewsPerCompany=0` as unlimited with automatic pagination through thousands of reviews — strong documented scalability, tempered by the real-world SHEIN reliability gap observed this run |

## Criterion 6: Developer Experience — 0.76 / 1.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Time-to-first-successful-request | 0.3 | 0.27 | Worked correctly on the first live attempt |
| Docs quality | 0.3 | 0.27 | Thorough and precise; matched live behavior on 4/5 domains with zero discrepancies |
| SDKs & code examples | 0.2 | 0.14 | Official Apify client SDKs exist (not directly exercised — raw HTTP was used per this project's design) |
| Error message clarity | 0.2 | 0.08 | **Penalized heavily**: no error signal was ever surfaced for the SHEIN failure |

## Criterion 7: Input Flexibility & Coverage — 0.54 / 0.8

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Accepted input types | 0.3 | 0.28 | Accepts bare domain or full Trustpilot URL, **and** multiple companies in a single call — most flexible input of any tool tested |
| Endpoint breadth | 0.3 | 0.12 | This specific Actor is narrowly scoped to Trustpilot reviews only — no separate company-search/category endpoints (unlike OpenWeb Ninja's 9-endpoint suite) |
| Enrichment/related endpoints | 0.2 | 0.14 | `includeCompanyInfo` embeds company trust score, stars, total reviews, and categories directly into each review record |

---

## Aggregate score: **7.51 / 10 → Strong — minor trade-offs** (7.5–8.9 band, per `docs/testing-criteria.md` §5)

Right at the low edge of "Strong." The math is driven by excellent results on 4 of 5 domains (best field coverage and reply-date coverage of any tool tested, cost formula measured almost exactly as published) offsetting the one real problem: SHEIN silently returning zero reviews with no error signal anywhere.

| Criterion | Score | /5 stars |
|---|---:|---:|
| 1. Success Rate & Reliability | 1.38/2.0 | ★★★☆☆ (3.45) |
| 2. Data Quality & Completeness | 1.94/2.0 | ★★★★★ (4.85) |
| 3. Cost Efficiency | 1.20/1.5 | ★★★★☆ (4.0) |
| 4. Speed & Throughput | 1.17/1.5 | ★★★★☆ (3.9) |
| 5. Scalability | 0.52/1.2 | ★★☆☆☆ (2.2) |
| 6. Developer Experience | 0.76/1.0 | ★★★★☆ (3.8) |
| 7. Input Flexibility & Coverage | 0.54/0.8 | ★★★★☆ (3.4) |

**The caveat to flag: this is the highest-fidelity tool tested when it works, but the unexplained, silent, complete failure on one of five domains — with zero error signal anywhere in the API — is a real production risk that a single benchmark run cannot fully characterize.**
