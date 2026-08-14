"""Ported 1:1 from scripts/lobstr-ground-truth-compare.js.

Compares the live Lobstr.io (automation-lab crawler) result for
www.thepearlsource.com against the manually-verified ground-truth sample.
Matches rows by author_name.

Paths (already corrected in the .js source this was ported from - the
nested `raw/raw` was flattened):
  - reads  data/raw/ground-truth/thepearlsource-sample.json
  - reads  data/raw/lobstr/results/*.json
  - writes data/analysis/lobstr/ground-truth-match.json
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GT_PATH = ROOT / "DATA" / "ground-truth" / "thepearlsource-sample.json"
RESULTS_DIR = ROOT / "DATA" / "lobstr" / "raw" / "results"
OUT_PATH = ROOT / "DATA" / "lobstr" / "analysis" / "ground-truth-match.json"


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def norm(s):
    return re.sub(r"\s+", " ", str(s or "").strip().lower())


def coalesce(*values):
    for v in values:
        if v is not None:
            return v
    return None


def titles_match(gt_title, api_title):
    a = re.sub(r"[…]+$", "", norm(gt_title)).strip()
    b = norm(api_title)
    if not a:
        return b == ""
    return b.startswith(a) or a.startswith(b)


def load_all_pearl_source_items():
    items = []
    for file in sorted(RESULTS_DIR.iterdir()):
        if not file.name.endswith(".json"):
            continue
        j = json.loads(file.read_text(encoding="utf-8"))
        data = (j.get("response") or {}).get("data") or []
        for item in data:
            if "thepearlsource.com" in (item.get("company_page_url") or ""):
                items.append(item)
    return items


def find_match(gt_row, api_items, used_indexes):
    gt_author = norm(gt_row.get("author_name"))
    candidates = [
        {"item": item, "idx": idx}
        for idx, item in enumerate(api_items)
        if idx not in used_indexes and norm(item.get("author_name")) == gt_author
    ]
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]
    title_matches = [c for c in candidates if titles_match(gt_row.get("review_title"), c["item"].get("review_headline"))]
    return title_matches[0] if title_matches else candidates[0]


def compare_field(name, gt_value, api_value, not_returned=False, exact=True):
    if not_returned:
        return {"field": name, "ground_truth": gt_value, "api": None, "status": "not_returned_by_api"}
    if gt_value is None:
        return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "ground_truth_unavailable"}
    match = (norm(gt_value) == norm(api_value)) if exact else (gt_value == api_value)
    return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "match" if match else "mismatch"}


def main():
    ground_truth = json.loads(GT_PATH.read_text(encoding="utf-8"))
    api_items = load_all_pearl_source_items()

    used_indexes = set()
    rows = []

    for gt_row in ground_truth:
        match_result = find_match(gt_row, api_items, used_indexes)
        if not match_result:
            rows.append(
                {
                    "ground_truth_author": gt_row.get("author_name"),
                    "ground_truth_title": gt_row.get("review_title"),
                    "matched": False,
                    "reason": "no_api_item_with_matching_author_found",
                }
            )
            continue
        used_indexes.add(match_result["idx"])
        api = match_result["item"]
        company_replied_api = bool(api.get("owner_reply"))
        invited_api = bool(re.search("invit", api.get("verification_level") or "", re.I)) or bool(re.search("invit", api.get("review_source") or "", re.I))

        fields = [
            compare_field("author_name", gt_row.get("author_name"), api.get("author_name")),
            compare_field("author_country", gt_row.get("author_country"), api.get("consumer_country_code")),
            compare_field("author_reviews_count", gt_row.get("author_reviews_count"), api.get("number_of_reviews"), exact=False),
            compare_field("rating", gt_row.get("rating"), coalesce(api.get("rating_value"), api.get("stars")), exact=False),
            compare_field("review_title", gt_row.get("review_title"), api.get("review_headline")),
            compare_field("review_text", gt_row.get("review_text"), api.get("review_body")),
            compare_field("review_date_absolute", gt_row.get("review_date"), api.get("date_published")),
            compare_field("experience_date", None, api.get("experience_date"), not_returned=False),
            compare_field("review_type_invited_status", gt_row.get("review_type"), "Invited" if invited_api else "Not invited", exact=False),
            compare_field("useful_count", gt_row.get("useful_count"), api.get("likes"), exact=False),
            compare_field("company_replied", gt_row.get("company_replied"), company_replied_api, exact=False),
            compare_field("owner_reply", gt_row.get("owner_reply"), api.get("owner_reply")),
            compare_field("owner_reply_date", gt_row.get("owner_reply_date_display"), api.get("owner_reply_date")),
        ]

        rows.append(
            {
                "ground_truth_author": gt_row.get("author_name"),
                "ground_truth_title": gt_row.get("review_title"),
                "matched": True,
                "matched_api_review_url": api.get("review_url"),
                "matched_api_review_link": api.get("review_link"),
                "fields": fields,
            }
        )

    matched_rows = [r for r in rows if r["matched"]]
    field_stats = {}
    for row in matched_rows:
        for f in row["fields"]:
            stats = field_stats.setdefault(f["field"], {"match": 0, "mismatch": 0, "not_returned_by_api": 0, "ground_truth_unavailable": 0})
            stats[f["status"]] += 1
    field_accuracy = []
    for field, counts in field_stats.items():
        comparable = counts["match"] + counts["mismatch"]
        if comparable > 0:
            # Matches JS's `Number(((match/comparable)*100).toFixed(1))`: round to
            # 1 decimal, then collapse to a plain int when whole (JS has no
            # int/float distinction, so e.g. 100.0 serializes as 100, not 100.0).
            accuracy_percent = round((counts["match"] / comparable) * 100, 1)
            if accuracy_percent == int(accuracy_percent):
                accuracy_percent = int(accuracy_percent)
        else:
            accuracy_percent = None
        field_accuracy.append({"field": field, **counts, "accuracy_percent": accuracy_percent})

    summary = {
        "generated_at": now_iso(),
        "ground_truth_rows": len(ground_truth),
        "matched_rows": len(matched_rows),
        "unmatched_rows": len(rows) - len(matched_rows),
        "api_items_available": len(api_items),
        "field_accuracy": field_accuracy,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    # newline="" avoids Python translating "\n" to os.linesep ("\r\n" on Windows),
    # matching Node's fs.writeFileSync byte-literal write.
    OUT_PATH.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8", newline="")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
