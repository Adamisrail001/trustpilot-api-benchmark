# Scraper Data Comparison Model — Spec v1.2

A reusable methodology for scoring and comparing the **data output** of 2+ scrapers
that target the same platform. Designed to be consumed by Claude Code as the basis
for a scoring plugin.

Scope: this spec covers the **Data** pillar only (quality, completeness, correctness,
structure). It does not cover cost, speed, usability, or support.

> **Changelog v1.2** — added capture-time equivalence as a second axis (§3b) with graded
> tiers that scope/demote timing-sensitive dimensions; accuracy now scored over a *sample*
> of matched records rather than the single common record (§6b, §8.4); baseline selection
> hardened against the later-run accrual bias (§5); added `captured_at` and `volatile`
> inputs (§4) and a `timing` block to the output schema (§13); corrected the Lite worked
> example arithmetic (§12).
>
> **Changelog v1.1** — added Full/Lite modes (§2); relaxed the identical-input hard rule
> to a target-equivalence ladder with graceful degradation (§3); added Lite-mode weights (§12).

---

## 1. Purpose

Given the JSON (and optionally CSV) outputs of multiple scrapers run against the
**same target**, produce:

1. A per-dimension score `0–10` for each scraper across the dimensions the chosen mode covers.
2. A weighted **composite Data Quality Score** `0–10` per scraper.
3. A structured report (see §12) that is reproducible and defensible in a public article.

---

## 2. Modes

Two run modes. **Pick one per comparison, and use the same mode for every scraper in that
comparison** — composite scores from different modes are not comparable and must never be
ranked against each other.

### Full mode — keys **and** values
Runs all 7 dimensions. Requires alignable records and value-level verification. Use when
inputs are equivalent and outputs can be mapped field-for-field.

### Lite mode — keys / structure only, **no value verification**
Runs the 4 structural dimensions only: **fill rate, record completeness, consistency
(schema-only), breadth + cardinality.** Drops the 3 value-level dimensions: **accuracy,
normalization, freshness.**

Use Lite when: inputs can't be perfectly aligned, outputs differ too much to map values
field-for-field, value-level ground truth isn't feasible, or you just need a fast pass.

| # | Dimension | Full | Lite | Lite behavior change |
|---|---|---|---|---|
| 1 | Fill rate | ✅ | ✅ | none (already key-presence based) |
| 2 | Record completeness | ✅ | ✅ | none |
| 3 | Consistency | ✅ | ✅ | schema/field-set stability only; value drift ignored |
| 6 | Breadth + Cardinality | ✅ | ✅ | none |
| 4 | Accuracy | ✅ | ❌ | — |
| 5 | Normalization | ✅ | ❌ | — |
| 7 | Freshness | ✅ | ❌ | — |

The report must state which mode was used.

---

## 3. Target Equivalence (relaxed input rule)

Identical byte-for-byte input isn't always possible — scrapers take different handles
(URL vs ID vs search query) and return different shapes. Instead of voiding the run,
degrade gracefully down this ladder:

| Level | Condition | Action |
|---|---|---|
| **A. Ideal** | Identical input + records align 1:1 | Full mode valid |
| **B. Equivalent** | Same target entity, different input handle; records still align on a stable ID | Full mode valid — **note the input difference** |
| **C. Degraded** | Outputs can't be value-aligned (different field semantics, unmappable fields) | Drop to **Lite mode** |
| **D. Floor** | No overlap set can be established at all | Not a valid comparison — describe each scraper's structure, **emit no scores** |

The only true blocker is level D. Everything above it produces a valid, labeled result.
Always record which level the run sat at.

---

## 3b. Capture-Time Equivalence (a second, orthogonal axis)

The §3 ladder grades *input-handle* equivalence and silently assumes all scrapers were
captured at the same moment. In practice they often aren't — a subscription lapse or
platform issue can push one scraper's run hours, days, or a week later. This is a
**separate axis**: a run can be level-A on input (identical IDs) yet badly skewed in time.

Timing skew corrupts a comparison **only where the signal is a value or a count** — never
where it's structural. The gap between the earliest and latest capture picks a tier:

| Tier | Capture gap | Effect |
|---|---|---|
| **Negligible** | ≤ 1 hour | Treat as simultaneous. No adjustment. |
| **Moderate** | ≤ 48 hours | Accuracy scored on **stable (non-volatile) fields only**; cardinality kept but flagged lower-confidence. |
| **Large** | > 48 hours (days/weeks) | As moderate, **plus** completeness, cardinality and freshness demoted to `N/A` and reweighted (§11). |

Which dimensions survive a gap, and why:

- **Timing-robust — keep with confidence:** *fill rate* (whether a field is populated
  doesn't change because its value changed), *breadth* (the field set is a schema property),
  *normalization* (formatting habits are value-independent), *consistency* (an intra-scraper
  measure over back-to-back reruns, insulated from cross-scraper stagger).
- **Timing-sensitive — scope or demote:** *accuracy* (a value disagreement may just be the
  world changing between captures), *completeness* and *cardinality* (records/reviews accrue
  over time), *freshness* (meaningless across staggered captures by construction).

**The accrual bias (important).** A delay is not random noise — the scraper that runs *later*
sees more accumulated data and will look more complete, higher-cardinality and fresher purely
for running second. This is directional and easy to miss. Guard against it: (1) never let
record count drive baseline selection under a gap — pick baseline on field-path richness (§5);
(2) disclose capture order, or run the baseline scraper first.

**Escape hatch — reconstruct the overlap set.** If the platform exposes stable per-record IDs
and old records don't mutate or get deleted, rebuild a fair overlap set after the fact:
intersect on ID and keep only records that already existed at the *earlier* capture, discarding
everything the later run accrued. This restores a like-for-like comparison on the shared
records (smaller sample, but honest). Works well for reviews, where old ones rarely change.

**Bottom line.** A large gap yields a solid verdict on data *structure and formatting* and a
weak-to-unusable one on data *values and counts*. Report the structural dimensions as the
answer; label the value/count dimensions timing-limited rather than publishing a number that
is really measuring who ran second. Always record the capture gap and tier.

---

## 4. Inputs

| Input | Required | Notes |
|---|---|---|
| `scraper_outputs` | yes | 2+ named scrapers, each a JSON array/object of records. |
| `mode` | yes | `full` or `lite` (§2). |
| `csv_outputs` | optional | Per-scraper CSV, if offered. Used only for the export check (§10). |
| `target` | yes | Platform + the exact listing(s)/query used, per scraper. |
| `equivalence_level` | yes | A–D from §3. |
| `live_page_reference` | optional | Manual notes or Playwright capture, for full-mode spot-checks. |
| `rerun_outputs` | optional | 3× outputs of the same request per scraper, for consistency. |
| `captured_at` | optional (per scraper) | ISO 8601 timestamp of when each scraper was run. Drives the capture-time tier (§3b). Set on ≥2 scrapers or the gap is treated as unknown/simultaneous. |
| `volatile_fields` | optional | Canonical field names whose values change over time (helpful votes, aggregate rating, price, availability). Excluded from accuracy under a capture gap. Also settable per-field via `"volatile": true` in the field map. |

---

## 5. The Oracle (ground truth)

Verifying every field against the live page is **not required** — some scrapers return
the platform's internal API layer, which contains data not visible on the frontend.

Instead: **baseline against the most complete scraper's response.** In practice one
scraper reliably returns the superset of fields; that response is the de facto oracle.

**Two guards (full mode):**

1. **Disclose it.** The article must state "we baseline against the most complete response."
2. **Spot-check the baseline** against the live page on a few fields. Confirm
   *richest = correct*, not *richest = hallucinating extra keys*.

The baseline's fill rate and breadth are ~10 by definition — it is the reference, not a
competitor to itself. Say so. In Lite mode the baseline is still used for breadth/fill
denominators; the value spot-check is skipped.

**Under a capture-time gap (§3b), pick the baseline on field-path richness, not record
count.** "Most complete" can otherwise just mean "ran latest and accrued more records" —
the later scraper wins the oracle role for a reason that has nothing to do with quality.
Selecting on distinct key paths (a schema property) is timing-safe; selecting on record
or element counts is not.

---

## 6. The Two Datasets

Every metric runs on exactly one of these. Do not mix them.

### 6a. Overlap set — carries the *rates*
Every record returned by **all** scrapers under test. Denominator-bearing dataset for any
ratio metric (fill rate, completeness, consistency). Used in both modes.

### 6b. One common record — carries the *depth*
A **single** record present in all outputs, **deliberately chosen** to exercise nested
structures (reviews, multiple images, variants). A sparse record hides the exact
differences the comparison exists to show. Used for breadth/cardinality in both modes,
and for normalization in Full mode.

> Article ordering: lead with aggregate rates (trust), then zoom into the one record
> (illustration) so the reader *sees* the difference instead of trusting a number.

> **Accuracy does NOT score on this record.** The common record is *deliberately biased*
> — chosen for richness and narrative punch — which makes it perfect for illustration but
> wrong for measurement: one record can't tell you whether a field is generally correct.
> Accuracy is scored on a **sample** drawn from the overlap set (§8.4). Keep the single
> rich record for the article's zoom-in; measure accuracy across the sample.

---

## 7. Counting — always two numbers, never one

For dimension 6, compute **both** and report them side by side.

**Schema breadth** — distinct key *paths* in dot-notation, array indices collapsed.
`reviews[].author` counts **once**, regardless of how many reviews exist.

**Cardinality** — for each repeated collection, how many elements are actually populated.
This is where "5 reviews vs 50 reviews" surfaces.

Breadth answers *how many field types*. Cardinality answers *how much data per collection*.

---

## 8. Metric Definitions

### 1. Fill rate (overlap set — both modes)
Per field, `populated / actually_available` (availability defined by baseline).
Score = mean fill rate × 10. Key-presence based, so identical in both modes.

### 2. Record completeness (overlap set — both modes)
`records_returned / records_expected` (expected = baseline's count). Score = ratio × 10.

### 3. Consistency (overlap set, needs `rerun_outputs` — both modes)
Run the same request 3×, diff. **Full:** schema + value stability. **Lite:** schema /
field-set stability only, value drift ignored. Rubric §9. If reruns unavailable → `N/A`, reweight.

### 4. Accuracy (sample of the overlap set — Full only)
Scored over a **sample of matched records** (default 30–50; `accuracy_sample_size`, engine
default 40), **not** the single common record — one deliberately-rich record can't measure
whether values are generally correct, and its bias would define the score.

Method: for each sampled record present in both baseline and the scraper, compare mapped
non-collection fields against baseline (and the live page where frontend-visible). Wrong
currency, truncation, off-by-magnitude, stale values = incorrect.
`accuracy = correct_field_comparisons / total_field_comparisons` across the sample.
Score = ratio × 10. The engine emits raw string mismatches per field plus examples;
Claude judges which are true errors vs legitimate differences before scoring.

**Under a capture-time gap (§3b):** volatile fields (`volatile_fields` / per-field
`volatile:true`) are **excluded** — a disagreement on a helpful-vote count or price may
just be the value moving between captures, not a scraper error. Accuracy then reflects
stable fields only, and the report says so.

### 5. Normalization (common record — Full only)
Checklist, §9. Score = `(criteria_met / 8) × 10`.

### 6. Breadth + Cardinality (common record — both modes)
`breadth_ratio = key_paths / baseline_key_paths`
`cardinality_ratio = mean over collections of min(1, elements / baseline_elements)`
`score = (0.5 × breadth_ratio + 0.5 × cardinality_ratio) × 10`
Report both sub-scores explicitly, not just the combined number.

### 7. Freshness (manual / where possible — Full only)
Live vs cached, banded §9. Tag "measured where possible, N/A otherwise." Undeterminable → `N/A`, reweight.

### Timing sensitivity per dimension (§3b)

| Dimension | Under a capture gap |
|---|---|
| Fill rate | Robust — keep. |
| Breadth | Robust — keep. |
| Normalization | Robust — keep. |
| Consistency | Robust (intra-scraper reruns) — keep. |
| Accuracy | Scope to stable fields (moderate + large). |
| Cardinality | Flag (moderate); demote to `N/A` (large). |
| Completeness | Keep (moderate); demote to `N/A` (large). |
| Freshness | Demote to `N/A` (large). |

---

## 9. Scoring Rubric (0–10)

### Rate-based (1 Fill rate, 2 Completeness, 4 Accuracy)
`score = ratio × 10`, 1 decimal. Reference bands:

| Band | Ratio | Meaning |
|---|---|---|
| 9–10 | ≥ 0.90 | Near-complete / near-perfect |
| 7–8.9 | 0.70–0.89 | Strong, minor gaps |
| 5–6.9 | 0.50–0.69 | Usable but leaky |
| 3–4.9 | 0.30–0.49 | Significant loss |
| 0–2.9 | < 0.30 | Fails the dimension |

### 3. Consistency

| Score | Full mode | Lite mode |
|---|---|---|
| 10 | Identical schema **and** values across 3 runs | Identical schema / field-set |
| 7–9 | Schema identical; only volatile fields drift | (values ignored) |
| 4–6 | Field-set or stable-field values vary | Field-set varies mildly |
| 1–3 | Schema / field-set changes between runs | Schema changes between runs |
| 0 | Errors or fails on rerun | Errors or fails on rerun |

### 5. Normalization checklist (8 criteria, ×10 / 8) — Full only

1. Numbers typed as numbers, not strings
2. Dates in ISO 8601
3. Currency amount and code separated
4. No HTML tags / entities in text fields
5. No leading/trailing whitespace or junk
6. Atomic fields (no concatenated blobs)
7. Consistent key naming convention
8. Proper `null`, not `""` or `"N/A"` strings

### 6. Breadth + Cardinality
Formula in §8. Continuous ratio vs baseline, no bands.

### 7. Freshness — Full only

| Score | Condition |
|---|---|
| 10 | Live / real-time |
| 7–9 | Cached < 1 hour |
| 4–6 | Cached < 24 hours |
| 1–3 | Cached > 24 hours |
| N/A | Cannot determine → exclude and reweight |

---

## 10. Null Handling & CSV

**Nulls** (fill rate + completeness denominators):
- Null in all scrapers AND absent on the live record → genuine null, **drop from denominator.**
- Null in one scraper but present in another → real miss, counts against it.

**JSON is canonical for all structural metrics.** CSV is flat, strips types, can't hold
nested arrays. CSV gets one check — **export round-trip:** does it reproduce the JSON
without silent loss? Drops nested data → usability ding (not a schema score). CSV-only →
consumption-limitation flag.

---

## 11. Rollup & Weighting

Composite = weighted sum of the covered dimensions, 0–10 scale. **Declare weights in the article.**

### Full-mode weights

| Dimension | Weight |
|---|---|
| Accuracy | 0.25 |
| Record completeness | 0.20 |
| Fill rate | 0.20 |
| Breadth + Cardinality | 0.15 |
| Consistency | 0.10 |
| Freshness | 0.05 |
| Normalization | 0.05 |
| **Sum** | **1.00** |

### Lite-mode weights (value dimensions dropped, reweighted /0.65)

| Dimension | Weight |
|---|---|
| Fill rate | 0.308 |
| Record completeness | 0.308 |
| Breadth + Cardinality | 0.231 |
| Consistency | 0.154 |
| **Sum** | **1.00** |

**Reweighting rule (any `N/A` dimension, either mode):** drop its weight, divide every
remaining weight by the new sum so weights total 1.00, then compute the composite over
available dimensions only.

---

## 12. Worked Example (Full mode)

Target: one product listing with reviews, images, variants. Three scrapers **A, B, C**.
**A returns the superset → A is the baseline** (spot-checked clean; equivalence level A).

### Raw findings

| Signal | A (baseline) | B | C |
|---|---|---|---|
| Fill rate (overlap) | ~1.00 | 0.82 | 0.61 |
| Records returned / 40 | 40 | 38 | 33 |
| Consistency (3 runs) | identical | schema stable, minor drift | field-set varies |
| Accuracy (fields correct) | 20/20 spot | 16/20 | 12/20 |
| Normalization criteria met | 8/8 | ~5/8 | ~3/8 |
| Key paths / 42 | 42 | 34 | 26 |
| Cardinality (reviews/images/variants) | 50/6/3 | 20/4/3 | 5/2/3 |
| Freshness | live | cached ~1 day | undeterminable |

### Derived scores

| Dimension | Weight | A | B | C |
|---|---|---|---|---|
| Accuracy | 0.25 | 9.5 | 8.0 | 6.0 |
| Completeness | 0.20 | 10.0 | 9.5 | 8.25 |
| Fill rate | 0.20 | 10.0 | 8.2 | 6.1 |
| Breadth + Cardinality | 0.15 | 10.0 | 7.5 | 5.5 |
| Consistency | 0.10 | 10.0 | 8.0 | 5.0 |
| Freshness | 0.05 | 10.0 | 5.0 | N/A |
| Normalization | 0.05 | 9.0 | 6.0 | 4.0 |
| **Composite /10** | | **9.8** | **8.0** | **6.2** |

**Breadth + Cardinality, B:** breadth 34/42 = 0.81 → 8.1; cardinality mean(20/50, 4/6, 3/3)
= 0.69 → 6.9; combined 0.5×8.1 + 0.5×6.9 = **7.5**.

**Breadth + Cardinality, C:** breadth 26/42 = 0.62 → 6.2; cardinality mean(5/50, 2/6, 3/3)
= 0.48 → 4.8; combined = **5.5**.

**Composite, C (freshness N/A → reweight over 0.95):**
`(6.0×0.263)+(8.25×0.211)+(6.1×0.211)+(5.5×0.158)+(5.0×0.105)+(4.0×0.053) = 6.2`.

### Same three, Lite mode
Only Fill, Completeness, Breadth+Card, Consistency survive. Reweight the *exact* Full
weights over their new sum (0.65) — `0.20/0.65 = 0.30769`, `0.15/0.65 = 0.23077`,
`0.10/0.65 = 0.15385` — not the 3-decimal display values, or you drift a few hundredths:
- **B:** (8.2×0.30769)+(9.5×0.30769)+(7.5×0.23077)+(8.0×0.15385) = **8.41**
- **C (consistency stands, nothing N/A):** (6.1×0.30769)+(8.25×0.30769)+(5.5×0.23077)+(5.0×0.15385) = **6.45**

> Compute with the exact fractions, the way the engine does. Using the rounded weights
> (0.308 / 0.231 / 0.154) gives ≈8.44 / ≈6.42 — close, but the engine's exact reweighting
> is authoritative, so the report must match 8.41 / 6.45.

Note B and C score *higher* in Lite — value-level weaknesses (accuracy, normalization,
freshness) are simply not measured. This is exactly why modes must never be cross-ranked.

---

## 13. Suggested Output Schema

```json
{
  "mode": "full | lite",
  "equivalence_level": "A | B | C | D",
  "target": "platform + listing/query used",
  "baseline_scraper": "A",
  "baseline_disclosed": true,
  "baseline_spotcheck_passed": true,
  "datasets": {
    "overlap_set_size": 40,
    "common_record_id": "the deliberately chosen record"
  },
  "timing": {
    "gap_hours": 168.0,
    "tier": "negligible | moderate | large | unknown",
    "accuracy_stable_only": true,
    "cardinality_dropped": true,
    "demote_to_na": ["completeness", "freshness"],
    "volatile_fields": ["helpful_votes", "aggregate_rating"]
  },
  "scrapers": [
    {
      "name": "B",
      "captured_at": "2026-06-13T09:00:00Z",
      "dimensions": {
        "fill_rate": 8.2,
        "completeness": 9.5,
        "consistency": 8.0,
        "breadth_cardinality": { "breadth_score": 8.1, "cardinality_score": 6.9, "combined": 7.5 },
        "accuracy": 8.0,
        "normalization": 6.0,
        "freshness": 5.0
      },
      "na_dimensions": ["completeness", "freshness"],
      "weights_used": { "note": "full or lite table, reweighted for any N/A" },
      "composite": 8.0,
      "flags": ["dates not ISO", "csv drops nested reviews", "input handle differed (level B)",
                "capture gap 168h (large): completeness/cardinality/freshness timing-limited"]
    }
  ]
}
```

Notes: in Lite mode, omit `accuracy`, `normalization`, `freshness` from `dimensions`
(don't null them). Under a large capture gap the `timing.demote_to_na` dimensions move to
`na_dimensions` and are reweighted out (§11). A field can be marked `"volatile": true` in
the field map, or listed under top-level `volatile_fields`.

---

## 14. Non-negotiables (for the plugin author)

1. Equivalent target per §3; degrade full→lite rather than voiding, floor only at level D.
2. One mode per comparison; never cross-rank Full vs Lite composites.
3. Baseline disclosed; spot-checked in Full mode before use.
4. Rates on the overlap set; depth on the deliberately-chosen common record. Never swap.
5. Accuracy scored on a sample of the overlap set, never on the single common record.
6. Breadth and cardinality reported as two numbers.
7. Genuine nulls dropped from denominators.
8. JSON canonical for structure; CSV is an export round-trip check only.
9. Weights declared; `N/A` dimensions and Lite mode both trigger reweighting.
10. All scores on a 0–10 scale.
11. Record the capture gap and tier (§3b). Under a gap: scope accuracy to stable fields,
    demote timing-sensitive dimensions per the tier, never cross-rank across timing tiers,
    and select the baseline on field-path richness rather than record count.