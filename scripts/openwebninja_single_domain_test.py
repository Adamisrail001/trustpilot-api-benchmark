"""Standalone, isolated live test: how many reviews can OpenWeb Ninja's
Trustpilot Company Reviews endpoint actually return from ONE business when
paginated past page 10?

This directly tests a documented limit: scripts/lib/openwebninja_client.py's
module docstring records "Pages 1-10 available without a Trustpilot login
cookie; page 11+ requires a 'cookie' param (a logged-in Trustpilot user
session)". At 20 reviews/page that is a hard structural cap of 200 reviews
per business without extra auth this benchmark doesn't have. This script
requests page 11+ anyway (no cookie supplied) to find out empirically what
actually happens - a clean stop, an error, or a cookie-required message -
rather than assuming the docs are exactly right.

Note: the published 5-domain benchmark (outputs/openwebninja/domain-summary.json,
generated_at 2026-07-29) failed completely with HTTP 429 "Too Many Requests"
on the very first request of the very first domain - so there is no prior
confirmed-working evidence for this API key/account in this project. This
script may hit the same wall; if so it reports that plainly rather than
guessing at a cause (exhausted quota vs. a stricter rate limit than
documented).

This is intentionally a SEPARATE script from openwebninja_benchmark.py:
- It writes to its own output directory (outputs/openwebninja-single-domain-test/),
  never outputs/openwebninja/ - so it cannot contaminate the evidence behind
  the published benchmark article.
- It never writes to .env.

It reuses the same credentials (OPENWEBNINJA_API_KEY) as the main benchmark,
read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/openwebninja_single_domain_test.py [domain] [target]

  domain  defaults to www.thepearlsource.com
  target  defaults to 1000 (reviews; translated to page count at 20/page,
          capped at MAX_PAGES since the documented page-11 wall makes
          fetching further pages without a cookie pointless past that point)

This is a REAL paid/metered run against the live OpenWeb Ninja API (no
documented account/quota endpoint exists, per the main benchmark's own
finding - so quota cannot be checked programmatically here either).
Requires CONFIRM_PAID_RUN=yes to proceed, same safeguard as the main
benchmark script.
"""
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.openwebninja_client import create_client, AuthOrQuotaError, InvalidRequestError
from lib.dedupe import dedupe
from lib.csv_utils import to_csv

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "openwebninja-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"

REVIEWS_PER_PAGE = 20
DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE = 10
MAX_PAGES = 12  # 2 pages past the documented wall - enough to confirm/deny it cleanly
REQUEST_SPACING_S = 1.0  # more conservative than the main benchmark's 350ms, given its 429 history


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False))


def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def ensure_dirs():
    for d in (OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False) + "\n")


def get_env_var(name):
    if not ENV_PATH.exists():
        raise RuntimeError(".env not found.")
    text = ENV_PATH.read_text(encoding="utf-8")
    for raw_line in text.split("\n"):
        trimmed = raw_line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        idx = trimmed.find("=")
        if idx == -1:
            continue
        if trimmed[:idx].strip() == name:
            value = trimmed[idx + 1:].strip()
            return value or None
    return None


def load_api_key():
    key = get_env_var("OPENWEBNINJA_API_KEY")
    if not key:
        raise RuntimeError("OPENWEBNINJA_API_KEY not found or empty in .env.")
    return key


def safe_domain_name(domain):
    return re.sub(r"[^a-z0-9.-]", "_", domain, flags=re.IGNORECASE)


# Same shapes/rules as openwebninja_benchmark.py, so results are directly comparable.


def normalize_review_for_dedupe(item, domain):
    return {
        "id": item.get("review_id"),
        "url": None,
        "user_profile": {"name": item.get("consumer_name")},
        "timestamp": item.get("review_time"),
        "rating": item.get("review_rating"),
        "title": item.get("review_title"),
        "review_text": item.get("review_text"),
        "domain": domain,
    }


def is_valid_review(item):
    has_id = bool(item.get("review_id"))
    has_rating = item.get("review_rating") is not None
    has_date = bool(item.get("review_time"))
    has_text = bool(item.get("review_title")) or bool(item.get("review_text"))
    has_reviewer = bool(item.get("consumer_name")) or bool(item.get("consumer_id"))
    not_pending = item.get("review_is_pending") is not True
    return bool(has_id and has_rating and has_date and has_text and has_reviewer and not_pending)


def missing_fields_for(item):
    missing = []
    if not item.get("review_id"):
        missing.append("review_id")
    if item.get("review_rating") is None:
        missing.append("review_rating")
    if not item.get("review_time"):
        missing.append("review_time")
    if not item.get("review_title") and not item.get("review_text"):
        missing.append("review_title_or_text")
    if not item.get("consumer_name") and not item.get("consumer_id"):
        missing.append("reviewer_info")
    return missing


def _reviews_from_json(json_body):
    if not isinstance(json_body, dict):
        return None
    data = json_body.get("data")
    if not isinstance(data, dict):
        return None
    return data.get("reviews")


def fetch_domain_reviews(domain, max_pages, client, latencies):
    safe = safe_domain_name(domain)
    seen_keys = set()
    collected = []
    pages = []
    stop_reason = None
    page_at_which_wall_hit = None

    for page in range(1, max_pages + 1):
        req_file = REQUESTS_DIR / f"{safe}-page{page}.json"
        res_file = RESULTS_DIR / f"{safe}-page{page}.json"

        if res_file.exists():
            json_body = json.loads(res_file.read_text(encoding="utf-8"))["response"]
            print(f"[page] {domain} page {page}: reusing existing saved result (idempotent).")
        else:
            time.sleep(REQUEST_SPACING_S)
            try:
                result = client.get_company_reviews(company_domain=domain, page=page, sort="recency")
            except AuthOrQuotaError as err:
                append_error_event({"type": "auth_or_quota", "domain": domain, "page": page, "message": str(err), "body": err.body})
                stop_reason = "auth_or_quota_error"
                if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE:
                    page_at_which_wall_hit = page
                break
            except InvalidRequestError as err:
                append_error_event({"type": "invalid_request", "domain": domain, "page": page, "message": str(err), "body": err.body})
                stop_reason = "invalid_request"
                if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE:
                    page_at_which_wall_hit = page
                break
            latencies.append({"phase": "company-reviews", "page": page, "ms": result["latencyMs"], "attempts": result["attempts"]})
            write_json(req_file, {
                "domain": domain, "page": page, "requested_at": now_iso(),
                "request_url": result["requestUrl"], "latency_ms": result["latencyMs"],
                "attempts": result["attempts"], "ok": result["ok"], "status": result["status"],
            })
            if not result["ok"]:
                append_error_event({"type": "page_fetch_failed", "domain": domain, "page": page, "status": result["status"], "body": result["json"]})
                stop_reason = "fetch_failed"
                if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE:
                    page_at_which_wall_hit = page
                break
            json_body = result["json"]
            write_json(res_file, {"domain": domain, "page": page, "fetched_at": now_iso(), "response": json_body})

        items = _reviews_from_json(json_body)
        if not isinstance(items, list):
            append_error_event({"type": "unexpected_response_shape", "domain": domain, "page": page, "keys": list(json_body.keys()) if isinstance(json_body, dict) else None})
            stop_reason = "unexpected_response_shape"
            break

        pages.append({"page": page, "raw_count": len(items)})
        print(f"[page {page}] -> {len(items)} raw items" + (" (past documented page-10 wall)" if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE else ""))

        if len(items) == 0:
            stop_reason = "empty_page"
            if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE:
                page_at_which_wall_hit = page
            break

        new_count = 0
        for item in items:
            key = f"id:{item.get('review_id')}" if item.get("review_id") else None
            if key:
                if key not in seen_keys:
                    seen_keys.add(key)
                    new_count += 1
            else:
                new_count += 1
            collected.append({"domain": domain, "review": normalize_review_for_dedupe(item, domain), "raw": item})

        if new_count == 0:
            stop_reason = "repeated_page"
            if page > DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE:
                page_at_which_wall_hit = page
            break
        if len(items) < REVIEWS_PER_PAGE:
            stop_reason = "partial_last_page"
            break

    if not stop_reason:
        stop_reason = "max_pages_reached"
    return {"collected": collected, "pages": pages, "stopReason": stop_reason, "pageAtWhichWallHit": page_at_which_wall_hit}


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve making real metered OpenWeb Ninja requests.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    target_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    max_pages = min(max(MAX_PAGES, math.ceil(target_reviews / REVIEWS_PER_PAGE)), 15)

    ensure_dirs()
    api_key = load_api_key()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.time() * 1000

    client = create_client(api_key, on_event=lambda event: append_error_event({"label": "single_domain_test", **event}))

    result = fetch_domain_reviews(domain, max_pages, client, latencies)
    valid_entries = [e for e in result["collected"] if is_valid_review(e["raw"])]
    missing_tally = {}
    for e in result["collected"]:
        for f in missing_fields_for(e["raw"]):
            missing_tally[f] = missing_tally.get(f, 0) + 1

    dedupe_result = dedupe(valid_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]

    benchmark_end_ms = time.time() * 1000
    wall_clock_ms = int(benchmark_end_ms - benchmark_start_ms)
    latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
    median = latency_values[len(latency_values) // 2] if latency_values else None

    write_json(OUT_DIR / "timings.json", {
        "benchmark_start": benchmark_start, "benchmark_end": now_iso(),
        "wall_clock_ms": wall_clock_ms, "per_request": latencies, "median_latency_ms": median,
    })

    flat_reviews = []
    for e in unique:
        raw = e["raw"]
        flat_reviews.append({
            "domain": domain, "dedupe_key": e.get("dedupeKey"), "dedupe_key_type": e.get("dedupeKeyType"),
            "review_id": raw.get("review_id"), "review_rating": raw.get("review_rating"),
            "review_time": raw.get("review_time"), "review_title": raw.get("review_title"),
            "review_text": raw.get("review_text"), "consumer_name": raw.get("consumer_name"),
            "consumer_id": raw.get("consumer_id"),
        })
    write_json(OUT_DIR / "all-reviews.json", flat_reviews)
    write_text(OUT_DIR / "all-reviews.csv", to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "review_id", "review_rating", "review_time", "review_title", "review_text", "consumer_name", "consumer_id"]))
    write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
    write_json(OUT_DIR / "pagination-report.json", {"pages": result["pages"], "stop_reason": result["stopReason"], "page_at_which_wall_hit": result["pageAtWhichWallHit"]})

    summary = {
        "generated_at": now_iso(),
        "domain": domain,
        "target_reviews_requested": target_reviews,
        "max_pages_attempted": max_pages,
        "documented_max_page_without_cookie": DOCUMENTED_MAX_PAGE_WITHOUT_COOKIE,
        "pages_fetched": len(result["pages"]),
        "pagination_detail": result["pages"],
        "stop_reason": result["stopReason"],
        "page_at_which_wall_hit": result["pageAtWhichWallHit"],
        "documented_wall_confirmed": result["pageAtWhichWallHit"] is not None,
        "total_raw_items_fetched": len(result["collected"]),
        "total_valid_items": len(valid_entries),
        "total_unique_valid_reviews": len(unique),
        "total_duplicates": len(duplicates),
        "exceeded_200_reviews_from_one_business": len(unique) > 200,
        "wall_clock_ms": wall_clock_ms,
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
