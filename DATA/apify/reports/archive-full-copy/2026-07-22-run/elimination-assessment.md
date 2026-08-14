# Apify (automation-lab/trustpilot) — Elimination Assessment (E1–E6)

Applied per `docs/testing-criteria.md` §3, after the completed benchmark run.

| # | Criterion | Result | Evidence |
|---|---|---|---|
| E1 | No self-serve access | **PASS** | API token from `.env` worked on the very first live request; no manual approval step. |
| E2 | Benchmark run failure (success rate < 50%, or breaks mid-run) | **PASS** | Measured success rate 79.8% (798/1,000) — above the 50% threshold. The run itself completed cleanly (`SUCCEEDED`, zero HTTP errors, zero retries) — it did not break mid-run; it simply returned nothing for one of five domains. |
| E3 | No usable documentation | **PASS** | A complete implementation was built entirely from the provided official documentation; every endpoint/param/response field matched live behavior on 4 of 5 domains with zero discrepancies. |
| E4 | Uncomputable cost | **PASS** | Fully transparent pay-per-event pricing; the published formula predicted the measured `usageTotalUsd` ($0.465) within 0.3%. |
| E5 | Platform coverage failure (doesn't return the core data type) | **PASS** | Returns rich Trustpilot review objects (26+ documented fields, the most of any tool tested) for 4 of 5 domains. The SHEIN failure is a per-domain reliability gap, not evidence the platform can't return the core data type — it does, robustly, everywhere else. |
| E6 | Dead or abandoned | **PASS** | Actively maintained (build 0.1.44 reviewed), responded correctly and quickly throughout the run. |

## Result: Apify (automation-lab/trustpilot) is **not eliminated**. Proceed to scoring.

**Note on E2/E5 borderline judgment:** the SHEIN gap is a real, unexplained finding (see `missing-evidence.md`) and is reflected as a heavy penalty in the Reliability and Developer Experience scorecard criteria (specifically: the silent, unerrored nature of the failure), rather than as grounds for elimination — 79.8% overall success and a clean run-completion status are both comfortably above the elimination bar.
