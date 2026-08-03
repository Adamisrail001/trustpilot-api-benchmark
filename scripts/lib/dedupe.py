"""Ported 1:1 from scripts/lib/dedupe.js (see MISSING_AND_GAPS.md for the
JS->Python conversion note). Behavior, field names, and key priority order
are unchanged."""
import hashlib


def _normalize(value):
    if value is None:
        return ""
    return str(value).strip().lower()


def build_review_key(domain, review):
    """Three-tier dedupe key, in priority order:
    1. Native review ID (review['id'] / review['review_id'] / review['hash_id'])
    2. Review URL (review['url'])
    3. Deterministic hash of domain+author+timestamp+rating+title+text
    """
    native_id = _normalize(
        review.get("id") or review.get("review_id") or review.get("hash_id")
    )
    if native_id:
        return {"key": f"id:{native_id}", "keyType": "native_id"}

    url = _normalize(review.get("url"))
    if url:
        return {"key": f"url:{url}", "keyType": "url"}

    user_profile = review.get("user_profile") or {}
    author = _normalize(review.get("author_name") or user_profile.get("name"))
    timestamp = _normalize(review.get("timestamp") or review.get("datetime"))
    rating = review.get("rating")
    if isinstance(rating, dict):
        rating = rating.get("value")
    rating = _normalize(rating)
    title = _normalize(review.get("title"))
    text = _normalize(review.get("review_text"))

    hash_input = "|".join([_normalize(domain), author, timestamp, rating, title, text])
    digest = hashlib.sha256(hash_input.encode("utf-8")).hexdigest()
    return {"key": f"hash:{digest}", "keyType": "hash"}


def dedupe(entries):
    """Dedupes a flat list of {domain, review} dict entries.
    Returns {"unique": [...], "duplicates": [...]}, each duplicate entry
    recording which key/original it collided with.
    """
    seen = {}
    unique = []
    duplicates = []

    for entry in entries:
        result = build_review_key(entry["domain"], entry["review"])
        key, key_type = result["key"], result["keyType"]
        if key in seen:
            review = entry["review"]
            duplicates.append(
                {
                    "domain": entry["domain"],
                    "key": key,
                    "keyType": key_type,
                    "firstSeenDomain": seen[key]["domain"],
                    "review_title": review.get("title"),
                    "timestamp": review.get("timestamp") or review.get("datetime"),
                }
            )
            continue
        seen[key] = entry
        unique_entry = dict(entry)
        unique_entry["dedupeKey"] = key
        unique_entry["dedupeKeyType"] = key_type
        unique.append(unique_entry)

    return {"unique": unique, "duplicates": duplicates}
