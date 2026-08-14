# OpenWeb Ninja Trustpilot Reviews API — Fresh Benchmark Report (Re-run)

**Run date:** 2026-07-29
**Script executed:** `scripts/openwebninja_benchmark.py run` (unmodified,
`CONFIRM_PAID_RUN=yes OPENWEBNINJA_QUOTA_REMAINING=1000`)
**Target:** 1,000 unique Trustpilot reviews across 5 fixed domains (200 each)
**Previous run for comparison:** 2026-07-22 (archived at
`data/*/openwebninja/archive-full-copy/2026-07-22-run/`)
**This session's earlier failed attempts (1 and 2) archived at:**
`data/*/openwebninja/archive-full-copy/2026-07-29-failed-rate-limited/`

## Result: FAIL — 0 of 1,000 requested reviews returned (3 attempts, identical outcome each time)

Three independent live attempts, spread across ~38 minutes, **all** resulted
in 100% HTTP 429 "Too Many Requests" across all 5 domains on the very first
request, every time exhausting the client's full retry budget (1 initial +
3 retries, exponential backoff) before giving up.
`data/raw/openwebninja/results/` is empty after all 3 attempts — not a
single successful response was ever received.

| Attempt | Time (UTC) | Outcome |
|---|---|---|
| 1 | 08:20:31 – 08:21:31 | 429 ×4 on all 5 domains, fetch_failed |
| (cooldown) | 08:23:04 – 08:24:44 | 100s wait |
| 2 | 08:24:44 – 08:25:45 | 429 ×4 on all 5 domains, fetch_failed |
| 3 (this run) | 08:56:50 – 08:57:59 | 429 ×4 on all 5 domains, fetch_failed |

Full event log for this attempt: `data/logs/openwebninja/errors/event-log.jsonl`
(75 events across all 3 attempts combined this session). Full narrative
timeline: `data/logs/openwebninja/run.log`. Attempts 1–2's evidence is
preserved separately at
`data/*/openwebninja/archive-full-copy/2026-07-29-failed-rate-limited/`.

## Root cause (not fully confirmed — no diagnostic endpoint exists)

OpenWeb Ninja has no account/usage/quota/rate-limit API endpoint. Quota was
checked manually before this session and reported as "definitely very high
(1000+)" — which argues against monthly quota exhaustion, but a dashboard's
headline quota figure and a per-second/per-minute rate-limit tier are two
different things. Three consecutive identical failures across 38 minutes
rules out a brief single-burst rate limit — this is a **sustained**
condition, not a momentary blip. Without a support ticket or a documented
rate-limit-status endpoint, the exact cause cannot be confirmed; the most
consistent explanations are:

1. This API key/account is on a stricter per-second/per-minute rate-limit
   tier than the script's `REQUEST_SPACING_MS` (350ms, ~2.8 req/sec)
   assumes safe.
2. A broader, possibly extended, throttle or block on this key/account at
   OpenWeb Ninja's platform level.

## Real usage incurred across all 3 attempts

Each logical fetch retried 3 times (4 real HTTP attempts) before giving up.
Real HTTP calls made to OpenWeb Ninja's API this session:

```
5 domains × 4 attempts × 3 script invocations = 60 real HTTP requests
```

All 60 returned HTTP 429. Whether OpenWeb Ninja counts 429 responses
against billed usage/quota is unknown — not documented, no endpoint exists
to check it.

## Run results (this attempt, #3)

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
| Failed requests | 5 logical fetches (20 real HTTP attempts), all HTTP 429 |
| Retries | 3 per domain (client max), all exhausted |
| Rate-limit (429) events | 20 of 20 real HTTP attempts this run |
| Pagination | Never advanced past page 1 for any domain |
| Wall-clock | 69,000 ms (08:56:50 → 08:57:59) |
| Cost | See below |

## Cost

**Measured/billed cost: unavailable** (no OpenWeb Ninja billing/usage API
endpoint). `measured_cost_usd` is `null` in `cost-report.json`, not zero.

**Estimated cost** (published rate card × the script's own request counter
of 5 for this attempt, which undercounts real HTTP attempts — 20 real calls
were made): $0.0037–$0.025 for this attempt alone; roughly 3× that across
all 3 attempts combined. This is a calculated estimate, not measured.

**Credits/quota:** unknown — cannot verify whether the 60 total failed 429
responses this session consumed quota.

## Ground truth

Ran `scripts/openwebninja_ground_truth_compare.py` against the fresh
(empty) `www.thepearlsource.com` results: 0/20 matched, 0 API items
available — expected, given 0 reviews were ever returned across any of the
3 attempts. No accuracy signal, positive or negative, is available this
session.

## Comparison with previous run (2026-07-22)

| | Previous | Fresh (3 attempts) | Difference |
|---|---|---|---|
| Unique reviews | 1,000 | 0 | −1,000 |
| Domains completed | 5 of 5 | 0 of 5 (all 3 attempts) | −5 |
| Errors | 1 transient HTTP 500 (recovered) | 60 persistent HTTP 429 (never recovered, 3 attempts) | qualitatively different failure mode |
| Wall clock | 180,749 ms (completed) | 59–69k ms per attempt (all failed fast) | not comparable |

**Does this change any previous conclusion?** Not about OpenWeb Ninja's data
quality (untested this session) — but it adds a new, previously unobserved
reliability concern: on 2026-07-22 the API handled 50 real requests
cleanly; on 2026-07-29, across 3 separate attempts spanning 38+ minutes,
every single one of 60 real requests was rejected.

## Issues found

- **Sustained HTTP 429 across 100% of requests, across 3 attempts over 38
  minutes** — a genuine reliability concern for this API/account today, not
  a script defect (retry/backoff logic behaved correctly and as designed
  each time).
- The script's `total_requests_made` counter undercounts real HTTP
  attempts (counts logical fetches, not retries) — a pre-existing accuracy
  gap in cost/usage reporting, not something introduced by this run.

## Still missing

- Root cause of the sustained 429s — unconfirmable without OpenWeb Ninja
  support contact or a rate-limit-status endpoint, neither available here.
- Whether the 60 real HTTP 429 responses this session consumed any billed
  quota.

## Recommendation

Retrying again without changing anything is unlikely to produce a different
result — 3 attempts across 38 minutes were fully consistent. Next step
should be checking OpenWeb Ninja's dashboard specifically for a rate-limit
(not quota) indicator, or contacting their support, before attempting again.
