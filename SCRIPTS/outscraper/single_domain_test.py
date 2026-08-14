"""Standalone, isolated live test: how many reviews can Outscraper's
Trustpilot Reviews endpoint actually return from ONE business in a single
request when `limit` is raised well past the 200 value used in the
published 5-domain benchmark?

Outscraper's docs do not state a documented max for `limit` (see the
LIMIT_PER_PAGE comment in outscraper_benchmark.py - 200 there was a
benchmark choice, not a confirmed ceiling). This script finds out
empirically what a `limit=1000` request on one domain actually returns:
more than 200 in one page, a silently capped page (falls back to `skip`
pagination in multiples of 20, per the documented constraint), or an
outright rejection.

This is intentionally a SEPARATE script from outscraper_benchmark.py:
- It submits its own request(s) and writes to its own output directory
  (outputs/outscraper-single-domain-test/), never outputs/outscraper/ -
  so it cannot touch or contaminate the evidence behind the published
  benchmark article.
- It never writes to .env.

It reuses the same credentials (OUTSCRAPER_API_KEY) as the main benchmark,
read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/outscraper_single_domain_test.py [domain] [target]

  domain  defaults to www.thepearlsource.com
  target  defaults to 1000 (the `limit` param for the first page; also the
          pagination stop target if multiple pages are needed)

This is a REAL paid request against the live Outscraper API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as the main benchmark script.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.outscraper_client import create_client, AuthOrBillingError, InvalidParametersError
from lib.dedupe import build_review_key, dedupe
from lib.csv_utils import to_csv

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "outputs" / "outscraper-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"

MAX_PAGES = 10  # safety ceiling - well past what a 1000-review target with 20-skip increments should need
SORT = "recency"
LANGUAGES = "all"
POLL_INTERVAL_S = 5
MAX_POLL_WAIT_MS = 10 * 60_000  # per page, matches the main benchmark's operational choice

FREE_TIER_REVIEWS = 100
MEDIUM_TIER_CEILING = 50_000
MEDIUM_TIER_RATE_PER_REVIEW = 3 / 1000
BUSINESS_TIER_RATE_PER_REVIEW = 1 / 1000

_SAFE_NAME_RE = re.compile(r"[^a-z0-9.\-]", re.IGNORECASE)


def safe_domain_name(domain):
    return _SAFE_NAME_RE.sub("_", domain)


def _js_number(x):
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False))


def write_text(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def ensure_dirs():
    for d in (OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False) + "\n")


def load_api_key():
    if not ENV_PATH.exists():
        raise RuntimeError(".env not found.")
    raw = ENV_PATH.read_text(encoding="utf-8")
    for line in re.split(r"\r?\n", raw):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        idx = trimmed.find("=")
        if idx == -1:
            continue
        key = trimmed[:idx].strip()
        if key == "OUTSCRAPER_API_KEY":
            value = trimmed[idx + 1:].strip()
            if not value:
                raise RuntimeError("OUTSCRAPER_API_KEY is present but empty in .env.")
            return value
    raise RuntimeError("OUTSCRAPER_API_KEY not found in .env.")


# Same shapes/rules as outscraper_benchmark.py, so results are directly comparable.


def extract_review_items(result_json):
    data = result_json.get("data") if isinstance(result_json, dict) else None
    if not isinstance(data, list):
        return {"items": [], "shapeWarning": "no_data_array"}
    if len(data) == 0:
        return {"items": [], "shapeWarning": None}
    if isinstance(data[0], list):
        items = [item for sublist in data for item in sublist]
        return {"items": items, "shapeWarning": None}
    if isinstance(data[0], dict):
        return {"items": data, "shapeWarning": None}
    return {"items": [], "shapeWarning": "unrecognized_data_shape"}


def normalize_review_for_dedupe(item):
    return {
        "id": item.get("review_id"),
        "url": item.get("review_url"),
        "user_profile": {"name": item.get("author_title")},
        "timestamp": item.get("review_timestamp") if item.get("review_timestamp") is not None else item.get("review_datetime_utc"),
        "rating": item.get("review_rating"),
        "title": item.get("review_title"),
        "review_text": item.get("review_text"),
    }


def is_valid_review(item):
    has_id = bool(item.get("review_id"))
    has_rating = item.get("review_rating") is not None
    has_date = bool(item.get("review_timestamp") or item.get("review_datetime_utc"))
    has_text = bool(item.get("review_title")) or bool(item.get("review_text"))
    has_reviewer = bool(item.get("author_title")) or bool(item.get("author_id"))
    return bool(has_id and has_rating and has_date and has_text and has_reviewer)


def missing_fields_for(item):
    missing = []
    if not item.get("review_id"):
        missing.append("review_id")
    if item.get("review_rating") is None:
        missing.append("review_rating")
    if not item.get("review_timestamp") and not item.get("review_datetime_utc"):
        missing.append("review_date")
    if not item.get("review_title") and not item.get("review_text"):
        missing.append("review_title_or_text")
    if not item.get("author_title") and not item.get("author_id"):
        missing.append("reviewer_info")
    return missing


def calculate_cost_from_usage(total_usage_reviews, free_already_consumed):
    remaining = total_usage_reviews
    cost = 0
    free_available = 0 if free_already_consumed else FREE_TIER_REVIEWS
    free_used = min(remaining, free_available)
    remaining -= free_used
    if remaining > 0:
        medium_used = min(remaining, MEDIUM_TIER_CEILING - FREE_TIER_REVIEWS)
        cost += medium_used * MEDIUM_TIER_RATE_PER_REVIEW
        remaining -= medium_used
    if remaining > 0:
        cost += remaining * BUSINESS_TIER_RATE_PER_REVIEW
    return _js_number(round(cost, 4))


def fetch_pages(domain, target, client, latencies):
    skip = 0
    page_num = 1
    seen_keys = set()
    collected = []
    pages = []
    total_raw = 0
    stop_reason = None

    safe = safe_domain_name(domain)
    while page_num <= MAX_PAGES:
        req_file = REQUESTS_DIR / f"{safe}-page{page_num}.json"
        res_file = RESULTS_DIR / f"{safe}-page{page_num}.json"

        request_id = None
        results_location = None
        page_limit = target if page_num == 1 else 200

        if req_file.exists():
            existing = json.loads(req_file.read_text(encoding="utf-8"))
            existing_response = existing.get("response") or {}
            request_id = existing_response.get("id")
            results_location = existing_response.get("results_location")
            print(f"[submit] page {page_num}: reusing existing request (idempotent).")
        else:
            submit_result = client.submit_trustpilot_reviews_request(
                query=[domain], limit=page_limit, skip=skip, languages=LANGUAGES, sort=SORT, async_=True
            )
            latencies.append({"phase": "submit", "page": page_num, "ms": submit_result.get("latency_ms"), "attempts": submit_result.get("attempts")})
            write_json(
                req_file,
                {
                    "domain": domain, "page": page_num, "skip": skip, "limit": page_limit,
                    "requested_at": now_iso(), "request_url": submit_result.get("request_url"),
                    "latency_ms": submit_result.get("latency_ms"), "attempts": submit_result.get("attempts"),
                    "response": submit_result.get("json"),
                },
            )
            submit_json = submit_result.get("json") or {}
            if not submit_result.get("ok") or not submit_json.get("id"):
                append_error_event({"type": "submit_failed", "page": page_num, "response": submit_result.get("json")})
                stop_reason = "submission_failed"
                break
            request_id = submit_json.get("id")
            results_location = submit_json.get("results_location")

        if not results_location:
            append_error_event({"type": "missing_results_location", "page": page_num})
            stop_reason = "missing_results_location"
            break

        result_json = None
        if res_file.exists():
            result_json = json.loads(res_file.read_text(encoding="utf-8")).get("response")
            print(f"[poll] page {page_num}: reusing existing saved result.")
        else:
            poll_start = time.monotonic()
            while (time.monotonic() - poll_start) * 1000 < MAX_POLL_WAIT_MS:
                poll_result = client.poll_results_location(results_location)
                latencies.append({"phase": "poll", "page": page_num, "ms": poll_result.get("latency_ms"), "attempts": poll_result.get("attempts")})
                if not poll_result.get("ok"):
                    append_error_event({"type": "poll_error", "page": page_num, "response": poll_result.get("json")})
                    time.sleep(POLL_INTERVAL_S)
                    continue
                poll_json = poll_result.get("json") or {}
                status = poll_json.get("status")
                if status == "Success":
                    result_json = poll_result.get("json")
                    write_json(res_file, {"domain": domain, "page": page_num, "request_id": request_id, "fetched_at": now_iso(), "response": result_json})
                    break
                if status == "Failure":
                    append_error_event({"type": "task_failure", "page": page_num, "response": poll_result.get("json")})
                    stop_reason = "task_failure"
                    break
                time.sleep(POLL_INTERVAL_S)
            if not result_json and not stop_reason:
                append_error_event({"type": "poll_timeout", "page": page_num})
                stop_reason = "poll_timeout"

        if stop_reason:
            break

        extracted = extract_review_items(result_json)
        items, shape_warning = extracted["items"], extracted["shapeWarning"]
        if shape_warning:
            append_error_event({"type": "response_shape_warning", "page": page_num, "shapeWarning": shape_warning})
        pages.append({"page": page_num, "skip": skip, "requested_limit": page_limit, "raw_count": len(items), "shape_warning": shape_warning})
        total_raw += len(items)
        print(f"[page {page_num}] requested_limit={page_limit} skip={skip} -> {len(items)} raw items")

        if len(items) == 0:
            stop_reason = "empty_page"
            break

        new_count = 0
        for item in items:
            key_result = build_review_key(domain, normalize_review_for_dedupe(item))
            key = key_result["key"]
            if key not in seen_keys:
                seen_keys.add(key)
                new_count += 1
            collected.append({"domain": domain, "review": normalize_review_for_dedupe(item), "raw": item})

        if new_count == 0:
            stop_reason = "repeated_page"
            break
        if len(seen_keys) >= target:
            stop_reason = "target_reached"
            break
        if len(items) < page_limit:
            stop_reason = "partial_last_page"
            break

        skip = (total_raw // 20) * 20
        page_num += 1

    if not stop_reason:
        stop_reason = "max_pages_cap"

    return {"collected": collected, "pages": pages, "totalRaw": total_raw, "stopReason": stop_reason}


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating real paid Outscraper requests.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    target_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    ensure_dirs()
    api_key = load_api_key()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_perf = time.monotonic()

    client = create_client(api_key, on_event=lambda event: append_error_event({"label": "single_domain_test", **event}))

    try:
        result = fetch_pages(domain, target_reviews, client, latencies)
    except AuthOrBillingError as err:
        write_json(ERRORS_DIR / "BLOCKER-auth-or-billing.json", {"message": str(err), "status": err.status, "body": err.body})
        print(f"BLOCKER: authentication/billing failure: {err}", file=sys.stderr)
        sys.exit(2)
    except InvalidParametersError as err:
        write_json(ERRORS_DIR / "BLOCKER-invalid-parameters.json", {"message": str(err), "status": err.status, "body": err.body})
        print(f"BLOCKER: invalid parameters (likely limit={target_reviews} rejected): {err}", file=sys.stderr)
        sys.exit(2)

    valid_entries = [e for e in result["collected"] if is_valid_review(e["raw"])]
    missing_tally = {}
    for e in result["collected"]:
        for f in missing_fields_for(e["raw"]):
            missing_tally[f] = missing_tally.get(f, 0) + 1

    dedupe_result = dedupe(valid_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]

    benchmark_end_perf = time.monotonic()
    wall_clock_ms = int(round((benchmark_end_perf - benchmark_start_perf) * 1000))
    latency_values = sorted(v["ms"] for v in latencies if isinstance(v.get("ms"), (int, float)))
    median = latency_values[len(latency_values) // 2] if latency_values else None

    write_json(
        OUT_DIR / "timings.json",
        {"benchmark_start": benchmark_start, "benchmark_end": now_iso(), "wall_clock_ms": wall_clock_ms, "per_request": latencies, "median_latency_ms": median},
    )

    flat_reviews = []
    for e in unique:
        raw = e["raw"]
        flat_reviews.append(
            {
                "domain": domain, "dedupe_key": e.get("dedupeKey"), "dedupe_key_type": e.get("dedupeKeyType"),
                "review_id": raw.get("review_id"), "review_rating": raw.get("review_rating"),
                "review_verified": raw.get("review_verified"), "review_timestamp": raw.get("review_timestamp"),
                "review_datetime_utc": raw.get("review_datetime_utc"), "review_title": raw.get("review_title"),
                "review_text": raw.get("review_text"), "author_title": raw.get("author_title"),
                "author_id": raw.get("author_id"), "author_country_code": raw.get("author_country_code"),
                "author_reviews_number": raw.get("author_reviews_number"), "owner_answer": raw.get("owner_answer"),
                "owner_answer_date": raw.get("owner_answer_date"),
            }
        )
    write_json(OUT_DIR / "all-reviews.json", flat_reviews)
    write_text(
        OUT_DIR / "all-reviews.csv",
        to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "review_id", "review_rating", "review_verified", "review_timestamp", "review_datetime_utc", "review_title", "review_text", "author_title", "author_id", "author_country_code", "author_reviews_number", "owner_answer", "owner_answer_date"]),
    )
    write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
    write_json(OUT_DIR / "pagination-report.json", {"pages": result["pages"], "stop_reason": result["stopReason"]})

    calculated_fresh = calculate_cost_from_usage(result["totalRaw"], False)
    calculated_used = calculate_cost_from_usage(result["totalRaw"], True)
    write_json(
        OUT_DIR / "cost-report.json",
        {
            "generated_at": now_iso(), "total_usage_reviews_raw": result["totalRaw"],
            "calculated_cost_scenario_fresh_account_usd": calculated_fresh,
            "calculated_cost_scenario_free_tier_used_usd": calculated_used,
            "measured_cost_usd": None,
            "note": "calculated_* are from the published rate card applied to raw usage - Outscraper has no documented endpoint for measured account balance/cost.",
        },
    )

    summary = {
        "generated_at": now_iso(),
        "domain": domain,
        "target_reviews_requested": target_reviews,
        "first_page_requested_limit": target_reviews,
        "first_page_raw_count": result["pages"][0]["raw_count"] if result["pages"] else None,
        "pages_fetched": len(result["pages"]),
        "pagination_detail": result["pages"],
        "stop_reason": result["stopReason"],
        "total_raw_items_fetched": result["totalRaw"],
        "total_valid_items": len(valid_entries),
        "total_unique_valid_reviews": len(unique),
        "total_duplicates": len(duplicates),
        "exceeded_200_reviews_from_one_business": len(unique) > 200,
        "single_request_exceeded_200": bool(result["pages"] and result["pages"][0]["raw_count"] > 200),
        "wall_clock_ms": wall_clock_ms,
        "calculated_cost_scenario_fresh_account_usd": calculated_fresh,
        "calculated_cost_scenario_free_tier_used_usd": calculated_used,
        "missing_field_counts": missing_tally,
    }
    write_json(OUT_DIR / "summary.json", summary)

    print("--- SINGLE-DOMAIN TEST COMPLETE ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
