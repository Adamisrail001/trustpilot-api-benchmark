# Lobstr.io — DuplicateSquid Configuration Fix

## File changed

`scripts/lobstr-benchmark.js`

## Function changed

`configureSquid(client, squidId, currentParams)`

## Old behavior

The function unconditionally sent `name: 'Trustpilot API Benchmark - Lobstr'` in the `PATCH /v1/squids/{squid_hash}` body on every call, regardless of the squid's current name. On the clean squid `8d9e0b80d6d2481283c138104caf022d`, this collided with the old contaminated squid (`5644e83e28ce412c9370da2bc46fcd31`), which already held that exact name — causing `HTTP 400 DuplicateSquid`.

Separately (found while verifying the fix, not part of the original reported error): this function only ever raised `max_results`, never `max_unique_results_per_run` — the same field whose omission caused the original contaminated run to cap out at 20 total results. The preflight code path (a *different* function) had already been fixed for this in an earlier session, but this main-benchmark path had not.

## New behavior

1. **`name` is no longer sent at all.** The clean squid is selected and used purely by ID (`squidId`, backed by `LOBSTR_SQUID_ID` in `.env`) — never by name, and the squid is never renamed.
2. The remaining fields (`is_active`, `to_complete`, `export_unique_results`, `no_line_breaks`) are kept, each with an inline comment explaining why it's functionally required for this benchmark's own measurements (not cosmetic carryover):
   - `is_active: true` — a squid must be active to start a Run
   - `to_complete: true` — ensures the run reaches a terminal state instead of staying open for scheduling
   - `export_unique_results: false` — so this benchmark's own deduplication logic is what gets measured, not Lobstr's server-side export dedup
   - `no_line_breaks: false` — preserves original review-text line breaks for exact ground-truth text comparison
3. **`max_unique_results_per_run` is now explicitly raised to 1,000** alongside `max_results` (raised to 200), whenever both keys are present in the squid's current `params` — closing the gap described above.

## Confirmations

- **The `name` field was removed:** confirmed by direct inspection of the edited function body (no `name:` key anywhere in the `body` object literal) and by static search — the string `"Trustpilot API Benchmark - Lobstr"` (without the `(dedicated)` suffix) no longer appears inside `configureSquid`.
- **No API Run was created while applying this fix.** Only local file edits (`Edit` tool) and local syntax checks (`node --check`, no network access) were performed. The only live API calls made during this entire fix-and-verify phase were the read-only diagnostic lookup and balance check from the *previous* turn's investigation (already reported then) — nothing new was called against the Lobstr API while writing or verifying this fix.
- **The clean squid remains the target:** `findOrCreateSquid` still resolves the squid purely from `LOBSTR_SQUID_ID` in `.env` (untouched, still `8d9e0b80d6d2481283c138104caf022d`) before `configureSquid` is ever called - unchanged by this fix.
- **The old squid was not touched:** no code path in this fix reads, writes, or references `5644e83e28ce412c9370da2bc46fcd31`.
- **Resume/idempotency protection is unchanged:** `ensureTasks` and `ensureSingleRun`'s local-file existence checks were not modified.
- **At most one Run per invocation is unchanged:** `ensureSingleRun`'s logic was not modified by this fix.
