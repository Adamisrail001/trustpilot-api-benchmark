"""DataForSEO Trustpilot Reviews benchmark script.

Ported to Python from scripts/dataforseo-benchmark.js (which was itself
ported into this project from the "trustpilot review" source project - no
scripts/ folder existed for DataForSEO in this project's other, more mature
source, "trustpilot-api-benchmark," at all). RECONSTRUCTED, not the original
script - no scripts/ folder existed anywhere in either audited source
project when this benchmark's raw outputs were produced. This script is
built to reproduce the exact request shape confirmed in
data/raw/dataforseo/task-post/*.json and data/raw/dataforseo/task-get/*.json:
  - POST /v3/business_data/trustpilot/reviews/task_post
    body per task: { target: domain, depth: 200, sort_by: "recency", priority: 1 }
  - GET  /v3/business_data/trustpilot/reviews/task_get/{id}

UNVERIFIED IN THIS PROJECT: DataForSEO's auth mechanism. DataForSEO's public
documentation (see api_docs_mcps.txt, sections 3-4) describes HTTP Basic
Auth with a login/password pair, which is what this script implements.
Verify against your current DataForSEO account docs before relying on this.

Unlike the other 4 providers' Python scripts in this project, this one was
NOT rebuilt against the actual raw task-post/task-get capture shape on disk
in a per-domain, resumable way - it produces a single combined JSON, not the
domain-summary/duplicate-report/cost-report analysis outputs the other 4
providers produce. See MISSING_AND_GAPS.md for what a full parity rewrite
would need to add.

Usage:
  1. Copy .env.example to .env at the project root, fill in DATAFORSEO_LOGIN
     and DATAFORSEO_PASSWORD with your own credentials.
  2. python scripts/dataforseo_benchmark.py
  3. Output written to outputs/dataforseo/dataforseo-results.json
"""
import base64
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from lib.env import load_env, require_env
from lib.domains import DOMAINS, TARGET_REVIEWS_PER_BUSINESS, sleep

load_env()

BASE_URL = "https://api.dataforseo.com/v3/business_data/trustpilot/reviews"
SCRIPT_DIR = Path(__file__).resolve().parent


def auth_header():
    login = require_env("DATAFORSEO_LOGIN")
    password = require_env("DATAFORSEO_PASSWORD")
    token = base64.b64encode(f"{login}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _request(method, url, body=None):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Authorization", auth_header())
    if data is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urllib.request.urlopen(req) as res:
            return json.loads(res.read().decode("utf-8"))
    except urllib.error.HTTPError as err:
        return json.loads(err.read().decode("utf-8"))


def post_task(domain):
    body = [
        {
            "target": domain,
            "depth": TARGET_REVIEWS_PER_BUSINESS,
            "sort_by": "recency",
            "priority": 1,
            "tag": f"benchmark-{domain}-{int(time.time() * 1000)}",
        }
    ]
    result = _request("POST", f"{BASE_URL}/task_post", body)
    tasks = result.get("tasks") or []
    task_id = tasks[0].get("id") if tasks else None
    if not task_id:
        raise RuntimeError(f"No task id returned for {domain}: {json.dumps(result)}")
    return {"domain": domain, "taskId": task_id, "postResponse": result}


def get_task(task_id):
    return _request("GET", f"{BASE_URL}/task_get/{task_id}")


def poll_until_ready(task_id, max_attempts=20, delay_seconds=5):
    for _attempt in range(1, max_attempts + 1):
        result = get_task(task_id)
        tasks = result.get("tasks") or []
        task_result = tasks[0].get("result") if tasks else None
        if task_result:
            return result
        sleep(delay_seconds)
    raise RuntimeError(f"Task {task_id} did not become ready after {max_attempts} polls")


def main():
    results = []
    for domain in DOMAINS:
        print(f"[submit] {domain}")
        submitted = post_task(domain)
        task_id = submitted["taskId"]
        print(f"[poll]   {domain} -> task {task_id}")
        get_response = poll_until_ready(task_id)
        tasks = get_response.get("tasks") or []
        task_result = tasks[0].get("result") if tasks else None
        items = (task_result[0].get("items") if task_result else None) or []
        print(f"[done]   {domain}: {len(items)} reviews")
        results.append(
            {
                "domain": domain,
                "taskId": task_id,
                "itemCount": len(items),
                "items": items,
                "postResponse": submitted["postResponse"],
                "getResponse": get_response,
            }
        )

    out_dir = SCRIPT_DIR.parent / "outputs" / "dataforseo"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "dataforseo-results.json"
    with open(out_path, "w", encoding="utf-8", newline="") as f:
        f.write(json.dumps(results, indent=2, ensure_ascii=False))
    print(f"\nWrote {out_path}")


if __name__ == "__main__":
    try:
        main()
    except Exception as err:  # noqa: BLE001 - mirrors the JS script's top-level catch
        print(err)
        raise SystemExit(1)
