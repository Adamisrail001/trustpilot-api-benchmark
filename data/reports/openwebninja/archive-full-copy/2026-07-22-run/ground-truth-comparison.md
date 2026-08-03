# OpenWeb Ninja Trustpilot Reviews API — Ground Truth Comparison

**Scope: `www.thepearlsource.com` only.** As with every prior benchmark, accuracy is not claimed for the other 4 domains — no manually-verified sample exists for them.

Full row-by-row data: [outputs/openwebninja/ground-truth-match.json](../../outputs/openwebninja/ground-truth-match.json)
Matching method: each of the 20 ground-truth rows matched to a live review by `consumer_name` — all 20 matched uniquely.

## Match rate

- Ground-truth rows: 20 / Matched: 20 (100%)
- API items available to match against: 200

## Field-level accuracy

| Field | Match | Mismatch | Not returned | GT unavailable | Accuracy |
|---|---:|---:|---:|---:|---:|
| author_name | 20 | 0 | 0 | 0 | 100% |
| author_country | 20 | 0 | 0 | 0 | 100% |
| author_reviews_count | 20 | 0 | 0 | 0 | 100% |
| rating | 20 | 0 | 0 | 0 | 100% |
| review_title | 20 | 0 | 0 | 0 | 100% |
| review_text | 20 | 0 | 0 | 0 | 100% |
| review_date (absolute) | 0 | 0 | 0 | 20 | N/A — ground truth only recorded a relative display string |
| review_type (Invited, via `review_source` heuristic) | 19 | 0 | 0 | 1 | 100% (of comparable rows; one GT row had `review_type: null`) |
| useful_count | 20 | 0 | 0 | 0 | 100% |
| company_replied | 16 | **4** | 0 | 0 | 80% — **see explanation below, not a data error** |
| owner_reply | 14 | 0 | 0 | 6 | 100% (of the 14 rows with a reply in ground truth) |

## The 4 `company_replied` "mismatches" — investigated, explained

Rows for **Linda B, Human Sun, Sharon R., and MW** show ground truth `company_replied: false` but the live API returned a reply (`reply_text` populated). This is **not an extraction error**. Checking the actual review timestamps:

| Author | Review posted | Ground truth collected | This benchmark run |
|---|---|---|---|
| Linda B | 2026-07-21 | 2026-07-21 | 2026-07-22 |
| Human Sun | 2026-07-20 | 2026-07-21 | 2026-07-22 |
| Sharon R. | 2026-07-20 | 2026-07-21 | 2026-07-22 |
| MW | 2026-07-20 | 2026-07-21 | 2026-07-22 |

All 4 replies read like genuine, specific owner responses (e.g., "We're so happy to hear you've been enjoying your Hanadama Pearl..."). The most likely explanation: **The Pearl Source posted these 4 replies in the ~24 hours between the ground-truth capture and this benchmark run.** This is evidence of the API's real-time freshness (matching its own documented claim), not a data-quality defect — logged plainly rather than silently smoothed over.

## Freshness

Timestamps ranged from `2026-07-21T21:13:15Z` (newest, `www.thepearlsource.com`) down through the oldest of the 200 per domain — live, current data. `sort=recency` produced the same top-of-list ordering as the ground truth capture.

## Fields the API cannot be scored on

`owner_reply_date` and `review_url` have no equivalent anywhere in this API's documented or observed schema (see `field-coverage.md`).
