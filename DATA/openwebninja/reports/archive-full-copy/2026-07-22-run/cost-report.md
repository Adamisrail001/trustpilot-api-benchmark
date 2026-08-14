# OpenWeb Ninja Trustpilot Reviews API — Cost Report

## Documented pricing (source: `docs/openwebninja/openwebninja-pricing.md`)

Request-based monthly plans: Free ($0, 100 req/mo), Pro ($25, 10,000 req/mo), Ultra ($75, 50,000 req/mo), Mega ($150, 200,000 req/mo), Pay-As-You-Go ($0.005/request).

**Account plan for this run: "Basic"** (per your dashboard check) — **not one of the five tiers listed in the published rate card.** No published price-per-request figure could be found for "Basic" specifically. This is flagged, not guessed.

## Estimated cost (calculated, pre-run, for 50 requests)

| Plan | Estimated cost for 50 requests |
|---|---:|
| Free | $0 (marginal) |
| Pro (allocated) | $0.125 |
| Ultra (allocated) | $0.075 |
| Mega (allocated) | $0.0375 |
| Pay-As-You-Go | $0.25 |
| **Basic** | **Pending — rate not published** |

## Measured usage (post-run)

- **Total requests made: 50** — exactly matching the pre-run plan (5 domains × 10 pages), zero wasted requests.
- Quota before run (dashboard, confirmed by you): 100 remaining.
- Quota after run: not independently re-checked (no API endpoint exists to verify this automatically — would require another manual dashboard check).

## Measured (billed) dollar cost — **Pending**

OpenWeb Ninja's documented endpoint list (company-search, company-details, company-reviews, category-*, consumer-*) contains **no account/usage/billing endpoint**. There is no way to confirm the "Basic" plan's price or verify actual quota consumption via the API. This must be checked on the dashboard directly.

## Cost per 1,000 successful unique reviews

Since unique valid reviews = 1,000 exactly, normalization is trivial once a real rate is known:
```
Cost per 1,000 = (50 requests × price-per-request) ÷ 1,000 × 1,000 = 50 × price-per-request
```
Cannot be finalized until the "Basic" plan's per-request price is confirmed.

## Estimated vs. measured

| | Value |
|---|---|
| Estimated (published rate card, closest applicable tiers) | $0–$0.25 for 50 requests, depending on tier |
| Measured (actual "Basic"-plan billed amount) | **Pending** |

## Billing evidence to record (per project standard, not yet available)

- "Basic" plan's exact price and included-request allowance
- Account balance/quota before vs. after this run (only the "before" figure was manually confirmed: 100)
- Whether the one retried HTTP 500 consumed quota on both attempts or only the successful one — undocumented, Pending
