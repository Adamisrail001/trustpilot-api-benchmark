# Apify (automation-lab/trustpilot) — Cost Report

## Documented pricing (source: `docs/apify/apify-pricing.md`, pay-per-event model)

- Run start fee: $0.005 (one-time, per run)
- Free-tier per-review charge: $0.000575
- Published estimate for 1,000 reviews: $0.575 + $0.005 = **$0.580**

## Estimated cost (calculated, for the measured 798 unique reviews)

```
798 × $0.000575 = $0.45885
+ $0.005 run start fee
= $0.46385 ≈ $0.4638
```

## Measured cost — real, from the settled Run object

Per the docs' own instruction, the Run object was re-fetched 5 seconds after reaching `SUCCEEDED` so finalized usage values had time to settle.

| Field | Value |
|---|---|
| `usage` | not present on the settled Run object (Pending — not returned) |
| `usageUsd` | not present (Pending — not returned) |
| **`usageTotalUsd`** | **$0.465** |

**Measured total cost: $0.465** — this is a real, directly-measured figure from Apify, not a calculation.

## Estimated vs. measured

| | Value |
|---|---|
| Estimated (calculated from published rate × 798 unique) | $0.4638 |
| Measured (`usageTotalUsd` from the API) | $0.465 |
| Variance | +$0.0012 (+0.26%) — negligible, the published formula predicts the real charge almost exactly |

## Cost per 1,000 successful unique reviews

```
$0.465 ÷ 798 × 1,000 = $0.5827
```

This is slightly above the published "$0.58 per 1,000" headline rate, entirely because the denominator is 798 (the shortfall), not 1,000 — the per-unit rate itself is confirmed accurate.

## Billing behavior observed

- **Duplicate billing:** the 2 duplicate records within the dataset were included in the raw/valid counts before deduplication. Whether Apify's `usageTotalUsd` charged for those 2 duplicate result events specifically cannot be isolated from the aggregate figure — **Pending** (would require an event-level billing breakdown not exposed by the Run object's top-level fields).
- **SHEIN's zero-result domain:** no evidence of a separate charge or credit for the domain that returned nothing — the aggregate `usageTotalUsd` is consistent with ~798-800 charged results, suggesting SHEIN's failure did not incur its own event charges (a company that returns 0 reviews presumably has 0 chargeable review-events), but this is inferred from the aggregate number, not itemized — **Pending** exact confirmation.
- **One run vs. five:** using a single multi-company run (as required) avoided paying the $0.005 start fee 5 times — confirmed by the math above ($0.465 total is consistent with one run fee, not five).
