"""Ported 1:1 from scripts/apify-benchmark.js.

Apify Trustpilot Reviews benchmark orchestrator, using the
automation-lab/trustpilot Actor.

Facts relied on here are sourced from docs/apify/apify-documentation.md
and docs/apify/apify-pricing.md (user-provided, citing official Apify
docs and the Actor's own store page). See scripts/lib/apify_client.py's
header comment for the confirmed endpoint/param/response details.

Usage:
  python scripts/apify_benchmark.py plan
  CONFIRM_PAID_RUN=yes python scripts/apify_benchmark.py run

Safety: exactly ONE Actor run is created for all 5 domains together
(per explicit instruction). Idempotent resume via outputs/apify/raw/runs/run.json
- if a run was already started, it is polled/reused, never restarted.
"""
import json
import math
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.apify_client import ApifyClient, AuthOrBillingError, InvalidRequestError
from lib.csv_utils import to_csv
from lib.dedupe import dedupe

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "outputs" / "apify"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RUNS_DIR = OUT_DIR / "raw" / "runs"
DATASETS_DIR = OUT_DIR / "raw" / "datasets"
ERRORS_DIR = OUT_DIR / "errors"
SMOKE_DIR = OUT_DIR / "smoke"  # declared, but unused - matches the JS source 1:1
ENV_PATH = ROOT / ".env"

TARGET_PER_DOMAIN = 200
TARGET_TOTAL = 1000
POLL_INTERVAL_MS = 10_000
MAX_POLL_WAIT_MS = 40 * 60_000  # generous vs. the vendor's own ~2-4 min/200-reviews claim x5 domains
SETTLE_WAIT_MS = 5_000  # per docs: "wait briefly ... finalized usage values may take a few seconds to settle"
DATASET_PAGE_LIMIT = 1000
MAX_DATASET_PAGES = 20

RUN_START_FEE_USD = 0.005
FREE_TIER_PER_REVIEW_USD = 0.000575

TERMINAL_SUCCESS = {"SUCCEEDED"}
TERMINAL_FAILURE = {"FAILED", "ABORTED", "TIMED-OUT"}


def now_iso():
    """Matches JS's `new Date().toISOString()` - millisecond precision, Z suffix."""
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def now_ms():
    """Matches JS's `Date.now()` - whole milliseconds."""
    return int(time.time() * 1000)


def sleep_ms(ms):
    time.sleep(ms / 1000.0)


def to_fixed(value, digits):
    """Matches JS's `Number(value.toFixed(digits))`: rounds to `digits`
    decimal places, but collapses to a plain integer when the rounded
    value is whole (JS has no int/float distinction, so e.g. 200.00
    serializes as 200, not 200.0)."""
    rounded = float(f"{value:.{digits}f}")
    if rounded == int(rounded):
        return int(rounded)
    return rounded


def dump_json(obj):
    return json.dumps(obj, indent=2, ensure_ascii=False)


def write_json(path, obj):
    # newline="" prevents Python's text-mode newline translation (LF -> CRLF
    # on Windows), matching Node's fs.writeFileSync byte-exact behavior.
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(dump_json(obj))


def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def get_env_var(name):
    """Inline .env reader, ported 1:1 from apify-benchmark.js's own
    getEnvVar (NOT lib/env.py - the original JS didn't use lib/env.js for
    this provider either)."""
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
            value = trimmed[idx + 1 :].strip()
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
    # JS's `actorId.replace('/', '~')` replaces only the first '/' - mirror
    # that here (Python's str.replace() replaces all occurrences by default).
    return actor_id.replace("/", "~", 1) if "/" in actor_id else actor_id


def load_domains():
    p = ROOT / "benchmark-domains.json"
    if not p.exists():
        raise RuntimeError("benchmark-domains.json not found.")
    parsed = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(parsed, list) or len(parsed) != 5:
        found = len(parsed) if isinstance(parsed, list) else type(parsed).__name__
        raise RuntimeError(f"benchmark-domains.json must contain exactly 5 entries, found {found}.")
    return parsed


def ensure_dirs(dirs):
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    record = {"loggedAt": now_iso(), **event}
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def materialize_error_log_json():
    jsonl_path = ERRORS_DIR / "event-log.jsonl"
    events = []
    if jsonl_path.exists():
        for line in jsonl_path.read_text(encoding="utf-8").split("\n"):
            if line:
                events.append(json.loads(line))
    write_json(OUT_DIR / "error-log.json", events)
    return events


def normalize_domain(d):
    s = str(d if d is not None else "").strip().lower()
    return re.sub(r"^www\.", "", s)


# ---------- normalization / validity / dedupe ----------


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
    has_domain = bool(item.get("companyDomain"))
    return bool(has_id and has_rating and has_date and has_text and has_author and has_domain)


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
    if not item.get("companyDomain"):
        missing.append("companyDomain")
    return missing


# ---------- run (single paid trigger, idempotent) ----------


def ensure_single_run(client, rest_actor_id, input_body):
    run_file = RUNS_DIR / "run.json"
    if run_file.exists():
        saved = json.loads(run_file.read_text(encoding="utf-8"))
        print(f"[run] reusing existing saved run id: {saved['run_id']} (idempotent - no new Actor run created).")
        return saved["run_id"]

    write_json(
        REQUESTS_DIR / "actor-input.json",
        {"saved_at": now_iso(), "actor_id": rest_actor_id, "input": input_body},
    )

    result = client.start_actor_run(rest_actor_id, input_body)
    write_json(
        RUNS_DIR / "run-create-response.json",
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


def poll_run_to_terminal(client, run_id, latencies):
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

    write_json(RUNS_DIR / "poll-history.json", {"run_id": run_id, "poll_history": poll_history})
    return last_run


def fetch_final_run_object(client, run_id):
    sleep_ms(SETTLE_WAIT_MS)
    res = client.get_run(run_id)
    final_run = res["json"]["data"] if res.get("ok") else None
    write_json(RUNS_DIR / "run-final.json", {"fetched_at": now_iso(), "response": res.get("json")})
    return final_run


# ---------- dataset retrieval (offset/limit, loop-safe, idempotent) ----------


def fetch_all_dataset_items(client, dataset_id, latencies):
    offset = 0
    page_num = 1
    all_items = []
    pages = []
    seen_offsets = set()
    stop_reason = None

    while page_num <= MAX_DATASET_PAGES:
        page_file = DATASETS_DIR / f"page{page_num}-offset{offset}.json"

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


# ---------- main benchmark run ----------


def run_benchmark(domains, out_dir, label, input_body):
    api_token = load_api_token()
    rest_actor_id = load_rest_actor_id()
    ensure_dirs([out_dir, REQUESTS_DIR, RUNS_DIR, DATASETS_DIR, ERRORS_DIR])

    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = now_ms()

    client = ApifyClient(api_token, on_event=lambda event: append_error_event({"label": label, **event}))

    try:
        run_id = ensure_single_run(client, rest_actor_id, input_body)
        actor_run_start_ms = now_ms()
        terminal_run = poll_run_to_terminal(client, run_id, latencies)
        actor_run_duration_ms = now_ms() - actor_run_start_ms

        if not terminal_run or terminal_run.get("status") in TERMINAL_FAILURE:
            status_val = terminal_run.get("status") if terminal_run else None
            final_status = status_val if status_val is not None else "unknown/timeout"
            write_json(
                ERRORS_DIR / "BLOCKER-run-not-succeeded.json",
                {"run_id": run_id, "final_status": final_status},
            )
            print(
                f"BLOCKER: Actor run did not succeed (status: {final_status}). Not retrying automatically.",
                file=sys.stderr,
            )
            final_run = fetch_final_run_object(client, run_id)
            return {"blocked": True, "run_id": run_id, "final_run": final_run, "actor_run_duration_ms": actor_run_duration_ms}

        final_run = fetch_final_run_object(client, run_id)
        dataset_id = (final_run.get("defaultDatasetId") if final_run else None) or terminal_run.get("defaultDatasetId")
        if not dataset_id:
            raise RuntimeError("No defaultDatasetId found on the completed run.")

        dataset_fetch_start_ms = now_ms()
        all_items, pages, stop_reason = fetch_all_dataset_items(client, dataset_id, latencies)
        dataset_fetch_ms = now_ms() - dataset_fetch_start_ms

        # ---------- validate, attribute, dedupe ----------
        domain_by_normalized = {}
        for d in domains:
            domain_by_normalized[normalize_domain(d["domain"])] = d["domain"]

        all_entries = []
        domain_raw = {}
        domain_valid = {}
        missing_tally_all = {}
        unattributed = 0

        for item in all_items:
            normalized = normalize_domain(item.get("companyDomain"))
            canonical_domain = domain_by_normalized.get(normalized)
            if not canonical_domain:
                unattributed += 1
                continue
            domain_raw[canonical_domain] = domain_raw.get(canonical_domain, 0) + 1
            for f in missing_fields_for(item):
                missing_tally_all[f] = missing_tally_all.get(f, 0) + 1
            if is_valid_review(item):
                domain_valid[canonical_domain] = domain_valid.get(canonical_domain, 0) + 1
                all_entries.append({"domain": canonical_domain, "review": normalize_review_for_dedupe(item), "raw": item})

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
                    "business_name": d["business_name"],
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
        reviews_per_minute = to_fixed((total_unique / wall_clock_ms) * 60000, 2) if wall_clock_ms > 0 else None

        write_json(
            Path(out_dir) / "timings.json",
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
                "reviews_per_minute": reviews_per_minute,
            },
        )

        flat_reviews = []
        for e in unique:
            raw = e["raw"]
            flat_reviews.append(
                {
                    "domain": e["domain"],
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

        write_json(Path(out_dir) / "all-reviews.json", flat_reviews)
        csv_columns = [
            "domain",
            "dedupe_key",
            "dedupe_key_type",
            "reviewId",
            "reviewUrl",
            "rating",
            "title",
            "text",
            "publishedDate",
            "experienceDate",
            "language",
            "likes",
            "verificationLevel",
            "isVerified",
            "source",
            "authorName",
            "authorId",
            "authorReviewCount",
            "country",
            "replyMessage",
            "replyPublishedDate",
        ]
        write_text(Path(out_dir) / "all-reviews.csv", to_csv(flat_reviews, csv_columns))

        by_domain = {}
        for dup in duplicates:
            by_domain[dup["domain"]] = by_domain.get(dup["domain"], 0) + 1
        by_key_type = {}
        for dup in duplicates:
            by_key_type[dup["keyType"]] = by_key_type.get(dup["keyType"], 0) + 1

        write_json(
            Path(out_dir) / "duplicate-report.json",
            {
                "total_duplicates": len(duplicates),
                "by_domain": by_domain,
                "by_key_type": by_key_type,
                "entries": duplicates,
            },
        )

        write_json(
            Path(out_dir) / "pagination-report.json",
            {"pages": pages, "stop_reason": stop_reason, "unattributed_items": unattributed},
        )

        totals = {
            "requested_reviews": TARGET_TOTAL,
            "total_raw_records": total_raw,
            "unattributed_records": unattributed,
            "valid_records": total_valid,
            "unique_valid_reviews": total_unique,
            "duplicate_records": len(duplicates),
            "domains_with_shortfall": [r["domain"] for r in domain_reports if r["shortfall"] > 0],
            "overall_success_rate_percent": to_fixed((total_unique / TARGET_TOTAL) * 100, 2),
            "run_id": run_id,
            "dataset_id": dataset_id,
            "run_status": terminal_run.get("status"),
            "outcome": "completed"
            if (total_unique == TARGET_TOTAL and all(r["shortfall"] == 0 for r in domain_reports))
            else "partial",
        }

        write_json(
            Path(out_dir) / "domain-summary.json",
            {
                "generated_at": now_iso(),
                "label": label,
                "totals": totals,
                "domains": domain_reports,
                "missing_field_counts": missing_tally_all,
            },
        )
        write_json(
            Path(out_dir) / "run-state.json",
            {
                "generated_at": now_iso(),
                "run_id": run_id,
                "dataset_id": dataset_id,
                "final_status": terminal_run.get("status"),
                "domains": [{"domain": r["domain"], "shortfall": r["shortfall"]} for r in domain_reports],
            },
        )

        # ---------- usage / cost ----------
        usage = final_run.get("usage") if final_run else None
        usage_usd = final_run.get("usageUsd") if final_run else None
        usage_total_usd = final_run.get("usageTotalUsd") if final_run else None
        estimated_free_tier_usd = to_fixed(total_unique * FREE_TIER_PER_REVIEW_USD + RUN_START_FEE_USD, 4)

        write_json(
            Path(out_dir) / "usage-report.json",
            {
                "generated_at": now_iso(),
                "run_id": run_id,
                "usage": usage,
                "usageUsd": usage_usd,
                "usageTotalUsd": usage_total_usd,
                "note": "usage/usageUsd/usageTotalUsd are copied verbatim from the settled Run object (fetched after a 5s wait per Apify docs guidance). Absent fields are Pending, not invented.",
            },
        )

        write_json(
            Path(out_dir) / "cost-report.json",
            {
                "generated_at": now_iso(),
                "published_estimate_usd": {
                    "per_review_free_tier": FREE_TIER_PER_REVIEW_USD,
                    "run_start_fee": RUN_START_FEE_USD,
                    "estimated_for_1000_reviews": 0.58,
                },
                "estimated_cost_for_measured_unique_usd": estimated_free_tier_usd,
                "measured_actor_event_cost_usd": usage_usd,
                "measured_total_cost_usd": usage_total_usd,
                "cost_per_1000_successful_reviews_usd": to_fixed((usage_total_usd / total_unique) * 1000, 4)
                if (usage_total_usd is not None and total_unique > 0)
                else None,
                "note": "measured_* fields are null/Pending if the settled Run object did not return them - never invented.",
            },
        )

        materialize_error_log_json()

        print("--- RUN COMPLETE ---")
        print(dump_json(totals))
        return {"blocked": False, "totals": totals}
    except AuthOrBillingError as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(
            ERRORS_DIR / "BLOCKER-auth-or-billing.json",
            {"message": str(err), "status": err.status, "body": err.body},
        )
        print(f"BLOCKER: authentication/billing failure: {err}", file=sys.stderr)
        sys.exit(2)
    except InvalidRequestError as err:
        ERRORS_DIR.mkdir(parents=True, exist_ok=True)
        write_json(
            ERRORS_DIR / "BLOCKER-invalid-request.json",
            {"message": str(err), "status": err.status, "body": err.body},
        )
        print(f"BLOCKER: invalid request: {err}", file=sys.stderr)
        sys.exit(2)


# ---------- modes ----------


def build_input(domains):
    return {
        "companyUrls": [d["domain"] for d in domains],
        "maxReviewsPerCompany": TARGET_PER_DOMAIN,
        "sort": "recency",
        "includeCompanyInfo": True,
    }


def run_plan():
    domains = load_domains()
    load_api_token()
    rest_actor_id = load_rest_actor_id()
    ensure_dirs([OUT_DIR, REQUESTS_DIR, RUNS_DIR, DATASETS_DIR, ERRORS_DIR])
    input_body = build_input(domains)
    plan = {
        "generated_at": now_iso(),
        "base_url": "https://api.apify.com/v2",
        "actor_id": rest_actor_id,
        "auth_header": "Authorization: Bearer <APIFY_API_TOKEN> (value never logged)",
        "input": input_body,
        "workflow": [
            "start ONE run for all 5 domains",
            "poll same run id to terminal",
            "wait 5s, refetch final run for settled usage",
            "paginate dataset items to exhaustion",
            "dedupe + validate + report",
        ],
        "estimated_cost_usd": {
            "per_review_free_tier": FREE_TIER_PER_REVIEW_USD,
            "run_start_fee": RUN_START_FEE_USD,
            "estimated_for_1000_reviews": 0.58,
        },
    }
    write_json(OUT_DIR / "execution-plan.json", plan)
    print(dump_json(plan))


def run_smoke():
    if os.environ.get("CONFIRM_SMOKE_RUN") != "yes":
        print("Refusing to run: set CONFIRM_SMOKE_RUN=yes to confirm the smoke test.", file=sys.stderr)
        sys.exit(1)
    raise RuntimeError(
        "Smoke mode not implemented - this benchmark uses exactly one Actor run for all 5 domains per explicit instruction."
    )


def run_full():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print(
            "Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating a paid Apify Actor run.",
            file=sys.stderr,
        )
        sys.exit(1)
    domains = load_domains()
    input_body = build_input(domains)
    run_benchmark(domains=domains, out_dir=OUT_DIR, label="full", input_body=input_body)


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "plan":
        run_plan()
    elif mode == "smoke":
        run_smoke()
    elif mode == "run":
        run_full()
    else:
        print("Usage: python apify_benchmark.py <plan|run>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # noqa: BLE001 - mirrors the JS script's top-level catch
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
