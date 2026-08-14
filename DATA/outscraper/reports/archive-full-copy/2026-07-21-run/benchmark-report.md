# Outscraper Trustpilot Reviews API — Benchmark Report

**Run date:** 2026-07-21
**Target:** 1,000 unique Trustpilot reviews across 5 fixed domains (200 each)

## Result: Benchmark completed — 1,000 / 1,000 unique valid reviews

Every domain reached its 200-review target on the **first page** (`limit=200, skip=0`) — no pagination, retries, or duplicates were needed anywhere in this run.

| Domain | Business | Pages | Raw | Valid | Unique | Shortfall | Stop reason |
|---|---|---:|---:|---:|---:|---:|---|
| www.thepearlsource.com | The Pearl Source | 1 | 200 | 200 | 200 | 0 | target_reached |
| www.shein.com | SHEIN | 1 | 200 | 200 | 200 | 0 | target_reached |
| temu.com | Temu | 1 | 200 | 200 | 200 | 0 | target_reached |
| www.aliexpress.com | AliExpress | 1 | 200 | 200 | 200 | 0 | target_reached |
| thehalara.com | Halara | 1 | 200 | 200 | 200 | 0 | target_reached |
| **Total** | | **5** | **1,000** | **1,000** | **1,000** | **0** | |

Full evidence: [outputs/outscraper/domain-summary.json](../../outputs/outscraper/domain-summary.json), [pagination-report.json](../../outputs/outscraper/pagination-report.json).

## Response-shape verification (requirement: inspect and fix before trusting the parser)

The parser's shape assumption (`data: [[...reviews]]`, grouped per query) was verified against the very first real response and matched exactly — no `shape_warning` was logged on any of the 5 pages, and no parser fix was needed. Confirmed live field set: `query, total_reviews, review_rating, review_title, review_text, review_likes, review_timestamp, review_datetime_utc, review_id, review_verified, author_title, author_id, author_image, author_reviews_number, author_reviews_number_same_domain, author_country_code, owner_answer, owner_answer_date` — matches the documented "Expected Review Fields" list exactly.

## Duplicate detection

0 duplicates across all 1,000 records. Every dedupe decision resolved at **tier 1 (native `review_id`)** — Outscraper reliably returns `review_id` on every record, so the URL and hash fallback tiers never had to fire. Evidence: [duplicate-report.json](../../outputs/outscraper/duplicate-report.json).

Cross-check: the `review_id` returned for Linda B's review on `www.thepearlsource.com` (`6a5eab67673db7c0e3922f0a`) is byte-identical to the Trustpilot review-URL slug DataForSEO returned for the same review in the earlier benchmark — independent confirmation both APIs are reading the same live Trustpilot record.

## Required measurements

| Metric | Value | Basis |
|---|---|---|
| Requested reviews | 1,000 | design |
| Total raw returned | 1,000 | measured |
| Total valid | 1,000 | measured |
| Total unique | 1,000 | measured |
| Duplicates | 0 | measured |
| Empty responses | 0 | measured |
| Partial responses | 0 | measured |
| Failed requests | 0 | measured |
| Retries | 0 | measured — every request succeeded on attempt 1 |
| Rate-limit (429) responses | 0 | measured |
| Median latency | 1,169 ms | measured — [timings.json](../../outputs/outscraper/timings.json) |
| p95 latency | 1,982 ms | measured |
| Wall-clock time | 512,595 ms (~8 min 33 s) | measured |
| Pagination requests used | 5 (1 per domain — no second page needed anywhere) | measured |
| Total usage (reviews) | 1,000 | measured |
| Calculated cost | $2.70–$3.00 | calculated from published tiers — see cost-report.md |
| Measured (billed) cost | Pending | no account-balance/billing endpoint is documented — see missing-evidence.md |

## Generated files

- `outputs/outscraper/raw/requests/*.json` (5), `raw/results/*.json` (5)
- `outputs/outscraper/errors/event-log.jsonl` (empty — 0 errors)
- `outputs/outscraper/timings.json`, `all-reviews.json`, `all-reviews.csv`, `duplicate-report.json`, `pagination-report.json`, `domain-summary.json`, `cost-report.json`, `ground-truth-match.json`, `execution-plan.json`
- `reports/outscraper/*.md` (this file + 6 others)

## Remaining blockers

None. The run is fully complete at target (1,000/1,000). The only open items are evidentiary, not blocking — see `reports/outscraper/missing-evidence.md`.
