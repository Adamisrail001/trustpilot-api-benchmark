# Outscraper Trustpilot Reviews API — Missing / Pending Evidence

Nothing below was assumed, estimated, or invented to fill the gap. Each is called out explicitly so the scorecard's lower sub-scores (Scalability, parts of Cost Efficiency) aren't mistaken for observed failures — this run had zero failures.

## Cost

- **Measured (billed) cost:** Pending. Outscraper documents no endpoint returning account balance or per-request billed cost. Only a *calculated* range ($2.70–$3.00) from published pricing × measured usage is available. Closing this requires manually checking the Outscraper billing dashboard before/after this run.
- **Actual free-tier balance at run time:** Pending — unknown whether this account's first 100 free reviews were already consumed prior to this run, which determines which end of the $2.70–$3.00 range applies.

## Accuracy — domains without ground truth

`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` have no manually-verified ground-truth sample. Only `www.thepearlsource.com` accuracy is claimed.

## Scalability

- **Rate limits:** Not documented anywhere in `docs/outscraper-documentation.md` (its own status table lists this "Pending verification"). This run made only 5 requests + ~120 polling requests, nowhere near any conceivable limit, so nothing was learned empirically either.
- **10x volume degradation:** Not tested. This run submitted 5 domains sequentially; no attempt was made to submit 50 in parallel/rapid succession.
- **Multi-query batching at scale:** Docs state up to 1,000 queries can be batched into one request, but this run deliberately submitted one domain per request (to keep per-domain evidence/pagination independent) — batching behavior itself is untested.

## Developer Experience

- **Official SDKs:** Not tested — raw HTTP (`fetch`) was used, per this project's zero-dependency design.
- **Support responsiveness:** Not tested — no support ticket was filed.

## Speed & Throughput

- **Typical vs. worst-case timing:** No documented SLA exists for Outscraper's async turnaround (unlike DataForSEO's "up to 45 minutes"). This run's ~8.5-minute wall clock and 1.9s p95 latency are one observed data point, not a characterized distribution — repeated runs at different times would be needed for that.

## Response shape

- The parser's shape assumption was verified correct against real data this run (see `benchmark-report.md`) — no outstanding gap here, noted only because the plan explicitly flagged it as unconfirmed beforehand.

## Duplicate/secondary-key coverage

- The review-URL secondary dedupe key was never exercised (no `review_url`/`url` field was present anywhere in the 1,000 real records observed) — tier 1 (native `review_id`) resolved every record. Whether Outscraper ever returns a URL field under a different name is unconfirmed.
