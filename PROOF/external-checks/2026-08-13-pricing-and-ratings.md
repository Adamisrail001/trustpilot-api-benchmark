# External evidence checks — 2026-08-13

**Evidence type: EXTERNAL EVIDENCE / OFFICIAL DOCUMENTATION** (live web fetches
performed today, dated so they're never confused with the original 2026-07
benchmark run. No API keys or credentials were used for any of these — all are
public marketing/review pages.)

## Lobstr — credit definition (official documentation)

Source: https://www.lobstr.io/pricing (fetched 2026-08-13)

Confirms: **"A credit is super simple: 1 credit = 1 unique result."** This
directly supports the benchmark's "1,000 credits consumed for 1,000 reviews"
claim (which is benchmark-measured — see `DATA/lobstr/raw/credits-before.json`
/ `credits-after.json`).

**Does NOT resolve:** the actual dollar-per-credit / dollar-per-1,000-credits
rate. Lobstr's pricing page uses an interactive JS pricing simulator; the static
fetch could not retrieve the per-tier dollar figures. The "$1 per 1,000 reviews"
claim in `IMPORTANT/knowledge.md` remains **unconfirmed by any evidence in this
repo** — a preliminary web search returned a lead-generation-scraper rate
($10→$5 per 1,000 leads) that looks like a different product line entirely and
should not be used as a substitute. Recommend checking the pricing simulator
directly (requires a browser) or the account's own billing dashboard before
publishing a specific dollar figure.

## Lobstr — Capterra rating (external evidence)

Source: https://www.capterra.com/p/10018837/lobstr/reviews/ (fetched 2026-08-13)

Confirms: **5.0 / 5.0 average, 33 total reviews** (page shows "5 (33)" / "Showing
1-25 of 33 Reviews"). This is a **current** figure, not necessarily identical to
whatever count was true when the article's "5/5, small sample" line was
originally written (`IMPORTANT/knowledge.md` doesn't state a review count at
all, calling it "exact count not independently confirmed"). Recommend updating
the article's Lobstr rating citation to **5.0/5, 33 reviews (Capterra, checked
2026-08-13)** rather than leaving the count unstated.

## Apify — G2 rating (attempted, blocked)

Source: https://www.g2.com/sellers/apify (attempted 2026-08-13)

**Result: HTTP 403 Forbidden.** G2 blocks automated fetches. Could not verify or
refresh Apify's cited "4.7/5, 534 reviews" figure. **Remains an open gap** —
recommend a manual browser check before publishing, or keep the existing
citation with its original checked-date if one is recorded.

## Outscraper — pricing page (attempted, blocked)

Sources attempted: https://outscraper.com/pricing/ and
https://outscraper.com/trustpilot-reviews-api/ (2026-08-13)

**Result: connection refused** on both URLs (same host). Could not corroborate
the $2.70–$3.00/1,000 rate-card estimate already disclosed as unmeasured in
`DATA/outscraper/analysis/cost-report.json`. **Remains an open gap** — the
existing figure is unchanged and still labeled as an estimate, not weakened or
strengthened by this attempt.
