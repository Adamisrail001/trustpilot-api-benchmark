# owner_reply_date 0%-match — root cause analysis

**Evidence type: INFERRED** (derived by re-reading existing committed files —
`SCRIPTS/lobstr/ground_truth_compare.py` and `DATA/ground-truth/thepearlsource-sample.json`
— no new data was collected and nothing existing was modified).

## What the audit found

`DATA/lobstr/analysis/ground-truth-match.json` → `field_accuracy` shows
`owner_reply_date: {"match": 0, "mismatch": 14, "accuracy_percent": 0}` — every
single comparable row mismatches. On its face this looks like a real
data-accuracy problem with Lobstr's export.

## Root cause

`SCRIPTS/lobstr/ground_truth_compare.py` line 122 compares:

```python
compare_field("owner_reply_date", gt_row.get("owner_reply_date_display"), api.get("owner_reply_date"))
```

- `gt_row["owner_reply_date_display"]` (the ground-truth sample) stores a
  **relative string captured at manual-collection time** — e.g. `"1 days ago"`,
  `"3 days ago"`, `"Updated 1 days ago"` (confirmed directly in
  `DATA/ground-truth/thepearlsource-sample.json`).
- `api["owner_reply_date"]` (Lobstr's export) stores an **absolute ISO 8601
  timestamp** — e.g. `"2026-07-23T01:22:26Z"` (confirmed directly in
  `DATA/lobstr/exports/all-reviews.json`).
- `compare_field()`'s `norm()` helper (line 29-30) only lowercases/strips
  whitespace — it does **not** parse or normalize dates:
  ```python
  def norm(s):
      return re.sub(r"\s+", " ", str(s or "").strip().lower())
  ```

Comparing `"1 days ago"` against `"2026-07-23t01:22:26z"` by string equality
will mismatch on every row, regardless of whether the underlying date is
correct. This is a **comparison-script limitation** (mixing a relative display
string with an absolute timestamp, with no date-parsing step), not evidence
that Lobstr's `owner_reply_date` values are wrong.

## What this does NOT resolve

This explains *why* the metric reads 0%. It does not independently confirm
Lobstr's `owner_reply_date` values are *correct* — that would require converting
the ground truth's relative strings to absolute timestamps anchored to their
`collected_at` field and re-comparing, which was not done here (out of scope for
this pass; flagged as a remaining gap in the gap-closure report).

## Recommended fix (not applied — flagging only, per instruction not to modify scripts here)

Either exclude `owner_reply_date` from the accuracy denominator with a
`not_comparable_format` status, or add a small relative-to-absolute date
resolver anchored to `gt_row["collected_at"]` before comparing.
