# Lobstr.io Trustpilot Reviews — Final Verdict

## Benchmark completed: 1,000 / 1,000 unique reviews

Exactly one Run created (`4524c3ce2ad848739b5f2aea4902657b`), on the clean squid (`8d9e0b80d6d2481283c138104caf022d`), across the 5 approved domains, zero shortfall, zero duplicates.

## Two real bugs found and fixed along the way — both ours, not Lobstr's platform

1. Squid-configuration renamed the clean squid into a collision with the still-existing old contaminated squid → fixed by never sending `name`.
2. Result pagination assumed a 100-item page size (per docs) but the API silently serves 10/page → the safety cap that protects against infinite loops was too low, and separately, result items have no `task` field, requiring attribution via `company_page_url` instead. Both fixed; results were re-fetched using the **same** Run ID, creating zero additional Runs.

## Elimination: Not eliminated (E1–E6 all pass)

## Provisional score: 7.90/10 — Strong

Best-in-class data quality (92.3% field coverage, richest schema of any tool tested) and a perfectly fair, fully-confirmed 1:1 credit-to-review billing model. Held back by real developer-experience friction (two fix iterations needed) and untested scalability beyond this one 1,000-review run.

## Confirmed facts worth carrying into any cross-tool writeup

- Exactly 1,000 credits consumed for 1,000 unique reviews — the cleanest billing-fairness evidence of any tool in this project.
- The same 4 authors (Linda B, Human Sun, Sharon R., MW) showed a same-day-freshness owner-reply discrepancy against ground truth — now cross-confirmed by **three independent tools** (OpenWeb Ninja, Apify, Lobstr.io).
