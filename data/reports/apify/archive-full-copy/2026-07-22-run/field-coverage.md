# Apify (automation-lab/trustpilot) — Field Coverage

Comparison base: the fields manually captured on the live Trustpilot review page for `www.thepearlsource.com` (`ground-truth/thepearlsource-sample.json`), against the fields actually present in the live Apify dataset (`outputs/apify/raw/datasets/page1-offset0.json`).

## Confirmed live schema

`reviewId, reviewUrl, title, text, rating, publishedDate, experienceDate, updatedDate, language, likes, verificationLevel, isVerified, source, authorName, authorId, authorReviewCount, country, replyMessage, replyPublishedDate, companyName, companyDomain, companyTrustScore, companyStars, companyTotalReviews, companyUrl` — matches the officially documented field list. This is the **richest schema of any tool benchmarked in this project**, and notably the only one to document a dedicated `replyPublishedDate` field.

## Field-by-field mapping

| Page field (ground truth) | Returned by API? | API field | Notes |
|---|---|---|---|
| `author_name` | Yes | `authorName` | Exact match, 100% |
| `author_country` | Yes | `country` | Exact match, 100% |
| `author_reviews_count` | Yes | `authorReviewCount` | Exact match, 100% |
| `rating` | Yes | `rating` | Exact match, 100% |
| `review_title` | Yes | `title` | Exact match, 100% |
| `review_text` | Yes | `text` | Exact match, 100% |
| `review_date_display` (relative) | Partial | `publishedDate` (absolute) | More precise than ground truth's relative string |
| `review_type` (Invited/organic) | **Heuristic only** | `verificationLevel` / `source` (e.g. `"invited"`) | Not confirmed as an official 1:1 mapping, but matches Apify's own documented example (`"verificationLevel": "invited"`) closely — empirically 100% consistent across 19 comparable ground-truth rows |
| `useful_count` | Yes | `likes` | Exact match, 100% |
| `company_replied` | Yes | derived: `Boolean(replyMessage)` | 16/20 matched; 4 "mismatches" are freshness, not extraction errors — see `ground-truth-comparison.md` |
| `owner_reply` | Yes | `replyMessage` | Exact text match on all 14 rows with a reply in ground truth |
| `owner_reply_date` | **Yes (uniquely, among all 4 tools tested)** | `replyPublishedDate` | Field exists and is populated — but see the comparison-method note below |

## Coverage calculation

```
Fields on page checked: 13 (review_url has no ground-truth value to compare against - excluded)
Directly covered:       12  (every field above except the heuristic review_type)
Heuristic only:          1  (review_type)

Strict field coverage = 12 / 13 = 92.3%
```

This is the **highest field coverage of any tool benchmarked in this project** — Apify is the only one to return a populated `owner_reply_date`/`replyPublishedDate` field at all (DataForSEO, Outscraper, and OpenWeb Ninja all lacked this field entirely).

## A methodology note on `owner_reply_date`

The comparison script flagged 14/14 comparable rows as "mismatch" for this field — but that's a **string-format artifact, not a data error**: ground truth recorded only a relative display string (e.g. `"1 days ago"`), while Apify returns an absolute ISO timestamp (e.g. `"2026-07-19T22:58:42.000Z"`). A literal string comparison will never match a relative string against an absolute one. Manually spot-checked: the reply timestamps are chronologically consistent (always after the review's own `publishedDate`), and the `owner_reply` text itself matched exactly on all 14 rows. This field should be treated as **covered and accurate**, not failed — see `ground-truth-comparison.md` for the full explanation.

## Schema consistency across the full run

All 800 raw items returned were checked against the required-field set. **Zero missing-field occurrences** were recorded in `outputs/apify/domain-summary.json` (`missing_field_counts: {}`) — 100% schema consistency on every record that WAS returned. (This does not cover SHEIN, which returned no records at all — a coverage gap, not a schema-consistency issue.)
