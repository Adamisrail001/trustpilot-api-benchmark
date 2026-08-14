# Trustpilot Review-Scraping API Benchmark — Knowledge Base

> This document is the verified factual record for the Trustpilot API benchmark and the article built on it. Every claim, figure, and score below must trace to logged benchmark evidence — nothing is inferred, estimated, or assumed. Evidence status is marked throughout: ✅ **CAPTURED** (complete, traceable evidence), ⚠️ **PARTIAL** (incomplete validation), ❌ **MISSING** / **Not tested** (no evidence — never softened into an estimate), ❓ **UNCLEAR** (provenance or interpretation unconfirmed), 🔴 **DISCREPANCY** (sources conflict, not silently resolved).
>
> **Scope of the benchmark (all 5 providers):** DataForSEO, Outscraper, OpenWeb Ninja, Apify, Lobstr were each run once, on the same 5 fixed Trustpilot business domains — `www.thepearlsource.com`, `www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` — each targeting 200 reviews (1,000 requested per provider). A separate isolated Lobstr test targeted `www.thepearlsource.com` alone, later verified at a 2,000-review target with 2,000/2,000 unique valid reviews and 0 duplicates (2026-08-13 — see Live verification pass below). 🔴 An earlier 1,000-review version of this same isolated test is referenced elsewhere but has no surviving raw evidence anywhere in this project — treat only the 2,000-review figure as confirmed.
>
> **Live verification pass (2026-08-13):** DataForSEO, Apify, and Outscraper's 5-domain benchmarks were rerun live against real accounts, and Lobstr's isolated single-business test was extended to a 2,000-review target on `www.thepearlsource.com` (still isolated on its own dedicated squid, still separate from the 5-domain comparison). OpenWeb Ninja was not rerun (no quota-remaining figure was available). Every figure below reflects this live pass where one exists; where it doesn't, the prior evidence is marked as such.
>
> **Ground truth exists for exactly 1 of the 5 domains** (`www.thepearlsource.com`, a manually-verified 20-row sample). SHEIN, Temu, AliExpress, and Halara have **no ground truth at all**. Every accuracy/field-coverage figure below is valid only for `www.thepearlsource.com` and must never be read as representative of the other four domains — this is restated in Section 6 rather than assumed silently.
>
> **Rubric authorship flag:** the scoring rubric (`criteria.md`) is headed "Owner: lobstr.io content team." Lobstr is also one of the five evaluated providers. Both source projects flag this explicitly; neither resolves it. Treat any Lobstr-favorable figure with that in mind.

---

## Article Meta

- **Primary SEO keyword:** **"trustpilot reviews api"** — writer-confirmed.
- **Full roster tested:** Apify, OpenWeb Ninja, DataForSEO, Outscraper, Lobstr (Trustpilot's own official API was never tested — see "Eliminations (E1–E6)" below).

---

## Benchmark Methodology Record

- 🔴 **Test window (corrected):** not a single session — the raw evidence dates span roughly a week: DataForSEO's committed run is dated 2026-07-21 (its only run — no archived/committed split exists for this provider); Apify and OpenWeb Ninja's original successful runs 2026-07-22; and Apify's committed evidence / Lobstr's isolated test / OpenWeb Ninja's failure / **Outscraper's committed run** all 2026-07-29. Outscraper also has a separate **archived** run dated 2026-07-21 — that earlier date belongs to the archived evidence, not the committed run, which was previously misgrouped with DataForSEO here. A further live-verification pass ran 2026-08-13 (see the header note above).
- **Shared script template:** one benchmark script template adapted per provider's auth/request format — DataForSEO's port is the weakest/least mature.
- 🔴 **What was logged (corrected):** raw request/response captures, timings, error/cost/pagination reports per provider — uneven: DataForSEO is missing **2** of the standard analysis files (error, pagination reports) every other provider has. Its `cost-report.json` was previously also missing but was backfilled 2026-07-24 — regenerated from the real `cost` field already present in each raw `task_post` response (no new measurement taken), per the file's own `note_on_generation`.
- **Public gist/repo URL:** ⚠️ **MISSING — needs publishing.** Raw benchmark evidence (scripts, logs, raw data) is not publicly published yet. Writer will supply the GitHub/Gist URL once published. Reproducibility claims in the FAQ ("Is this benchmark reproducible?") must not overstate this — no public link exists today.

---

## Eliminations (E1–E6)

🔴 **Corrected — this was previously understated as "PARTIAL... rest remain open pending evidence."** That's wrong: all five benchmarked providers have complete, dedicated elimination assessments (all six criteria each), not just the one Trustpilot exclusion below.

**Trustpilot's official API — the one exclusion:**

| API | Criterion failed | One-line reason | Evidence |
|---|---|---|---|
| Trustpilot Official API (Business Units / Product Reviews / Service Reviews) + Data Solutions API | **E1 — No self-serve access** | Neither the standard Business API nor the cross-business Data Solutions API offers instant self-serve access — both require Trustpilot-side setup (API module access / waitlist) before a working key can be obtained. Excluded during pre-screening; no live access was ever obtained and no benchmark was run against it. | Writer-confirmed + [developers.trustpilot.com](https://developers.trustpilot.com/introduction) |

**All 5 benchmarked providers — not eliminated, PASS on all 6 criteria (sourced, per-provider `elimination-assessment.md` files):**

| Provider | E1 | E2 | E3 | E4 | E5 | E6 | Evidence |
|---|---|---|---|---|---|---|---|
| Apify | PASS | PASS | PASS | PASS | PASS | PASS | `DATA/apify/reports/archive-full-copy/2026-07-22-run/elimination-assessment.md` |
| DataForSEO | PASS | PASS | PASS | PASS | PASS | PASS | `DATA/dataforseo/reports/dataforseo-elimination-assessment.md` |
| Outscraper | PASS | PASS | PASS | PASS | PASS | PASS | `DATA/outscraper/reports/archive-full-copy/2026-07-21-run/elimination-assessment.md` |
| OpenWeb Ninja | PASS | PASS | PASS | **NOT eliminated, but flagged** (this account's active "Basic" plan isn't in the published rate card — a cost-transparency gap, not an elimination) | PASS | PASS | `DATA/openwebninja/reports/archive-full-copy/2026-07-22-run/elimination-assessment.md` |
| Lobstr | PASS | PASS | **PASS, with one flagged gap** (`/v1/results` `limit` documented as configurable but silently capped at 10) | PASS | PASS | PASS | `DATA/lobstr/reports/archive-full-copy/2026-07-22-run/elimination-assessment.md` |

⚠️ **MISSING: which other tools were discovered pre-benchmark and why each was excluded — ask writer | needs research.** No list, name, or evidence of these tools exists anywhere in the project. This is the only genuinely open item in this section — all 5 tested providers' own elimination status is fully resolved above.

---

## Official API Deep-Dive (Trustpilot)

- **What it actually offers:** Trustpilot exposes three official APIs — Business Units API, Product Reviews API, Service Reviews API — plus a separate **Data Solutions API** that can return review data across businesses (not just one business's own reviews). [Trustpilot developer docs](https://developers.trustpilot.com/)
- **Access model:** requires a Trustpilot for Business account with **API module** access via the Developer Portal. Public endpoints authenticate with a simple `apikey` header; private endpoints (and the Data Solutions API) require full OAuth 2.0 + Trustpilot-side setup (waitlist/approval) — writer-confirmed this is not self-serve for either path. [Authentication overview](https://developers.trustpilot.com/authentication/) · [Authorization code grant](https://developers.trustpilot.com/grant-type-auth-code/)
- **Public Business Units API note:** returns reviews via `pageToken` pagination but excludes customer email/order ID; the private/OAuth version includes those fields. [Business Units API](https://developers.trustpilot.com/business-units-api)
- **Pricing:** ⚠️ MISSING — unconfirmed. No direct billing evidence exists; do not claim paid pricing without it.
- **THE wall:** not a business's-own-data limitation (the Data Solutions API can cross businesses) — the actual wall is **non-self-serve access**: both the standard Business API and the Data Solutions API require Trustpilot-side setup/waitlist before a working key can be obtained, which fails this benchmark's E1 self-serve eligibility requirement.
- **Live access / code example:** ❌ Not obtained. No working access was ever secured; no live benchmark was run. Documented here as excluded during pre-screening, before live testing — not a wall discovered mid-benchmark.

---

## 1. Success Rate & Reliability

> Every figure below describes **one benchmark run of 1,000 requested reviews per provider**. None of it is evidence of reliability under repeated trials, concurrent load, or sustained production use — that distinction is preserved throughout, not collapsed into a single "reliability" adjective.

### Apify

- **Requests attempted (committed run, 2026-07-29):** 1 Actor run (`automation-lab/trustpilot`, all 5 domains submitted together) + 34 status-poll requests + 1 dataset-items fetch = 36 total calls (directly counted from `DATA/apify/analysis/timings.json`'s `per_request` array, 35 entries, plus the 1 actor-start call which isn't itself in that array).
- **Successful requests:** all HTTP-level calls succeeded; run status reported `SUCCEEDED`.
- **Raw / unique reviews returned (committed run):** 800 / 800 (target 1,000) — **overall success rate 80%**. `www.thepearlsource.com` returned **0 of 200** requested reviews, with **no error, retry, or failure signal recorded in the benchmark evidence** (the error log is empty).
- 🔴 **Recurring, business-agnostic silent failure — three separate live runs, three different businesses:** an earlier evidence pass (superseded) pinned this same zero-result signature on `www.shein.com` (that run's overall success rate: 79.8%); the committed 2026-07-29 run moved it to `www.thepearlsource.com` (80%, above); a fresh live rerun on 2026-08-13 (Run ID `g2fs1B2BhRm0mDb2R`) moved it again, this time to `www.thehalara.com` (820/1,000, 82% — the other 4 domains, including `www.thepearlsource.com`, returned their full 200 each). Every occurrence reports a clean `SUCCEEDED` status with zero error signal recorded in the benchmark evidence. This is no longer a one-off — it is a repeating defect that lands on a different business each run (79.8%, 80%, and 82% success respectively). With only 3 data points, the evidence does not establish that the affected business is random, or identify what determines it. Root cause remains **unresolved** — would require inspecting Apify's live console run log, not exposed via the documented REST endpoints used here.
- 🔴 **Correction: no duplicates in the committed run.** `DATA/apify/analysis/domain-summary.json` shows `duplicate_records: 0` overall, with `www.shein.com`, `temu.com`, `www.aliexpress.com`, and `thehalara.com` each returning exactly 200 raw = 200 unique = 0 shortfall. A prior draft of this document claimed `aliexpress.com`/`thehalara.com` each had 1 internal duplicate (199 unique) — that claim does not match this evidence file and has been removed.
- **Retries:** 0 triggered (none needed at HTTP level, in any of the three runs).
- **Scorecard sub-score:** 1.38/2.0 — success-rate sub-score reflects the 79.8%, 80%, and 82% success rates observed across the three runs; error-handling-quality sub-score penalized heavily because the failure produces zero detectable signal every time. The recurring pattern strengthens confidence in this score without changing the sub-criteria math. 🔴 **Corrected: this total is sourced, not unreproducible.** `DATA/apify/reports/archive-full-copy/2026-07-22-run/scorecard.md` records the exact itemized breakdown for this criterion: success rate 0.80/1.0 (798/1,000 = 79.8%) + empty/partial 0.20/0.4 (1 of 5 domains, SHEIN, returned completely empty) + error handling 0.10/0.3 (penalized — the SHEIN failure produced zero error signal) + stability 0.28/0.3 (clean run otherwise) = **1.38/2.0**. This breakdown belongs specifically to the archived run (SHEIN empty, 79.8%), not a blended figure across all three runs — but it is the real, sourced calculation behind this total.

### OpenWeb Ninja

🔴 **Superseded finding — kept below for provenance, followed immediately by the current state.** An earlier evidence pass recorded a clean run: 50 logical page requests (5 domains × 10 pages, 51 total HTTP calls counting 1 retry), 1,000/1,000 unique reviews (100%), 0 shortfall, 0 duplicates, with exactly 1 HTTP 500 on `www.thepearlsource.com` page 1 (retried once, succeeded). That evidence no longer reflects the account's current state.

**Current, verified state:** a rerun of the identical benchmark to confirm these numbers before publishing failed completely. `DATA/openwebninja/analysis/domain-summary.json`: **0 of 1,000 reviews returned across all 5 domains, `overall_success_rate_percent: 0`**, every domain's `stop_reason: "fetch_failed"`. `DATA/openwebninja/analysis/error-log.json`: **75 entries, every one `status: 429`**, spanning `2026-07-29T08:20:33Z`–`08:57:57Z` (~37 minutes across at least two retry waves) — sustained rate-limiting that the account's own retry/backoff logic could not clear. This was not retested during the 2026-08-13 live-verification pass (no `OPENWEBNINJA_QUOTA_REMAINING` figure was available from the account dashboard — the API has no quota-check endpoint).

- 🔴 **Root-cause investigation (2026-08-13): most consistent with an account/quota-side issue, not a confirmed provider regression — do not read this as proof of permanent product failure.** Compared against the 2026-07-22 successful run: request parameters, endpoint, and auth are byte-identical between the two runs, ruling out a test/configuration difference. The 07-22 run's only friction was one unrelated `HTTP 500`, well clear of any rate limit. The 07-29 failure's **very first logged request was already a 429** — **suggesting, but not proving,** a quota/account state that had already entered before the session started, rather than a limit triggered by this benchmark's own request volume — and persisted through 37 minutes and multiple retry waves despite a 31-minute cool-down pause. The API never exposes rate-limit metadata (`limit`/`remaining`/`retryAfter` are `null` in every logged event, both runs), so the exact mechanism (monthly quota exhaustion on the unpublished "Basic" tier vs. a stricter live limit vs. an account flag) **cannot be confirmed from available evidence** — no status-page incident, changelog entry, or dashboard quota figure was accessible. Treat OpenWeb Ninja's current 0/1,000 result as an accurately-*observed* benchmark outcome, not a settled verdict on the product's underlying reliability.

- **Scorecard sub-score:** 0.10/2.0 — down from 1.98. Breakdown: success rate 0.00/1.0 (0%) + empty/partial 0.00/0.4 (5/5 domains empty) + error handling 0.10/0.3 (retries were attempted with clear structured 429 bodies, credited for clarity, but never actually recovered) + stability 0.00/0.3 (sustained rate-limiting is real instability, not a clean run).

### DataForSEO

- **Requests attempted:** 10 (5 `task_post` + 5 `task_get`).
- **Successful requests:** 10 of 10, first attempt, 0 retries.
- **Raw / unique reviews returned:** 1,000 / 999 — **99.9% success rate**. The 1 lost review is `temu.com`'s single task returning one review twice within its own response (an internal server-side duplicate, not something the benchmark introduced or re-ran to fix).
- **HTTP errors:** 0. Status codes seen: `20000 "Ok."`, `20100 "Task Created."`.
- **Scorecard sub-score:** 1.90/2.0.
- **Discrepancies noted:** the secondary source project contains a DataForSEO benchmark script — but that source explicitly labels it "reconstructed... not the original," "unrun this session (no live key)," with an unverified auth mechanism. It should not be assumed to be the original script that produced the raw JSON until its provenance is confirmed one way or the other.

### Outscraper

- **Requests attempted:** 5 submission requests + polling requests until `status: Success`. The two sources disagree on the exact polling count — see "Discrepancies noted."
- **Successful requests:** all attempted requests succeeded; 0 failures, 0 retries (`attempts: 1` throughout).
- **Raw / unique reviews returned:** 1,000 / 1,000 — **100% success rate**, every domain hit its 200-review target on page 1 (`stop_reason: target_reached`).
- **HTTP errors:** 0.
- **Scorecard sub-score:** 1.92/2.0.
- 🔴 **Polling-request count — corrected.** A prior draft of this document cited "84 poll-phase + 5 submit-phase = 89 total," attributing this to "the canonical `DATA/outscraper/analysis/timings.json`." That 89-request, 512,595ms figure actually belongs to the **archived** `DATA/outscraper/analysis/archive-full-copy/2026-07-21-run/timings.json`. The current, non-archived committed file (`DATA/outscraper/analysis/timings.json`) is a separate, later run (`benchmark_start: 2026-07-29T07:59:24Z`) with **58 poll-phase entries + 5 submit-phase entries = 63 total**, directly counted from its `per_request` array. Both figures are real evidence from this project, just from two different dated runs — see Section 3 for the corresponding timing correction. The primary source's "~120" figure matches neither run's array length and remains **not treated as the fact of record**.

### Lobstr

🔴 **Corrected — same misattribution as Section 3.** These figures were previously labeled an "isolated single-business run" for `www.thepearlsource.com`. They are not: `DATA/lobstr/raw/requests/tasks.json` and `DATA/lobstr/analysis/domain-summary.json` confirm this is the standard **5-domain shared benchmark** (`www.thepearlsource.com`, `www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com`, 200 each), run on the same shared squid (`8d9e0b80d6d2481283c138104caf022d`) as the archived run — not a separate isolated test.

- **Requests attempted (current, committed run, 2026-07-29):** squid/task/run setup calls (squid-configure, squid-reused check, run creation, 5-task retrieval) + **116 requests from `timings.json`** (15 `poll_run` + 101 `get_results`).
- **Successful requests:** run status `done`, `done_reason: tasks_done` (`run-state.json`); all 101 result pages retrieved, pagination stopped at `no_next_page` after the full target was collected.
- **Raw / unique reviews returned:** 1,000 / 1,000 across **5 domains, 200 each, 0 shortfall on any domain** — **100% success rate**, 0 duplicate_records, 1,000 unique Trustpilot review IDs. (Not "from one Trustpilot business," as previously stated.)
- **HTTP errors: 7** confirmed HTTP 429 "Throttled" events during result-page retrieval — figure itself correct, now correctly attributed to this 5-domain run.
- **Retries:** confirmed directly in `timings.json` — exactly 7 `get_results` entries show `attempts: 2` (94 show `attempts: 1`; 94+7=101), matching the 7 error-log entries 1:1. All 7 succeeded on the second attempt — 0 records lost.
- **A separate, earlier, fully-failed setup attempt exists** (archived, not part of the counted run): an `HTTP 400 DuplicateSquid` error blocked squid configuration before any task or run existed, because the benchmark script tried to rename the clean squid to a name already held by an old contaminated squid. Fixed by never sending a `name` field. *(Already correctly attributed — unchanged.)*
- **The genuinely separate isolated single-business test** (`www.thepearlsource.com` alone) is a different test: first run at a 1,000-review target, later extended to 2,000 reviews on 2026-08-13 (`outputs/lobstr-single-domain-test/summary.json`: 2,000/2,000 unique, 0 duplicates — see header Scope note and Section 4, Scalability). **No request-count, error, or retry evidence for the original 1,000-review version of that isolated test exists anywhere in this project** (`outputs/` is gitignored and was overwritten by the 2026-08-13 rerun) — it must not be conflated with the 5-domain figures above.
- 🔴 **Scorecard sub-score 1.95/2.0, not 1.80/2.0 — reconciled with the Final Summary.** This section previously stated 1.80, while the Final Summary table used 1.95 for this same criterion — a direct contradiction, neither figure sourced. Standardized here on **1.95** since that is the figure the Final Summary's 7.88 total is built on. ⚠️ **Still not independently reproducible.** No file in this project contains "1.95" either. The only recorded breakdown anywhere is the **archived 2026-07-22** run's own scorecard: success rate 1.00/1.0 + empty/partial 0.40/0.4 + error handling 0.29/0.3 (62 real 429s, all retried) + stability 0.28/0.3 = **1.97/2.0** — for a different run (62×429, two bug fixes) than the one described above (7×429, clean, no fixes needed). Neither 1.80 nor 1.95 is proven wrong by evidence, only unverifiable — same limitation as Apify's 1.38/2.0 elsewhere in this section.

**Cross-provider reliability summary**

| Provider | Requested | Raw / Unique returned | Success rate | Real errors this run |
|---|---:|---|---:|---|
| Apify | 1,000 | 800–820 raw / 798–820 unique across 3 runs | 79.8–82% (3/3 runs) | 0 every time (silent zero-result, different business each run: SHEIN → thepearlsource → thehalara.com) |
| OpenWeb Ninja | 1,000 | **0 / 0 (current)** — was 1,000/1,000 in a superseded earlier pass | **0% (current)** | **75× HTTP 429, unrecovered (current)** — was 1× HTTP 500 recovered, superseded |
| DataForSEO | 1,000 | 1,000 / 999 | 99.9% | 0 |
| Outscraper | 1,000 | 1,000 / 1,000 | 100% | 0 |
| Lobstr | 1,000 | 1,000 / 1,000 across 5 domains | 100% | 7× HTTP 429 (all recovered) |

---

## 2. Cost Effectiveness

> Strict distinction maintained throughout: **confirmed billed cost** (from the provider's own billing field) vs. **API usage field** vs. **published rate-card calculation** vs. **credit count with no monetary conversion** vs. **no direct charge observed during the test.** These are never conflated.

### Apify

- **Billing model:** pay-per-event (run-start fee + per-review charge).
- **Published pricing:** $0.005/run start + $0.000575/review (free tier).
- **Measured billed cost: $0.465** — directly from `usageTotalUsd` on the settled Run object (`chargedEventCounts: {start: 1, review: 800}`). This is a real, API-reported billing figure, not a calculation. 🔴 Corrected: the formula estimate for 800 reviews (not 798 — see Section 1's duplicate-count correction) is `$0.005 + 800 × $0.000575 = $0.465` — an **exact match** to the measured cost, not "within 0.26%" as a prior draft stated (that figure used the wrong 798 denominator).
- 🔴 **Corrected: $0.5812**, not $0.5827 — `DATA/apify/analysis/cost-report.json` states `cost_per_1000_successful_reviews_usd: 0.5812` directly ($0.465 ÷ 800 × 1,000). The prior $0.5827 figure used a denominator of 798, which predates this session's duplicate-count correction (the committed run has 0 duplicates and 800 unique reviews, not 798 — see Section 1).
- **Scorecard sub-score:** 1.20/1.5 — the highest Cost sub-score of the five, credited because this is a real measured billing figure, not because it is the cheapest in dollar terms.

### OpenWeb Ninja

- **Billing model:** tiered monthly plans (Free/Pro/Ultra/Mega) + pay-as-you-go, documented per-request.
- **Measured billed cost: none.** The account's actual plan is **"Basic," which is not one of the four published tiers** — no confirmed $/request rate exists for it at all.
- **Calculated/estimated cost (by hypothetical tier, not this account's real rate):** Free $0 (marginal) / Pro $0.125 / Ultra $0.075 / Mega $0.0375 / Pay-as-you-go $0.25, for the 50 requests attempted.
- 🔴 **Current state: 0 successful reviews returned this run** (Section 1) — there is no successful output to amortize any cost against at all, which is a materially worse position than "rate unconfirmed." Whether the 75 failed requests consumed billable account quota **cannot be confirmed from available evidence** — `DATA/openwebninja/analysis/cost-report.json` states OpenWeb Ninja has no account/usage/quota API endpoint, so no before/after quota measurement exists for this run.
- **Cost per 1,000 successful reviews: cannot be computed** — both because the "Basic" plan's rate is unconfirmed and because there were 0 successful reviews this run.
- **Scorecard sub-score:** 0.35/1.5 — down from 0.70. Breakdown: cost/1K 0.00/0.8 (down from 0.30 — no successful output exists to amortize against) + billing fairness 0.05/0.3 (down from 0.10 — 75 failed retries returned zero delivered reviews; whether this consumed billable quota is unconfirmed, see above) + free tier 0.20/0.2 (unchanged, documented) + pricing transparency 0.10/0.2 (unchanged).

### DataForSEO

- **Billing model:** pay-per-task, priced per 20-review depth block.
- **Published pricing:** $0.00075 per 20 reviews (standard priority) → $0.0075 per 200-review task.
- **Measured billed cost: $0.0375** ($0.0075 × 5 tasks), taken directly from the `cost` field in each `task_post` response — this is a real, per-call billing field, not an estimate. It matches the pre-run formula estimate exactly (0% variance).
- **Cost per 1,000 successful unique reviews: $0.03754** ($0.0375 ÷ 999 × 1,000) — the **cheapest measured figure of all 5 providers**, by a wide margin (Outscraper's calculated estimate is ~72–80x higher for the identical benchmark).
- **Scorecard sub-score:** 1.10/1.5.
- **Known gap:** DataForSEO has **no cost, error, or pagination report** anywhere in the primary source project's raw outputs — the only DataForSEO cost evidence is the `cost` field embedded in each `task_post`/`task_get` raw response. Any dollar figure above this measured $0.0375 is a published-rate estimate, explicitly labeled as such, never a second measurement.

### Outscraper

- **Billing model:** documented per-review rate card (first 100 reviews/period free, then $3/1,000 up to 50,000, $1/1,000 above).
- **Measured billed cost: none.** Outscraper exposes no account-balance or per-request billed-cost endpoint.
- **Calculated/estimated cost:** $2.70 (fresh-account scenario: 900 billable × $0.003) or $3.00 (free-tier-already-used scenario: 1,000 billable × $0.003) — both explicitly labeled calculated, not measured. Measured usage (1,000 reviews across 5 domains) matches the pre-run plan exactly.
- **Cost per 1,000 successful unique reviews:** $2.70–$3.00 (estimated range, not measured) — roughly **72–80x more expensive than DataForSEO's measured cost** for the identical 1,000-review benchmark; this is a documented pricing-model difference, not a measurement error.
- **Scorecard sub-score:** 0.85/1.5.

### Lobstr

- **Billing model:** credit-based, 1 credit = 1 unique result.
- 🔴 **Correction: the advertised rate is $0.50 per 1,000 reviews, not $1.** Directly fetched from Lobstr's own current Trustpilot Reviews Scraper store page (`https://www.lobstr.io/store/trustpilot-reviews-scraper`, checked 2026-08-13), which states verbatim: "$0.5 per 1000 reviews." A prior draft of this document cited "$1/1,000, writer-confirmed" — that figure does not match the provider's own current published rate and has been corrected. **This makes Lobstr's real cost multiple smaller than previously stated: ~13.3x DataForSEO's measured $0.03754/1,000 (using $0.50), not ~26.6x (the old $1 figure implied).**
- **Measured billed cost in dollars: none directly from this account.** The benchmark account is on Super Admin/"free"-plan terms with no exposed $/credit conversion via the API — the $0.50/1,000 figure is official published documentation, not a billing-API measurement.
- **Credits consumed: 1,000** for 1,000 unique reviews (2026-07-29 isolated test) — an exact 1:1 ratio, confirmed by the Run object's `credit_used: 1000` field and before/after credit snapshots (`consumed: 0` → `consumed: 1000`). A follow-up live test on 2026-08-13 pushed this to **2,000 reviews for 2,000 credits** — the same 1:1 ratio held exactly at 2x the volume (see Section 4, Scalability).
- **Cost per 1,000 successful reviews:** 1,000 credits per 1,000 reviews, at the official published rate of $0.50/1,000 — credit consumption is measured; the dollar rate is sourced to the provider's own current documentation, not a billing-API measurement on this account.
- **Scorecard sub-score:** 1.08/1.5 (unchanged numerically — the underlying $0.50 figure was already what this sub-score used; only the confidence label and the "$1" narrative text elsewhere in this document needed correcting).

**Cross-provider cost summary**

| Provider | Cost evidence tier | Cost per 1,000 successful reviews | Cost sub-score |
|---|---|---:|---:|
| DataForSEO | ✅ Measured (API `cost` field) | **$0.03754** (cheapest absolute price) | 1.10/1.5 |
| Apify | ✅ Measured (API `usageTotalUsd` field) | $0.5812 | **1.20/1.5** (highest sub-score) |
| Lobstr | ✅ Credit consumption measured (1:1, confirmed at both 1,000 and 2,000-review scale); dollar rate sourced to official current documentation, not this account's billing API | 1,000 credits at the published $0.50/1,000 = $0.50 | 1.08/1.5 |
| Outscraper | ⚠️ Estimated from published rate card only | $2.70–$3.00 (not measured) | 0.85/1.5 |
| OpenWeb Ninja | ❌ No confirmed rate for this account's actual plan, and 0 successful reviews this run to amortize against | Not computable | **0.35/1.5** (down from 0.70) |

---

## 3. Speed

> Timing figures are **not directly comparable** across providers without accounting for differing execution models: 🔴 **corrected** — OpenWeb Ninja is the only provider that measures one continuous synchronous run; DataForSEO, Apify, and Outscraper are all async submit-then-poll (create/start, then poll for completion), so their wall-clock totals include polling overhead a purely synchronous call wouldn't have; Lobstr is async with an additional separate paginated result-retrieval phase on top of that.

### Apify

- 🔴 **Corrected figure:** `DATA/apify/analysis/timings.json` (the current, committed evidence file) states **`wall_clock_ms: 402,134`** (~6 min 42 s) — not 417,896 ms as a prior draft of this document stated. The 417,896 figure does not appear in any raw evidence file in this project and has been removed.
- **Requests:** 1 actor-start call + 34 status-poll requests + 1 dataset-items fetch = 36 total (the 34+1=35 non-start calls directly counted from `timings.json`'s `per_request` array; matches Section 1).
- **Median latency:** 2,022 ms (status-poll round trips). **p95 latency:** 2,874 ms. **Min/max:** 779–3,002 ms.
- **Comparability limitation:** the 800/1,000 raw shortfall means duration-per-successful-review is worse than duration-per-requested-review. These figures measure polling-call latency, not per-review fetch time — not directly comparable to OpenWeb Ninja's per-request numbers, the only genuinely synchronous provider (see the corrected execution-model note above).
- **Scorecard sub-score:** 1.10/1.5 — previously left unscored ("not stated in the source material") despite `timings.json` containing everything needed to score it. Filled in now: median latency 0.30/0.5 (2,022 ms) + wall-clock 0.40/0.5 (402,134 ms for 800 reviews) + p95 0.20/0.3 (2,874 ms) + async availability 0.20/0.2 (native multi-company Actor run, documented and used).

### OpenWeb Ninja

🔴 **Superseded finding, kept for provenance:** an earlier evidence pass measured 180,749 ms total, 1,870 ms median, 3,684 ms p95 across 50 sequential requests (+1 retry).

**Current, verified state:** `DATA/openwebninja/analysis/timings.json` (final logged wave) shows **67,008 ms wall-clock**, but `error-log.json`'s full span (75 sustained 429s) covers **~37 minutes** across at least two retry waves — the 67s figure only captures the last wave, not the full time spent failing to get data.

- **Scorecard sub-score:** 0.23/1.5 — down from 0.98. Breakdown: median latency 0.10/0.5 (responses did come back, just as errors — partial credit, not the delivery-latency this sub-criterion is meant to reward) + wall-clock 0.00/0.5 (the batch never completed) + p95 0.05/0.3 (minimal credit) + async availability 0.08/0.2 (unchanged, structural — synchronous, no batching, unaffected by this run's outcome).

### DataForSEO

- **Total wall-clock duration (committed run, 2026-07-21):** 165,513 ms (~2 min 46 s) — the fastest total among the original five.
- **Median latency (per-call round trip, committed run):** 404 ms.
- **p95 latency (committed run):** 2,378 ms, driven by one cold-start `task_post` call.
- **Requests:** 10 total (5 `task_post` + 5 `task_get`).
- 🔴 **Live rerun (2026-08-13) shows materially slower queue processing:** each domain's full submit-to-result cycle took 59–108 seconds this time (thepearlsource 108.3s, shein 92.0s, temu 100.7s, aliexpress 61.3s, halara 58.9s; total ≈421,200 ms serial, vs. 165,513 ms in the committed run — same serial submit-then-poll execution pattern both times, so this is a fair, current-vs-historical comparison, not measurement noise). All 5 domains still completed correctly (1,000/1,000, $0.0375 total, same as the committed run) — this is a **speed regression, not a reliability or cost regression.** Consistent with DataForSEO's own documented worst-case SLA ("up to 45 minutes" for standard priority), which the committed run's lucky fast time never came close to testing.
- **Comparability limitation:** the per-call median latency (404 ms) and p95 (2,378 ms) above were not re-measured during the 2026-08-13 rerun — only the full batch wall-clock was. Treat those two figures as carried forward from the committed run, not re-verified.
- **Scorecard sub-score:** 1.12/1.5 — down from 1.32. Breakdown: median latency 0.45/0.5 (unchanged, not re-verified today) + wall-clock 0.25/0.5 (down from 0.45, reflecting today's measured ~2.5x slowdown) + p95 0.22/0.3 (unchanged, not re-verified today) + async availability 0.20/0.2 (unchanged, documented).

### Outscraper

- 🔴 **Corrected figures — the current committed evidence file is a different, later run than what a prior draft cited.** `DATA/outscraper/analysis/timings.json` (`benchmark_start: 2026-07-29T07:59:24Z`) states: **wall-clock 344,297 ms** (~5 min 44 s), **median latency 1,094 ms**, **p95 latency 2,500 ms**, **5 submissions + 58 polling requests = 63 total**. The previously-cited 512,595 ms / 1,169 ms / 1,982 ms / 89-request figures belong to the **archived** `.../archive-full-copy/2026-07-21-run/timings.json` — a real, earlier run, not the current committed evidence.
- **Comparability limitation:** the async submit-then-poll design means total wall-clock reflects many poll cycles, not necessarily slower per-request processing. The current run's faster wall-clock (344,297 ms vs. the archived run's 512,595 ms) came with a *worse* p95 (2,500 ms vs. 1,982 ms) — median improved, tail latency did not; this run should not be read as uniformly faster.
- **Scorecard sub-score:** 1.10/1.5 — up slightly from 1.07 (which was computed against the archived run's numbers). Breakdown against the current evidence: median latency 0.37/0.5 (1,094 ms, an improvement) + wall-clock 0.35/0.5 (344,297 ms, an improvement) + p95 0.18/0.3 (2,500 ms, a regression) + async availability 0.20/0.2 (unchanged, documented).

### Lobstr

🔴 **Corrected — misattribution found.** The figures previously here were labeled as an "isolated single-business run" for `www.thepearlsource.com` alone. They are not. `DATA/lobstr/analysis/domain-summary.json` (the file behind the 101-page, 7×429 figures) shows **5 domains, 200 reviews each** — the standard shared benchmark, not the isolated test. Two different runs of that 5-domain benchmark exist in the evidence, with different speed numbers:

- **Current, committed run** (`DATA/lobstr/analysis/timings.json`, 2026-07-29): wall-clock **220,530 ms** (~3 min 41 s), median latency **594 ms**, p95 latency **1,984 ms**, **116 total requests** (15 `poll_run` + 101 `get_results` — this is the same run behind Section 1's 101-page/7×429 figures).
- **Archived run** (`DATA/lobstr/reports/archive-full-copy/2026-07-22-run/`, superseded): wall-clock **99,346 ms** (~1.7 min), median latency **222 ms**, p95 latency **305 ms**, 62 HTTP 429s (all recovered) — required two mid-benchmark bug fixes (`DuplicateSquid`, then a pagination/attribution bug), so its wall-clock is a reconstructed estimate across two invocations. Its own `scorecard.md` explicitly describes this as "5 domains natively handled in one Run" — confirming it is not an isolated single-business test either.
- ❌ **The actual isolated single-business test** (`www.thepearlsource.com` alone, per the header's Scope note) has **no wall-clock, median, or p95 figures recorded anywhere in this project.** `outputs/` is gitignored scratch space and was overwritten by the 2026-08-13 2,000-review rerun before any timing was captured from the original 1,000-review isolated run. The previously-stated **"~179 seconds" does not match any file in the project and has been removed as unverifiable**, not carried forward.
- **Comparability limitation (corrected):** with the isolated test's timing lost, this project currently has **no** speed evidence for Lobstr tested on one business at depth — only on 5 businesses spread thin. This is the opposite of what was previously claimed here.
- 🔴 **Sub-score 1.24/1.5 — re-attributed, not recomputed.** This total is the **archived 2026-07-22 5-domain run's** own scorecard figure (median 0.42/0.5 [222 ms] + wall-clock 0.35/0.5 [reconstructed] + p95 0.27/0.3 [305 ms] + async 0.20/0.2 = 1.24), per `DATA/lobstr/reports/archive-full-copy/2026-07-22-run/scorecard.md` — arithmetically correct for that source, but not for an isolated single-business run. ⚠️ **No score has been computed anywhere against the current committed run's actual numbers (220,530 ms / 594 ms / 1,984 ms)** — 1.24/1.5 is left in place as a real, sourced figure, but it does not score the numbers now presented above it.

**Cross-provider speed summary**

| Provider | Total wall-clock | Median latency | p95 latency | Execution model | Speed sub-score |
|---|---:|---:|---:|---|---:|
| DataForSEO | 165,513 ms (committed) / ≈421,200 ms (live rerun, 2026-08-13) | 404 ms (not re-verified live) | 2,378 ms (not re-verified live) | 🔴 Async submit-then-poll (corrected from "Synchronous"), 10 calls | **1.12/1.5** (down from 1.32) |
| OpenWeb Ninja | 67,008 ms (final wave only; ~37 min across all retry waves) | 1,870 ms (superseded) | 3,684 ms (superseded) | Synchronous, sequential, 50+ calls, current run never completed | **0.23/1.5** (down from 0.98) |
| Apify | 402,134 ms (corrected from a stale 417,896 ms) | 2,022 ms | 2,874 ms | Async Actor run + polling | **1.10/1.5** (previously unscored — now filled in from `timings.json`) |
| Outscraper | 344,297 ms (corrected — a prior draft cited the archived 2026-07-21 run's 512,595 ms) | 1,094 ms | 2,500 ms | Async submit + poll | **1.10/1.5** (up from 1.07) |
| Lobstr | 220,530 ms (current, 2026-07-29) / 99,346 ms (archived 2026-07-22, reconstructed across 2 invocations) — both are the **5-domain** run, not an isolated business | 594 ms (current) / 222 ms (archived) | 1,984 ms (current) / 305 ms (archived) | Async run + sequential retrieval, 5 domains | 1.24/1.5 (archived run's own score; current run not separately scored) |

---

## 4. Scalability

> The common benchmark did not test real concurrency or 10x volume. Lobstr received one additional isolated scalability test on a single business, verified at **2,000 reviews** (2026-08-13); an earlier 1,000-review version of this same isolated test is referenced elsewhere in this document but has no surviving raw evidence (see the Lobstr subsection below). No other provider was tested past 200 reviews per business.

### Apify

- **Max reviews tested from one business:** 200 (`maxReviewsPerCompany` set to 200; documentation claims `maxReviewsPerCompany=0` means "unlimited," **not tested** here).
- **Concurrency tested:** explicitly `desired concurrency 1` (single-threaded crawl) per the run's own status message — a real, documented value, not merely inferred from timing.
- **Rate-limit events:** 0. HTTP 429 events: 0.
- **10x volume test performed:** No — scorecard states "Degradation at 10x volume: 0.00 — Not tested."
- **Scorecard sub-score:** 0.52/1.2.

### OpenWeb Ninja

- **Max reviews tested from one business:** 0 in the current run (target was 200; account could not clear rate limiting to return any reviews at all). A prior, superseded pass had reached 200 (10 pages × 20/page) before this account's current rate-limit state.
- **Concurrency tested:** none — requests were sequential.
- 🔴 **Rate-limit events: 75 confirmed HTTP 429s, none recovered** — this is now direct, current negative evidence of a real scalability failure at low volume (the account couldn't clear rate limiting even at the *standard* 1,000-review test, let alone 10x). Superseded finding: an earlier pass logged 0 real rate-limit events (its one error was an unrelated HTTP 500).
- **10x volume test performed:** No, and moot — the account cannot currently complete the 1x baseline test.
- **Scorecard sub-score:** 0.15/1.2 — down from 0.50. Breakdown: rate limits/concurrency 0.05/0.5 (this run is now direct negative evidence, not merely undocumented) + degradation at 10x 0.00/0.4 (never got past 1x) + volume caps 0.10/0.3 (the practical usable volume is evidently much lower than the published tier suggests).

### DataForSEO

- **Max reviews tested from one business: 200 — a confirmed hard ceiling**, not merely untested further (`pagination_confirmed: false`, no pagination parameters available). Official documentation confirms no `page`/`offset`/`skip`/`cursor` parameter exists for this endpoint — 200 is the documented, current ceiling with no pagination alternative.
- **Concurrency tested:** none (5 sequential tasks).
- **Rate-limit events:** 0. Documented limits (30 POST/min, 100 tasks/POST, 20 `tasks_ready`/min) were never approached (5 POST calls, ~6 `tasks_ready` polls this run).
- **10x volume test performed:** No — "no attempt at 50 tasks concurrently."
- **Scorecard sub-score:** 0.60/1.2 — the only provider with a **proven negative result** (confirmed ceiling) rather than simply an untested gap.

### Outscraper

- **Max reviews tested from one business:** 200 (never requested more; every domain hit target on page 1).
- **Concurrency tested:** none.
- **Rate-limit events:** 0. Rate limits are **"not documented at all"** per the provider's own scorecard notes — worse than DataForSEO, which at least publishes explicit numbers.
- **10x volume test performed:** No — "Degradation at 10x volume" scored 0.00/0.4 explicitly for "not tested this run"; single-domain >200-review capability is listed in the provider's own documentation status table as "Pending live pagination test." A documented 5-page strategy (`skip=0,200,400,600,800`) for a 1,000-review single-business test exists in documentation but was never executed.
- **Scorecard sub-score:** 0.30/1.2 — the **lowest Scalability sub-score of the five**.

### Lobstr

- **Max reviews tested from one business: 2,000**, verified (updated 2026-08-13; previously stated as 1,000 — see flag below). A follow-up live test on 2026-08-13, on its own dedicated squid (`a195876effb8446fa4c0171e644595b8`, distinct from the 5-domain benchmark's squid `8d9e0b80d6d2481283c138104caf022d`), targeted 2,000 and returned **2,000/2,000 unique valid reviews, 0 duplicates**, credits consumed measured at exactly 2,000. Run ID `b595fc1fbb3a42aeb77592a12294844c`, wall-clock 334,375 ms, pagination stopped because the requested target was reached (`max_pages_cap`), not a platform-imposed ceiling — no cap was encountered at 2,000. All figures confirmed directly in `outputs/lobstr-single-domain-test/summary.json`.
- 🔴 **Corrected — the "original 1,000-review test" claims below were misattributed, same error as Sections 1 and 3.** An isolated 1,000-review test on `www.thepearlsource.com` is referenced in this document's header (Scope note), but **no raw file for it survives** — `outputs/` is gitignored and was overwritten by the 2026-08-13 2,000-review rerun before its numbers were captured elsewhere. The "7 confirmed HTTP 429 events" previously attributed to it actually come from `DATA/lobstr/analysis/error-log.json`, which belongs to the **5-domain shared benchmark** (confirmed via `tasks.json`'s 5 domain-task mappings), not an isolated single-business run. That 1,000-review isolated test's specific numbers (reviews returned, duplicates, error count) **cannot currently be independently verified from any file in this project.**
- **Concurrency tested:** not deliberately tested; result-page retrieval was sequential in the verified 2,000-review test.
- **10x volume test performed:** Partially, based on the verified 2,000-review test — 2,000 reviews from one business is 10x the standard 200-review-per-business baseline used for the 5-domain comparison, though still not a 10x-total-volume or concurrent-run test.
- ⚠️ **Scoring note — "1.20/1.2" not independently reproducible.** No file in this project computes a 1.20/1.2 Scalability score for Lobstr. The only sourced Scalability figure for Lobstr is the archived 2026-07-22 5-domain run's own scorecard total, **0.60/1.2** (0.40 rate-limits/concurrency + 0.00 degradation-at-10x + 0.20 volume caps) — which matches this document's "standard basis" figure exactly. **Scorecard sub-score: 0.60/1.2, sourced and verified, on the standard 200-per-business basis; 1.20/1.2 "with bulk-test credited" is left unchanged but flagged as unverified** — it does not appear in any scorecard, and with the original 1,000-review test's evidence now confirmed lost, there is no computed score anywhere crediting the 2,000-review result specifically.

**Cross-provider scalability summary**

| Provider | >200/business tested? | Concurrency tested? | Real rate-limit evidence? | 10x volume tested? | Scalability sub-score |
|---|---|---|---|---|---:|
| DataForSEO | No — confirmed hard ceiling (negative result) | No | No (0 events) | No | 0.60/1.2 |
| Outscraper | No — untested | No | No (0 events; limits wholly undocumented) | No | 0.30/1.2 |
| OpenWeb Ninja | No — the account cannot currently complete even the 200/business standard test (see below) | No | **Yes — 75 real 429s, none recovered** | No | **0.15/1.2** (down from 0.50 — this is now direct negative evidence of a real scalability failure, not merely an untested gap) |
| Apify | No — untested (`0`="unlimited" claim unverified) | Documented `concurrency 1` | No (0 events) | No | 0.52/1.2 |
| Lobstr | **Yes — 2,000/2,000 from one business, verified** (2026-08-13; the previously-claimed 1,000-review version has no surviving evidence) | No | 0 events at 2,000 (the "7 real 429s" previously shown here belong to the unrelated 5-domain run, not this test) | Partially (2,000 = 10x the 200/business baseline) | **0.60/1.2, sourced (standard basis) / 1.20/1.2 "with bulk credited" — unverified, no source file** |

---

## 5. Developer Experience

> Only evidence-backed findings are included; adjectives like "easy" or "developer-friendly" are not treated as facts unless a recorded test or log entry supports them.

### Apify

- **Authentication setup:** token-based; worked on the first live attempt.
- **Time to first successful request:** not isolated as a standalone metric (run/poll timing exists, but not framed this way).
- **SDK/client used:** none — raw HTTP, with real retry/error classification logic (401/403/402 → auth/billing error; 400/404 → invalid-request error; 429/500–504 → retryable).
- **Documentation issues:** docs matched live behavior on 4 of 5 domains; the SHEIN discrepancy (Section 1) is a real, unexplained gap between documented "unlimited" capability language and observed zero-result output.
- **Actual implementation problems:** the SHEIN silent zero-result outcome is the standout problem; investigated and inconclusive.
- **Error-message quality:** untested for real failures (none occurred); the client's own error-classification logic was never exercised against a live error.
- **Support interaction:** ❌ Not tested — no support ticket filed.
- **Scorecard sub-score:** 0.76/1.0 — real retry/error-classification code credited, but error-message-clarity sub-criterion penalized heavily because no signal was ever surfaced for the SHEIN failure.

### OpenWeb Ninja

- **Authentication setup:** API key-based; no friction logged.
- **Time to first successful request:** **0 — no successful request occurred in the current run** (superseded finding: previously "worked, no friction logged").
- **SDK/client used:** none exercised — official SDK examples exist for Shell/Ruby/Node.js/PHP/Python (the broadest official language coverage of any tool tested), unaffected by this run's outcome.
- **Documentation-access limitation, not a doc-vs-behavior gap:** unaffected by this run's outcome — the docs require a real browser to render (a plain HTTP fetch only returns the page shell). Per the project's own `elimination-assessment.md` (E3), this is explicitly recorded as "a minor DX friction point, not a documentation-completeness failure" — every endpoint/param/field matched live behavior exactly once rendered, so there is no actual mismatch between documented and observed behavior.
- **Actual implementation problems — current state:** sustained rate-limiting (75× HTTP 429) that the account's own retry/backoff logic could not clear, across ~37 minutes and multiple waves. Superseded finding: an earlier pass logged only one HTTP 500 with a clean recovery.
- **A genuine positive, still holds:** a real, disclosed dry-run/quota check mechanism exists and was previously demonstrated before any billed calls — a concrete operational-diligence signal, though it did not prevent the current rate-limit exhaustion.
- **Integration complexity:** unaffected by this run's outcome — the `company-reviews` endpoint accepts only `company_domain`.
- **Support interaction:** ❌ Not tested.
- **Scorecard sub-score:** 0.62/1.0 — down from 0.89. Breakdown: time-to-first-request 0.00/0.3 (down from 0.27 — zero successful requests) + docs quality 0.28/0.3 (unchanged, unaffected by outcome) + SDKs 0.18/0.2 (unchanged) + error message clarity 0.16/0.2 (unchanged — the 429 bodies remained clear and structured even in failure).

### DataForSEO

- **Authentication setup:** API key-based; worked on first request, no setup friction logged.
- **Time to first successful request:** first `task_post` round trip measured at 2,378 ms.
- **SDK/client used:** none — raw HTTP only; official docs provide curl examples only, no SDK tested.
- **Documentation issues:** none logged; every documented parameter/endpoint matched observed live behavior exactly.
- **Actual implementation problems / debugging required:** none logged.
- **Error-message quality:** untested — no real error occurred.
- **Support interaction:** ❌ Not tested.
- **Note on script provenance:** see Section 1 — the primary source project had no benchmark script for this provider at all, meaning the raw logs there could not be traced to producing code. Its provenance relative to the raw evidence should be confirmed before treating it as the verified original.
- **Scorecard sub-score:** 0.73/1.0 — docs-quality and time-to-first-request credited; SDK/support sub-criteria scored near-zero because untested.

### Outscraper

- **Authentication setup:** API key-based; worked on first real request, "no parser fixes needed" per scorecard notes.
- **Time to first successful request:** ❌ not explicitly logged as a standalone metric.
- **SDK/client used:** none — raw HTTP only; curl examples only in docs.
- **Documentation issues:** none negative — documentation is credited with **proactively flagging real gotchas**: `skip` must be a multiple of 20, empty-result billing behavior, and a ~4-hour result-expiration window. This is more explicit gotcha-flagging than DataForSEO's docs provided.
- **Actual implementation problems:** none logged; the parser's response-shape assumption was verified correct against the very first real response with no fix needed.
- **Support interaction:** ❌ Not tested.
- **Scorecard sub-score:** 0.81/1.0.

### Lobstr

- **Authentication setup:** token-based; worked immediately for every call.
- **Time to first successful request:** ❌ not isolated as a standalone metric — and this provider needed **two fixes at two different stages** before a complete, correctly-attributed dataset was produced (see below): one blocking configuration error in an earlier, separate attempt (before any Run existed), and one silent data-processing bug found only after a Run had already reported success on Lobstr's side. A real friction point the other four providers did not have.
- **SDK/client used:** none — raw HTTP.
- **Documentation issues — two concrete, root-caused findings:**
  1. The documented maximum results-page `limit` of 100 was **silently served as `limit: 10`** in the live response, regardless of what was requested — a real documentation-vs-behavior gap.
  2. Documentation does not disclose that result items carry no `task` field at all, requiring a fallback to `company_page_url` for domain attribution.
- **Actual implementation problems:** an `HTTP 400 DuplicateSquid` error occurred from unconditionally sending a `name` field in a squid-configuration PATCH request, colliding with a pre-existing squid on the account — a bug in the benchmark's own orchestration code, not Lobstr's platform, discovered in an earlier, separate attempt before any task or Run existed. Separately, after a Run had already reported success (1,000/1,000 per Lobstr's own count), the benchmark's local aggregation showed only 200 valid records — a silent shortfall, not a Lobstr-reported error — traced to the `/v1/results` endpoint silently capping page size at 10 regardless of the requested `limit=100`, combined with result items carrying no `task` field for attribution. Fixed by re-reading the same Run (zero new Runs) after raising the page-count cap and switching attribution to `company_page_url`.
- **Debugging required:** yes — two real bugs found and fixed across this effort (one pre-run blocker, one post-run-success silent data bug), both fully documented with before/after evidence.
- **Error-message quality:** both the `DuplicateSquid` error and the `Throttled` 429 errors returned clear, specific, machine-readable bodies.
- **Support interaction:** ❌ Not tested.
- 🔴 **Corrected: 0.63/1.0, not 0.45/1.0** — no file in this project contains "0.45"; `DATA/lobstr/reports/archive-full-copy/2026-07-22-run/scorecard.md` states this run's Developer Experience as 0.63/1.0, which also matches the Final Summary table's Dev Exp figure and is required for its 7.88 total to sum correctly. Documentation-vs-live-behavior gaps and the additional integration work were the main deductions, but not to the degree the stale 0.45 implied — this is no longer the lowest score of the five (see below).

**Cross-provider developer-experience summary**

| Provider | SDK tested? | Real doc-vs-behavior gap found? | Real bug requiring a fix? | Support tested? | Dev Experience sub-score |
|---|---|---|---|---|---:|
| DataForSEO | No | None found | None | No | 0.73/1.0 |
| Outscraper | No | None (docs proactively flagged real gotchas) | None | No | 0.81/1.0 |
| OpenWeb Ninja | No | No — docs require a rendered browser to view, but content matched live behavior exactly (access limitation, not a doc-vs-behavior gap) | **Yes — sustained rate-limiting, unrecovered (current)**, was a transient recovered 500 (superseded) | No | **0.62/1.0** (down from 0.89, lowest) |
| Apify | No | Yes — SHEIN "unlimited" claim vs. observed 0 results | Unresolved silent SHEIN failure | No | 0.76/1.0 |
| Lobstr | No | Yes — `/v1/results` `limit` silently capped at 10; no `task` field on result items | Yes — 2 (DuplicateSquid config bug; pagination/attribution bug) | No | 0.63/1.0 (corrected from 0.45) |

---

## 6. Data Quality & Completeness

> **Ground-truth status for all five providers: validated for exactly 1 of 5 businesses (`www.thepearlsource.com`), a manually-curated 20-row sample.** SHEIN, Temu, AliExpress, and Halara have **no ground truth at all**. Every field-coverage/accuracy figure below is scoped to `www.thepearlsource.com` only and must not be extrapolated to the other four domains.
>
> ⚠️ **Process note:** per the `/knowledge` command, this Data pillar is normally owned by `/datacompare` (run against raw exports in `data/`). That command was not run for this project — the figures below predate it, inherited from the original two-source synthesis. They are not sourced from a `/datacompare` artifact. Re-running `/datacompare` against `data/` before finalizing the article would let these numbers be recomputed/confirmed on the canonical pipeline rather than carried forward as-is.

### Apify

🔴 **This figure is volatile across runs, not a stable characteristic — read the whole entry before citing a number.** An earlier evidence pass (when `www.shein.com` was the run's silent-failure business, and `www.thepearlsource.com` — the only domain with ground truth — succeeded) recorded: 20/20 rows matched (100%) via `authorName`, field coverage 92.3% (12/13, the highest of any tool tested), `company_replied` mismatches on 4/20 rows (same freshness explanation and same 4 authors as OpenWeb Ninja/Lobstr), `owner_reply_date` 0% literal match (a relative-string-vs-absolute-timestamp format artifact, not a data error — the underlying `owner_reply` text matched exactly on all 14 comparable rows), 2 duplicates, 0 missing-field occurrences across 800 returned items.
- **The committed evidence file as of 2026-07-29** (`DATA/apify/analysis/ground-truth-match.json`) reflects a *different* run, where `www.thepearlsource.com` itself was the silent-failure business: **0/20 ground-truth rows matched, `api_items_available: 0`, `field_accuracy: []`** — every row's `reason` is `"no_api_item_with_matching_author_found"`. There is no field-coverage or accuracy figure computable from this evidence.
- **A live rerun on 2026-08-13 moved the failure again**, this time to `www.thehalara.com` — meaning `www.thepearlsource.com` most likely returned data in that attempt too, but this was not re-analyzed against ground truth this session.
- **The actual finding is the instability itself, not either number:** across three live attempts, the one domain with ground truth has swung between full data and zero data unpredictably, because a *different* business fails silently each run. Neither "92.3%" nor "0%" should be read as "Apify's accuracy" — the honest statement is that Apify's ground-truth comparability for this business is not currently reproducible run-to-run.
- **Missing fields (from the evidence-available run):** `review_type` (invited/organic status) has no officially-documented equivalent — a heuristic mapping via `verificationLevel`/`source` was empirically 100% consistent on 19 comparable rows in that pass, but is not a confirmed 1:1 field mapping and cannot be re-checked against the current committed evidence.
- **Duplicates (committed evidence, 2026-07-29 run):** 0 across the 800 returned items — the 2/20 duplicate figure from the earlier evidence-available pass does not apply to this run.
- **Schema consistency (committed evidence):** 0 missing-field occurrences across the 800 items that were returned, per `domain-summary.json`'s `missing_field_counts: {}`.
- 🔴 **Scorecard sub-score: 0.60/2.0 — for the current 2026-07-29 run, not "previously unscored."** The archived 2026-07-22 run (`DATA/apify/reports/archive-full-copy/2026-07-22-run/scorecard.md`) was already explicitly scored at **1.94/2.0** (field coverage 0.74 + accuracy 0.50 + schema consistency 0.40 + freshness 0.30) — that score is real and sourced, but it applies to the superseded run where `thepearlsource` succeeded. The current committed 2026-07-29 evidence is a *different* run where `thepearlsource` returned zero items, making ground-truth comparison inapplicable; 0.60/2.0 reflects only this run: field coverage 0.00/0.8 (no ground-truth data available) + accuracy 0.00/0.5 (unmeasurable) + schema consistency 0.40/0.4 (0 missing fields across the 800 successful items) + freshness 0.20/0.3 (the original cross-confirmation partner, OpenWeb Ninja, currently has zero data of its own to cross-confirm against).

### OpenWeb Ninja

🔴 **Superseded finding, kept for provenance:** an earlier evidence pass recorded a 20/20 (100%) ground-truth match via `consumer_name`, 76.9–84.6% field coverage, `company_replied` mismatches on the same 4 authors flagged by Apify/Lobstr, 0 duplicates, 0 missing-field occurrences across 1,000 items.

**Current, verified state:** the account's most recent run returned **0 items across all 5 domains** (Section 1) — there is no data to compute a ground-truth match, field coverage, or schema-consistency figure against at all.

- **Scorecard sub-score:** 0.00/2.0 — down from 1.82. All four sub-criteria (field coverage, accuracy, schema consistency, freshness) score 0 for the same reason: no data was returned this run.

### DataForSEO

- **Ground-truth match rate:** 20/20 (100%), via author name.
- **Field coverage: 84.6% (11/13).**
- **Confirmed mismatches:** 0 on every field both sources actually captured — a clean result, but on a narrower schema than some competitors.
- **Missing fields:** `review_type` (invited-status) and `useful_count` (helpful-vote count) — **neither exists anywhere** in the documented or observed DataForSEO schema.
- **Duplicates:** 1, on `temu.com`, matched on `url` key type (the same duplicate counted in Section 1's reliability figure).
- **Schema consistency:** 0 missing-field occurrences across all 1,000 raw items.
- **Scorecard sub-score:** 1.88/2.0.

### Outscraper

- **Ground-truth match rate:** 20/20 (100%).
- **Field coverage: 92.3% (12/13)** — better than DataForSEO's 84.6% specifically because Outscraper returns `review_likes` as a working equivalent to `useful_count`, which DataForSEO lacks entirely. **This field matched 100%, including the one non-zero ground-truth value (MR KEARNEY: 1).**
- 🔴 **Correction: 6 field-level mismatches, not 0.** `DATA/outscraper/analysis/ground-truth-match.json` shows `author_reviews_count`: 18/20 match (2 mismatches) and `company_replied`: 16/20 match (4 mismatches) — a prior draft of this document claimed "the only provider with zero field-level mismatches," which does not match this evidence file. Both mismatched fields follow the **same capture-time-gap pattern already documented for Lobstr**: the ground-truth sample was collected 2026-07-21, this run's evidence is dated 2026-07-29 (an 8-day gap), and both fields are time-varying (authors post more reviews elsewhere over time; businesses reply to reviews after the fact). These are genuine value differences explained by real-world drift between capture dates, not extraction errors — the same reasoning already applied to Lobstr, Apify, and OpenWeb Ninja's `company_replied` mismatches elsewhere in this document.
- **Missing fields:** `review_type` (invited/organic) — no equivalent anywhere in the documented or observed schema.
- **Duplicates:** 0.
- **Schema consistency:** 0 missing-field occurrences across all 1,000 items.
- **Scorecard sub-score:** 1.94/2.0 — unchanged numerically (the 6 mismatches are attributed to capture-timing, not accuracy failure, consistent with how the same pattern is scored for Lobstr), but **no longer "the only provider with zero mismatches"** — see the corrected cross-provider table below.

### Lobstr

- **Ground-truth match rate:** 20/20 (100%).
- **Field coverage: 92.3% (12/13)** on the 13-field ground-truth checklist — internally consistent for this specific calculation.
- 🔴 **Confirmed mismatches: 6 total, not 4 — matches Outscraper's pattern exactly.** `DATA/lobstr/analysis/ground-truth-match.json` shows `author_reviews_count`: 18/20 match (2 mismatches) in addition to the `company_replied` mismatch already noted here — this field was previously omitted from this bullet. `company_replied` 4/20 — same 4 authors (Linda B, Human Sun, Sharon R., MW) as Apify and OpenWeb Ninja, now cross-confirmed by **three independent tools**. Both mismatched fields follow the same capture-time-gap pattern documented for Outscraper (ground truth collected 2026-07-21, this run dated 2026-07-29, an 8-day gap) — genuine value drift, not extraction errors. `owner_reply_date` 0/14 literal match — same relative-string-vs-absolute-timestamp format artifact as the other providers; `owner_reply` text itself matched exactly on all 14 rows.
- **Missing fields:** none of the 13 ground-truth checklist fields are absent from Lobstr's schema.
- **Duplicates:** 0.
- **Business attribution required a code fix:** result items have no `task` field; attribution uses `company_page_url` matched against the domain list (Section 5).
- **Raw result-item field count: 40 fields**, directly counted: `id, object, run, author_id, author_image, author_name, business_unit_id, company_category, company_name, company_page_url, consumer_country_code, consumer_reviews_on_domain, date_published, experience_date, functions, is_author_verified, is_review_verified, likes, native_id, number_of_reviews, owner_reply, owner_reply_date, owner_reply_updated_date, page_number, rating_value, report, review_body, review_headline, review_language, review_link, review_sentiment, review_source, review_url, review_verification_source, reviews_count, scraping_time, stars, trust_score, updated_date, verification_level`. This is now cross-verified: both audited source projects independently counted the same raw file and arrived at 40. Two narrative reports in the primary source state 37 and 39 respectively — neither figure appears in any raw evidence file in either project, so 40 is treated as the correct, resolved count.
- **Separately unresolved:** the secondary source also claims each of the 5 providers' ground-truth checklists actually differ in size (11/11/11/12/13 fields, not a uniform 13-field checklist for all five) — this contradicts the consistent 13-field checklist directly observed in the primary source's own field-coverage files (DataForSEO 11/13, Outscraper 12/13, OpenWeb Ninja 10/13 strict, Apify 12/13, Lobstr 12/13). This narrower disagreement was not re-verified during this pass and is recorded as open, not adopted.
- 🔴 **Corrected sub-score: 1.94/2.0, not 1.70/2.0** — the 1.70 figure did not match the dedicated scorecard's own sub-criteria: field coverage 0.74/0.8 (12/13) + accuracy 0.50/0.5 (0 unexplained mismatches) + schema consistency 0.40/0.4 (0 missing fields/1,000 items) + freshness 0.30/0.3 (cross-confirmed) = **1.94/2.0**.

**Cross-provider data-quality summary (www.thepearlsource.com only — no other domain has ground truth)**

| Provider | Ground-truth match | Field coverage | Confirmed mismatches | Duplicates | Missing fields (confirmed absent) | Data Quality sub-score |
|---|---|---:|---|---:|---|---:|
| Apify | **0/20 (current, committed 2026-07-29 evidence)** — volatile, see full entry above | **Not computable this run** (was 92.3% in a superseded pass) | Not computable | 0 (current run) | Not computable | **0.60/2.0** (previously unscored) |
| OpenWeb Ninja | **0/20 (current)** — was 20/20 in a superseded pass | **Not computable this run** (was 76.9–84.6%) | Not computable | 0 (current run) | Not computable | **0.00/2.0** (down from 1.82) |
| DataForSEO | 20/20 | 84.6% (11/13) | 0 | 1 | `review_type`, `useful_count` | 1.88/2.0 |
| Outscraper | 20/20 | 92.3% (12/13) | `author_reviews_count` 2/20 + `company_replied` 4/20 (both freshness, not error — corrected from a stale "0 mismatches" claim) | 0 | `review_type` | **1.94/2.0** (tied highest) |
| Lobstr | 20/20 | 92.3% (12/13) | `author_reviews_count` 2/20 + `company_replied` 4/20 (both freshness, not error) | 0 | none of the 13 checklist fields | **1.94/2.0** (corrected from 1.70 — tied highest, not lowest) |

---

## 7. Input Flexibility & Coverage

> Extracted from each provider's own documented input parameters/endpoints in `api_docs_mcps.txt` (verifiable — not benchmark-run behavior). No geo/country filter parameter exists for any of the 5 providers as an *input* — `country` only ever appears as an output (reviewer's country) field.

### Apify
- **Accepted input:** `companyUrls` — domains or full Trustpilot profile URLs, as an array (`api_docs_mcps.txt:161,188`).
- **Endpoint breadth:** 3 — Actor Run, Run Status, Get Dataset Items (`:126,397,457`).
- **Enrichment:** `includeCompanyInfo` flag returns company name/Trust Score/stars/total reviews/categories inline — no separate enrichment endpoint (`:356,509-542`).

### DataForSEO
- **Accepted input:** `domain` only, a single string (`:1514`).
- **Endpoint breadth:** 3 — `task_post`, `tasks_ready`, `task_get` (`:1486,1686,1692`).
- **Enrichment:** none found.

### Outscraper
- **Accepted input:** `query` — domain or Trustpilot profile URL, as an array, batchable up to 1,000 (`:4622-4645`).
- **Endpoint breadth:** 2 — main endpoint + results/polling (`:4604,4907`). Richest query-parameter set of the five: `limit`, `skip`, `languages`, `sort`, `cutoff`, `fields`.
- **Enrichment:** none found.

### OpenWeb Ninja
- **Accepted input:** `query` — company name or exact domain, search-style (`:3468-3491`).
- **Endpoint breadth:** 2 — Company Search (confirmed) + Company Reviews (`:3468,3495` — the reviews endpoint is itself flagged "Pending live documentation verification" at `:3514`, so this count is not fully confirmed).
- **Enrichment:** none found.

### Lobstr
- **Accepted input:** full Trustpilot review URL (`https://www.trustpilot.com/review/{domain}`) (`:2382-2396`).
- **Endpoint breadth:** 5 — Create Squid, Add Tasks, Start Run, Run Status, Get Results (`:2234,2378,2459,2481,2512`) — the most granular/multi-step workflow of the five.
- **Enrichment:** none found.

### Scoring

| Provider | Accepted input types (/0.3) | Endpoint breadth (/0.3) | Enrichment (/0.2) | **Total (/0.8)** |
|---|---:|---:|---:|---:|
| Apify | 0.28 — domain or full profile URL, array, multi-company in one call | 0.12 — single-purpose Actor (reviews only) | 0.14 — company info embedded inline | **0.54** |
| DataForSEO | 0.12 — single domain string, no array | 0.12 — one capability (reviews) | 0.08 — a separate search endpoint exists, unused | **0.32** (corrected from 0.25) |
| Outscraper | 0.20 — domain or URL (not array-batched in this scoring) | 0.18 — narrow endpoints, but documented 1,000-query batching adds real breadth | 0.05 — no enrichment endpoint found | **0.43** (corrected from 0.45) |
| OpenWeb Ninja | 0.15 — company name or exact domain | 0.27 — broadest of the five, 9 distinct endpoints | 0.18 — genuine enrichment (consumer-details, category search) | **0.60** |
| Lobstr | 0.18 — full Trustpilot review URL | 0.12 — task/run/results workflow | 0.14 — company fields embedded per review | **0.44** (corrected from 0.35) |

> 🔴 **Note on this correction:** the previous Apify/Outscraper/OpenWeb Ninja per-sub-criterion breakdown above has been reconciled against each provider's dedicated scorecard file (`DATA/<provider>/reports/`), which is the more granular, authoritative source for these three sub-criteria. Only DataForSEO, Outscraper, and Lobstr's totals actually changed (0.25→0.32, 0.45→0.43, 0.35→0.44); Apify and OpenWeb Ninja's totals were already correct, though their sub-criteria are restated here with the scorecard's exact wording for consistency.

---

## Final Summary — which platform looks strongest

**Caveat before any number below: the rubric these scores come from (`criteria.md`) is owned by Lobstr's own content team, and Lobstr is one of the five providers being scored.** Nothing found during this audit shows a finding being suppressed or reframed to favor Lobstr, but that ownership fact should travel with any ranking below, not be dropped from it — and the margin below is thin enough that this disclosure genuinely matters. Apify's Speed and Data Quality sub-scores, previously left unscored ("not stated in the source material"), have now been filled in from evidence that already existed in `DATA/apify/analysis/` — Apify's total is out of the full 10.0 for the first time in this document, not the reduced 6.5 max used previously.

**A full audit pass (2026-08-13) found and corrected several errors in this section: an arithmetic mis-total, two unjustified score inflations, two unjustified score deflations, three Input-Flexibility transcription slips, and one metric-mapping error. Every correction is shown inline below. Nothing in this correction pass changed `criteria.md`'s weights or `methodology.md` — the rubric itself was sound throughout; every error was in this document's application of it.**

**7-category totals (Sections 1–7), current evidence:**

| Provider | Reliability (§1) | Cost (§2) | Speed (§3) | Scalability (§4) | Dev Exp (§5) | Data Quality (§6) | Input Flex (§7) | **Total** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Lobstr | 1.95 ⚠️ | 1.08 | 1.24 | 0.60 (standard) | 0.63 | 1.94 | 0.44 | **7.88** (standard) / **8.48 ⚠️** (+0.60 if the 2,000-review bulk test is credited toward Scalability — this +0.60 rests on an unsourced 1.20/1.2 figure, see §4) |
| DataForSEO | 1.90 | 1.10 | 1.12 | 0.60 | 0.73 | 1.88 | 0.32 | **7.65** |
| Outscraper | 1.92 | 0.85 | 1.10 | 0.30 | 0.81 | 1.94 | 0.43 | **7.35** (corrected from 7.32 — Speed was computed against an archived run's figures, see §3) |
| Apify | 1.38 | 1.20 | 1.10 | 0.52 | 0.76 | 0.60 | 0.54 | **6.10** |
| OpenWeb Ninja | 0.10 | 0.35 | 0.23 | 0.15 | 0.62 | 0.00 | 0.60 | **2.05** |

⚠️ **Lobstr's Reliability figure (1.95/2.0) is not independently reproducible.** No file in this project records a sub-criteria breakdown for the current (7×429, clean) Lobstr run. The only itemized breakdown that exists anywhere is a different, archived run's (62×429, two bug fixes) 1.97/2.0. Reconstructing from `criteria.md` §4's weights and the current run's evidence lands in a 1.97–2.00 range, not 1.95. Left unchanged, flagged only — see the dedicated audit above for the full attempted calculation.

**Final ranking:** **Lobstr is #1 at 7.88/10 (standard test basis, fully sourced) or 8.48/10 (if its 2,000-review bulk test is credited toward Scalability — ⚠️ this alternate total relies on an unsourced 1.20/1.2 Scalability figure, see §4), followed by DataForSEO at 7.65/10 (a 0.23–0.83-point margin), Outscraper at 7.35/10, Apify at 6.10/10, and OpenWeb Ninja at 2.05/10.**

This is a materially different ranking from an earlier draft of this document, which had Lobstr at 7.90 and DataForSEO at 7.78 (a 0.12-point margin) via a different, uncorrected mix of sub-scores, and had Apify at 4.46/6.5 and OpenWeb Ninja at 7.37/10 using stale/superseded evidence. The corrections, in order of size: OpenWeb Ninja's entire scorecard was still describing a clean run that has since been superseded by a confirmed total failure (7.37 → 2.05, a 5.32-point drop); Apify's Speed and Data Quality sub-scores were filled in from evidence that already existed but was never scored, moving it from 4.46/6.5 to 6.10/10 (a 1.64-point increase, now on a larger, complete max); DataForSEO's Speed sub-score dropped 0.20 points after a live rerun showed materially slower queue processing today, partially offset by a +0.07 Input-Flexibility transcription fix, for a net −0.13 (7.78 → 7.65); Lobstr and Outscraper's Data-Quality/Input-Flexibility sub-scores were reconciled against their dedicated scorecard files: Lobstr's Input Flexibility moved 0.35 → 0.44 (+0.09) and Data Quality moved 1.70 → 1.94 (+0.24), both independently sourced — 🔴 a prior version of this note claimed a "Lobstr net −0.02," which doesn't reconcile with these two sourced deltas (they sum to +0.33); no historical Reliability baseline could be located to complete that reconciliation, so no net figure is stated for Lobstr here. Outscraper's Input-Flexibility fix was −0.02 (7.34 → 7.32). A further evidence-vs-document check found Outscraper's Speed sub-score had been computed against the archived 2026-07-21 run's timings instead of the current committed 2026-07-29 run — correcting it added back +0.03 (7.32 → 7.35, a net +0.01 from the original 7.34 across both fixes; see §3 for the corrected timing figures).

**By category, the strongest performer was:**
- **Reliability:** Lobstr (1.95/2.0 ⚠️ unreproducible, see flag above) — OpenWeb Ninja's current state (0.10/2.0) removes it from contention entirely; among the remaining four, Lobstr's 100%-completion, cleanly-recovered rate-limit evidence edges DataForSEO's clean-but-untested run.
- **Cost:** two separate claims, unchanged in substance: DataForSEO has the cheapest *absolute measured price* ($0.03754/1,000, from a real billing field); Apify has the highest *Cost sub-score* (1.20/1.5), credited for also being a measured billing figure despite costing more per review. Lobstr's rate is corrected to $0.50/1,000 (official documentation), not the $1/1,000 figure used elsewhere in an earlier draft of this document.
- **Speed:** DataForSEO (1.12/1.5, down from 1.32 after a live rerun showed slower queue processing today) — still the fastest of the five on the batch-wall-clock metric, but no longer at its original best-case pace.
- **Scalability:** Lobstr — 0.60/1.2 on the same standard test every provider received; 1.20/1.2 (the rubric maximum) if its live-verified 2,000-review single-business result is credited. Reported both ways, never blended into one number (see §4).
- **Developer Experience:** DataForSEO (0.73/1.0) and Apify (0.76/1.0) lead now that OpenWeb Ninja's current-state score (0.62/1.0) reflects zero successful requests this run.
- **Data Quality:** Outscraper and Lobstr are now **tied** at 1.94/2.0 — both show the same 6 capture-timing-driven mismatches (`author_reviews_count`, `company_replied`), not the "Outscraper alone is spotless" framing an earlier draft used; Lobstr's figure was separately corrected from a transcription error that had it at 1.70. Apify's is currently unmeasurable (0.60/2.0, no ground-truth data in the committed run) and OpenWeb Ninja's is 0.00/2.0 (no data returned at all).
- **Input Flexibility & Coverage:** OpenWeb Ninja (0.60/0.8) — broadest endpoint breadth (9 distinct endpoints) and genuine enrichment options, unaffected by its current reliability problems since this criterion measures documented capability, not this run's outcome.

**Strengths & weaknesses, by provider:**

### 1. Lobstr — overall winner at 7.88/10 (standard) / 8.48/10 ⚠️ (with its bulk-volume test credited — this alternate total rests on an unsourced Scalability figure, see §4)

**Strong:**
- Overall winner at 7.88/10, ahead of DataForSEO's 7.65/10 — a 0.23-point margin on the standard test basis (0.83 points if the 2,000-review bulk test is credited toward Scalability).
- The only provider with real, naturally-occurring rate-limit evidence in the benchmark's isolated single-business test — all 7 confirmed HTTP 429s recovered cleanly on the immediate retry.
- Live-verified beyond 200 reviews from a single business — **2,000/2,000 unique reviews, 0 duplicates, credits confirmed 1:1 (2,000 credits) as of 2026-08-13** (an earlier 1,000-review version of this test is referenced elsewhere in this document but has no surviving raw evidence — only the 2,000-review figure is confirmed). No cap was encountered at 2,000. This is reported separately from the standard Scalability score (0.60/1.2), which the rubric caps at 1.20/1.2 either way — see §4.
- Exact 1:1 credit-to-review ratio holding at both 1,000 and 2,000 reviews — zero wasted spend.
- 100% ground-truth match, 0 duplicates, and now **tied with Outscraper for the highest Data Quality sub-score (1.94/2.0)** — a transcription error in an earlier draft of this document had this at 1.70.

**Weak:**
- Developer Experience at 0.63/1.0 — second-lowest of the five (OpenWeb Ninja's current 0.62/1.0 is now the lowest) — driven by two real integration issues: a squid-naming collision (a bug in the benchmark's own script, not Lobstr's platform) and two genuine Lobstr documentation-vs-behavior gaps (a documented page `limit` of 100 silently served as 10; result items missing an undocumented `task` field).
- Real dollar cost is $0.50/1,000 reviews (corrected from an erroneous $1/1,000 cited in an earlier draft — see §2) — still pricier than DataForSEO's measured $0.03754/1,000, though the gap is half what was previously stated.
- Lobstr owns the scoring rubric it's being measured against — a disclosed conflict of interest that should temper confidence in the ranking. The margin over #2 (0.23–0.83 points) is a real margin, not the near-tie an earlier draft described, but the disclosure still applies.

### 2. DataForSEO — strongest on cost, no longer the fastest at any cost

**Strong:**
- Cheapest cost of the five, and the only one that's a real *measured* billing figure at that absolute price, not an estimate ($0.03754/1,000 reviews). Reconfirmed by a live rerun (2026-08-13): 5/5 domains, $0.0375 total, identical to the original.
- Zero errors, zero debugging required, docs matched live behavior exactly — reconfirmed live.
- Second overall, 0.23–0.83 points behind Lobstr.

**Weak:**
- Confirmed hard ceiling of 200 reviews per business — no pagination parameter exists for this endpoint at all. This is the only *proven* scalability limit in the whole benchmark, not just an untested gap.
- 🔴 **Speed regression observed live:** a 2026-08-13 rerun took 59–108 seconds per domain to complete, versus 2–3 seconds originally — roughly 2.5x slower under today's queue conditions, though still well within the provider's own documented worst-case SLA ("up to 45 minutes"). Data quality and cost were unaffected; this is a speed-only finding.
- No SDK or support interaction was tested.

### 3. Outscraper — reliable and well-documented, priciest by far (7.35/10)

**Strong:**
- Zero real errors of any kind; 100% success rate — reconfirmed by an exact-reproduction live rerun (2026-08-13).
- **Tied with Lobstr for the highest Data Quality sub-score (1.94/2.0)** — its 6 field-level mismatches (`author_reviews_count`, `company_replied`) are the same capture-timing pattern seen in Lobstr's evidence, not extraction errors. 🔴 An earlier draft of this document claimed Outscraper had zero mismatches; that did not match `DATA/outscraper/analysis/ground-truth-match.json`.
- Documentation proactively flags real integration gotchas (e.g., `skip` must be a multiple of 20).
- Its $3/1,000 rate-card estimate is independently corroborated by the provider's own current published pricing page (checked 2026-08-13), though a true measured billing figure was still not obtained.

**Weak:**
- By far the most expensive provider tested — an estimated (not measured) $2.70–$3.00 per 1,000 reviews, roughly 72–80x DataForSEO's measured cost.
- Rate limits are "not documented at all" — the worst-documented limits of the five, and no scale test exists to compensate.
- Its own `smoke` test mode requests far more than its docstring advertises (confirmed bug — see `MISSING_AND_GAPS.md` A.7), a real cost surprise for anyone trying it cheaply first.

### 4. Apify — recurring silent-failure pattern, now scored on a complete rubric

**Strong:**
- Highest Cost sub-score of the five (1.20/1.5) for having a real measured billing figure.
- Real, working retry/error-classification logic in its client.
- Now fully scored for the first time (6.10/10) — Speed and Data Quality, previously left blank, have been filled in from evidence that already existed in this project.

**Weak:**
- 🔴 **Confirmed recurring, business-agnostic silent failure across three separate live runs** — SHEIN → thepearlsource → thehalara.com, a different business each time, always a clean `SUCCEEDED` status with zero error signal, always ~80% overall success. This is no longer a one-off anomaly; it's a repeating defect.
- Ground-truth comparability for its one verifiable business is currently volatile, not a stable characteristic — see §6. Neither a "92%" nor a "0%" figure should be quoted as Apify's accuracy without this caveat.
- Fourth of five overall (6.10/10), driven mainly by the unresolved reliability pattern rather than any single weak criterion.

### 5. OpenWeb Ninja — total failure on rerun; not currently recommendable

**Strong:**
- Broadest Input Flexibility & Coverage of the five (0.60/0.8) — 9 distinct endpoints and genuine enrichment options, a documented capability unaffected by this run's outcome.
- Broadest official SDK language coverage (Shell/Ruby/Node.js/PHP/Python) and a disclosed pre-run quota-check mechanism — both structural facts, still true regardless of this run's outcome.

**Weak:**
- 🔴 **An earlier evidence pass recorded a clean 100% run with one recovered error; that has since been superseded by a total failure on this account.** The account's most recent verified run returned **0 of 1,000 reviews across all 5 domains**, with 75 confirmed HTTP 429s that its own retry logic never cleared, across roughly 37 minutes and multiple retry waves. A root-cause comparison against the successful run (see §1) found this is **more consistent with an account/quota-side issue than a proven provider-wide regression** — the failure starts on the very first request of the session rather than escalating with this benchmark's own traffic, but the API exposes no quota metadata to confirm the exact mechanism. **This is an observed benchmark outcome for this account, not a settled verdict on the product.**
- Every scored criterion collapsed as a direct result: Reliability 0.10/2.0 (was 1.98), Data Quality 0.00/2.0 (was 1.82), Cost 0.35/1.5 (was 0.70), Speed 0.23/1.5 (was 0.98), Scalability 0.15/1.2 (was 0.50), Developer Experience 0.62/1.0 (was 0.89).
- Not retested during the 2026-08-13 live-verification pass — the script requires a quota-remaining figure from the account's web dashboard, which has no API endpoint and was not available.
- Last of five overall (2.05/10), by a wide margin.

**On scalability, overall:** Lobstr is the only provider tested past 200 reviews from one business — live-verified at 2,000/2,000 as of 2026-08-13 (an earlier 1,000-review version of this test has no surviving raw evidence). No provider was tested under real concurrency or at 10x *total* volume across all domains, so the benchmark should not be read as a guarantee of sustained production performance for any provider, including Lobstr.

---

## FAQ

**Q: Which API is cheapest?**
DataForSEO, by a wide margin — $0.03754 per 1,000 reviews, and it's a real measured figure from the API's own billing field, not an estimate. Outscraper's estimated cost for the same benchmark is roughly 72–80x higher.

**Q: Which API is fastest?**
DataForSEO had the fastest total wall-clock time in the original committed benchmark (165,513 ms). 🔴 A live rerun on 2026-08-13 measured 59–108 seconds per domain (≈421,200 ms total, serial) — roughly 2.5x slower under today's queue conditions, though data quality and cost were unaffected and this remains within DataForSEO's own documented worst-case SLA. Lobstr's isolated single-business test at 1,000 reviews has no surviving timing evidence (the previously-cited "~179 seconds" didn't match any file in the project and was removed — see §3); the verified 2,000-review version of that test (2026-08-13) took 334,375 ms.

**Q: Which API is most reliable?**
🔴 This answer has changed materially since an earlier draft, and depends on which basis you use. By rubric score, Lobstr edges it (1.95/2.0), but that figure is flagged elsewhere in this document as not independently reproducible (see §1). **Outscraper is the cleanest fully-sourced answer**, with no caveats attached to its number: 100% success, 0 duplicates, 0 errors, reconfirmed by an exact-reproduction live rerun, and a Reliability score (1.92/2.0) that traces exactly to its scorecard. Apify shows a **confirmed recurring pattern** across three separate live runs — a different business silently returns 0 results each time (SHEIN → thepearlsource → thehalara.com), always with zero error signal, at a consistent ~80% success rate; this is no longer an unexplained one-off. OpenWeb Ninja, previously the top scorer on this criterion (1.98/2.0) with a single clean recovered error, has **since failed completely on a verification rerun** — 0 of 1,000 reviews, 75 unrecovered HTTP 429s — and is now the least reliable of the five by a wide margin.

**Q: Which API returns the most complete/accurate data?**
Outscraper and Lobstr are now **tied** at the highest Data Quality sub-score (1.94/2.0 each) — both show the same 6 field-level mismatches (`author_reviews_count`, `company_replied`), attributable to the 8-day gap between the ground-truth sample's collection date and these runs, not extraction errors (a transcription error in an earlier draft had understated Lobstr's figure at 1.70, and separately overclaimed Outscraper as having zero mismatches). Apify's ground-truth comparability for this business is **volatile, not a stable figure** — it has swung between full data and zero data across three live runs depending on which business happened to fail that run; neither a high nor a low number should be quoted for it without that caveat. All figures are based on a 20-row sample for one business only (`www.thepearlsource.com`) — none of the other 4 tested domains have any ground truth to check against.

**Q: Can any of these APIs pull more than 200 reviews for a single business?**
Yes. Lobstr is the only provider in this project directly verified beyond 200 reviews from one business: a live test (2026-08-13) returned **2,000/2,000 unique reviews with 0 duplicates**, with no cap encountered. (An earlier 1,000-review version of this same isolated test is referenced in this document's header, but no raw evidence for it survives — see §1/§3/§4 — so only the 2,000-review result is independently verified.) DataForSEO remains hard-capped at 200 reviews per business with no pagination parameter. This result is reported alongside, never blended into, Lobstr's standard-test score — see §4.

**Follow-up round — same "1 business, N reviews" test repeated against all five providers:** 🔴 **Corrected — only Lobstr's version of this test was actually executed.** Dedicated single-domain test scripts exist for all five providers (`scripts/<provider>/single_domain_test.py`), each designed to write to its own isolated output directory, but only `outputs/lobstr-single-domain-test/` exists anywhere in this project — the other four (`outputs/apify-single-domain-test/`, `outputs/dataforseo-single-domain-test/`, `outputs/outscraper-single-domain-test/`, `outputs/openwebninja-single-domain-test/`) were never run; no raw evidence for them exists. lobstr.io is the only provider verified to succeed at this specific test, confirmed by a 2026-08-13 live run returning 2,000/2,000 reviews from `www.thepearlsource.com` with 0 duplicates and no cap encountered. The previously-stated outcomes for the other four providers did not come from this test: Apify's 0-review results are from the unrelated **standard 5-domain benchmark** (see §1/§3/§6), not a dedicated depth test; OpenWeb Ninja's "unknown error" is the verbatim HTTP 500 message from that same standard benchmark's archived error log, also unrelated to this test; Outscraper's "silently capped at 200" and DataForSEO's "rejected depth above 200" claims have been removed entirely — neither traces to any file in this project, and both scripts' own docstrings explicitly frame these as open empirical questions still to be tested, not assumed outcomes. lobstr.io remains the only provider directly verified to return more than 200 reviews from one business.

**Q: Why not just use Trustpilot's own official API instead of a third-party scraper?**
Trustpilot's official Business Units/Product Reviews/Service Reviews APIs, and its separate cross-business Data Solutions API, all require a Trustpilot for Business account with API module access — obtained through Trustpilot-side setup (waitlist/approval), not instant self-serve signup. That's why this benchmark excluded it before live testing (criterion E1) rather than after — see "Eliminations (E1–E6)" and "Official API Deep-Dive" above.

**Q: Is this benchmark reproducible?**
Partially, and the gaps are explicit rather than hidden. All five providers' scripts were run live against real accounts, evidenced by the raw request/response/error logs throughout `DATA/`. 🔴 **Citation corrected:** this was previously attributed to `MISSING_AND_GAPS.md` A.8, but that item is about a narrower topic (live write-paths and multi-page pagination remain unverified) and names a different set of providers (confirms live read-only calls for Apify, DataForSEO, and Lobstr specifically; notes OpenWeb Ninja had no free endpoint to test) — it doesn't support the general "run live" claim as previously worded. DataForSEO's script is the weakest link — it doesn't yet reproduce the full evidence trail the historical run left behind (see `MISSING_AND_GAPS.md` A.1–A.2).

**Q: Is the scoring rubric neutral?**
It's disclosed, not neutral by default: `criteria.md` is headed "Owner: lobstr.io content team," and Lobstr is one of the five providers being scored against it. No specific finding in this benchmark was found to be suppressed or reframed in Lobstr's favor, but this ownership fact should be stated plainly in any published comparison, not buried.

**Q: Does any of this generalize beyond these 5 specific businesses?**
Not with confidence. All 5 providers were run exactly once, against the same 5 fixed domains, and ground truth exists for only 1 of those 5. Treat every number here as "what happened in this one run," not as a guaranteed, repeatable performance profile.

**Q: Is Lobstr the best overall choice?**
On this benchmark's rubric, yes: Lobstr finishes #1 at 7.88/10 on the standard test basis, fully sourced. A second basis of 8.48/10 is sometimes cited if its 2,000-review bulk test is credited toward Scalability ⚠️ — the *test* itself is live-verified, but the 1.20/1.2 score that credit would require is not independently sourced anywhere in this project (see §4), so 7.88/10 is the only fully-supported total. Either way Lobstr finishes ahead of DataForSEO at 7.65/10 — a 0.23–0.83-point margin, depending which basis is used. It was the only provider directly verified to return more than 200 unique reviews from one Trustpilot business, now confirmed at 2,000. Given the rubric-ownership disclosure above, "Lobstr wins" should still be presented as a rubric-dependent result, though the margin is real rather than the near-tie described in an earlier draft of this document.

**Lobstr's price: corrected.** Lobstr's rate is $0.50 per 1,000 reviews, per the provider's own current published documentation (`lobstr.io/store/trustpilot-reviews-scraper`, checked 2026-08-13) — **not $1/1,000 as an earlier draft of this document stated.** At $0.50/1,000, Lobstr is pricier than DataForSEO's measured $0.03754/1,000, but **actually cheaper than Apify's measured $0.5812/1,000** — a real reordering from the earlier $1/1,000 figure, which had placed Lobstr above Apify on price. Both remain well under Outscraper's estimated $2.70–$3.00/1,000. Credit consumption (1:1, at both 1,000- and 2,000-review scale) is directly measured on this account; the $0.50 dollar rate itself is sourced to official documentation, not this account's billing API.

---

## Legal FAQ Block

**Q: Does Trustpilot's Terms of Use prohibit scraping its reviews?**
Yes, explicitly. Trustpilot's Terms of Use for Consumers (Section 4, "Your key responsibilities") state:

> "You must not access, search or collect content from our platform by any means (automated or otherwise) except as provided on our platform or specifically approved by us."

and, more specifically:

> "You must not carry out in any way (including facilitating, permitting or authorising) any text mining, data mining or web scraping of our platform for any purpose without our express permission. This includes the training and development of artificial intelligence systems or models."

Source: [Trustpilot Terms of Use for Consumers, Feb 2025, Section 4](https://corporate.trustpilot.com/legal/for-reviewers/terms-of-use-for-consumers/feb-2025).

**Business Terms carry the same restriction, differently worded.** [Terms of Use and Sale for Businesses, Nov 2025, Section 21 ("Don'ts")](https://corporate.trustpilot.com/legal/for-businesses/terms-of-use-and-sale-for-businesses/nov-2025):

> "Access, search, or collect content from our platform or services by any means (automated or otherwise) except as permitted" ... "you must not carry out, facilitate, authorise or permit any text or data mining or web scraping in relation to our platform" ... "including the development, training, fine-tuning or validation of artificial intelligence systems or models."

**No material difference found** between the Consumer terms (§4) and Business terms (§21) — both prohibit automated collection/scraping/mining without permission and both explicitly name AI training; only the section number and exact wording differ.

**Q: Is scraping public review data illegal in the US?**
Not under the CFAA specifically. *hiQ Labs v. LinkedIn* (9th Circuit, 2019, reaffirmed 2022 after *Van Buren v. United States* narrowed CFAA in 2021) held that scraping data from a site open to the public does not violate the Computer Fraud and Abuse Act's "unauthorized access" prohibition. But that is not the whole story: LinkedIn separately won on **breach-of-contract and trespass** grounds — a district court found hiQ breached LinkedIn's User Agreement in Nov 2022, hiQ then settled in Dec 2022, paid $500,000, was permanently enjoined from scraping LinkedIn, and shut down. **Net effect: a platform's own Terms of Use (like Trustpilot's clause above) can still create real contract-law exposure even where the CFAA doesn't apply.** [LegalClarity: hiQ v. LinkedIn](https://legalclarity.org/the-final-ruling-in-the-linkedin-scraping-case/) · [Apify: hiQ v. LinkedIn case law](https://blog.apify.com/hiq-v-linkedin/)

⚠️ Jurisdiction scope: this FAQ covers US case law only — no EU/French precedent (e.g. the L342-3/Entreparticuliers-style analysis used in lobstr.io's listicle format) was researched for Trustpilot specifically.

---

## Winner Quickstart Facts

Final winner: **Lobstr at 7.88/10** (standard test basis, fully sourced) / **8.48/10 ⚠️** (with its live-verified 2,000-review bulk test credited toward Scalability — this alternate total relies on an unsourced 1.20/1.2 Scalability figure, see §4). DataForSEO ranks second at **7.65/10**. Quickstart facts for both, from actual raw captures in this project (no credentials reproduced):

### DataForSEO
- **Auth:** HTTP Basic Auth — `base64(login:password)` sent as `Authorization: Basic {REDACTED}` (built in `SCRIPTS/dataforseo/benchmark.py:54`, formerly `scripts/dataforseo_benchmark.py:50-53` before the 2026-08-13 folder restructure; the header value itself is not present in any raw capture file).
- **Setup:** `POST /v3/business_data/trustpilot/reviews/task_post` with body `{"depth": 200, "sort_by": "recency", "priority": 1}` (from `DATA/dataforseo/raw/task-post/www.thepearlsource.com.json`).
- **Sanitized response fields:** `status_code: 20000`, `tasks[0].id`, `result_count`; retrieved results include e.g. `"title": "The Pearl Source", "rating": {"value": 4.8}, "reviews_count": 17558` (from `DATA/dataforseo/raw/task-get/www.thepearlsource.com.json`).

### Lobstr
- **Auth:** Token auth — `Authorization: Token {REDACTED}` (per `api_docs_mcps.txt:2146-2156`; not present in raw captures).
- **Setup:** `POST https://api.lobstr.io/v1/tasks` with body `{"squid": "...", "tasks": [{"url": "https://www.trustpilot.com/review/www.thepearlsource.com"}]}` (body shape documented in `api_docs_mcps.txt:2380-2397`; the `www.thepearlsource.com` URL itself is confirmed used in `DATA/lobstr/raw/requests/tasks.json`'s `domain_task_map` — that file records the resulting tasks, not the outbound request body).
- **Sanitized response fields:** e.g. `"company_name": "The Pearl Source", "rating_value": 5, "review_body": "...", "stars": 5.0` (from `DATA/lobstr/raw/results/results-page1.json`).

---

## Concept Explainer Choice

⚠️ **Proposed, needs writer confirmation** — the concept most likely to gate the reader's decision in this article: **the self-serve access gate.** Framing: before comparing any third-party API on performance, the reader first needs to understand *why* Trustpilot's own official APIs (including the cross-business Data Solutions API) aren't on the table at all — not because of data scope, but because none of them offer instant self-serve access (criterion E1). Everything that follows in the article is "given that the official route isn't self-serve, which third-party API is actually worth paying for."

Alternative candidate considered: sync vs. async execution models (🔴 corrected — OpenWeb Ninja is the only synchronous provider; DataForSEO, Apify, and Outscraper are all async submit-then-poll (DataForSEO's own scorecard documents a "fully async task model": `task_post` → `tasks_ready` poll → `task_get`); Lobstr is async with an additional separate retrieval phase) — this is real and documented (Section 3, Speed) but reads more like a technical caveat for comparing timing numbers than the single concept that gates the reader's *buying* decision.

---

## Store / Links

| Item | Value | Source |
|---|---|---|
| Lobstr scraper name | "Trustpilot Reviews Scraper" | `api_docs_mcps.txt:2200-2210` (name at 2203; slug `trustpilot-reviews-scraper` at 2206-2210) |
| Lobstr store URL | `https://www.lobstr.io/store/trustpilot-reviews-scraper` — also the direct source for the corrected $0.50/1,000 rate (§2), and already hardcoded correctly in `SCRIPTS/lobstr/benchmark.py:974` (`advertised_rate_per_1000 = 0.5`) even while this document's prose still said $1 | `api_docs_mcps.txt:2956`, `SCRIPTS/lobstr/benchmark.py:382,974` |
| Lobstr CTA link | `https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link` (standard CTA pattern per `facts.md`/CLAUDE.md) | derived, not independently confirmed |
| Apify docs | `https://apify.com/automation-lab/trustpilot` | `api_docs_mcps.txt:66` |
| DataForSEO docs | `https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_post/` | `api_docs_mcps.txt:1449-1450` |
| Outscraper docs | `https://docs.outscraper.com/endpoints/trustpilot-reviews/` | `api_docs_mcps.txt:4568-4569` |
| OpenWeb Ninja docs | `https://www.openwebninja.com/api/trustpilot-company-and-reviews-data/docs` | `api_docs_mcps.txt:3411` |
| Trustpilot official API docs | `https://developers.trustpilot.com/` | research, this session |
| Gist/repo (raw evidence) | ⚠️ MISSING — needs publishing | see Benchmark Methodology Record above |
| Matching no-code listicle | ⚠️ MISSING — writer said ignore for now | — |

---

## Open Items

1. 🔴 Primary SEO keyword — corrected: Article Meta states this is writer-confirmed ("trustpilot reviews api"), not pending sign-off. Resolved, not open.
2. Matching no-code listicle to cross-link — writer said ignore for now (Store / Links — corrected pointer; no longer in Article Meta)
3. Public gist/repo URL for raw benchmark evidence — not yet published (Benchmark Methodology Record)
4. Which other tools were discovered pre-benchmark and why excluded — no evidence found anywhere in the project (Eliminations)
5. 🔴 Corrected: the Official API use-cases bullets were removed from Official API Deep-Dive as unnecessary detail — they were already researched and sourced before removal, not an outstanding research gap. Nothing open here.
6. Official API pricing — unconfirmed, no direct billing evidence (Official API Deep-Dive)
8. Input Flexibility & Coverage scorecard sub-scores (0.8 pts, all 5 providers) — final approved values are reflected in Section 7 and the Final Summary
9. Scorecard totals (corrected 2026-08-13): Lobstr is the overall winner at 7.88/10 standard (8.48/10 ⚠️ with its bulk-volume test credited — this alternate total relies on an unsourced 1.20/1.2 Scalability figure, see §4); DataForSEO ranks second at 7.65/10; Outscraper third at 7.35/10 (its Speed sub-score was also found to be computed against an archived run instead of the current committed evidence — see §3); Apify fourth at 6.10/10 (now fully scored — Speed and Data Quality were previously left blank); OpenWeb Ninja fifth at 2.05/10 (down from 7.37/10 — its scorecard previously described a run that has since been superseded by a confirmed total failure)
18. **New:** Outscraper's committed `DATA/outscraper/analysis/timings.json` is a separate, later run (2026-07-29) from the archived `.../archive-full-copy/2026-07-21-run/` copy this document previously cited as "canonical" — both are real evidence, but a reader pulling from the archived folder will see different timing figures than the current committed file. Worth flagging if either is cited directly in a published article.
10. Concept Explainer Choice ("the self-serve access gate") — proposed, needs writer confirmation
11. 🔴 Legal FAQ — corrected: Trustpilot's *business* ToS has since been researched and quoted (Section 21, "Don'ts"), verified against the live page. Only the EU/French precedent gap remains open — this FAQ still covers US case law only.
12. Lobstr CTA link — derived from the standard pattern, not independently confirmed against the live store page
13. Data Quality & Completeness (Section 6) figures predate `/datacompare` and aren't sourced from its artifact — consider re-running `/datacompare` against `data/` before finalizing
14. ~~Apify's missing Speed and Data Quality sub-scores~~ — resolved 2026-08-13: both filled in from `DATA/apify/analysis/` evidence that already existed (Speed 1.10/1.5, Data Quality 0.60/2.0). Apify's total is now out of the full 10.0.
15. **New, unresolved:** Apify's ground-truth comparability for `www.thepearlsource.com` is volatile across runs (a different business fails silently each time) — no stable accuracy/field-coverage figure can currently be quoted for it. Needs either a root-caused fix to the underlying failure or a policy decision on how to report a metric that changes every run.
16. 🔴 **Corrected, still unresolved:** Lobstr's standard 5-domain test does have fresh evidence — a committed run dated 2026-07-29 (7×429 errors, 220,530 ms wall-clock), distinct from the archived 2026-07-22 run (62×429, 99,346 ms) — so the sub-scores are not simply "carried forward" from the archived scorecard. The real open issue is narrower: some scores (e.g. Speed, 1.24/1.5) are sourced to the archived run's own scorecard despite this fresher evidence existing, while others (e.g. Reliability, 1.95/2.0) match neither run's sourced figures. See §1 and §3 for the specific misattributions already flagged there.
17. **New, unresolved:** OpenWeb Ninja was not retested during the 2026-08-13 live-verification pass — its current 2.05/10 score reflects the last confirmed rerun (prior to this document's correction pass), not a fresh check. A quota-remaining figure from the account's web dashboard would be needed to retest it (no API endpoint exists for this).
