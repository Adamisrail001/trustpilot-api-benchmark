# Lobstr.io Trustpilot Reviews — Ground Truth Comparison

**Scope: `www.thepearlsource.com`.** 20/20 ground-truth rows matched uniquely by `author_name` against the 200 live results for this domain.

## Field-level accuracy

| Field | Match | Mismatch | Not returned | GT unavailable | Accuracy |
|---|---:|---:|---:|---:|---:|
| author_name | 20 | 0 | 0 | 0 | 100% |
| author_country | 20 | 0 | 0 | 0 | 100% |
| author_reviews_count | 20 | 0 | 0 | 0 | 100% |
| rating | 20 | 0 | 0 | 0 | 100% |
| review_title | 20 | 0 | 0 | 0 | 100% |
| review_text | 20 | 0 | 0 | 0 | 100% |
| review_date (absolute) | 0 | 0 | 0 | 20 | N/A — ground truth only recorded relative strings |
| review_type (Invited, heuristic) | 19 | 0 | 0 | 1 | 100% of comparable rows |
| useful_count | 20 | 0 | 0 | 0 | 100% |
| company_replied | 16 | **4** | 0 | 0 | 80% — see below, not a data error |
| owner_reply (text) | 14 | 0 | 0 | 6 | 100% |
| owner_reply_date | 0 | 14 | 0 | 6 | 0% literal — format artifact, see below |

## The 4 `company_replied` mismatches — now confirmed by THREE independent tools

**Linda B, Human Sun, Sharon R., and MW** — the exact same 4 authors flagged by both the OpenWeb Ninja and Apify benchmarks earlier in this project. All three independently-implemented tools agree: The Pearl Source posted replies to these 4 specific reviews in the window between the ground-truth capture (2026-07-21) and each benchmark's run date. This is now about as thoroughly cross-validated as a "freshness, not an error" finding can get.

## `owner_reply_date` — format artifact, not a real mismatch

Same explanation as the OpenWeb Ninja and Apify reports: ground truth recorded only relative display strings (e.g. "1 days ago"); Lobstr returns absolute ISO timestamps. The `owner_reply` **text** matched exactly on all 14 comparable rows — the underlying data is accurate, only the literal string comparison fails by design.

## Freshness

Timestamps current as of the run date; `sort` behavior (recency-equivalent, via the squid's default ordering) matched the ground truth's top-of-list ordering.
