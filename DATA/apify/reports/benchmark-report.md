# Apify (automation-lab/trustpilot) — Fresh Benchmark Report (Re-run)

**Run date:** 2026-07-29
**Script executed:** `scripts/apify_benchmark.py run` (unmodified,
`CONFIRM_PAID_RUN=yes`)
**Target:** 1,000 unique Trustpilot reviews across 5 fixed domains (200 each),
via exactly ONE Apify Actor run for all 5 domains together
**Previous run for comparison:** 2026-07-22 (archived at
`data/*/apify/archive-full-copy/2026-07-22-run/`)

## Result: PARTIAL — 800 / 1,000 unique valid reviews (80%)

The Actor run itself completed and reported `SUCCEEDED` with **zero errors
logged anywhere** (`data/analysis/apify/error-log.json` is a confirmed empty
array), yet **`www.thepearlsource.com` returned 0 of its requested 200
reviews**. All 4 other domains returned a clean 200/200 each with 0
duplicates.

| Domain | Raw | Valid | Unique | Shortfall |
|---|---:|---:|---:|---:|
| www.thepearlsource.com | 0 | 0 | 0 | 200 |
| www.shein.com | 200 | 200 | 200 | 0 |
| temu.com | 200 | 200 | 200 | 0 |
| www.aliexpress.com | 200 | 200 | 200 | 0 |
| thehalara.com | 200 | 200 | 200 | 0 |
| **Total** | **800** | **800** | **800** | **200** |

Verified directly against the raw dataset
(`data/raw/apify/datasets/page1-offset0.json`, 800 items): the distinct
`companyDomain` values present are `{www.shein.com, temu.com,
www.aliexpress.com, thehalara.com}` — `www.thepearlsource.com` does not
appear even once. `unattributed_records: 0`, ruling out a
domain-normalization/attribution bug — the Actor's own dataset genuinely
contains zero rows for that domain.

## This reproduces a known, previously-unresolved anomaly — with a twist

`MISSING_AND_GAPS.md` item A.6 documented that the 2026-07-21/22 historical
run saw `www.shein.com` silently return 0/200 with zero error signal, and
flagged it as "never reproduced with a second run." **This fresh run is
that second reproduction** — but the domain that failed is different
(`www.thepearlsource.com`, not `www.shein.com`, which succeeded cleanly
this time). Same actor, same input shape, same 5 domains, same
`maxReviewsPerCompany=200`. In both of the only two live runs ever made
against this Actor, exactly one of the five domains silently returned zero
reviews, with no error/warning anywhere in the Apify run object or
dataset, and it was a **different domain each time**. This is strong
evidence of a genuine, non-domain-specific, roughly-1-in-5 silent failure
mode in the `automation-lab/trustpilot` Actor itself, not a fluke of
`shein.com`'s Trustpilot page specifically.

## Ground truth (www.thepearlsource.com only — the only domain with a verified sample)

**0 of 20 ground-truth rows matched, 0 API items available** — because
`www.thepearlsource.com` returned 0 reviews this run. This is a direct
consequence of the silent-failure anomaly above, not a data-quality
regression: the historical run (when `thepearlsource` DID return data)
matched 20/20 (100% on all content fields). This run cannot be used to
draw any accuracy conclusion for Apify — it only confirms the domain had
no data to compare.

## Run results

| Metric | Value |
|---|---|
| Businesses requested | 5 |
| Reviews requested per business | 200 |
| Total reviews requested | 1,000 |
| Raw reviews returned | 800 |
| Unique reviews returned | 800 |
| Duplicates | 0 |
| Zero-result businesses | 1 of 5 (www.thepearlsource.com) |
| Actor run status | SUCCEEDED |
| Errors logged | 0 (confirmed empty, not merely absent) |
| Retries | 0 (every poll and the dataset fetch succeeded on attempt 1) |
| Rate-limit events | 0 |
| Pagination | 1 dataset page (800 items, under the 1000/page limit) — `stop_reason: all_items_downloaded` |
| Actor run duration | 391,603 ms (~6.5 min) |
| Dataset retrieval | 2,164 ms |
| Wall clock | 402,134 ms (~6.7 min) |
| Cost | $0.465 measured |

## Cost

**Measured cost: $0.465** — read verbatim from the settled Apify Run
object's `usageTotalUsd` field (fetched after Apify's documented 5-second
settle-wait), not an estimate. Identical to the historical run's measured
cost, consistent with both runs producing exactly 800 billable unique
reviews (4 domains × 200) — Apify's per-event billing doesn't distinguish
which domain the events came from, so the missing domain doesn't reduce
cost, it just reduces yield.

`measured_actor_event_cost_usd` remains `null` — the settled Run object
didn't return a separate per-event breakdown, only the total. Flagged as
Pending, not invented.

## Comparison with previous run (2026-07-22)

| | Previous | Fresh | Difference |
|---|---|---|---|
| Unique reviews | 798 | 800 | +2 |
| Duplicates | 2 | 0 | −2 |
| Domain that silently failed | www.shein.com | www.thepearlsource.com | different domain each time |
| Domains with any shortfall | 3 (shein full loss, aliexpress −1, halara −1) | 1 (thepearlsource full loss only) | fresh run's 4 succeeding domains were each cleaner (0 duplicates vs 2) |
| Errors logged | 0 | 0 | none either time |
| Measured cost | $0.465 | $0.465 | $0 |
| Wall clock | 417,896 ms | 402,134 ms | −15,762 ms |
| Ground truth (thepearlsource) | 20/20 matched (100%) | 0/20 (no data) | thepearlsource happened to be the domain that failed this time |

**Does this change any previous conclusion?** It strengthens rather than
contradicts the prior finding: the silent single-domain 0-result failure
is now confirmed as a **repeatable pattern** (2 for 2 runs), not a one-off
`shein.com`-specific incident. `knowledge.md`'s Apify entry should
eventually reflect this as a recurring reliability defect in the Actor,
independent of which specific domain it hits.

## Issues found

- **Recurring silent single-domain failure, 2/2 runs, no error signal.**
  This is the primary finding — the Actor run reports `SUCCEEDED` with a
  clean bill of health while quietly dropping one domain's data entirely.
  Genuine reliability concern for anyone building on this Actor without
  independently verifying per-domain review counts.

## Still missing

- Root cause of the silent per-domain failure — unconfirmable from the
  Apify REST API surface used here (no per-domain sub-status or log
  excerpt was exposed in the run/dataset objects). Would require Apify's
  Actor run console log (not exposed via the endpoints this benchmark
  uses) — same limitation already noted in `MISSING_AND_GAPS.md` item A.6.
- Whether a 3rd run would fail a 3rd different domain, or start succeeding
  cleanly, is unknown — only 2 data points exist.
