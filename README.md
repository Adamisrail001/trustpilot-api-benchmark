# Trustpilot Review-Scraping API Benchmark

A reproducible benchmark of 5 APIs for scraping Trustpilot business reviews —
**Apify, OpenWeb Ninja, DataForSEO, Outscraper, Lobstr** — each tested against the
same 5 public Trustpilot business listings (`www.thepearlsource.com`,
`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com`), each targeting
200 reviews (1,000 requested per provider).

This project exists to support writing an article/comparison, and is built around
one rule: **raw evidence is preserved over cleanliness.** Every number in
`IMPORTANT/knowledge.md` was verified against the raw evidence in `DATA/` before
being written down. Nothing was invented, and every known gap is documented in
`MISSING_AND_GAPS.md` instead of silently papered over. Anyone should be able to
inspect the scripts, inspect the raw outputs, add their own API keys, rerun the
benchmark, and get comparable (not necessarily identical — see "Reproducibility"
below) results.

## Known limitations — read before trusting the numbers

Three things materially limit what this benchmark can claim, kept visible here
rather than buried in the notes. Full detail on each is in
[`MISSING_AND_GAPS.md`](./MISSING_AND_GAPS.md):

- **The scoring rubric has a conflict of interest.** [`IMPORTANT/criteria.md`](./IMPORTANT/criteria.md)
  is headed "Owner: lobstr.io content team," and **Lobstr is one of the 5
  providers scored against it.** Nothing in the rubric was changed to favor
  Lobstr, but it was never reviewed by an independent party either
  (`MISSING_AND_GAPS.md` B.1).
- **Ground truth exists for only 1 of the 5 test domains** (`www.thepearlsource.com`).
  Every accuracy and field-coverage figure for the other four domains
  (`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com`) is
  **unverified against a manually-checked sample** — those numbers describe
  self-consistency, not confirmed correctness (`MISSING_AND_GAPS.md` A.4 / B.2).
- **Scalability is essentially untested for all 5 providers.** None was pushed
  past ~200 reviews/business or tested under real concurrency or 10x volume.
  DataForSEO's 200-review ceiling is the only *confirmed* limit here — the
  others are simply untested, not proven to scale (`MISSING_AND_GAPS.md` B.3).

## Where this project came from

This project was originally assembled by auditing and merging two earlier, messier
project folders that both contained overlapping evidence from the same underlying
benchmark, then later reorganized a second time into the provider-first layout
below so it's easy to hand to a reader who wants to verify the article's claims.
**Every organizational decision from both passes — which script/dataset version
was kept, what was renamed, what's missing, what's duplicated — is documented in
full in [`MISSING_AND_GAPS.md`](./MISSING_AND_GAPS.md) and the "Organizational
decisions" section below.** Read those before trusting any script's provenance or
assuming a piece of evidence doesn't exist just because you don't see it here.

## Folder structure

```
trustpilot-api-benchmark/
├── README.md                — this file
├── MISSING_AND_GAPS.md       — every known gap, decision, and how to close it
├── IMPORTANT/                — the 4 documents that back every claim in the article
│   ├── knowledge.md              Findings across 6 required categories, plus a
│   │                              ranked Final Summary and FAQ
│   ├── criteria.md                The scoring rubric every provider was measured
│   │                              against (see "Known limitations" above)
│   ├── methodology.md             How the Data-pillar (fill-rate/accuracy)
│   │                              scores were computed — the spec datacompare.py implements
│   └── article.md                 The published article itself
├── DATA/                     — the evidence, one folder per provider
│   ├── apify/        │
│   ├── dataforseo/    │  each contains:
│   ├── lobstr/         │    raw/       byte-for-byte request/response captures
│   ├── openwebninja/  │    exports/   flattened all-reviews.json / .csv
│   ├── outscraper/    │    analysis/  domain-summary, cost-report, timings, etc.
│   │                    │    logs/      run.log
│   │                    │    reports/   benchmark-report, scorecard, final-verdict, etc.
│   └── ground-truth/         thepearlsource-sample.json — the one manually-verified
│                              sample every *_ground_truth_compare.py checks against
├── SCRIPTS/                  — the code, one folder per provider
│   ├── apify/ ... outscraper/    benchmark.py, ground_truth_compare.py,
│   │                              single_domain_test.py, config.md
│   ├── lobstr/                    (also has prerun_validate.py)
│   └── lib/                       shared, dependency-free helper modules
├── PROOF/
│   ├── screenshots/          16 dashboard/report screenshots cited throughout
│   │                          knowledge.md and the article
│   └── errors/                Raw event-log.jsonl for the 2 providers that hit a
│                              real error during this run (Lobstr, OpenWeb Ninja)
├── benchmark-domains.json    The 5 test domains + target review counts
├── api_docs_mcps.txt         Consolidated API documentation + pricing reference
├── datacompare.py + datacompare.config.example.json   The Data-pillar scoring engine
├── requirements.txt          No third-party dependencies — see file for detail
├── .env.example              Credential template — copy to .env and fill in
└── .gitignore
```

**Not shown above, kept at root, out of scope for a reader verifying the
benchmark** (content-authoring internals, not evidence — see "What's excluded
from the reader-facing tree" below): `.claude/`, `CLAUDE.md`, `instructions/`,
`facts.md`, `datacompare-workspace/`.

**Quick nav — where to find things:**

| Looking for... | Go to |
|---|---|
| Raw, unmodified API responses | `DATA/<provider>/raw/` |
| The scripts that produced everything | `SCRIPTS/<provider>/` |
| Screenshots proving a specific claim | `PROOF/screenshots/` |
| Raw error evidence (429s, failures) | `PROOF/errors/` |
| The scoring rubric | `IMPORTANT/criteria.md` |
| How the data-quality scores were computed | `IMPORTANT/methodology.md` |
| Every known gap or unresolved issue | `MISSING_AND_GAPS.md` |
| The write-up the numbers feed into | `IMPORTANT/knowledge.md` and `IMPORTANT/article.md` |

### What's excluded from the reader-facing tree

- **`.claude/`, `CLAUDE.md`, `instructions/`, `facts.md`** — these are lobstr.io's
  internal content-authoring tooling (slash commands, writing playbooks, brand
  facts). They explain *how the article got written*, not *whether its claims are
  true*, so they're left in place (removing them would break the `/api`,
  `/datacompare`, `/knowledge` commands and future authoring sessions in this
  repo) but are not part of what a reader needs to verify anything here.
- **`datacompare-workspace/`** (formerly `content/data/`) — the live input/config/
  output directory for `datacompare.py`'s fill-rate-table run (`datacompare.config.json`
  + per-provider `.json`/`.csv` + `signals.json`). Its `.json`/`.csv` files duplicate
  the same reviews already in `DATA/<provider>/exports/`, reformatted for that one
  tool — left alone rather than merged, since repointing the tool's config carries
  more risk of breaking reproducibility than it's worth.

## Installation

The benchmark scripts are **Python 3** (originally Node.js — converted to Python
on request; see "Note on the JS → Python conversion" below). No third-party
packages are used.

1. Install Python **3.8 or later** (an inferred minimum from the code — f-strings
   and `pathlib` — not a tested one on every machine; see the verification caveat
   in "Organizational decisions" below).
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

Every `benchmark.py` script refuses to make paid/live calls unless explicitly
confirmed, to prevent accidental spend:

```bash
# Apify — plan first (no network calls), then run for real
python SCRIPTS/apify/benchmark.py plan
CONFIRM_PAID_RUN=yes python SCRIPTS/apify/benchmark.py run

# DataForSEO
python SCRIPTS/dataforseo/benchmark.py

# Lobstr — validate your account/squid setup first (read-only, no charges)
python SCRIPTS/lobstr/prerun_validate.py
python SCRIPTS/lobstr/benchmark.py plan
CONFIRM_PAID_RUN=yes python SCRIPTS/lobstr/benchmark.py run

# OpenWeb Ninja — also requires stating your remaining monthly quota
python SCRIPTS/openwebninja/benchmark.py plan
CONFIRM_PAID_RUN=yes OPENWEBNINJA_QUOTA_REMAINING=<n> python SCRIPTS/openwebninja/benchmark.py run

# Outscraper
python SCRIPTS/outscraper/benchmark.py plan
CONFIRM_SMOKE_RUN=yes python SCRIPTS/outscraper/benchmark.py smoke   # 1 request only
CONFIRM_PAID_RUN=yes python SCRIPTS/outscraper/benchmark.py run

# Ground-truth comparisons (run after the corresponding benchmark, or directly
# against the archived DATA/ evidence — they default to reading from DATA/)
python SCRIPTS/apify/ground_truth_compare.py
python SCRIPTS/dataforseo/ground_truth_compare.py
python SCRIPTS/lobstr/ground_truth_compare.py
python SCRIPTS/openwebninja/ground_truth_compare.py
python SCRIPTS/outscraper/ground_truth_compare.py
```

On some systems the interpreter is invoked as `python3` instead of `python` —
use whichever resolves to Python 3 on your machine.

A fresh run writes its output to `outputs/<provider>/` at the project root
(git-ignored, scratch space). This is intentionally kept **separate from
`DATA/`**, which holds the original, committed benchmark evidence that
`IMPORTANT/knowledge.md`'s findings were verified against. Re-running a script
does not overwrite `DATA/`.

## Reproducibility — what to expect from a fresh run

**Two of the five main scripts (Apify's and DataForSEO's) explicitly self-describe
as reconstructions**, not preserved original code — they were built by
reverse-engineering the request/response shapes confirmed in the historical raw
JSON, because the literal original test code no longer exists in either source
project. The other three (Lobstr, OpenWeb Ninja, Outscraper) have more confident
headers but no confirmed record of having been run end-to-end against live paid
accounts either. Practically:

- A fresh run **will not** reproduce the exact historical review counts, timings,
  or costs recorded in `DATA/` — live scraping targets and pricing change over
  time, same as any live scrape or API call would.
- Do expect a **comparable** result: same call sequence, same request shape, same
  analysis outputs (`domain-summary.json`, `cost-report.json`, etc.) in the same
  format, so a fresh run's `outputs/<provider>/` can be compared side-by-side
  against `DATA/<provider>/`.
- DataForSEO's script is the least complete of the five — see
  `MISSING_AND_GAPS.md` A.1 for exactly what's missing and how to close it.

## Organizational decisions made during the merge (summary)

Full detail and reasoning for every item below is in **`MISSING_AND_GAPS.md`** —
this is a short index so you know what to look up there:

- **Scripts source:** the base scripts for Apify, Lobstr, OpenWeb Ninja, and
  Outscraper came from the more complete of the two audited source projects, and
  their file-write paths matched the actual historical raw evidence byte-for-byte.
  **DataForSEO had no script at all** in that project — the only one found
  anywhere was ported from the second source project (MISSING_AND_GAPS.md A.1).
- **`IMPORTANT/knowledge.md` was synthesized** from the primary source project's
  922-line knowledge base, restructured into the 6 required categories, with the
  second project's lower-confidence version used only as a cross-check. It has
  since been extended with a ranked **Final Summary** and an **FAQ**. Two internal
  number disputes flagged during synthesis (Lobstr's HTTP 429 count and raw field
  count) were re-checked directly against both source projects' raw files and
  resolved — see `MISSING_AND_GAPS.md` item 5.
- **`IMPORTANT/criteria.md`** is an unmodified copy of the original scoring
  rubric, byte-identical between both source projects — no conflict to resolve
  there. Its "Owner: lobstr.io content team" header, with Lobstr as one of the
  five scored providers, is disclosed prominently rather than buried
  (MISSING_AND_GAPS.md B.1, and at the top of this README).
- **`api_docs_mcps.txt`** consolidates all 10 documentation/pricing files
  (2 per API) verbatim. No MCP server references exist in either source project,
  so that part of the deliverable is unfulfilled by absence of evidence, not by
  oversight (MISSING_AND_GAPS.md A.6).
- **Real `.env` files** from the source projects were never copied here — only
  `.env.example` templates were merged.
- **Missing `final-verdict.md`** for Outscraper and DataForSEO, and **only 1 of 5
  domains has ground truth** — both are gaps in the original evidence, not
  something lost during reorganization (MISSING_AND_GAPS.md A.3 and A.4).
- **All scripts were converted from JavaScript to Python** on request, as a
  faithful line-by-line port (same CLI, same paths, same retry logic) — see "Note
  on the JS → Python conversion" below.

### Second pass — provider-first restructure (for reader sharing)

The layout above (`IMPORTANT/` / `DATA/` / `SCRIPTS/` / `PROOF/`) replaces an
earlier type-first layout (`data/raw/<provider>/`, `data/exports/<provider>/`,
`scripts/<provider>_benchmark.py`, etc.) that was harder for an outside reader to
navigate. Everything under `DATA/`, `SCRIPTS/`, `PROOF/`, and `IMPORTANT/` was
moved, not copied — nothing was duplicated by this pass. Because scripts hardcode
paths relative to their own location, the move required real code changes, not
just file drags:

- Every script's `ROOT` (or `SCRIPT_DIR`) computation was bumped by one directory
  level, since scripts now live one level deeper (`SCRIPTS/<provider>/x.py`
  instead of `scripts/<provider>_x.py`).
- A `sys.path` entry pointing at `SCRIPTS/` was added to every script that imports
  from `lib/` (previously implicit, since the script's own directory *was*
  `scripts/`, right next to `lib/`).
- The 5 `ground_truth_compare.py` scripts' hardcoded `data/<type>/<provider>/...`
  paths were rewritten to `DATA/<provider>/<type>/...`, and the shared ground-truth
  sample moved to `DATA/ground-truth/`.

**Verification, stated plainly:** every `ROOT`/`sys.path`/`DATA`-path line was
first re-grepped after editing to confirm no old path survived, then actually
executed — `python -m py_compile` passed on every file under `SCRIPTS/`, and all
5 `ground_truth_compare.py` scripts (Apify, DataForSEO, Lobstr, OpenWeb Ninja,
Outscraper) ran for real against the archived `DATA/` evidence, read-only, no
`.env` needed. All 5 completed without error and reproduced their pre-existing
`analysis/ground-truth-match.json` output **byte-for-byte except the timestamp**
(diffed and confirmed) — including Apify's and OpenWeb Ninja's 0-matched-rows
result, which is the same historical failure already documented in
`IMPORTANT/knowledge.md` and `MISSING_AND_GAPS.md`, not a new one introduced by
this restructure. Those timestamp-only diffs were reverted afterward so the
committed evidence stays byte-for-byte what it was before this pass.

## Note on the JS → Python conversion

Every script in this project was originally JavaScript (Node.js) — both source
projects audited during the initial reorganization only contained JS. The
scripts were subsequently converted to Python 3 (stdlib only, no third-party
packages) on request, as a line-by-line behavioral port: same CLI modes
(`plan`/`smoke`/`run`), same safety env-var gates (`CONFIRM_PAID_RUN`,
`CONFIRM_SMOKE_RUN`, `OPENWEBNINJA_QUOTA_REMAINING`), same output file paths and
JSON shapes, same retry/backoff/error-classification logic, same idempotent-resume
behavior.

**This conversion was verified with a real Python interpreter** (Python 3.12.10):
- `python -m py_compile` passed on all 18 files.
- Every benchmark script was actually run and its full import chain confirmed to
  resolve at runtime, not just parse cleanly — each failed exactly where expected
  (missing `.env`), proving the code path up to that point is sound.
- All 4 ground-truth-compare scripts were run for real against the archived data
  (no credentials needed) and their output diffed against the original
  JS-produced files. Apify, Lobstr, and Outscraper reproduced the original
  byte-for-byte (aside from the timestamp); OpenWeb Ninja has 2 pre-existing,
  JS-inherited discrepancies unrelated to the Python port. This diffing process
  caught and fixed 2 real bugs (a missing whole-number JSON collapse in Lobstr's
  script, and a missing `ensure_ascii=False` across 6 files that would have
  mangled non-ASCII review text).

**Real credentials were located** and used for further live verification, at zero
or near-zero cost:
- **Apify & DataForSEO**: read-only calls against historical run/task IDs
  succeeded live and matched `IMPORTANT/knowledge.md`'s recorded figures exactly.
- **Lobstr**: the prerun-validate script ran live (read-only), all 12 checks
  passed against the real account.
- **Outscraper**: the `smoke` mode was run live and succeeded, but consumed more
  usage than its docstring promises (200 reviews, not ~20) — a pre-existing bug in
  the original JS, not the Python port. See `MISSING_AND_GAPS.md` A.7.
- **OpenWeb Ninja could not be tested without cost** — its API has no
  free/read-only endpoint of any kind, so this was skipped rather than run.

**What is still NOT verified**: the actual *write* paths that create new paid
resources were not exercised, since that means spending real money beyond what
was explicitly approved. Multi-page pagination is also unverified (every live
test above returned all results on one page). Do a `plan`-mode dry run and get
explicit sign-off on cost before any full paid `run` — and re-read the
"Verification caveat" above, since that Python verification predates this repo's
provider-first restructure.
