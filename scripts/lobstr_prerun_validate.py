"""Ported 1:1 from scripts/lobstr-prerun-validate.js.

One-off, read-only pre-run validation. Makes no Run. Never prints
credential values.
"""
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

from lib.lobstr_client import create_client

ROOT = Path(__file__).resolve().parent.parent
CLEAN_SQUID = "8d9e0b80d6d2481283c138104caf022d"
CONTAMINATED_SQUID = "5644e83e28ce412c9370da2bc46fcd31"


def get_env_var(name):
    for line in re.split(r"\r?\n", (ROOT / ".env").read_text(encoding="utf-8")):
        t = line.strip()
        if not t or t.startswith("#"):
            continue
        idx = t.find("=")
        if idx == -1:
            continue
        if t[:idx].strip() == name:
            return t[idx + 1 :].strip() or None
    return None


def main():
    results = {}
    api_key = get_env_var("LOBSTR_API_KEY")
    squid_id = get_env_var("LOBSTR_SQUID_ID")
    crawler_id = get_env_var("LOBSTR_CRAWLER_ID")
    domains = json.loads((ROOT / "benchmark-domains.json").read_text(encoding="utf-8"))

    results["1_LOBSTR_API_KEY_exists"] = bool(api_key)
    results["2_LOBSTR_SQUID_ID_exists"] = bool(squid_id)
    results["3_squid_equals_clean"] = squid_id == CLEAN_SQUID
    results["4_squid_not_contaminated"] = squid_id != CONTAMINATED_SQUID

    client = create_client({"apiKey": api_key})

    squid_res = client["getSquidDetails"](squid_id)
    squid_json = squid_res.get("json") or {}
    results["5_squid_uses_trustpilot_crawler"] = bool(
        squid_res["ok"] and squid_json.get("crawler") == crawler_id and re.search("trustpilot", squid_json.get("crawler_name") or "", re.I)
    )
    results["squid_crawler_name"] = squid_json.get("crawler_name")
    results["squid_params_current"] = squid_json.get("params")
    results["squid_total_runs"] = squid_json.get("total_runs")
    results["squid_last_run_status"] = squid_json.get("last_run_status")
    results["squid_last_run_id"] = squid_json.get("last_run")

    tasks_res = client["listTasks"](squid=squid_id, page=1, limit=100)
    tasks = (tasks_res.get("json") or {}).get("data") or []
    task_urls = [(t.get("params") or {}).get("url") for t in tasks]
    expected_urls = [f"https://www.trustpilot.com/review/{d['domain']}" for d in domains]
    results["6_exactly_five_approved_domains_configured"] = len(tasks) == 5 and all(u in task_urls for u in expected_urls)
    results["tasks_count_live"] = len(tasks)
    results["task_urls_live"] = task_urls
    results["7_no_unrelated_domains"] = all(u in expected_urls for u in task_urls)
    results["8_happen_com_absent"] = not any("happen.com" in (u or "") for u in task_urls)
    results["9_target_200_per_domain"] = all(d.get("target_reviews") == 200 for d in domains)
    # JS: `squidRes.json?.params && typeof ...max_unique_results_per_run === 'number'`
    # - an empty-but-present params object is still truthy in JS, so check
    # `is not None` rather than Python truthiness; also exclude bool (a subclass
    # of int in Python but not typeof 'number' in JS) from the numeric check.
    params = squid_json.get("params")
    max_unique = params.get("max_unique_results_per_run") if isinstance(params, dict) else None
    is_number = isinstance(max_unique, (int, float)) and not isinstance(max_unique, bool)
    if params is not None and is_number:
        results["10_can_store_at_least_1000"] = max_unique >= 1000
    else:
        results["10_can_store_at_least_1000"] = "pending_configuration_this_run"

    local_run_file = ROOT / "outputs" / "lobstr" / "raw" / "requests" / "run.json"
    results["11_no_existing_run_id_in_local_state"] = not local_run_file.exists()

    runs_res = client["listRuns"](squid=squid_id, page=1, limit=10)
    runs = (runs_res.get("json") or {}).get("data") or []
    results["runs_on_squid_live"] = [{"id": r.get("id"), "status": r.get("status"), "created_at": r.get("created_at")} for r in runs]
    results["12_previous_failed_attempt_created_zero_runs"] = (
        "consistent_with_squid_total_runs_field" if len(runs) == (results.get("squid_total_runs") or 0) else "mismatch_investigate"
    )

    out_dir = ROOT / "outputs" / "lobstr" / "raw" / "requests"
    out_dir.mkdir(parents=True, exist_ok=True)
    dt = datetime.now(timezone.utc)
    checked_at = dt.strftime("%Y-%m-%dT%H:%M:%S.") + f"{dt.microsecond // 1000:03d}Z"
    (out_dir / "prerun-validation.json").write_text(
        json.dumps(
            {
                "checked_at": checked_at,
                "results": results,
                "raw_squid_response": squid_res.get("json"),
                "raw_tasks_response": tasks_res.get("json"),
                "raw_runs_response": runs_res.get("json"),
            },
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
        newline="",  # avoid Python translating "\n" to os.linesep on Windows
    )

    print(json.dumps(results, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"VALIDATION FAILED: {e}", file=sys.stderr)
        sys.exit(1)
