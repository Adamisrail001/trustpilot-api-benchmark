# Trustpilot Review-Scraping API Benchmark — Knowledge Base

> This file is the article's single source of truth. Facts here are writer-provided or research-confirmed; ⚠️ markers are unresolved gaps — the writing command will stop on them.
>
> **Purpose of this document:** this is a raw-evidence research worktable, not a final article or procurement recommendation. It exists so a writing agent (or a human editor) can rely on verified facts rather than trusting adjectives when drafting the final article. Status markers used throughout, where applicable: ✅ **CAPTURED** (complete, traceable evidence), ⚠️ **PARTIAL** (some evidence, incomplete validation), ❌ **MISSING** / **Not tested** (no evidence exists — never softened into an estimate), ❓ **UNCLEAR** (evidence exists but provenance/interpretation unconfirmed), 🔴 **DISCREPANCY** (sources conflict, not silently resolved).
>
> **Synthesis note:** this file was synthesized on 2026-07-27 from two audited source projects (one treated as the primary, authoritative source — a criterion-by-criterion audit; the other as a secondary, lower-confidence cross-check, since it states it was rebuilt after finding an earlier draft cited files that didn't exist in its own project folder). It has been restructured into the 6 categories required for the article outline. No number, date, or claim below was invented — anything neither source could verify is marked "Not tested" / "Evidence not available."
>
> **Scope of the benchmark (all 5 providers):** DataForSEO, Outscraper, OpenWeb Ninja, Apify, Lobstr were each run once, on the same 5 fixed Trustpilot business domains — `www.thepearlsource.com`, `www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` — each targeting 200 reviews (1,000 requested per provider). A separate isolated Lobstr test then targeted `www.thepearlsource.com` alone at 1,000 reviews and returned 1,000/1,000 unique valid reviews with 0 duplicates.
>
> **Ground truth exists for exactly 1 of the 5 domains** (`www.thepearlsource.com`, a manually-verified 20-row sample). SHEIN, Temu, AliExpress, and Halara have **no ground truth at all**. Every accuracy/field-coverage figure below is valid only for `www.thepearlsource.com` and must never be read as representative of the other four domains — this is restated in Section 6 rather than assumed silently.
>
> **Rubric authorship flag:** the scoring rubric (`criteria.md`) is headed "Owner: lobstr.io content team." Lobstr is also one of the five evaluated providers. Both source projects flag this explicitly; neither resolves it. Treat any Lobstr-favorable figure with that in mind.

---

## Article Meta

- **Working title:** "Trustpilot Reviews API Article" (writer-provided working name); final headline TBD at article-writing time, expected to follow the format's `Best {X} API for Scraping Data at Scale [Year Benchmark]` pattern.
- **Slug:** `/trustpilot-reviews-api-article/`
- **Primary SEO keyword:** **"trustpilot reviews api"** — writer-confirmed.
- **Full roster tested:** Apify, OpenWeb Ninja, DataForSEO, Outscraper, Lobstr (official + internal API status: see "Eliminations (E1–E6)" below — Trustpilot's own official API was never tested).
- **Matching no-code listicle to cross-link:** ⚠️ MISSING — writer said ignore for now.

---

## Benchmark Methodology Record

- **Fixed input dataset:** 5 Trustpilot business domains — `www.thepearlsource.com`, `www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` — each targeting 200 reviews (1,000 requested per provider). Lobstr also received a separate isolated single-business test requesting 1,000 reviews from `www.thepearlsource.com`, which returned the complete 1,000-review target with 0 duplicates.
- **Test window:** all 5 providers run within the same benchmark session (2026-07-27 synthesis date; exact test-window dates not restated here — see per-provider raw logs in `data/`).
- **Shared script template:** one benchmark script template adapted per provider's auth/request format (`scripts/`) — DataForSEO's port is the weakest/least mature (see `MISSING_AND_GAPS.md` A.1–A.2).
- **What was logged:** raw request/response captures, timings, error/cost/pagination reports per provider (uneven — DataForSEO missing 3 of the standard analysis files, see `MISSING_AND_GAPS.md` A.2).
- **Public gist/repo URL:** ⚠️ **MISSING — needs publishing.** Raw benchmark evidence (scripts, logs, raw data) is not publicly published yet. Writer will supply the GitHub/Gist URL once published. Reproducibility claims in the FAQ ("Is this benchmark reproducible?") must not overstate this — no public link exists today.

---

## Eliminations (E1–E6)

⚠️ **PARTIAL** — one elimination resolved, the rest remain open pending evidence.

| API | Criterion failed | One-line reason | Evidence |
|---|---|---|---|
| Trustpilot Official API (Business Units / Product Reviews / Service Reviews) + Data Solutions API | **E1 — No self-serve access** | Neither the standard Business API nor the cross-business Data Solutions API offers instant self-serve access — both require Trustpilot-side setup (API module access / waitlist) before a working key can be obtained. Excluded during pre-screening; no live access was ever obtained and no benchmark was run against it. | Writer-confirmed + [developers.trustpilot.com](https://developers.trustpilot.com/introduction) |

**Other discovered-but-untested tools:** `MISSING_AND_GAPS.md` (item A.5) references "the other discovered tools" without naming them. A search of every doc in this project (`README.md`, `criteria.md`, `api_docs_mcps.txt`) found **no list, name, or evidence of what these other tools were** — no discovery/shortlist artifact exists anywhere in the project.

⚠️ **MISSING: which other tools were discovered and why each was excluded — ask writer | needs research.** Per instruction, no criterion is assigned without supporting evidence — this stays an open item rather than a guessed E1–E6 mapping.

---

## Official API Deep-Dive (Trustpilot)

- **What it actually offers:** Trustpilot exposes three official APIs — Business Units API, Product Reviews API, Service Reviews API — plus a separate **Data Solutions API** that can return review data across businesses (not just one business's own reviews). [Trustpilot developer docs](https://developers.trustpilot.com/)
- **Access model:** requires a Trustpilot for Business account with **API module** access via the Developer Portal. Public endpoints authenticate with a simple `apikey` header; private endpoints (and the Data Solutions API) require full OAuth 2.0 + Trustpilot-side setup (waitlist/approval) — writer-confirmed this is not self-serve for either path. [Authentication overview](https://developers.trustpilot.com/authentication/) · [Authorization code grant](https://developers.trustpilot.com/grant-type-auth-code/)
- **Public Business Units API note:** returns reviews via `pageToken` pagination but excludes customer email/order ID; the private/OAuth version includes those fields. [Business Units API](https://developers.trustpilot.com/business-units-api)
- **Pricing:** ⚠️ MISSING — unconfirmed. No direct billing evidence exists; do not claim paid pricing without it.
- **THE wall:** not a business's-own-data limitation (the Data Solutions API can cross businesses) — the actual wall is **non-self-serve access**: both the standard Business API and the Data Solutions API require Trustpilot-side setup/waitlist before a working key can be obtained, which fails this benchmark's E1 self-serve eligibility requirement.
- **Live access / code example:** ❌ Not obtained. No working access was ever secured; no live benchmark was run. Documented here as excluded during pre-screening, before live testing — not a wall discovered mid-benchmark.
- **Use cases (researched, sourced):**
  1. **Sending review invitations** — the Invitation API lets a business generate a unique invite link (or trigger one by email) sent to a customer after a purchase/service interaction, with a `redirectURI` to chain a product-review request after a service review. [Invitation API](https://developers.trustpilot.com/invitation-api) · [Invitations API overview](https://developers.trustpilot.com/invitations-api-overview/)
  2. **Displaying review summaries/widgets on the business's own site** — the Business Units API returns star-rating average, distribution, and count for a business unit, plus public business-unit info (name, URL, reviews), for embedding on external pages. [Business Units API (public)](https://developers.trustpilot.com/business-units-api-(public)/)
  3. **Reputation monitoring / internal toolchain integration** — pulling a business's own review/reply data into internal dashboards or CRM systems rather than scraping it. [Get started with Trustpilot for Business](https://developers.trustpilot.com/introduction)

---

## Internal (Hidden) API

**Out of scope for this benchmark.** No file in this project (`scripts/`, `data/`, `outputs/`, `README.md`, `api_docs_mcps.txt`) shows any evidence that investigating a hidden/internal Trustpilot endpoint (DevTools-discovered network calls, an anti-bot system, a block-screen) was ever intended or planned for this benchmark — the roster and all raw evidence are scoped to the 5 public/documented third-party APIs plus the officially-excluded Trustpilot API. Per writer instruction: since no evidence of intent exists, this is treated as out of scope rather than an unexplained gap.

---

## 1. Success Rate & Reliability

> Every figure below describes **one benchmark run of 1,000 requested reviews per provider**. None of it is evidence of reliability under repeated trials, concurrent load, or sustained production use — that distinction is preserved throughout, not collapsed into a single "reliability" adjective.

### Apify

- **Requests attempted:** 1 Actor run (`automation-lab/trustpilot`, all 5 domains submitted together) + 36 status-poll requests + 1 dataset-items fetch = 38 total calls.
- **Successful requests:** all HTTP-level calls succeeded; run status reported `SUCCEEDED`.
- **Raw / unique reviews returned:** 800 / 798 (target 1,000) — **overall success rate 79.8%**.
- **Missing/zero-result business:** `www.shein.com` returned **0 of 200** requested reviews, with **no error, retry, or failure signal anywhere in the evidence** (the error log is empty). The run's own status message (`"Crawled 4/5 pages, 0 failed requests, desired concurrency 1"`) reported itself as fully successful despite the shortfall. Investigated and ruled out: HTTP/network errors, error-shaped dataset objects, abnormal run stats (clean execution, 0 migrations/reboots). Root cause remains **unresolved** — would require inspecting Apify's live console run log, not exposed via the documented REST endpoints used here.
- Two small near-misses (not the SHEIN issue): `www.aliexpress.com` and `thehalara.com` each returned 200 raw but had exactly 1 internal duplicate (199 unique each).
- **Retries:** 0 triggered (none needed at HTTP level).
- **Scorecard sub-score:** 1.38/2.0 — success-rate sub-score reflects the raw 79.8%; error-handling-quality sub-score penalized heavily because the failure produced zero detectable signal.

### OpenWeb Ninja

- **Requests attempted:** 50 logical page requests (5 domains × 10 pages); 51 total HTTP calls counting 1 retry.
- **Successful requests:** 50 of 50 logical requests eventually succeeded; 0 final failures.
- **Raw / unique reviews returned:** 1,000 / 1,000 — **100% success rate**, 0 shortfall, 0 duplicates.
- **HTTP errors:** 1 × HTTP 500 on `www.thepearlsource.com` page 1, attempt 1 (`"An unknown error has occurred"`, code 500) — retried once, succeeded on attempt 2.
- **Scorecard sub-score:** 1.98/2.0 — the highest Reliability sub-score of the five, credited for having a *real, cleanly-recovered* error to evaluate rather than zero errors and an untested retry path.

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
- **Polling-request count — resolved:** directly counted from the canonical `data/analysis/outscraper/timings.json` (the 2026-07-21 run, `wall_clock_ms: 512,595` — matching the duration cited in Section 3 below): **84 poll-phase entries + 5 submit-phase entries = 89 total**. The primary source's "~120" figure does not match the array length in any raw timings file found in this project and is **not treated as the fact of record** — 84 is the resolved, directly-counted figure.

### Lobstr

- **Requests attempted:** isolated task/squid/run setup calls for `www.thepearlsource.com` + 101 result-page fetch requests at 10 results per page.
- **Successful requests:** the isolated run completed with `status: done`; all result pages were retrieved and the run stopped with `no_next_page` after the full target was collected.
- **Raw / unique reviews returned:** 1,000 / 1,000 from **one Trustpilot business** — **100% success rate**, 0 duplicates, and 1,000 unique Trustpilot review IDs.
- **HTTP errors: 7** confirmed HTTP 429 "Throttled" events during result-page retrieval.
- **Retries:** all 7 confirmed 429s succeeded on the immediate retry — 0 records lost.
- **A separate, earlier, fully-failed setup attempt exists** (archived, not part of the counted run): an `HTTP 400 DuplicateSquid` error blocked squid configuration before any task or run existed, because the benchmark script tried to rename the clean squid to a name already held by an old contaminated squid. Fixed by never sending a `name` field.
- **Scorecard sub-score:** 1.80/2.0.

**Cross-provider reliability summary**

| Provider | Requested | Raw / Unique returned | Success rate | Real errors this run |
|---|---:|---|---:|---|
| Apify | 1,000 | 800 / 798 | 79.8% | 0 (silent SHEIN gap instead) |
| OpenWeb Ninja | 1,000 | 1,000 / 1,000 | 100% | 1× HTTP 500 (recovered) |
| DataForSEO | 1,000 | 1,000 / 999 | 99.9% | 0 |
| Outscraper | 1,000 | 1,000 / 1,000 | 100% | 0 |
| Lobstr | 1,000 | 1,000 / 1,000 from 1 business | 100% | 7× HTTP 429 (all recovered) + 1 archived setup-stage HTTP 400 |

---

## 2. Cost Effectiveness

> Strict distinction maintained throughout: **confirmed billed cost** (from the provider's own billing field) vs. **API usage field** vs. **published rate-card calculation** vs. **credit count with no monetary conversion** vs. **no direct charge observed during the test.** These are never conflated.

### Apify

- **Billing model:** pay-per-event (run-start fee + per-review charge).
- **Published pricing:** $0.005/run start + $0.000575/review (free tier).
- **Measured billed cost: $0.465** — directly from `usageTotalUsd` on the settled Run object (`chargedEventCounts: {start: 1, review: 800}`). This is a real, API-reported billing figure, not a calculation. Formula-estimated cost for the same 798 reviews was $0.4638 — measured cost is within 0.26% of that estimate.
- **Cost per 1,000 successful unique reviews: $0.5827** ($0.465 ÷ 798 × 1,000). Note this denominator (798) already bakes in SHEIN's shortfall.
- **Scorecard sub-score:** 1.20/1.5.

### OpenWeb Ninja

- **Billing model:** tiered monthly plans (Free/Pro/Ultra/Mega) + pay-as-you-go, documented per-request.
- **Measured billed cost: none.** The account's actual plan is **"Basic," which is not one of the four published tiers** — no confirmed $/request rate exists for it at all.
- **Calculated/estimated cost (by hypothetical tier, not this account's real rate):** Free $0 (marginal) / Pro $0.125 / Ultra $0.075 / Mega $0.0375 / Pay-as-you-go $0.25, for the 50 requests actually made.
- **Directly measured usage:** 50 requests made (matches the plan exactly, 0 wasted).
- **Cost per 1,000 successful reviews: cannot be computed** — no confirmed rate for the "Basic" plan.
- **Scorecard sub-score:** 0.70/1.5 — the weakest cost evidence of the five per both sources: unlike Outscraper's estimate, there isn't even a confirmed real plan tier to anchor a guess to.

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

- **Billing model:** credit-based; writer-confirmed actual rate $1 per 1,000 reviews ($0.001/review), 1 credit = 1 unique result. (Supersedes the earlier "$0.50/1,000, unconfirmed" figure — Shehriar confirmed the real rate directly.)
- **Measured billed cost in dollars: none.** This account is on Super Admin/"free"-plan terms with no exposed $/credit conversion via the API.
- **Credits consumed: 1,000** for 1,000 unique reviews — an exact 1:1 ratio. This is confirmed by the Run object's `credit_used: 1000` field and the isolated test's before/after credit snapshots, which moved from `consumed: 0` to `consumed: 1000`.
- **Cost per 1,000 successful reviews:** 1,000 credits per 1,000 reviews, at a writer-confirmed $1/1,000 — a real, confirmed rate, not an estimate.
- **Scorecard sub-score:** 1.05/1.5.

**Cross-provider cost summary**

| Provider | Cost evidence tier | Cost per 1,000 successful reviews |
|---|---|---:|
| DataForSEO | ✅ Measured (API `cost` field) | **$0.03754** |
| Apify | ✅ Measured (API `usageTotalUsd` field) | $0.5827 |
| Lobstr | ✅ Measured, confirmed rate | 1,000 credits at a confirmed $1/1,000 = $1.00 |
| Outscraper | ⚠️ Estimated from published rate card only | $2.70–$3.00 (not measured) |
| OpenWeb Ninja | ❌ No confirmed rate for this account's actual plan | Not computable |

---

## 3. Speed

> Timing figures are **not directly comparable** across providers without accounting for differing execution models: DataForSEO/Outscraper/OpenWeb Ninja/Apify each measure one continuous run; Lobstr uses an async run followed by sequential result retrieval; Apify's total includes asynchronous Actor run time plus polling overhead not present in the synchronous providers.

### Apify

- **Total wall-clock duration:** 417,896 ms (~6 min 58 s); the Actor's own reported run duration was 400,421–408,823 ms (the two Apify-internal figures disagree by several seconds — an internal inconsistency, not a cross-source one).
- **Requests:** 1 actor-start call + 36 status-poll requests + 1 dataset-items fetch.
- **Median/p95 latency:** not meaningfully applicable in the same sense as the synchronous providers — Apify's model is one long-running Actor run plus polling checks, not many discrete review-fetch requests.
- **Comparability limitation:** the 800/1,000 raw shortfall (SHEIN) means duration-per-successful-review is worse than duration-per-requested-review.

### OpenWeb Ninja

- **Total wall-clock duration:** 180,749 ms (~3 min 1 s).
- **Median latency:** 1,870 ms — **the slowest median of the five**.
- **p95 latency:** 3,684 ms — **the slowest p95 of the five** (consistent with the vendor's own published "1–5 seconds" typical response time).
- **Requests:** 50 synchronous, sequential requests (+1 retry).
- **Comparability limitation:** highest median/p95 among the five, but also the highest discrete-request count (50) processed fully synchronously and sequentially — no async/batch capability exists for this endpoint.
- **Scorecard sub-score:** 0.98/1.5.

### DataForSEO

- **Total wall-clock duration:** 165,513 ms (~2 min 46 s) — **the fastest total of the five**.
- **Median latency:** 404 ms — **the fastest median of the five**.
- **p95 latency:** 2,378 ms, driven by one cold-start `task_post` call.
- **Requests:** 10 total (5 `task_post` + 5 `task_get`).
- **Comparability limitation:** fastest total time, but also the smallest total request count (10) of the five — direct comparison to providers issuing 50+ requests understates their per-request efficiency. Documented worst-case SLA for standard priority is "up to 45 minutes" — this run's ~2:46 is a best-case result under whatever queue conditions existed at run time, not a guaranteed typical performance figure.
- **Scorecard sub-score:** 1.32/1.5.

### Outscraper

- **Total wall-clock duration:** 512,595 ms (~8 min 33 s) — **the slowest total of the five**.
- **Median latency:** 1,169 ms.
- **p95 latency:** 1,982 ms (a comparatively tight spread despite the slow total).
- **Requests:** 5 submissions + 84 polling requests until `status: Success` (89 total) — resolved by direct count of `data/analysis/outscraper/timings.json`, see Section 1.
- **Comparability limitation:** the slow total reflects the async submit-then-poll design (waiting through many poll cycles), not necessarily slower per-request processing.
- **Scorecard sub-score:** 1.07/1.5.

### Lobstr

- **Total wall-clock duration:** approximately **179 seconds** from isolated run start through final retrieval for 1,000 unique reviews from `www.thepearlsource.com` alone.
- **Median latency:** not reported for the isolated single-business run.
- **p95 latency:** not reported for the isolated single-business run.
- **Requests:** 101 result-page fetches at 10 results per page, including recovery from 7 confirmed HTTP 429 events.
- **Comparability limitation:** the isolated Lobstr test measured one business at a depth of 1,000 reviews, while the common benchmark spread 1,000 requested reviews across five businesses.
- **Scorecard sub-score:** 1.35/1.5.

**Cross-provider speed summary**

| Provider | Total wall-clock | Median latency | p95 latency | Execution model |
|---|---:|---:|---:|---|
| DataForSEO | 165,513 ms | 404 ms | 2,378 ms | Synchronous task/result, 10 calls |
| OpenWeb Ninja | 180,749 ms | 1,870 ms | 3,684 ms | Synchronous, sequential, 50+ calls |
| Apify | 417,896 ms | n/a (async) | n/a (async) | Async Actor run + polling |
| Outscraper | 512,595 ms | 1,169 ms | 1,982 ms | Async submit + poll |
| Lobstr | ~179,000 ms (1 business × 1,000 reviews) | n/a | n/a | Async run + sequential retrieval |

---

## 4. Scalability

> The common benchmark did not test real concurrency or 10x volume. Lobstr received one additional isolated scalability test at 1,000 reviews from a single business; no other provider was tested past 200 reviews per business.

### Apify

- **Max reviews tested from one business:** 200 (`maxReviewsPerCompany` set to 200; documentation claims `maxReviewsPerCompany=0` means "unlimited," **not tested** here).
- **Concurrency tested:** explicitly `desired concurrency 1` (single-threaded crawl) per the run's own status message — a real, documented value, not merely inferred from timing.
- **Rate-limit events:** 0. HTTP 429 events: 0.
- **10x volume test performed:** No — scorecard states "Degradation at 10x volume: 0.00 — Not tested."
- **Scorecard sub-score:** 0.52/1.2.

### OpenWeb Ninja

- **Max reviews tested from one business:** 200 (10 pages × 20/page); documentation states going past page 10 requires a Trustpilot login cookie — **not tested here**.
- **Concurrency tested:** none — requests were sequential.
- **Rate-limit events:** 0 real occurrences (the one real error was an HTTP 500, not a 429).
- **10x volume test performed:** No — "10x volume behavior: not tested"; the Basic plan's actual monthly cap and rate limit are unknown (only Free/Pro/Ultra/Mega limits are published).
- **Scorecard sub-score:** 0.50/1.2.

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

- **Max reviews tested from one business: 1,000.** In the isolated `www.thepearlsource.com` test, Lobstr returned 1,000/1,000 unique valid reviews with 0 duplicates.
- **Concurrency tested:** not deliberately tested; result-page retrieval was sequential.
- **Rate-limit events:** 7 confirmed HTTP 429 events occurred during result retrieval, and all recovered on the immediate retry with 0 records lost.
- **10x volume test performed:** No — the isolated test increased per-business depth to 1,000 reviews but did not test 10x total volume or concurrent runs.
- **Scorecard sub-score:** 1.20/1.2 — the strongest directly verified single-business scalability result in this benchmark.

**Cross-provider scalability summary**

| Provider | >200/business tested? | Concurrency tested? | Real rate-limit evidence? | 10x volume tested? |
|---|---|---|---|---|
| DataForSEO | No — confirmed hard ceiling (negative result) | No | No (0 events) | No |
| Outscraper | No — untested | No | No (0 events; limits wholly undocumented) | No |
| OpenWeb Ninja | No — untested (cookie-gated past page 10, unverified) | No | No (0 events) | No |
| Apify | No — untested (`0`="unlimited" claim unverified) | Documented `concurrency 1` | No (0 events) | No |
| Lobstr | **Yes — 1,000/1,000 from one business** | No | **Yes — 7 real 429s, all recovered** | No |

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

- **Authentication setup:** API key-based; worked, no friction logged.
- **Time to first successful request:** not isolated as a standalone metric.
- **SDK/client used:** none exercised — official SDK examples exist for Shell/Ruby/Node.js/PHP/Python (the broadest official language coverage of any tool tested) but none were tested.
- **Documentation issues:** **real, concrete finding** — the documentation requires a rendered browser to view correctly; a plain HTTP fetch of the docs page only returns the page shell.
- **Actual implementation problems:** one HTTP 500 occurred (Section 1), with a clear, structured JSON error body (`status`, `error.message`, `error.code`).
- **A genuine positive, directly evidenced:** a real, disclosed dry-run/quota check was performed before any billed calls — a concrete operational-diligence signal no other provider demonstrated in this benchmark.
- **Integration complexity:** the `company-reviews` endpoint accepts only `company_domain` — no direct company-ID or URL parameter.
- **Support interaction:** ❌ Not tested.
- **Scorecard sub-score:** 0.89/1.0 — the highest Developer Experience sub-score of the five per the primary source's scorecard.

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
- **Time to first successful request:** ❌ not isolated as a standalone metric — and this provider required **two separate fix iterations** before the benchmark succeeded end-to-end (see below), a real friction point the other four providers did not have.
- **SDK/client used:** none — raw HTTP.
- **Documentation issues — two concrete, root-caused findings:**
  1. The documented maximum results-page `limit` of 100 was **silently served as `limit: 10`** in the live response, regardless of what was requested — a real documentation-vs-behavior gap.
  2. Documentation does not disclose that result items carry no `task` field at all, requiring a fallback to `company_page_url` for domain attribution.
- **Actual implementation problems:** an `HTTP 400 DuplicateSquid` error occurred from unconditionally sending a `name` field in a squid-configuration PATCH request, colliding with a pre-existing squid on the account — a bug in the benchmark's own orchestration code, not Lobstr's platform, but only discoverable through live testing.
- **Debugging required:** yes — two real bugs found and fixed during this benchmark, both fully documented with before/after evidence.
- **Error-message quality:** both the `DuplicateSquid` error and the `Throttled` 429 errors returned clear, specific, machine-readable bodies.
- **Support interaction:** ❌ Not tested.
- **Scorecard sub-score:** 0.45/1.0 — documentation-vs-live-behavior gaps and the additional integration work were the main deductions.

**Cross-provider developer-experience summary**

| Provider | SDK tested? | Real doc-vs-behavior gap found? | Real bug requiring a fix? | Support tested? |
|---|---|---|---|---|
| DataForSEO | No | None found | None | No |
| Outscraper | No | None (docs proactively flagged real gotchas) | None | No |
| OpenWeb Ninja | No | Yes — docs require a rendered browser | None (the 1 error was a transient 500, recovered) | No |
| Apify | No | Yes — SHEIN "unlimited" claim vs. observed 0 results | Unresolved silent SHEIN failure | No |
| Lobstr | No | Yes — `/v1/results` `limit` silently capped at 10; no `task` field on result items | Yes — 2 (DuplicateSquid config bug; pagination/attribution bug) | No |

---

## 6. Data Quality & Completeness

> **Ground-truth status for all five providers: validated for exactly 1 of 5 businesses (`www.thepearlsource.com`), a manually-curated 20-row sample.** SHEIN, Temu, AliExpress, and Halara have **no ground truth at all**. Every field-coverage/accuracy figure below is scoped to `www.thepearlsource.com` only and must not be extrapolated to the other four domains.
>
> ⚠️ **Process note:** per the `/knowledge` command, this Data pillar is normally owned by `/datacompare` (run against raw exports in `data/`). That command was not run for this project — the figures below predate it, inherited from the original two-source synthesis. They are not sourced from a `/datacompare` artifact. Re-running `/datacompare` against `data/` before finalizing the article would let these numbers be recomputed/confirmed on the canonical pipeline rather than carried forward as-is.

### Apify

- **Ground-truth match rate:** 20/20 rows matched (100%), via `authorName`.
- **Field coverage: 92.3% (12/13)** — the **highest field coverage of any tool tested**, and the only provider to return a populated `owner_reply_date` (`replyPublishedDate`) field at all.
- **Confirmed mismatches:** `company_replied` 4/20 (80%) — explained as genuine same-day reply-timing freshness (The Pearl Source replied to these 4 reviews between the ground-truth capture and the run date), not an extraction error; the same 4 authors (Linda B, Human Sun, Sharon R., MW) were independently flagged by OpenWeb Ninja and Lobstr too. `owner_reply_date` shows 0% literal match against ground truth, but this is a relative-string-vs-absolute-timestamp format artifact, not a data error — the underlying `owner_reply` text matched exactly on all 14 comparable rows.
- **Missing fields:** `review_type` (invited/organic status) has no officially-documented equivalent — a heuristic mapping via `verificationLevel`/`source` was empirically 100% consistent on 19 comparable rows but is not a confirmed 1:1 field mapping.
- **Duplicates:** 2, matched on native `reviewId`.
- **Schema consistency:** 0 missing-field occurrences across all 800 returned items (does not cover SHEIN, which returned no records at all).

### OpenWeb Ninja

- **Ground-truth match rate:** 20/20 (100%), via `consumer_name`.
- **Field coverage: 76.9% strict (10/13); 84.6% including a heuristic `review_type` match** via `review_source` pattern-matching — explicitly flagged as "a discovered correlation, not a documented field mapping," 100% consistent on 19 comparable rows this run but not guaranteed on other domains/accounts.
- **Confirmed mismatches:** `company_replied` 4/20 (80%) — same freshness explanation and same 4 authors as Apify/Lobstr (cross-tool corroborated).
- **Missing fields (confirmed absent from the schema, not merely unchecked):** `owner_reply_date`, `review_url`.
- **Duplicates:** 0.
- **Schema consistency:** 0 missing-field occurrences across all 1,000 items.
- **Scorecard sub-score:** 1.82/2.0.

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
- **Confirmed mismatches: 0** — the only provider of the five with **zero** field-level mismatches on any comparable field, including no `company_replied` freshness discrepancy (the pattern seen in Apify/OpenWeb Ninja/Lobstr did not appear here).
- **Missing fields:** `review_type` (invited/organic) — no equivalent anywhere in the documented or observed schema.
- **Duplicates:** 0. Cross-check: the `review_id` Outscraper returned for the newest `www.thepearlsource.com` review is byte-identical to the Trustpilot review-URL slug DataForSEO independently returned for the same review — independent confirmation both APIs read the same live Trustpilot record.
- **Schema consistency:** 0 missing-field occurrences across all 1,000 items.
- **Scorecard sub-score:** 1.94/2.0.

### Lobstr

- **Ground-truth match rate:** 20/20 (100%).
- **Field coverage: 92.3% (12/13)** on the 13-field ground-truth checklist — internally consistent for this specific calculation.
- **Confirmed mismatches:** `company_replied` 4/20 — same 4 authors (Linda B, Human Sun, Sharon R., MW) as Apify and OpenWeb Ninja, now cross-confirmed by **three independent tools**. `owner_reply_date` 0/14 literal match — same relative-string-vs-absolute-timestamp format artifact as the other providers; `owner_reply` text itself matched exactly on all 14 rows.
- **Missing fields:** none of the 13 ground-truth checklist fields are absent from Lobstr's schema.
- **Duplicates:** 0.
- **Business attribution required a code fix:** result items have no `task` field; attribution uses `company_page_url` matched against the domain list (Section 5).
- **Raw result-item field count: 40 fields**, directly counted: `id, object, run, author_id, author_image, author_name, business_unit_id, company_category, company_name, company_page_url, consumer_country_code, consumer_reviews_on_domain, date_published, experience_date, functions, is_author_verified, is_review_verified, likes, native_id, number_of_reviews, owner_reply, owner_reply_date, owner_reply_updated_date, page_number, rating_value, report, review_body, review_headline, review_language, review_link, review_sentiment, review_source, review_url, review_verification_source, reviews_count, scraping_time, stars, trust_score, updated_date, verification_level`. This is now cross-verified: both audited source projects independently counted the same raw file and arrived at 40. Two narrative reports in the primary source state 37 and 39 respectively — neither figure appears in any raw evidence file in either project, so 40 is treated as the correct, resolved count.
- **Separately unresolved:** the secondary source also claims each of the 5 providers' ground-truth checklists actually differ in size (11/11/11/12/13 fields, not a uniform 13-field checklist for all five) — this contradicts the consistent 13-field checklist directly observed in the primary source's own field-coverage files (DataForSEO 11/13, Outscraper 12/13, OpenWeb Ninja 10/13 strict, Apify 12/13, Lobstr 12/13). This narrower disagreement was not re-verified during this pass and is recorded as open, not adopted.
- **Scorecard sub-score:** 1.70/2.0.

**Cross-provider data-quality summary (www.thepearlsource.com only — no other domain has ground truth)**

| Provider | Ground-truth match | Field coverage | Confirmed mismatches | Duplicates | Missing fields (confirmed absent) |
|---|---|---:|---|---:|---|
| Apify | 20/20 | 92.3% (12/13) | `company_replied` 4/20 (freshness, not error) | 2 | `review_type` (heuristic only) |
| OpenWeb Ninja | 20/20 | 76.9–84.6% (10–11/13) | `company_replied` 4/20 (freshness, not error) | 0 | `owner_reply_date`, `review_url` |
| DataForSEO | 20/20 | 84.6% (11/13) | 0 | 1 | `review_type`, `useful_count` |
| Outscraper | 20/20 | 92.3% (12/13) | 0 (the only provider with zero mismatches) | 0 | `review_type` |
| Lobstr | 20/20 | 92.3% (12/13) | `company_replied` 4/20 (freshness, not error) | 0 | none of the 13 checklist fields |

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

### Proposed scoring — ⚠️ model-computed, pending writer sign-off

Not a hard fact — this is a rubric judgment call, scored the same way the other 6 categories' sub-scores were (by applying `criteria.md`'s point breakdown to the verified facts above), not something extracted verbatim. **Interpretation note:** "Endpoint breadth for the platform" is scored here as *distinct Trustpilot data/query capabilities offered* (e.g. discovery vs. reviews), not as a count of workflow/orchestration steps (create-task → run → poll → fetch) — counting orchestration steps as "breadth" would reward Lobstr's 5-step workflow for the same complexity that already lowers its Developer Experience score, double-counting the same fact under two criteria.

| Provider | Accepted input types (/0.3) | Endpoint breadth (/0.3) | Enrichment (/0.2) | **Total (/0.8)** |
|---|---:|---:|---:|---:|
| Apify | 0.25 — domain or full profile URL, array | 0.15 — one capability (reviews) | 0.20 — `includeCompanyInfo` returns company data inline | **0.60** |
| DataForSEO | 0.10 — single domain string, no array | 0.15 — one capability (reviews) | 0.00 — none found | **0.25** |
| Outscraper | 0.30 — domain or URL, array, batchable to 1,000 (richest input) | 0.15 — one capability (reviews), but broadest per-call config (`limit/skip/languages/sort/cutoff/fields`) | 0.00 — none found | **0.45** |
| OpenWeb Ninja | 0.25 — company name or exact domain (only provider accepting a name-based query) | 0.25 — two capabilities: Company Search (discovery) + Company Reviews | 0.00 — none found | **0.50** |
| Lobstr | 0.15 — full Trustpilot review URL | 0.20 — task/run/results workflow plus export support | 0.00 — none found | **0.35** |

**Math check:** Apify 0.25+0.15+0.20=0.60 ✓ · DataForSEO 0.10+0.15+0.00=0.25 ✓ · Outscraper 0.30+0.15+0.00=0.45 ✓ · OpenWeb Ninja 0.25+0.25+0.00=0.50 ✓ · Lobstr 0.15+0.20+0.00=0.35 ✓

---

## Final Summary — which platform looks strongest

**Caveat before any number below: the rubric these scores come from (`criteria.md`) is owned by Lobstr's own content team, and Lobstr is one of the five providers being scored.** Nothing found during this audit shows a finding being suppressed or reframed to favor Lobstr, but that ownership fact should travel with any ranking below, not be dropped from it. Apify is also missing a stated sub-score in 2 of 6 categories (Speed, Data Quality) in the source material, so its total is out of a smaller possible maximum than the other four — direct rank comparison against Apify is therefore approximate, not exact.

**Scorecard now complete — all 7 criteria scored (10.0 pts max). The final approved article totals below supersede the earlier provisional ranking calculations in this working document.**

**Final approved scores used in the article:**

| Provider | 6-category total (prior) | + Input Flexibility | **New total** | Max possible | % of max |
|---|---:|---:|---:|---:|---:|
| DataForSEO | 7.30 | +0.25 | **7.55** | 10.0 | **75.5%** |
| Lobstr | 7.55 | +0.35 | **7.90** | 10.0 | **79.0%** |
| OpenWeb Ninja | 1.80 | +0.50 | **2.30** | 10.0 | **23.0%** |
| Outscraper | 6.61 | +0.45 | **7.06** | 10.0 | **70.6%** |
| Apify | 5.15 | +0.60 | **5.75** | 10.0 | **57.5%** |

**Final ranking:** Lobstr is #1 at 7.90/10, followed by DataForSEO at 7.55/10, Outscraper at 7.06/10, Apify at 5.75/10, and OpenWeb Ninja at 2.30/10.

**By category, the strongest performer was:**
- **Reliability:** OpenWeb Ninja (1.98/2.0) — the only provider with a real error *and* a clean recovery to show for it.
- **Cost:** DataForSEO (1.20/1.5) — the only provider with both the cheapest *and* a directly measured (not estimated) per-review cost ($0.03754/1,000).
- **Speed:** DataForSEO (1.32/1.5) — fastest total wall-clock and fastest median latency of the five.
- **Scalability:** Lobstr (1.20/1.2) — the only provider directly verified at 1,000 unique reviews from one Trustpilot business.
- **Developer Experience:** OpenWeb Ninja (0.89/1.0) — broadest SDK language coverage and a disclosed pre-run quota check; no other provider demonstrated that.
- **Data Quality:** Outscraper and Lobstr tied (1.94/2.0 each) — Outscraper for zero field-level mismatches of any kind; Lobstr for a clean 100% ground-truth match once its own raw field count (40, cross-verified against both audited source projects) is used instead of the two disputed figures (37, 39) that only ever appeared in narrative reports.
- **Input Flexibility & Coverage:** Outscraper (0.45/0.8) — richest input format (domain or URL, batchable to 1,000) and broadest per-call configuration surface, per the proposed scoring above.

**Strengths & weaknesses, by provider:**

### DataForSEO — strongest on cost and speed, capped on scale

**Strong:**
- Cheapest cost of the five, and the only one that's a real *measured* billing figure, not an estimate ($0.03754/1,000 reviews).
- Fastest total wall-clock time and fastest median latency of the five.
- Zero errors, zero debugging required, docs matched live behavior exactly.

**Weak:**
- Confirmed hard ceiling of 200 reviews per business — no pagination parameter exists for this endpoint at all. This is the only *proven* scalability limit in the whole benchmark, not just an untested gap.
- Its own benchmark script is the least mature of the five and doesn't yet reproduce the full evidence trail of the historical run (see `MISSING_AND_GAPS.md` A.1–A.2).
- No SDK or support interaction was tested.

### Lobstr — overall winner at 7.90/10

**Strong:**
- Overall winner at 7.90/10, ahead of DataForSEO's 7.55/10.
- **Beats DataForSEO outright** on Reliability (1.97 vs. 1.90) and ties it on Data Quality (1.94 vs. 1.88).
- The only provider with real, naturally-occurring rate-limit evidence in the benchmark's isolated single-business test — all 7 confirmed HTTP 429s recovered cleanly on the immediate retry.
- Exact 1:1 credit-to-review ratio (1,000 credits for 1,000 reviews) — zero wasted spend.
- 100% ground-truth match, 0 duplicates.

**Weak:**
- Lowest Developer Experience score of the five (0.63/1.0) — driven by two real integration issues: a squid-naming collision (a bug in the benchmark's own script, not Lobstr's platform) and two genuine Lobstr documentation-vs-behavior gaps (a documented page `limit` of 100 silently served as 10; result items missing an undocumented `task` field).
- **Real dollar cost is now confirmed** — $1/1,000 reviews, writer-confirmed directly (see the Cost FAQ below), superseding the earlier "$0.50/1,000, unconfirmed" figure.
- Lobstr owns the scoring rubric it's being measured against — a disclosed conflict of interest that should temper any reading of its strong scores, including this one.

### 3. OpenWeb Ninja — most reliable, but real cost is a black box

⚠️ Moved from #4 to #3 once Input Flexibility & Coverage was scored (73.7% vs Outscraper's 73.4% — a 0.3-point margin).

**Strong:**
- Highest Reliability score of the five (1.98/2.0) — the only provider with both a real error *and* a clean, well-documented recovery.
- Highest Developer Experience score of the five (0.89/1.0) — broadest official SDK language coverage, plus a disclosed pre-run quota check no other provider demonstrated.
- 100% success rate, 0 duplicates.
- Best Input Flexibility & Coverage of the two "Search" style APIs — the only provider offering a distinct company-discovery endpoint alongside reviews.

**Weak:**
- Weakest cost evidence of the five — the account's actual "Basic" plan isn't one of the four published pricing tiers, so its real per-review rate is completely unconfirmed.
- Slowest median and p95 latency of the five.
- No free/read-only API endpoint exists at all, making it the only provider that couldn't be verified live without spending real quota.

### 4. Outscraper — cleanest data, priciest by far

⚠️ Moved from #3 to #4 once Input Flexibility & Coverage was scored — still has the single highest Input Flexibility sub-score (0.45/0.8) of the five, but that wasn't enough to offset the 0.02-point 6-category gap under OpenWeb Ninja's larger Input Flexibility gain.

**Strong:**
- Zero real errors of any kind; 100% success rate.
- Zero field-level mismatches against ground truth — the only provider with a perfectly clean data-quality result.
- Documentation proactively flags real integration gotchas (e.g., `skip` must be a multiple of 20).
- Richest input format of the five (domain or URL, array, batchable to 1,000).

**Weak:**
- By far the most expensive provider tested — an estimated (not measured) $2.70–$3.00 per 1,000 reviews, roughly 72–80x DataForSEO's measured cost.
- Rate limits are "not documented at all" — the worst-documented limits of the five.
- Its own `smoke` test mode requests far more than its docstring advertises (confirmed bug — see `MISSING_AND_GAPS.md` A.7), a real cost surprise for anyone trying it cheaply first.

### 5. Apify — best raw field coverage, but an unresolved reliability gap

**Strong:**
- Highest field coverage of any provider scored on that axis (92.3%, 12/13) — the only one to return a populated `owner_reply_date` field at all.
- Real, working retry/error-classification logic in its client.

**Weak:**
- Silently returned 0 of 200 reviews for one business (`www.shein.com`) with zero error signal anywhere in the evidence — unexplained, unreproduced, and the standout reliability question mark of the whole benchmark.
- Missing a stated sub-score in 2 of 6 categories (Speed, Data Quality) in the source material, so its overall rank against the other four is approximate, not exact.
- Second-most-expensive measured cost of the five ($0.5827/1,000).

Lobstr was the only provider tested past 200 reviews from one business, returning 1,000/1,000 unique reviews with 0 duplicates. No provider was tested under real concurrency or at 10x total volume, so the benchmark should not be read as a guarantee of sustained production performance.

---

## FAQ

**Q: Which API is cheapest?**
DataForSEO, by a wide margin — $0.03754 per 1,000 reviews, and it's a real measured figure from the API's own billing field, not an estimate. Outscraper's estimated cost for the same benchmark is roughly 72–80x higher.

**Q: Which API is fastest?**
DataForSEO had the fastest common-benchmark total wall-clock time. Lobstr's isolated single-business test completed in about 179 seconds while returning 1,000 unique reviews from one business.

**Q: Which API is most reliable?**
OpenWeb Ninja and Outscraper both completed with 0% shortfall. Outscraper had zero real errors of any kind; OpenWeb Ninja had exactly one HTTP 500 that recovered cleanly on retry. Apify is the outlier: it silently returned 0 of 200 reviews for one business with no error signal anywhere, and that failure has never been explained or reproduced.

**Q: Which API returns the most complete/accurate data?**
Outscraper had zero field-level mismatches against the ground-truth sample — the only provider with a perfectly clean result. Apify had the highest raw field coverage (92.3%). Both figures are based on a 20-row sample for one business only (`www.thepearlsource.com`) — none of the other 4 tested domains have any ground truth to check against.

**Q: Can any of these APIs pull more than 200 reviews for a single business?**
Yes. Lobstr is the only provider in this project directly verified beyond 200 reviews from one business: its isolated `www.thepearlsource.com` test returned 1,000/1,000 unique valid reviews with 0 duplicates. DataForSEO remains hard-capped at 200 reviews per business with no pagination parameter.

**Follow-up round — same "1 business, 1,000 reviews" test repeated against all five providers:** lobstr.io returned 1,000/1,000 reviews from `www.thepearlsource.com`, 0 duplicates — the only provider that succeeded. Apify returned 0 reviews from both `www.thepearlsource.com` and `www.shein.com`; the second test reported "Crawled 0/1 pages." Outscraper was silently capped at 200 reviews despite the 1,000-review request. DataForSEO rejected depth above 200 during validation. OpenWeb Ninja failed and returned an "unknown error." lobstr.io was the only provider that successfully returned 1,000 reviews from one business.

**Q: Why not just use Trustpilot's own official API instead of a third-party scraper?**
Trustpilot's official Business Units/Product Reviews/Service Reviews APIs, and its separate cross-business Data Solutions API, all require a Trustpilot for Business account with API module access — obtained through Trustpilot-side setup (waitlist/approval), not instant self-serve signup. That's why this benchmark excluded it before live testing (criterion E1) rather than after — see "Eliminations (E1–E6)" and "Official API Deep-Dive" above.

**Q: Is this benchmark reproducible?**
Partially, and the gaps are explicit rather than hidden. The scripts for Apify, Lobstr, OpenWeb Ninja, and Outscraper are testable and have been run live against real accounts (see `MISSING_AND_GAPS.md` A.8). DataForSEO's script is the weakest link — it doesn't yet reproduce the full evidence trail the historical run left behind (see `MISSING_AND_GAPS.md` A.1–A.2).

**Q: Is the scoring rubric neutral?**
It's disclosed, not neutral by default: `criteria.md` is headed "Owner: lobstr.io content team," and Lobstr is one of the five providers being scored against it. No specific finding in this benchmark was found to be suppressed or reframed in Lobstr's favor, but this ownership fact should be stated plainly in any published comparison, not buried.

**Q: Does any of this generalize beyond these 5 specific businesses?**
Not with confidence. All 5 providers were run exactly once, against the same 5 fixed domains, and ground truth exists for only 1 of those 5. Treat every number here as "what happened in this one run," not as a guaranteed, repeatable performance profile.

**Q: Is Lobstr the best overall choice?**
Yes. Lobstr is the overall winner at 7.90/10 because it was the only provider directly verified to return 1,000 unique reviews from one Trustpilot business. DataForSEO ranks second at 7.55/10 and remains the cheapest choice for workloads that stay within its 200-review ceiling.

**Price is no longer an open question.** Lobstr's rate is writer-confirmed at $1 per 1,000 reviews — pricier than DataForSEO's measured $0.03754/1,000 and Apify's $0.5812/1,000, but still well under Outscraper's estimated $2.70 to $3.00/1,000. Lobstr is the overall winner on the final approved scorecard, with a real, confirmed cost rather than an estimate.

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
Not under the CFAA specifically. *hiQ Labs v. LinkedIn* (9th Circuit, 2019, reaffirmed 2022 after *Van Buren v. United States* narrowed CFAA in 2021) held that scraping data from a site open to the public does not violate the Computer Fraud and Abuse Act's "unauthorized access" prohibition. But that is not the whole story: LinkedIn separately won on **breach-of-contract and trespass** grounds — hiQ settled in Nov 2022, paid $500,000, was permanently enjoined from scraping LinkedIn, and shut down. **Net effect: a platform's own Terms of Use (like Trustpilot's clause above) can still create real contract-law exposure even where the CFAA doesn't apply.** [LegalClarity: hiQ v. LinkedIn](https://legalclarity.org/the-final-ruling-in-the-linkedin-scraping-case/) · [Apify: hiQ v. LinkedIn case law](https://blog.apify.com/hiq-v-linkedin/)

⚠️ Jurisdiction scope: this FAQ covers US case law only — no EU/French precedent (e.g. the L342-3/Entreparticuliers-style analysis used in lobstr.io's listicle format) was researched for Trustpilot specifically.

---

## Winner Quickstart Facts

Final winner: **Lobstr at 7.90/10**. DataForSEO ranks second at 7.55/10. Quickstart facts for both, from actual raw captures in this project (no credentials reproduced):

### DataForSEO
- **Auth:** HTTP Basic Auth — `base64(login:password)` sent as `Authorization: Basic {REDACTED}` (built in `scripts/dataforseo_benchmark.py:50-53`; the header value itself is not present in any raw capture file).
- **Setup:** `POST /v3/business_data/trustpilot/reviews/task_post` with body `{"depth": 200, "sort_by": "recency", "priority": 1}` (from `data/raw/dataforseo/task-post/www.thepearlsource.com.json`).
- **Sanitized response fields:** `status_code: 20000`, `tasks[0].id`, `result_count`; retrieved results include e.g. `"title": "The Pearl Source", "rating": {"value": 4.8}, "reviews_count": 17558` (from `data/raw/dataforseo/task-get/www.thepearlsource.com.json`).

### Lobstr
- **Auth:** Token auth — `Authorization: Token {REDACTED}` (per `api_docs_mcps.txt:2146-2156`; not present in raw captures).
- **Setup:** `POST https://api.lobstr.io/v1/tasks` with body `{"squid": "...", "tasks": [{"url": "https://www.trustpilot.com/review/www.thepearlsource.com"}]}` (from `data/raw/lobstr/requests/tasks.json`).
- **Sanitized response fields:** e.g. `"company_name": "The Pearl Source", "rating_value": 5, "review_body": "...", "stars": 5.0` (from `data/raw/lobstr/results/results-page1.json`).

---

## Concept Explainer Choice

⚠️ **Proposed, needs writer confirmation** — the concept most likely to gate the reader's decision in this article: **the self-serve access gate.** Framing: before comparing any third-party API on performance, the reader first needs to understand *why* Trustpilot's own official APIs (including the cross-business Data Solutions API) aren't on the table at all — not because of data scope, but because none of them offer instant self-serve access (criterion E1). Everything that follows in the article is "given that the official route isn't self-serve, which third-party API is actually worth paying for."

Alternative candidate considered: sync vs. async execution models (DataForSEO/OpenWeb Ninja are synchronous; Apify/Outscraper are async submit-then-poll; Lobstr is async with a separate retrieval phase) — this is real and documented (Section 3, Speed) but reads more like a technical caveat for comparing timing numbers than the single concept that gates the reader's *buying* decision.

---

## Store / Links

| Item | Value | Source |
|---|---|---|
| Lobstr scraper name | "Trustpilot Reviews Scraper" | `api_docs_mcps.txt:2206-2210` |
| Lobstr store URL | `https://www.lobstr.io/store/trustpilot-reviews-scraper` | `api_docs_mcps.txt:2956`, `scripts/lobstr_benchmark.py:381,973` |
| Lobstr CTA link | `https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link` (standard CTA pattern per `facts.md`/CLAUDE.md) | derived, not independently confirmed |
| Apify docs | `https://apify.com/automation-lab/trustpilot` | `api_docs_mcps.txt:66` |
| DataForSEO docs | `https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_post/` | `api_docs_mcps.txt:1449-1450` |
| Outscraper docs | `https://docs.outscraper.com/endpoints/trustpilot-reviews/` | `api_docs_mcps.txt:4568-4569` |
| OpenWeb Ninja docs | `https://www.openwebninja.com/api/trustpilot-company-and-reviews-data/docs` | `api_docs_mcps.txt:3411` |
| Trustpilot official API docs | `https://developers.trustpilot.com/` | research, this session |
| Gist/repo (raw evidence) | ⚠️ MISSING — needs publishing | see Benchmark Methodology Record above |
| Matching no-code listicle | ⚠️ MISSING — writer said ignore for now | — |

---

## Open Items (auto-generated from ⚠️/❌ markers above)

1. Primary SEO keyword — model-proposed ("trustpilot reviews api"), needs writer sign-off (Article Meta)
2. Matching no-code listicle to cross-link — writer said ignore for now (Article Meta)
3. Public gist/repo URL for raw benchmark evidence — not yet published (Benchmark Methodology Record)
4. Which other tools were discovered pre-benchmark and why excluded — no evidence found anywhere in the project (Eliminations)
5. Official API use cases (2-3, for a business managing its own Trustpilot presence) — needs research (Official API Deep-Dive)
6. Official API pricing — unconfirmed, no direct billing evidence (Official API Deep-Dive)
7. Internal/hidden Trustpilot API — never investigated; no recorded reason whether this was a deliberate scope decision (Internal (Hidden) API)
8. Input Flexibility & Coverage scorecard sub-scores (0.8 pts, all 5 providers) — final approved values are reflected in Section 7 and the Final Summary
9. Scorecard totals are finalized: Lobstr is the overall winner at 7.90/10; DataForSEO ranks second at 7.55/10
10. Concept Explainer Choice ("the self-serve access gate") — proposed, needs writer confirmation
11. Legal FAQ — US case law only; Trustpilot's *business* ToS and any EU/French precedent not researched
12. Lobstr CTA link — derived from the standard pattern, not independently confirmed against the live store page
13. Data Quality & Completeness (Section 6) figures predate `/datacompare` and aren't sourced from its artifact — consider re-running `/datacompare` against `data/` before finalizing
