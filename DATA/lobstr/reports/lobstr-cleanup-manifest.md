# Lobstr.io Cleanup Manifest

Generated prior to any deletion, per the required safety procedure. Contains no credential values.

## 1. Preserve (untouched)

**Shared methodology (not Lobstr-specific):**
- `docs/testing-criteria.md`
- `docs/structure-template.md`
- `benchmark-domains.json`
- `ground-truth/thepearlsource-sample.json`

**Lobstr reference and configuration (inspected — no contaminated identifiers found):**
- `docs/lobster/lobstr-documentation.md`
- `docs/lobster/lobstr-pricing.md`
- `lobstr-benchmark-config.md`

**Lobstr reusable implementation (inspected — no hardcoded Run/Task/Squid IDs, no `happen.com`, no hardcoded `20`-result-limit constant found in either file):**
- `scripts/lobstr-benchmark.js`
- `scripts/lib/lobstr-client.js`

**Environment:**
- `.env` — never read for values, never printed. Verified by boolean check only: `LOBSTR_API_KEY` is set (credential, untouched); `LOBSTR_CRAWLER_ID` is set (the legitimate Trustpilot-crawler-type identifier, not contaminated — kept); `LOBSTR_SQUID_ID` is set and **confirmed equal to the clean squid `8d9e0b80d6d2481283c138104caf022d`, confirmed NOT equal to the contaminated squid `5644e83e28ce412c9370da2bc46fcd31`** — kept as a configuration identifier per instruction, not contacted.

**All other providers (out of scope for this cleanup, confirmed untouched):**
- `docs/dataforseo/`, `dataforseo-benchmark-config.md`, `outputs/dataforseo/`, `reports/dataforseo/`
- `docs/outscraper/`, `outscraper-benchmark-config.md`, `outputs/outscraper/`, `reports/outscraper/`, `scripts/outscraper-benchmark.js`, `scripts/lib/outscraper-client.js`, `scripts/outscraper-ground-truth-compare.js`
- `docs/openwebninja/`, `openwebninja-benchmark-config.md`, `outputs/openwebninja/`, `reports/openwebninja/`, `scripts/openwebninja-benchmark.js`, `scripts/lib/openwebninja-client.js`, `scripts/openwebninja-ground-truth-compare.js`
- `docs/apify/`, `apify-benchmark-config.md`, `outputs/apify/`, `reports/apify/`, `scripts/apify-benchmark.js`, `scripts/lib/apify-client.js`, `scripts/apify-ground-truth-compare.js`
- `scripts/lib/csv.js`, `scripts/lib/dedupe.js` (shared utilities, unrelated to this cleanup)

## 2. Clean / Reset

**No in-place code edits were required.** `scripts/lobstr-benchmark.js` and `scripts/lib/lobstr-client.js` were inspected and contain no hardcoded old Run ID, Task ID, Squid ID, `happen.com` reference, or hardcoded `20`-result-limit constant. All prior-test state lived exclusively in:
- `outputs/lobstr/` (removed below — this **is** the reset), and
- `.env`'s `LOBSTR_SQUID_ID`/`LOBSTR_CRAWLER_ID` (already holding only current, clean values — confirmed above, not modified).

The implementation's idempotent-resume logic (checks for `raw/requests/run.json`, `raw/requests/tasks.json`, etc. before creating new paid resources) works correctly *because* those state files are being deleted — deleting them is the reset mechanism the code already expects, not a code change.

## 3. Remove

**`outputs/lobstr/archive/run-1-contaminated-squid/`** (18 files) — the original contaminated-squid run: `happen.com` data, old Run ID `4ce3f4de36c84ff3a850361c0d2f4df6`, old Squid ID `5644e83e28ce412c9370da2bc46fcd31`, old 20-result-limit evidence, old credits before/after.

**`outputs/lobstr/` top-level files** — `credits-preflight.json`, `execution-plan.json`, `preflight-report.json`, `preflight.log`.

**`outputs/lobstr/raw/requests/`** (8 files) — the clean-squid preflight's discovery/task/configure evidence (`crawlers-preflight.json`, `squid-create-dedicated.json`, `squid-configure-preflight.json`, `squid-details-before/after-configure.json`, `tasks-before/after-preflight.json`, `tasks.json`). These reference old Task IDs bound to a run that never executed and pagination/discovery state from a prior session — removed so the retest starts genuinely fresh, per instruction not to retain old Task IDs/pagination state even from the clean-squid path.

**`reports/lobstr/`** (6 files: `benchmark-report.md`, `elimination-assessment.md`, `field-coverage.md`, `ground-truth-comparison.md`, `missing-evidence.md`, `scorecard.md`) — all describe the invalid/contaminated run or the credit-blocked preflight; none reflect a completed clean benchmark.

**Confirmed: no file outside `outputs/lobstr/` or `reports/lobstr/` is included in this removal list. No other provider's evidence is touched.**

## 4. Directories recreated (empty, with `.gitkeep`)

- `outputs/lobstr/raw/requests/`
- `outputs/lobstr/raw/runs/`
- `outputs/lobstr/raw/tasks/`
- `outputs/lobstr/raw/results/`
- `outputs/lobstr/raw/exports/`
- `outputs/lobstr/errors/`
- `outputs/lobstr/smoke/`
- `reports/lobstr/`

## 5. New files created

- `.env.example` — safe placeholder names only, no values, covering every variable currently in `.env` (not just Lobstr's).

## Status after cleanup

**Lobstr benchmark status: Pending clean retest.**
