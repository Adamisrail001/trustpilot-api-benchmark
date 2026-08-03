# OpenWeb Ninja Trustpilot Reviews API — Fresh Benchmark Report (Re-run)

**Run date:** 2026-07-29
**Script executed:** `scripts/openwebninja_benchmark.py run` (unmodified,
`CONFIRM_PAID_RUN=yes OPENWEBNINJA_QUOTA_REMAINING=1000`)
**Target:** 1,000 unique Trustpilot reviews across 5 fixed domains (200 each)
**Previous run for comparison:** 2026-07-22 (archived at
`data/*/openwebninja/archive-full-copy/2026-07-22-run/`)

## Result: FAIL — 0 of 1,000 requested reviews returned

Two independent live attempts (100 seconds apart) both resulted in **100%
HTTP 429 "Too Many Requests"** across all 5 domains on the very first
request, in both cases exhausting the client's full retry budget (1 initial
+ 3 retries, exponential backoff) before giving up. `data/raw/openwebninja/results/`
is empty — not a single successful response was received in either attempt.

| Domain | Attempt 1 | Attempt 2 (after 100s cooldown) |
|---|---|---|
| www.thepearlsource.com | 429 ×4, fetch_failed | 429 ×4, fetch_failed |
| www.shein.com | 429 ×4, fetch_failed | 429 ×4, fetch_failed |
| temu.com | 429 ×4, fetch_failed | 429 ×4, fetch_failed |
| www.aliexpress.com | 429 ×4, fetch_failed | 429 ×4, fetch_failed |
| thehalara.com | 429 ×4, fetch_failed | 429 ×4, fetch_failed |

Full event log: `data/logs/openwebninja/errors/event-log.jsonl` (46 events
across both attempts). Full narrative timeline:
`data/logs/openwebninja/run.log`.

## Root cause (not fully confirmed — no diagnostic endpoint exists)

OpenWeb Ninja has no account/usage/quota/rate-limit API endpoint (confirmed
absent from the documented endpoint list — same limitation noted in the
original benchmark). Before this run, quota was checked manually and
reported as "definitely very high (1000+)" — which argues against monthly
quota exhaustion, but a dashboard's headline quota figure and a per-second/
per-minute rate-limit tier are two different things, and this account may
simply be rate-limited more strictly than the script's `REQUEST_SPACING_MS`
(350ms, ~2.8 req/sec) assumes safe. Two possibilities that fit the evidence
equally well and cannot be distinguished without a support ticket or a
documented rate-limit-status endpoint:

1. This API key/account is on a stricter per-second/per-minute rate-limit
   tier than the script assumes.
2. A broader, possibly temporary, throttle on OpenWeb Ninja's platform.

Both attempts failed **identically** (same status, same attempt count, same
stop reason) with a 100-second gap between them, which rules out a
brief single-burst rate limit that would have cleared on its own.

## Real usage incurred

`total_requests_made: 5` in `domain-summary.json`/`cost-report.json` only
counts one *logical* fetch per domain per attempt — it does **not** reflect
the real number of HTTP calls made. Each logical fetch internally retried
3 times (4 real HTTP attempts) before giving up. Actual real HTTP calls to
OpenWeb Ninja's API this session:

```
5 domains × 4 attempts × 2 script invocations = 40 real HTTP requests
```

All 40 returned HTTP 429. Whether OpenWeb Ninja counts a 429 response
against billed usage/quota is **unknown** — not documented, and there is no
endpoint to check it. This is flagged explicitly rather than assumed either
way.

## Run results

| Metric | Value |
|---|---|
| Businesses requested | 5 |
| Reviews requested per business | 200 |
| Total reviews requested | 1,000 |
| Raw reviews returned | 0 |
| Unique reviews returned | 0 |
| Duplicates | 0 |
| Zero-result businesses | 5 of 5 |
| Successful requests | 0 |
| Failed requests | 5 (attempt 1) + 5 (attempt 2) logical fetches; 40 real HTTP attempts, all HTTP 429 |
| Retries | 3 per domain per attempt (client's max), all exhausted |
| Rate-limit (429) events | 40 of 40 real HTTP attempts |
| Pagination | Never advanced past page 1 for any domain (stopped on first-page failure) |
| Wall-clock (attempt 2, final) | 59,665 ms; attempt 1 was 60,105 ms (08:20:31→08:21:31) |
| Cost | See below |

## Cost

**Measured/billed cost: unavailable** (no OpenWeb Ninja billing/usage API
endpoint — same limitation as the historical run). `measured_cost_usd` is
`null` in `cost-report.json`, not zero.

**Estimated cost** (published rate card × the script's own
`total_requests_made` counter of 5, which undercounts real HTTP attempts —
see above): $0.0037–$0.025 depending on plan tier. This is a calculated
estimate from a request count that itself likely understates real usage
(40 real HTTP attempts occurred, not 5) — flagged as such, not measured.

**Credits/quota:** unknown — cannot verify whether failed 429 responses
consumed quota. No direct-charge evidence either way.

## Ground truth

Ran `scripts/openwebninja_ground_truth_compare.py` for real against the
fresh (empty) `www.thepearlsource.com` results. Result: 0/20 matched, 0 API
items available — expected given 0 reviews were returned. This run produces
**no accuracy signal** for OpenWeb Ninja's data quality, positive or
negative.

## Comparison with previous run (2026-07-22)

| | Previous | Fresh | Difference |
|---|---|---|---|
| Unique reviews | 1,000 | 0 | −1,000 |
| Duplicates | 0 | 0 | 0 |
| Domains completed | 5 of 5 | 0 of 5 | −5 |
| Requests made (logical) | 50 | 5 (×2 attempts) | — |
| Errors | 1 (transient HTTP 500, recovered same domain) | 40 (persistent HTTP 429, never recovered) | qualitatively different failure mode |
| Wall clock | 180,749 ms (completed) | 59,665 ms (attempt 2, failed fast) | not comparable — one completed, one failed |
| Ground truth match | 100% (implied, full data) | 0/20 (no data) | — |

**Does this change any previous conclusion?** Not about OpenWeb Ninja's data
quality or field accuracy (untested this run) — but it does add a new,
previously unobserved failure mode: on 2026-07-22 the API handled 50 real
requests with only 1 transient error; on 2026-07-29 it rejected literally
every request. This is worth flagging as a reliability/rate-limit
consideration independent of the historical run's clean result, not a
contradiction of it.

## Issues found

- **Persistent HTTP 429 across 100% of requests, surviving a 100-second
  cooldown and a full retry budget** — a genuine reliability concern for
  this API/account, not a script defect (the retry/backoff logic itself
  behaved correctly and as designed).
- `total_requests_made` in the script's own output undercounts real HTTP
  attempts (counts logical fetches, not retries) — worth fixing for
  accurate cost/usage accounting, but not touched here per this task's
  script-preservation scope.

## Still missing

- Root cause of the 429s cannot be confirmed without contacting OpenWeb
  Ninja support or having a documented rate-limit-status endpoint — neither
  is available to this benchmark.
- Whether the 40 real HTTP 429 responses consumed any billed quota is
  unknown and unconfirmable via the API.
