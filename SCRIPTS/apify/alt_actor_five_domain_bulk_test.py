"""Standalone, isolated live test: run the memo23 Apify Actor
(memo23/trustpilot-scraper-ppe -- NOT the automation-lab/trustpilot Actor
scored in this benchmark) across all 5 benchmark businesses, targeting
1,000 reviews per business (5,000 total) -- the Apify-side equivalent of
scripts/lobstr/five_domain_multi_task_test.py.

This exists to answer the same positioning question as that lobstr.io test,
but for memo23: can this Actor deliver high per-business volume across all
5 benchmark domains, not just the one domain probed by
alt_actor_single_domain_test.py (which returned only 50/1000 requested for
www.thepearlsource.com on 2026-09-03)?

Design notes:
- memo23's input takes ONE `startUrls` entry per run (confirmed shape from
  alt_actor_single_domain_test.py); it does NOT take a `companyUrls` array
  like automation-lab/trustpilot does. So this script issues 5 SEPARATE
  Actor runs (one per domain), sequentially, rather than guessing whether a
  single run with 5 startUrls would even attribute output back to the
  correct domain.
- This is intentionally a SEPARATE script from alt_actor_single_domain_test.py:
  - Writes to its own isolated output directory
    (outputs/apify-alt-actor-five-domain-bulk-test/), never touches
    outputs/apify/, outputs/apify-single-domain-test/, or
    outputs/apify-alt-actor-single-domain-test/.
  - Never writes to .env. Reuses APIFY_API_TOKEN read-only; the target
    Actor id is hardcoded (memo23/trustpilot-scraper-ppe), same as the
    single-domain script.
  - Reads the 5 businesses from benchmark-domains.json, read-only.
- Each of the 5 runs is idempotent per-domain (a saved run.json for that
  domain is reused, not restarted) -- same safeguard pattern as every other
  paid script in this project.
- Does NOT assume this Actor's output field names match automation-lab's
  schema -- dedup here is best-effort/generic, same as the single-domain
  script, since the real item shape is still only confirmed from the one
  prior sample.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/apify/alt_actor_five_domain_bulk_test.py [target_per_domain]

  target_per_domain  defaults to 1000 (maxItems per domain's run)

This is a REAL paid run against the live Apify API -- 5 separate Actor runs,
one per benchmark domain. Requires CONFIRM_PAID_RUN=yes to proceed, same
safeguard as every other paid script in this project.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.apify_client import ApifyClient, AuthOrBillingError, InvalidRequestError

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "outputs" / "apify-alt-actor-five-domain-bulk-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RUNS_DIR = OUT_DIR / "raw" / "runs"
DATASETS_DIR = OUT_DIR / "raw" / "datasets"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"
DOMAINS_PATH = ROOT / "benchmark-domains.json"

ALT_REST_ACTOR_ID = "memo23~trustpilot-scraper-ppe"

POLL_INTERVAL_MS = 10_000
MAX_POLL_WAIT_MS = 60 * 60_000
SETTLE_WAIT_MS = 5_000
DATASET_PAGE_LIMIT = 1000
MAX_DATASET_PAGES = 20

TERMINAL_SUCCESS = {"SUCCEEDED"}
TERMINAL_FAILURE = {"FAILED", "ABORTED", "TIMED-OUT"}


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def now_ms():
    return int(time.time() * 1000)


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def dump_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(dump_json(obj))


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


def load_domains():
    if not DOMAINS_PATH.exists():
        raise RuntimeError("benchmark-domains.json not found.")
    parsed = json.loads(DOMAINS_PATH.read_text(encoding="utf-8"))
    if not isinstance(parsed, list) or len(parsed) != 5:
        found = len(parsed) if isinstance(parsed, list) else type(parsed).__name__
        raise RuntimeError(f"benchmark-domains.json must contain exactly 5 entries, found {found}.")
    return parsed


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


def ensure_single_run(client, rest_actor_id, input_body, safe):
    run_file = RUNS_DIR / f"{safe}-run.json"
    if run_file.exists():
        saved = json.loads(run_file.read_text(encoding="utf-8"))
        print(f"[run] {safe}: reusing existing saved run id: {saved['run_id']} (idempotent - no new Actor run created).")
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
        raise RuntimeError(f"startActorRun failed for {safe}: HTTP {result.get('status')} body={json_body}")

    run_id = data_id
    write_json(run_file, {"run_id": run_id, "started_at": now_iso(), "raw": data})
    print(f"[run] {safe}: started ONE paid Actor run on {rest_actor_id}: {run_id}")
    return run_id


def poll_run_to_terminal(client, run_id, safe):
    poll_history = []
    poll_start = now_ms()
    last_run = None

    while now_ms() - poll_start < MAX_POLL_WAIT_MS:
        res = client.get_run(run_id)
        if not res.get("ok"):
            append_error_event({"type": "get_run_error", "domain": safe, "runId": run_id, "response": res.get("json")})
            poll_history.append({"polled_at": now_iso(), "error": f"HTTP {res.get('status')}"})
            sleep_ms(POLL_INTERVAL_MS)
            continue
        last_run = res["json"]["data"]
        poll_history.append(
            {"polled_at": now_iso(), "status": last_run.get("status"), "defaultDatasetId": last_run.get("defaultDatasetId")}
        )
        print(f"[poll] {safe}: run {run_id}: status={last_run.get('status')}")
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


def fetch_all_dataset_items(client, dataset_id, safe):
    offset = 0
    page_num = 1
    all_items = []
    pages = []
    stop_reason = None

    while page_num <= MAX_DATASET_PAGES:
        res = client.get_dataset_items(dataset_id, offset=offset, limit=DATASET_PAGE_LIMIT)
        if not res.get("ok"):
            append_error_event({"type": "dataset_fetch_failed", "domain": safe, "page": page_num, "offset": offset, "status": res.get("status"), "body": res.get("json")})
            stop_reason = "fetch_failed"
            break
        items = res.get("json") if isinstance(res.get("json"), list) else []
        pagination_total = res.get("pagination_total")
        write_json(
            DATASETS_DIR / f"{safe}-page{page_num}-offset{offset}.json",
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
        pages.append({"page": page_num, "offset": offset, "raw_count": len(items), "pagination_total": pagination_total})

        if len(items) == 0:
            stop_reason = "empty_page"
            break
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


def best_effort_unique_count(items):
    """We don't know this Actor's field names for certain, so dedupe
    generically: try common id-like keys first; fall back to a hash of the
    whole item. Matches alt_actor_single_domain_test.py's approach."""
    id_keys = ["reviewId", "review_id", "id", "url", "reviewUrl", "review_url"]
    seen = set()
    for item in items:
        key = None
        if isinstance(item, dict):
            for k in id_keys:
                if item.get(k):
                    key = f"{k}:{item[k]}"
                    break
            if key is None:
                key = json.dumps(item, sort_keys=True)
        else:
            key = json.dumps(item, sort_keys=True)
        seen.add(key)
    return len(seen)


def run_one_domain(client, domain, target_per_domain):
    safe = safe_domain_name(domain)
    input_body = {
        "startUrls": [f"https://www.trustpilot.com/review/{domain}"],
        "maxItems": target_per_domain,
        "filterDateRange": "all",
    }

    try:
        run_id = ensure_single_run(client, ALT_REST_ACTOR_ID, input_body, safe)
        terminal_run = poll_run_to_terminal(client, run_id, safe)

        if not terminal_run or terminal_run.get("status") in TERMINAL_FAILURE:
            status_val = terminal_run.get("status") if terminal_run else None
            final_status = status_val if status_val is not None else "unknown/timeout"
            write_json(ERRORS_DIR / f"BLOCKER-{safe}-run-not-succeeded.json", {"run_id": run_id, "final_status": final_status})
            print(f"BLOCKER: {safe} Actor run did not succeed (status: {final_status}).", file=sys.stderr)
            return {
                "domain": domain, "run_id": run_id, "run_status": final_status, "run_succeeded": False,
                "total_raw_items_fetched": 0, "best_effort_unique_count": 0, "measured_total_cost_usd": None,
                "pagination_stop_reason": "run_not_succeeded",
            }

        final_run = fetch_final_run_object(client, run_id, safe)
        dataset_id = (final_run.get("defaultDatasetId") if final_run else None) or terminal_run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError(f"No defaultDatasetId found on the completed run for {safe}.")

        all_items, pages, stop_reason = fetch_all_dataset_items(client, dataset_id, safe)
        unique_count = best_effort_unique_count(all_items)
        usage_total_usd = final_run.get("usageTotalUsd") if final_run else None

        if all_items:
            write_json(OUT_DIR / f"{safe}-sample-item.json", all_items[0])

        return {
            "domain": domain,
            "run_id": run_id,
            "dataset_id": dataset_id,
            "run_status": terminal_run.get("status"),
            "run_succeeded": terminal_run.get("status") in TERMINAL_SUCCESS,
            "total_raw_items_fetched": len(all_items),
            "best_effort_unique_count": unique_count,
            "shortfall": max(0, target_per_domain - unique_count),
            "pagination_stop_reason": stop_reason,
            "measured_total_cost_usd": usage_total_usd,
        }
    except (AuthOrBillingError, InvalidRequestError) as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        kind = "auth-or-billing" if isinstance(err, AuthOrBillingError) else "invalid-request"
        write_json(ERRORS_DIR / f"BLOCKER-{safe}-{kind}.json", {"message": str(err), "status": err.status, "body": err.body})
        print(f"BLOCKER: {safe} {kind} failure: {err}", file=sys.stderr)
        return {
            "domain": domain, "run_id": None, "run_status": f"blocked:{kind}", "run_succeeded": False,
            "total_raw_items_fetched": 0, "best_effort_unique_count": 0, "measured_total_cost_usd": None,
            "pagination_stop_reason": kind,
        }


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating 5 real paid Apify Actor runs.", file=sys.stderr)
        sys.exit(1)

    target_per_domain = int(sys.argv[1]) if len(sys.argv) > 1 else 1000

    ensure_dirs([OUT_DIR, REQUESTS_DIR, RUNS_DIR, DATASETS_DIR, ERRORS_DIR])
    api_token = load_api_token()
    domains = load_domains()

    client = ApifyClient(api_token, on_event=lambda event: append_error_event({"label": "alt_actor_five_domain_bulk_test", **event}))

    bench_start = now_iso()
    domain_reports = []
    for d in domains:
        print(f"=== {d['domain']} (target {target_per_domain}) ===")
        domain_reports.append(run_one_domain(client, d["domain"], target_per_domain))

    total_target = target_per_domain * len(domains)
    total_unique = sum(r["best_effort_unique_count"] for r in domain_reports)
    total_cost = sum(r["measured_total_cost_usd"] for r in domain_reports if isinstance(r.get("measured_total_cost_usd"), (int, float)))

    summary = {
        "generated_at": bench_start,
        "actor_id": ALT_REST_ACTOR_ID,
        "target_per_domain": target_per_domain,
        "total_target_reviews": total_target,
        "domains": domain_reports,
        "total_unique_valid_reviews_best_effort": total_unique,
        "all_domains_hit_target": all(r.get("shortfall", target_per_domain) == 0 for r in domain_reports),
        "total_measured_cost_usd": round(total_cost, 4) if total_cost else total_cost,
        "note": "Reconnaissance test only. Field-name schema for this Actor is unconfirmed -- see raw dataset pages for the actual item shape before trusting any per-field claim. best_effort_unique_count uses generic id-key dedupe, not a confirmed schema mapping.",
    }
    write_json(OUT_DIR / "summary.json", summary)

    print("--- ALT-ACTOR FIVE-DOMAIN BULK TEST COMPLETE ---")
    print(dump_json(summary))


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
