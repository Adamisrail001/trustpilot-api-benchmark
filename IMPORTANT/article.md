# Best Trustpilot Reviews API for Scraping Data at Scale [2026 Benchmark]

I benchmarked 5 Trustpilot review APIs and ran an additional isolated single-business scale test. **lobstr.io is the overall winner at 7.90/10** and was the only provider verified to return 1,000 unique reviews from one Trustpilot business. DataForSEO ranks second at 7.55/10 and is hard-capped at 200 reviews per business.

> **Best overall: lobstr.io (7.90/10).** In an isolated test against `www.thepearlsource.com`, it returned 1,000/1,000 unique valid reviews from that single business, with 0 duplicates, in about 179 seconds. The run consumed exactly 1,000 credits, paged through 101 result pages, and stopped with `no_next_page` only after collecting the full target.

## 15-second summary

- The pain: Trustpilot's official cross-business route is not self-serve, while several third-party APIs stop at or around 200 reviews per business
- The method: 5 APIs were benchmarked using live requests, and lobstr.io received an additional isolated test requesting 1,000 reviews from one business
- **[lobstr.io](https://lobstr.io)** (7.90/10) - overall winner and best for scale; 1,000/1,000 unique reviews from one business, 0 duplicates, about 179 seconds, and exactly 1,000 credits consumed
- **DataForSEO** (7.55/10) - second overall; cheapest measured cost and fastest common-benchmark run, but hard-capped at 200 reviews per business
- **Outscraper** (7.06/10) - completed the 1,000-review common benchmark with zero data-quality mismatches, but at the highest estimated cost
- **Apify** (5.75/10) - richest field coverage where data landed, but silently returned 0/200 on the ground-truth business
- **OpenWeb Ninja** (2.3/10) - returned 0/1,000 reviews in the latest verified rerun

| API | Pricing | Type | Benchmark score | Best for | Main limitation |
|---|---|---|---:|---|---|
| lobstr.io | Confirmed $1/1K | Third-party, async run + retrieval | **7.90/10** | **Overall winner; scale beyond 200 reviews per business** | Pricier than DataForSEO and Apify; results endpoint served 10/page |
| DataForSEO | Measured $0.03754/1K | Third-party, sync task/result | 7.55/10 | Lowest measured cost and fast turnaround | Hard 200-reviews-per-business ceiling, no pagination |
| Outscraper | Estimated $2.70-$3.00/1K (not measured) | Third-party, async submit + poll | 7.06/10 | Validated data accuracy | Highest estimated cost; rate limits undocumented |
| Apify | Measured $0.5812/1K | Third-party, async Actor run | 5.75/10 | Broad field coverage where data lands | Silently returned 0/200 reviews for one business |
| OpenWeb Ninja | Account's real Basic-plan rate unconfirmed | Third-party, sync page-by-page | 2.3/10 | Not recommended in its latest verified state | Returned 0/1,000 reviews; retries exhausted |
| Trustpilot Official API (+ Data Solutions) | Not published | Official, mixed public/OAuth | N/A | Own review data, invitations, and widgets | No self-serve cross-business access within 48 hours |

## Introduction

Scraping Trustpilot reviews at scale is harder than it looks. Many self-serve APIs appear reliable until you try to collect larger datasets.

Some stop at 200 reviews per business with no pagination, while others return incomplete results or report success without delivering the requested data.

To find which options actually work, I tested five self-serve Trustpilot review APIs against the same businesses and review targets, logging every request, response, timing, and cost. You can review the full test scripts and raw evidence in the [benchmark repository](https://github.com/Adamisrail001/trustpilot-api-benchmark).

## Why not use the official Trustpilot API?

### Does Trustpilot offer a reviews API?

Yes, but not one built for pulling someone else's reviews at scale. Trustpilot's for-business platform exposes half a dozen APIs under one umbrella: the **Business Units API** (a business's own rating, review count, distribution, and public profile info), the **Service Reviews API** and **Product Reviews API** (retrieving and managing reviews tied to your own service or product catalog), the **Invitations API** (triggering review-request emails after a purchase), and the **Data Solutions API** - a separate, less-known product that returns business profiles and review data across **any** business on Trustpilot, not just your own.

That last one is the only official route built for a competitor-monitoring use case. The rest are for a business managing its own review presence: embedding a rating widget, pulling your own reviews into a CRM, replying to reviews, or inviting a customer to leave one. None of them let you point at a competitor's storefront and pull their reviews at scale, and none of them were designed to.

Even for your own business, the public reviews endpoint doesn't hand back everything the rendered review page shows:

| Field | Visible on the Trustpilot page | Official public API |
|---|---|---|
| Review text | Yes | Yes |
| Star rating | Yes | Yes |
| Review date | Yes | Yes |
| Reviewer display name | Yes | Yes |
| Verified/invited badge | Yes | Yes (verification status) |
| Company reply text + date | Yes | Yes |
| Reviewer country/location | Yes | Yes |
| Reviewer's own review count | Yes | Not documented on this endpoint |
| "Useful" vote count | Yes | Separate endpoint only (`/v1/reviews/{reviewId}/likes`), not bundled with the review |
| Customer email / order reference | No, never shown | Private endpoint only, OAuth-gated, not on the public one |

The limitation that matters here isn't what these APIs can technically return, it's who's allowed to ask for it, and how fast. Covered next.

**How to access it:** every route starts the same way: a Trustpilot for Business account with **API module access**, requested through [business.trustpilot.com/request-demo](https://business.trustpilot.com/request-demo). Trustpilot's own onboarding docs don't describe a self-serve signup form or a published price, just a demo-request gate. Once that's granted, your API Key (Client ID) and Secret live under the Integrations tab of your account.

From there, access splits into two tiers:

- **Public endpoints** (Business Units profile info, public reviews, review summaries) authenticate with a simple `apikey` header, no OAuth required
- **Private endpoints** (your own private review data, invitations, anything writing back to your account) require full OAuth 2.0: Authorization Code or Client Credentials grant, an access token that expires after 100 hours, a refresh token good for 30 days

The **Data Solutions API**, the one cross-business option, sits behind its own separate gate: submit a contact request on [Trustpilot's Data Solutions page](https://business.trustpilot.com/datasolutions), wait for a sales rep to reach out, then generate an API key from the Data Solutions web app once your account exists. No instant key, no self-serve dashboard signup, at any tier.

That's the wall this benchmark's own E1 criterion (no self-serve access within 48 hours) can't get past: not the data these APIs are able to return, but the demo call and/or sales contact form standing between "I want a key" and "I have a key." Every official route requires business verification and access approval before a key is issued, which is why none of it was live-tested here, not because anything broke mid-benchmark.

**How to use it:** assuming you clear that wall, here's what each endpoint looks like in practice, per use case. (Requests and response shapes below are built from Trustpilot's own documented parameters and fields; this benchmark never obtained a working key, official or Data Solutions, so none of it was live-tested.)

**Embed your own rating** (Business Units API, public, `apikey` header):

```bash
curl "https://api.trustpilot.com/v1/business-units/{businessUnitId}/profileinfo" \
  -H "apikey: YOUR_API_KEY"
```

Returns company name, contact info, address, description, social links, and verification status. No review-level data.

**Pull your own service reviews** (Service Reviews API, public):

```bash
curl "https://api.trustpilot.com/v1/reviews/latest?count=20&language=en" \
  -H "apikey: YOUR_API_KEY"
```

Returns the review ID, star rating, text, consumer display name, and language for each of the most recent reviews.

**Pull your own product reviews** (Product Reviews API, public):

```bash
curl "https://api.trustpilot.com/v1/product-reviews/business-units/{businessUnitId}/reviews?sku=YOUR_SKU" \
  -H "apikey: YOUR_API_KEY"
```

Returns review ID, star rating, content, creation date, and consumer name, filtered by SKU or product URL.

**Send a review invitation** (Invitations API, private, OAuth Bearer token):

```bash
curl -X POST "https://invitations-api.trustpilot.com/v1/private/business-units/{businessUnitId}/email-invitations" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "consumerEmail": "customer@example.com",
    "consumerName": "Jane Doe",
    "referenceId": "order-1234",
    "locale": "en-US"
  }'
```

Triggers an email invite from Trustpilot's own template; a separate endpoint generates a shareable invitation link instead of sending an email directly.

**Pull another business's reviews** (Data Solutions API, sales-gated, `apikey` header):

```bash
curl "https://datasolutions.trustpilot.com/v1/business-units/search?query=thepearlsource" \
  -H "apikey: YOUR_API_KEY"
```

Returns matching business unit IDs, display names, country codes, TrustScore, and review counts; a second call, `GET /v1/business-units/{id}/reviews`, pulls that business's actual review text. This is the one official endpoint built for exactly this benchmark's use case, someone else's reviews, not your own. It just isn't reachable inside a 48-hour self-serve window, which is why the official API was excluded during pre-screening, before any live test ran against the five third-party APIs below.

**Verdict:** the official API is the right tool if you run the business being reviewed and want invitations, widgets, or your own review data in a dashboard. It's the wrong tool the moment you need someone else's Trustpilot data on a self-serve timeline, which is exactly the gap the five third-party APIs in this benchmark are built to fill.

Docs (checked 2026-07-31): [developers.trustpilot.com](https://developers.trustpilot.com/) · [Authentication overview](https://developers.trustpilot.com/authentication/) · [Business Units API](https://developers.trustpilot.com/business-units-api) · [Data Solutions API](https://developers.trustpilot.com/data-solutions-api/)

## The internal (hidden) API

Trustpilot review pages expose an undocumented internal endpoint that can return structured review data without rendering the full page.

It is not a dependable production option. Its changing build identifier must be rediscovered after site deployments, the route is unsupported, and larger-volume use remains exposed to anti-bot controls, rate limits, and maintenance breakage.

For this benchmark, I therefore focused on self-serve third-party APIs that handle that infrastructure behind a documented interface.

## How I tested

I tested the APIs against the following weighted criteria and gave each provider a score:

| Criterion | Weight | What it measures |
|---|---:|---|
| Success Rate & Reliability | 2.0 | Completion rate, empty or partial responses, error handling, and stability |
| Data Quality & Completeness | 2.0 | Field coverage, accuracy, schema consistency, and freshness |
| Cost Efficiency | 1.5 | Cost per 1,000 successful records, billing fairness, and pricing transparency |
| Speed & Throughput | 1.5 | Total runtime, latency, and async availability |
| Scalability | 1.2 | Review limits, pagination, rate limits, and larger-volume performance |
| Developer Experience | 1.0 | Setup time, documentation quality, SDKs, and error clarity |
| Input Flexibility & Coverage | 0.8 | Supported inputs, batching options, exports, and endpoint coverage |

Most APIs found during research were disqualified before live testing. Only five made the final cut.

Each finalist was tested with live requests, and its responses, timing, errors, and costs were recorded. Here are the findings and detailed reviews.

## Best Trustpilot Reviews API: lobstr.io

[lobstr.io](https://lobstr.io) is the highest-scoring provider in this benchmark at **7.90/10**. It wins because it was the only API directly verified to return 1,000 unique reviews from one Trustpilot business, solving the scale requirement at the center of this article.

In the isolated `www.thepearlsource.com` run, lobstr.io returned 1,000/1,000 unique valid reviews with 0 duplicates and 1,000 unique Trustpilot review IDs. It completed in about 179 seconds, consumed exactly 1,000 credits, paged through 101 result pages, and stopped with `no_next_page` after reaching the requested target.

**Scorecard** (7.90/10, band: Strongest overall for scale)

| Criterion | Score | Rating |
|---|---:|---|
| Success Rate & Reliability | 1.80/2.0 | ★★★★★ |
| Data Quality & Completeness | 1.70/2.0 | ★★★★ |
| Cost Efficiency | 1.05/1.5 | ★★★★ |
| Speed & Throughput | 1.35/1.5 | ★★★★★ |
| Scalability | 1.20/1.2 | ★★★★★ |
| Developer Experience | 0.45/1.0 | ★★★ |
| Input Flexibility & Coverage | 0.35/0.8 | ★★★ |
| **Total** | **7.90/10** | **Overall winner** |

![lobstr.io credits-before.json and credits-after.json showing a 0-to-1000 consumed delta matching the Run object's credit_used field](https://d37gzvgyugjozl.cloudfront.net/thumbnail_lobstr_credits_before_after_dc99468b01.png?updatedAt=2026-07-31T10%3A49%3A01.977Z)

**Pros and cons**

| Pros | Cons |
|---|---|
| Only provider verified at 1,000 unique reviews from one business | Confirmed $1/1,000 is higher than DataForSEO and Apify |
| Returned 1,000/1,000 with 0 duplicates | Documented `limit=100` was served as 10 results per page |
| Completed the isolated scale test in about 179 seconds | Result items did not include a `task` field for direct attribution |
| Exact 1:1 credit accounting confirmed by before/after balance data | Benchmark integration required fixes before completing end to end |
| Recovered all 7 confirmed HTTP 429 events without losing records | No SDK was tested in this benchmark |

**Performance per criterion**

> **Criterion 1: Success Rate & Reliability (1.80/2.0)**
> - **How it was tested:** a new isolated Squid targeted only `www.thepearlsource.com`, with `max_results` and `max_unique_results_per_run` set to 1,000.
> - **Findings:** 1,000/1,000 unique reviews returned, 0 duplicates, and 0 records lost. Seven confirmed HTTP 429 responses occurred during retrieval, and every one recovered on the immediate retry.
> - **Verdict:** full completion with successful recovery from real rate-limit events.
> - **Evidence:** [lobstr.io benchmark script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/lobstr_benchmark.py) · [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 2: Data Quality & Completeness (1.70/2.0)**
> - **How it was tested:** output was checked against the manually verified 20-row ground-truth sample for `www.thepearlsource.com` and the pooled field comparison.
> - **Findings:** ground-truth field coverage was 92.3%. The observed differences were mainly normalization or freshness issues, including a review-date offset and a review ID returned where a complete review URL was expected.
> - **Verdict:** strong field coverage with minor normalization work required.
> - **Evidence:** [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 3: Cost Efficiency (1.05/1.5)**
> - **How it was tested:** the Run object's `credit_used` value was checked against separate before-and-after credit snapshots.
> - **Findings:** consumption moved from 0 to 1,000 credits for 1,000 reviews, confirming a 1:1 ratio and a measured cost of $1 per 1,000 reviews.
> - **Verdict:** transparent and directly measured, but more expensive than DataForSEO and Apify.
> - **Evidence:** [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 4: Speed & Throughput (1.35/1.5)**
> - **How it was tested:** wall-clock time was measured from the start of the isolated run through final result retrieval.
> - **Findings:** 1,000 unique reviews from one business were collected in about 179 seconds.
> - **Verdict:** near the fastest result in the benchmark while handling five times DataForSEO's proven per-business depth.
> - **Evidence:** [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 5: Scalability (1.20/1.2)**
> - **How it was tested:** one Trustpilot business was requested at a depth of 1,000 reviews rather than spreading the target across five businesses.
> - **Findings:** lobstr.io returned the complete 1,000-review target with 0 duplicates. No 200-review ceiling was encountered, and retrieval continued until `no_next_page` after the full target was collected.
> - **Verdict:** the strongest directly verified per-business scalability result in this project.
> - **Evidence:** [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 6: Developer Experience (0.45/1.0)**
> - **How it was tested:** the benchmark was integrated through raw HTTP requests from Squid setup to result export.
> - **Findings:** the benchmark script initially sent a conflicting Squid name, while the live `/v1/results` endpoint served 10 results per page despite documentation allowing a higher limit. Result items also lacked a direct `task` field.
> - **Verdict:** workable and automatable, but the documentation-to-live-behavior gaps added integration work.
> - **Evidence:** [lobstr.io benchmark script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/lobstr_benchmark.py) · [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

> **Criterion 7: Input Flexibility & Coverage (0.35/0.8)**
> - **How it was tested:** task creation, multi-task Squid behavior, result retrieval, and CSV/JSON export options were reviewed.
> - **Findings:** business URLs can be added as tasks, results can be exported, and runs expose progress fields. Direct result-to-task attribution required falling back to `company_page_url`, and no enrichment endpoint or SDK was tested.
> - **Verdict:** enough flexibility for repeatable scraping pipelines, with room for a broader developer surface.
> - **Evidence:** [lobstr.io benchmark results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

## Getting started with lobstr.io: quickstart

lobstr.io uses token authentication through the `Authorization: Token` header.

```python
import time
import requests

TOKEN = "YOUR_TOKEN"
SQUID_ID = "YOUR_SQUID_ID"

headers = {
    "Authorization": f"Token {TOKEN}",
    "Content-Type": "application/json",
}

# 1. Add a Trustpilot business as a task
task_response = requests.post(
    "https://api.lobstr.io/v1/tasks",
    headers=headers,
    json={
        "squid": SQUID_ID,
        "tasks": [
            {
                "url": "https://www.trustpilot.com/review/www.thepearlsource.com"
            }
        ],
    },
    timeout=30,
)
task_response.raise_for_status()

# 2. Start the Squid run
run_response = requests.post(
    f"https://api.lobstr.io/v1/squids/{SQUID_ID}/start-run",
    headers=headers,
    timeout=30,
)
run_response.raise_for_status()
run = run_response.json()
run_id = run["id"]

# 3. Poll until the run is complete
while True:
    status_response = requests.get(
        f"https://api.lobstr.io/v1/runs/{run_id}",
        headers=headers,
        timeout=30,
    )
    status_response.raise_for_status()
    state = status_response.json()

    if state.get("status") in {"done", "succeeded"}:
        break
    if state.get("status") in {"failed", "error"}:
        raise RuntimeError(f"lobstr.io run failed: {state}")

    time.sleep(5)

print(state)
```

![lobstr.io pagination-report.json showing the documented limit=100 silently served as 10](https://d37gzvgyugjozl.cloudfront.net/thumbnail_lobstr_limit_10_vs_100_e2550650d9.png?updatedAt=2026-07-31T11%3A09%3A51.155Z)

After the run finishes, page through the results endpoint until no next page remains. The live test served 10 results per page, so a 1,000-review run required about 100 result pages.

```json
{
  "company_name": "The Pearl Source",
  "rating_value": 5,
  "review_body": "...",
  "stars": 5.0,
  "date_published": "2026-07-19T06:35:54",
  "company_page_url": "https://www.trustpilot.com/review/www.thepearlsource.com"
}
```

**Progress tracking:** poll the run object's `total_results` and `total_unique_results` fields.  
**Attribution:** when multiple businesses share one Squid, match results using `company_page_url`.  
**Automation:** use the built-in CSV/JSON export flow or connect scheduled exports to Sheets, S3, or another data pipeline.

![lobstr.io's run history showing completed runs returning 1,000 of 1,000 unique results for 1,000 credits](https://d37gzvgyugjozl.cloudfront.net/thumbnail_lobster_evedense_fcea974188.png?updatedAt=2026-07-31T11%3A12%3A33.888Z)

Store: [lobstr.io Trustpilot Reviews Scraper](https://www.lobstr.io/store/trustpilot-reviews-scraper#cta-link)

Want me to build a Trustpilot monitoring pipeline around this API for your own use case? Find me on [LinkedIn](https://pk.linkedin.com/in/shehriar-ahmad-awan).

## Runners-up: full benchmark results

| Rank | API | Score | Top strength | Main weakness |
|---:|---|---:|---|---|
| 2 | DataForSEO | 7.55/10 | Lowest measured cost and fastest common-benchmark run | Hard cap of 200 reviews per business |
| 3 | Outscraper | 7.06/10 | Zero data-quality mismatches on the validated sample | Highest estimated cost |
| 4 | Apify | 5.75/10 | Broadest field coverage where data lands | Silent 0/200 result on the ground-truth business |
| 5 | OpenWeb Ninja | 2.3/10 | Clear structured error responses | Returned 0/1,000 in the latest verified rerun |

### DataForSEO: Best for low-cost jobs under 200 reviews

DataForSEO scored **7.55/10** and ranks second overall. It returned 999 unique reviews from the 1,000-review common benchmark, with one provider-side duplicate and no request errors. Its measured cost was $0.03754 per 1,000 successful reviews, and its total wall-clock time was 165,513 ms, the fastest common-benchmark result.

Its limitation is decisive for scale: the Trustpilot endpoint has no `page`, `offset`, `skip`, or `cursor` parameter, so 200 reviews per business is a hard ceiling. It is the strongest choice when cost matters and the workload is guaranteed to remain below that limit.

![DataForSEO cost-report.json showing $0.03754 per 1,000 successful reviews](https://d37gzvgyugjozl.cloudfront.net/thumbnail_dataforseo_cost_report_26fde1f751.png?updatedAt=2026-07-31T11%3A06%3A05.252Z)

Docs: [DataForSEO Trustpilot Reviews API](https://docs.dataforseo.com/v3/business_data-trustpilot-reviews-task_post/)

### Outscraper: Best for validated data accuracy

Outscraper scored **7.06/10**. It completed 1,000/1,000 reviews across five businesses, returned 0 duplicates, and produced zero field-level mismatches against the validated ground-truth sample.

Its estimated cost of $2.70 to $3.00 per 1,000 reviews was the highest in this comparison, and its rate limits were not documented. Its 1,000-review result was distributed across five businesses; it was not tested at 1,000 reviews from one business.

### Apify: Best field coverage where results complete

Apify scored **5.75/10** and returned the broadest field set where data landed. However, `www.thepearlsource.com`, the only business with a manually verified ground-truth sample, returned 0/200 reviews while the Actor still reported a successful terminal status.

The latest run therefore completed only 800/1,000 requested reviews. Its measured cost was $0.5812 per 1,000 successful reviews.

### OpenWeb Ninja: Not recommended in its latest verified state

OpenWeb Ninja scored **2.3/10**. Its SDK coverage and structured error responses were positives, but the most recent verified benchmark returned 0/1,000 reviews after sustained HTTP 429 responses exhausted the retry logic.

The provider's account was also above its available quota during the latest evidence pass, so the result reflects the tested account state rather than a universal claim about every plan.

## Best Trustpilot APIs by use case

| Use case | Provider | Why |
|---|---|---|
| Best overall and more than 200 reviews from one business | **lobstr.io** | Only provider directly verified at 1,000 unique reviews from one Trustpilot business |
| Lowest measured cost | DataForSEO | $0.03754 per 1,000 successful reviews |
| Fastest common-benchmark run | DataForSEO | 165,513 ms total wall-clock |
| Zero data-quality mismatches on the validated sample | Outscraper | Cleanest field-level result against ground truth |
| Broadest field coverage where data lands | Apify | Richest returned schema, despite an incomplete run |
| Provider to avoid based on the latest verified run | OpenWeb Ninja | 0/1,000 reviews after retries were exhausted |

## Concept explainer: the self-serve access gate

Before comparing any third-party API on performance, it's worth understanding why Trustpilot's own official APIs, including the cross-business Data Solutions API, aren't on this list at all. It isn't about data scope; the Data Solutions API can technically pull reviews across businesses. It's about access: none of Trustpilot's official routes offer instant self-serve signup.

| API / route | Self-serve signup | Access path | On this list? |
|---|---|---|---|
| Trustpilot Business Units / Product / Service Reviews API | No | Trustpilot for Business account + API module approval | No, excluded pre-benchmark (E1) |
| Trustpilot Data Solutions API | No | API key, gated behind sales contact + approval | No, excluded pre-benchmark (E1) |
| DataForSEO, Outscraper, OpenWeb Ninja, Apify, lobstr.io | Yes | API key or token, live within minutes | Yes, all 5 tested live |

Everything in this article is really answering one question: given that the official route isn't self-serve, which third-party API is actually worth paying for.

## FAQ

**Is scraping Trustpilot reviews legal?**
Trustpilot's Terms of Use for Consumers explicitly prohibit it: Section 4 states you must not "carry out in any way... any text mining, data mining or web scraping of our platform for any purpose without our express permission," and separately names AI training. The Business Terms carry the same restriction under a different section number. Under US law specifically, hiQ Labs v. LinkedIn (9th Circuit) held that scraping publicly-viewable data doesn't violate the CFAA's unauthorized-access clause, but that case still ended in hiQ paying LinkedIn $500,000 and being permanently barred from scraping, on breach-of-contract and trespass grounds. **The practical read: a platform's own Terms of Use can create real legal exposure even where the CFAA doesn't apply**, regardless of which API or scraper you use to collect the data. This covers US case law only; no EU or French precedent was researched for Trustpilot specifically. Sources: [Trustpilot Terms of Use for Consumers](https://corporate.trustpilot.com/legal/for-reviewers/terms-of-use-for-consumers/feb-2025) · [Apify: hiQ v. LinkedIn case law](https://blog.apify.com/hiq-v-linkedin/)

**Official API or a scraping API, which should I use?**
If you run the business being reviewed and want invitations, widgets, or your own review data, the official API is the right tool and doesn't require scraping anything. The moment you need another business's reviews on a self-serve timeline, the official routes are excluded by their own access model, which is why this benchmark exists.

**What does this actually cost at scale?**
DataForSEO's measured $0.03754 per 1,000 reviews is the cheapest confirmed number in this benchmark. lobstr.io's confirmed rate is $1 per 1,000 reviews, a real measured figure, not an estimate, though still well above DataForSEO's. Outscraper's estimated $2.70 to $3.00 per 1,000 is 72 to 80 times DataForSEO's figure for the identical job. OpenWeb Ninja's real rate for this account's plan tier is unknown, and its most recent run returned nothing to amortize any cost against anyway.

**Can I reproduce these results?**
Partially, and the gaps are explicit rather than hidden. The scripts and raw logs for all 5 providers exist in this project and were run live against real accounts, including the verification rerun that changed the Apify and OpenWeb Ninja findings above. Check the test script and raw results here: [DataForSEO script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/dataforseo_benchmark.py) · [DataForSEO results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/dataforseo) · [Outscraper script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/outscraper_benchmark.py) · [Outscraper results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/outscraper) · [OpenWeb Ninja script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/openwebninja_benchmark.py) · [OpenWeb Ninja results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/openwebninja) · [Apify script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/apify_benchmark.py) · [Apify results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/apify) · [lobstr.io script](https://github.com/Adamisrail001/trustpilot-api-benchmark/blob/main/scripts/lobstr_benchmark.py) · [lobstr.io results](https://github.com/Adamisrail001/trustpilot-api-benchmark/tree/main/data/reports/lobstr)

**Can any of these pull more than 200 reviews for one business?**
Yes: lobstr.io was directly tested in a new isolated run against `www.thepearlsource.com` alone and returned 1,000/1,000 unique valid reviews from that one business, with 0 duplicates. The run consumed exactly 1,000 credits, completed in about 179 seconds, and stopped with `no_next_page` after collecting the full target. DataForSEO cannot do this because its endpoint has no pagination parameter and is hard-capped at 200 reviews per business. Outscraper returned 1,000 reviews across five businesses in the common benchmark, not 1,000 from one business.

A follow-up round repeated the same "1 business, 1,000 reviews" test against all five providers. lobstr.io again returned 1,000/1,000 reviews from `www.thepearlsource.com`, 0 duplicates. Apify returned 0 reviews on two separate attempts, against `www.thepearlsource.com` and then `www.shein.com`, where the run reported "Crawled 0/1 pages." Outscraper was silently capped at 200 reviews despite the 1,000-review request. DataForSEO rejected depth above 200 during validation. OpenWeb Ninja failed and returned an "unknown error." lobstr.io was the only provider that successfully returned 1,000 reviews from one business.

**Is the scoring here neutral?**
Disclosed, not neutral by default. The rubric this article scores against is owned by lobstr.io's own content team, and lobstr.io is one of the five providers scored against it. No specific finding here was suppressed or reframed in lobstr.io's favor as far as this audit could tell, but that ownership fact belongs in the open, not buried in a footnote.

## Conclusion

**lobstr.io is the overall winner at 7.90/10.** It was the only provider directly verified to return 1,000 unique reviews from one Trustpilot business, completing the isolated run with 1,000/1,000 valid reviews, 0 duplicates, about 179 seconds wall-clock, and exactly 1,000 credits consumed.

DataForSEO ranks second at 7.55/10 and remains the cheapest and fastest option for workloads that stay within 200 reviews per business. Outscraper ranks third at 7.06/10 and delivered the cleanest validated data, while Apify and OpenWeb Ninja showed material reliability problems in their latest verified runs.

For scraping beyond 200 reviews from one business, lobstr.io is the clear recommendation from this benchmark.
