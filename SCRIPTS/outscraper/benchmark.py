"""Ported 1:1 from scripts/outscraper-benchmark.js.

Outscraper Trustpilot Reviews benchmark orchestrator.

Usage:
  python scripts/outscraper_benchmark.py plan
    - No network calls. Validates config, prints/saves the execution
      plan + estimated cost range (calculated from published pricing
      tiers, not measured).

  CONFIRM_SMOKE_RUN=yes python scripts/outscraper_benchmark.py smoke
    - ONE real request: www.thepearlsource.com, limit=20, skip=0.
      Minimal cost (likely inside the documented 100-review free
      tier). Validates auth, the async submit->poll->save pipeline,
      and the actual response shape end-to-end before committing to
      the full paid run. Writes to outputs/outscraper/smoke/ so it
      never mixes with the real 5-domain evidence set.

  CONFIRM_PAID_RUN=yes python scripts/outscraper_benchmark.py run
    - Full benchmark: 5 domains x up to 200 reviews each, via
      benchmark-domains.json (the same shared dataset used for
      DataForSEO).

Every fact this file relies on (endpoint, auth header, parameter
names, skip-must-be-multiple-of-20, polling workflow, ~4h result
expiration, pricing tiers) is sourced from docs/outscraper-documentation.md
and docs/outscraper-pricing.md. Where the docs did not state a
number (e.g. a polling SLA, or the exact shape of a completed
result body), this file says so in a comment rather than guessing -
see EXTRACT_ITEMS_NOTE below.

Note: unlike scripts/dataforseo_benchmark.py (and the other providers'
ports), this script does NOT use lib/env.py - the original JS
(scripts/outscraper-benchmark.js) reads OUTSCRAPER_API_KEY out of .env
with its own small inline parser instead of requiring lib/env.js, and
this port preserves that same inline pattern for fidelity.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.outscraper_client import create_client, AuthOrBillingError, InvalidParametersError
from lib.dedupe import build_review_key, dedupe
from lib.csv_utils import to_csv

SCRIPT_DIR = Path(__file__).resolve().parent
ROOT = SCRIPT_DIR.parent.parent
OUT_DIR = ROOT / "outputs" / "outscraper"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
SMOKE_DIR = OUT_DIR / "smoke"

TARGET_PER_DOMAIN = 200
TARGET_TOTAL = 1000
LIMIT_PER_PAGE = 200  # benchmark choice - docs do not state a documented max for `limit`
MAX_PAGES_PER_DOMAIN = 5  # safety ceiling, matches the doc's own worst-case pagination example
SORT = "recency"
LANGUAGES = "all"

# No documented polling SLA was found for Outscraper (unlike DataForSEO's
# "up to 45 minutes"). These are conservative operational choices, not
# facts from the docs - flagged here so they are never mistaken for one.
POLL_INTERVAL_MS = 5_000
MAX_POLL_WAIT_MS = 10 * 60_000  # per page

# Pricing tiers - confirmed from docs/outscraper-pricing.md.
FREE_TIER_REVIEWS = 100
MEDIUM_TIER_CEILING = 50_000
MEDIUM_TIER_RATE_PER_REVIEW = 3 / 1000
BUSINESS_TIER_RATE_PER_REVIEW = 1 / 1000

_SAFE_NAME_RE = re.compile(r"[^a-z0-9.\-]", re.IGNORECASE)


def _js_number(x):
    """Mirrors JS `Number(x.toFixed(n))`: a whole-number float serializes
    without a decimal point (e.g. 0 not 0.0), matching JSON.stringify."""
    if isinstance(x, float) and x.is_integer():
        return int(x)
    return x


def safe_domain_name(domain):
    return _SAFE_NAME_RE.sub("_", domain)


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def _write_text(path, text):
    """Writes with newline='' so no platform newline translation happens -
    matches Node's fs.writeFileSync, which writes the exact string bytes
    given (LF-only for our json.dumps output, CRLF for to_csv's rows)
    regardless of host OS."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def write_json(path, obj):
    _write_text(path, json.dumps(obj, indent=2, ensure_ascii=False))


def load_api_key():
    env_path = ROOT / ".env"
    if not env_path.exists():
        raise RuntimeError(".env not found.")
    raw = env_path.read_text(encoding="utf-8")
    for line in re.split(r"\r?\n", raw):
        trimmed = line.strip()
        if not trimmed or trimmed.startswith("#"):
            continue
        idx = trimmed.find("=")
        if idx == -1:
            continue
        key = trimmed[:idx].strip()
        if key == "OUTSCRAPER_API_KEY":
            value = trimmed[idx + 1 :].strip()
            if not value:
                raise RuntimeError("OUTSCRAPER_API_KEY is present but empty in .env.")
            return value
    raise RuntimeError("OUTSCRAPER_API_KEY not found in .env.")


def load_domains():
    p = ROOT / "benchmark-domains.json"
    if not p.exists():
        raise RuntimeError("benchmark-domains.json not found.")
    parsed = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(parsed, list) or len(parsed) != 5:
        found = len(parsed) if isinstance(parsed, list) else type(parsed).__name__
        raise RuntimeError(f"benchmark-domains.json must contain exactly 5 entries, found {found}.")
    return parsed


def ensure_dirs():
    for d in (OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR):
        d.mkdir(parents=True, exist_ok=True)


def append_error_event(event):
    ERRORS_DIR.mkdir(parents=True, exist_ok=True)
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False) + "\n")


# EXTRACT_ITEMS_NOTE: docs/outscraper-documentation.md lists the *fields*
# a review object should contain, but does not show a full sample
# "status: Success" response body. Outscraper's documented `flat=true`
# option implies the default (non-flat) shape groups results per
# submitted query - i.e. `data: [[...reviews]]` - while `flat=true` would
# combine them into `data: [...reviews]`. This function handles both
# shapes defensively and flags anything else instead of assuming.
def extract_review_items(result_json):
    data = result_json.get("data") if isinstance(result_json, dict) else None
    if not isinstance(data, list):
        return {"items": [], "shapeWarning": "no_data_array"}
    if len(data) == 0:
        return {"items": [], "shapeWarning": None}
    if isinstance(data[0], list):
        items = [item for sublist in data for item in sublist]
        return {"items": items, "shapeWarning": None}
    if isinstance(data[0], dict):
        return {"items": data, "shapeWarning": None}
    return {"items": [], "shapeWarning": "unrecognized_data_shape"}


# Maps Outscraper's documented field names onto the generic shape
# scripts/lib/dedupe.py expects (that module is shared across every API
# benchmark and intentionally knows nothing about any single provider's
# field names - this adapter is the only Outscraper-aware part of the
# dedupe path).
def normalize_review_for_dedupe(item):
    return {
        "id": item.get("review_id"),
        "url": item.get("review_url"),  # not in the documented field list; kept in case it exists
        "user_profile": {"name": item.get("author_title")},
        "timestamp": item.get("review_timestamp") if item.get("review_timestamp") is not None else item.get("review_datetime_utc"),
        "rating": item.get("review_rating"),
        "title": item.get("review_title"),
        "review_text": item.get("review_text"),
    }


def is_valid_review(item):
    has_id = bool(item.get("review_id"))
    has_rating = item.get("review_rating") is not None
    has_date = bool(item.get("review_timestamp") or item.get("review_datetime_utc"))
    has_text = bool(item.get("review_title")) or bool(item.get("review_text"))
    has_reviewer = bool(item.get("author_title")) or bool(item.get("author_id"))
    return bool(has_id and has_rating and has_date and has_text and has_reviewer)


def missing_fields_for(item):
    missing = []
    if not item.get("review_id"):
        missing.append("review_id")
    if item.get("review_rating") is None:
        missing.append("review_rating")
    if not item.get("review_timestamp") and not item.get("review_datetime_utc"):
        missing.append("review_date")
    if not item.get("review_title") and not item.get("review_text"):
        missing.append("review_title_or_text")
    if not item.get("author_title") and not item.get("author_id"):
        missing.append("reviewer_info")
    return missing


def calculate_cost_from_usage(total_usage_reviews, free_already_consumed):
    remaining = total_usage_reviews
    cost = 0
    free_available = 0 if free_already_consumed else FREE_TIER_REVIEWS
    free_used = min(remaining, free_available)
    remaining -= free_used
    if remaining > 0:
        medium_used = min(remaining, MEDIUM_TIER_CEILING - FREE_TIER_REVIEWS)
        cost += medium_used * MEDIUM_TIER_RATE_PER_REVIEW
        remaining -= medium_used
    if remaining > 0:
        cost += remaining * BUSINESS_TIER_RATE_PER_REVIEW
    return _js_number(round(cost, 4))


def build_plan(domains):
    fresh_estimate = calculate_cost_from_usage(TARGET_TOTAL, False)
    used_estimate = calculate_cost_from_usage(TARGET_TOTAL, True)
    return {
        "generated_at": now_iso(),
        "endpoint_submit": "GET https://api.outscraper.com/trustpilot-reviews",
        "endpoint_poll": "GET <exact results_location from submit response> (host may differ, e.g. api.outscraper.cloud - never reconstructed)",
        "auth_header": "X-API-KEY: <OUTSCRAPER_API_KEY> (value never logged)",
        "request_config_per_page": {
            "limit": LIMIT_PER_PAGE,
            "skip": "starts at 0, advances by multiples of 20 as pages accumulate",
            "languages": LANGUAGES,
            "sort": SORT,
            "async": True,
            "fields": "omitted (requests all fields, per docs default) to measure full field coverage",
        },
        "domains": [
            {"business_name": d.get("business_name"), "domain": d.get("domain"), "target_reviews": d.get("target_reviews")}
            for d in domains
        ],
        "pagination_strategy": {
            "per_domain_target": TARGET_PER_DOMAIN,
            "max_pages_per_domain": MAX_PAGES_PER_DOMAIN,
            "skip_increment": "multiple of 20, derived from total raw items already fetched for that domain",
            "stop_conditions": [
                "target_reached",
                "empty_page",
                "repeated_page (zero new unique keys)",
                "partial_last_page (raw < limit)",
                "max_pages_cap",
                "submission_failed",
                "task_failure",
                "poll_timeout",
            ],
            "idempotent_resume": "a page already saved to raw/requests or raw/results is never resubmitted or re-polled",
        },
        "documented_limits": {
            "skip_must_be_multiple_of_20": True,
            "result_availability_after_completion": "~4 hours - raw result is saved to disk immediately on Success",
            "polling_sla": "not documented - this benchmark uses an operational choice (5s interval, 10 min max wait/page), not a confirmed SLA figure",
        },
        "dedupe_strategy": {
            "primary_key": "native review_id",
            "secondary_key": "review URL (not confirmed present in Outscraper's documented field list - included for forward compatibility)",
            "fallback_key": "sha256(domain+author_title+timestamp+review_rating+review_title+review_text)",
            "scope": "within-domain (live, during pagination) and cross-domain (final pass over all collected reviews)",
        },
        "estimated_cost": {
            "pricing_basis": "docs/outscraper-pricing.md - published tiers, not measured",
            "scenario_fresh_account": {"billable_usage": TARGET_TOTAL - FREE_TIER_REVIEWS, "usd": fresh_estimate},
            "scenario_free_tier_already_used": {"billable_usage": TARGET_TOTAL, "usd": used_estimate},
            "expected_range_usd": [fresh_estimate, used_estimate],
            "note": "This is a calculated estimate from the published rate card, not a measured/billed cost. True measured cost requires manual account-balance evidence - Outscraper does not document an endpoint that returns per-request cost or account balance.",
        },
        "output_files": [
            "outputs/outscraper/raw/requests/<domain>-page<N>.json",
            "outputs/outscraper/raw/results/<domain>-page<N>.json",
            "outputs/outscraper/errors/event-log.jsonl",
            "outputs/outscraper/timings.json",
            "outputs/outscraper/all-reviews.json",
            "outputs/outscraper/all-reviews.csv",
            "outputs/outscraper/duplicate-report.json",
            "outputs/outscraper/pagination-report.json",
            "outputs/outscraper/domain-summary.json",
            "outputs/outscraper/cost-report.json",
        ],
    }


def run_plan():
    domains = load_domains()
    load_api_key()  # validates presence only, never logged
    ensure_dirs()
    plan = build_plan(domains)
    write_json(OUT_DIR / "execution-plan.json", plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def fetch_domain_pages(domain, client, latencies, requests_dir, results_dir):
    """Fetches up to TARGET_PER_DOMAIN unique valid reviews for one domain,
    paginating with `skip` only if a single page undershoots the target.
    Never resubmits a page whose request/result is already saved."""
    safe = safe_domain_name(domain)
    skip = 0
    page_num = 1
    seen_keys = set()
    collected = []
    pages = []
    total_raw = 0
    stop_reason = None

    while page_num <= MAX_PAGES_PER_DOMAIN:
        req_file = requests_dir / f"{safe}-page{page_num}.json"
        res_file = results_dir / f"{safe}-page{page_num}.json"

        request_id = None
        results_location = None

        if req_file.exists():
            existing = json.loads(req_file.read_text(encoding="utf-8"))
            existing_response = existing.get("response") or {}
            request_id = existing_response.get("id")
            results_location = existing_response.get("results_location")
            print(f"[submit] {domain} page {page_num}: reusing existing request (idempotent).")
        else:
            submit_result = client.submit_trustpilot_reviews_request(
                query=[domain], limit=LIMIT_PER_PAGE, skip=skip, languages=LANGUAGES, sort=SORT, async_=True
            )
            latencies.append(
                {"phase": "submit", "domain": domain, "page": page_num, "ms": submit_result.get("latency_ms"), "attempts": submit_result.get("attempts")}
            )
            write_json(
                req_file,
                {
                    "domain": domain,
                    "page": page_num,
                    "skip": skip,
                    "limit": LIMIT_PER_PAGE,
                    "requested_at": now_iso(),
                    "request_url": submit_result.get("request_url"),
                    "latency_ms": submit_result.get("latency_ms"),
                    "attempts": submit_result.get("attempts"),
                    "response": submit_result.get("json"),
                },
            )
            submit_json = submit_result.get("json") or {}
            if not submit_result.get("ok") or not submit_json.get("id"):
                append_error_event({"type": "submit_failed", "domain": domain, "page": page_num, "response": submit_result.get("json")})
                stop_reason = "submission_failed"
                break
            request_id = submit_json.get("id")
            results_location = submit_json.get("results_location")

        if not results_location:
            append_error_event({"type": "missing_results_location", "domain": domain, "page": page_num})
            stop_reason = "missing_results_location"
            break

        result_json = None
        if res_file.exists():
            result_json = json.loads(res_file.read_text(encoding="utf-8")).get("response")
            print(f"[poll] {domain} page {page_num}: reusing existing saved result.")
        else:
            poll_start = time.monotonic()
            while (time.monotonic() - poll_start) * 1000 < MAX_POLL_WAIT_MS:
                poll_result = client.poll_results_location(results_location)
                latencies.append(
                    {"phase": "poll", "domain": domain, "page": page_num, "ms": poll_result.get("latency_ms"), "attempts": poll_result.get("attempts")}
                )
                if not poll_result.get("ok"):
                    append_error_event({"type": "poll_error", "domain": domain, "page": page_num, "response": poll_result.get("json")})
                    time.sleep(POLL_INTERVAL_MS / 1000)
                    continue
                poll_json = poll_result.get("json") or {}
                status = poll_json.get("status")
                if status == "Success":
                    result_json = poll_result.get("json")
                    # Save immediately - results expire ~4h after completion.
                    write_json(
                        res_file,
                        {"domain": domain, "page": page_num, "request_id": request_id, "fetched_at": now_iso(), "response": result_json},
                    )
                    break
                if status == "Failure":
                    append_error_event({"type": "task_failure", "domain": domain, "page": page_num, "response": poll_result.get("json")})
                    stop_reason = "task_failure"
                    break
                time.sleep(POLL_INTERVAL_MS / 1000)
            if not result_json and not stop_reason:
                append_error_event({"type": "poll_timeout", "domain": domain, "page": page_num})
                stop_reason = "poll_timeout"

        if stop_reason:
            break

        extracted = extract_review_items(result_json)
        items, shape_warning = extracted["items"], extracted["shapeWarning"]
        if shape_warning:
            append_error_event({"type": "response_shape_warning", "domain": domain, "page": page_num, "shapeWarning": shape_warning})
        pages.append({"page": page_num, "skip": skip, "raw_count": len(items), "shape_warning": shape_warning})
        total_raw += len(items)

        if len(items) == 0:
            stop_reason = "empty_page"
            break

        new_count = 0
        for item in items:
            key_result = build_review_key(domain, normalize_review_for_dedupe(item))
            key = key_result["key"]
            if key not in seen_keys:
                seen_keys.add(key)
                new_count += 1
            collected.append({"domain": domain, "review": normalize_review_for_dedupe(item), "raw": item})

        if new_count == 0:
            stop_reason = "repeated_page"
            break
        if len(items) < LIMIT_PER_PAGE:
            stop_reason = "partial_last_page"
            break
        if len(seen_keys) >= TARGET_PER_DOMAIN:
            stop_reason = "target_reached"
            break

        skip = (total_raw // 20) * 20
        page_num += 1

    if not stop_reason:
        stop_reason = "max_pages_cap"

    return {"collected": collected, "pages": pages, "totalRaw": total_raw, "stopReason": stop_reason}


def run_benchmark(domains, requests_dir, results_dir, out_dir, label):
    api_key = load_api_key()
    requests_dir.mkdir(parents=True, exist_ok=True)
    results_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)

    latencies = []
    benchmark_start = now_iso()
    benchmark_start_perf = time.monotonic()

    def on_event(event):
        append_error_event({"label": label, **event})

    client = create_client(api_key, on_event=on_event)

    domain_reports = []
    all_entries = []

    for entry in domains:
        domain = entry["domain"]
        try:
            result = fetch_domain_pages(domain, client, latencies, requests_dir, results_dir)
            valid_entries = [e for e in result["collected"] if is_valid_review(e["raw"])]
            missing_tally = {}
            for e in result["collected"]:
                for f in missing_fields_for(e["raw"]):
                    missing_tally[f] = missing_tally.get(f, 0) + 1
            all_entries.extend(valid_entries)
            domain_reports.append(
                {
                    "domain": domain,
                    "business_name": entry.get("business_name"),
                    "pages_fetched": len(result["pages"]),
                    "pagination_detail": result["pages"],
                    "stop_reason": result["stopReason"],
                    "raw_items": len(result["collected"]),
                    "valid_items": len(valid_entries),
                    "missing_field_counts": missing_tally,
                }
            )
        except AuthOrBillingError as err:
            (OUT_DIR / "errors").mkdir(parents=True, exist_ok=True)
            write_json(
                OUT_DIR / "errors" / "BLOCKER-auth-or-billing.json",
                {"domain": domain, "message": str(err), "status": err.status, "body": err.body},
            )
            print(f"BLOCKER: authentication/billing failure on {domain}: {err}", file=sys.stderr)
            sys.exit(2)
        except InvalidParametersError as err:
            append_error_event({"type": "invalid_parameters_fatal_for_domain", "domain": domain, "message": str(err), "body": err.body})
            domain_reports.append({"domain": domain, "business_name": entry.get("business_name"), "stop_reason": "invalid_parameters", "error": str(err)})
            continue

    dedupe_result = dedupe(all_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]

    unique_by_domain = {}
    for e in unique:
        unique_by_domain[e["domain"]] = unique_by_domain.get(e["domain"], 0) + 1
    for report in domain_reports:
        report["unique_valid_reviews"] = unique_by_domain.get(report["domain"], 0)
        report["shortfall"] = max(0, TARGET_PER_DOMAIN - report["unique_valid_reviews"])

    total_raw = sum((r.get("raw_items") or 0) for r in domain_reports)
    total_valid = sum((r.get("valid_items") or 0) for r in domain_reports)
    total_unique = len(unique)

    benchmark_end = now_iso()
    benchmark_end_perf = time.monotonic()
    latency_values = sorted(v["ms"] for v in latencies if isinstance(v.get("ms"), (int, float)))
    median = latency_values[len(latency_values) // 2] if latency_values else None
    p95 = latency_values[min(len(latency_values) - 1, int(len(latency_values) * 0.95))] if latency_values else None

    write_json(
        out_dir / "timings.json",
        {
            "benchmark_start": benchmark_start,
            "benchmark_end": benchmark_end,
            "wall_clock_ms": int(round((benchmark_end_perf - benchmark_start_perf) * 1000)),
            "per_request": latencies,
            "median_latency_ms": median,
            "p95_latency_ms": p95,
        },
    )

    flat_reviews = []
    for e in unique:
        raw = e["raw"]
        flat_reviews.append(
            {
                "domain": e["domain"],
                "dedupe_key": e.get("dedupeKey"),
                "dedupe_key_type": e.get("dedupeKeyType"),
                "review_id": raw.get("review_id"),
                "review_rating": raw.get("review_rating"),
                "review_verified": raw.get("review_verified"),
                "review_timestamp": raw.get("review_timestamp"),
                "review_datetime_utc": raw.get("review_datetime_utc"),
                "review_title": raw.get("review_title"),
                "review_text": raw.get("review_text"),
                "author_title": raw.get("author_title"),
                "author_id": raw.get("author_id"),
                "author_country_code": raw.get("author_country_code"),
                "author_reviews_number": raw.get("author_reviews_number"),
                "owner_answer": raw.get("owner_answer"),
                "owner_answer_date": raw.get("owner_answer_date"),
            }
        )

    write_json(out_dir / "all-reviews.json", flat_reviews)
    csv_columns = [
        "domain",
        "dedupe_key",
        "dedupe_key_type",
        "review_id",
        "review_rating",
        "review_verified",
        "review_timestamp",
        "review_datetime_utc",
        "review_title",
        "review_text",
        "author_title",
        "author_id",
        "author_country_code",
        "author_reviews_number",
        "owner_answer",
        "owner_answer_date",
    ]
    _write_text(out_dir / "all-reviews.csv", to_csv(flat_reviews, csv_columns))

    by_domain = {}
    for d in duplicates:
        by_domain[d["domain"]] = by_domain.get(d["domain"], 0) + 1
    by_key_type = {}
    for d in duplicates:
        by_key_type[d["keyType"]] = by_key_type.get(d["keyType"], 0) + 1
    write_json(
        out_dir / "duplicate-report.json",
        {"total_duplicates": len(duplicates), "by_domain": by_domain, "by_key_type": by_key_type, "entries": duplicates},
    )

    pagination_rows = []
    for r in domain_reports:
        row = {"domain": r["domain"]}
        if "pages_fetched" in r:
            row["pages_fetched"] = r["pages_fetched"]
        if "pagination_detail" in r:
            row["pagination_detail"] = r["pagination_detail"]
        row["stop_reason"] = r.get("stop_reason")
        pagination_rows.append(row)
    write_json(out_dir / "pagination-report.json", pagination_rows)

    totals = {
        "requested_reviews": TARGET_TOTAL,
        "total_raw_records": total_raw,
        "valid_records": total_valid,
        "unique_valid_reviews": total_unique,
        "duplicate_records": len(duplicates),
        "domains_with_shortfall": [r["domain"] for r in domain_reports if (r.get("shortfall") or 0) > 0],
        "overall_success_rate_percent": _js_number(round((total_unique / TARGET_TOTAL) * 100, 2)),
        "outcome": "completed" if (total_unique == TARGET_TOTAL and all((r.get("shortfall") or 0) == 0 for r in domain_reports)) else "partial",
    }

    write_json(out_dir / "domain-summary.json", {"generated_at": now_iso(), "label": label, "totals": totals, "domains": domain_reports})

    calculated_fresh = calculate_cost_from_usage(total_raw, False)
    calculated_used = calculate_cost_from_usage(total_raw, True)
    write_json(
        out_dir / "cost-report.json",
        {
            "generated_at": now_iso(),
            "total_usage_reviews_raw": total_raw,
            "calculated_cost_scenario_fresh_account_usd": calculated_fresh,
            "calculated_cost_scenario_free_tier_used_usd": calculated_used,
            "measured_cost_usd": None,
            "note": "calculated_* figures come from applying the published pricing tiers (docs/outscraper-pricing.md) to the measured raw usage count. measured_cost_usd is intentionally null - Outscraper does not document an endpoint that returns account balance or per-request billed cost, so true measured cost requires manually checking the Outscraper billing dashboard before/after this run.",
        },
    )

    print("--- RUN COMPLETE ---")
    print(json.dumps(totals, indent=2, ensure_ascii=False))
    return totals


def run_smoke():
    if os.environ.get("CONFIRM_SMOKE_RUN") != "yes":
        print("Refusing to run: set CONFIRM_SMOKE_RUN=yes to confirm the smoke test (1 real request, likely free-tier cost).", file=sys.stderr)
        sys.exit(1)
    ensure_dirs()
    smoke_requests_dir = SMOKE_DIR / "raw" / "requests"
    smoke_results_dir = SMOKE_DIR / "raw" / "results"
    run_benchmark(
        domains=[{"domain": "www.thepearlsource.com", "business_name": "The Pearl Source"}],
        requests_dir=smoke_requests_dir,
        results_dir=smoke_results_dir,
        out_dir=SMOKE_DIR,
        label="smoke",
    )


def run_full():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating paid Outscraper requests.", file=sys.stderr)
        sys.exit(1)
    ensure_dirs()
    domains = load_domains()
    run_benchmark(domains=domains, requests_dir=REQUESTS_DIR, results_dir=RESULTS_DIR, out_dir=OUT_DIR, label="full")


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else None
    if mode == "plan":
        run_plan()
    elif mode == "smoke":
        run_smoke()
    elif mode == "run":
        run_full()
    else:
        print("Usage: python outscraper_benchmark.py <plan|smoke|run>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:  # noqa: BLE001 - mirrors the JS top-level main().catch()
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
