# Apify (automation-lab/trustpilot) — Final Verdict

## Benchmark partially completed: 798 / 1,000 unique reviews

One Actor run, all 5 domains submitted together as required. 4 of 5 domains came back essentially perfect (200, 200, 199, 199 unique — the two 199s just single internal duplicates). The 5th, **SHEIN, returned zero reviews with no error anywhere** — not in HTTP responses, not in the dataset, not in the Run's stats object.

## Elimination: Not eliminated (E1–E6 all pass)

## Provisional score: 7.51/10 — Strong, right at the edge

This is the best **data-quality** result of any tool benchmarked in this project (92.3% field coverage, including the only working `owner_reply_date` field of the four tools tested) and the cost model is the most precisely self-consistent (measured cost within 0.3% of the published formula). It's held down by a genuine reliability problem: one domain failed completely and silently.

## Why this is different from the DataForSEO/Outscraper near-miss shortfalls

DataForSEO's temu.com shortfall (1 review) and Apify's own aliexpress.com/thehalara.com shortfalls (1 each) are trivial — a single internal duplicate that dedup correctly caught. **SHEIN returning literally zero results, with zero error signal, is qualitatively different** — it means a production user could not distinguish "this company has no reviews" from "the Actor silently failed" without independently checking. That distinction matters more than the raw percentage.

## Where this tool fits

If the SHEIN-style gap is a one-off (unconfirmed — would need a repeat run or the Actor's live console log to know), Apify's per-review data quality and cost predictability are excellent. If it's a systematic weakness for certain company pages, that's a real production risk this single run can't rule out either way.

## Confirmed facts worth carrying into any cross-tool writeup

- Actor: `automation-lab/trustpilot`, one `companyUrls` array run for all 5 domains
- Auth: `Authorization: Bearer <token>`
- Async run → poll `GET /v2/actor-runs/{id}` → `GET /v2/datasets/{id}/items`
- Measured cost: $0.465 for 798 unique reviews ($0.5827/1,000) — pay-per-event, free-tier rate
- The only tool of the four benchmarked that returns a populated owner-reply-date field
