"""Ported 1:1 from scripts/lib/lobstr-client.js.

Lobstr.io API client.

Source of every fact baked in here: docs/lobster/lobstr-documentation.md
(confirmed against live fetches of https://docs.lobstr.io/ during the
original session - base URL, auth header, crawlers/squids/tasks/runs/results
endpoints, pagination shape, rate limits, and run status values).
Nothing below is guessed - where a crawler-specific detail (e.g. the
Trustpilot crawler's exact `params` keys) isn't confirmed, the caller
discovers it live from the API's own responses rather than this file
assuming a shape.

Node's `fetch`-based async retry loop is ported here as a synchronous
`urllib.request`-based loop with `time.sleep` for backoff - same control
flow, same retry count, same backoff formula, just without an event loop.
"""
import json
import math
import time
import urllib.error
import urllib.parse
import urllib.request

BASE_URL = "https://api.lobstr.io/v1"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_BACKOFF_MS = 1000


class AuthOrBillingError(Exception):
    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "AuthOrBillingError"
        self.message = message
        self.status = status
        self.body = body


class InvalidRequestError(Exception):
    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "InvalidRequestError"
        self.message = message
        self.status = status
        self.body = body


def _sleep_ms(ms):
    time.sleep(ms / 1000.0)


def _safe_parse(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return {"raw_unparsed_length": len(text)}


def create_client(config, on_event=None):
    """config: {"apiKey": ...}. on_event: optional callable(event_dict).

    The "Authorization: Token <key>" header is built once in the closure
    and never exposed on the returned object, in logs, or in any saved
    file.
    """
    api_key = config.get("apiKey") if config else None
    if not api_key:
        raise Exception("Lobstr.io API key missing.")
    headers = {
        "Authorization": f"Token {api_key}",
        "Content-Type": "application/json",
    }

    def emit(event):
        if callable(on_event):
            on_event(event)

    def request(method, url, body=None, context=None):
        attempt = 0
        last_error = None
        started_at = None

        while attempt <= MAX_RETRIES:
            attempt += 1
            started_at = time.monotonic()
            try:
                data = json.dumps(body).encode("utf-8") if body is not None else None
                req = urllib.request.Request(url, data=data, method=method, headers=dict(headers))
                try:
                    with urllib.request.urlopen(req) as res:
                        status = res.status
                        response_headers = res.headers
                        raw_body = res.read()
                except urllib.error.HTTPError as http_err:
                    status = http_err.code
                    response_headers = http_err.headers
                    raw_body = http_err.read()

                latency_ms = int((time.monotonic() - started_at) * 1000)
                rate_limit_headers = {
                    "limit": response_headers.get("X-RateLimit-Limit") if response_headers else None,
                    "remaining": response_headers.get("X-RateLimit-Remaining") if response_headers else None,
                    "reset": response_headers.get("X-RateLimit-Reset") if response_headers else None,
                    "retryAfter": response_headers.get("Retry-After") if response_headers else None,
                }

                # 401/403 - auth failure; 402 - billing failure. Never retried.
                if status in (401, 403, 402):
                    text = raw_body.decode("utf-8", errors="replace") if raw_body else ""
                    emit({"type": "auth_or_billing_failure", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms})
                    raise AuthOrBillingError(f"Auth/billing failure (HTTP {status})", status, _safe_parse(text))

                # 400 - invalid request (e.g. duplicate active run, bad squid/crawler id). Never retried blindly.
                if status == 400:
                    text = raw_body.decode("utf-8", errors="replace") if raw_body else ""
                    emit({"type": "invalid_request", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms, "body": _safe_parse(text)})
                    raise InvalidRequestError("Invalid request (HTTP 400)", status, _safe_parse(text))

                if status in RETRYABLE_STATUS and attempt <= MAX_RETRIES:
                    text = raw_body.decode("utf-8", errors="replace") if raw_body else ""
                    emit({
                        "type": "rate_limited" if status == 429 else "retryable_http_error",
                        "context": context,
                        "status": status,
                        "attempt": attempt,
                        "latencyMs": latency_ms,
                        "rateLimitHeaders": rate_limit_headers,
                        "body": _safe_parse(text),
                    })
                    retry_after_ms = None
                    retry_after_raw = rate_limit_headers.get("retryAfter")
                    if retry_after_raw:
                        try:
                            retry_after_ms = float(retry_after_raw) * 1000
                        except (TypeError, ValueError):
                            retry_after_ms = None
                    # Mirrors JS: `retryAfterMs && !Number.isNaN(retryAfterMs) ? retryAfterMs : backoff`
                    # i.e. a falsy (including 0/None) or NaN retry-after falls back to exponential backoff.
                    if retry_after_ms and not math.isnan(retry_after_ms):
                        _sleep_ms(retry_after_ms)
                    else:
                        _sleep_ms(BASE_BACKOFF_MS * (2 ** (attempt - 1)))
                    continue

                text = raw_body.decode("utf-8", errors="replace") if raw_body else ""
                parsed_json = _safe_parse(text)

                ok = 200 <= status < 300
                if not ok:
                    emit({"type": "non_retryable_http_error", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms, "body": parsed_json})
                    return {"ok": False, "status": status, "json": parsed_json, "latencyMs": latency_ms, "attempts": attempt, "rateLimitHeaders": rate_limit_headers}

                return {"ok": True, "status": status, "json": parsed_json, "latencyMs": latency_ms, "attempts": attempt, "rateLimitHeaders": rate_limit_headers}
            except (AuthOrBillingError, InvalidRequestError):
                raise
            except Exception as err:  # network_error equivalent
                last_error = err
                latency_ms = int((time.monotonic() - started_at) * 1000) if started_at else None
                emit({"type": "network_error", "context": context, "attempt": attempt, "latencyMs": latency_ms, "message": str(err)})
                if attempt <= MAX_RETRIES:
                    _sleep_ms(BASE_BACKOFF_MS * (2 ** (attempt - 1)))
                    continue

        return {
            "ok": False,
            "status": None,
            "json": None,
            "latencyMs": None,
            "attempts": attempt,
            "error": str(last_error) if last_error else "unknown_error",
        }

    def list_crawlers(page=1, limit=100):
        return request("GET", f"{BASE_URL}/crawlers?page={page}&limit={limit}", context="list_crawlers")

    def list_squids(name=None, page=1, limit=100):
        params = {"page": str(page), "limit": str(limit)}
        if name:
            params["name"] = name
        return request("GET", f"{BASE_URL}/squids?{urllib.parse.urlencode(params)}", context="list_squids")

    def get_squid_details(squid_id):
        return request("GET", f"{BASE_URL}/squids/{squid_id}", context="get_squid_details")

    def create_squid(crawler, name):
        return request("POST", f"{BASE_URL}/squids", {"crawler": crawler, "name": name}, context="create_squid")

    def update_squid(squid_id, body):
        return request("POST", f"{BASE_URL}/squids/{squid_id}", body, context="update_squid")

    def list_tasks(squid=None, page=1, limit=100):
        params = {"page": str(page), "limit": str(limit)}
        if squid:
            params["squid"] = squid
        return request("GET", f"{BASE_URL}/tasks?{urllib.parse.urlencode(params)}", context="list_tasks")

    def add_tasks(squid, tasks):
        return request("POST", f"{BASE_URL}/tasks", {"squid": squid, "tasks": tasks}, context="add_tasks")

    def list_runs(squid=None, page=1, limit=100):
        params = {"page": str(page), "limit": str(limit)}
        if squid:
            params["squid"] = squid
        return request("GET", f"{BASE_URL}/runs?{urllib.parse.urlencode(params)}", context="list_runs")

    def start_run(squid):
        return request("POST", f"{BASE_URL}/runs", {"squid": squid}, context="start_run")

    def get_run(run_id):
        return request("GET", f"{BASE_URL}/runs/{run_id}", context="get_run")

    def get_results(run=None, squid=None, page=1, page_size=100):
        # `limit` is accepted by the API but does not control page size - it's
        # silently ignored (see data/lobstr/analysis/page_size-parameter-correction.md).
        # `page_size` is the real, working parameter.
        params = {"page": str(page), "page_size": str(page_size)}
        if run:
            params["run"] = run
        if squid and not run:
            params["squid"] = squid
        return request("GET", f"{BASE_URL}/results?{urllib.parse.urlencode(params)}", context="get_results")

    def get_results_by_url(url):
        # For following the exact `next` pagination URL returned by the API.
        return request("GET", url, context="get_results_next")

    def get_balance():
        return request("GET", f"{BASE_URL}/user/balance", context="get_balance")

    return {
        "listCrawlers": list_crawlers,
        "listSquids": list_squids,
        "getSquidDetails": get_squid_details,
        "createSquid": create_squid,
        "updateSquid": update_squid,
        "listTasks": list_tasks,
        "addTasks": add_tasks,
        "listRuns": list_runs,
        "startRun": start_run,
        "getRun": get_run,
        "getResults": get_results,
        "getResultsByUrl": get_results_by_url,
        "getBalance": get_balance,
    }
