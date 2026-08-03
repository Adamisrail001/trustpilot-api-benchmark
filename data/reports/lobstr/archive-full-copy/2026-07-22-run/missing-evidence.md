# Lobstr.io Trustpilot Reviews — Missing / Pending Evidence

## Cost

- **Dollar-equivalent cost:** Pending. Only credit counts are exposed via the API; the account's effective $/credit rate under its Super Admin / "free"-plan-with-negative-available-balance arrangement is not documented anywhere accessible via the API.
- **Failed-request billing:** untested — no request failed (all 429s were retried to success).

## Timing

- **Clean, single-invocation wall-clock time for the full scrape:** the benchmark's own scraping phase (Run creation → `done`) happened in the first script invocation; the second invocation (after the fix) only re-fetched already-completed results. The two invocations' timings were not merged into one clean total, so `timings.json` reflects only the result-retrieval phase (~99s) cleanly. The original scrape's exact duration is reconstructable from the archived poll history but was not re-measured as a single continuous run.

## Scalability

- 10x volume behavior: not tested.
- Whether `max_unique_results_per_run` can be raised beyond 1,000, and how the account's credit/plan limits interact with larger runs: not tested.

## Accuracy — other domains

`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` have no manually-verified ground-truth sample, consistent with every prior benchmark in this project.

## Developer Experience

- Official Lobstr SDK/CLI usability: not tested (raw HTTP used throughout).
- Support responsiveness: not tested.

## Resolved this run (no longer missing)

- Root cause of the `DuplicateSquid` error — fully confirmed (see `duplicate-squid-fix.md`).
- Root cause of the incomplete-pagination/zero-attribution result — fully confirmed and fixed (see `error-investigation.md`).
