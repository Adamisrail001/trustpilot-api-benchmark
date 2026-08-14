# Lobstr.io Trustpilot Reviews — Missing / Pending Evidence

## Blocking issue (must be resolved before any further attempt)

- **Squid-name collision:** the clean squid `8d9e0b80d6d2481283c138104caf022d` cannot be configured under the name `"Trustpilot API Benchmark - Lobstr"` because the old contaminated squid `5644e83e28ce412c9370da2bc46fcd31` already holds that exact name on the live Lobstr account. This must be resolved (rename one of the two squids, or change the benchmark's configuration-step name) before a retry.

## Everything downstream of that (all Pending, none tested this attempt)

- All 5 domains' review counts, shortfalls, and validity
- Duplicate detection results
- Ground-truth comparison for `www.thepearlsource.com`
- Field coverage
- Timing/latency distribution beyond the single 238ms measured call
- Actual credit consumption for a real run
- E4 (cost) and E5 (platform coverage) elimination criteria
- A provisional `/10` score

## What would resolve this

1. Decide how to handle the name collision (see `final-verdict.md`).
2. Get explicit approval to retry the full run.
3. Re-run `CONFIRM_PAID_RUN=yes node scripts/lobstr-benchmark.js run` and let it proceed through task creation, one Run, polling, and result retrieval.
