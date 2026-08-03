"""Ported 1:1 from scripts/apify-ground-truth-compare.js.

Compares the live Apify (automation-lab/trustpilot) result for
www.thepearlsource.com against the manually-verified ground-truth
sample. Matches rows by authorName <-> author_name.

Paths below match the JS source as it stands today (already edited in an
earlier pass to point at data/raw and data/exports/data/analysis rather
than the original outputs/ layout).
"""
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GT_PATH = ROOT / "data" / "raw" / "ground-truth" / "thepearlsource-sample.json"
ALL_REVIEWS_PATH = ROOT / "data" / "exports" / "apify" / "all-reviews.json"
OUT_PATH = ROOT / "data" / "analysis" / "apify" / "ground-truth-match.json"

_WHITESPACE_RE = re.compile(r"\s+")
_TRAILING_ELLIPSIS_RE = re.compile(r"[…]+$")


def now_iso():
    """Matches JS's `new Date().toISOString()` - millisecond precision, Z suffix."""
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
        if idx not in used_indexes and norm(item.get("authorName")) == gt_author
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


def main():
    ground_truth = json.loads(GT_PATH.read_text(encoding="utf-8"))
    all_reviews = json.loads(ALL_REVIEWS_PATH.read_text(encoding="utf-8"))
    api_items = [r for r in all_reviews if r.get("domain") == "www.thepearlsource.com"]

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
        company_replied_api = bool(api.get("replyMessage"))
        invited_api = bool(re.search("invit", api.get("verificationLevel") or "", re.IGNORECASE)) or bool(
            re.search("invit", api.get("source") or "", re.IGNORECASE)
        )

        fields = [
            compare_field("author_name", gt_row.get("author_name"), api.get("authorName")),
            compare_field("author_country", gt_row.get("author_country"), api.get("country")),
            compare_field(
                "author_reviews_count", gt_row.get("author_reviews_count"), api.get("authorReviewCount"), exact=False
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
            compare_field("useful_count", gt_row.get("useful_count"), api.get("likes"), exact=False),
            compare_field("company_replied", gt_row.get("company_replied"), company_replied_api, exact=False),
            compare_field("owner_reply", gt_row.get("owner_reply"), api.get("replyMessage")),
            compare_field("owner_reply_date", gt_row.get("owner_reply_date_display"), api.get("replyPublishedDate")),
        ]

        rows.append(
            {
                "ground_truth_author": gt_row.get("author_name"),
                "ground_truth_title": gt_row.get("review_title"),
                "matched": True,
                "matched_api_review_id": api.get("reviewId"),
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
            # Matches JS's `Number(((match/comparable)*100).toFixed(1))`:
            # round to 1 decimal, then collapse to a plain int when whole
            # (JS has no int/float distinction, so e.g. 100.0 serializes
            # as 100, not 100.0).
            accuracy_percent = float(f"{(counts['match'] / comparable) * 100:.1f}")
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
    OUT_PATH.write_text(json.dumps({"summary": summary, "rows": rows}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
