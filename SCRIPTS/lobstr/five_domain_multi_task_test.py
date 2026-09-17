"""Standalone, isolated live test: put all 5 benchmark businesses into ONE
squid as 5 tasks, raise max_results/max_unique_results_per_run well past the
200 value used in the published 5-domain benchmark, and start a SINGLE run
that collects newest reviews for all 5 at once.

This exists to answer a specific positioning question: instead of citing two
separate numbers (1,000/1,000 standard run + 2,000/2,000 single-domain
scalability test), can lobstr.io pull a bigger, single-run total (up to
5 x target_per_domain, e.g. 5,000) across multiple businesses in one squid?

This is intentionally a SEPARATE script from benchmark.py and
single_domain_test.py:
- It creates its own brand-new, dedicated squid (never reuses
  LOBSTR_SQUID_ID from .env), so it cannot touch or contaminate the squid/
  results behind the published benchmark article or the single-domain test.
- It writes to its own output directory
  (outputs/lobstr-five-domain-multi-task-test/), never into outputs/lobstr/
  or outputs/lobstr-single-domain-test/.
- It never writes to .env.

It reuses the same credentials (LOBSTR_API_KEY) and the same confirmed
Trustpilot crawler (LOBSTR_CRAWLER_ID) as the main benchmark, read-only, and
reads the 5 businesses from benchmark-domains.json, read-only.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/lobstr/five_domain_multi_task_test.py [target_per_domain]

  target_per_domain  defaults to 1000 (max_results / max_unique_results_per_run
                      PER TASK; max_unique_results_per_run on the squid is set
                      to target_per_domain * 5 so the run-level cap doesn't
                      choke off later tasks once earlier ones are full)

This is a REAL paid run against the live lobstr.io API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as the other two scripts.
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
OUT_DIR = ROOT / "outputs" / "lobstr-five-domain-multi-task-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"
DOMAINS_PATH = ROOT / "benchmark-domains.json"

RESULTS_PAGE_SIZE = 1000  # real page-size param is `page_size`, not `limit` - see data/lobstr/analysis/page_size-parameter-correction.md
MAX_RESULT_PAGES = 200  # safety cap, generous for a 5,000+ target at 1000/page
POLL_INTERVAL_MS = 8_000
MAX_POLL_WAIT_MS = 90 * 60_000  # generous - 5x the per-business volume of the single-domain test


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
    name = f"Trustpilot Multi-Task 5x1000 Test - {now_iso()}"
    created = client["createSquid"](crawler=crawler_id, name=name)
    write_json(REQUESTS_DIR / "squid-create.json", {"requested_at": now_iso(), "request": {"crawler": crawler_id, "name": name}, "response": created["json"]})
    if not created["ok"] or not jg(created["json"], "id"):
        raise Exception(f"createSquid failed: HTTP {created['status']}")
    print(f"[squid] created NEW dedicated squid (isolated from the main benchmark and the single-domain test): \"{name}\" ({created['json']['id']})")
    return created["json"]["id"]


def configure_squid(client, squid_id, target_per_domain, domain_count):
    details = client["getSquidDetails"](squid_id)
    write_json(REQUESTS_DIR / "squid-details-before-configure.json", {"checked_at": now_iso(), "response": details["json"]})
    params_before = jg(details["json"], "params") or {}

    new_params = dict(params_before)
    notes = []
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


def add_tasks(client, squid_id, domains):
    tasks_payload = [{"url": task_url_for_domain(d["domain"])} for d in domains]
    res = client["addTasks"](squid_id, tasks_payload)
    write_json(REQUESTS_DIR / "tasks.json", {"requested_at": now_iso(), "request": tasks_payload, "response": res["json"]})
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


def start_run(client, squid_id):
    res = client["startRun"](squid_id)
    if not res["ok"] or not jg(res["json"], "id"):
        raise Exception(f"startRun failed: HTTP {res['status']}")
    write_json(REQUESTS_DIR / "run-start.json", {"requested_at": now_iso(), "response": res["json"]})
    print(f"[run] started ONE paid run covering all 5 tasks: {res['json']['id']}")
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
            res = client["getResults"](run=run_id, page=current_page, page_size=RESULTS_PAGE_SIZE)
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


# Confirmed live shape (see benchmark.py): result items carry no `task` field
# at all in this Actor's output. Domain attribution must use
# `company_page_url` - required here since ALL 5 domains share one run.
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

    target_per_domain = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    ensure_dirs()
    api_key = load_api_key()
    domains = load_domains()
    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.monotonic()

    client = create_client({"apiKey": api_key}, lambda event: append_error_event({"label": "five_domain_multi_task_test", **event}))

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
    configure_result = configure_squid(client, squid_id, target_per_domain, len(domains))
    domain_task_map = add_tasks(client, squid_id, domains)
    task_id_to_domain = {task_id: domain for domain, task_id in domain_task_map.items()}
    domain_by_normalized = {normalize_domain_for_match(d["domain"]): d["domain"] for d in domains}

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
    write_json(OUT_DIR / "all-reviews.json", flat_reviews)
    (OUT_DIR / "all-reviews.csv").write_text(
        to_csv(flat_reviews, ["domain", "dedupe_key", "dedupe_key_type", "review_url", "trustpilot_review_id", "rating_value", "date_published", "review_headline", "review_body", "author_name", "author_id"]),
        encoding="utf-8",
        newline="",
    )
    write_json(OUT_DIR / "duplicate-report.json", {"total_duplicates": len(duplicates), "entries": duplicates})
    write_json(OUT_DIR / "pagination-report.json", {"pages": results["pages"], "stop_reason": results_stop_reason, "unattributed_results": unattributed})

    benchmark_end_ms = time.monotonic()
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

    summary = {
        "generated_at": now_iso(),
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
        "wall_clock_ms": int((benchmark_end_ms - benchmark_start_ms) * 1000),
        "credits_consumed_measured": credits_consumed,
        "pagination_stop_reason": results_stop_reason,
    }
    write_json(OUT_DIR / "summary.json", summary)
    print("--- FIVE-DOMAIN MULTI-TASK TEST COMPLETE ---")
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
