# OpenWeb Ninja Trustpilot Reviews API — Final Verdict

## Benchmark completed: 1,000 unique reviews

All 5 approved domains reached exactly 200 unique valid reviews each, for a clean 1,000/1,000 total. No shortfalls, no duplicates, no domain substitutions, one transient error (HTTP 500) correctly retried to success.

## Elimination: Not eliminated (E1–E6 all pass; E4 flagged, not failed)

## Provisional score: 7.47/10 — Usable with caveats, right at the edge of "Strong"

Excellent reliability (1.98/2.0) and data quality (1.82/2.0) — matching or exceeding every prior tool benchmarked in this project on accuracy. Held back by:
- **Cost uncertainty**: the account's actual "Basic" plan doesn't appear in the published rate card, so the real cost-per-1,000-reviews figure is unconfirmed (range: $0–$0.25 across the tiers that *are* published).
- **Low measured throughput ceiling**: a documented 100-requests/month cap on lower tiers, and no async/batch capability, versus tools like Outscraper (1,000-query batching) or DataForSEO (bulk task submission).

## Where this tool fits

If cost and volume aren't primary concerns, OpenWeb Ninja is a strong, well-documented, accurate option — its 9-endpoint coverage (company/category/consumer data, not just reviews) is broader than any other tool tested in this project. It is not automatically the winner of the aggregate benchmark; that determination requires comparing this 7.47 against DataForSEO's and Outscraper's final scores side by side (Lobstr.io remains unscored — its one run was invalidated by a contaminated squid, not a tool failure).

## Confirmed facts worth carrying into any cross-tool writeup

- Endpoint: `GET https://api.openwebninja.com/trustpilot-company-and-reviews/company-reviews`
- Auth: `x-api-key` header
- 20 reviews/page, pages 1–10 without a Trustpilot cookie (200/domain ceiling matches Trustpilot's own platform limit, consistent with every other tool tested)
- Real-time data, confirmed by the freshness discovery in this run (see `ground-truth-comparison.md`)
