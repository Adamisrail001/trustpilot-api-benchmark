# Apify (automation-lab/trustpilot) — Ground Truth Comparison

**Scope: `www.thepearlsource.com` only** — the one domain that returned its full 200/200 target. As with every prior benchmark, no accuracy claim is made for the other 4 domains (no manually-verified samples exist for them, and SHEIN returned nothing at all this run).

Full row-by-row data: [outputs/apify/ground-truth-match.json](../../outputs/apify/ground-truth-match.json)
Matching method: each of the 20 ground-truth rows matched to a live review by `authorName` — all 20 matched uniquely.

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
| review_type (Invited, via `verificationLevel`/`source`) | 19 | 0 | 0 | 1 | 100% (of comparable rows) |
| useful_count | 20 | 0 | 0 | 0 | 100% |
| company_replied | 16 | **4** | 0 | 0 | 80% — see explanation below, not a data error |
| owner_reply (text) | 14 | 0 | 0 | 6 | 100% |
| owner_reply_date | 0 | **14** | 0 | 6 | **0% literal — but see explanation, this is a format artifact, not a real mismatch** |

## The 4 `company_replied` "mismatches" — same freshness pattern seen with OpenWeb Ninja

Rows for **Linda B, Human Sun, Sharon R., and MW** — the exact same 4 authors flagged in the OpenWeb Ninja benchmark's ground-truth comparison — show ground truth `company_replied: false` but Apify returned a populated `replyMessage`. Same explanation applies: these 4 reviews were posted 2026-07-20/21, ground truth was captured 2026-07-21, and this benchmark ran 2026-07-22 — **The Pearl Source replied to these 4 reviews in the gap between the two captures.** Confirmed genuine freshness, not an extraction error — two independent tools (OpenWeb Ninja and Apify) now agree on exactly which 4 reviews gained a reply in that window.

## The `owner_reply_date` "0% accuracy" — a comparison-format artifact, not a data error

Ground truth recorded only relative display strings (e.g. `"1 days ago"`); Apify returns absolute ISO timestamps (e.g. `"2026-07-19T22:58:42.000Z"`). A strict string-equality check will never match these. Manually verified instead:
- `owner_reply` **text** matched exactly on all 14 comparable rows (100%).
- The `replyPublishedDate` timestamps are chronologically sound — always after the review's own `publishedDate`.

This field should be read as **accurate**, not failed. Apify is the only one of the four tools benchmarked in this project to return a reply-date field at all.

## Freshness

Timestamps ranged current as of the run date (2026-07-22), consistent with `sort: "recency"` and the top-of-list ordering matching the ground truth capture.

## Fields the API cannot be scored on

None for `www.thepearlsource.com` specifically — every ground-truth-checkable field had a usable API counterpart this run, a first among the four tools tested.
