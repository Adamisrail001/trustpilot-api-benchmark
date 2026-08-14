"""Ported 1:1 from scripts/openwebninja-benchmark.js.

OpenWeb Ninja Trustpilot Reviews benchmark orchestrator.

Facts relied on here are confirmed against the live, browser-rendered
official docs at https://www.openwebninja.com/api/trustpilot-company-and-reviews-data/docs
(a Scalar/OpenAPI reference - a plain HTTP fetch only returns the page
shell, so this was verified with a real browser in the original research
session). See scripts/lib/openwebninja_client.py's module docstring for
the confirmed endpoint/param/response details.

Usage:
  python scripts/openwebninja_benchmark.py plan
  python scripts/openwebninja_benchmark.py preflight
  CONFIRM_SMOKE_RUN=yes python scripts/openwebninja_benchmark.py smoke
  CONFIRM_PAID_RUN=yes OPENWEBNINJA_QUOTA_REMAINING=<n> python scripts/openwebninja_benchmark.py run

IMPORTANT: OpenWeb Ninja's documented endpoint list (company-search,
company-details, company-reviews, category-*, consumer-*) contains NO
account/usage/quota endpoint. Remaining quota cannot be checked via the
API. The `run` mode therefore requires the human to supply the current
remaining monthly quota via OPENWEBNINJA_QUOTA_REMAINING (read from the
dashboard at app.openwebninja.com) and refuses to run below the safe
minimum of 60, per the project's explicit instruction. This is a
deliberate design choice, not a missed feature - inventing a fake
"quota check" against a nonexistent endpoint would violate the
do-not-guess rule.

This script reads OPENWEBNINJA_API_KEY from .env at the project root using
its own inline reader (get_env_var), the same as the original JS - it does
NOT use lib/env.py, for fidelity with the original script's design.
"""
import json
import os
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from lib.openwebninja_client import create_client, AuthOrQuotaError, InvalidRequestError
from lib.dedupe import dedupe
from lib.csv_utils import to_csv

ROOT = Path(__file__).resolve().parent.parent.parent
OUT_DIR = ROOT / "outputs" / "openwebninja"
REQUESTS_DIR = OUT_DIR / "raw" / "requests"
RESULTS_DIR = OUT_DIR / "raw" / "results"
ERRORS_DIR = OUT_DIR / "errors"
SMOKE_DIR = OUT_DIR / "smoke"
ENV_PATH = ROOT / ".env"

TARGET_PER_DOMAIN = 200
TARGET_TOTAL = 1000
REVIEWS_PER_PAGE = 20  # confirmed: "each page includes up to 20 results"
MAX_PAGES_WITHOUT_COOKIE = 10  # confirmed: page 11+ requires a logged-in Trustpilot cookie
MIN_QUOTA_REQUIRED = 60  # 50 review-page requests + headroom for retries/company lookups, per project instruction
REQUEST_SPACING_MS = 350  # ~2.8 req/sec, safely under every documented plan's rate limit (Free 10/s, Pro 5/s, ..., recommended safe default 4/s)


def now_iso():
    dt = datetime.now(timezone.utc)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"


def to_fixed_number(value, digits):
    """Mirrors JS's Number(value.toFixed(digits)) - fixed-decimal rounding
    that drops trailing zeros / the decimal point entirely for whole numbers
    (e.g. 50.00 -> 50, not 50.0), so serialized JSON matches the JS output."""
    formatted = f"{value:.{digits}f}"
    num = float(formatted)
    return int(num) if num == int(num) else num


def js_num_str(n):
    """Mirrors JS's default numeric-to-string coercion (no trailing .0 on
    whole numbers) for use in interpolated console messages."""
    return str(int(n)) if n == int(n) else str(n)


def write_json(path, obj):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(obj, indent=2, ensure_ascii=False))


def write_text(path, content):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(content)


def get_env_var(name):
    if not ENV_PATH.exists():
        raise RuntimeError(".env not found.")
    text = ENV_PATH.read_text(encoding="utf-8")
    for raw_line in text.split("\n"):
        trimmed = raw_line.strip()
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
    key = get_env_var("OPENWEBNINJA_API_KEY")
    if not key:
        raise RuntimeError("OPENWEBNINJA_API_KEY not found or empty in .env.")
    return key


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
    with open(ERRORS_DIR / "event-log.jsonl", "a", encoding="utf-8", newline="") as f:
        f.write(json.dumps({"loggedAt": now_iso(), **event}, ensure_ascii=False) + "\n")


def materialize_error_log_json():
    jsonl_path = ERRORS_DIR / "event-log.jsonl"
    events = []
    if jsonl_path.exists():
        for line in jsonl_path.read_text(encoding="utf-8").split("\n"):
            if line:
                events.append(json.loads(line))
    write_json(OUT_DIR / "error-log.json", events)
    return events


def safe_domain_name(domain):
    return re.sub(r"[^a-z0-9.-]", "_", domain, flags=re.IGNORECASE)


# ---------- normalization / validity / dedupe ----------

def normalize_review_for_dedupe(item, domain):
    return {
        "id": item.get("review_id"),
        "url": None,  # no review-URL field is documented for this endpoint - tier 2 gracefully never fires
        "user_profile": {"name": item.get("consumer_name")},
        "timestamp": item.get("review_time"),
        "rating": item.get("review_rating"),
        "title": item.get("review_title"),
        "review_text": item.get("review_text"),
        "domain": domain,
    }


def is_valid_review(item):
    has_id = bool(item.get("review_id"))
    has_rating = item.get("review_rating") is not None
    has_date = bool(item.get("review_time"))
    has_text = bool(item.get("review_title")) or bool(item.get("review_text"))
    has_reviewer = bool(item.get("consumer_name")) or bool(item.get("consumer_id"))
    not_pending = item.get("review_is_pending") is not True  # pending reviews are not yet published/final
    return bool(has_id and has_rating and has_date and has_text and has_reviewer and not_pending)


def missing_fields_for(item):
    missing = []
    if not item.get("review_id"):
        missing.append("review_id")
    if item.get("review_rating") is None:
        missing.append("review_rating")
    if not item.get("review_time"):
        missing.append("review_time")
    if not item.get("review_title") and not item.get("review_text"):
        missing.append("review_title_or_text")
    if not item.get("consumer_name") and not item.get("consumer_id"):
        missing.append("reviewer_info")
    return missing


# ---------- per-domain pagination (pages 1-10, idempotent, loop-safe) ----------

def _reviews_from_json(json_body):
    if not isinstance(json_body, dict):
        return None
    data = json_body.get("data")
    if not isinstance(data, dict):
        return None
    return data.get("reviews")


def fetch_domain_reviews(domain, client, latencies, requests_dir, results_dir, max_pages):
    safe = safe_domain_name(domain)
    seen_keys = set()
    collected = []
    pages = []
    stop_reason = None

    for page in range(1, max_pages + 1):
        req_file = Path(requests_dir) / f"{safe}-page{page}.json"
        res_file = Path(results_dir) / f"{safe}-page{page}.json"

        if res_file.exists():
            json_body = json.loads(res_file.read_text(encoding="utf-8"))["response"]
            print(f"[page] {domain} page {page}: reusing existing saved result (idempotent).")
        else:
            time.sleep(REQUEST_SPACING_MS / 1000)  # sequential, rate-limited
            try:
                result = client.get_company_reviews(company_domain=domain, page=page, sort="recency")
            except AuthOrQuotaError:
                raise
            except InvalidRequestError as err:
                append_error_event({"type": "invalid_request", "domain": domain, "page": page, "message": str(err), "body": err.body})
                stop_reason = "invalid_request"
                break
            latencies.append({"phase": "company-reviews", "domain": domain, "page": page, "ms": result["latencyMs"], "attempts": result["attempts"]})
            write_json(req_file, {
                "domain": domain,
                "page": page,
                "requested_at": now_iso(),
                "request_url": result["requestUrl"],
                "latency_ms": result["latencyMs"],
                "attempts": result["attempts"],
                "ok": result["ok"],
                "status": result["status"],
            })
            if not result["ok"]:
                append_error_event({"type": "page_fetch_failed", "domain": domain, "page": page, "status": result["status"], "body": result["json"]})
                stop_reason = "fetch_failed"
                break
            json_body = result["json"]
            write_json(res_file, {"domain": domain, "page": page, "fetched_at": now_iso(), "response": json_body})

        items = _reviews_from_json(json_body)
        if not isinstance(items, list):
            append_error_event({"type": "unexpected_response_shape", "domain": domain, "page": page, "keys": list(json_body.keys()) if isinstance(json_body, dict) else None})
            stop_reason = "unexpected_response_shape"
            break

        pages.append({"page": page, "raw_count": len(items)})

        if len(items) == 0:
            stop_reason = "empty_page"
            break

        new_count = 0
        for item in items:
            key = f"id:{item.get('review_id')}" if item.get("review_id") else None
            if key:
                if key not in seen_keys:
                    seen_keys.add(key)
                    new_count += 1
            else:
                new_count += 1  # no id to compare - can't prove it's a repeat, so don't false-stop
            collected.append({"domain": domain, "review": normalize_review_for_dedupe(item, domain), "raw": item})

        if new_count == 0:
            stop_reason = "repeated_page"
            break
        if len(items) < REVIEWS_PER_PAGE:
            stop_reason = "partial_last_page"
            break
        if len(seen_keys) >= TARGET_PER_DOMAIN:
            stop_reason = "target_reached"
            break

    if not stop_reason:
        stop_reason = "max_pages_reached"
    return {"collected": collected, "pages": pages, "stopReason": stop_reason}


# ---------- main benchmark run (shared by smoke and full) ----------

def run_benchmark(domains, requests_dir, results_dir, out_dir, label, max_pages):
    api_key = load_api_key()
    out_dir = Path(out_dir)
    ensure_dirs([out_dir, requests_dir, results_dir, ERRORS_DIR])

    latencies = []
    benchmark_start = now_iso()
    benchmark_start_ms = time.time() * 1000

    def on_event(event):
        append_error_event({"label": label, **event})

    client = create_client(api_key, on_event=on_event)

    domain_reports = []
    all_entries = []

    for entry in domains:
        domain = entry["domain"]
        try:
            result = fetch_domain_reviews(domain, client, latencies, requests_dir, results_dir, max_pages)
            valid_entries = [e for e in result["collected"] if is_valid_review(e["raw"])]
            missing_tally = {}
            for e in result["collected"]:
                for f in missing_fields_for(e["raw"]):
                    missing_tally[f] = missing_tally.get(f, 0) + 1
            all_entries.extend(valid_entries)
            domain_reports.append({
                "domain": domain,
                "business_name": entry.get("business_name"),
                "pages_fetched": len(result["pages"]),
                "pagination_detail": result["pages"],
                "stop_reason": result["stopReason"],
                "raw_items": len(result["collected"]),
                "valid_items": len(valid_entries),
                "missing_field_counts": missing_tally,
            })
        except AuthOrQuotaError as err:
            ERRORS_DIR.mkdir(parents=True, exist_ok=True)
            write_json(ERRORS_DIR / "BLOCKER-auth-or-quota.json", {"domain": domain, "message": str(err), "status": err.status, "body": err.body})
            print(f"BLOCKER: authentication/quota failure on {domain}: {err}", file=sys.stderr)
            sys.exit(2)

    dedupe_result = dedupe(all_entries)
    unique = dedupe_result["unique"]
    duplicates = dedupe_result["duplicates"]

    unique_by_domain = {}
    for e in unique:
        unique_by_domain[e["domain"]] = unique_by_domain.get(e["domain"], 0) + 1
    for report in domain_reports:
        report["unique_valid_reviews"] = unique_by_domain.get(report["domain"], 0)
        report["shortfall"] = max(0, TARGET_PER_DOMAIN - report["unique_valid_reviews"])

    total_raw = sum(r.get("raw_items", 0) for r in domain_reports)
    total_valid = sum(r.get("valid_items", 0) for r in domain_reports)
    total_unique = len(unique)
    total_requests = len(latencies)

    benchmark_end = now_iso()
    benchmark_end_ms = time.time() * 1000
    latency_values = sorted(l["ms"] for l in latencies if isinstance(l.get("ms"), (int, float)))
    median = latency_values[len(latency_values) // 2] if latency_values else None
    p95 = latency_values[min(len(latency_values) - 1, int(len(latency_values) * 0.95))] if latency_values else None

    write_json(out_dir / "timings.json", {
        "benchmark_start": benchmark_start,
        "benchmark_end": benchmark_end,
        "wall_clock_ms": int(benchmark_end_ms - benchmark_start_ms),
        "per_request": latencies,
        "median_latency_ms": median,
        "p95_latency_ms": p95,
    })

    flat_reviews = []
    for e in unique:
        raw = e["raw"]
        flat_reviews.append({
            "domain": e["domain"],
            "dedupe_key": e.get("dedupeKey"),
            "dedupe_key_type": e.get("dedupeKeyType"),
            "review_id": raw.get("review_id"),
            "review_rating": raw.get("review_rating"),
            "review_time": raw.get("review_time"),
            "review_experienced_time": raw.get("review_experienced_time"),
            "review_title": raw.get("review_title"),
            "review_text": raw.get("review_text"),
            "review_is_verified": raw.get("review_is_verified"),
            "review_likes": raw.get("review_likes"),
            "consumer_name": raw.get("consumer_name"),
            "consumer_id": raw.get("consumer_id"),
            "consumer_country": raw.get("consumer_country"),
            "consumer_review_count": raw.get("consumer_review_count"),
            "consumer_is_verified": raw.get("consumer_is_verified"),
            "reply_text": raw.get("reply_text"),
        })

    write_json(out_dir / "all-reviews.json", flat_reviews)
    columns = ["domain", "dedupe_key", "dedupe_key_type", "review_id", "review_rating", "review_time", "review_experienced_time", "review_title", "review_text", "review_is_verified", "review_likes", "consumer_name", "consumer_id", "consumer_country", "consumer_review_count", "consumer_is_verified", "reply_text"]
    write_text(out_dir / "all-reviews.csv", to_csv(flat_reviews, columns))

    by_domain = {}
    for d in duplicates:
        by_domain[d["domain"]] = by_domain.get(d["domain"], 0) + 1
    by_key_type = {}
    for d in duplicates:
        by_key_type[d["keyType"]] = by_key_type.get(d["keyType"], 0) + 1

    write_json(out_dir / "duplicate-report.json", {
        "total_duplicates": len(duplicates),
        "by_domain": by_domain,
        "by_key_type": by_key_type,
        "entries": duplicates,
    })

    write_json(out_dir / "pagination-report.json", [
        {"domain": r["domain"], "pages_fetched": r["pages_fetched"], "pagination_detail": r["pagination_detail"], "stop_reason": r["stop_reason"]}
        for r in domain_reports
    ])

    totals = {
        "requested_reviews": TARGET_TOTAL,
        "total_raw_records": total_raw,
        "valid_records": total_valid,
        "unique_valid_reviews": total_unique,
        "duplicate_records": len(duplicates),
        "domains_with_shortfall": [r["domain"] for r in domain_reports if r["shortfall"] > 0],
        "overall_success_rate_percent": to_fixed_number((total_unique / TARGET_TOTAL) * 100, 2),
        "total_requests_made": total_requests,
        "outcome": "completed" if (total_unique == TARGET_TOTAL and all(r["shortfall"] == 0 for r in domain_reports)) else "partial",
    }

    write_json(out_dir / "domain-summary.json", {"generated_at": now_iso(), "label": label, "totals": totals, "domains": domain_reports})
    write_json(out_dir / "run-state.json", {
        "generated_at": now_iso(),
        "label": label,
        "total_requests_made": total_requests,
        "domains": [{"domain": r["domain"], "stop_reason": r["stop_reason"], "pages_fetched": r["pages_fetched"]} for r in domain_reports],
    })

    write_json(out_dir / "cost-report.json", {
        "generated_at": now_iso(),
        "total_requests_made": total_requests,
        "note": (
            "OpenWeb Ninja has no documented account/usage/quota API endpoint, so remaining quota and measured $ "
            "cost cannot be verified programmatically. total_requests_made is the only directly measured usage "
            "figure from this run; converting it to a dollar cost requires the account's active plan (see "
            "docs/openwebninja/openwebninja-pricing.md rate card) and dashboard quota evidence, both Pending "
            "manual confirmation."
        ),
        "estimated_cost_by_plan": {
            "free_marginal_usd": 0,
            "pro_allocated_usd": to_fixed_number(total_requests * 0.0025, 4),
            "ultra_allocated_usd": to_fixed_number(total_requests * 0.0015, 4),
            "mega_allocated_usd": to_fixed_number(total_requests * 0.00075, 4),
            "pay_as_you_go_usd": to_fixed_number(total_requests * 0.005, 4),
        },
        "measured_cost_usd": None,
    })

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
        "base_url": "https://api.openwebninja.com/trustpilot-company-and-reviews",
        "endpoint": "GET /company-reviews",
        "auth_header": "x-api-key: <OPENWEBNINJA_API_KEY> (value never logged)",
        "params_per_request": {"company_domain": "<domain>", "page": "1..10", "sort": "recency"},
        "reviews_per_page": REVIEWS_PER_PAGE,
        "max_pages_without_cookie": MAX_PAGES_WITHOUT_COOKIE,
        "domains": [{"business_name": d.get("business_name"), "domain": d.get("domain"), "target_reviews": d.get("target_reviews")} for d in domains],
        "expected_requests": len(domains) * MAX_PAGES_WITHOUT_COOKIE,
        "quota_check": f"No API quota endpoint exists (confirmed - not in the documented endpoint list). 'run' mode requires OPENWEBNINJA_QUOTA_REMAINING (from the dashboard) >= {MIN_QUOTA_REQUIRED}.",
        "estimated_cost": {"free_marginal_usd": 0, "pro_allocated_usd": 0.125, "ultra_allocated_usd": 0.075, "mega_allocated_usd": 0.0375, "pay_as_you_go_usd": 0.25, "note": "for 50 requests, from docs/openwebninja/openwebninja-pricing.md rate card"},
    }
    write_json(OUT_DIR / "execution-plan.json", plan)
    print(json.dumps(plan, indent=2, ensure_ascii=False))


def run_preflight():
    # Network-free by design: the ONLY documented endpoints are metered
    # (company-reviews, company-search), so there is no way to "preflight"
    # against the live API without consuming quota. This mode instead does
    # exhaustive local validation and prints the exact request plan.
    domains = load_domains()
    load_api_key()
    ensure_dirs([OUT_DIR, REQUESTS_DIR, RESULTS_DIR, ERRORS_DIR])

    gt_path = ROOT / "DATA" / "ground-truth" / "thepearlsource-sample.json"
    requests_that_will_be_made = [
        f"GET /company-reviews?company_domain={d['domain']}&page={i + 1}&sort=recency"
        for d in domains
        for i in range(MAX_PAGES_WITHOUT_COOKIE)
    ]
    report = {
        "generated_at": now_iso(),
        "domains_valid": len(domains) == 5,
        "ground_truth_file_present": gt_path.exists(),
        "requests_that_will_be_made": requests_that_will_be_made,
        "total_requests_planned": len(domains) * MAX_PAGES_WITHOUT_COOKIE,
        "quota_endpoint_exists": False,
        "quota_verification_method": "manual - OPENWEBNINJA_QUOTA_REMAINING env var, checked against dashboard at app.openwebninja.com before `run`",
        "min_quota_required": MIN_QUOTA_REQUIRED,
        "zero_network_calls_made": True,
    }
    write_json(OUT_DIR / "preflight-report.json", report)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return report


def run_smoke():
    if os.environ.get("CONFIRM_SMOKE_RUN") != "yes":
        print("Refusing to run: set CONFIRM_SMOKE_RUN=yes to confirm the smoke test (1 real request).", file=sys.stderr)
        sys.exit(1)
    smoke_requests_dir = SMOKE_DIR / "raw" / "requests"
    smoke_results_dir = SMOKE_DIR / "raw" / "results"
    run_benchmark(
        domains=[{"domain": "www.thepearlsource.com", "business_name": "The Pearl Source", "target_reviews": 20}],
        requests_dir=smoke_requests_dir,
        results_dir=smoke_results_dir,
        out_dir=SMOKE_DIR,
        label="smoke",
        max_pages=1,
    )


def run_full():
    if os.environ.get("CONFIRM_PAID_RUN") != "yes":
        print("Refusing to run: set CONFIRM_PAID_RUN=yes to confirm you approve creating paid OpenWeb Ninja requests.", file=sys.stderr)
        sys.exit(1)

    quota_remaining_raw = os.environ.get("OPENWEBNINJA_QUOTA_REMAINING")
    quota_remaining = None
    if quota_remaining_raw:
        try:
            quota_remaining = float(quota_remaining_raw)
        except ValueError:
            quota_remaining = None

    if not quota_remaining_raw or quota_remaining is None:
        print(
            "Refusing to run: no API quota endpoint exists for OpenWeb Ninja, so remaining quota cannot be checked automatically. "
            f"Check app.openwebninja.com and set OPENWEBNINJA_QUOTA_REMAINING=<number> (>= {MIN_QUOTA_REQUIRED}) to proceed.",
            file=sys.stderr,
        )
        sys.exit(1)

    if quota_remaining < MIN_QUOTA_REQUIRED:
        print(f"Refusing to run: OPENWEBNINJA_QUOTA_REMAINING={js_num_str(quota_remaining)} is below the safe minimum of {MIN_QUOTA_REQUIRED}.", file=sys.stderr)
        sys.exit(1)

    domains = load_domains()
    run_benchmark(domains=domains, requests_dir=REQUESTS_DIR, results_dir=RESULTS_DIR, out_dir=OUT_DIR, label="full", max_pages=MAX_PAGES_WITHOUT_COOKIE)


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
        print("Usage: python openwebninja_benchmark.py <plan|preflight|smoke|run>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        raise
    except Exception as err:  # noqa: BLE001 - mirrors the JS script's top-level catch
        print(f"FATAL: {err}", file=sys.stderr)
        sys.exit(1)
