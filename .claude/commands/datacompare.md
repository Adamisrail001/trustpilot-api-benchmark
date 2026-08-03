Run a scraper data-output comparison (the Data pillar) for: $ARGUMENTS

This command scores and compares the **data output** of 2+ scrapers (or a scraper vs an official API) that target the same platform, using the methodology in `data-comparison-model.md`. It produces a reproducible, defensible Data-pillar artifact that `/listicle` and scraper-vs-API articles consume. It does NOT write the article and NEVER edits `knowledge.md`.

`$ARGUMENTS` is the article folder name (e.g. `bestyelpreviewsscrapers`), optionally followed by `mode=full|lite`.

## Step 0: The split (read this first)

The arithmetic is done by `datacompare.py` (deterministic, reproducible). The judgment calls are yours (accuracy, normalization, freshness, the baseline spot-check, the field map). NEVER hand-compute a fill rate, ratio, or composite yourself, and never override a script number with a guess. Your job is the judgment the script can't make, plus the honest write-up.

## Step 1: Facts + spec

Read `data-comparison-model.md` (repo root) once. It is the authoritative spec for every metric, mode, and rule the script implements; this command only orchestrates it. For evergreen brand facts read `facts.md`. Do not load `instructions/` or `*_samples/`.

Never invent, speculate, or fill gaps. If a required input is missing (see §2), list exactly what's missing and ask Shehriar for that one thing. Judgment scores you assign (accuracy, normalization, freshness) must trace to the script's diffs/pre-checks or to something Shehriar or the live page confirmed, never to a guess.

## Step 2: Locate inputs + config

Data lives in `content/{articlefolder}/data/` (fall back to the article folder root if there's no `data/`, then ask if neither has the files). The config is `<dir>/datacompare.config.json`. See `datacompare.config.example.json` (repo root) for the annotated shape.

Required config: `target`, `mode`, `equivalence_level` (A-D, §3 of the spec), `id_field` (per scraper if names differ), `common_record_id` (a deliberately data-rich record present in all outputs, §6b), the `scrapers` list, and `exclude_paths` (the plumbing to strip: internal IDs, run/job metadata, listing data duplicated onto every row - "raw column counts lie"). Optional but strongly recommended for Full mode: the `fields` map (the canonical field universe with each scraper's key path).

Timing inputs (§3b): `captured_at` per scraper (ISO 8601 run time, needed on ≥2 scrapers or the gap counts as unknown) and `volatile_fields` (or per-field `"volatile": true` in the map) for values that move over time (helpful votes, aggregate rating, price, availability). If the runs were staggered, get the real timestamps from Shehriar — the gap sets the tier (≤1h negligible / ≤48h moderate / >48h large) and the tier decides which dimensions survive. Also optional: `accuracy_sample_size` (accuracy sample, default 40), `skip_dimensions` (drop a dimension by choice, reweighted like an N/A), `records_expected`, `verdict`.

If the config is absent, offer to scaffold it: auto-detect each output file's records array + id field, propose `exclude_paths` from obvious plumbing, and confirm `mode`/`target`/`common_record_id`/`captured_at` with Shehriar before writing it. Never assume the mode.

## Step 3: Signals (deterministic pass)

Run: `python datacompare.py signals --dir content/{articlefolder}/data`

Read `signals.json`, then act on it:

- **Warnings.** An `EMPTY OVERLAP SET` warning means the run is at the level-D floor: stop, do not produce scores, describe each scraper's structure instead, and tell Shehriar the ids don't align.
- **No field map** (`field_map_provided: false`). The script emits `suggested_field_map`. Full-mode fill rate, accuracy, and normalization need a real map because field names differ across scrapers (`review_text` / `text` / `TEXT`). Present the suggestion to Shehriar with the low-confidence rows called out, get the alignments confirmed (never guess equivalences silently), paste the confirmed `fields` block into the config, and re-run signals. If he can't/won't map, drop to Lite mode (structure only) per the equivalence ladder rather than voiding the run.
- **Baseline.** If auto-selected, disclose it. In Full mode, spot-check the baseline against the live page on a few frontend-visible fields (Playwright MCP, or ask Shehriar, or use notes in `knowledge.md`) to confirm richest = correct, not richest = hallucinating extra keys. Record the result for `baseline_spotcheck_passed`.
- **Timing** (`timing` block). The capture gap picks the tier. `moderate` (≤48h): accuracy is auto-scoped to stable fields; treat cardinality as lower-confidence in the write-up. `large` (>48h): completeness + freshness get demoted to N/A at rollup and cardinality is dropped (breadth alone carries the combined score) — honor the demotions, never score them back in; the later run accrues records, so confirm the baseline was picked on field-path richness, not record count, and disclose capture order in the report. If the platform has stable IDs and old records don't mutate, offer Shehriar the §3b escape hatch: rebuild the overlap set on records that already existed at the earlier capture. `unknown` (timestamps on <2 scrapers): ask Shehriar for the real run times instead of assuming simultaneous. Structural dimensions (fill, breadth, normalization, consistency) are timing-robust — report them as the answer; label the value/count dimensions timing-limited.

## Step 4: Judgment (Full mode only for the value dimensions)

Read the raw material the script computed and assign the value-dimension scores. Write them to `<dir>/judgments.json` (shape below).

- **Accuracy** (`accuracy_diffs` per scraper). Scored over a SAMPLE of matched overlap records (`sampled_records`, default 40) — never the single common record, which is deliberately rich and would bias the score (§8.4). The script aggregates raw string mismatches across the sample (`mismatch_by_field` + up to 15 examples); its `raw_match_ratio` is plain string inequality, NOT the score. Judge which mismatches are real errors (wrong currency, truncation, off-by-magnitude, stale value) vs legitimate differences (formatting, equivalent encodings), then `score = correct_field_comparisons / total_field_comparisons * 10` across the sample. Where a field is frontend-visible and disputed, verify against the platform directly. Under a capture gap the script already skipped volatile fields (`skipped_volatile_fields`) — the report must say accuracy reflects stable fields only.
- **Normalization** (`normalization_prechecks` per scraper). The script pre-flags the mechanical criteria (numeric-as-string, non-ISO dates, glued currency, HTML in text, whitespace junk, `"N/A"` strings). Confirm those and judge the two fuzzy ones (atomic fields, consistent key naming). `score = criteria_met / 8 * 10`.
- **Freshness.** Live vs cached, banded per the spec. Needs a live/timestamp reference; if undeterminable, set `"N/A"` and it will be reweighted out. Under a large capture gap it's demoted at rollup automatically — don't score it.
- **Consistency.** The script suggests a band from the rerun diff (`suggested_score`, `schema_identical`, `value_drift_pct`, `drifting_fields`). In Full mode confirm or adjust it (drift confined to volatile fields like view counts = 7-9). In Lite mode it's schema-only. No reruns = leave it out (`N/A`).

`judgments.json`:
```json
{
  "baseline_disclosed": true,
  "baseline_spotcheck_passed": true,
  "scrapers": [
    { "name": "B", "accuracy": 8.0, "normalization": 6.0, "freshness": 5.0, "consistency": 8.0,
      "flags": ["dates not ISO", "csv drops nested reviews", "input handle differed (level B)"] }
  ]
}
```
Only include `accuracy`/`normalization`/`freshness` in Full mode. Omit any value you're setting to N/A, or pass the string `"N/A"`. `consistency` is optional (defaults to the script's suggested band).

## Step 5: Rollup (deterministic composite)

Run: `python datacompare.py rollup --dir content/{articlefolder}/data`

This writes `datacompare.json` (the §13 machine artifact) and `datacompare_scores.md` (the scores table) with the composite computed under the correct weight table and reweighted for any N/A dimension. Read both. Do not touch the numbers.

## Step 6: Generate the doc files

Run: `python datacompare.py docs --dir content/{articlefolder}/data`

This writes the vault-facing files (the mechanical layer - all reproducible, all carry a `generated by datacompare.py` marker):

- **`{scraper}-data.txt`** - every field the scraper returns (dot notation, `[]` for arrays), with `UNIQUE IN` and `NOT RETURNED BY` sections.
- **`{scraper}-meaningful-data.txt`** - same list with the plumbing (`exclude_paths`) stripped, and the strip list noted.
- **`gaps.txt`** - the FACTUAL gap skeleton: fields unique to each scraper + fields missing from the baseline, annotated with who has them. This is only the factual layer; the priority / why-it-matters / feasibility / roadmap framing is added by hand (offer to help draft it on top, never invent it).
- **`comparison.md`** - the detailed, engine-fuelled comparison (methodology, field-inventory counts, the scores table with breadth+cardinality as two numbers, uniques cross-tab, baseline misses). This is the file `knowledge.md` references for the article's Data facts.

Safety: `docs` NEVER overwrites a file that lacks the generated marker, so a hand-written `gaps.txt` roadmap is safe. It reported any skipped file. Only pass `--force` when Shehriar confirms he wants a hand-edited file regenerated. The flag lines in `comparison.md` come from `judgments.json` via `datacompare.json`, so if you revise a flag, re-run `rollup` then `docs`.

Read `comparison.md`. Sanity-check it against your judgment, and call out any ranking artifact from N/A reweighting (e.g. "B edges C only because C's freshness was N/A and dropped") so Shehriar sees it. If a field map wasn't provided, note that renamed-equivalent fields may appear as false uniques and a `fields` map would sharpen the gap analysis.

### Scraper-vs-API articles
When one output is the official API (`"is_api": true`), it's just another named output; the baseline is still the most complete response (usually the lobstr.io scraper). `comparison.md` labels the API column and the gap files then read directly as "what the API caps vs what the scraper returns" (e.g. the API hands you 5 reviews per place; the scraper returns all of them). Every claim traces to the script's numbers.

## Step 7: Non-negotiables self-review (do not skip)

Output PASS/FAIL for each, with the offending line on any FAIL, fix, and re-run:

1. Equivalence level recorded; the run degraded full->lite rather than voiding (floor only at level D, where no scores are emitted)
2. One mode for the whole comparison; Full and Lite composites never cross-ranked
3. Baseline disclosed in the report; spot-checked in Full mode before use
4. Capture gap and tier recorded (§3b); under a gap: accuracy scoped to stable fields, the tier's demotions honored (never scored back in by hand), capture order disclosed, the baseline picked on field-path richness not record count, and composites never cross-ranked across timing tiers
5. Rates (fill, completeness, consistency) computed on the overlap set; depth (breadth, cardinality, normalization) on the deliberately-chosen common record - never swapped
6. Accuracy scored on the sample of matched overlap records, never on the single common record
7. Breadth and cardinality reported as two separate numbers
8. Genuine nulls (null in all scrapers AND absent on the live record) dropped from denominators via `genuine_null_fields`; real misses counted
9. JSON canonical for structure; CSV treated as an export round-trip check only
10. Weights declared in the report; every N/A dimension, skipped dimension, timing demotion, and Lite mode triggered reweighting
11. All scores on a 0-10 scale, and every number traces to the script output (none hand-computed)
12. No number, field, or claim invented; gaps were surfaced to Shehriar, not filled
13. `docs` ran; no hand-written file was clobbered (skips honored unless Shehriar OK'd `--force`); the `gaps.txt` roadmap layer was left to Shehriar, not fabricated

Present the results only after all items PASS. Include the checklist under your summary. Point Shehriar at `comparison.md` (the file `knowledge.md` references) and the `*-data.txt` / `gaps.txt` outputs, and confirm `knowledge.md` itself was not modified.
