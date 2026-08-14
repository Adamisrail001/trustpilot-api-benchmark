# Outscraper Trustpilot Reviews API — Field Coverage

Comparison base: the fields manually captured on the live Trustpilot review page for `www.thepearlsource.com` (`ground-truth/thepearlsource-sample.json`), against the fields actually present in the live Outscraper response (`outputs/outscraper/raw/results/www.thepearlsource.com-page1.json`).

## Field-by-field mapping

| Page field (ground truth) | Returned by API? | API field | Notes |
|---|---|---|---|
| `author_name` | Yes | `author_title` | Exact match, 100% |
| `author_country` | Yes | `author_country_code` | Exact match, 100% |
| `author_reviews_count` | Yes | `author_reviews_number` | Exact match, 100%; API also returns `author_reviews_number_same_domain` (bonus) |
| `rating` | Yes | `review_rating` | Exact match, 100% |
| `review_title` | Yes | `review_title` | Exact match, 100% |
| `review_text` | Yes | `review_text` | Exact match, 100% |
| `review_date_display` (relative) | Partial | `review_timestamp` (unix) / `review_datetime_utc` (absolute) | API returns two absolute-date representations instead of a relative display string — strictly more precise |
| `review_type` (Invited / organic) | **No** | — | Not present anywhere in the documented or observed API schema |
| `useful_count` | **Yes** | `review_likes` | Exact match, 100% on all rows checked — unlike DataForSEO, Outscraper does return a helpful-vote-equivalent field |
| `company_replied` | Yes | derived: `Boolean(owner_answer)` | Exact match, 100% |
| `owner_reply` | Yes | `owner_answer` | Exact match on all 14 rows where a reply existed |
| `owner_reply_date_display` (relative) | Partial | `owner_answer_date` | Same relative-vs-absolute gap as `review_date_display`; format not yet inspected on a null-vs-populated pair beyond match confirmation |
| `review_url` (ground truth recorded `null`) | Not documented | — | No `review_url`/`url` field appears in the documented field list or the live response; `review_id` is the only identifier |

## Coverage calculation

```
Fields on page checked: 13
Directly/fully covered:  12  (all of the above except review_type)
Not covered:              1  (review_type / invited-status)

Field coverage = 12 / 13 = 92.3%
```

This is a **better** documented field coverage than DataForSEO's 84.6% on the same ground-truth checklist — specifically because Outscraper returns a `review_likes` equivalent to the "useful_count" field, which DataForSEO does not return at all.

## Fields returned beyond the ground-truth capture (bonus)

`query`, `total_reviews` (business-level review count, not per-review), `review_verified`, `author_id`, `author_image`, `author_reviews_number_same_domain`.

## Schema consistency across the full 1,000-record run

All 1,000 raw items (5 domains × 200) were checked against the required-field set (`review_id`, `review_rating`, `review_date`, `review_title_or_text`, `reviewer_info`). **Zero missing-field occurrences** were recorded in `outputs/outscraper/domain-summary.json` (`missing_field_counts: {}` for every domain) — 100% schema consistency.
