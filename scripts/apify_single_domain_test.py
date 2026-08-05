"""Standalone, isolated live test: how many reviews can Apify's Trustpilot
Reviews Scraper (automation-lab/trustpilot) actually return from ONE business
when maxReviewsPerCompany is raised well past the 200 value used in the
published 5-domain benchmark?

This is intentionally a SEPARATE script from apify_benchmark.py:
- It starts its own Actor run and writes to its own output directory
  (outputs/apify-single-domain-test/), never outputs/apify/ - so it cannot
  touch or contaminate the run/results behind the published benchmark
  article.
- It never writes to .env.

It reuses the same credentials (APIFY_API_TOKEN, APIFY_ACTOR_ID) as the main
benchmark, read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/apify_single_domain_test.py [domain] [target]

  domain  defaults to www.thepearlsource.com
  target  defaults to 1000 (maxReviewsPerCompany for this one task)

This is a REAL paid run against the live Apify API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as the main benchmark script.
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
from lib.apify_client import ApifyClient, AuthOrBillingError, InvalidRequestError
from lib.dedupe import dedupe
from lib.csv_utils import to_csv

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "apify-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RUNS_DIR = OUT_DIR / "raw" / "runs"
DATASETS_DIR = OUT_DIR / "raw" / "datasets"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"

POLL_INTERVAL_MS = 10_000
MAX_POLL_WAIT_MS = 60 * 60_000  # 60 min - generous for a single-business deep pull
SETTLE_WAIT_MS = 5_000  # per docs: "wait briefly ... finalized usage values may take a few seconds to settle"
DATASET_PAGE_LIMIT = 1000
MAX_DATASET_PAGES = 20

RUN_START_FEE_USD = 0.005
FREE_TIER_PER_REVIEW_USD = 0.000575

TERMINAL_SUCCESS = {"SUCCEEDED"}
TERMINAL_FAILURE = {"FAILED", "ABORTED", "TIMED-OUT"}


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def now_ms():
    return int(time.time() * 1000)


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def to_fixed(value, digits):
    rounded = float(f"{value:.{digits}f}")
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def dump_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(dump_json(obj))


def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def get_env_var(name):
    if not ENV_PATH.exists():
        raise RuntimeError(".env not found.")
    text = ENV_PATH.read_text(encoding="utf-8")
    for line in re.split(r"\r?\n", text):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        idx = trimmed.find("=")
        if idx == -1:
            continue
        if trimmed[:idx].strip() == name:
            value = trimmed[idx + 1:].strip()
            return value or None
    return None


def load_api_token():
    token = get_env_var("APIFY_API_TOKEN")
    if not token:
        raise RuntimeError("APIFY_API_TOKEN not found or empty in .env.")
    return token


def load_rest_actor_id():
    actor_id = get_env_var("APIFY_ACTOR_ID")
    if not actor_id:
        raise RuntimeError("APIFY_ACTOR_ID not found or empty in .env.")
    return actor_id.replace("/", "~", 1) if "/" in actor_id else actor_id


def ensure_dirs(dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


_SAFE_NAME_RE = re.compile(r"[^a-z0-9.\-]", re.IGNORECASE)


def safe_domain_name(domain):
    return _SAFE_NAME_RE.sub("_", domain)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    record = {"loggedAt": now_iso(), **event}
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


# ---------- normalization / validity (same rules as apify_benchmark.py) ----------


def normalize_review_for_dedupe(item):
    return {
        "id": item.get("reviewId"),
        "url": item.get("reviewUrl"),
        "user_profile": {"name": item.get("authorName")},
        "timestamp": item.get("publishedDate"),
        "rating": item.get("rating"),
        "title": item.get("title"),
        "review_text": item.get("text"),
    }


def is_valid_review(item):
    has_id = bool(item.get("reviewId")) or bool(item.get("reviewUrl"))
    has_rating = item.get("rating") is not None
    has_date = bool(item.get("publishedDate"))
    has_text = bool(item.get("title")) or bool(item.get("text"))
    has_author = bool(item.get("authorName")) or bool(item.get("authorId"))
    return bool(has_id and has_rating and has_date and has_text and has_author)


def missing_fields_for(item):
    missing = []
    if not item.get("reviewId") and not item.get("reviewUrl"):
        missing.append("reviewId_or_reviewUrl")
    if item.get("rating") is None:
        missing.append("rating")
    if not item.get("publishedDate"):
        missing.append("publishedDate")
    if not item.get("title") and not item.get("text"):
        missing.append("title_or_text")
    if not item.get("authorName") and not item.get("authorId"):
        missing.append("authorName_or_authorId")
    return missing


# ---------- run (single paid trigger, idempotent) ----------


def ensure_single_run(client, rest_actor_id, input_body, safe):
    run_file = RUNS_DIR / f"{safe}-run.json"
    if run_file.exists():
        saved = json.loads(run_file.read_text(encoding="utf-8"))
        print(f"[run] reusing existing saved run id: {saved['run_id']} (idempotent - no new Actor run created).")
        return saved["run_id"]

    write_json(
        REQUESTS_DIR / f"{safe}-actor-input.json",
        {"saved_at": now_iso(), "actor_id": rest_actor_id, "input": input_body},
    )

    result = client.start_actor_run(rest_actor_id, input_body)
    write_json(
        RUNS_DIR / f"{safe}-run-create-response.json",
        {
            "requested_at": now_iso(),
            "request_url": result.get("request_url"),
            "latency_ms": result.get("latency_ms"),
            "attempts": result.get("attempts"),
            "ok": result.get("ok"),
            "status": result.get("status"),
            "response": result.get("json"),
        },
    )

    json_body = result.get("json")
    data = json_body.get("data") if isinstance(json_body, dict) else None
    data_id = data.get("id") if isinstance(data, dict) else None
    if not result.get("ok") or not data_id:
        raise RuntimeError(f"startActorRun failed: HTTP {result.get('status')}")

    run_id = data_id
    write_json(run_file, {"run_id": run_id, "started_at": now_iso(), "raw": data})
    print(f"[run] started ONE paid Actor run: {run_id}")
    return run_id


def poll_run_to_terminal(client, run_id, latencies, safe):
    poll_history = []
    poll_start = now_ms()
    last_run = None

    while now_ms() - poll_start < MAX_POLL_WAIT_MS:
        res = client.get_run(run_id)
        latencies.append({"phase": "get_run", "ms": res.get("latency_ms"), "attempts": res.get("attempts")})
        if not res.get("ok"):
            append_error_event({"type": "get_run_error", "runId": run_id, "response": res.get("json")})
            poll_history.append({"polled_at": now_iso(), "error": f"HTTP {res.get('status')}"})
            sleep_ms(POLL_INTERVAL_MS)
            continue
        last_run = res["json"]["data"]
        poll_history.append(
            {
                "polled_at": now_iso(),
                "status": last_run.get("status"),
                "defaultDatasetId": last_run.get("defaultDatasetId"),
            }
        )
        print(f"[poll] run {run_id}: status={last_run.get('status')}")
        if last_run.get("status") in TERMINAL_SUCCESS or last_run.get("status") in TERMINAL_FAILURE:
            break
        sleep_ms(POLL_INTERVAL_MS)

    write_json(RUNS_DIR / f"{safe}-poll-history.json", {"run_id": run_id, "poll_history": poll_history})
    return last_run


def fetch_final_run_object(client, run_id, safe):
    sleep_ms(SETTLE_WAIT_MS)
    res = client.get_run(run_id)
    final_run = res["json"]["data"] if res.get("ok") else None
    write_json(RUNS_DIR / f"{safe}-run-final.json", {"fetched_at": now_iso(), "response": res.get("json")})
    return final_run


# ---------- dataset retrieval (offset/limit, loop-safe, idempotent) ----------


def fetch_all_dataset_items(client, dataset_id, latencies, safe):
    offset = 0
    page_num = 1
    all_items = []
    pages = []
    seen_offsets = set()
    stop_reason = None

    while page_num <= MAX_DATASET_PAGES:
        page_file = DATASETS_DIR / f"{safe}-page{page_num}-offset{offset}.json"

        if page_file.exists():
            saved = json.loads(page_file.read_text(encoding="utf-8"))
            items = saved["response"]
            pagination = saved.get("pagination") or {}
            pagination_count = pagination.get("count")
            pagination_total = pagination.get("total")
            print(f"[dataset] page {page_num} (offset {offset}): reusing existing saved page (idempotent).")
        else:
            res = client.get_dataset_items(dataset_id, offset=offset, limit=DATASET_PAGE_LIMIT)
            latencies.append(
                {
                    "phase": "get_dataset_items",
                    "page": page_num,
                    "offset": offset,
                    "ms": res.get("latency_ms"),
                    "attempts": res.get("attempts"),
                }
            )
            if not res.get("ok"):
                append_error_event(
                    {
                        "type": "dataset_fetch_failed",
                        "page": page_num,
                        "offset": offset,
                        "status": res.get("status"),
                        "body": res.get("json"),
                    }
                )
                stop_reason = "fetch_failed"
                break
            items = res.get("json") if isinstance(res.get("json"), list) else []
            pagination_count = res.get("pagination_count")
            pagination_total = res.get("pagination_total")
            write_json(
                page_file,
                {
                    "page": page_num,
                    "offset": offset,
                    "fetched_at": now_iso(),
                    "pagination": {
                        "offset": res.get("pagination_offset"),
                        "limit": res.get("pagination_limit"),
                        "count": res.get("pagination_count"),
                        "total": res.get("pagination_total"),
                    },
                    "response": items,
                },
            )

        pages.append(
            {
                "page": page_num,
                "offset": offset,
                "raw_count": len(items),
                "pagination_count": pagination_count if pagination_count is not None else None,
                "pagination_total": pagination_total if pagination_total is not None else None,
            }
        )

        if len(items) == 0:
            stop_reason = "empty_page"
            break
        if offset in seen_offsets:
            stop_reason = "repeated_offset"
            break
        seen_offsets.add(offset)
        all_items.extend(items)

        next_offset = offset + len(items)
        if isinstance(pagination_total, (int, float)) and next_offset >= pagination_total:
            stop_reason = "all_items_downloaded"
            break
        if len(items) < DATASET_PAGE_LIMIT:
            stop_reason = "partial_last_page"
            break
        offset = next_offset
        page_num += 1

    if not stop_reason:
        stop_reason = "max_pages_cap"
    return all_items, pages, stop_reason


# ---------- main single-domain test ----------


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating a real paid Apify Actor run.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    target_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    safe = safe_domain_name(domain)

    ensure_dirs([OUT_DIR, REQUESTS_DIR, RUNS_DIR, DATASETS_DIR, ERRORS_DIR])
    api_token = load_api_token()
    rest_actor_id = load_rest_actor_id()

    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = now_ms()

    client = ApifyClient(api_token, on_event=lambda event: append_error_event({"label": "single_domain_test", **event}))

    input_body = {
        "companyUrls": [domain],
        "maxReviewsPerCompany": target_reviews,
        "sort": "recency",
        "includeCompanyInfo": True,
    }

    try:
        run_id = ensure_single_run(client, rest_actor_id, input_body, safe)
        actor_run_start_ms = now_ms()
        terminal_run = poll_run_to_terminal(client, run_id, latencies, safe)
        actor_run_duration_ms = now_ms() - actor_run_start_ms

        if not terminal_run or terminal_run.get("status") in TERMINAL_FAILURE:
            status_val = terminal_run.get("status") if terminal_run else None
            final_status = status_val if status_val is not None else "unknown/timeout"
            write_json(ERRORS_DIR / "BLOCKER-run-not-succeeded.json", {"run_id": run_id, "final_status": final_status})
            print(f"BLOCKER: Actor run did not succeed (status: {final_status}). Not retrying automatically.", file=sys.stderr)
            sys.exit(2)

        final_run = fetch_final_run_object(client, run_id, safe)
        dataset_id = (final_run.get("defaultDatasetId") if final_run else None) or terminal_run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError("No defaultDatasetId found on the completed run.")

        dataset_fetch_start_ms = now_ms()
        all_items, pages, stop_reason = fetch_all_dataset_items(client, dataset_id, latencies, safe)
        dataset_fetch_ms = now_ms() - dataset_fetch_start_ms

        # ---------- validate, dedupe (single domain - no cross-domain attribution needed) ----------
        valid_entries = []
        missing_tally = {}
        for item in all_items:
            for f in missing_fields_for(item):
                missing_tally[f] = missing_tally.get(f, 0) + 1
            if is_valid_review(item):
                valid_entries.append({"domain": domain, "review": normalize_review_for_dedupe(item), "raw": item})

        dedupe_result = dedupe(valid_entries)
        unique = dedupe_result["unique"]
        duplicates = dedupe_result["duplicates"]

        benchmark_end = now_iso()
        benchmark_end_ms = now_ms()
        latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
        median = latency_values[len(latency_values) // 2] if latency_values else None
        p95 = (
            latency_values[min(len(latency_values) - 1, math.floor(len(latency_values) * 0.95))]
            if latency_values
            else None
        )
        min_latency = latency_values[0] if latency_values else None
        max_latency = latency_values[-1] if latency_values else None
        avg = to_fixed(sum(latency_values) / len(latency_values), 1) if latency_values else None
        wall_clock_ms = benchmark_end_ms - benchmark_start_ms

        write_json(
            OUT_DIR / "timings.json",
            {
                "benchmark_start": benchmark_start,
                "benchmark_end": benchmark_end,
                "actor_run_duration_ms": actor_run_duration_ms,
                "dataset_retrieval_ms": dataset_fetch_ms,
                "wall_clock_ms": wall_clock_ms,
                "per_request": latencies,
                "min_latency_ms": min_latency,
                "max_latency_ms": max_latency,
                "avg_latency_ms": avg,
                "median_latency_ms": median,
                "p95_latency_ms": p95,
            },
        )

        flat_reviews = []
        for e in unique:
            raw = e["raw"]
            flat_reviews.append(
                {
                    "domain": domain,
                    "dedupe_key": e["dedupeKey"],
                    "dedupe_key_type": e["dedupeKeyType"],
                    "reviewId": raw.get("reviewId"),
                    "reviewUrl": raw.get("reviewUrl"),
                    "rating": raw.get("rating"),
                    "title": raw.get("title"),
                    "text": raw.get("text"),
                    "publishedDate": raw.get("publishedDate"),
                    "experienceDate": raw.get("experienceDate"),
                    "language": raw.get("language"),
                    "likes": raw.get("likes"),
                    "verificationLevel": raw.get("verificationLevel"),
                    "isVerified": raw.get("isVerified"),
                    "source": raw.get("source"),
                    "authorName": raw.get("authorName"),
                    "authorId": raw.get("authorId"),
                    "authorReviewCount": raw.get("authorReviewCount"),
                    "country": raw.get("country"),
                    "replyMessage": raw.get("replyMessage"),
                    "replyPublishedDate": raw.get("replyPublishedDate"),
                }
            )

        write_json(OUT_DIR / "all-reviews.json", flat_reviews)
        csv_columns = [
            "domain", "dedupe_key", "dedupe_key_type", "reviewId", "reviewUrl", "rating", "title", "text",
            "publishedDate", "experienceDate", "language", "likes", "verificationLevel", "isVerified", "source",
            "authorName", "authorId", "authorReviewCount", "country", "replyMessage", "replyPublishedDate",
        ]
        write_text(OUT_DIR / "all-reviews.csv", to_csv(flat_reviews, csv_columns))

        write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
        write_json(OUT_DIR / "pagination-report.json", {"pages": pages, "stop_reason": stop_reason})

        usage = final_run.get("usage") if final_run else None
        usage_usd = final_run.get("usageUsd") if final_run else None
        usage_total_usd = final_run.get("usageTotalUsd") if final_run else None
        estimated_free_tier_usd = to_fixed(len(unique) * FREE_TIER_PER_REVIEW_USD + RUN_START_FEE_USD, 4)

        write_json(
            OUT_DIR / "usage-report.json",
            {
                "generated_at": now_iso(),
                "run_id": run_id,
                "usage": usage,
                "usageUsd": usage_usd,
                "usageTotalUsd": usage_total_usd,
                "note": "usage/usageUsd/usageTotalUsd are copied verbatim from the settled Run object. Absent fields are Pending, not invented.",
            },
        )

        summary = {
            "generated_at": now_iso(),
            "domain": domain,
            "run_id": run_id,
            "dataset_id": dataset_id,
            "target_reviews_requested": target_reviews,
            "run_status": terminal_run.get("status"),
            "run_succeeded": terminal_run.get("status") in TERMINAL_SUCCESS,
            "total_raw_items_fetched": len(all_items),
            "total_valid_items": len(valid_entries),
            "total_unique_valid_reviews": len(unique),
            "total_duplicates": len(duplicates),
            "exceeded_200_reviews_from_one_business": len(unique) > 200,
            "wall_clock_ms": wall_clock_ms,
            "pagination_stop_reason": stop_reason,
            "estimated_cost_for_measured_unique_usd": estimated_free_tier_usd,
            "measured_actor_event_cost_usd": usage_usd,
            "measured_total_cost_usd": usage_total_usd,
            "cost_per_1000_successful_reviews_usd": to_fixed((usage_total_usd / len(unique)) * 1000, 4)
            if (usage_total_usd is not None and len(unique) > 0)
            else None,
            "missing_field_counts": missing_tally,
        }
        write_json(OUT_DIR / "summary.json", summary)

        print("--- SINGLE-DOMAIN TEST COMPLETE ---")
        print(dump_json(summary))
    except AuthOrBillingError as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(ERRORS_DIR / "BLOCKER-auth-or-billing.json", {"message": str(err), "status": err.status, "body": err.body})
        print(f"BLOCKER: authentication/billing failure: {err}", file=sys.stderr)
        sys.exit(2)
    except InvalidRequestError as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(ERRORS_DIR / "BLOCKER-invalid-request.json", {"message": str(err), "status": err.status, "body": err.body})
        print(f"BLOCKER: invalid request: {err}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
