# `/v1/results` page-size finding — correction: wrong parameter name, not a Lobstr platform bug

**Evidence type: LIVE, verified 2026-09-01** — two fresh `GET` requests made directly
against the live API (outside the benchmark harness, via `curl`), against the same
archived run (`4c2e07bd3b9b4c9386661edb8ef58174`, squid `8d9e0b80d6d2481283c138104caf022d`)
used throughout the original benchmark. Nothing in the original raw evidence files was
modified — this is a new, independent check layered on top of them.

## What was previously believed

`IMPORTANT/knowledge.md` (Lobstr § Documentation issues) and
`PROOF/screenshots/lobstr-pagination-attribution-proof.html` stated that the documented
maximum results-page `limit` of 100 on `/v1/results` was silently served as `limit: 10`
in the live response regardless of what was requested — framed as a Lobstr
documentation-vs-behavior gap and factored into the Developer Experience deduction.

That belief traces to `scripts/lib/lobstr_client.py:215-221`, whose `get_results()`
builds its querystring with a `limit` parameter — the same parameter name shown in
Lobstr's own documented example request (`api_docs_mcps.txt:2530`).

## What was found

`limit` is accepted by the API but does not control page size at all — requesting
`limit=100` is silently ignored and the server always returns exactly 10 items/page.
Re-confirmed live today; matches the original `data/lobstr/raw/results/results-page*.json`
captures exactly (`"limit": 10"` on every page).

The real, working (and undocumented — not mentioned anywhere in `api_docs_mcps.txt`)
parameter is **`page_size`**:

```
GET https://api.lobstr.io/v1/results?run=4c2e07bd3b9b4c9386661edb8ef58174&page=1&page_size=1000
```
returned:
```json
{
  "total_results": 1000,
  "limit": 1000,
  "page": 1,
  "total_pages": 1,
  "result_from": 1,
  "result_to": 1000,
  "data": [ /* 1000 items */ ]
}
```

Cross-checked against the run's own object (the authoritative source for what this run
actually produced):
```
GET https://api.lobstr.io/v1/runs/4c2e07bd3b9b4c9386661edb8ef58174
```
returned `"total_results": 1000, "total_unique_results": 1000, "status": "done"` — an
exact match to what `page_size=1000` returned in one page. Spot-checked several items in
that response's `data[]` and confirmed each carries `"run": "4c2e07bd3b9b4c9386661edb8ef58174"`
— i.e. the larger page size is correctly scoped to this one run, not a broader/leaked
filter producing a coincidentally-matching count.

## Root cause

`limit` is simply the wrong query parameter name for controlling page size on
`/v1/results` — and Lobstr's own documentation example uses that same wrong name, which
is presumably how it ended up in this benchmark's client code too. `page_size` is the
parameter that actually works. This is a real (still-undocumented) naming gap worth
noting, but it is **not** "the server silently downgrades your requested limit" — the
real control (`page_size`) isn't capped at all, at least up to 1000 (the full size of
this run).

## What this does NOT resolve

- Whether `page_size` has a ceiling above 1000 was not tested — this run only has 1,000
  total results, so 1000 was already the entire run.
- Whether `page_size` behaves the same on other crawlers/endpoints — only tested here on
  `/v1/results` for the Trustpilot crawler.
- The separate Lobstr documentation gap — result items carry no `task` field for
  source/domain attribution — is unrelated to this parameter and **remains valid**;
  this correction does not touch it.

## Recommended follow-up (not applied here — flagging only)

- `scripts/lib/lobstr_client.py:215-221` — `get_results()` should send `page_size`
  instead of (or alongside) `limit`.
- `PROOF/screenshots/lobstr-pagination-attribution-proof.html` — its §1 finding needs
  the same correction.
- Any Developer Experience scoring that penalized Lobstr for this specific finding
  should be revisited — this was a wrong-parameter-name issue in the benchmark's own
  tooling and in Lobstr's own doc example, not a demonstrated Lobstr platform behavior
  bug.
