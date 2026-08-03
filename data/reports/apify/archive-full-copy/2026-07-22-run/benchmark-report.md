# Apify (automation-lab/trustpilot) — Benchmark Report

**Run date:** 2026-07-22
**Actor:** `automation-lab/trustpilot` (REST: `automation-lab~trustpilot`)
**Run ID:** `AL74CUwNDfUDkRINC` | **Dataset ID:** `6C7upbw3gTTxze0Wd`
**Run status:** `SUCCEEDED`

## Result: Benchmark partially completed — 798 / 1,000 unique reviews

Exactly **one** Actor run was created for all 5 domains together, as required. The run reported `SUCCEEDED` with zero HTTP/network errors on our side — but one domain returned **zero** reviews.

| Domain | Business | Raw | Valid | Unique | Shortfall |
|---|---|---:|---:|---:|---:|
| www.thepearlsource.com | The Pearl Source | 200 | 200 | 200 | 0 |
| www.shein.com | SHEIN | **0** | 0 | 0 | **200** |
| temu.com | Temu | 200 | 200 | 200 | 0 |
| www.aliexpress.com | AliExpress | 200 | 200 | 199 | 1 |
| thehalara.com | Halara | 200 | 200 | 199 | 1 |
| **Total** | | **800** | **800** | **798** | **202** |

Full evidence: [outputs/apify/domain-summary.json](../../outputs/apify/domain-summary.json), [pagination-report.json](../../outputs/apify/pagination-report.json).

## Investigating the SHEIN gap

Checked before writing this up, not assumed:
- **Zero HTTP or network errors** were logged for this run (`outputs/apify/error-log.json` is empty).
- The single dataset page (`page1-offset0.json`) was inspected directly: it contains exactly 800 items, and **zero** of them have `companyDomain` matching `shein.com` in any form — not an attribution bug, the Actor genuinely did not produce any SHEIN records.
- No error-shaped or placeholder objects exist in the dataset for SHEIN (checked for `error`/`errorMessage`/`success:false` fields — none found).
- The Run's `stats` object shows a clean, unremarkable execution (400.4s runtime, normal CPU/memory usage, 0 migrations/reboots/restarts) — nothing suggesting the Actor crashed or was throttled.

**Conclusion: the Actor silently failed to scrape `www.shein.com` while succeeding on all 4 other domains in the same run, with no error surfaced anywhere in the API response.** The exact cause (anti-bot block on that specific company page, a parsing edge case, a transient site-side issue) is **Pending** — it would require inspecting the Actor's live run log on the Apify console directly, which isn't exposed through the documented run/dataset endpoints used here.

## Two additional near-misses (not investigated as deeply — clearly benign)

`www.aliexpress.com` and `thehalara.com` each returned 200 raw items but exactly 1 internal duplicate (same `reviewId` appearing twice within that domain's own results) — same pattern DataForSEO showed for `temu.com` in an earlier benchmark. Evidence: [duplicate-report.json](../../outputs/apify/duplicate-report.json).

## Per the approved rules

- All 5 domains were processed in the single run (no early abort on the SHEIN shortfall).
- No domain was substituted.
- No second run was created to fix the shortfall — reporting it as-is.

## Required measurements

| Metric | Value | Basis |
|---|---|---|
| Requested reviews | 1,000 | design |
| Total raw returned | 800 | measured |
| Valid records | 800 | measured |
| Unique valid reviews | 798 | measured |
| Duplicates | 2 | measured |
| Overall success rate | 79.8% | calculated: 798/1,000 |
| Actor runs created | 1 (exactly one, as required) | measured |
| Run status | SUCCEEDED | measured |
| Dataset pages retrieved | 1 (800 items fit in a single offset=0,limit=1000 page) | measured |
| Errors / retries | 0 / 0 | measured |
| Actor execution duration | 408,823 ms (~6 min 49 s) | measured |
| Total wall-clock time | 417,896 ms (~6 min 58 s) | measured |
| Median / p95 latency (our API calls) | 1,429 ms / 2,256 ms | measured |
| Min / max / avg latency | 274 ms / 2,266 ms / 1,596.5 ms | measured |
| Reviews per minute | 114.57 (based on 798 unique ÷ wall-clock) | calculated |
| Estimated cost | $0.4638 (for 798 unique, free-tier formula) | calculated |
| Measured cost | **$0.465** (`usageTotalUsd` from the settled Run object) | measured |
| Cost per 1,000 successful reviews | $0.5827 | calculated |

## Generated files

- `outputs/apify/raw/requests/actor-input.json`, `raw/runs/{run.json, run-create-response.json, poll-history.json, run-final.json}`, `raw/datasets/page1-offset0.json`
- `outputs/apify/{all-reviews.json/.csv, domain-summary.json, duplicate-report.json, pagination-report.json, timings.json, error-log.json, execution-plan.json, run-state.json, cost-report.json, usage-report.json, ground-truth-match.json}`
- `reports/apify/*.md` (this file + 7 others)

## Remaining blockers

None that block reporting — the run completed and produced usable evidence. The **cause of the SHEIN gap is unresolved** and is the one open item (see `missing-evidence.md`). Per the approved rules, no retry was attempted.
