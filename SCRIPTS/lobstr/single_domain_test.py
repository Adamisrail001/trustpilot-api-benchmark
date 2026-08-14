"""Standalone, isolated live test: how many reviews can lobstr.io's Trustpilot
Reviews Scraper actually return from ONE business when max_results is raised
well past the 200 value used in the published 5-domain benchmark?

This is intentionally a SEPARATE script from lobstr_benchmark.py:
- It creates its own brand-new, dedicated squid (never reuses
  LOBSTR_SQUID_ID from .env), so it cannot touch or contaminate the squid/
  results behind the published benchmark article.
- It writes to its own output directory (outputs/lobstr-single-domain-test/),
  never into outputs/lobstr/.
- It never writes to .env.

It reuses the same credentials (LOBSTR_API_KEY) and the same confirmed
Trustpilot crawler (LOBSTR_CRAWLER_ID) as the main benchmark, read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/lobstr_single_domain_test.py [domain] [target]

  domain  defaults to www.thepearlsource.com
  target  defaults to 1000 (max_results / max_unique_results_per_run for this one task)

This is a REAL paid run against the live lobstr.io API. Requires
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
from lib.lobstr_client import create_client, AuthOrBillingError, InvalidRequestError
from lib.dedupe import dedupe
from lib.csv_utils import to_csv

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "outputs" / "lobstr-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"

RESULTS_PAGE_LIMIT = 100  # requested; live API was observed capping effective page size at 10 regardless
MAX_RESULT_PAGES = 200  # safety cap, generous for a 1,000+ target at ~10/page
POLL_INTERVAL_MS = 8_000
MAX_POLL_WAIT_MS = 60 * 60_000  # 60 min - generous for a single-business deep pull


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def jg(obj, key, default=None):
    if not isinstance(obj, dict):
        return default
    value = obj.get(key)
    return value if value is not None else default


def coalesce(*values):
    for v in values:
        if v is not None:
            return v
    return None


def write_json(path, obj):
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8", newline="")


def read_env_lines():
    if not ENV_PATH.exists():
        raise Exception(".env not found.")
    return re.split(r"\r?\n", ENV_PATH.read_text(encoding="utf-8"))


def get_env_var(name):
    for line in read_env_lines():
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


def load_api_key():
    key = get_env_var("LOBSTR_API_KEY")
    if not key:
        raise Exception("LOBSTR_API_KEY not found or empty in .env.")
    return key


def task_url_for_domain(domain):
    return f"https://www.trustpilot.com/review/{domain}"


def ensure_dirs():
    for d in [OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8", newline="") as f:
        f.write(line + "\n")


def discover_crawler_id(client):
    existing = get_env_var("LOBSTR_CRAWLER_ID")
    if existing:
        print(f"[crawler] reusing LOBSTR_CRAWLER_ID from .env (read-only): {existing}")
        return existing
    res = client["listCrawlers"](1, 100)
    write_json(REQUESTS_DIR / "crawlers.json", {"fetched_at": now_iso(), "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"listCrawlers failed: HTTP {res['status']}")
    data = jg(res["json"], "data") or []
    found = next((c for c in data if re.search("trustpilot", c.get("name") or "", re.I) or re.search("trustpilot", c.get("slug") or "", re.I)), None)
    if not found:
        raise Exception('No crawler matching "trustpilot" found. Refusing to invent a crawler ID.')
    print(f"[crawler] discovered: \"{found.get('name')}\" ({found.get('id')})")
    return found["id"]


def create_dedicated_squid(client, crawler_id):
    name = f"Trustpilot Single-Domain Test - {now_iso()}"
    created = client["createSquid"](crawler=crawler_id, name=name)
    write_json(REQUESTS_DIR / "squid-create.json", {"requested_at": now_iso(), "request": {"crawler": crawler_id, "name": name}, "response": created["json"]})
    if not created["ok"] or not jg(created["json"], "id"):
        raise Exception(f"createSquid failed: HTTP {created['status']}")
    print(f"[squid] created NEW dedicated squid (isolated from the main benchmark): \"{name}\" ({created['json']['id']})")
    return created["json"]["id"]


def configure_squid(client, squid_id, target_reviews):
    details = client["getSquidDetails"](squid_id)
    write_json(REQUESTS_DIR / "squid-details-before-configure.json", {"checked_at": now_iso(), "response": details["json"]})
    params_before = jg(details["json"], "params") or {}

    new_params = dict(params_before)
    notes = []
    if "max_results" in new_params:
        new_params["max_results"] = target_reviews
        notes.append(f"max_results: {params_before.get('max_results')} -> {target_reviews}")
    else:
        notes.append("max_results key not present in default params - left untouched (Pending).")
    if "max_unique_results_per_run" in new_params:
        new_params["max_unique_results_per_run"] = target_reviews
        notes.append(f"max_unique_results_per_run: {params_before.get('max_unique_results_per_run')} -> {target_reviews}")
    else:
        notes.append("max_unique_results_per_run key not present in default params - left untouched (Pending).")

    body = {
        "is_active": True,
        "to_complete": True,
        "export_unique_results": False,
        "no_line_breaks": False,
        "params": new_params,
    }
    res = client["updateSquid"](squid_id, body)
    write_json(REQUESTS_DIR / "squid-configure.json", {"requested_at": now_iso(), "request_body": body, "notes": notes, "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"updateSquid failed: HTTP {res['status']}")

    details_after = client["getSquidDetails"](squid_id)
    write_json(REQUESTS_DIR / "squid-details-after-configure.json", {"checked_at": now_iso(), "response": details_after["json"]})
    params_after = jg(details_after["json"], "params") or {}
    return {"params_before": params_before, "params_after": params_after, "notes": notes}


def add_task(client, squid_id, domain):
    res = client["addTasks"](squid_id, [{"url": task_url_for_domain(domain)}])
    write_json(REQUESTS_DIR / "tasks.json", {"requested_at": now_iso(), "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"addTasks failed: HTTP {res['status']}")
    tasks = jg(res["json"], "tasks") or []
    task = next((t for t in tasks if jg(t.get("params"), "url") == task_url_for_domain(domain)), None)
    return jg(task, "id") if task else None


def start_run(client, squid_id):
    res = client["startRun"](squid_id)
    if not res["ok"] or not jg(res["json"], "id"):
        raise Exception(f"startRun failed: HTTP {res['status']}")
    write_json(REQUESTS_DIR / "run-start.json", {"requested_at": now_iso(), "response": res["json"]})
    print(f"[run] started ONE paid run: {res['json']['id']}")
    return res["json"]["id"]


def poll_run_to_terminal(client, run_id, latencies):
    stop_statuses = {"DONE", "ERROR", "ABORTED", "PAUSED"}
    poll_history = []
    poll_start = time.monotonic()
    last_run = None
    while (time.monotonic() - poll_start) * 1000 < MAX_POLL_WAIT_MS:
        res = client["getRun"](run_id)
        latencies.append({"phase": "poll_run", "ms": res["latencyMs"], "attempts": res["attempts"]})
        if not res["ok"]:
            append_error_event({"type": "get_run_error", "runId": run_id, "response": res["json"]})
            poll_history.append({"polled_at": now_iso(), "error": f"HTTP {res['status']}"})
            sleep_ms(POLL_INTERVAL_MS)
            continue
        last_run = res["json"]
        poll_history.append({
            "polled_at": now_iso(),
            "status": last_run.get("status"),
            "is_done": last_run.get("is_done"),
            "total_results": last_run.get("total_results"),
            "total_unique_results": last_run.get("total_unique_results"),
            "credit_used": last_run.get("credit_used"),
        })
        print(f"[poll] run {run_id}: status={last_run.get('status')} total_results={coalesce(last_run.get('total_results'), '-')} unique={coalesce(last_run.get('total_unique_results'), '-')}")
        if (last_run.get("status") or "").upper() in stop_statuses:
            break
        sleep_ms(POLL_INTERVAL_MS)
    write_json(OUT_DIR / "run-state.json", {"run_id": run_id, "poll_history": poll_history, "final": last_run})
    return last_run


def fetch_all_results(client, run_id, latencies):
    current_page = 1
    use_next_url = None
    seen_page_markers = set()
    all_items = []
    pages = []
    stop_reason = None
    while current_page <= MAX_RESULT_PAGES:
        if use_next_url:
            res = client["getResultsByUrl"](use_next_url)
        else:
            res = client["getResults"](run=run_id, page=current_page, limit=RESULTS_PAGE_LIMIT)
        latencies.append({"phase": "get_results", "page": current_page, "ms": res["latencyMs"], "attempts": res["attempts"]})
        write_json(RESULTS_DIR / f"results-page{current_page}.json", {"page": current_page, "fetched_at": now_iso(), "response": res["json"]})
        if not res["ok"]:
            append_error_event({"type": "get_results_error", "page": current_page, "response": res["json"]})
            stop_reason = "results_fetch_error"
            break
        data = jg(res["json"], "data") or []
        page_marker = ",".join("" if d.get("id") is None else str(d.get("id")) for d in data)
        if len(data) > 0 and page_marker in seen_page_markers:
            append_error_event({"type": "repeated_results_page", "page": current_page})
            pages.append({"page": current_page, "count": len(data), "repeated": True})
            stop_reason = "repeated_page"
            break
        seen_page_markers.add(page_marker)
        all_items.extend(data)
        pages.append({"page": current_page, "count": len(data), "total_results": jg(res["json"], "total_results"), "total_pages": jg(res["json"], "total_pages")})
        print(f"[results] page {current_page}: {len(data)} items (total_results={coalesce(jg(res['json'], 'total_results'), '-')})")
        next_field = jg(res["json"], "next")
        if not next_field:
            stop_reason = "no_next_page"
            break
        use_next_url = next_field
        current_page += 1
    if not stop_reason:
        stop_reason = "max_pages_cap"
    return {"allItems": all_items, "pages": pages, "stopReason": stop_reason}


_BARE_ID_RE = re.compile(r"^[a-f0-9]{16,32}$", re.I)
_IN_URL_ID_RE = re.compile(r"reviews/([a-f0-9]{16,32})", re.I)


def extract_trustpilot_review_id(review_url_or_link):
    if not review_url_or_link:
        return None
    m = _BARE_ID_RE.match(review_url_or_link)
    if m:
        return m.group(0)
    m2 = _IN_URL_ID_RE.search(review_url_or_link)
    return m2.group(1) if m2 else None


def normalize_review_for_dedupe(item):
    extracted_id = extract_trustpilot_review_id(item.get("review_url")) or extract_trustpilot_review_id(item.get("review_link"))
    return {
        "id": coalesce(extracted_id, item.get("id")),
        "url": coalesce(item.get("review_link"), item.get("review_url")),
        "user_profile": {"name": item.get("author_name")},
        "timestamp": item.get("date_published"),
        "rating": coalesce(item.get("rating_value"), item.get("stars")),
        "title": item.get("review_headline"),
        "review_text": item.get("review_body"),
    }


def is_valid_review(item):
    has_id = bool(item.get("review_url")) or bool(item.get("id"))
    has_rating = item.get("rating_value") is not None or item.get("stars") is not None
    has_date = bool(item.get("date_published"))
    has_text = bool(item.get("review_headline")) or bool(item.get("review_body"))
    has_reviewer = bool(item.get("author_name")) or bool(item.get("author_id"))
    return bool(has_id and has_rating and has_date and has_text and has_reviewer)


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating a real paid Lobstr.io run.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    target_reviews = int(sys.argv[2]) if len(sys.argv) > 2 else 1000

    ensure_dirs()
    api_key = load_api_key()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.monotonic()

    client = create_client({"apiKey": api_key}, lambda event: append_error_event({"label": "single_domain_test", **event}))

    balance_before = None
    try:
        bal_res = client["getBalance"]()
        write_json(OUT_DIR / "credits-before.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_before = bal_res["json"]
    except Exception as err:
        append_error_event({"type": "balance_before_failed", "message": str(err)})

    crawler_id = discover_crawler_id(client)
    squid_id = create_dedicated_squid(client, crawler_id)
    configure_result = configure_squid(client, squid_id, target_reviews)
    task_id = add_task(client, squid_id, domain)

    run_id = None
    final_run = None
    try:
        run_id = start_run(client, squid_id)
        final_run = poll_run_to_terminal(client, run_id, latencies)
    except AuthOrBillingError as err:
        write_json(ERRORS_DIR / "BLOCKER-auth-or-billing.json", {"message": err.message, "status": err.status, "body": err.body})
        print(f"BLOCKER: authentication/billing failure: {err.message}", file=sys.stderr)
        sys.exit(2)
    except InvalidRequestError as err:
        write_json(ERRORS_DIR / "BLOCKER-invalid-request.json", {"message": err.message, "status": err.status, "body": err.body})
        print(f"BLOCKER: invalid request starting run: {err.message}", file=sys.stderr)
        sys.exit(2)

    status_upper = (jg(final_run, "status") or "").upper()
    run_succeeded = status_upper == "DONE"

    results = fetch_all_results(client, run_id, latencies)
    all_items = results["allItems"]
    results_stop_reason = results["stopReason"]

    balance_after = None
    try:
        bal_res = client["getBalance"]()
        write_json(OUT_DIR / "credits-after.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_after = bal_res["json"]
    except Exception as err:
        append_error_event({"type": "balance_after_failed", "message": str(err)})

    valid_entries = []
    missing_tally = {}
    for item in all_items:
        if is_valid_review(item):
            valid_entries.append({"domain": domain, "review": normalize_review_for_dedupe(item), "raw": item})

    dedupe_result = dedupe(valid_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]

    flat_reviews = [
        {
            "domain": domain,
            "dedupe_key": e["dedupeKey"],
            "dedupe_key_type": e["dedupeKeyType"],
            "review_url": e["raw"].get("review_url"),
            "trustpilot_review_id": extract_trustpilot_review_id(e["raw"].get("review_url")),
            "rating_value": coalesce(e["raw"].get("rating_value"), e["raw"].get("stars")),
            "date_published": e["raw"].get("date_published"),
            "review_headline": e["raw"].get("review_headline"),
            "review_body": e["raw"].get("review_body"),
            "author_name": e["raw"].get("author_name"),
            "author_id": e["raw"].get("author_id"),
        }
        for e in unique
    ]
    write_json(OUT_DIR / "all-reviews.json", flat_reviews)
    (OUT_DIR / "all-reviews.csv").write_text(
        to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "review_url", "trustpilot_review_id", "rating_value", "date_published", "review_headline", "review_body", "author_name", "author_id"]),
        encoding="utf-8",
        newline="",
    )
    write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
    write_json(OUT_DIR / "pagination-report.json", {"pages": results["pages"], "stop_reason": results_stop_reason})

    benchmark_end_ms = time.monotonic()
    credits_consumed = None
    if (
        balance_before is not None
        and balance_after is not None
        and isinstance(balance_before.get("consumed"), (int, float))
        and isinstance(balance_after.get("consumed"), (int, float))
    ):
        credits_consumed = balance_after["consumed"] - balance_before["consumed"]

    summary = {
        "generated_at": now_iso(),
        "domain": domain,
        "squid_id": squid_id,
        "task_id": task_id,
        "run_id": run_id,
        "target_reviews_requested": target_reviews,
        "max_results_confirmed_after_configure": configure_result["params_after"].get("max_results"),
        "max_unique_results_per_run_confirmed_after_configure": configure_result["params_after"].get("max_unique_results_per_run"),
        "run_status": jg(final_run, "status"),
        "run_succeeded": run_succeeded,
        "run_reported_total_results": jg(final_run, "total_results"),
        "run_reported_total_unique_results": jg(final_run, "total_unique_results"),
        "run_reported_credit_used": jg(final_run, "credit_used"),
        "total_raw_items_fetched": len(all_items),
        "total_valid_items": len(valid_entries),
        "total_unique_valid_reviews": len(unique),
        "total_duplicates": len(duplicates),
        "exceeded_200_reviews_from_one_business": len(unique) > 200,
        "wall_clock_ms": int((benchmark_end_ms - benchmark_start_ms) * 1000),
        "credits_consumed_measured": credits_consumed,
        "pagination_stop_reason": results_stop_reason,
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
