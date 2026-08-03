# Lobstr.io Trustpilot Reviews — Cost Report

## This attempt

**Measured cost: $0.00.** No Run was created (blocked at squid configuration before any billable action), so this specific attempt genuinely cost nothing — this is a measured fact, not an estimate.

## Account evidence (measured, read-only `GET /v1/user/balance`)

| Field | Value |
|---|---|
| Plan | `free` |
| Available credits | `0` |
| Credits consumed (this billing cycle) | `20` (unchanged from before this attempt — carried over from the original contaminated run) |
| Super Admin status | Not exposed by any documented API field — Pending |

## Published pricing (unchanged from prior research, `docs/lobster/lobstr-pricing.md`)

- Advertised rate: $0.50 per 1,000 unique reviews (1 credit = 1 unique result)

## Cost per 1,000 successful unique reviews

Not calculable — 0 unique reviews were collected this attempt.

## Note on "Super Admin" / credit-blocker framing

Per instruction, credit balance was not treated as a blocker, and it was not the cause of this failure — the actual failure (`HTTP 400 DuplicateSquid`, see `error-investigation.md`) is a naming-validation conflict, unrelated to billing. The account's `available: 0` balance is recorded here as evidence only, not as an explanation for what happened.
