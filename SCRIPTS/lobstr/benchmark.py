"""Ported 1:1 from scripts/lobstr-benchmark.js.

Lobstr.io Trustpilot Reviews benchmark orchestrator.

Facts relied on here are sourced from docs/lobster/lobstr-documentation.md
and docs/lobster/lobstr-pricing.md (base URL, Token auth, crawler/squid/
task/run/results model, pagination, rate limits, run status values, credit
model) - cross-confirmed against live fetches of docs.lobstr.io during the
original session. Where a crawler-specific detail (exact `params` keys,
exact result field names) isn't 100% certain, this file discovers it live
from the API's own responses rather than assuming.

Usage:
  python scripts/lobstr_benchmark.py plan
  CONFIRM_SMOKE_RUN=yes python scripts/lobstr_benchmark.py smoke
  CONFIRM_PAID_RUN=yes python scripts/lobstr_benchmark.py run
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
OUT_DIR = ROOT / "outputs" / "lobstr"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
SMOKE_DIR = OUT_DIR / "smoke"
ENV_PATH = ROOT / ".env"

TARGET_PER_DOMAIN = 200
TARGET_TOTAL = 1000
RESULTS_PAGE_SIZE = 1000  # real page-size param is `page_size`, not `limit` - see data/lobstr/analysis/page_size-parameter-correction.md; verified working up to 1000/page
MAX_RESULT_PAGES = 150  # safety cap; generous now that page_size=1000 needs ~1 page per 1,000 results instead of 100
POLL_INTERVAL_MS = 8_000
MAX_POLL_WAIT_MS = 40 * 60_000  # generous vs. the advertised ~200 reviews/min


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def jg(obj, key, default=None):
    """Mimics JS optional-chaining `obj?.key ?? default` for dict-shaped obj."""
    if not isinstance(obj, dict):
        return default
    value = obj.get(key)
    return value if value is not None else default


def coalesce(*values):
    """Mimics a `a ?? b ?? c ?? ...` chain (first non-None wins)."""
    for v in values:
        if v is not None:
            return v
    return None


def write_json(path, obj):
    # newline="" disables Python's universal-newline translation on write (which
    # would otherwise turn "\n" into os.linesep, i.e. "\r\n" on Windows) so the
    # bytes written match Node's fs.writeFileSync (which writes the string as-is).
    Path(path).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8", newline="")


# ---------- .env (read-only for credentials, read/fill for resource IDs) ----------


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
            value = trimmed[idx + 1 :].strip()
            return value or None
    return None


# Only ever used for non-secret resource IDs (LOBSTR_CRAWLER_ID / LOBSTR_SQUID_ID).
# Replaces only the matching line's value; every other line (including all
# credentials) is left byte-for-byte untouched. Never logs the .env content.
def set_env_var(name, value):
    lines = read_env_lines()
    found = False
    updated = []
    for line in lines:
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            updated.append(line)
            continue
        idx = trimmed.find("=")
        if idx == -1:
            updated.append(line)
            continue
        if trimmed[:idx].strip() == name:
            found = True
            updated.append(f"{name}={value}")
        else:
            updated.append(line)
    if not found:
        raise Exception(f"Refusing to invent a new .env line for {name} - expected an existing (possibly blank) line.")
    ENV_PATH.write_text("\n".join(updated), encoding="utf-8", newline="")


def load_api_key():
    key = get_env_var("LOBSTR_API_KEY")
    if not key:
        raise Exception("LOBSTR_API_KEY not found or empty in .env.")
    return key


# ---------- domains ----------


def load_domains():
    p = ROOT / "benchmark-domains.json"
    if not p.exists():
        raise Exception("benchmark-domains.json not found.")
    parsed = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(parsed, list) or len(parsed) != 5:
        found = len(parsed) if isinstance(parsed, list) else type(parsed).__name__
        raise Exception(f"benchmark-domains.json must contain exactly 5 entries, found {found}.")
    return parsed


def task_url_for_domain(domain):
    return f"https://www.trustpilot.com/review/{domain}"


# ---------- dirs / error log ----------


def ensure_dirs(dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    line = json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8", newline="") as f:
        f.write(line + "\n")


def materialize_error_log_json():
    jsonl_path = ERRORS_DIR / "event-log.jsonl"
    events = []
    if jsonl_path.exists():
        for l in jsonl_path.read_text(encoding="utf-8").split("\n"):
            if l:
                events.append(json.loads(l))
    write_json(OUT_DIR / "error-log.json", events)
    return events


# ---------- discovery: crawler ----------


def discover_or_load_crawler_id(client):
    existing = get_env_var("LOBSTR_CRAWLER_ID")
    if existing:
        print(f"[crawler] reusing LOBSTR_CRAWLER_ID from .env: {existing}")
        return existing

    page = 1
    found = None
    seen = []
    while page <= 20:
        res = client["listCrawlers"](page, 100)
        write_json(REQUESTS_DIR / f"crawlers-page{page}.json", {"page": page, "fetched_at": now_iso(), "response": res["json"]})
        if not res["ok"]:
            raise Exception(f"listCrawlers failed: HTTP {res['status']}")
        data = jg(res["json"], "data") or []
        for c in data:
            seen.append({"id": c.get("id"), "name": c.get("name"), "slug": c.get("slug")})
        found = next(
            (c for c in data if re.search("trustpilot", c.get("name") or "", re.I) or re.search("trustpilot", c.get("slug") or "", re.I)),
            None,
        )
        if found:
            break
        total_pages = jg(res["json"], "total_pages")
        if not total_pages or page >= total_pages:
            break
        page += 1

    write_json(REQUESTS_DIR / "crawler-discovery-summary.json", {"discovered_at": now_iso(), "matched": found, "crawlers_seen": seen})

    if not found:
        raise Exception('No crawler matching "trustpilot" was found via the live /v1/crawlers listing. Refusing to invent a crawler ID.')
    print(f"[crawler] discovered: \"{found.get('name')}\" ({found.get('id')})")
    set_env_var("LOBSTR_CRAWLER_ID", found["id"])
    return found["id"]


# ---------- discovery/creation: squid ----------


def find_or_create_squid(client, crawler_id):
    existing = get_env_var("LOBSTR_SQUID_ID")
    if existing:
        details = client["getSquidDetails"](existing)
        write_json(REQUESTS_DIR / "squid-reused.json", {"checked_at": now_iso(), "response": details["json"]})
        if not details["ok"]:
            raise Exception(f"Saved LOBSTR_SQUID_ID {existing} could not be fetched: HTTP {details['status']}")
        if details["json"].get("crawler") != crawler_id:
            raise Exception(
                f"Saved LOBSTR_SQUID_ID {existing} is bound to crawler {details['json'].get('crawler')}, "
                f"not the discovered Trustpilot crawler {crawler_id}. Refusing to reuse unsafely."
            )
        print(f"[squid] reusing LOBSTR_SQUID_ID from .env: {existing}")
        return {"squidId": existing, "created": False, "details": details["json"]}

    page = 1
    found_squid = None
    seen = []
    while page <= 20:
        res = client["listSquids"](page=page, limit=100)
        write_json(REQUESTS_DIR / f"squids-page{page}.json", {"page": page, "fetched_at": now_iso(), "response": res["json"]})
        if not res["ok"]:
            raise Exception(f"listSquids failed: HTTP {res['status']}")
        data = jg(res["json"], "data") or []
        for s in data:
            seen.append({"id": s.get("id"), "name": s.get("name"), "crawler": s.get("crawler")})
        found_squid = next(
            (s for s in data if s.get("crawler") == crawler_id and re.search("trustpilot|benchmark", s.get("name") or "", re.I)),
            None,
        )
        if found_squid:
            break
        total_pages = jg(res["json"], "total_pages")
        if not total_pages or page >= total_pages:
            break
        page += 1

    write_json(REQUESTS_DIR / "squid-discovery-summary.json", {"discovered_at": now_iso(), "matched": found_squid, "squids_seen": seen})

    if found_squid:
        print(f"[squid] reusing existing suitable squid: \"{found_squid.get('name')}\" ({found_squid.get('id')})")
        set_env_var("LOBSTR_SQUID_ID", found_squid["id"])
        details = client["getSquidDetails"](found_squid["id"])
        return {"squidId": found_squid["id"], "created": False, "details": details["json"]}

    created = client["createSquid"](crawler=crawler_id, name="Trustpilot API Benchmark - Lobstr")
    write_json(REQUESTS_DIR / "squid-create.json", {"requested_at": now_iso(), "response": created["json"]})
    if not created["ok"] or not jg(created["json"], "id"):
        raise Exception(f"createSquid failed: HTTP {created['status']}")
    print(f"[squid] created new squid: {created['json']['id']}")
    set_env_var("LOBSTR_SQUID_ID", created["json"]["id"])
    return {"squidId": created["json"]["id"], "created": True, "details": created["json"]}


# ---------- squid configuration ----------


def configure_squid(client, squid_id, current_params):
    # NOTE: `name` is intentionally NOT sent here. A prior run PATCHed the
    # squid's name to a fixed string, which collided (HTTP 400 DuplicateSquid)
    # with a different squid on the account already holding that name. This
    # benchmark must never rename any squid - the clean squid is selected and
    # used purely by ID (squidId / LOBSTR_SQUID_ID), never by name. Every
    # field below is kept only because it is functionally required for this
    # benchmark's own measurements, not because it's "the original body":
    #   - is_active: a squid must be active to start a Run
    #   - to_complete: ensures the run finishes instead of staying open for scheduling
    #   - export_unique_results: false so THIS benchmark's own dedupe logic
    #     (not Lobstr's server-side export dedup) is what gets measured
    #   - no_line_breaks: false preserves original review-text line breaks,
    #     which matters for exact ground-truth text comparison
    body = {
        "is_active": True,
        "to_complete": True,
        "export_unique_results": False,
        "no_line_breaks": False,
    }

    notes = []
    # JS: `currentParams ? { ...currentParams } : null` - an empty-but-present
    # object is truthy in JS, so mirror that with an `is not None` check
    # rather than Python's truthiness (which treats {} as falsy).
    new_params = dict(current_params) if current_params is not None else None
    if new_params is not None and "max_results" in new_params:
        new_params["max_results"] = TARGET_PER_DOMAIN
        notes.append(f"max_results confirmed present in squid params - set to {TARGET_PER_DOMAIN}.")
    else:
        notes.append("max_results key not confirmed present in this squid's params - left untouched (Pending), relying on the crawler's own documented 200-review-per-listing ceiling.")
    # This is the field that was missed in the very first (contaminated) run,
    # which capped that run at 20 total results regardless of max_results.
    if new_params is not None and "max_unique_results_per_run" in new_params:
        new_params["max_unique_results_per_run"] = TARGET_TOTAL
        notes.append(f"max_unique_results_per_run confirmed present in squid params - set to {TARGET_TOTAL}.")
    else:
        notes.append("max_unique_results_per_run key not confirmed present in this squid's params - left untouched (Pending).")
    if new_params is not None:
        body["params"] = new_params
    sort_key = next((k for k in current_params.keys() if re.search("sort", k, re.I)), None) if current_params is not None else None
    notes.append(
        f'A sort-like param key ("{sort_key}") exists but its enum values were not independently confirmed - left at default rather than guessing a value (Pending).'
        if sort_key
        else "No sort-like param key found in this squid's params - recency behavior relies on crawler default (Pending confirmation)."
    )

    res = client["updateSquid"](squid_id, body)
    write_json(REQUESTS_DIR / "squid-configure.json", {"requested_at": now_iso(), "request_body": body, "notes": notes, "response": res["json"]})
    if not res["ok"]:
        raise Exception(f"updateSquid failed: HTTP {res['status']}")
    return {"response": res["json"], "notes": notes}


# ---------- forced-fresh squid creation (no reuse search at all) ----------


def create_dedicated_squid(client, crawler_id):
    name = f"Trustpilot Benchmark - Clean - {now_iso()}"
    created = client["createSquid"](crawler=crawler_id, name=name)
    write_json(REQUESTS_DIR / "squid-create-dedicated.json", {"requested_at": now_iso(), "request": {"crawler": crawler_id, "name": name}, "response": created["json"]})
    if not created["ok"] or not jg(created["json"], "id"):
        raise Exception(f"createSquid failed: HTTP {created['status']}")
    print(f"[squid] created NEW dedicated squid (no reuse): \"{name}\" ({created['json']['id']})")
    set_env_var("LOBSTR_SQUID_ID", created["json"]["id"])
    return created["json"]["id"]


# ---------- preflight (setup only - never starts a Run) ----------


def run_preflight():
    api_key = load_api_key()
    domains = load_domains()
    ensure_dirs([OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR])

    client = create_client({"apiKey": api_key}, lambda event: append_error_event({"label": "preflight", **event}))

    report = {"generated_at": now_iso()}

    # 1. Crawler (reuse the already-confirmed crawler id; it is not the contaminated resource).
    crawler_id = discover_or_load_crawler_id(client)
    report["crawler_id"] = crawler_id

    crawler_meta = None
    res = client["listCrawlers"](1, 100)
    write_json(REQUESTS_DIR / "crawlers-preflight.json", {"fetched_at": now_iso(), "response": res["json"]})
    crawler_meta = next((c for c in (jg(res["json"], "data") or []) if c.get("id") == crawler_id), None)
    report["crawler_meta"] = (
        {
            "name": crawler_meta.get("name"),
            "slug": crawler_meta.get("slug"),
            "max_concurrency": crawler_meta.get("max_concurrency"),
            "credits_per_row": crawler_meta.get("credits_per_row"),
            "is_premium": crawler_meta.get("is_premium"),
            "is_available": crawler_meta.get("is_available"),
            "has_issues": crawler_meta.get("has_issues"),
        }
        if crawler_meta
        else None
    )
    report["crawler_level_max_results_per_listing"] = {
        "value": 200,
        "source": 'documented: lobstr.io/store/trustpilot-reviews-scraper ("Up to 200 reviews per listing considering the Trustpilot limit")',
        "confirmed_via_dedicated_endpoint": False,
    }

    # 2. Force a brand-new dedicated squid - never reuse.
    squid_id = create_dedicated_squid(client, crawler_id)
    report["squid_id"] = squid_id

    # Confirm it starts with zero tasks (proves no contamination is even possible).
    tasks_before_res = client["listTasks"](squid=squid_id, page=1, limit=100)
    write_json(REQUESTS_DIR / "tasks-before-preflight.json", {"checked_at": now_iso(), "response": tasks_before_res["json"]})
    tasks_before_count = jg(tasks_before_res["json"], "total_results")
    if tasks_before_count is None:
        tasks_before_count = len(jg(tasks_before_res["json"], "data") or [])
    report["tasks_before_count"] = tasks_before_count
    if tasks_before_count != 0:
        raise Exception(f"New squid {squid_id} unexpectedly already has {tasks_before_count} task(s) - refusing to proceed without investigation.")

    # 3. Inspect default squid params/limits BEFORE any configuration.
    details_before = client["getSquidDetails"](squid_id)
    write_json(REQUESTS_DIR / "squid-details-before-configure.json", {"checked_at": now_iso(), "response": details_before["json"]})
    params_before = jg(details_before["json"], "params") or {}
    report["squid_default_params"] = params_before

    # 4. Configure: raise BOTH max_results (per-task) and max_unique_results_per_run (per-run) -
    #    the second one is exactly what was missed last time and caused the contaminated run
    #    to cap out at 20.
    new_params = dict(params_before)
    config_notes = []
    if "max_results" in new_params:
        new_params["max_results"] = TARGET_PER_DOMAIN
        config_notes.append(f"max_results: {params_before.get('max_results')} -> {TARGET_PER_DOMAIN}")
    else:
        config_notes.append("max_results key not present in default params - left untouched (Pending).")
    if "max_unique_results_per_run" in new_params:
        new_params["max_unique_results_per_run"] = TARGET_TOTAL
        config_notes.append(f"max_unique_results_per_run: {params_before.get('max_unique_results_per_run')} -> {TARGET_TOTAL} (this is the field that was missed in the failed run)")
    else:
        config_notes.append("max_unique_results_per_run key not present in default params - left untouched (Pending).")

    configure_body = {
        "name": "Trustpilot API Benchmark - Lobstr (dedicated)",
        "is_active": True,
        "to_complete": True,
        "export_unique_results": False,
        "no_line_breaks": False,
        "params": new_params,
    }
    configure_res = client["updateSquid"](squid_id, configure_body)
    write_json(REQUESTS_DIR / "squid-configure-preflight.json", {"requested_at": now_iso(), "request_body": configure_body, "notes": config_notes, "response": configure_res["json"]})
    if not configure_res["ok"]:
        raise Exception(f"updateSquid failed: HTTP {configure_res['status']}")

    # Re-fetch to confirm the update actually applied (don't trust the echo alone).
    details_after = client["getSquidDetails"](squid_id)
    write_json(REQUESTS_DIR / "squid-details-after-configure.json", {"checked_at": now_iso(), "response": details_after["json"]})
    params_after = jg(details_after["json"], "params") or {}
    report["squid_params_after_configure"] = params_after
    report["configuration_notes"] = config_notes
    report["max_unique_results_per_run_confirmed"] = params_after.get("max_unique_results_per_run")
    report["max_results_confirmed"] = params_after.get("max_results")

    # 5. Add exactly our 5 tasks.
    domain_task_map = ensure_tasks(client, squid_id, domains, REQUESTS_DIR)
    report["domain_task_map"] = domain_task_map
    report["task_urls"] = [{"domain": d["domain"], "url": task_url_for_domain(d["domain"])} for d in domains]

    # Verify: exactly 5 tasks, all and only our domains.
    tasks_after_res = client["listTasks"](squid=squid_id, page=1, limit=100)
    write_json(REQUESTS_DIR / "tasks-after-preflight.json", {"checked_at": now_iso(), "response": tasks_after_res["json"]})
    tasks_after_data = jg(tasks_after_res["json"], "data") or []
    expected_urls = {task_url_for_domain(d["domain"]) for d in domains}
    unexpected_tasks = [t for t in tasks_after_data if jg(t.get("params"), "url") not in expected_urls]
    report["tasks_after_count"] = coalesce(jg(tasks_after_res["json"], "total_results"), len(tasks_after_data))
    report["unexpected_tasks_found"] = len(unexpected_tasks)
    report["no_unrelated_tasks_confirmed"] = len(tasks_after_data) == len(domains) and len(unexpected_tasks) == 0

    # 6. Balance / plan / credits.
    bal_res = client["getBalance"]()
    write_json(OUT_DIR / "credits-preflight.json", {"checked_at": now_iso(), "response": bal_res["json"]})
    report["account_plan"] = jg(bal_res["json"], "name")
    report["credits_available"] = jg(bal_res["json"], "available")
    report["credits_consumed_so_far_this_cycle"] = jg(bal_res["json"], "consumed")
    report["total_available_slots"] = jg(bal_res["json"], "total_available_slots")
    report["expected_credits_required"] = TARGET_TOTAL

    # 7/8. Feasibility verdict - based only on documented/observed facts, never invented.
    free_plan_row_cap_documented = 30  # lobstr.io/pricing: "exports are capped at 30 rows per request" on the free plan
    is_free_plan = (report.get("account_plan") or "").lower() == "free"
    squid_run_cap_raised_successfully = report["max_unique_results_per_run_confirmed"] == TARGET_TOTAL

    if is_free_plan:
        report["feasibility_verdict"] = "BLOCKED (documented plan cap)"
        report["feasibility_reason"] = (
            f'Account plan is reported as "free" via GET /v1/user/balance. Lobstr.io\'s public pricing page documents the free '
            f"plan as capped at {free_plan_row_cap_documented} rows per export request, well below the 1,000-review target. "
            f"This has not been empirically re-confirmed at the API level this session (no Run has been started), but it is "
            f"the exact publicly documented ceiling for this plan tier."
        )
    elif not squid_run_cap_raised_successfully:
        report["feasibility_verdict"] = "BLOCKED (squid-level cap not confirmed raised)"
        report["feasibility_reason"] = (
            f"max_unique_results_per_run could not be confirmed at {TARGET_TOTAL} after configuration "
            f"(observed: {report['max_unique_results_per_run_confirmed']})."
        )
    else:
        report["feasibility_verdict"] = "NOT BLOCKED BY KNOWN FACTORS"
        report["feasibility_reason"] = (
            'Squid-level max_results and max_unique_results_per_run are both confirmed raised to support the 1,000-review '
            'target, and the account plan is not reported as "free". No other documented cap applies. This does not '
            "guarantee 1,000 results will actually be returned (that depends on live scraping success), only that no "
            "known configuration/plan ceiling would block it."
        )

    write_json(OUT_DIR / "preflight-report.json", report)
    print("--- PREFLIGHT COMPLETE (no Run created) ---")
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


# ---------- tasks ----------


def ensure_tasks(client, squid_id, domains, requests_dir):
    requests_dir = Path(requests_dir)
    task_file = requests_dir / "tasks.json"
    if task_file.exists():
        saved = json.loads(task_file.read_text(encoding="utf-8"))
        print("[tasks] reusing existing saved tasks (idempotent - no resubmission).")
        return saved["domain_task_map"]

    tasks_payload = [{"url": task_url_for_domain(d["domain"])} for d in domains]
    res = client["addTasks"](squid_id, tasks_payload)
    if not res["ok"]:
        raise Exception(f"addTasks failed: HTTP {res['status']}")

    task_map = {}
    for d in domains:
        url = task_url_for_domain(d["domain"])
        match = next((t for t in (jg(res["json"], "tasks") or []) if jg(t.get("params"), "url") == url), None)
        if match:
            task_map[d["domain"]] = match["id"]

    write_json(
        task_file,
        {
            "created_at": now_iso(),
            "duplicated_count": jg(res["json"], "duplicated_count"),
            "domain_task_map": task_map,
            "raw": res["json"],
        },
    )
    print(f"[tasks] created {len(task_map)}/{len(domains)} domain tasks (duplicated_count={jg(res['json'], 'duplicated_count')}).")
    return task_map


# ---------- run (single paid trigger) ----------


def ensure_single_run(client, squid_id, requests_dir):
    requests_dir = Path(requests_dir)
    run_file = requests_dir / "run.json"
    if run_file.exists():
        saved = json.loads(run_file.read_text(encoding="utf-8"))
        print(f"[run] reusing existing saved run id: {saved['run_id']} (idempotent - no new paid Run created).")
        return saved["run_id"]

    start_res = None
    try:
        start_res = client["startRun"](squid_id)
    except InvalidRequestError as err:
        append_error_event({"type": "start_run_400", "message": err.message, "body": err.body})
        list_res = client["listRuns"](squid=squid_id, page=1, limit=10)
        write_json(requests_dir / "run-recovery-list.json", {"checked_at": now_iso(), "response": list_res["json"]})
        active = None
        if list_res["ok"]:
            active = next(
                (r for r in (jg(list_res["json"], "data") or []) if (r.get("status") or "").upper() not in ("DONE", "ERROR", "ABORTED")),
                None,
            )
        if active:
            print(f"[run] recovered existing active run instead of creating a duplicate: {active['id']}")
            write_json(run_file, {"run_id": active["id"], "recovered": True, "raw": active})
            return active["id"]
        raise Exception(f"startRun rejected (HTTP 400) and no active run could be recovered via listRuns: {err.message}")

    if not start_res["ok"] or not jg(start_res["json"], "id"):
        raise Exception(f"startRun failed: HTTP {start_res['status']}")
    write_json(run_file, {"run_id": start_res["json"]["id"], "recovered": False, "requested_at": now_iso(), "raw": start_res["json"]})
    print(f"[run] started ONE paid run: {start_res['json']['id']}")
    return start_res["json"]["id"]


# ---------- polling ----------


def poll_run_to_terminal(client, run_id, latencies, out_dir):
    out_dir = Path(out_dir)
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
        poll_history.append(
            {
                "polled_at": now_iso(),
                "status": last_run.get("status"),
                "is_done": last_run.get("is_done"),
                "total_results": last_run.get("total_results"),
                "total_unique_results": last_run.get("total_unique_results"),
                "credit_used": last_run.get("credit_used"),
            }
        )
        print(
            f"[poll] run {run_id}: status={last_run.get('status')} "
            f"total_results={coalesce(last_run.get('total_results'), '-')} unique={coalesce(last_run.get('total_unique_results'), '-')}"
        )
        if (last_run.get("status") or "").upper() in stop_statuses:
            break
        sleep_ms(POLL_INTERVAL_MS)

    write_json(out_dir / "run-state.json", {"run_id": run_id, "poll_history": poll_history, "final": last_run})
    return last_run


# ---------- results pagination ----------


def fetch_all_results(client, run_id, latencies, results_dir):
    results_dir = Path(results_dir)
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

        write_json(results_dir / f"results-page{current_page}.json", {"page": current_page, "fetched_at": now_iso(), "response": res["json"]})

        if not res["ok"]:
            append_error_event({"type": "get_results_error", "page": current_page, "response": res["json"]})
            stop_reason = "results_fetch_error"
            break

        data = jg(res["json"], "data") or []
        # JS: `data.map((d) => d.id).join(',')` - Array.join renders null/undefined
        # elements as empty strings, so mirror that rather than Python's str(None).
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


# ---------- normalization / validity / dedupe ----------

# Confirmed live shape: `review_url` is actually the bare Trustpilot review
# hex ID (e.g. "6a6083012bbe4c893e5ec3d3"), NOT a full URL. The full URL is
# in `review_link` (e.g. "https://www.trustpilot.com/reviews/<id>"). This
# extractor accepts either shape rather than assuming the "reviews/" prefix
# is always present.
_BARE_ID_RE = re.compile(r"^[a-f0-9]{16,32}$", re.I)
_IN_URL_ID_RE = re.compile(r"reviews/([a-f0-9]{16,32})", re.I)
_COMPANY_PAGE_URL_RE = re.compile(r"trustpilot\.com/review/([^/?#]+)", re.I)


def extract_trustpilot_review_id(review_url_or_link):
    if not review_url_or_link:
        return None
    bare_id_match = _BARE_ID_RE.match(review_url_or_link)
    if bare_id_match:
        return bare_id_match.group(0)
    in_url_match = _IN_URL_ID_RE.search(review_url_or_link)
    return in_url_match.group(1) if in_url_match else None


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


# Confirmed live shape: result items have no `task` field at all. Domain
# attribution must use `company_page_url` (e.g. "https://www.trustpilot.com/
# review/www.thepearlsource.com"), normalized for a harmless www/non-www
# difference, matched against benchmark-domains.json.
def normalize_domain_for_match(d):
    return re.sub(r"^www\.", "", (d or "").strip().lower())


def extract_domain_from_company_page_url(company_page_url):
    if not company_page_url:
        return None
    match = _COMPANY_PAGE_URL_RE.search(company_page_url)
    return match.group(1) if match else None


def is_valid_review(item):
    has_id = bool(item.get("review_url")) or bool(item.get("id"))
    has_rating = item.get("rating_value") is not None or item.get("stars") is not None
    has_date = bool(item.get("date_published"))
    has_text = bool(item.get("review_headline")) or bool(item.get("review_body"))
    has_reviewer = bool(item.get("author_name")) or bool(item.get("author_id"))
    return bool(has_id and has_rating and has_date and has_text and has_reviewer)


def missing_fields_for(item):
    missing = []
    if not item.get("review_url") and not item.get("id"):
        missing.append("review_url_or_id")
    if item.get("rating_value") is None and item.get("stars") is None:
        missing.append("rating")
    if not item.get("date_published"):
        missing.append("date_published")
    if not item.get("review_headline") and not item.get("review_body"):
        missing.append("review_headline_or_body")
    if not item.get("author_name") and not item.get("author_id"):
        missing.append("reviewer_info")
    return missing


def attribute_domain(item, task_id_to_domain, domain_by_normalized):
    # Primary (kept for forward-compatibility, but not observed on live data
    # from this Actor - result items had no `task` field at all).
    task = item.get("task")
    if task and task_id_to_domain.get(task):
        return task_id_to_domain[task]
    # Confirmed live mechanism: attribute via company_page_url.
    extracted = extract_domain_from_company_page_url(item.get("company_page_url"))
    if extracted:
        canonical = domain_by_normalized.get(normalize_domain_for_match(extracted))
        if canonical:
            return canonical
    return None


# ---------- main benchmark run ----------


def run_benchmark(domains, requests_dir, results_dir, out_dir, label):
    requests_dir = Path(requests_dir)
    results_dir = Path(results_dir)
    out_dir = Path(out_dir)

    api_key = load_api_key()
    ensure_dirs([out_dir, requests_dir, results_dir, ERRORS_DIR])

    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.monotonic()

    client = create_client({"apiKey": api_key}, lambda event: append_error_event({"label": label, **event}))

    # Credits before (best-effort evidence, per requirement to record balance when available).
    balance_before = None
    try:
        bal_res = client["getBalance"]()
        write_json(out_dir / "credits-before.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_before = bal_res["json"]
    except Exception as err:
        append_error_event({"type": "balance_before_failed", "message": str(err)})

    crawler_id = discover_or_load_crawler_id(client)
    squid_result = find_or_create_squid(client, crawler_id)
    squid_id = squid_result["squidId"]
    details = squid_result["details"]
    configure_squid(client, squid_id, jg(details, "params"))
    domain_task_map = ensure_tasks(client, squid_id, domains, requests_dir)
    task_id_to_domain = {task_id: domain for domain, task_id in domain_task_map.items()}
    domain_by_normalized = {normalize_domain_for_match(d["domain"]): d["domain"] for d in domains}

    run_id = None
    final_run = None
    try:
        run_id = ensure_single_run(client, squid_id, requests_dir)
        final_run = poll_run_to_terminal(client, run_id, latencies, out_dir)
    except AuthOrBillingError as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(ERRORS_DIR / "BLOCKER-auth-or-billing.json", {"message": err.message, "status": err.status, "body": err.body})
        print(f"BLOCKER: authentication/billing failure: {err.message}", file=sys.stderr)
        sys.exit(2)

    status_upper = (jg(final_run, "status") or "").upper()
    run_succeeded = status_upper == "DONE"

    results = fetch_all_results(client, run_id, latencies, results_dir)
    all_items = results["allItems"]
    pages = results["pages"]
    results_stop_reason = results["stopReason"]

    # Credits after.
    balance_after = None
    try:
        bal_res = client["getBalance"]()
        write_json(out_dir / "credits-after.json", {"checked_at": now_iso(), "response": bal_res["json"]})
        if bal_res["ok"]:
            balance_after = bal_res["json"]
    except Exception as err:
        append_error_event({"type": "balance_after_failed", "message": str(err)})

    # Attribute, validate, tally per domain.
    all_entries = []
    domain_raw = {}
    domain_valid = {}
    missing_tally_all = {}
    unattributed = 0

    for item in all_items:
        domain = attribute_domain(item, task_id_to_domain, domain_by_normalized)
        if not domain:
            unattributed += 1
            continue
        domain_raw[domain] = domain_raw.get(domain, 0) + 1
        for f in missing_fields_for(item):
            missing_tally_all[f] = missing_tally_all.get(f, 0) + 1
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
        domain_reports.append(
            {
                "domain": domain,
                "business_name": d.get("business_name"),
                "task_id": domain_task_map.get(domain),
                "raw_items": domain_raw.get(domain, 0),
                "valid_items": domain_valid.get(domain, 0),
                "unique_valid_reviews": unique_count,
                "shortfall": max(0, TARGET_PER_DOMAIN - unique_count),
            }
        )

    total_raw = len(all_items)
    total_valid = sum(domain_valid.values())
    total_unique = len(unique)

    benchmark_end = now_iso()
    benchmark_end_ms = time.monotonic()
    latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
    median = latency_values[len(latency_values) // 2] if latency_values else None
    p95 = latency_values[min(len(latency_values) - 1, int(len(latency_values) * 0.95))] if latency_values else None

    write_json(
        out_dir / "timings.json",
        {
            "benchmark_start": benchmark_start,
            "benchmark_end": benchmark_end,
            "wall_clock_ms": int((benchmark_end_ms - benchmark_start_ms) * 1000),
            "per_request": latencies,
            "median_latency_ms": median,
            "p95_latency_ms": p95,
        },
    )

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
            "consumer_country_code": e["raw"].get("consumer_country_code"),
            "number_of_reviews": e["raw"].get("number_of_reviews"),
            "is_author_verified": e["raw"].get("is_author_verified"),
            "is_review_verified": e["raw"].get("is_review_verified"),
            "owner_reply": e["raw"].get("owner_reply"),
            "owner_reply_date": e["raw"].get("owner_reply_date"),
        }
        for e in unique
    ]

    write_json(out_dir / "all-reviews.json", flat_reviews)
    (out_dir / "all-reviews.csv").write_text(
        to_csv(
            flat_reviews,
            [
                "domain", "dedupe_key", "dedupe_key_type", "review_url", "trustpilot_review_id", "rating_value",
                "date_published", "review_headline", "review_body", "author_name", "author_id",
                "consumer_country_code", "number_of_reviews", "is_author_verified", "is_review_verified",
                "owner_reply", "owner_reply_date",
            ],
        ),
        encoding="utf-8",
        newline="",  # preserve to_csv's literal \r\n - avoid Python re-translating it to \r\r\n on Windows
    )

    by_domain = {}
    by_key_type = {}
    for d in duplicates:
        by_domain[d["domain"]] = by_domain.get(d["domain"], 0) + 1
        by_key_type[d["keyType"]] = by_key_type.get(d["keyType"], 0) + 1

    write_json(
        out_dir / "duplicate-report.json",
        {
            "total_duplicates": len(duplicates),
            "by_domain": by_domain,
            "by_key_type": by_key_type,
            "entries": duplicates,
        },
    )

    write_json(
        out_dir / "pagination-report.json",
        {"pages": pages, "stop_reason": results_stop_reason, "unattributed_results": unattributed},
    )

    overall_success_rate_percent = round((total_unique / TARGET_TOTAL) * 100, 2)
    totals = {
        "requested_reviews": TARGET_TOTAL,
        "total_raw_records": total_raw,
        "unattributed_records": unattributed,
        "valid_records": total_valid,
        "unique_valid_reviews": total_unique,
        "duplicate_records": len(duplicates),
        "domains_with_shortfall": [r["domain"] for r in domain_reports if r["shortfall"] > 0],
        "overall_success_rate_percent": overall_success_rate_percent,
        "run_status": jg(final_run, "status"),
        "run_succeeded": run_succeeded,
        "outcome": "completed" if (run_succeeded and total_unique == TARGET_TOTAL and all(r["shortfall"] == 0 for r in domain_reports)) else "partial",
    }

    write_json(
        out_dir / "domain-summary.json",
        {"generated_at": now_iso(), "label": label, "run_id": run_id, "totals": totals, "domains": domain_reports, "missing_field_counts": missing_tally_all},
    )

    credits_consumed = None
    if (
        balance_before is not None
        and balance_after is not None
        and isinstance(balance_before.get("consumed"), (int, float))
        and isinstance(balance_after.get("consumed"), (int, float))
    ):
        credits_consumed = balance_after["consumed"] - balance_before["consumed"]
    advertised_rate_per_1000 = 0.5  # $0.50/1,000 reviews - confirmed from lobstr.io/store/trustpilot-reviews-scraper
    write_json(
        out_dir / "cost-report.json",
        {
            "generated_at": now_iso(),
            "advertised_rate_usd_per_1000_reviews": advertised_rate_per_1000,
            "estimated_cost_usd_for_1000": advertised_rate_per_1000,
            "run_reported_credit_used": jg(final_run, "credit_used"),
            "balance_before": balance_before,
            "balance_after": balance_after,
            "credits_consumed_measured": credits_consumed,
            "measured_cost_usd": None,
            "note": (
                "measured_cost_usd is intentionally null - converting consumed credits to a dollar figure requires the "
                "account's effective credit value (monthly subscription price / included credits), which is "
                "account-plan-specific and was not available via any documented API field. credits_consumed_measured "
                "and run_reported_credit_used are the real measured figures; advertised_rate is the published "
                "marketing rate, not a per-account bill."
            ),
        },
    )

    materialize_error_log_json()

    print("--- RUN COMPLETE ---")
    print(json.dumps(totals, indent=2, ensure_ascii=False))
    return totals


# ---------- modes ----------


def run_plan():
    domains = load_domains()
    load_api_key()
    ensure_dirs([OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR])
    plan = {
        "generated_at": now_iso(),
        "base_url": "https://api.lobstr.io/v1",
        "auth_header": "Authorization: Token <LOBSTR_API_KEY> (value never logged)",
        "domains": [{"business_name": d.get("business_name"), "domain": d.get("domain"), "target_reviews": d.get("target_reviews")} for d in domains],
        "workflow": [
            "discover or load crawler",
            "find or create squid",
            "configure squid",
            "add 5 domain tasks (idempotent)",
            "start ONE run (idempotent)",
            "poll same run id to terminal",
            "paginate /v1/results to exhaustion",
            "dedupe + validate + report",
        ],
        "estimated_cost": {"advertised_rate_usd_per_1000": 0.5, "estimated_usd_for_1000": 0.5, "note": "advertised marketing rate, not account-specific measured cost"},
    }
    write_json(OUT_DIR / "execution-plan.json", plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def run_smoke():
    if os.environ.get("CONFIRM_SMOKE_RUN") != "yes":
        print("Refusing to run: set CONFIRM_SMOKE_RUN=yes to confirm the smoke test.", file=sys.stderr)
        sys.exit(1)
    smoke_requests_dir = SMOKE_DIR / "raw" / "requests"
    smoke_results_dir = SMOKE_DIR / "raw" / "results"
    run_benchmark(
        domains=[{"domain": "www.thepearlsource.com", "business_name": "The Pearl Source", "target_reviews": 20}],
        requests_dir=smoke_requests_dir,
        results_dir=smoke_results_dir,
        out_dir=SMOKE_DIR,
        label="smoke",
    )


def run_full():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating paid Lobstr.io resources.", file=sys.stderr)
        sys.exit(1)
    domains = load_domains()
    run_benchmark(domains=domains, requests_dir=REQUESTS_DIR, results_dir=RESULTS_DIR, out_dir=OUT_DIR, label="full")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "plan":
        run_plan()
    elif mode == "preflight":
        run_preflight()
    elif mode == "smoke":
        run_smoke()
    elif mode == "run":
        run_full()
    else:
        print("Usage: python lobstr_benchmark.py <plan|preflight|smoke|run>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
