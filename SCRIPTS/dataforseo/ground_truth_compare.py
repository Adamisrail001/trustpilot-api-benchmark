"""DataForSEO ground-truth comparison, mirroring the pattern used by
scripts/outscraper_ground_truth_compare.py, adapted for DataForSEO's
Trustpilot Reviews response shape.

Compares the live DataForSEO Trustpilot Reviews result for
www.thepearlsource.com against the manually-verified ground-truth sample,
matching rows by author_name (ground truth) <-> item.user_profile.name
(DataForSEO). Field mapping below was reverse-derived from the existing
data/analysis/dataforseo/ground-truth-match.json output cross-checked
against data/raw/dataforseo/task-get/www.thepearlsource.com.json - re-running
this script against that same raw file reproduces that file byte-for-byte.

Paths:
  - reads data/raw/ground-truth/thepearlsource-sample.json
  - reads data/raw/dataforseo/task-get/www.thepearlsource.com.json
  - writes data/analysis/dataforseo/ground-truth-match.json
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GT_PATH = ROOT / "data" / "raw" / "ground-truth" / "thepearlsource-sample.json"
API_PATH = ROOT / "data" / "raw" / "dataforseo" / "task-get" / "www.thepearlsource.com.json"
OUT_PATH = ROOT / "data" / "analysis" / "dataforseo" / "ground-truth-match.json"

_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_ELLIPSIS_RE = re.compile(r"[…]+$")


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _js_number(x):
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def norm(s):
    if not s:
        s = ""
    return _WHITESPACE_RE.sub(" ", str(s).strip().lower())


def titles_match(gt_title, api_title):
    a = _TRAILING_ELLIPSIS_RE.sub("", norm(gt_title)).strip()
    b = norm(api_title)
    if not a:
        return b == ""
    return b.startswith(a) or a.startswith(b)


def find_match(gt_row, api_items, used_indexes):
    gt_author = norm(gt_row.get("author_name"))
    candidates = [
        {"item": item, "idx": idx}
        for idx, item in enumerate(api_items)
        if idx not in used_indexes and norm((item.get("user_profile") or {}).get("name")) == gt_author
    ]
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]
    title_matches = [c for c in candidates if titles_match(gt_row.get("review_title"), c["item"].get("title"))]
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
    api_raw = json.loads(API_PATH.read_text(encoding="utf-8"))
    tasks = ((api_raw.get("response") or {}).get("tasks")) or []
    task_result = tasks[0].get("result") if tasks else None
    api_items = (task_result[0].get("items") if task_result else None) or []

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
        profile = api.get("user_profile") or {}
        responses = api.get("responses") or []
        owner_reply_text = responses[0].get("text") if responses else None
        company_replied_api = bool(responses)

        fields = [
            compare_field("author_name", gt_row.get("author_name"), profile.get("name")),
            compare_field("author_country", gt_row.get("author_country"), profile.get("location")),
            compare_field("author_reviews_count", gt_row.get("author_reviews_count"), profile.get("reviews_count"), exact=False),
            compare_field("rating", gt_row.get("rating"), (api.get("rating") or {}).get("value"), exact=False),
            compare_field("review_title", gt_row.get("review_title"), api.get("title")),
            compare_field("review_text", gt_row.get("review_text"), api.get("review_text")),
            compare_field("review_date_absolute", gt_row.get("review_date"), api.get("timestamp")),
            compare_field("review_type_invited_status", gt_row.get("review_type"), None, not_returned=True),
            compare_field("useful_count", gt_row.get("useful_count"), None, not_returned=True),
            compare_field("company_replied", gt_row.get("company_replied"), company_replied_api, exact=False),
            compare_field("owner_reply", gt_row.get("owner_reply"), owner_reply_text),
        ]

        rows.append(
            {
                "ground_truth_author": gt_row.get("author_name"),
                "ground_truth_title": gt_row.get("review_title"),
                "matched": True,
                "matched_api_rank_absolute": api.get("rank_absolute"),
                "matched_api_url": api.get("url"),
                "fields": fields,
            }
        )

    matched_rows = [r for r in rows if r.get("matched")]
    field_stats = {}
    for row in matched_rows:
        for f in row["fields"]:
            stats = field_stats.setdefault(
                f["field"], {"match": 0, "mismatch": 0, "not_returned_by_api": 0, "ground_truth_unavailable": 0}
            )
            stats[f["status"]] += 1

    field_accuracy = []
    for field, counts in field_stats.items():
        comparable = counts["match"] + counts["mismatch"]
        accuracy_percent = _js_number(round((counts["match"] / comparable) * 100, 1)) if comparable > 0 else None
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
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False))
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
