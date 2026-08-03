# Outscraper Trustpilot Reviews API — Provisional Scorecard (/10 rubric)

Rubric source: `docs/testing-criteria.md` §4. Elimination result: **passed** (see `elimination-assessment.md`) — scoring applies.

**Marked provisional** because several sub-scores depend on evidence this single successful run cannot produce (true billed cost, 10x-load behavior, documented rate limits, support responsiveness) — see `missing-evidence.md`. Nothing below is invented to fill those gaps; each is scored conservatively and labeled.

## Criterion 1: Success Rate & Reliability — 1.92 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Success rate on 1K-request benchmark | 1.0 | 1.00 | Measured: 1,000/1,000 = 100% |
| Empty/partial response rate | 0.4 | 0.40 | Measured: 0 empty, 0 partial |
| Error handling quality | 0.3 | 0.22 | Judged: docs specify unusually clear, distinct meanings for 401/402/422 (richer taxonomy than DataForSEO's generic codes), but zero errors occurred this run to confirm real recovery behavior |
| Stability during test window | 0.3 | 0.30 | Measured: no degradation across the ~8.5 min run |

## Criterion 2: Data Quality & Completeness — 1.94 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Field coverage vs ground truth | 0.8 | 0.74 | Calculated: 12/13 = 92.3% (see field-coverage.md) |
| Data accuracy | 0.5 | 0.50 | Measured: 0 mismatches on any field both sources captured |
| Schema consistency across responses | 0.4 | 0.40 | Measured: 0 missing-field occurrences across all 1,000 raw items |
| Freshness | 0.3 | 0.30 | Measured: current timestamps, `sort=recency` ordering matched ground truth |

## Criterion 3: Cost Efficiency — 0.85 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Cost per 1K successful records | 0.8 | 0.35 | Measured usage × published pricing: $2.70–$3.00/1,000 — roughly 72–80x DataForSEO's measured $0.0375/1,000 for the identical benchmark |
| Billing fairness (failed requests not charged) | 0.3 | 0.10 | Not tested this run (no failures occurred), and docs themselves document an unfavorable behavior (empty results may still consume ~1 review of usage) |
| Free tier / trial credits for evaluation | 0.2 | 0.20 | Documented and concrete (first 100 reviews free) — a real, confirmed evaluation allowance, unlike DataForSEO where this was entirely unverified |
| Pricing transparency | 0.2 | 0.20 | Fully public tiered pricing; calculated cost matched the pre-run estimate exactly |

## Criterion 4: Speed & Throughput — 1.07 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Median latency per request | 0.5 | 0.35 | Measured: 1,169 ms — slower than DataForSEO's 404 ms |
| Wall-clock time for 1K-record batch | 0.5 | 0.30 | Measured: 512,595 ms (~8 min 33 s) — roughly 3.1x slower than DataForSEO's 165 s for the same 1,000-review benchmark |
| p95 latency (consistency under load) | 0.3 | 0.22 | Measured: 1,982 ms, a tight distribution with no major outlier |
| Async/batch endpoint availability | 0.2 | 0.20 | Documented + used: async workflow, plus documented batching of up to 1,000 queries per single request (not exercised this run, since each domain was submitted independently for clean per-domain evidence) |

## Criterion 5: Scalability — 0.30 / 1.2

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Rate limits & max concurrency allowed | 0.5 | 0.15 | **Not documented at all** (`docs/outscraper-documentation.md`'s own status table lists this as "Pending verification") — worse than DataForSEO, which at least publishes explicit numbers |
| Degradation at 10x volume | 0.4 | 0.00 | **Not tested this run** |
| Volume caps blocking production use | 0.3 | 0.15 | No cap encountered, but also undocumented at the account-tier level |

## Criterion 6: Developer Experience — 0.81 / 1.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Time-to-first-successful-request | 0.3 | 0.28 | Measured: worked correctly on the very first real request, no parser fixes needed |
| Docs quality | 0.3 | 0.29 | Measured: every parameter/workflow/field matched live behavior exactly; docs proactively flagged non-obvious traps (skip-must-be-multiple-of-20, empty-result billing, ~4h result expiration) that DataForSEO's docs did not call out as explicitly |
| SDKs & working code examples | 0.2 | 0.10 | curl examples only in docs; no official SDK tested |
| Error message clarity + support responsiveness | 0.2 | 0.14 | Documented error meanings are clear and specific; support responsiveness untested |

## Criterion 7: Input Flexibility & Coverage — 0.43 / 0.8

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Accepted input types | 0.3 | 0.20 | Accepts both a bare domain **and** a full Trustpilot profile URL — more flexible than DataForSEO's domain-only input |
| Endpoint breadth for the platform | 0.3 | 0.18 | Still narrow (1 submit + 1 results endpoint), but documented multi-query batching (up to 1,000 queries per request) adds real breadth DataForSEO lacks |
| Enrichment/related endpoints | 0.2 | 0.05 | No clearly documented related/enrichment endpoint for Trustpilot found |

---

## Aggregate score: **7.32 / 10 → Usable with caveats — flag them** (6.0–7.4 band, per `docs/testing-criteria.md` §5)

| Criterion | Score | /5 stars |
|---|---:|---:|
| 1. Success Rate & Reliability | 1.92/2.0 | ★★★★★ (4.8) |
| 2. Data Quality & Completeness | 1.94/2.0 | ★★★★★ (4.9) |
| 3. Cost Efficiency | 0.85/1.5 | ★★★☆☆ (2.8) |
| 4. Speed & Throughput | 1.07/1.5 | ★★★★☆ (3.6) |
| 5. Scalability | 0.30/1.2 | ★☆☆☆☆ (1.3) |
| 6. Developer Experience | 0.81/1.0 | ★★★★☆ (4.1) |
| 7. Input Flexibility & Coverage | 0.43/0.8 | ★★★☆☆ (2.7) |

**Biggest drag on the score: Scalability (undocumented rate limits, no 10x test) and Cost Efficiency (77x pricier than DataForSEO for the identical benchmark).** Data quality and reliability are excellent — perfect run, perfect ground-truth match, better field coverage than DataForSEO. The caveat to flag for readers: Outscraper is the more expensive, better-documented, slightly slower option so far — the real differentiator will be how it and DataForSEO compare once a third tool and a load test are in the picture.
