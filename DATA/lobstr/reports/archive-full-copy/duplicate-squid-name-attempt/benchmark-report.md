# Lobstr.io Trustpilot Reviews — Benchmark Report

**Run date:** 2026-07-22
**Squid used:** `8d9e0b80d6d2481283c138104caf022d` (the clean, dedicated squid — correctly resolved from `.env`, confirmed not the contaminated squid)

## Result: Benchmark blocked before task/Run creation — 0 reviews collected

The run correctly reused the clean crawler (`b3362ab52c6fab3d8897af79cbba380e`) and the clean squid (`8d9e0b80d6d2481283c138104caf022d`) from `.env`. It then failed at the **squid-configuration** step with `HTTP 400 DuplicateSquid` before any task or Run was created. See `reports/lobstr/error-investigation.md` for the full, verified root-cause analysis (a hardcoded-name collision with the still-existing original contaminated squid, not a credit/billing issue).

## Per the approved rules

- The old contaminated squid was **not** used — confirmed: the run correctly targeted `8d9e0b80d6d2481283c138104caf022d` throughout.
- No `happen.com` or unapproved domain was ever contacted — the failure occurred before any domain-level task was created.
- No second Run was created; no automatic retry of the full run was attempted.
- Every raw response, the error event, and one diagnostic read-only lookup made to confirm root cause were all saved.

## Required measurements

| Metric | Value | Basis |
|---|---|---|
| Reviews requested | 1,000 | design |
| Raw reviews returned | 0 | measured |
| Valid unique reviews | 0 | measured |
| Duplicates | 0 | measured (nothing to deduplicate) |
| Domains processed | 0 of 5 | measured — failure occurred before per-domain task creation |
| Tasks created | 0 | measured |
| Runs created | 0 | measured |
| Errors | 1 (see `error-investigation.md`) | measured |
| Retries | 0 (correct — 400 is non-retryable) | measured |
| Credits consumed this attempt | 0 | measured, via `GET /v1/user/balance` before/after comparison |

## Generated files

- `outputs/lobstr/raw/requests/{squid-reused.json, diagnostic-squid-name-search.json}`
- `outputs/lobstr/errors/event-log.jsonl`, `error-log.json`
- `outputs/lobstr/{execution-plan.json, run-state.json, domain-summary.json, duplicate-report.json, pagination-report.json, timings.json, cost-report.json, usage-report.json, credits-check.json, all-reviews.json, all-reviews.csv, ground-truth-match.json}`
- `reports/lobstr/*.md` (this file + 8 others)

## Remaining blocker

**Yes — one, fully diagnosed, not yet fixed.** The clean squid's configuration step cannot complete until the name collision with the old contaminated squid (still present on the Lobstr account) is resolved — either by using a different name for the clean squid's configuration step, or by renaming/removing the old contaminated squid on the Lobstr platform itself. Per the explicit instruction not to retry the full run without approval, no fix was applied and no retry was attempted.
