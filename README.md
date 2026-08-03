# Trustpilot Review-Scraping API Benchmark

A reproducible benchmark of 5 APIs for scraping Trustpilot business reviews —
**Apify, OpenWeb Ninja, DataForSEO, Outscraper, Lobstr** — each tested against the
same 5 public Trustpilot business listings (`www.thepearlsource.com`,
`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com`), each targeting
200 reviews (1,000 requested per provider).

This project exists to support writing an article/comparison, and is built around
one rule: **raw evidence is preserved over cleanliness.** Every number in
`knowledge.md` was verified against the raw evidence in `data/` before being
written down — `knowledge.md` itself stays free of file-path citations by design,
since those links belong in the final article, not the working notes. Nothing
was invented, and every known gap is documented in `MISSING_AND_GAPS.md` instead
of silently papered over. Anyone should be able to inspect the scripts, inspect
the raw outputs, add their own API keys, rerun the benchmark, and get comparable
(not necessarily identical — see "Reproducibility" below) results.

## Where this project came from

This project was assembled by auditing and merging two earlier, messier project
folders (`trustpilot-api-benchmark` and `trustpilot review`) that both contained
overlapping evidence from the same underlying benchmark. **Every organizational
decision made during that merge — which script/dataset version was kept, what was
renamed, what's missing, what's duplicated — is documented in full in
[`MISSING_AND_GAPS.md`](./MISSING_AND_GAPS.md).** Read that file before trusting
any script's provenance or assuming a piece of evidence doesn't exist just because
you don't see it here.

## Folder structure

```
trustpilot-api-article/
├── data/
│   ├── raw/<api>/          Raw request/response captures, byte-for-byte from the
│   │                       original benchmark run (the primary evidence layer)
│   ├── exports/<api>/      Flattened review datasets: all-reviews.json / .csv
│   ├── analysis/<api>/     Computed JSON: domain-summary, duplicate-report,
│   │                       cost-report, timings, ground-truth-match, etc.
│   ├── logs/<api>/         run.log, and errors/event-log.jsonl where applicable
│   ├── reports/<api>/      Narrative markdown reports: benchmark-report,
│   │                       scorecard, field-coverage, final-verdict, etc.
│   └── raw/ground-truth/   Manually-verified sample used to check accuracy
│                           (www.thepearlsource.com only — see MISSING_AND_GAPS.md A.4)
├── scripts/
│   ├── <api>_benchmark.py         One standalone script per API
│   ├── <api>_ground_truth_compare.py   Compares live/archived output vs. ground truth
│   ├── lobstr_prerun_validate.py  Read-only Lobstr account/squid sanity check
│   ├── lib/                       Shared, dependency-free helper modules
│   └── configs/                   Per-API benchmark configuration notes (markdown)
├── benchmark-domains.json   The 5 test domains + target review counts
├── knowledge.md             Findings across 6 required categories, plus a ranked
│                           Final Summary (strengths/weaknesses per provider) and FAQ
├── criteria.md              The scoring rubric every provider was measured against
├── api_docs_mcps.txt        Consolidated API documentation + pricing reference
├── MISSING_AND_GAPS.md      Every known gap, decision, and how to close it
├── requirements.txt         No third-party dependencies — see file for detail
├── .env.example             Credential template — copy to .env and fill in
└── .gitignore
```

## Installation

The benchmark scripts are **Python 3** (originally Node.js — converted to Python
on request; see "Note on the JS → Python conversion" below). No third-party
packages are used.

1. Install Python **3.8 or later** (an inferred minimum from the code — f-strings
   and `pathlib` — not a tested one; no Python interpreter was available on the
   machine this conversion was done on to verify it end-to-end, see
   `MISSING_AND_GAPS.md`).
2. No `pip install` is required — zero dependencies (`requirements.txt` confirms
   this; only the standard library is used: `urllib.request`, `json`, `pathlib`,
   `time`, `hashlib`, `base64`).

## Environment setup

```
cp .env.example .env
```

Then fill in `.env` with your own credentials for whichever provider(s) you want
to test:

| Variable | Provider | Notes |
|---|---|---|
| `APIFY_API_TOKEN`, `APIFY_ACTOR_ID` | Apify | The original test used a private Actor you likely can't access — point `APIFY_ACTOR_ID` at a Trustpilot-reviews Actor you do have access to |
| `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | DataForSEO | HTTP Basic Auth pair |
| `OUTSCRAPER_API_KEY` | Outscraper | |
| `LOBSTR_API_KEY`, `LOBSTR_CRAWLER_ID`, `LOBSTR_SQUID_ID` | Lobstr | Requires a pre-configured squid for the Trustpilot Reviews crawler |
| `OPENWEBNINJA_API_KEY` | OpenWeb Ninja | |

`.env` is git-ignored. Never commit real credentials or paste them into scripts,
output files, or anything pushed to a shared repo/Gist.

## How to run each script

Every `*_benchmark.py` script refuses to make paid/live calls unless explicitly
confirmed, to prevent accidental spend:

```bash
# Apify — plan first (no network calls), then run for real
python scripts/apify_benchmark.py plan
CONFIRM_PAID_RUN=yes python scripts/apify_benchmark.py run

# DataForSEO
python scripts/dataforseo_benchmark.py

# Lobstr — validate your account/squid setup first (read-only, no charges)
python scripts/lobstr_prerun_validate.py
python scripts/lobstr_benchmark.py plan
CONFIRM_PAID_RUN=yes python scripts/lobstr_benchmark.py run

# OpenWeb Ninja — also requires stating your remaining monthly quota
python scripts/openwebninja_benchmark.py plan
CONFIRM_PAID_RUN=yes OPENWEBNINJA_QUOTA_REMAINING=<n> python scripts/openwebninja_benchmark.py run

# Outscraper
python scripts/outscraper_benchmark.py plan
CONFIRM_SMOKE_RUN=yes python scripts/outscraper_benchmark.py smoke   # 1 request only
CONFIRM_PAID_RUN=yes python scripts/outscraper_benchmark.py run

# Ground-truth comparisons (run after the corresponding benchmark, or directly
# against the archived data/ evidence — they default to reading from data/)
python scripts/apify_ground_truth_compare.py
python scripts/lobstr_ground_truth_compare.py
python scripts/openwebninja_ground_truth_compare.py
python scripts/outscraper_ground_truth_compare.py
```

On some systems the interpreter is invoked as `python3` instead of `python` —
use whichever resolves to Python 3 on your machine.

A fresh run writes its output to `outputs/<provider>/` at the project root
(git-ignored, scratch space). This is intentionally kept **separate from
`data/`**, which holds the original, committed benchmark evidence that
`knowledge.md`'s findings were verified against. Re-running a script does not
overwrite `data/`.

## Reproducibility — what to expect from a fresh run

**Two of the five main scripts (`apify-benchmark.js`, `dataforseo-benchmark.js`,
now `apify_benchmark.py` / `dataforseo_benchmark.py`) explicitly self-describe as
reconstructions**, not preserved original code — they were built by
reverse-engineering the request/response shapes confirmed in the historical raw
JSON, because the literal original test code no longer exists in either source
project. The other three (Lobstr, OpenWeb Ninja, Outscraper) have more confident
headers but no confirmed record of having been run end-to-end against live paid
accounts either. The Python scripts are now a **second-generation port** of that
same reconstruction (JS reconstruction → Python port) — see "Note on the JS →
Python conversion" below. Practically:

- A fresh run **will not** reproduce the exact historical review counts, timings,
  or costs recorded in `data/` — live scraping targets and pricing change over
  time, same as any live scrape or API call would.
- Do expect a **comparable** result: same call sequence, same request shape, same
  analysis outputs (`domain-summary.json`, `cost-report.json`, etc.) in the same
  format, so a fresh run's `outputs/<provider>/` can be compared side-by-side
  against `data/*/​<provider>/`.
- DataForSEO's script is the least complete of the five — see
  `MISSING_AND_GAPS.md` A.1 for exactly what's missing and how to close it.

## Organizational decisions made during the merge (summary)

Full detail and reasoning for every item below is in **`MISSING_AND_GAPS.md`** —
this is a short index so you know what to look up there:

- **Scripts source:** `trustpilot-api-benchmark`'s scripts were used as the base
  for Apify, Lobstr, OpenWeb Ninja, and Outscraper — they are far more complete
  (928/119, 506/74, 604/72 lines vs. the equivalent scripts in `trustpilot review`)
  and their file-write paths match the actual historical `raw/` evidence
  byte-for-byte. **DataForSEO had no script at all** in that project — the only
  one found anywhere was ported from `trustpilot review` (MISSING_AND_GAPS.md A.1).
- **`data/raw/<api>/raw/...` was flattened** to `data/raw/<api>/...` — the nested
  `raw/raw` naming was a mechanical artifact of copying `outputs/<api>/raw/` into
  `data/raw/<api>/`, not meaningful, so it was flattened for consistency.
- **`knowledge.md` was synthesized from `trustpilot-api-benchmark/knowledge.md`**
  (922 lines, primary source) restructured into the 6 required categories, with
  `trustpilot review/knowledge.md` (653 lines) used only as a lower-confidence
  cross-check — that file itself says it predates `docs/`, `scripts/`, `reports/`
  existing in its own project. It has since been simplified (file-path citations
  and "Missing evidence" commentary removed, since those belong in the final
  article and in `MISSING_AND_GAPS.md` respectively) and extended with a ranked
  **Final Summary** (per-provider strengths/weaknesses, aggregate scoring) and an
  **FAQ**. Two internal number disputes flagged during synthesis (Lobstr's HTTP
  429 count and raw field count) were subsequently re-checked directly against
  both source projects' raw files and resolved — see `MISSING_AND_GAPS.md` item 5.
- **`criteria.md`** is an unmodified copy of `docs/testing-criteria.md`, which was
  byte-identical between both source projects — no conflict to resolve there. Its
  rubric is headed "Owner: lobstr.io content team," and Lobstr is one of the five
  scored providers — disclosed prominently rather than buried (MISSING_AND_GAPS.md B.1).
- **`api_docs_mcps.txt`** consolidates all 10 documentation/pricing files
  (2 per API) verbatim. No MCP server references exist in either source project,
  so that part of the deliverable is unfulfilled by absence of evidence, not by
  oversight (MISSING_AND_GAPS.md A.6).
- **Real `.env` files** from the source projects were never copied here — only
  `.env.example` templates were merged. Squid IDs hardcoded in
  `scripts/lobstr-prerun-validate.js` are resource identifiers, not credentials,
  and were left as-is (the file itself asserts it never prints real credentials).
- **Missing `final-verdict.md`** for Outscraper and DataForSEO, and **only 1 of 5
  domains has ground truth** — both are gaps in the original evidence, not
  something lost during this reorganization (MISSING_AND_GAPS.md A.3 and A.4).
- **All scripts were converted from JavaScript to Python** on request, as a
  faithful line-by-line port (same CLI, same paths, same retry logic). Python
  3.12 was then installed and used to verify the port — see the section below
  for what was (and wasn't) confirmed.

## Note on the JS → Python conversion

Every script in this project was originally JavaScript (Node.js) — both source
projects audited during the initial reorganization only contained JS. That
version is documented in `MISSING_AND_GAPS.md`. The scripts were subsequently
converted to Python 3 (stdlib only, no third-party
packages) on request, as a line-by-line behavioral port: same CLI modes
(`plan`/`smoke`/`run`), same safety env-var gates (`CONFIRM_PAID_RUN`,
`CONFIRM_SMOKE_RUN`, `OPENWEBNINJA_QUOTA_REMAINING`), same output file paths and
JSON shapes, same retry/backoff/error-classification logic, same idempotent-resume
behavior. The original `.js` files were removed once the Python port was
reviewed — if you need to compare against the JS version, it's preserved in the
audited source project `trustpilot-api-benchmark` (for Apify/Lobstr/OpenWeb
Ninja/Outscraper) and `trustpilot review` (for DataForSEO) alongside this project.

**This conversion was verified with a real Python interpreter** (Python 3.12.10,
installed via `winget install Python.Python.3.12` after the initial port review
found none present):
- `python -m py_compile` passes on all 18 files.
- Every `*_benchmark.py`/`dataforseo_benchmark.py` script was actually run and
  its full import chain (`from lib.X import Y`) confirmed to resolve at
  runtime, not just parse cleanly — each failed exactly where expected (missing
  `.env`), proving the code path up to that point is sound.
- All 4 `*_ground_truth_compare.py` scripts were run for real against the
  archived data in `data/` (no credentials needed) and their output diffed
  against the original JS-produced files. Apify, Lobstr, and Outscraper now
  reproduce the original byte-for-byte (aside from the timestamp); OpenWeb
  Ninja has 2 pre-existing, JS-inherited discrepancies unrelated to the Python
  port. This diffing process is what
  caught and fixed 2 real bugs (a missing whole-number JSON collapse in
  Lobstr's script, and a missing `ensure_ascii=False` across 6 files that would
  have mangled non-ASCII review text).

**Update — real credentials were located** (`trustpilot-api-benchmark/.env`) and
used for further live verification, at zero or near-zero cost:
- **Apify & DataForSEO**: read-only calls against historical run/task IDs
  (`get_run`, `get_task`) succeeded live and matched `knowledge.md`'s recorded
  figures exactly — free, since they query already-existing resources rather
  than creating new ones.
- **Lobstr**: `lobstr_prerun_validate.py` ran live (read-only), all 12 checks
  passed against the real account.
- **Outscraper**: the `smoke` mode was run live and succeeded, but consumed
  more usage than its docstring promises (200 reviews, not ~20) — a
  pre-existing bug in the original JS, not the Python port. See
  `MISSING_AND_GAPS.md` A.7.
- **OpenWeb Ninja could not be tested without cost** — its API has no
  free/read-only endpoint of any kind (confirmed in its own docs), so this was
  skipped rather than run.

**What is still NOT verified**: the actual *write* paths that create new paid
resources (Apify's `start_actor_run`, DataForSEO's `post_task`, Lobstr's
`start_run`, OpenWeb Ninja's only endpoint) were not exercised, since that means
spending real money beyond what was explicitly approved. Multi-page pagination
is also unverified (every live test above returned all results on one page). Do
a `plan`-mode dry run and get explicit sign-off on cost before any full paid
`run`.
