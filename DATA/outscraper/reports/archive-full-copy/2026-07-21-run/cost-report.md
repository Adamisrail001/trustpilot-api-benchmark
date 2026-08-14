# Outscraper Trustpilot Reviews API — Cost Report

## Documented pricing (source: `docs/outscraper-pricing.md`)

- First 100 reviews/billing-period: free
- Reviews 101–50,000: $3 per 1,000 ($0.003/review)
- Reviews above 50,000: $1 per 1,000 ($0.001/review)
- Empty-result queries may still consume ~1 review of usage (documented risk, not encountered this run)

## Estimated cost (calculated, pre-run)

```
Fresh account:      1,000 - 100 free = 900 billable × $0.003 = $2.70
Free tier consumed: 1,000 billable × $0.003 = $3.00
```
Source: `outputs/outscraper/execution-plan.json`.

## Measured usage (post-run, from actual raw counts)

| Domain | Raw reviews returned |
|---|---:|
| www.thepearlsource.com | 200 |
| www.shein.com | 200 |
| temu.com | 200 |
| www.aliexpress.com | 200 |
| thehalara.com | 200 |
| **Total usage** | **1,000** |

Source: `outputs/outscraper/domain-summary.json`. Exactly 5 billable requests were made — one per domain, no extra pagination pages.

## Calculated cost from measured usage

| Scenario | Calculated cost |
|---|---:|
| Fresh account (first 100 reviews still free) | $2.70 |
| Free tier already consumed this billing period | $3.00 |

Source: `outputs/outscraper/cost-report.json`.

## Measured (billed) cost — **Pending**

Outscraper does not document an endpoint that returns account balance or a per-request billed-cost figure (unlike DataForSEO, which returns a `cost` field on every task response). The task creation and result responses observed in this run contain no cost/usage field at all. **True measured cost can only be obtained by checking the Outscraper account billing dashboard before and after this run — that has not been done and is marked Pending, not assumed.**

## Cost per 1,000 successful unique reviews

```
Since unique valid reviews = 1,000 exactly, normalization is trivial:
Fresh-account scenario:      $2.70 ÷ 1,000 × 1,000 = $2.70
Free-tier-consumed scenario: $3.00 ÷ 1,000 × 1,000 = $3.00
```

Both figures are **calculated**, not measured — kept as a range until account evidence resolves which scenario applies.

## Estimated vs. measured

| | Value |
|---|---|
| Estimated (pre-run, documented pricing) | $2.70–$3.00 |
| Calculated (post-run, from measured usage × documented pricing) | $2.70–$3.00 (identical — usage matched the plan exactly, 1,000/1,000, no failed/partial/duplicate billable requests) |
| Measured (actual billed amount) | **Pending** — requires manual account-dashboard check |

## Comparison to the DataForSEO benchmark

Outscraper's calculated cost ($2.70–$3.00 per 1,000 reviews) is approximately **72–80x more expensive** than DataForSEO's measured cost for the same 1,000-review benchmark ($0.0375). This is a documented pricing-model difference (DataForSEO bills ~$0.00075/20 reviews vs. Outscraper's $0.003/review), not a measurement error — both figures trace to each provider's own published/measured cost evidence.

## Billing fairness — evidence status

- **Failed/duplicate requests charged?** Not observed — zero failures or duplicate submissions occurred this run.
- **Empty-result billing:** Documented as a real risk (empty queries may still cost ~1 review of usage) but not encountered — all 5 domains returned full pages.
- **Free-tier remaining balance:** Pending — not checked against the account dashboard before this run, so whether any of the $2.70–$3.00 range was actually free is unresolved.
