# DataForSEO Trustpilot Reviews API — Missing / Pending Evidence

Everything below was explicitly **not** measured in this benchmark run. Nothing here was assumed, estimated, or invented to fill the gap — each is called out so it can be tested deliberately if needed, and so the scorecard's lower sub-scores (Scalability, Input Flexibility, parts of Cost Efficiency and Developer Experience) aren't mistaken for observed failures.

## Accuracy — domains without ground truth

`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` have no manually-verified ground-truth sample (`ground_truth_file: null` in `benchmark-domains.json`). Their **data quality is unverified** — only `www.thepearlsource.com` accuracy is claimed, and only for the fields both sources captured. To close this, a manually-verified sample (same shape as `ground-truth/thepearlsource-sample.json`) would need to be collected for each domain.

## Scalability

- **10x volume degradation:** not tested. This run submitted 5 tasks total; no attempt was made to submit 50 tasks concurrently or in rapid succession to observe latency/success-rate degradation.
- **Rate limits:** documented (30 POST/min, 100 tasks/POST, 20 `tasks_ready`/min) but never approached — this run made 5 POST calls and ~6 `tasks_ready` polls, nowhere near the ceiling.
- **Daily/monthly volume caps:** none is documented as blocking self-serve use at this account tier, but this was not independently confirmed against the account dashboard.

## Cost Efficiency

- **Billing fairness on failed requests:** zero failed requests occurred, so whether DataForSEO charges for a task that errors out is unverified.
- **Free tier / trial credits:** not checked. Whether a trial credit exists, its size, and whether it was applied to this run's $0.0375 charge was not investigated.
- **Account balance before/after:** not captured (no billing-dashboard screenshot/export taken). The only cost evidence is the `cost` field from each task's API response.

## Developer Experience

- **Official SDKs:** not tested — this benchmark used raw HTTP (`fetch`) against the documented REST endpoints, per the project's zero-dependency script design. Any official client library's ergonomics are unassessed.
- **Support responsiveness:** not tested — no support ticket or contact was filed during this benchmark.

## Speed & Throughput

- **Worst-case turnaround:** the documented standard-priority SLA is "up to 45 minutes." This run completed in ~2 min 46 s — a best-case result under whatever queue conditions existed at run time, not a guarantee of typical performance. Repeated runs at different times of day would be needed to characterize the real distribution.

## Input Flexibility

- **Trustpilot Search endpoint:** exists per the official docs (business discovery by keyword) but was not exercised — this benchmark only used the Reviews Task POST/GET flow, since the target was reviews, not business discovery.

## Reconciliation with billing dashboard

Per `docs/dataforseo-pricing.md`, full reconciliation should also include a billing-dashboard export. That step was not performed for this run — the cost figures in `reports/dataforseo-cost-report.md` come exclusively from the API's own `cost` field in each task response, which is documented as the authoritative per-task charge but has not been cross-checked against the account's billing history UI.
