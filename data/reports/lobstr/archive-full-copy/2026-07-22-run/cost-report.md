# Lobstr.io Trustpilot Reviews — Cost Report

## Documented pricing (`docs/lobster/lobstr-pricing.md`)

1 credit = 1 unique result. Advertised rate: **$0.50 per 1,000 unique reviews**. Duplicates should not consume additional credits.

## Measured credit consumption — real, confirmed

| Evidence source | Value |
|---|---|
| Account `consumed` balance before this benchmark (captured earlier in this session, during pre-run validation) | 20 |
| Account `consumed` balance after this benchmark | 1,020 |
| **Measured credits consumed by this benchmark** | **1,000** |
| Run object's own `credit_used` field (independent confirmation) | **1,000** |

Both independent sources (account-balance delta, and the Run object's own field) agree exactly: **1,000 credits for 1,000 unique successful reviews — a perfect 1:1 ratio, with zero waste** from the earlier setup errors, the 62 retried rate-limit responses, or any duplicate/failed record.

## Estimated vs. measured dollar cost

| | Value |
|---|---|
| Advertised rate | $0.50 / 1,000 reviews |
| Estimated cost for this benchmark | $0.50 |
| **Measured dollar cost** | **Pending** — the account balance endpoint returns credit counts only, no dollar figure, and this account's plan is reported as `"free"` with Super Admin access noted as the reason credits could go negative-relative-to-`available` (0 available, 1,020 consumed) without blocking execution. No documented API field exposes the account's actual effective $/credit rate under Super Admin terms. |

## Cost per 1,000 successful unique reviews

```
1,000 credits ÷ 1,000 unique reviews × 1,000 = 1,000 credits per 1,000 successful reviews (i.e. exactly 1:1, as documented)
```
In dollar terms, **$0.50/1,000 if the advertised rate applies to this account** — not independently confirmed as the actual bill, per above.

## Billing fairness — confirmed this run

- **Failed requests:** none occurred (the 62 throttled requests were all retried to success) — so failed-request billing behavior remains untested, not because of missing evidence but because nothing failed.
- **Duplicate requests:** none — no duplicate reviews were returned, and re-submitting the same 5 task URLs (during the fix-and-retry cycle) did not create duplicate task objects on the squid (confirmed: identical task IDs before and after).
- **Setup-error cost:** the earlier blocked `DuplicateSquid` attempt and the pagination-bug re-fetch cycle consumed **zero** additional credits — confirmed via the account balance staying at `consumed: 20` through the blocked attempt, and only advancing to `1,020` once the actual successful scrape completed.
