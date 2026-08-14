# DataForSEO Trustpilot Reviews API — Field Coverage

Comparison base: the fields manually captured on the live Trustpilot review page for `www.thepearlsource.com` (`ground-truth/thepearlsource-sample.json`), against the fields actually present in the DataForSEO API response (`outputs/dataforseo/raw/task-get/www.thepearlsource.com.json`).

Static/contextual fields from the ground-truth file (`source`, `business_name`, `business_domain`, `manually_verified`, `collected_at`) are excluded — they describe the capture, not the review itself.

## Field-by-field mapping

| Page field (ground truth) | Returned by API? | API field | Notes |
|---|---|---|---|
| `author_name` | Yes | `items[].user_profile.name` | Exact match, 100% (see ground-truth-comparison.md) |
| `author_country` | Yes | `items[].user_profile.location` | Exact match, 100% |
| `author_reviews_count` | Yes | `items[].user_profile.reviews_count` | Exact match, 100% |
| `rating` | Yes | `items[].rating.value` | Exact match, 100%; API also returns `rating_type` and `rating_max` (bonus) |
| `review_title` | Yes | `items[].title` | Exact match, 100% |
| `review_text` | Yes | `items[].review_text` | Exact match, 100% |
| `review_date_display` (relative, e.g. "3 days ago") | Partial | `items[].timestamp` | API returns an **absolute** timestamp instead of a relative display string — strictly more precise, but not a like-for-like string match |
| `review_date` (ground truth captured this as `null` — no absolute date was recorded manually) | N/A | `items[].timestamp` | API is the only source of an absolute date here |
| `review_type` ("Invited" / organic) | **No** | — | Not present anywhere in the documented or observed API schema |
| `useful_count` (helpful-vote count) | **No** | — | Not present anywhere in the documented or observed API schema |
| `company_replied` | Yes | derived: `Boolean(items[].responses?.length)` | Exact match, 100% (API doesn't return this as an explicit boolean, but it's unambiguously derivable) |
| `owner_reply` | Yes | `items[].responses[0].text` | Exact match on all 14 rows where a reply existed |
| `owner_reply_date_display` (relative) | Partial | `items[].responses[0].timestamp` | Same relative-vs-absolute gap as `review_date_display` |
| `review_url` (ground truth recorded `null` for all rows — not manually collected) | Yes | `items[].url` | API is the only source of this |

## Coverage calculation

```
Fields on page checked: 13
Directly/fully covered:  11  (author_name, author_country, author_reviews_count,
                               rating, review_title, review_text, review_date,
                               company_replied, owner_reply, owner_reply_date, review_url)
Not covered:              2  (review_type/invited-status, useful_count)

Field coverage = 11 / 13 = 84.6%
```

Two ground-truth fields (`review_date_display`, `owner_reply_date_display`) are counted as covered because the API returns a strictly more precise absolute-timestamp equivalent, even though the exact relative-display string isn't reproduced.

## Fields the API returns beyond the ground-truth capture (bonus, not penalized or rewarded in the coverage %)

`rank_group`, `rank_absolute`, `position`, `verified` (Trustpilot's own verification flag), `language`, `review_images`, `rating.rating_type`, `rating.rating_max`, `rating.votes_count`, `user_profile.url`, `user_profile.image_url`.

## Schema consistency across the full 1,000-record run

All 1,000 raw items (across all 5 domains) were checked against the same required-field set (`id_or_url`, `rating`, `date`, `review_text`, `title`, `reviewer_info`). **Zero missing-field occurrences** were recorded in `outputs/dataforseo/domain-summary.json` (`missing_field_counts: {}` for every domain) — the item schema was 100% consistent across all 1,000 records.
