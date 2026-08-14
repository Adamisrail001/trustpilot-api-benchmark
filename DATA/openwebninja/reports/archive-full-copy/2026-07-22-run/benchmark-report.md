# OpenWeb Ninja Trustpilot Reviews API — Benchmark Report

**Run date:** 2026-07-22
**Endpoint:** `GET /company-reviews` (sort=recency, pages 1–10, no cookie)

## Result: Benchmark completed — 1,000 / 1,000 unique valid reviews

All 5 domains reached their 200-review target across the full 10 pages each — no shortfalls, no duplicates, no domain substitutions.

| Domain | Business | Pages | Raw | Valid | Unique | Shortfall | Stop reason |
|---|---|---:|---:|---:|---:|---:|---|
| www.thepearlsource.com | The Pearl Source | 10 | 200 | 200 | 200 | 0 | target_reached |
| www.shein.com | SHEIN | 10 | 200 | 200 | 200 | 0 | target_reached |
| temu.com | Temu | 10 | 200 | 200 | 200 | 0 | target_reached |
| www.aliexpress.com | AliExpress | 10 | 200 | 200 | 200 | 0 | target_reached |
| thehalara.com | Halara | 10 | 200 | 200 | 200 | 0 | target_reached |
| **Total** | | **50** | **1,000** | **1,000** | **1,000** | **0** | |

Full evidence: [outputs/openwebninja/domain-summary.json](../../outputs/openwebninja/domain-summary.json), [pagination-report.json](../../outputs/openwebninja/pagination-report.json).

## Retries and errors

One `HTTP 500` occurred on `www.thepearlsource.com` page 1 (attempt 1), correctly retried per policy (network/429/5xx only) and succeeded on attempt 2. Zero other errors across all 50 requests. Full detail: [error-log.json](../../outputs/openwebninja/error-log.json).

## Duplicate detection

**Zero duplicates across all 1,000 records.** No native review-URL field exists in this API's schema, so deduplication relied on tier 1 (`review_id`, always present) — never needed to fall through to the hash fallback. Evidence: [duplicate-report.json](../../outputs/openwebninja/duplicate-report.json).

## Required measurements

| Metric | Value | Basis |
|---|---|---|
| Requested reviews | 1,000 | design |
| Total raw returned | 1,000 | measured |
| Total valid | 1,000 | measured |
| Total unique | 1,000 | measured |
| Duplicates | 0 | measured |
| Empty/partial responses | 0 | measured — every one of the 50 pages returned exactly 20 items |
| Failed requests | 0 | measured (the one 500 was retried to success, not a final failure) |
| Retries | 1 | measured |
| Total requests made | 50 | measured — exactly matches the pre-run plan (5 domains × 10 pages), no waste |
| Median latency | 1,870 ms | measured — [timings.json](../../outputs/openwebninja/timings.json) |
| p95 latency | 3,684 ms | measured — consistent with the vendor's published "1–5 seconds" typical response time |
| Wall-clock time | 180,749 ms (~3 min 1 s) | measured |
| Quota consumed | 50 of the 100 remaining (confirmed by you via dashboard before the run) | measured |
| Estimated cost | $0–$0.25 depending on plan tier (see cost-report.md) | calculated |
| Measured (billed) cost | Pending — no quota/usage API endpoint exists to confirm the "Basic" plan's rate | see missing-evidence.md |

## Generated files

- `outputs/openwebninja/raw/requests/*.json` (50), `raw/results/*.json` (50)
- `outputs/openwebninja/{timings,all-reviews,duplicate-report,pagination-report,domain-summary,run-state,cost-report,ground-truth-match,execution-plan,preflight-report,error-log}.json`, `all-reviews.csv`
- `reports/openwebninja/*.md` (this file + 6 others)

## Remaining blockers

None. The run completed fully at target on the first attempt.
