# Lobstr.io — Error Investigation

## Error 1

- **Domain:** N/A — failure occurred before any domain-level task existed
- **Task ID:** N/A — not reached
- **Run ID:** N/A — not reached
- **Export ID:** N/A — not reached
- **Stage:** Squid configuration (`configureSquid` → `PATCH /v1/squids/{squid_hash}`, internal client context label `update_squid`)
- **HTTP status:** `400`
- **Lobstr error code:** `400` (Lobstr also returns a `type` field: `"DuplicateSquid"`)
- **Exact message:** `"A squid with the specified name already exists."`
- **Sanitized response body (exact, credentials removed — there were none in this response):**
  ```json
  {
    "errors": {
      "message": "A squid with the specified name already exists.",
      "type": "DuplicateSquid",
      "code": 400
    }
  }
  ```
- **Timestamp:** `2026-07-22T12:04:44.919Z`
- **Retry count:** `0` — correct per policy: HTTP 400 is a validation error, not a network/429/5xx condition, so it was never retried (confirmed: `"attempt":1` in the saved event).
- **Failure source:** Validation (squid-name uniqueness constraint on the Lobstr platform) — not authentication, not Squid *start*, not task execution, not crawler execution, not pagination, not export, not result retrieval, not rate limiting, not normalization.

### Confirmed cause

The benchmark attempted `PATCH /v1/squids/8d9e0b80d6d2481283c138104caf022d` (the clean squid) with `name: "Trustpilot API Benchmark - Lobstr"`. Lobstr rejected this because a **different** squid on the same account already holds that exact name.

### Root cause — verified with one additional read-only lookup (`GET /v1/squids?name=Trustpilot%20API%20Benchmark`, zero cost, no Run, evidence saved at `outputs/lobstr/raw/requests/diagnostic-squid-name-search.json`):

| Squid ID | Name | Total runs | Created |
|---|---|---:|---|
| `8d9e0b80d6d2481283c138104caf022d` (our clean squid) | `Trustpilot API Benchmark - Lobstr (dedicated)` | 0 | 2026-07-22T06:55:16Z |
| `5644e83e28ce412c9370da2bc46fcd31` (the **original contaminated squid**) | `Trustpilot API Benchmark - Lobstr` | 3 | 2026-07-17T12:06:35Z |

**This is now confirmed, not inferred:** the contaminated squid currently holds the exact name our clean squid's configuration step tried to claim. It was renamed to this string during the very first (invalid, `happen.com`) benchmark attempt's own `configureSquid` call, and was never renamed or deleted **on the Lobstr platform itself** — the prior cleanup task correctly removed only local repository evidence and explicitly did not contact the Lobstr API, so the contaminated squid still exists remotely under this name.

### The actual code-level bug (confirmed, not inferred)

`scripts/lobstr-benchmark.js`'s `configureSquid()` function (used by `run` mode) hardcodes the literal name `"Trustpilot API Benchmark - Lobstr"`. The *separate* preflight code path (`createDedicatedSquid`/its own configure step) used a different literal, `"Trustpilot API Benchmark - Lobstr (dedicated)"`. The two code paths use different hardcoded names for what is conceptually the same squid, and the shorter one collides with the old contaminated squid's current name.

### Unresolved evidence

None outstanding for this error — the cause is fully confirmed by the two pieces of evidence above (the original 400 response, and the follow-up name-search lookup). No further investigation is needed to explain *why* it failed.

---

## Silent failures / shortfalls

None to report beyond Error 1 — the run aborted immediately after this single explicit API error. No task was created, no Run was created, so there is no "task returned zero results" or "Run succeeded but domain missing" scenario to describe here; every domain shows a shortfall of 200 solely because task/Run creation never began.

## This is explicitly NOT a credit/billing issue

Per the account balance check made after this failure (`outputs/lobstr/usage-report.json`, `GET /v1/user/balance`, read-only, zero cost): plan `"free"`, `available: 0`, `consumed: 20` (unchanged from before this attempt). **The observed 400 error carries no billing-related status code (401/402/403) and no billing-related message** — it is a pure name-uniqueness validation error. Crediting this failure to insufficient credits, free-plan limits, or Super Admin status would be inventing a cause not supported by the evidence, which this investigation was explicitly instructed not to do.
