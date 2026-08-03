# X API Articles — Testing Methodology (Master Doc)

**Format:** "Best {X} API for Scraping Data at Scale"
**Owner:** lobstr.io content team
**Version:** 1.0 — July 2026

---

## 1. Purpose

This document defines how every API in an "X API" article is tested, scored, eliminated, and presented. Every article in the format follows this methodology without exception. All raw testing assets (scripts, logs, outputs) are published to a public gist or GitHub repo linked from the article, so readers can reproduce every result.

---

## 2. Article Structure (reference)

1. Does {X} have an official API? — use cases, code/request examples, why it can't be used for scraping at scale
2. Best {X} API for scraping at scale — testing criteria, methodology, eliminations
3. Winner deep-dive — intro + user rating, benchmark scores, pros/cons table, per-criteria performance (how tested → findings → verdict → CTA to testing report)
4. Best {X} APIs by use case — "API — Best for {use case}"

The winner is whichever API genuinely scores highest. No predetermined outcomes.

---

## 3. Elimination Criteria

Checked **before** scoring. Failing any one disqualifies the API. Disqualified APIs appear in the article's "Disqualified" table with the criterion failed and a one-line reason, linked to gist evidence where applicable.

| # | Criterion | Rule |
|---|-----------|------|
| E1 | No self-serve access | Sales-call-only, waitlist-gated, or no trial. If a key can't be obtained and the benchmark run within 48h, it's out. |
| E2 | Benchmark run failure | Success rate below 50% on the standard 1K-request run, or API breaks mid-run and cannot complete it. |
| E3 | No usable documentation | No public docs, or docs so outdated/incomplete a working request can't be built from them alone. Community workarounds don't count. |
| E4 | Uncomputable cost | Pricing so opaque that cost-per-1K-records cannot be calculated even after signup. |
| E5 | Platform coverage failure | Does not return the core data type the article targets. |
| E6 | Dead or abandoned | No response within test window, broken infra, or clear abandonment (changelog/status dead 12+ months, key endpoints deprecated with no replacement). |

**Disqualified table format:** API name | Criterion failed | One-line reason | Evidence link

---

## 4. Scoring Rubric — 10 points total

### Criterion 1: Success Rate & Reliability — 2.0 pts

| Sub-criterion | Points |
|---------------|--------|
| Success rate on 1K-request benchmark | 1.0 |
| Empty/partial response rate | 0.4 |
| Error handling quality (meaningful error codes, safe retries) | 0.3 |
| Stability during test window (no mid-run degradation/outages) | 0.3 |

### Criterion 2: Data Quality & Completeness — 2.0 pts

| Sub-criterion | Points |
|---------------|--------|
| Field coverage vs ground truth (fields returned ÷ fields on page) | 0.8 |
| Data accuracy (values match source) | 0.5 |
| Schema consistency across responses | 0.4 |
| Freshness (live data vs stale cache) | 0.3 |

### Criterion 3: Cost Efficiency — 1.5 pts

| Sub-criterion | Points |
|---------------|--------|
| Cost per 1K successful records | 0.8 |
| Billing fairness (failed requests not charged) | 0.3 |
| Free tier / trial credits for evaluation | 0.2 |
| Pricing transparency (self-serve, predictable) | 0.2 |

### Criterion 4: Speed & Throughput — 1.5 pts

| Sub-criterion | Points |
|---------------|--------|
| Median latency per request | 0.5 |
| Wall-clock time for 1K-record batch | 0.5 |
| p95 latency (consistency under load) | 0.3 |
| Async/batch endpoint availability | 0.2 |

### Criterion 5: Scalability — 1.2 pts

| Sub-criterion | Points |
|---------------|--------|
| Rate limits & max concurrency allowed | 0.5 |
| Degradation at 10x volume (success rate/latency hold?) | 0.4 |
| Volume caps (daily/monthly ceilings blocking production use) | 0.3 |

### Criterion 6: Developer Experience — 1.0 pt

| Sub-criterion | Points |
|---------------|--------|
| Time-to-first-successful-request | 0.3 |
| Docs quality (complete, current, searchable) | 0.3 |
| SDKs & working code examples | 0.2 |
| Error message clarity + support responsiveness | 0.2 |

### Criterion 7: Input Flexibility & Coverage — 0.8 pts

| Sub-criterion | Points |
|---------------|--------|
| Accepted input types (URL, ID, search query, geo/filters) | 0.3 |
| Endpoint breadth for the platform | 0.3 |
| Enrichment/related endpoints | 0.2 |

---

## 5. Score Bands (verdicts)

| Score | Verdict |
|-------|---------|
| 9.0–10 | Best-in-class — safe default choice |
| 7.5–8.9 | Strong — minor trade-offs |
| 6.0–7.4 | Usable with caveats — flag them |
| Below 6.0 | Not recommended at scale |

---

## 6. Methodology Skeleton

Every benchmark run follows these rules:

- **Same input dataset for every API** — one fixed list of URLs/IDs/queries per article, versioned in the gist
- **Same time window** — all APIs tested within the same period to keep conditions comparable
- **Same script structure** — one benchmark script template, adapted only for each API's auth and request format
- **Everything logged to the public gist** — raw requests, responses, timings, failures, and cost calculations

The public raw runs are the moat: nobody else publishes them. Reproducibility is the differentiator, not just the scores.

---

## 7. Display Rules for Articles

- Aggregate score shown as **/10** in the main benchmark table
- Per-criteria rating blocks normalized to **/5 stars** — readers parse stars faster than decimals
- **Sub-criteria scores stay internal** (or in the gist) — criterion-level scores only in the article (e.g. "Reliability: 1.8/2.0")
- Every criterion section follows: **How it was tested → Findings → Verdict → CTA** (link to testing report/gist)

---

## 8. Notes for Writers

- Do not add "violates platform ToS" as an elimination criterion — it applies to the entire category. Address legality once in a neutral FAQ block if needed.
- If lobstr.io does not win the aggregate benchmark, it does not get crowned. Place it in the use-case section where it genuinely fits best.
- Every claim in the article must trace back to a logged run in the gist. No unverifiable numbers.