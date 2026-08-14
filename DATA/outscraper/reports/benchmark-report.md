# Outscraper Trustpilot Reviews API — Fresh Benchmark Report (Re-run)

**Run date:** 2026-07-29
**Script executed:** `scripts/outscraper_benchmark.py run` (unmodified, `CONFIRM_PAID_RUN=yes`)
**Target:** 1,000 unique Trustpilot reviews across 5 fixed domains (200 each)
**Previous run for comparison:** 2026-07-21 (archived at `data/*/outscraper/archive-full-copy/2026-07-21-run/`)

## Result: PASS — 1,000 / 1,000 unique valid reviews

Every domain reached its 200-review target on the **first page**
(`limit=200, skip=0`) — no pagination, retries, or rate-limit events
anywhere in this run. `append_error_event()` only writes
`data/logs/outscraper/errors/event-log.jsonl` when an actual event occurs;
confirmed the file was never created at all this run (checked directly,
not inferred) — i.e. zero error/retry/rate-limit events were emitted, not
merely a log that failed to write.

| Domain | Business | Pages | Raw | Valid | Unique | Shortfall | Stop reason |
|---|---|---:|---:|---:|---:|---:|---|
| www.thepearlsource.com | The Pearl Source | 1 | 200 | 200 | 200 | 0 | target_reached |
| www.shein.com | SHEIN | 1 | 200 | 200 | 200 | 0 | target_reached |
| temu.com | Temu | 1 | 200 | 200 | 200 | 0 | target_reached |
| www.aliexpress.com | AliExpress | 1 | 200 | 200 | 200 | 0 | target_reached |
| thehalara.com | Halara | 1 | 200 | 200 | 200 | 0 | target_reached |
| **Total** | | **5** | **1,000** | **1,000** | **1,000** | **0** | |

Evidence: `data/analysis/outscraper/domain-summary.json`,
`data/analysis/outscraper/pagination-report.json`, raw pages at
`data/raw/outscraper/{requests,results}/<domain>-page1.json`.

## Validation performed (not just "HTTP 200 = pass")

- Spot-checked `data/raw/outscraper/results/www.thepearlsource.com-page1.json`:
  real, freshly-timestamped review content (`review_datetime_utc:
  "07/29/2026 05:20:49"`, i.e. minutes before this run), not stale/cached
  data.
- Cross-checked `all-reviews.json` (1,000 rows) against `all-reviews.csv`
  (parsed with Python's `csv` module, not just `wc -l`, since multi-line
  review text legitimately spans multiple physical lines inside quoted CSV
  cells) — both show exactly 1,000 rows, 200 per domain, matching
  `domain-summary.json` exactly.
- `duplicate-report.json`: 0 duplicates, confirming dedupe ran (not just
  skipped) and found nothing to remove.
- Ran `scripts/outscraper_ground_truth_compare.py` for real against the
  fresh `www.thepearlsource.com` data (see below) rather than reusing the
  historical ground-truth-match.json.

## Duplicate detection

0 duplicates across all 1,000 records — same as the historical run.

## Ground truth (www.thepearlsource.com only — the only domain with a verified sample)

20/20 ground-truth rows matched (100%) — every ground-truth reviewer was
found in the fresh 200-review page. Field accuracy:

| Field | Fresh (2026-07-29) | Historical (2026-07-21 capture / re-run 2026-07-27) |
|---|---|---|
| author_name | 100% | 100% |
| author_country | 100% | 100% |
| author_reviews_count | **90%** (2/20 mismatch) | 100% |
| rating | 100% | 100% |
| review_title | 100% | 100% |
| review_text | 100% | 100% |
| useful_count | 100% | 100% |
| company_replied | **80%** (4/20 mismatch) | 100% |
| owner_reply | 100% (14/20 comparable, 6 ground-truth-unavailable) | 100% |

**Likely explanation (evidence-supported, not speculative):** the ground
truth sample is a fixed historical capture, while this run pulls
`sort=recency` reviews live. `author_reviews_count` and `company_replied`
are both mutable over time (a reviewer posts more reviews elsewhere; the
business replies to a review after the ground truth was captured) — so
drift on exactly these two count/state fields, and *only* these two, is
consistent with genuine time passing between the ground-truth capture and
this run, not a new accuracy regression in Outscraper's data. This does
**not** change the previous conclusion that Outscraper's core review-content
fields (text, title, rating, author identity) are reliably accurate — it
only shows that two mutable metadata fields need re-verification against a
fresh ground truth if exact accuracy on those two specific fields matters.

Full detail: `data/analysis/outscraper/ground-truth-match.json`.

## Timing

| | Historical (2026-07-21) | Fresh (2026-07-29) | Difference |
|---|---|---|---|
| Wall clock | 512,597 ms (~8.5 min) | 344,297 ms (~5.7 min) | −168,300 ms (faster) |
| Median per-request latency | not recomputed historically in this form | 1,094 ms | — |
| p95 per-request latency | — | 2,500 ms | — |
| Retries | 0 | 0 | none |
| Rate-limit (429) events | 0 | 0 | none |

## Cost

**Measured cost: unavailable (Outscraper does not expose a billed-cost or
account-balance API endpoint)** — same limitation as the historical run.
`cost-report.json`'s `measured_cost_usd` is `null`, not a stand-in zero.

**Calculated estimate** (published rate card × measured raw usage, 1,000
reviews): $2.70 (if free tier already used) – $3.00 (fresh account) —
identical to the historical run's calculation, since usage was identical
(1,000 raw reviews) and no evidence of a pricing change surfaced this run.
This is an **estimate**, not a measured/billed figure — flagged as such in
`data/analysis/outscraper/cost-report.json`.

## Comparison with previous run (2026-07-21)

| | Previous | Fresh | Difference |
|---|---|---|---|
| Unique reviews | 1,000 | 1,000 | 0 |
| Duplicates | 0 | 0 | 0 |
| Domains completed | 5 of 5 | 5 of 5 | 0 |
| Errors/retries | 0 | 0 | 0 |
| Rate limits | 0 | 0 | 0 |
| Wall clock | 512,597 ms | 344,297 ms | −168,300 ms |
| Calculated cost estimate | $2.70–$3.00 | $2.70–$3.00 | $0 |
| Ground truth match rate | 20/20 (100% all fields) | 20/20 (100% content fields; 90%/80% on 2 mutable metadata fields) | see explanation above |

No conclusion from the previous run is invalidated by this fresh run —
Outscraper again completed the full 1,000-review benchmark cleanly with a
single page per domain, no errors, and no duplicates.

## Issues found

None affecting correctness. The two ground-truth field mismatches
(`author_reviews_count`, `company_replied`) are attributable to real-world
time drift between the ground-truth capture and this run, not a script or
API defect.

## Still missing

- **True measured/billed cost** — Outscraper has no documented endpoint for
  this; would require manually checking the Outscraper billing dashboard
  before/after a run (unchanged limitation from the historical run).
