# DataForSEO Trustpilot Reviews API — Benchmark Report

**Run date:** 2026-07-21
**Run ID:** `2026-07-21T11-50-13-551Z`
**Target:** 1,000 unique Trustpilot reviews
**Design:** 5 fixed business domains × 200 reviews/task (see rationale below)

---

## 1. Single-domain attempt (www.thepearlsource.com)

**Result: 200 unique reviews retrieved from www.thepearlsource.com alone. Single-domain pagination is NOT supported.**

Before spending on the multi-domain fallback, one task was submitted for `www.thepearlsource.com` at the documented ceiling (`depth=200`, `sort_by=recency`, `priority=1`, standard). This is the maximum obtainable from a single Trustpilot business profile via this API.

**Why it stopped here (not tested further):** the stop condition — "no official pagination method exists" — was already established from the official DataForSEO documentation *before* this run, via direct fetches of the live docs during this engagement:

- [Task POST docs](https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_post/) — parameters are `domain`, `sort_by` (`recency`/`relevance` only), `priority`, `depth` (max 200), `tag`, `postback_url`, `pingback_url`. No `page`, `offset`, `skip`, `cursor`, date-range, or rank-range parameter exists.
- [Task GET docs](https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_get/) — replays the cached result of the original task only; no parameters, no new data on repeat calls.
- [Trustpilot overview](https://docs.dataforseo.com/v3/business_data-trustpilot-overview/) — confirms only 3 endpoints exist for Trustpilot Reviews (Task POST / Tasks Ready / Task GET); no Live or secondary search-within-reviews endpoint.
- [Depth-limit update announcement](https://dataforseo.com/update/new-depth-limit-in-trustpilot-reviews-api) — 200 is the current hard ceiling, no pagination alternative offered.
- [Help Center walkthrough](https://dataforseo.com/help-center/get-trustpilot-reviews) — describes only the single Task POST → Task GET flow.

Running additional identical tasks against the same 200-review ceiling to "confirm" this empirically would have (a) violated the explicit rule against inventing undocumented parameters, (b) violated the rule against counting repeated identical-task results as pagination, and (c) spent money to re-prove a fact already established from primary-source documentation. The single task above therefore doubles as domain #1 of the approved multi-domain fallback — no separate/duplicate task was created for it.

## 2. Multi-domain fallback — used automatically

Per the approved design, the remaining 4 domains were submitted immediately (not sequentially gated behind the single-domain result, since the decision to fall back was already settled on documentation grounds, not empirical grounds).

| Domain | Business | Task ID | Raw items | Valid items | Unique valid | Shortfall |
|---|---|---|---:|---:|---:|---:|
| www.thepearlsource.com | The Pearl Source | `07211450-2117-0358-0000-be4f52a532ca` | 200 | 200 | 200 | 0 |
| www.shein.com | SHEIN | `07211450-2117-0358-0000-dddcb7ebacdb` | 200 | 200 | 200 | 0 |
| temu.com | Temu | `07211450-2117-0358-0000-8b72f8f48833` | 200 | 200 | **199** | **1** |
| www.aliexpress.com | AliExpress | `07211450-2117-0358-0000-c8f93938123d` | 200 | 200 | 200 | 0 |
| thehalara.com | Halara | `07211450-2117-0358-0000-84fa9ff0af90` | 200 | 200 | 200 | 0 |
| **Total** | | | **1,000** | **1,000** | **999** | **1** |

**temu.com shortfall (exact):** the task returned 200 raw items, all individually valid, but one review (`https://www.trustpilot.com/reviews/6a5bc3e8ba35c9f26c69aa78`, title "Let down", timestamp 2026-07-18 20:20:24 +00:00) appeared **twice within the same task's result** — i.e., DataForSEO's own single-task response contained an internal duplicate, not a duplicate we introduced by re-running the task. Full evidence: [outputs/dataforseo/duplicate-report.json](../outputs/dataforseo/duplicate-report.json). Per the approved rules, this domain was **not** re-run and **not** silently padded — the shortfall of 1 is reported as-is.

## 3. Final outcome

> **Benchmark partially completed: 999 unique valid reviews (target: 1,000). Reason: temu.com's single task returned one internal duplicate review, netting 199 unique reviews instead of 200. No domain was replaced or re-run to close this gap, per the no-auto-substitution rule.**

## 4. Required measurements

| Metric | Value | Source |
|---|---|---|
| Requested reviews | 1,000 | design (5 × 200) |
| Total raw records returned | 1,000 | measured — [domain-summary.json](../outputs/dataforseo/domain-summary.json) |
| Valid records | 1,000 | measured — all raw items passed the successful-review definition |
| Unique valid reviews | 999 | measured — [all-reviews.json](../outputs/dataforseo/all-reviews.json) |
| Duplicate reviews | 1 | measured — [duplicate-report.json](../outputs/dataforseo/duplicate-report.json) |
| Failed tasks | 0 | measured |
| Empty responses | 0 | measured |
| Partial responses | 0 | measured (all 5 domains returned the full requested depth of 200) |
| Success rate (unique valid ÷ requested) | 99.9% | calculated: 999/1000 |
| Failure rate | 0.1% | calculated: 1/1000 (the one unresolved duplicate) |
| Duplicate rate | 0.1% | calculated: 1/1000 valid records |
| Records returned per domain | see table above | measured |
| Median request latency | 404 ms | measured — [timings.json](../outputs/dataforseo/timings.json) |
| p95 request latency | 2,378 ms | measured |
| Total wall-clock time | 165,513 ms (~2 min 46 s) | measured |
| API-reported task cost | $0.0075/task × 5 = $0.0375 | measured — task_post responses |
| Measured total cost | $0.0375 | measured |
| Cost per 1,000 successful unique reviews | $0.03754 | calculated: $0.0375 ÷ 999 × 1000 |
| Schema consistency | 100% (0 missing required fields across all 1,000 raw items) | measured |
| Missing-field counts | 0 across all 5 domains | measured — `missing_field_counts: {}` in domain-summary.json |
| Rate-limit responses | 0 | measured — [errors/event-log.jsonl](../outputs/dataforseo/errors/event-log.jsonl) (empty) |
| Retries | 0 | measured |
| Task status/error-message quality | Clear — `20000 "Ok."` / `20100 "Task Created."` on every task | measured |

## 5. Generated files

- `outputs/dataforseo/raw/task-post/*.json` (5 files)
- `outputs/dataforseo/raw/task-get/*.json` (5 files)
- `outputs/dataforseo/errors/event-log.jsonl` (empty — zero errors/retries)
- `outputs/dataforseo/timings.json`
- `outputs/dataforseo/all-reviews.json` / `.csv`
- `outputs/dataforseo/duplicate-report.json`
- `outputs/dataforseo/domain-summary.json`
- `outputs/dataforseo/ground-truth-match.json`
- `outputs/dataforseo/execution-plan.json`
- `reports/dataforseo-cost-report.md`
- `reports/dataforseo-field-coverage.md`
- `reports/dataforseo-ground-truth-comparison.md`
- `reports/dataforseo-elimination-assessment.md`
- `reports/dataforseo-scorecard.md`
- `reports/dataforseo-missing-evidence.md`

## 6. Remaining blocker

None. The 1-review shortfall on temu.com is reported, not blocking — per the approved rules, closing it requires your explicit approval to replace or supplement that domain, which has not been requested yet.
