# DataForSEO Trustpilot Reviews API — Cost Report

## Documented pricing (source: `docs/dataforseo-pricing.md`, confirmed against official pricing page)

- Standard priority: $0.00075 per 20 reviews → $0.0075 per 200-review task → $0.0375 per 1,000 reviews (5 × 200)
- Billing unit: every block of up to 20 reviews, rounded up

## Estimated cost (calculated, pre-run)

```
5 domains × 200 depth × $0.00075/20 reviews
= 5 × 10 billable blocks × $0.00075
= 5 × $0.0075
= $0.0375
```
Source: `outputs/dataforseo/execution-plan.json` → `estimated_cost.estimated_max_total_usd`.

## Measured cost (post-run, from actual API responses)

| Domain | Task creation cost (from `task_post` response) | Task retrieval cost (from `task_get` response) |
|---|---:|---:|
| www.thepearlsource.com | $0.0075 | $0 |
| www.shein.com | $0.0075 | $0 |
| temu.com | $0.0075 | $0 |
| www.aliexpress.com | $0.0075 | $0 |
| thehalara.com | $0.0075 | $0 |
| **Total** | **$0.0375** | **$0** |

Source: `outputs/dataforseo/raw/task-post/*.json` (`response.tasks[0].cost`) and `outputs/dataforseo/raw/task-get/*.json` (`response.tasks[0].cost`). Retrieval (`task_get`) carries no additional charge — cost is billed entirely at task creation.

**Measured total cost: $0.0375**

## Estimated vs. measured

| | Value |
|---|---|
| Estimated (documented pricing formula) | $0.0375 |
| Measured (actual API-reported cost) | $0.0375 |
| Variance | $0.00 (0%) |

These are presented separately per the requirement not to conflate estimated and measured figures — in this run they happen to be identical because every task returned its full requested depth with no failed or partial tasks.

## Normalized cost efficiency

```
Cost per 1,000 successful unique records
= Total measured cost ÷ Successful unique records × 1,000
= $0.0375 ÷ 999 × 1,000
= $0.037538 (≈ $0.0375)
```

The one duplicate on `temu.com` has a negligible effect on normalized cost (rounds to the same headline figure), but is kept distinct here rather than silently absorbed, per the requirement to track successful vs. requested records separately.

## Billing fairness — evidence status

- **Failed requests charged?** Not observed — zero failed requests occurred in this run, so whether DataForSEO would charge for a failed task is **Pending** (no evidence either way from this benchmark).
- **Duplicate/repeated tasks charged?** Not applicable — no domain's task was re-run.
- **Trial/promotional credits applied?** **Pending** — this run used pre-funded/standard billing; whether a trial credit exists and was or wasn't applied was not checked and is not claimed here.
- **Account balance before/after:** **Pending** — not captured; the billing dashboard was not screenshotted for this run. The per-task `cost` field from the API response is the only measured cost evidence available.
