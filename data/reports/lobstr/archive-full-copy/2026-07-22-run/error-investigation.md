# Lobstr.io — Error Investigation (Final Successful Run)

This covers the run that succeeded (`4524c3ce2ad848739b5f2aea4902657b`). The prior `DuplicateSquid` blocker from the earlier attempt is archived separately at `reports/lobstr/archive/duplicate-squid-name-attempt/error-investigation.md` and is not repeated here.

## Errors: 62 × HTTP 429 (Throttled) — all retried to success, zero final failures

- **Domain:** N/A — these occurred during result-page retrieval, which is shared across all 5 domains' data in one paginated stream, not attributable to a single domain.
- **Task ID:** N/A (not a task-level operation)
- **Run ID:** `4524c3ce2ad848739b5f2aea4902657b`
- **Export ID:** N/A — this API does not use a separate export step; results are read directly via `/v1/results`.
- **Stage:** Result-page retrieval (`GET /v1/results`, internal context label `get_results_next`)
- **HTTP status:** `429` (all 62 occurrences)
- **Lobstr error code:** `429`, type `"Throttled"`
- **Exact message:** `"Request was throttled. Expected available in 1 second."`
- **Sanitized response body (representative example):** `{"errors":{"message":"Request was throttled. Expected available in 1 second.","type":"Throttled","code":429}}`
- **Timestamps:** first at `2026-07-22T12:26:15.479Z`, last at `2026-07-22T12:32:16.449Z` (spread across the ~100-page retrieval)
- **Retry count:** 1 retry per occurrence, all successful on the next attempt (within the documented max of 3, exponential backoff) — **0 occurrences exhausted all 3 retries**
- **Failure source:** Rate limiting — confirms the documented ~2 requests/second limit on `/v1/results`.
- **Confirmed cause:** the result-page retrieval loop was requesting pages faster than the documented rate limit for this endpoint.
- **Inferred cause:** none needed — this is exactly the documented, expected behavior of a rate-limited endpoint under sustained sequential polling.
- **Unresolved evidence:** none.

## Silent failure / shortfall investigated and fixed (not an API error — found by inspecting output, exactly as instructed)

**Observable symptom (first post-fix run, before the second fix):** the Run succeeded (`status: done, total_results: 1000, unique: 1000` — confirmed directly by Lobstr), but the benchmark's own processing reported `total_raw_records: 200, unattributed_records: 200, valid_records: 0`. **No explicit Lobstr error was returned for this** — this was a silent shortfall discovered by inspecting the script's own aggregation output against the Run's authoritative totals.

- **Confirmed cause (verified by direct inspection of raw response data, not guessed):**
  1. `/v1/results?limit=100` returns `"limit": 10` in the actual response — the server silently caps the effective page size at 10 regardless of the requested value, and `"total_pages": 100`. The benchmark's own safety cap (`MAX_RESULT_PAGES = 20`) stopped retrieval after 20 pages × 10 items = 200 of the true 1,000 total.
  2. Result items contain no `task` field at all (confirmed by listing all 39 keys on a real item) — the benchmark's domain-attribution logic was checking a field that doesn't exist, so **100%** of retrieved items failed attribution.
- **Fix applied:** raised `MAX_RESULT_PAGES` to 150 (safely above the true 100-page requirement), and switched attribution to use `company_page_url` (confirmed present and correct on every item), normalized for www/non-www differences against `benchmark-domains.json`.
- **Re-verification:** re-ran using the same Run ID (zero new Runs) and confirmed `total_raw_records: 1000, unattributed_records: 0, valid_records: 1000, unique_valid_reviews: 1000`.
- **Unresolved evidence:** none — both the page-size cap and the missing `task` field were directly observed in saved raw response data, not inferred.
