"""Standalone, isolated live test: does the squid-level `concurrency` setting
change measured speed? Runs the same 5-domain / 200-per-domain / 1,000-total
shape as the main benchmark (concurrency needs >1 queued task to have
anything to run in parallel against), once at concurrency=1 and once at
concurrency=10, so the two runs are apples-to-apples on everything except
that one field.

`concurrency` is a real, documented, settable squid field (POST
/v1/squids/{squid_hash} accepts it - see api_docs_mcps.txt "Squid
Configuration"). Every prior run in this project used the default
(concurrency: 1, confirmed in every squid-details capture checked); no run
before this one ever set it to anything else.

This is intentionally a SEPARATE script from benchmark.py,
single_domain_test.py, and five_domain_multi_task_test.py:
- It creates its own brand-new, dedicated squid per run (never reuses
  LOBSTR_SQUID_ID from .env), so it cannot touch or contaminate the squid/
  results behind the published benchmark article or the other test scripts.
- It writes to its own output directory, namespaced by concurrency value
  (outputs/lobstr-concurrency-test/c<N>/), never into any other script's
  output directory.
- It never writes to .env.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/lobstr/concurrency_test.py <concurrency> [target_per_domain]

  concurrency         required, e.g. 1 or 10
  target_per_domain   defaults to 200 (5 domains x 200 = 1,000 total, same
                       shape as the main published benchmark)

This is a REAL paid run against the live lobstr.io API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as the other scripts.
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
BASE_OUT_DIR = ROOT / "outputs" / "lobstr-concurrency-test"
ENV_PATH = ROOT / ".env"
DOMAINS_PATH = ROOT / "benchmark-domains.json"

RESULTS_PAGE_SIZE = 1000  # real page-size param is `page_size`, not `limit` - see data/lobstr/analysis/page_size-parameter-correction.md
MAX_RESULT_PAGES = 200
POLL_INTERVAL_MS = 8_000
MAX_POLL_WAIT_MS = 60 * 60_000


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


def load_domains():
    if not DOMAINS_PATH.exists():
        raise Exception("benchmark-domains.json not found.")
    parsed = json.loads(DOMAINS_PATH.read_text(encoding="utf-8"))
    if not isinstance(parsed, list) or len(parsed) != 5:
        found = len(parsed) if isinstance(parsed, list) else type(parsed).__name__
        raise Exception(f"benchmark-domains.json must contain exactly 5 entries, found {found}.")
    return parsed


def task_url_for_domain(domain):
    return f"https://www.trustpilot.com/review/{domain}"


def ensure_dirs(out_dir, requests_dir, results_dir, errors_dir):
    for d in [out_dir, requests_dir, results_dir, errors_dir]:
        Path(d).mkdir(parents=True, exist_ok=True)


def append_error_event(errors_dir, event):
    Path(errors_dir).mkdir(parents=True, exist_ok=True)
    line = json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False)
    with open(Path(errors_dir) / "event-log.jsonl", "a", encoding="utf-8", newline="") as f:
        f.write(line + "\n")


def discover_crawler_id(client, requests_dir):
    existing = get_env_var("LOBSTR_CRAWLER_ID")
    if existing:
        print(f"[crawler] reusing LOBSTR_CRAWLER_ID from .env (read-only): {existing}")
        return existing
    res = client["listCrawlers"](1, 100)
    write_json(Path(requests_dir) / "crawlers.json", {"fetched_at": now_iso(), "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"listCrawlers failed: HTTP {res['status']}")
    data = jg(res["json"], "data") or []
    found = next((c for c in data if re.search("trustpilot", c.get("name") or "", re.I) or re.search("trustpilot", c.get("slug") or "", re.I)), None)
    if not found:
        raise Exception('No crawler matching "trustpilot" found. Refusing to invent a crawler ID.')
    print(f"[crawler] discovered: \"{found.get('name')}\" ({found.get('id')})")
    return found["id"]


def create_dedicated_squid(client, crawler_id, concurrency, requests_dir):
    name = f"Trustpilot Concurrency Test c{concurrency} - {now_iso()}"
    created = client["createSquid"](crawler=crawler_id, name=name)
    write_json(Path(requests_dir) / "squid-create.json", {"requested_at": now_iso(), "request": {"crawler": crawler_id, "name": name}, "response": created["json"]})
    if not created["ok"] or not jg(created["json"], "id"):
        raise Exception(f"createSquid failed: HTTP {created['status']}")
    print(f"[squid] created NEW dedicated squid (isolated from every other script): \"{name}\" ({created['json']['id']})")
    return created["json"]["id"]


def configure_squid(client, squid_id, concurrency, target_per_domain, domain_count, requests_dir):
    details = client["getSquidDetails"](squid_id)
    write_json(Path(requests_dir) / "squid-details-before-configure.json", {"checked_at": now_iso(), "response": details["json"]})
    params_before = jg(details["json"], "params") or {}
    concurrency_before = jg(details["json"], "concurrency")

    new_params = dict(params_before)
    notes = [f"concurrency: {concurrency_before} -> {concurrency}"]
    run_cap = target_per_domain * domain_count
    if "max_results" in new_params:
        new_params["max_results"] = target_per_domain
        notes.append(f"max_results (per task): {params_before.get('max_results')} -> {target_per_domain}")
    else:
        notes.append("max_results key not present in default params - left untouched (Pending).")
    if "max_unique_results_per_run" in new_params:
        new_params["max_unique_results_per_run"] = run_cap
        notes.append(f"max_unique_results_per_run (whole run, {domain_count} tasks): {params_before.get('max_unique_results_per_run')} -> {run_cap}")
    else:
        notes.append("max_unique_results_per_run key not present in default params - left untouched (Pending).")

    body = {
        "is_active": True,
        "to_complete": True,
        "export_unique_results": False,
        "no_line_breaks": False,
        "concurrency": concurrency,
        "params": new_params,
    }
    res = client["updateSquid"](squid_id, body)
    write_json(Path(requests_dir) / "squid-configure.json", {"requested_at": now_iso(), "request_body": body, "notes": notes, "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"updateSquid failed: HTTP {res['status']}")

    details_after = client["getSquidDetails"](squid_id)
    write_json(Path(requests_dir) / "squid-details-after-configure.json", {"checked_at": now_iso(), "response": details_after["json"]})
    params_after = jg(details_after["json"], "params") or {}
    concurrency_after = jg(details_after["json"], "concurrency")
    if concurrency_after != concurrency:
        raise Exception(f"Refusing to proceed: requested concurrency={concurrency} but squid reports concurrency={concurrency_after} after configure.")
    return {"params_before": params_before, "params_after": params_after, "concurrency_before": concurrency_before, "concurrency_after": concurrency_after, "notes": notes}


def add_tasks(client, squid_id, domains, requests_dir):
    tasks_payload = [{"url": task_url_for_domain(d["domain"])} for d in domains]
    res = client["addTasks"](squid_id, tasks_payload)
    write_json(Path(requests_dir) / "tasks.json", {"requested_at": now_iso(), "request": tasks_payload, "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"addTasks failed: HTTP {res['status']}")
    task_map = {}
    for d in domains:
        url = task_url_for_domain(d["domain"])
        match = next((t for t in (jg(res["json"], "tasks") or []) if jg(t.get("params"), "url") == url), None)
        if match:
            task_map[d["domain"]] = match["id"]
    print(f"[tasks] created {len(task_map)}/{len(domains)} domain tasks in ONE squid (duplicated_count={jg(res['json'], 'duplicated_count')}).")
    return task_map


def start_run(client, squid_id, requests_dir):
    res = client["startRun"](squid_id)
    if not res["ok"] or not jg(res["json"], "id"):
        raise Exception(f"startRun failed: HTTP {res['status']}")
    write_json(Path(requests_dir) / "run-start.json", {"requested_at": now_iso(), "response": res["json"]})
    print(f"[run] started ONE paid run covering all 5 tasks: {res['json']['id']}")
    return res["json"]["id"]


def poll_run_to_terminal(client, run_id, latencies, out_dir, errors_dir):
    stop_statuses = {"DONE", "ERROR", "ABORTED", "PAUSED"}
    poll_history = []
    poll_start = time.monotonic()
    last_run = None
    while (time.monotonic() - poll_start) * 1000 < MAX_POLL_WAIT_MS:
        res = client["getRun"](run_id)
        latencies.append({"phase": "poll_run", "ms": res["latencyMs"], "attempts": res["attempts"]})
        if not res["ok"]:
            append_error_event(errors_dir, {"type": "get_run_error", "runId": run_id, "response": res["json"]})
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
    write_json(Path(out_dir) / "run-state.json", {"run_id": run_id, "poll_history": poll_history, "final": last_run})
    return last_run


def fetch_all_results(client, run_id, latencies, results_dir, errors_dir):
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
            res = client["getResults"](run=run_id, page=current_page, page_size=RESULTS_PAGE_SIZE)
        latencies.append({"phase": "get_results", "page": current_page, "ms": res["latencyMs"], "attempts": res["attempts"]})
        write_json(Path(results_dir) / f"results-page{current_page}.json", {"page": current_page, "fetched_at": now_iso(), "response": res["json"]})
        if not res["ok"]:
            append_error_event(errors_dir, {"type": "get_results_error", "page": current_page, "response": res["json"]})
            stop_reason = "results_fetch_error"
            break
        data = jg(res["json"], "data") or []
        page_marker = ",".join("" if d.get("id") is None else str(d.get("id")) for d in data)
        if len(data) > 0 and page_marker in seen_page_markers:
            append_error_event(errors_dir, {"type": "repeated_results_page", "page": current_page})
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
_COMPANY_PAGE_URL_RE = re.compile(r"trustpilot\.com/review/([^/?#]+)", re.I)


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


def normalize_domain_for_match(d):
    return re.sub(r"^www\.", "", (d or "").strip().lower())


def extract_domain_from_company_page_url(company_page_url):
    if not company_page_url:
        return None
    match = _COMPANY_PAGE_URL_RE.search(company_page_url)
    return match.group(1) if match else None


def attribute_domain(item, task_id_to_domain, domain_by_normalized):
    task = item.get("task")
    if task and task_id_to_domain.get(task):
        return task_id_to_domain[task]
    extracted = extract_domain_from_company_page_url(item.get("company_page_url"))
    if extracted:
        canonical = domain_by_normalized.get(normalize_domain_for_match(extracted))
        if canonical:
            return canonical
    return None


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

    if len(sys.argv) < 2:
        print("Usage: python scripts/lobstr/concurrency_test.py <concurrency> [target_per_domain]", file=sys.stderr)
        sys.exit(1)
    concurrency = int(sys.argv[1])
    target_per_domain = int(sys.argv[2]) if len(sys.argv) > 2 else 200

    out_dir = BASE_OUT_DIR / f"c{concurrency}"
    requests_dir = out_dir / "raw" / "requests"
    results_dir = out_dir / "raw" / "results"
    errors_dir = out_dir / "errors"
    ensure_dirs(out_dir, requests_dir, results_dir, errors_dir)

    api_key = load_api_key()
    domains = load_domains()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.monotonic()

    client = create_client({"apiKey": api_key}, lambda event: append_error_event(errors_dir, {"label": f"concurrency_test_c{concurrency}", **event}))

    balance_before = None
    try:
        bal_res = client["getBalance"]()
        write_json(out_dir / "credits-before.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_before = bal_res["json"]
    except Exception as err:
        append_error_event(errors_dir, {"type": "balance_before_failed", "message": str(err)})

    crawler_id = discover_crawler_id(client, requests_dir)
    squid_id = create_dedicated_squid(client, crawler_id, concurrency, requests_dir)
    configure_result = configure_squid(client, squid_id, concurrency, target_per_domain, len(domains), requests_dir)
    domain_task_map = add_tasks(client, squid_id, domains, requests_dir)
    task_id_to_domain = {task_id: domain for domain, task_id in domain_task_map.items()}
    domain_by_normalized = {normalize_domain_for_match(d["domain"]): d["domain"] for d in domains}

    run_id = None
    final_run = None
    try:
        run_id = start_run(client, squid_id, requests_dir)
        final_run = poll_run_to_terminal(client, run_id, latencies, out_dir, errors_dir)
    except AuthOrBillingError as err:
        write_json(errors_dir / "BLOCKER-auth-or-billing.json", {"message": err.message, "status": err.status, "body": err.body})
        print(f"BLOCKER: authentication/billing failure: {err.message}", file=sys.stderr)
        sys.exit(2)
    except InvalidRequestError as err:
        write_json(errors_dir / "BLOCKER-invalid-request.json", {"message": err.message, "status": err.status, "body": err.body})
        print(f"BLOCKER: invalid request starting run: {err.message}", file=sys.stderr)
        sys.exit(2)

    status_upper = (jg(final_run, "status") or "").upper()
    run_succeeded = status_upper == "DONE"

    results = fetch_all_results(client, run_id, latencies, results_dir, errors_dir)
    all_items = results["allItems"]
    results_stop_reason = results["stopReason"]

    balance_after = None
    try:
        bal_res = client["getBalance"]()
        write_json(out_dir / "credits-after.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_after = bal_res["json"]
    except Exception as err:
        append_error_event(errors_dir, {"type": "balance_after_failed", "message": str(err)})

    all_entries = []
    domain_raw = {}
    domain_valid = {}
    unattributed = 0
    for item in all_items:
        domain = attribute_domain(item, task_id_to_domain, domain_by_normalized)
        if not domain:
            unattributed += 1
            continue
        domain_raw[domain] = domain_raw.get(domain, 0) + 1
        if is_valid_review(item):
            domain_valid[domain] = domain_valid.get(domain, 0) + 1
            all_entries.append({"domain": domain, "review": normalize_review_for_dedupe(item), "raw": item})

    dedupe_result = dedupe(all_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]
    unique_by_domain = {}
    for e in unique:
        unique_by_domain[e["domain"]] = unique_by_domain.get(e["domain"], 0) + 1

    domain_reports = []
    for d in domains:
        domain = d["domain"]
        unique_count = unique_by_domain.get(domain, 0)
        domain_reports.append({
            "domain": domain,
            "business_name": d.get("business_name"),
            "task_id": domain_task_map.get(domain),
            "raw_items": domain_raw.get(domain, 0),
            "valid_items": domain_valid.get(domain, 0),
            "unique_valid_reviews": unique_count,
            "shortfall": max(0, target_per_domain - unique_count),
        })

    flat_reviews = [
        {
            "domain": e["domain"],
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
    write_json(out_dir / "all-reviews.json", flat_reviews)
    (out_dir / "all-reviews.csv").write_text(
        to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "review_url", "trustpilot_review_id", "rating_value", "date_published", "review_headline", "review_body", "author_name", "author_id"]),
        encoding="utf-8",
        newline="",
    )
    write_json(out_dir / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
    write_json(out_dir / "pagination-report.json", {"pages": results["pages"], "stop_reason": results_stop_reason, "unattributed_results": unattributed})

    benchmark_end_ms = time.monotonic()
    wall_clock_ms = int((benchmark_end_ms - benchmark_start_ms) * 1000)

    get_results_latencies = [l["ms"] for l in latencies if l.get("phase") == "get_results" and isinstance(l.get("ms"), (int, float))]
    all_latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
    median = all_latency_values[len(all_latency_values) // 2] if all_latency_values else None
    p95 = all_latency_values[min(len(all_latency_values) - 1, int(len(all_latency_values) * 0.95))] if all_latency_values else None
    write_json(out_dir / "timings.json", {
        "benchmark_start": benchmark_start,
        "benchmark_end": now_iso(),
        "wall_clock_ms": wall_clock_ms,
        "per_request": latencies,
        "min_latency_ms": min(all_latency_values) if all_latency_values else None,
        "max_latency_ms": max(all_latency_values) if all_latency_values else None,
        "median_latency_ms": median,
        "p95_latency_ms": p95,
        "get_results_min_latency_ms": min(get_results_latencies) if get_results_latencies else None,
        "get_results_max_latency_ms": max(get_results_latencies) if get_results_latencies else None,
    })

    credits_consumed = None
    if (
        balance_before is not None
        and balance_after is not None
        and isinstance(balance_before.get("consumed"), (int, float))
        and isinstance(balance_after.get("consumed"), (int, float))
    ):
        credits_consumed = balance_after["consumed"] - balance_before["consumed"]

    total_unique = len(unique)
    total_target = target_per_domain * len(domains)
    reviews_per_minute = (total_unique / (wall_clock_ms / 60000.0)) if wall_clock_ms else None

    summary = {
        "generated_at": now_iso(),
        "concurrency_requested": concurrency,
        "concurrency_confirmed_before": configure_result["concurrency_before"],
        "concurrency_confirmed_after": configure_result["concurrency_after"],
        "squid_id": squid_id,
        "task_ids": domain_task_map,
        "run_id": run_id,
        "target_per_domain": target_per_domain,
        "total_target_reviews": total_target,
        "max_results_confirmed_after_configure": configure_result["params_after"].get("max_results"),
        "max_unique_results_per_run_confirmed_after_configure": configure_result["params_after"].get("max_unique_results_per_run"),
        "run_status": jg(final_run, "status"),
        "run_succeeded": run_succeeded,
        "run_reported_total_results": jg(final_run, "total_results"),
        "run_reported_total_unique_results": jg(final_run, "total_unique_results"),
        "run_reported_credit_used": jg(final_run, "credit_used"),
        "total_raw_items_fetched": len(all_items),
        "unattributed_records": unattributed,
        "total_unique_valid_reviews": total_unique,
        "total_duplicates": len(duplicates),
        "domains": domain_reports,
        "all_domains_hit_target": all(r["shortfall"] == 0 for r in domain_reports),
        "wall_clock_ms": wall_clock_ms,
        "reviews_per_minute": round(reviews_per_minute, 1) if reviews_per_minute is not None else None,
        "credits_consumed_measured": credits_consumed,
        "pagination_stop_reason": results_stop_reason,
    }
    write_json(out_dir / "summary.json", summary)
    print(f"--- CONCURRENCY TEST (c={concurrency}) COMPLETE ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
