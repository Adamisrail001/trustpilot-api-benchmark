"""Ground-truth comparison for the memo23 Actor (memo23/trustpilot-scraper-ppe),
same methodology as scripts/apify/ground_truth_compare.py (which scores the
primary automation-lab/trustpilot Actor), applied for the first time to memo23
now that real, full-volume data for www.thepearlsource.com exists from its
paid-tier tests.

Matches rows by reviewerName <-> author_name (memo23's field is `reviewerName`,
not `authorName` -- confirmed live schema, see outputs/apify-alt-actor-*-test/
sample items).

Reads from the single-run multi-domain test's raw dataset pages (the freshest,
fastest-confirmed memo23 run) rather than the 5-separate-runs test, since both
returned the identical 1,000/1,000 for this business and the single-run test
is the one now cited as memo23's primary comparison point.

Usage:
  python scripts/apify/alt_actor_ground_truth_compare.py
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
GT_PATH = ROOT / "data" / "ground-truth" / "thepearlsource-sample.json"
DATASET_DIR = ROOT / "outputs" / "apify-alt-actor-single-run-multi-domain-test" / "raw" / "datasets"
OUT_PATH = ROOT / "outputs" / "apify-alt-actor-single-run-multi-domain-test" / "ground-truth-match.json"

_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_ELLIPSIS_RE = re.compile(r"[…]+$")


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def norm(s):
    text = "" if s is None else str(s)
    return _WHITESPACE_RE.sub(" ", text.strip().lower())


def titles_match(gt_title, api_title):
    a = _TRAILING_ELLIPSIS_RE.sub("", norm(gt_title)).strip()
    b = norm(api_title)
    if not a:
        return b == ""
    return b.startswith(a) or a.startswith(b)


def find_match(gt_row, api_items, used_indexes):
    gt_author = norm(gt_row.get("author_name"))
    candidates = [
        (idx, item)
        for idx, item in enumerate(api_items)
        if idx not in used_indexes and norm(item.get("reviewerName")) == gt_author
    ]
    if len(candidates) == 0:
        return None
    if len(candidates) == 1:
        return candidates[0]
    title_matches = [c for c in candidates if titles_match(gt_row.get("review_title"), c[1].get("title"))]
    return title_matches[0] if title_matches else candidates[0]


def compare_field(name, gt_value, api_value, not_returned=False, exact=True):
    if not_returned:
        return {"field": name, "ground_truth": gt_value, "api": None, "status": "not_returned_by_api"}
    if gt_value is None:
        return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "ground_truth_unavailable"}
    match = (norm(gt_value) == norm(api_value)) if exact else (gt_value == api_value)
    return {"field": name, "ground_truth": gt_value, "api": api_value, "status": "match" if match else "mismatch"}


def load_thepearlsource_items():
    items = []
    for page_file in sorted(DATASET_DIR.glob("page*-offset*.json")):
        data = json.loads(page_file.read_text(encoding="utf-8"))
        for item in data.get("response", []):
            biz_url = item.get("businessUrl") or ""
            if "thepearlsource" in biz_url:
                items.append(item)
    return items


def main():
    ground_truth = json.loads(GT_PATH.read_text(encoding="utf-8"))
    api_items = load_thepearlsource_items()
    print(f"[data] loaded {len(api_items)} memo23 items for www.thepearlsource.com from the single-run test dataset pages.")

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
        idx, api = match_result
        used_indexes.add(idx)
        company_replied_api = bool(api.get("companyReply"))
        invited_api = bool(re.search("invit", api.get("verificationLevel") or "", re.IGNORECASE)) or bool(
            re.search("invit", api.get("source") or "", re.IGNORECASE)
        )
        company_reply = api.get("companyReply") or {}

        fields = [
            compare_field("author_name", gt_row.get("author_name"), api.get("reviewerName")),
            compare_field("author_country", gt_row.get("author_country"), api.get("reviewerCountry")),
            compare_field(
                "author_reviews_count", gt_row.get("author_reviews_count"), api.get("reviewerNumberOfReviews"), exact=False
            ),
            compare_field("rating", gt_row.get("rating"), api.get("rating"), exact=False),
            compare_field("review_title", gt_row.get("review_title"), api.get("title")),
            compare_field("review_text", gt_row.get("review_text"), api.get("text")),
            compare_field("review_date_absolute", gt_row.get("review_date"), api.get("publishedDate")),
            compare_field(
                "review_type_invited_status",
                gt_row.get("review_type"),
                "Invited" if invited_api else "Not invited",
                exact=False,
            ),
            compare_field("useful_count", gt_row.get("useful_count"), api.get("likes") or api.get("numberOfLikes"), exact=False),
            compare_field("company_replied", gt_row.get("company_replied"), company_replied_api, exact=False),
            compare_field("owner_reply", gt_row.get("owner_reply"), company_reply.get("text")),
            compare_field("owner_reply_date", gt_row.get("owner_reply_date_display"), company_reply.get("publishedDate")),
        ]

        rows.append(
            {
                "ground_truth_author": gt_row.get("author_name"),
                "ground_truth_title": gt_row.get("review_title"),
                "matched": True,
                "matched_api_review_id": api.get("id"),
                "fields": fields,
            }
        )

    matched_rows = [r for r in rows if r["matched"]]
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
        if comparable > 0:
            accuracy_percent = float(f"{(counts['match'] / comparable) * 100:.1f}")
            if accuracy_percent == int(accuracy_percent):
                accuracy_percent = int(accuracy_percent)
        else:
            accuracy_percent = None
        field_accuracy.append({"field": field, **counts, "accuracy_percent": accuracy_percent})

    total_comparable_fields = sum(fa["match"] + fa["mismatch"] for fa in field_accuracy)
    total_matched_fields = sum(fa["match"] for fa in field_accuracy)
    overall_field_accuracy = (
        float(f"{(total_matched_fields / total_comparable_fields) * 100:.1f}") if total_comparable_fields else None
    )
    fields_with_zero_absent = sum(1 for fa in field_accuracy if fa["not_returned_by_api"] == 0)

    summary = {
        "generated_at": now_iso(),
        "actor_id": "memo23~trustpilot-scraper-ppe",
        "data_source": "outputs/apify-alt-actor-single-run-multi-domain-test/ (single-run, 2026-09-16)",
        "note": "First ground-truth comparison ever run against memo23 -- not previously computed. Uses the identical methodology and field checklist as scripts/apify/ground_truth_compare.py (the primary automation-lab/trustpilot Actor's scoring script), adapted only for memo23's own confirmed field names (reviewerName, reviewerCountry, companyReply.{text,publishedDate}, etc.).",
        "ground_truth_rows": len(ground_truth),
        "matched_rows": len(matched_rows),
        "unmatched_rows": len(rows) - len(matched_rows),
        "api_items_available": len(api_items),
        "field_accuracy": field_accuracy,
        "overall_field_match_rate_percent": overall_field_accuracy,
        "fields_present_in_schema_count": fields_with_zero_absent,
        "fields_checked_count": len(field_accuracy),
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
