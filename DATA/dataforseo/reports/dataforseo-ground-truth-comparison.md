# DataForSEO Trustpilot Reviews API — Ground Truth Comparison

**Scope: `www.thepearlsource.com` only.** Per the approved rules, accuracy is not claimed for `www.shein.com`, `temu.com`, `www.aliexpress.com`, or `thehalara.com` — no manually-verified ground-truth sample exists for those domains (`ground_truth_file: null` in `benchmark-domains.json`). Their accuracy is marked **Pending** until a manually-verified sample is provided.

Full row-by-row data: [outputs/dataforseo/ground-truth-match.json](../outputs/dataforseo/ground-truth-match.json)
Matching method: each of the 20 ground-truth rows was matched to an API review by author name (all 20 matched uniquely; no ambiguous or unmatched rows).

## Match rate

- Ground-truth rows: 20
- Matched to an API review: 20 / 20 (100%)
- API items available to match against: 200 (the full retrieved set for this domain)

## Field-level accuracy (measured, over the 20 matched rows)

| Field | Match | Mismatch | Not returned by API | Ground truth unavailable | Accuracy |
|---|---:|---:|---:|---:|---:|
| author_name | 20 | 0 | 0 | 0 | 100% |
| author_country | 20 | 0 | 0 | 0 | 100% |
| author_reviews_count | 20 | 0 | 0 | 0 | 100% |
| rating | 20 | 0 | 0 | 0 | 100% |
| review_title | 20 | 0 | 0 | 0 | 100% |
| review_text | 20 | 0 | 0 | 0 | 100% |
| review_date (absolute) | 0 | 0 | 0 | 20 | N/A — ground truth only recorded a relative display string ("3 days ago"), never an absolute date, so there is nothing to compare the API's absolute timestamp against |
| review_type (Invited status) | 0 | 0 | 20 | 0 | N/A — field does not exist in the API response |
| useful_count | 0 | 0 | 20 | 0 | N/A — field does not exist in the API response |
| company_replied | 20 | 0 | 0 | 0 | 100% |
| owner_reply | 14 | 0 | 0 | 6 | 100% (of the 14 rows where a reply existed in ground truth; the other 6 ground-truth rows had `owner_reply: null` and were correctly not compared) |

**Zero mismatches on any field that both sources actually captured.** Every author, country, reviewer review-count, rating, title, review text, company-reply flag, and owner-reply text matched exactly between the manually-verified sample and the live API response.

## Freshness

Ground truth was captured 2026-07-21. The API run was also executed 2026-07-21, and returned absolute timestamps ranging from `2026-07-21 01:12:39 +00:00` (newest) down to timestamps for `2026-07-18`/`2026-07-19` for the older rows — i.e., live, current data, not a stale cache. `sort_by=recency` produced the same review ordering as the manually-browsed ground truth (rank_absolute 1–5 corresponded exactly to ground-truth rows 1–5 in the same order).

## Fields the API cannot be scored on

`review_type` (Invited vs. organic) and `useful_count` (helpful-vote count) are not returned by the DataForSEO Trustpilot Reviews API in any documented or observed field — this is a genuine coverage gap, not a data-quality failure. See `reports/dataforseo-field-coverage.md` for the full field inventory.
