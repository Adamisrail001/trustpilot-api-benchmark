# Lobstr.io Trustpilot Reviews — Field Coverage

Comparison base: ground-truth fields for `www.thepearlsource.com` vs. the live Lobstr response (`outputs/lobstr/raw/results/*.json`).

## Confirmed live schema (37 fields per result item)

`id, object, run, author_id, author_image, author_name, business_unit_id, company_category, company_name, company_page_url, consumer_country_code, consumer_reviews_on_domain, date_published, experience_date, functions, is_author_verified, is_review_verified, likes, native_id, number_of_reviews, owner_reply, owner_reply_date, owner_reply_updated_date, page_number, rating_value, report, review_body, review_headline, review_language, review_link, review_sentiment, review_source, review_url, review_verification_source, reviews_count, scraping_time, stars, trust_score, updated_date, verification_level` — the richest schema of any tool benchmarked in this project.

Note: `review_url` is the bare Trustpilot review hex ID (not a URL); the full URL is in `review_link`. This was a real bug source (see `error-investigation.md`), now corrected in the dedupe/normalization adapter.

## Field-by-field mapping

| Page field | Returned? | API field | Notes |
|---|---|---|---|
| author_name | Yes | `author_name` | 100% match |
| author_country | Yes | `consumer_country_code` | 100% match |
| author_reviews_count | Yes | `number_of_reviews` | 100% match |
| rating | Yes | `rating_value` (also `stars`) | 100% match |
| review_title | Yes | `review_headline` | 100% match |
| review_text | Yes | `review_body` | 100% match |
| review_date (absolute) | Yes | `date_published` | more precise than ground truth's relative string |
| review_type (Invited) | Heuristic only | `verification_level` / `review_source` | not an officially documented mapping, but 100% consistent across 19 comparable rows |
| useful_count | Yes | `likes` | 100% match |
| company_replied | Yes | derived: `Boolean(owner_reply)` | 16/20 matched; 4 explained by cross-tool-confirmed freshness |
| owner_reply | Yes | `owner_reply` | 100% text match on all 14 rows with a reply |
| owner_reply_date | Yes (field exists and is populated) | `owner_reply_date` | absolute timestamp vs. ground truth's relative string — see ground-truth-comparison.md |
| review_url | Yes | `review_url` (bare ID) / `review_link` (full URL) | both present |

## Coverage calculation

```
Fields checked: 13
Directly covered: 12
Heuristic only: 1 (review_type)

Strict field coverage = 12/13 = 92.3%
```

## Schema consistency

0 missing-field occurrences across all 1,000 raw items (`missing_field_counts: {}` in `domain-summary.json`).
