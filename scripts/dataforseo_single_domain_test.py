"""Standalone, isolated live test: how many reviews can DataForSEO's
Trustpilot Reviews endpoint actually return from ONE business when `depth`
is raised well past the 200 value used in the published 5-domain benchmark?

This directly tests a documented limit: data/analysis/dataforseo/execution-plan.json
records `documented_limits.max_depth_per_task: 200` with no pagination
parameter available in DataForSEO's official docs. This script finds out
empirically whether that cap actually holds (task rejected / depth clamped
to 200 / or genuinely more returned) rather than assuming it does.

This is intentionally a SEPARATE script from dataforseo_benchmark.py:
- It posts its own task and writes to its own output directory
  (outputs/dataforseo-single-domain-test/), never outputs/dataforseo/ or
  data/raw/dataforseo/ - so it cannot touch or contaminate the task/results
  behind the published benchmark article.
- It never writes to .env.

It reuses the same credentials (DATAFORSEO_LOGIN, DATAFORSEO_PASSWORD) as
the main benchmark, read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/dataforseo_single_domain_test.py [domain] [target]

  domain  defaults to www.thepearlsource.com
  target  defaults to 1000 (the `depth` param for this one task)

This is a REAL paid task against the live DataForSEO API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as the main benchmark script.
"""
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib.env import load_env, require_env
from lib.dedupe import dedupe
from lib.csv_utils import to_csv

load_env()

ROOT = Path(__file__).resolve().parent.parent
OUT_DIR = ROOT / "outputs" / "dataforseo-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
ERRORS_DIR = OUT_DIR / "errors"

BASE_URL = "https://api.dataforseo.com/v3/business_data/trustpilot/reviews"
POLL_INTERVAL_S = 15
MAX_POLL_ATTEMPTS = 60  # 15 min at 15s/poll - generous for a single deep task


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
    for d in [OUT_DIR, REQUESTS_DIR, ERRORS_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False) + "\n")


def auth_header():
    login = require_env("DATAFORSEO_LOGIN")
    password = require_env("DATAFORSEO_PASSWORD")
    token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _request(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth_header())
    if data is not None:
        req.add_header("Content-Type", "application/json")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(req) as res:
            body_json = json.loads(res.read().decode("utf-8"))
            status = res.status
    except urllib.error.HTTPError as err:
        body_json = json.loads(err.read().decode("utf-8"))
        status = err.code
    latency_ms = int((time.monotonic() - start) * 1000)
    return {"status": status, "json": body_json, "latency_ms": latency_ms}


def post_task(domain, depth):
    task_file = REQUESTS_DIR / "task-post-response.json"
    if task_file.exists():
        saved = json.loads(task_file.read_text(encoding="utf-8"))
        task_id = saved.get("task_id")
        if task_id:
            print(f"[task] reusing existing saved task id: {task_id} (idempotent - no new paid task created).")
            return task_id, saved.get("response")

    body = [{"target": domain, "depth": depth, "sort_by": "recency", "priority": 1, "tag": f"single-domain-test-{domain}-{int(time.time() * 1000)}"}]
    write_json(REQUESTS_DIR / "task-post-request.json", {"requested_at": now_iso(), "body": body})
    result = _request("POST", f"{BASE_URL}/task_post", body)
    response = result["json"]
    tasks = response.get("tasks") or []
    task = tasks[0] if tasks else None
    task_id = task.get("id") if task else None
    post_status_code = task.get("status_code") if task else None
    post_status_message = task.get("status_message") if task else None
    write_json(
        task_file,
        {
            "requested_at": now_iso(),
            "task_id": task_id,
            "post_status_code": post_status_code,
            "post_status_message": post_status_message,
            "rejected_at_post": post_status_code is not None and post_status_code != 20000,
            "latency_ms": result["latency_ms"],
            "response": response,
        },
    )
    if not task_id:
        raise RuntimeError(f"No task id returned for {domain}: {json.dumps(response)}")
    if post_status_code is not None and post_status_code != 20000:
        # DataForSEO can echo back a task id even when the task itself was
        # rejected at submission time (e.g. depth exceeding the documented
        # max_depth_per_task=200 cap) - a rejected task is never queued, so
        # polling it will just spin until it 404s. Surface this immediately.
        print(f"[task] REJECTED at post time: {task_id} status_code={post_status_code} \"{post_status_message}\" (requested depth={depth})")
    else:
        print(f"[task] posted ONE paid task: {task_id} (requested depth={depth})")
    return task_id, response


def get_task(task_id):
    return _request("GET", f"{BASE_URL}/task_get/{task_id}")


def poll_until_ready(task_id, latencies):
    poll_history = []
    for attempt in range(1, MAX_POLL_ATTEMPTS + 1):
        result = get_task(task_id)
        latencies.append({"phase": "task_get", "attempt": attempt, "ms": result["latency_ms"]})
        response = result["json"]
        tasks = response.get("tasks") or []
        task = tasks[0] if tasks else None
        status_code = task.get("status_code") if task else None
        task_result = task.get("result") if task else None
        poll_history.append({"polled_at": now_iso(), "status_code": status_code, "status_message": task.get("status_message") if task else None})
        print(f"[poll] task {task_id}: status_code={status_code} attempt={attempt}")
        if task_result:
            write_json(REQUESTS_DIR / "task-get-response.json", {"fetched_at": now_iso(), "response": response})
            write_json(OUT_DIR / "poll-history.json", {"task_id": task_id, "poll_history": poll_history})
            return response, task
        # Mirrors dataforseo_benchmark.py's poll_until_ready: never treat an
        # error status_code (e.g. 40401 "Task Not Found") as terminal on its
        # own - DataForSEO tasks are processed asynchronously and the task
        # can be briefly unindexed right after task_post. Only give up after
        # exhausting MAX_POLL_ATTEMPTS.
        if status_code and status_code >= 40000:
            append_error_event({"type": "task_error_status", "task_id": task_id, "status_code": status_code, "response": response})
        time.sleep(POLL_INTERVAL_S)
    write_json(OUT_DIR / "poll-history.json", {"task_id": task_id, "poll_history": poll_history})
    raise RuntimeError(f"Task {task_id} did not become ready after {MAX_POLL_ATTEMPTS} polls")


def normalize_review_for_dedupe(item):
    return {
        "id": None,
        "url": item.get("url"),
        "user_profile": {"name": (item.get("user_profile") or {}).get("name")},
        "timestamp": item.get("timestamp"),
        "rating": (item.get("rating") or {}).get("value"),
        "title": item.get("title"),
        "review_text": item.get("review_text"),
    }


def is_valid_review(item):
    has_id = bool(item.get("url"))
    has_rating = (item.get("rating") or {}).get("value") is not None
    has_date = bool(item.get("timestamp"))
    has_text = bool(item.get("title")) or bool(item.get("review_text"))
    has_author = bool((item.get("user_profile") or {}).get("name"))
    return bool(has_id and has_rating and has_date and has_text and has_author)


def missing_fields_for(item):
    missing = []
    if not item.get("url"):
        missing.append("url")
    if (item.get("rating") or {}).get("value") is None:
        missing.append("rating")
    if not item.get("timestamp"):
        missing.append("timestamp")
    if not item.get("title") and not item.get("review_text"):
        missing.append("title_or_review_text")
    if not (item.get("user_profile") or {}).get("name"):
        missing.append("user_profile.name")
    return missing


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating a real paid DataForSEO task.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    target_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    ensure_dirs()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.monotonic()

    try:
        task_id, post_response = post_task(domain, target_reviews)
        post_tasks = post_response.get("tasks") or []
        post_task_obj = post_tasks[0] if post_tasks else None
        post_status_code = post_task_obj.get("status_code") if post_task_obj else None

        if post_status_code is not None and post_status_code != 20000:
            wall_clock_ms = int((time.monotonic() - benchmark_start_ms) * 1000)
            summary = {
                "generated_at": now_iso(),
                "domain": domain,
                "task_id": task_id,
                "target_reviews_requested_depth": target_reviews,
                "outcome": "rejected_at_task_post",
                "task_post_status_code": post_status_code,
                "task_post_status_message": post_task_obj.get("status_message"),
                "total_unique_valid_reviews": 0,
                "exceeded_200_reviews_from_one_business": False,
                "wall_clock_ms": wall_clock_ms,
                "task_post_cost_usd": post_task_obj.get("cost"),
                "note": "DataForSEO rejected the task at submission time (never queued) - the documented max_depth_per_task=200 cap (see execution-plan.json) held as a hard API-level wall for this depth value.",
            }
            write_json(OUT_DIR / "summary.json", summary)
            print("--- SINGLE-DOMAIN TEST COMPLETE (task rejected at post) ---")
            print(json.dumps(summary, indent=2, ensure_ascii=False))
            return

        get_response, task = poll_until_ready(task_id, latencies)

        task_result = task.get("result") if task else None
        result0 = task_result[0] if task_result else None
        all_items = (result0.get("items") if result0 else None) or []
        requested_depth_echoed = ((task.get("data") or {}).get("depth")) if task else None

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

        benchmark_end_ms = time.monotonic()
        wall_clock_ms = int((benchmark_end_ms - benchmark_start_ms) * 1000)
        latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
        median = latency_values[len(latency_values) // 2] if latency_values else None
        avg = round(sum(latency_values) / len(latency_values), 1) if latency_values else None

        write_json(
            OUT_DIR / "timings.json",
            {
                "benchmark_start": benchmark_start,
                "benchmark_end": now_iso(),
                "wall_clock_ms": wall_clock_ms,
                "per_request": latencies,
                "avg_latency_ms": avg,
                "median_latency_ms": median,
            },
        )

        flat_reviews = [
            {
                "domain": domain,
                "dedupe_key": e["dedupeKey"],
                "dedupe_key_type": e["dedupeKeyType"],
                "url": e["raw"].get("url"),
                "rating": (e["raw"].get("rating") or {}).get("value"),
                "title": e["raw"].get("title"),
                "review_text": e["raw"].get("review_text"),
                "timestamp": e["raw"].get("timestamp"),
                "verified": e["raw"].get("verified"),
                "language": e["raw"].get("language"),
                "author_name": (e["raw"].get("user_profile") or {}).get("name"),
                "author_location": (e["raw"].get("user_profile") or {}).get("location"),
                "author_reviews_count": (e["raw"].get("user_profile") or {}).get("reviews_count"),
                "rank_absolute": e["raw"].get("rank_absolute"),
            }
            for e in unique
        ]
        write_json(OUT_DIR / "all-reviews.json", flat_reviews)
        write_text(
            OUT_DIR / "all-reviews.csv",
            to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "url", "rating", "title", "review_text", "timestamp", "verified", "language", "author_name", "author_location", "author_reviews_count", "rank_absolute"]),
        )
        write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})

        task_cost = task.get("cost") if task else None
        post_tasks = post_response.get("tasks") if isinstance(post_response, dict) else None
        post_cost = post_tasks[0].get("cost") if post_tasks else None

        summary = {
            "generated_at": now_iso(),
            "domain": domain,
            "task_id": task_id,
            "target_reviews_requested_depth": target_reviews,
            "requested_depth_echoed_back_by_api": requested_depth_echoed,
            "depth_was_clamped": (requested_depth_echoed is not None and requested_depth_echoed != target_reviews),
            "task_status_code": task.get("status_code") if task else None,
            "task_status_message": task.get("status_message") if task else None,
            "items_count_reported": result0.get("items_count") if result0 else None,
            "total_raw_items_fetched": len(all_items),
            "total_valid_items": len(valid_entries),
            "total_unique_valid_reviews": len(unique),
            "total_duplicates": len(duplicates),
            "exceeded_200_reviews_from_one_business": len(unique) > 200,
            "wall_clock_ms": wall_clock_ms,
            "task_post_cost_usd": post_cost,
            "task_get_cost_usd": task_cost,
            "missing_field_counts": missing_tally,
            "note": "Costs are copied verbatim from the DataForSEO response - never invented.",
        }
        write_json(OUT_DIR / "summary.json", summary)

        print("--- SINGLE-DOMAIN TEST COMPLETE ---")
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    except Exception as err:
        write_json(ERRORS_DIR / "BLOCKER.json", {"message": str(err)})
        print(f"BLOCKER: {err}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
