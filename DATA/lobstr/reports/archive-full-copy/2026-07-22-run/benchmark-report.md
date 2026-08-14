# Lobstr.io Trustpilot Reviews — Benchmark Report

**Run date:** 2026-07-22
**Squid used:** `8d9e0b80d6d2481283c138104caf022d` (clean, dedicated squid — never renamed, never replaced)
**Run ID:** `4524c3ce2ad848739b5f2aea4902657b` (exactly one Run created for this entire benchmark)

## Result: Benchmark completed — 1,000 / 1,000 unique valid reviews

After fixing the `DuplicateSquid` configuration bug (see `duplicate-squid-fix.md`) and a pagination/attribution bug discovered while processing the first successful run (see `error-investigation.md`), all 5 domains reached exactly 200/200 with zero shortfall.

| Domain | Business | Task ID | Raw | Valid | Unique | Shortfall |
|---|---|---|---:|---:|---:|---:|
| www.thepearlsource.com | The Pearl Source | `edb32c4d...` | 200 | 200 | 200 | 0 |
| www.shein.com | SHEIN | `0125f07c...` | 200 | 200 | 200 | 0 |
| temu.com | Temu | `36f28a65...` | 200 | 200 | 200 | 0 |
| www.aliexpress.com | AliExpress | `960b12dc...` | 200 | 200 | 200 | 0 |
| thehalara.com | Halara | `e495dfee...` | 200 | 200 | 200 | 0 |
| **Total** | | | **1,000** | **1,000** | **1,000** | **0** |

Full evidence: [outputs/lobstr/domain-summary.json](../../outputs/lobstr/domain-summary.json).

## Two bugs found and fixed during this benchmark (both in our own code, not Lobstr's platform)

1. **`DuplicateSquid` (HTTP 400)** — the squid-configuration step tried to rename the clean squid to a name already held by the old contaminated squid. Fixed by removing the `name` field entirely — see `duplicate-squid-fix.md`.
2. **Pagination cap too low + wrong attribution field** — discovered only after the Run itself succeeded (1000/1000 confirmed by Lobstr): the `/v1/results` endpoint silently caps pages at 10 items regardless of the requested `limit=100` (documented as up to 100, observed as 10 — a real documentation/behavior gap), and result items have no `task` field at all, requiring attribution via `company_page_url` instead. Both fixed; results were then **re-fetched using the same Run ID** (zero new Runs) — see `error-investigation.md`.

## Rate limiting — real evidence, correctly handled

62 `HTTP 429 Throttled` responses occurred while paginating 100 result pages (confirms the documented ~2 req/sec limit on `/v1/results`). **All 62 were correctly retried to success** with exponential backoff — zero retries were exhausted, zero final failures. This is the first time in this project's benchmarks that retry logic was actually exercised against a real rate limit, not just written defensively.

## Duplicates

**Zero duplicates across all 1,000 records.**

## Required measurements

| Metric | Value | Basis |
|---|---|---|
| Requested reviews | 1,000 | design |
| Raw returned | 1,000 | measured |
| Valid | 1,000 | measured |
| Unique | 1,000 | measured |
| Duplicates | 0 | measured |
| Runs created | 1 (exactly one) | measured |
| Tasks created | 5 (reused from the earlier preflight setup — Lobstr did not create duplicate task objects when re-submitted) | measured |
| Rate-limit (429) responses | 62 | measured — all retried to success |
| Other errors | 0 | measured |
| Median / p95 latency (result-page requests) | 222 ms / 305 ms | measured |
| Credits consumed (measured) | **1,000** (`run_reported_credit_used` on the Run object, and confirmed via before/after balance: 20 → 1,020) | measured |

## Generated files

All required `outputs/lobstr/*` and `reports/lobstr/*` files (see final chat response for the complete list).

## Remaining blockers

None. The benchmark completed fully at target.
