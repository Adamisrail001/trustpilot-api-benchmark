"""Ported 1:1 from scripts/lib/outscraper-client.js.

Outscraper API client for the Trustpilot Reviews endpoint.

Source of every fact baked in here: docs/outscraper-documentation.md
(fetched/confirmed against https://docs.outscraper.com/endpoints/trustpilot-reviews/
and https://docs.outscraper.com/endpoints/requests-requestid/). Nothing
below is guessed - where the docs didn't state something (e.g. an
exact polling SLA), the caller controls it via options instead of
this file inventing a number.

stdlib-only: uses urllib instead of the JS version's fetch(). Unlike fetch(),
urllib.request.urlopen() raises urllib.error.HTTPError for 4xx/5xx responses
instead of returning a non-ok response, so _do_request() catches that and
normalizes it back into the (status, text, ok) shape fetch() would have
given the JS version.
"""
import json
import time
import urllib.error
import urllib.request
from urllib.parse import urlencode

BASE_URL = "https://api.outscraper.com"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_BACKOFF_MS = 1000


class AuthOrBillingError(Exception):
    """Raised on HTTP 401 (auth) or 402 (billing). Never retried."""

    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


class InvalidParametersError(Exception):
    """Raised on HTTP 422 (invalid/unsupported query parameters). Never retried."""

    def __init__(self, message, status=None, body=None):
        super().__init__(message)
        self.status = status
        self.body = body


def _safe_parse(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return {"raw_unparsed_length": len(text)}


def _js_bool_str(value):
    # Mirrors JS `String(x)` for the one boolean-valued query param this
    # client builds ("async"): JS lowercases true/false, Python's str()
    # would otherwise produce "True"/"False".
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


class _OutscraperClient:
    """The X-API-KEY header is built once in the constructor and never
    exposed via any method, log line, or saved file."""

    def __init__(self, api_key, on_event=None):
        if not api_key:
            raise ValueError("Outscraper API key missing.")
        self._headers = {"X-API-KEY": api_key}
        self._on_event = on_event

    def _emit(self, event):
        if callable(self._on_event):
            self._on_event(event)

    def _do_request(self, url):
        """Returns (status, text, ok) - ok mirrors fetch()'s res.ok
        (true for 2xx), matching JS's non-throwing-on-HTTP-error fetch."""
        req = urllib.request.Request(url, method="GET", headers=self._headers)
        try:
            with urllib.request.urlopen(req, timeout=120) as res:
                status = res.getcode()
                text = res.read().decode("utf-8", errors="replace")
                return status, text, True
        except urllib.error.HTTPError as err:
            status = err.code
            try:
                text = err.read().decode("utf-8", errors="replace")
            except Exception:
                text = ""
            return status, text, False

    def _get_with_retry(self, url, context=None):
        attempt = 0
        last_error = None

        while attempt <= MAX_RETRIES:
            attempt += 1
            started_at = time.monotonic()
            try:
                status, text, ok = self._do_request(url)
                latency_ms = int(round((time.monotonic() - started_at) * 1000))

                # 401 - missing/invalid API key: stop the benchmark, never retry.
                if status == 401:
                    self._emit(
                        {"type": "auth_failure", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms}
                    )
                    raise AuthOrBillingError("Authentication failed (HTTP 401)", status, _safe_parse(text))

                # 402 - billing/payment/invoice problem: stop paid execution, never retry.
                if status == 402:
                    self._emit(
                        {"type": "billing_failure", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms}
                    )
                    raise AuthOrBillingError("Billing failure (HTTP 402)", status, _safe_parse(text))

                # 422 - invalid/unsupported query parameters: inspect, never retry blindly.
                if status == 422:
                    self._emit(
                        {
                            "type": "invalid_parameters",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                            "body": _safe_parse(text),
                        }
                    )
                    raise InvalidParametersError("Invalid or unsupported parameters (HTTP 422)", status, _safe_parse(text))

                if status in RETRYABLE_STATUS and attempt <= MAX_RETRIES:
                    self._emit(
                        {
                            "type": "rate_limited" if status == 429 else "retryable_http_error",
                            "context": context,
                            "status": status,
                            "attempt": attempt,
                            "latencyMs": latency_ms,
                            "body": _safe_parse(text),
                        }
                    )
                    time.sleep(BASE_BACKOFF_MS * (2 ** (attempt - 1)) / 1000.0)
                    continue

                json_body = _safe_parse(text)

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
                    return {"ok": False, "status": status, "json": json_body, "latency_ms": latency_ms, "attempts": attempt}

                return {"ok": True, "status": status, "json": json_body, "latency_ms": latency_ms, "attempts": attempt}

            except (AuthOrBillingError, InvalidParametersError):
                raise
            except Exception as err:  # noqa: BLE001 - mirrors the JS catch-all network error path
                last_error = err
                latency_ms = int(round((time.monotonic() - started_at) * 1000))
                self._emit(
                    {"type": "network_error", "context": context, "attempt": attempt, "latencyMs": latency_ms, "message": str(err)}
                )
                if attempt <= MAX_RETRIES:
                    time.sleep(BASE_BACKOFF_MS * (2 ** (attempt - 1)) / 1000.0)
                    continue

        return {
            "ok": False,
            "status": None,
            "json": None,
            "latency_ms": None,
            "attempts": attempt,
            "error": str(last_error) if last_error else "unknown_error",
        }

    def submit_trustpilot_reviews_request(self, query, limit=None, skip=None, languages=None, sort=None, async_=None, fields=None):
        """Submits one Trustpilot Reviews scraping request.
        query: list of domains/URLs (batching multiple is documented, but
               this benchmark submits one domain per call so each domain's
               evidence/pagination stays independent)."""
        if not isinstance(query, list) or len(query) == 0:
            raise ValueError("query must be a non-empty array of domains/URLs.")
        params = []
        for q in query:
            params.append(("query", q))
        if limit is not None:
            params.append(("limit", str(limit)))
        if skip is not None:
            params.append(("skip", str(skip)))
        if languages is not None:
            params.append(("languages", languages))
        if sort is not None:
            params.append(("sort", sort))
        if fields is not None:
            params.append(("fields", fields))
        async_value = True if async_ is None else async_
        params.append(("async", _js_bool_str(async_value)))

        url = f"{BASE_URL}/trustpilot-reviews?{urlencode(params)}"
        result = self._get_with_retry(url, context="submit")
        result["request_url"] = url
        return result

    def poll_results_location(self, results_location):
        """Polls the EXACT results_location URL returned by the submit call.
        Per docs/outscraper-documentation.md, this must never be
        reconstructed - the host/path can legitimately differ from
        BASE_URL (docs show api.outscraper.cloud for results)."""
        if not results_location:
            raise ValueError("resultsLocation is required to poll.")
        return self._get_with_retry(results_location, context="poll")


def create_client(api_key, on_event=None):
    return _OutscraperClient(api_key, on_event=on_event)
