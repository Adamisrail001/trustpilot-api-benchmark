"""Standalone, isolated live test: does a DIFFERENT Apify Actor
(memo23/trustpilot-scraper-ppe -- NOT the automation-lab/trustpilot Actor
scored in this benchmark) actually return more than 200 reviews from ONE
business, as its own store-page marketing copy claims ("bypasses Trustpilot's
~200-review web cap")?

This is exploratory reconnaissance, not part of the scored benchmark:
- Writes to its own isolated output directory
  (outputs/apify-alt-actor-single-domain-test/), never touches outputs/apify/
  or outputs/apify-single-domain-test/.
- Never writes to .env. Reuses APIFY_API_TOKEN read-only; the target Actor
  id is hardcoded here (memo23/trustpilot-scraper-ppe), not read from
  APIFY_ACTOR_ID (which stays pointed at automation-lab/trustpilot).
- Does NOT assume this Actor's output field names match automation-lab's
  schema (reviewId/authorName/etc.) -- unknown until we see real output.
  Dedup here is best-effort/generic; a full field-mapping only makes sense
  once we've confirmed this Actor is worth scoring at all.

Usage:
  CONFIRM_PAID_RUN=yes python scripts/apify/alt_actor_single_domain_test.py [domain] [maxItems]

  domain    defaults to www.thepearlsource.com (same business used throughout
            this benchmark, for a clean apples-to-apples comparison)
  maxItems  defaults to 1000

This is a REAL paid run against the live Apify API. Requires
CONFIRM_PAID_RUN=yes to proceed, same safeguard as every other paid script
in this project.
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
OUT_DIR = ROOT / "outputs" / "apify-alt-actor-single-domain-test"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RUNS_DIR = OUT_DIR / "raw" / "runs"
DATASETS_DIR = OUT_DIR / "raw" / "datasets"
ERRORS_DIR = OUT_DIR / "errors"
ENV_PATH = ROOT / ".env"

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
        raise RuntimeError(f"startActorRun failed: HTTP {result.get('status')} body={json_body}")

    run_id = data_id
    write_json(run_file, {"run_id": run_id, "started_at": now_iso(), "raw": data})
    print(f"[run] started ONE paid Actor run on {rest_actor_id}: {run_id}")
    return run_id


def poll_run_to_terminal(client, run_id, safe):
    poll_history = []
    poll_start = now_ms()
    last_run = None

    while now_ms() - poll_start < MAX_POLL_WAIT_MS:
        res = client.get_run(run_id)
        if not res.get("ok"):
            append_error_event({"type": "get_run_error", "runId": run_id, "response": res.get("json")})
            poll_history.append({"polled_at": now_iso(), "error": f"HTTP {res.get('status')}"})
            sleep_ms(POLL_INTERVAL_MS)
            continue
        last_run = res["json"]["data"]
        poll_history.append(
            {"polled_at": now_iso(), "status": last_run.get("status"), "defaultDatasetId": last_run.get("defaultDatasetId")}
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


def fetch_all_dataset_items(client, dataset_id, safe):
    offset = 0
    page_num = 1
    all_items = []
    pages = []
    stop_reason = None

    while page_num <= MAX_DATASET_PAGES:
        res = client.get_dataset_items(dataset_id, offset=offset, limit=DATASET_PAGE_LIMIT)
        if not res.get("ok"):
            append_error_event({"type": "dataset_fetch_failed", "page": page_num, "offset": offset, "status": res.get("status"), "body": res.get("json")})
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
    """We don't know this Actor's field names yet, so dedupe generically:
    try common id-like keys first; fall back to a hash of the whole item."""
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


def main():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating a real paid Apify Actor run.", file=sys.stderr)
        sys.exit(1)

    domain = sys.argv[1] if len(sys.argv) > 1 else "www.thepearlsource.com"
    max_items = int(sys.argv[2]) if len(sys.argv) > 2 else 1000
    filter_date_range = sys.argv[3] if len(sys.argv) > 3 else "all"
    safe = safe_domain_name(domain) + f"-{filter_date_range}"

    ensure_dirs([OUT_DIR, REQUESTS_DIR, RUNS_DIR, DATASETS_DIR, ERRORS_DIR])
    api_token = load_api_token()

    client = ApifyClient(api_token, on_event=lambda event: append_error_event({"label": "alt_actor_single_domain_test", **event}))

    input_body = {
        "startUrls": [f"https://www.trustpilot.com/review/{domain}"],
        "maxItems": max_items,
        "filterDateRange": filter_date_range,
    }

    try:
        run_id = ensure_single_run(client, ALT_REST_ACTOR_ID, input_body, safe)
        terminal_run = poll_run_to_terminal(client, run_id, safe)

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

        all_items, pages, stop_reason = fetch_all_dataset_items(client, dataset_id, safe)
        unique_count = best_effort_unique_count(all_items)

        usage_total_usd = final_run.get("usageTotalUsd") if final_run else None

        summary = {
            "generated_at": now_iso(),
            "actor_id": ALT_REST_ACTOR_ID,
            "domain": domain,
            "run_id": run_id,
            "dataset_id": dataset_id,
            "max_items_requested": max_items,
            "run_status": terminal_run.get("status"),
            "run_succeeded": terminal_run.get("status") in TERMINAL_SUCCESS,
            "total_raw_items_fetched": len(all_items),
            "best_effort_unique_count": unique_count,
            "exceeded_200_reviews_from_one_business": unique_count > 200,
            "pagination_stop_reason": stop_reason,
            "measured_total_cost_usd": usage_total_usd,
            "note": "Reconnaissance test only. Field-name schema for this Actor is unconfirmed -- see raw dataset pages for the actual item shape before trusting any per-field claim.",
        }
        write_json(OUT_DIR / f"{safe}-summary.json", summary)
        write_json(OUT_DIR / "summary.json", summary)  # last-run convenience copy
        if all_items:
            write_json(OUT_DIR / f"{safe}-sample-item.json", all_items[0])

        print("--- ALT-ACTOR SINGLE-DOMAIN TEST COMPLETE ---")
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
