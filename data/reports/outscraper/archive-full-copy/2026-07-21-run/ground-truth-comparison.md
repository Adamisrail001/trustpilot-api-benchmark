# Outscraper Trustpilot Reviews API — Ground Truth Comparison

**Scope: `www.thepearlsource.com` only.** As with the DataForSEO benchmark, accuracy is not claimed for `www.shein.com`, `temu.com`, `www.aliexpress.com`, or `thehalara.com` — no manually-verified ground-truth sample exists for those domains. Their accuracy remains **Pending**.

Full row-by-row data: [outputs/outscraper/ground-truth-match.json](../../outputs/outscraper/ground-truth-match.json)
Matching method: each of the 20 ground-truth rows matched to a live Outscraper review by author name — all 20 matched uniquely, no ambiguous or unmatched rows.

## Match rate

- Ground-truth rows: 20
- Matched to a live review: 20 / 20 (100%)
- API items available to match against: 200

## Field-level accuracy (measured, over the 20 matched rows)

| Field | Match | Mismatch | Not returned by API | Ground truth unavailable | Accuracy |
|---|---:|---:|---:|---:|---:|
| author_name | 20 | 0 | 0 | 0 | 100% |
| author_country | 20 | 0 | 0 | 0 | 100% |
| author_reviews_count | 20 | 0 | 0 | 0 | 100% |
| rating | 20 | 0 | 0 | 0 | 100% |
| review_title | 20 | 0 | 0 | 0 | 100% |
| review_text | 20 | 0 | 0 | 0 | 100% |
| review_date (absolute) | 0 | 0 | 0 | 20 | N/A — ground truth only recorded a relative display string, never an absolute date |
| review_type (Invited status) | 0 | 0 | 20 | 0 | N/A — field does not exist in the API response |
| useful_count | 20 | 0 | 0 | 0 | **100%** — Outscraper's `review_likes` matched every ground-truth `useful_count` value exactly, including the one non-zero case (MR KEARNEY: 1) |
| company_replied | 20 | 0 | 0 | 0 | 100% |
| owner_reply | 14 | 0 | 0 | 6 | 100% (of the 14 rows where a reply existed; the other 6 had `owner_reply: null` in ground truth and were correctly skipped) |

**Zero mismatches on any field both sources captured** — same result as the DataForSEO run, but with one additional field (`useful_count` / `review_likes`) now verifiable and matching perfectly.

## Freshness

Ground truth was captured 2026-07-21; this run executed the same day and returned `review_datetime_utc` values from `07/21/2026 01:12:39` (newest) down through `07/16/2026` for the oldest of the 200 — live, current data, not a stale cache. `sort=recency` produced the same review ordering as the ground truth capture.

## Cross-API corroboration

The `review_id` Outscraper returned for the newest review (Linda B, "The Hanadama Pearl earrings") — `6a5eab67673db7c0e3922f0a` — is identical to the Trustpilot review-URL slug DataForSEO returned for the same review in the earlier benchmark, and both APIs reported the same rating (5), same review text, and the same underlying timestamp. Independent confirmation that both tools are reading the same live Trustpilot record correctly.

## Fields the API cannot be scored on

`review_type` (Invited vs. organic) is the only ground-truth field with no equivalent anywhere in Outscraper's documented or observed schema.
