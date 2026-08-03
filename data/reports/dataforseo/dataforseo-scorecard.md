# DataForSEO Trustpilot Reviews API — Scorecard (/10 rubric)

Rubric source: `docs/testing-criteria.md` §4. Elimination result: **passed** (see `dataforseo-elimination-assessment.md`) — scoring applies.

Each sub-score below states its evidence basis. "Measured" = directly observed this run. "Calculated" = arithmetic on measured numbers. "Judged" = a scoring call grounded in measured/documented evidence, explicitly reasoned. "Not tested" = no evidence either way this run; scored conservatively (low/zero) rather than assumed.

## Criterion 1: Success Rate & Reliability — 1.90 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Success rate on 1K-request benchmark | 1.0 | 1.00 | Measured: 999/1,000 unique valid reviews = 99.9% |
| Empty/partial response rate | 0.4 | 0.40 | Measured: 0 empty, 0 partial across all 5 tasks |
| Error handling quality | 0.3 | 0.20 | Judged: status codes/messages were clear and documented (`20000 Ok.`, `20100 Task Created.`), but no actual error/retry was exercised this run to confirm real-world recovery behavior — partial credit, not full |
| Stability during test window | 0.3 | 0.30 | Measured: no degradation across the ~165s run |

## Criterion 2: Data Quality & Completeness — 1.88 / 2.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Field coverage vs ground truth | 0.8 | 0.68 | Calculated: 11/13 comparable page fields covered = 84.6% (see `dataforseo-field-coverage.md`) |
| Data accuracy | 0.5 | 0.50 | Measured: 0 mismatches on any field both sources captured (see `dataforseo-ground-truth-comparison.md`) |
| Schema consistency across responses | 0.4 | 0.40 | Measured: 0 missing-field occurrences across all 1,000 raw items |
| Freshness | 0.3 | 0.30 | Measured: timestamps current as of run date, `sort_by=recency` ordering matched ground truth exactly |

## Criterion 3: Cost Efficiency — 1.10 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Cost per 1K successful records | 0.8 | 0.75 | Measured: $0.0375/1,000 (normalized: $0.03754/1,000 successful unique) — objectively very cheap in absolute terms |
| Billing fairness (failed requests not charged) | 0.3 | 0.15 | Not tested: zero failed requests occurred this run, so whether a failure would be billed is unverified — scored conservatively |
| Free tier / trial credits for evaluation | 0.2 | 0.00 | Not tested: no trial-credit mechanism was checked or used this run |
| Pricing transparency | 0.2 | 0.20 | Measured: public pricing page formula matched actual API-reported cost exactly ($0.0375 estimated = $0.0375 measured) |

## Criterion 4: Speed & Throughput — 1.32 / 1.5

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Median latency per request | 0.5 | 0.45 | Measured: 404 ms |
| Wall-clock time for 1K-record batch | 0.5 | 0.45 | Measured: 165,513 ms (~2 min 46 s) for all 1,000 reviews across 5 tasks. Caveat: documented worst-case SLA for standard priority is up to 45 min/task — this run was far faster than the documented ceiling, so credit is not full |
| p95 latency (consistency under load) | 0.3 | 0.22 | Measured: 2,378 ms, driven by one cold-start `task_post` call (2,378 ms vs. a 179–467 ms range for everything else) |
| Async/batch endpoint availability | 0.2 | 0.20 | Documented + used: fully async task model, supports up to 100 tasks per POST call |

## Criterion 5: Scalability — 0.60 / 1.2

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Rate limits & max concurrency allowed | 0.5 | 0.35 | Documented (30 POST/min, 100 tasks/POST, 20 `tasks_ready`/min) but not stress-tested against this run's tiny volume (5 tasks) |
| Degradation at 10x volume | 0.4 | 0.00 | **Not tested this run** — this benchmark did not attempt a 10x-volume load test |
| Volume caps blocking production use | 0.3 | 0.25 | No account-level daily/monthly ceiling was encountered; the 200/task depth cap is a per-task shape limit, not a volume ceiling |

## Criterion 6: Developer Experience — 0.73 / 1.0

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Time-to-first-successful-request | 0.3 | 0.27 | Measured: first task created successfully on first real attempt, 2,378 ms round trip |
| Docs quality | 0.3 | 0.28 | Measured: every documented parameter/endpoint matched observed live behavior with zero discrepancies |
| SDKs & working code examples | 0.2 | 0.10 | Official docs provide curl examples only; no official SDK was tested (this benchmark used raw HTTP) |
| Error message clarity + support responsiveness | 0.2 | 0.08 | Status messages were clear, but support responsiveness was not tested (no support ticket filed) |

## Criterion 7: Input Flexibility & Coverage — 0.32 / 0.8

| Sub-criterion | Max | Score | Basis |
|---|---:|---:|---|
| Accepted input types | 0.3 | 0.12 | Reviews endpoint accepts domain only — no URL/ID/search-query/geo-filter variety |
| Endpoint breadth for the platform | 0.3 | 0.12 | Only 3 endpoints for Trustpilot Reviews (Task POST / Tasks Ready / Task GET) |
| Enrichment/related endpoints | 0.2 | 0.08 | A separate Trustpilot Search endpoint exists (business discovery) but was not exercised in this benchmark |

---

## Aggregate score: **7.85 / 10 → Strong — minor trade-offs** (7.5–8.9 band, per `docs/testing-criteria.md` §5)

| Criterion | Score | /5 stars |
|---|---:|---:|
| 1. Success Rate & Reliability | 1.90/2.0 | ★★★★★ (4.8) |
| 2. Data Quality & Completeness | 1.88/2.0 | ★★★★★ (4.7) |
| 3. Cost Efficiency | 1.10/1.5 | ★★★★☆ (3.7) |
| 4. Speed & Throughput | 1.32/1.5 | ★★★★☆ (4.4) |
| 5. Scalability | 0.60/1.2 | ★★★☆☆ (2.5) |
| 6. Developer Experience | 0.73/1.0 | ★★★★☆ (3.7) |
| 7. Input Flexibility & Coverage | 0.32/0.8 | ★★☆☆☆ (2.0) |

**Biggest drag on the score: Scalability and Input Flexibility** — both suffer from this benchmark simply not having tested 10x load or exercised alternate input types/endpoints, not from any observed failure. See `reports/dataforseo-missing-evidence.md` for exactly what would need to be tested to move those scores.
