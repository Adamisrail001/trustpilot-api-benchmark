"""Ported 1:1 from scripts/lib/openwebninja-client.js.

OpenWeb Ninja API client for the Trustpilot Company Reviews endpoint.

Every fact below is confirmed against the live, rendered official docs
at https://www.openwebninja.com/api/trustpilot-company-and-reviews-data/docs
(a Scalar-rendered OpenAPI reference - fetched via a real browser in the
original research session, since a plain HTTP fetch only returns the page
shell). Nothing here is guessed.

Confirmed:
  Server:  https://api.openwebninja.com/trustpilot-company-and-reviews
  Auth:    header "x-api-key: <key>"
  Reviews: GET /company-reviews?company_domain=<domain>&page=<n>&sort=recency...
  Reviews-per-page: up to 20 (page default 1)
  Pages 1-10 available without a Trustpilot login cookie; page 11+ requires
    a "cookie" param (a logged-in Trustpilot user session) - not used by
    this benchmark since the target is 200/domain (10 pages).
  Response reviews array location: data.reviews[]
  Full documented endpoint list for this API: company-search, company-details,
    company-reviews, category-company-list, category-recently-reviewed-companies,
    category-search, category-details, consumer-details, consumer-reviews.
    NO account/usage/quota endpoint exists anywhere in this list - quota
    is dashboard-only per current documentation (see docs/openwebninja/
    openwebninja-documentation.md "Quota Verification" section).

stdlib-only: uses urllib.request/urllib.error for HTTP (no third-party
dependencies), matching the zero-npm-dependency approach of the original.
"""
import json
import time
import urllib.error
import urllib.parse
import urllib.request
from types import SimpleNamespace

BASE_URL = "https://api.openwebninja.com/trustpilot-company-and-reviews"
RETRYABLE_STATUS = {429, 500, 502, 503, 504}
MAX_RETRIES = 3
BASE_BACKOFF_MS = 1000


class AuthOrQuotaError(Exception):
    """401/403 auth failures and HTTP-200-but-non-OK-status application
    errors (e.g. quota exhaustion surfaced at the application level).
    Never retried."""

    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "AuthOrQuotaError"
        self.status = status
        self.body = body


class InvalidRequestError(Exception):
    """400/404/422 - invalid domain/page/param. Never retried blindly."""

    def __init__(self, message, status, body):
        super().__init__(message)
        self.name = "InvalidRequestError"
        self.status = status
        self.body = body


def _safe_parse(text):
    if not text:
        return None
    try:
        return json.loads(text)
    except (ValueError, TypeError):
        return {"raw_unparsed_length": len(text)}


def _js_str(value):
    """Mirrors JS's String(value) for the one case that matters here:
    booleans stringify as lowercase 'true'/'false', not Python's 'True'/'False'."""
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _perform_get(url, headers):
    """Performs the GET request and returns (status, headers, text)
    regardless of whether the server responded with an HTTP error status.
    Only raises for genuine network-level failures (DNS, connection
    refused, timeout, etc.) - mirroring fetch()'s behavior of resolving
    (not rejecting) on HTTP error statuses."""
    req = urllib.request.Request(url, method="GET", headers=headers)
    try:
        with urllib.request.urlopen(req) as res:
            body = res.read()
            text = body.decode("utf-8", errors="replace") if body else ""
            return res.status, res.headers, text
    except urllib.error.HTTPError as err:
        body = err.read()
        text = body.decode("utf-8", errors="replace") if body else ""
        return err.code, err.headers, text


def create_client(api_key, on_event=None):
    """The x-api-key header is built once in the closure and never exposed
    on the returned object, in logs, or in any saved file."""
    if not api_key:
        raise ValueError("OpenWeb Ninja API key missing.")
    headers = {"x-api-key": api_key}

    def emit(event):
        if callable(on_event):
            on_event(event)

    def get_with_retry(url, context=None):
        attempt = 0
        last_error = None

        while attempt <= MAX_RETRIES:
            attempt += 1
            started_at = time.monotonic()
            try:
                status, resp_headers, text = _perform_get(url, headers)
                latency_ms = int((time.monotonic() - started_at) * 1000)
                rate_limit_headers = {
                    "limit": resp_headers.get("X-RateLimit-Limit") or resp_headers.get("RateLimit-Limit"),
                    "remaining": resp_headers.get("X-RateLimit-Remaining") or resp_headers.get("RateLimit-Remaining"),
                    "retryAfter": resp_headers.get("Retry-After"),
                }

                # 401/403 - auth failure. Never retried.
                if status in (401, 403):
                    emit({"type": "auth_failure", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms})
                    raise AuthOrQuotaError(f"Authentication failure (HTTP {status})", status, _safe_parse(text))

                # 400/404/422 - invalid domain/page/param. Never retried blindly.
                if status in (400, 404, 422):
                    emit({"type": "invalid_request", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms, "body": _safe_parse(text)})
                    raise InvalidRequestError(f"Invalid request (HTTP {status})", status, _safe_parse(text))

                if status in RETRYABLE_STATUS and attempt <= MAX_RETRIES:
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
                        except ValueError:
                            retry_after_ms = None
                    sleep_ms = retry_after_ms if retry_after_ms is not None else BASE_BACKOFF_MS * (2 ** (attempt - 1))
                    time.sleep(sleep_ms / 1000)
                    continue

                json_body = _safe_parse(text)
                ok = 200 <= status < 300

                if not ok:
                    emit({"type": "non_retryable_http_error", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms, "body": json_body})
                    return {"ok": False, "status": status, "json": json_body, "latencyMs": latency_ms, "attempts": attempt, "rateLimitHeaders": rate_limit_headers}

                # The API can return HTTP 200 with a non-"OK" status field (e.g. quota
                # exhaustion or an application-level error) - surface this distinctly
                # so the caller never mistakes it for a successful page of reviews.
                if isinstance(json_body, dict) and isinstance(json_body.get("status"), str) and json_body.get("status") != "OK":
                    emit({"type": "application_error_status", "context": context, "status": status, "attempt": attempt, "latencyMs": latency_ms, "body": json_body})
                    raise AuthOrQuotaError(f"API returned non-OK status: {json_body.get('status')}", status, json_body)

                return {"ok": True, "status": status, "json": json_body, "latencyMs": latency_ms, "attempts": attempt, "rateLimitHeaders": rate_limit_headers}

            except (AuthOrQuotaError, InvalidRequestError):
                raise
            except Exception as err:  # noqa: BLE001 - mirrors JS's catch(err) + instanceof re-throw
                last_error = err
                latency_ms = int((time.monotonic() - started_at) * 1000)
                emit({"type": "network_error", "context": context, "attempt": attempt, "latencyMs": latency_ms, "message": str(err)})
                if attempt <= MAX_RETRIES:
                    time.sleep((BASE_BACKOFF_MS * (2 ** (attempt - 1))) / 1000)
                    continue

        return {"ok": False, "status": None, "json": None, "latencyMs": None, "attempts": attempt, "error": str(last_error) if last_error else "unknown_error"}

    def get_company_reviews(company_domain, page=1, sort="recency", cookie=None, verified=None, with_replies=None, date_posted=None, rating=None, locale=None):
        """GET /company-reviews - the only endpoint this benchmark uses.
        company_domain is required; page defaults to 1 (up to 20 results).
        sort='recency' matches the shared benchmark's "Most recent" requirement."""
        params = [("company_domain", company_domain), ("page", str(page))]
        if sort is not None:
            params.append(("sort", sort))
        if cookie is not None:
            params.append(("cookie", cookie))
        if verified is not None:
            params.append(("verified", _js_str(verified)))
        if with_replies is not None:
            params.append(("with_replies", _js_str(with_replies)))
        if date_posted is not None:
            params.append(("date_posted", date_posted))
        if rating is not None:
            params.append(("rating", rating))
        if locale is not None:
            params.append(("locale", locale))

        url = f"{BASE_URL}/company-reviews?{urllib.parse.urlencode(params)}"
        result = get_with_retry(url, context="company-reviews")
        result["requestUrl"] = url
        return result

    def company_search(query, page=1, locale=None):
        """GET /company-search - only used if a domain needs disambiguation
        (not required for company-reviews, which accepts company_domain
        directly). Unused by this benchmark; ported for parity with the JS client."""
        params = [("query", query), ("page", str(page))]
        if locale is not None:
            params.append(("locale", locale))
        url = f"{BASE_URL}/company-search?{urllib.parse.urlencode(params)}"
        result = get_with_retry(url, context="company-search")
        result["requestUrl"] = url
        return result

    return SimpleNamespace(get_company_reviews=get_company_reviews, company_search=company_search)
