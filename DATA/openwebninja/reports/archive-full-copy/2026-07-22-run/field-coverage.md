# OpenWeb Ninja Trustpilot Reviews API — Field Coverage

Comparison base: the fields manually captured on the live Trustpilot review page for `www.thepearlsource.com` (`ground-truth/thepearlsource-sample.json`), against the fields actually present in the live OpenWeb Ninja response (`outputs/openwebninja/raw/results/www.thepearlsource.com-page*.json`).

## Confirmed live schema

`review_id, review_title, review_text, review_rating, review_is_verified, review_is_pending, review_likes, review_language, review_time, review_source, review_experienced_time, reply_text, consumer_id, consumer_name, consumer_review_count, consumer_country, consumer_is_verified, consumer_review_count_same_domain` — matches the officially documented field list exactly, confirmed against real data.

## Field-by-field mapping

| Page field (ground truth) | Returned by API? | API field | Notes |
|---|---|---|---|
| `author_name` | Yes | `consumer_name` | Exact match, 100% |
| `author_country` | Yes | `consumer_country` | Exact match, 100% |
| `author_reviews_count` | Yes | `consumer_review_count` | Exact match, 100% |
| `rating` | Yes | `review_rating` | Exact match, 100% |
| `review_title` | Yes | `review_title` | Exact match, 100% |
| `review_text` | Yes | `review_text` | Exact match, 100% |
| `review_date_display` (relative) | Partial | `review_time` (absolute) | More precise than the ground truth's relative string |
| `review_type` (Invited/organic) | **Heuristic only** | `review_source` (e.g. `"InvitationLinkApi"`) | **Not an officially documented equivalent** — inferred by pattern-matching `/invit/i` against `review_source`. Empirically 100% consistent across all 19 comparable ground-truth rows this run, but this is a discovered correlation, not a documented field mapping — treat with appropriate caution on other domains. |
| `useful_count` | Yes | `review_likes` | Exact match, 100% |
| `company_replied` | Yes | derived: `Boolean(reply_text)` | 16/20 matched; 4 "mismatches" are **not extraction errors** — see `ground-truth-comparison.md` for the freshness explanation |
| `owner_reply` | Yes | `reply_text` | Exact match on all 14 rows where ground truth recorded a reply |
| `owner_reply_date` | **No** | — | No reply-timestamp field exists anywhere in the documented or observed schema |
| `review_url` | **No** | — | No URL/link field exists for reviews in this API; `review_id` (a Trustpilot review hex ID) is the only identifier, which is sufficient for deduplication but not a clickable URL |

## Coverage calculation

```
Fields on page checked: 13
Directly covered:        10  (author_name, author_country, author_reviews_count, rating,
                               review_title, review_text, review_date, useful_count,
                               company_replied, owner_reply)
Heuristic only:            1  (review_type - not an official mapping)
Not covered:               2  (owner_reply_date, review_url)

Strict field coverage = 10 / 13 = 76.9%
Coverage including the heuristic review_type match = 11 / 13 = 84.6%
```

## Schema consistency across the full 1,000-record run

All 1,000 raw items (5 domains × 10 pages × 20) were checked against the required-field set. **Zero missing-field occurrences** were recorded in `outputs/openwebninja/domain-summary.json` (`missing_field_counts: {}` for every domain) — 100% schema consistency.
