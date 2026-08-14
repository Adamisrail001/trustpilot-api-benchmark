"""Ported 1:1 from scripts/lib/apify-client.js.

Apify API client for running the automation-lab/trustpilot Actor.

Every fact below is confirmed against docs/apify/apify-documentation.md
and docs/apify/apify-pricing.md (user-provided, citing official Apify
docs at docs.apify.com/api/v2 and the Actor's own store page).

Confirmed:
  Base URL: https://api.apify.com/v2
  Auth:     "Authorization: Bearer <token>"
  Start run: POST /v2/acts/{restActorId}/runs   (restActorId uses '~', e.g. automation-lab~trustpilot)
  Get run:   GET  /v2/actor-runs/{runId}
  Dataset:   GET  /v2/datasets/{datasetId}/items?format=json&clean=true&offset=&limit=
    - response body is a bare JSON array (not wrapped)
    - pagination info comes back in headers: X-Apify-Pagination-Offset/Limit/Count/Total
  Terminal run statuses: SUCCEEDED, FAILED, ABORTED, TIMED-OUT
  Non-terminal: READY, RUNNING

Uses only urllib (stdlib) for HTTP - no third-party dependencies, matching
this project's zero-npm-dependency design for the original JS.
"""
import json
import time
import urllib.error
import urllib.request

BASE_URL = "https://api.apify.com/v2"
RETRYABLE_STATUS = {429, 500, 501, 502, 503, 504}
MAX_RETRIES = 3
BASE_BACKOFF_S = 1.0  # 1000ms, same as JS's BASE_BACKOFF_MS


class AuthOrBillingError(Exception):
    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "AuthOrBillingError"
        self.status = status
        self.body = body


class InvalidRequestError(Exception):
    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "InvalidRequestError"
        self.status = status
        self.body = body


def _sleep(seconds):
    time.sleep(seconds)


def _safe_parse_json(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return {"raw_unparsed_length": len(text)}


def _now_ms():
    return time.time() * 1000.0


def _elapsed_ms(started_at):
    """Whole-millisecond elapsed time, mirroring JS's `Date.now() - startedAt`
    (Date.now() is already integer ms, so JS latencies are always whole
    numbers; time.time() is float, so we round here to match)."""
    return int(round(_now_ms() - started_at))


def _number_or_none(headers, name):
    """Mirrors `r.headers ? Number(r.headers.get(name)) : null` from the JS.

    Number(null) === 0 in JS (i.e. a present headers object but a missing
    individual header still yields 0, not null/NaN)."""
    if headers is None:
        return None
    value = headers.get(name)
    if value is None:
        return 0
    try:
        if isinstance(value, str) and ("." in value or "e" in value.lower()):
            return float(value)
        return int(value)
    except (TypeError, ValueError):
        try:
            return float(value)
        except (TypeError, ValueError):
            return float("nan")


class ApifyClient:
    """
    The "Authorization: Bearer <token>" header is built once in the
    constructor and never exposed on the returned object, in logs, or in
    any saved file.
    """

    def __init__(self, api_token, on_event=None):
        if not api_token:
            raise ValueError("Apify API token missing.")
        self._headers = {"Authorization": f"Bearer {api_token}"}
        self._on_event = on_event

    def _emit(self, event):
        if callable(self._on_event):
            self._on_event(event)

    def _request(self, method, url, body=None, context=None, parse_as_array=False):
        attempt = 0
        last_error = None

        while attempt <= MAX_RETRIES:
            attempt += 1
            started_at = _now_ms()
            try:
                data = json.dumps(body).encode("utf-8") if body is not None else None
                req_headers = dict(self._headers)
                if body is not None:
                    req_headers["Content-Type"] = "application/json"
                req = urllib.request.Request(url, data=data, headers=req_headers, method=method)

                try:
                    with urllib.request.urlopen(req) as res:
                        status = res.status
                        text = res.read().decode("utf-8")
                        resp_headers = res.headers
                except urllib.error.HTTPError as http_err:
                    status = http_err.code
                    text = http_err.read().decode("utf-8")
                    resp_headers = http_err.headers

                latency_ms = _elapsed_ms(started_at)

                if status in (401, 403, 402):
                    self._emit(
                        {
                            "type": "auth_or_billing_failure",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                        }
                    )
                    raise AuthOrBillingError(
                        f"Auth/billing failure (HTTP {status})", status, _safe_parse_json(text)
                    )

                if status in (400, 404):
                    self._emit(
                        {
                            "type": "invalid_request",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                            "body": _safe_parse_json(text),
                        }
                    )
                    raise InvalidRequestError(
                        f"Invalid request (HTTP {status})", status, _safe_parse_json(text)
                    )

                if status in RETRYABLE_STATUS and attempt <= MAX_RETRIES:
                    self._emit(
                        {
                            "type": "rate_limited" if status == 429 else "retryable_http_error",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                            "body": _safe_parse_json(text),
                        }
                    )
                    _sleep(BASE_BACKOFF_S * (2 ** (attempt - 1)))
                    continue

                json_body = _safe_parse_json(text)

                ok = 200 <= status < 300
                if not ok:
                    self._emit(
                        {
                            "type": "non_retryable_http_error",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                            "body": json_body,
                        }
                    )
                    return {
                        "ok": False,
                        "status": status,
                        "json": json_body,
                        "latency_ms": latency_ms,
                        "attempts": attempt,
                        "headers": resp_headers,
                    }

                return {
                    "ok": True,
                    "status": status,
                    "json": json_body,
                    "latency_ms": latency_ms,
                    "attempts": attempt,
                    "headers": resp_headers,
                }

            except (AuthOrBillingError, InvalidRequestError):
                raise
            except Exception as err:  # network error (URLError, timeout, etc.)
                last_error = err
                latency_ms = _elapsed_ms(started_at)
                self._emit(
                    {
                        "type": "network_error",
                        "context": context,
                        "attempt": attempt,
                        "latencyMs": latency_ms,
                        "message": str(err),
                    }
                )
                if attempt <= MAX_RETRIES:
                    _sleep(BASE_BACKOFF_S * (2 ** (attempt - 1)))
                    continue

        return {
            "ok": False,
            "status": None,
            "json": None,
            "latency_ms": None,
            "attempts": attempt,
            "error": str(last_error) if last_error else "unknown_error",
        }

    def start_actor_run(self, rest_actor_id, input_body):
        """POST /v2/acts/{restActorId}/runs - starts exactly one Actor run."""
        url = f"{BASE_URL}/acts/{rest_actor_id}/runs"
        result = self._request("POST", url, input_body, context="start_run")
        result["request_url"] = url
        return result

    def get_run(self, run_id):
        """GET /v2/actor-runs/{runId} - poll the SAME run id, never start another."""
        url = f"{BASE_URL}/actor-runs/{run_id}"
        result = self._request("GET", url, None, context="get_run")
        result["request_url"] = url
        return result

    def get_dataset_items(self, dataset_id, offset=0, limit=1000):
        """GET /v2/datasets/{datasetId}/items - body is a bare array; pagination
        metadata comes back in X-Apify-Pagination-* headers, not the body."""
        url = f"{BASE_URL}/datasets/{dataset_id}/items?format=json&clean=true&offset={offset}&limit={limit}"
        result = self._request("GET", url, None, context="get_dataset_items", parse_as_array=True)
        result["request_url"] = url
        headers = result.get("headers")
        result["pagination_offset"] = _number_or_none(headers, "x-apify-pagination-offset")
        result["pagination_limit"] = _number_or_none(headers, "x-apify-pagination-limit")
        result["pagination_count"] = _number_or_none(headers, "x-apify-pagination-count")
        result["pagination_total"] = _number_or_none(headers, "x-apify-pagination-total")
        return result
