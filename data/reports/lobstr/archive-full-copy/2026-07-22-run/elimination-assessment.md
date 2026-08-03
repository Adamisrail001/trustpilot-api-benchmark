# Lobstr.io Trustpilot Reviews — Elimination Assessment (E1–E6)

Applied per `docs/testing-criteria.md` §3, after the completed, corrected benchmark run.

| # | Criterion | Result | Evidence |
|---|---|---|---|
| E1 | No self-serve access | **PASS** | API key worked immediately for every call across both attempts. |
| E2 | Benchmark run failure (success rate < 50%, or breaks mid-run) | **PASS** | 100% success rate (1,000/1,000). The Run itself never failed at the platform level — the earlier blocker was our own orchestration bug (squid renaming), already fixed and documented separately. |
| E3 | No usable documentation | **PASS, with one flagged gap** | Every endpoint/param matched documented behavior except one: `/v1/results`' `limit` param is documented as configurable but was observed silently capped at 10 regardless of the requested value (100) — a real documentation-accuracy gap, but not severe enough to call the documentation unusable (everything else was accurate, and the cap was discoverable from the response's own `limit`/`total_pages` fields). |
| E4 | Uncomputable cost | **PASS** | Credit-based cost is fully computable and precisely confirmed (1,000 credits for 1,000 reviews, verified two independent ways). The dollar-equivalent rate is Pending only because this specific account's Super Admin terms aren't exposed via any documented field — the pricing *model* itself is transparent. |
| E5 | Platform coverage failure | **PASS** | Returns the richest review schema (37 fields) of any tool tested, with 92.3% ground-truth field coverage. |
| E6 | Dead or abandoned | **PASS** | Actively responsive, real-time data, confirmed fresh via 3-tool cross-validation. |

## Result: Lobstr.io is **not eliminated**.
