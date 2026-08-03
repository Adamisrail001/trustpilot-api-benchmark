"""Ported 1:1 from scripts/openwebninja-ground-truth-compare.js.

Compares the live OpenWeb Ninja Trustpilot result for
www.thepearlsource.com against the manually-verified ground-truth
sample. Matches rows by consumer_name (OpenWeb Ninja) <-> author_name
(ground truth), same approach used for the Outscraper/DataForSEO comparisons.

Paths below match the already-corrected JS version (data/raw/ground-truth/
thepearlsource-sample.json, data/raw/openwebninja/results/ - flattened,
NOT data/raw/openwebninja/raw/results - and data/analysis/openwebninja/
ground-truth-match.json), not the original outputs/openwebninja/ paths used
by openwebninja_benchmark.py.
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GT_PATH = ROOT / "data" / "raw" / "ground-truth" / "thepearlsource-sample.json"
RESULTS_DIR = ROOT / "data" / "raw" / "openwebninja" / "results"
OUT_PATH = ROOT / "data" / "analysis" / "openwebninja" / "ground-truth-match.json"

_WHITESPACE_RE = re.compile(r"\s+")
_ELLIPSIS_TRAIL_RE = re.compile(r"[…]+$")


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def to_fixed_number(value, digits):
    """Mirrors JS's Number(value.toFixed(digits))."""
    formatted = f"{value:.{digits}f}"
    num = float(formatted)
    return int(num) if num == int(num) else num


def norm(s):
    s = s if s else ""
    return _WHITESPACE_RE.sub(" ", str(s).strip().lower())


def titles_match(gt_title, api_title):
    a = _ELLIPSIS_TRAIL_RE.sub("", norm(gt_title)).strip()
    b = norm(api_title)
    if not a:
        return b == ""
    return b.startswith(a) or a.startswith(b)


def load_all_pearlsource_items():
    items = []
    for page in range(1, 11):
        p = RESULTS_DIR / f"www.thepearlsource.com-page{page}.json"
        if not p.exists():
            continue
        j = json.loads(p.read_text(encoding="utf-8"))
        response = j.get("response") or {}
        data = response.get("data") or {}
        reviews = data.get("reviews") or []
        items.extend(reviews)
    return items


def find_match(gt_row, api_items, used_indexes):
    gt_author = norm(gt_row.get("author_name"))
    candidates = [
        (idx, item)
        for idx, item in enumerate(api_items)
        if idx not in used_indexes and norm(item.get("consumer_name")) == gt_author
    ]
    if not candidates:
        return None
    if len(candidates) == 1:
        idx, item = candidates[0]
        return {"idx": idx, "item": item}
    title_matches = [(idx, item) for idx, item in candidates if titles_match(gt_row.get("review_title"), item.get("review_title"))]
    idx, item = title_matches[0] if title_matches else candidates[0]
    return {"idx": idx, "item": item}


def compare_field(name, gt_value, api_value, not_returned=False, exact=True):
    if not_returned:
        return {"field": name, "ground_truth": gt_value, "api": None, "status": "not_returned_by_api"}
    if gt_value is None:
        return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "ground_truth_unavailable"}
    match = (norm(gt_value) == norm(api_value)) if exact else (gt_value == api_value)
    return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "match" if match else "mismatch"}


def main():
    ground_truth = json.loads(GT_PATH.read_text(encoding="utf-8"))
    api_items = load_all_pearlsource_items()

    used_indexes = set()
    rows = []

    for gt_row in ground_truth:
        match_result = find_match(gt_row, api_items, used_indexes)
        if not match_result:
            rows.append({
                "ground_truth_author": gt_row.get("author_name"),
                "ground_truth_title": gt_row.get("review_title"),
                "matched": False,
                "reason": "no_api_item_with_matching_author_found",
            })
            continue

        used_indexes.add(match_result["idx"])
        api = match_result["item"]
        company_replied_api = bool(api.get("reply_text"))
        invited_api = bool(re.search("invit", api.get("review_source") or "", re.IGNORECASE))

        fields = [
            compare_field("author_name", gt_row.get("author_name"), api.get("consumer_name")),
            compare_field("author_country", gt_row.get("author_country"), api.get("consumer_country")),
            compare_field("author_reviews_count", gt_row.get("author_reviews_count"), api.get("consumer_review_count"), exact=False),
            compare_field("rating", gt_row.get("rating"), api.get("review_rating"), exact=False),
            compare_field("review_title", gt_row.get("review_title"), api.get("review_title")),
            compare_field("review_text", gt_row.get("review_text"), api.get("review_text")),
            compare_field("review_date_absolute", gt_row.get("review_date"), api.get("review_time")),
            compare_field("review_type_invited_status", gt_row.get("review_type"), "Invited" if invited_api else "Not invited", exact=False),
            compare_field("useful_count", gt_row.get("useful_count"), api.get("review_likes"), exact=False),
            compare_field("company_replied", gt_row.get("company_replied"), company_replied_api, exact=False),
            compare_field("owner_reply", gt_row.get("owner_reply"), api.get("reply_text")),
        ]

        rows.append({
            "ground_truth_author": gt_row.get("author_name"),
            "ground_truth_title": gt_row.get("review_title"),
            "matched": True,
            "matched_api_review_id": api.get("review_id"),
            "fields": fields,
        })

    matched_rows = [r for r in rows if r["matched"]]
    field_stats = {}
    for row in matched_rows:
        for f in row["fields"]:
            stats = field_stats.setdefault(f["field"], {"match": 0, "mismatch": 0, "not_returned_by_api": 0, "ground_truth_unavailable": 0})
            stats[f["status"]] += 1

    field_accuracy = []
    for field, counts in field_stats.items():
        comparable = counts["match"] + counts["mismatch"]
        accuracy = to_fixed_number((counts["match"] / comparable) * 100, 1) if comparable > 0 else None
        field_accuracy.append({"field": field, **counts, "accuracy_percent": accuracy})

    summary = {
        "generated_at": now_iso(),
        "ground_truth_rows": len(ground_truth),
        "matched_rows": len(matched_rows),
        "unmatched_rows": len(rows) - len(matched_rows),
        "api_items_available": len(api_items),
        "field_accuracy": field_accuracy,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
