# OpenWeb Ninja Trustpilot Reviews API — Missing / Pending Evidence

Nothing below was assumed or invented. This run achieved its full 1,000-review target cleanly — these gaps are evidentiary, not blocking findings.

## Cost

- **"Basic" plan's exact price-per-request:** Pending. Not present in the published rate card (Free/Pro/Ultra/Mega/PAYG). Requires contacting OpenWeb Ninja or checking a plan-details page not surfaced in the documented API reference.
- **Measured billed dollar cost:** Pending — no account/usage/billing API endpoint exists (confirmed by reading the complete documented endpoint list).
- **Whether the retried HTTP 500 consumed quota on both attempts:** Pending — undocumented behavior.
- **Quota remaining after this run:** Pending — not re-checked (would require another manual dashboard visit); before-run figure (100) was manually confirmed by you.

## Accuracy — domains without ground truth

`www.shein.com`, `temu.com`, `www.aliexpress.com`, `thehalara.com` have no manually-verified ground-truth sample, same as every prior benchmark.

## Field coverage gaps (confirmed absent, not merely unchecked)

- `owner_reply_date` / reply timestamp — no such field anywhere in the documented or observed schema.
- `review_url` / a clickable review link — no such field exists; `review_id` (a bare hex string) is the only identifier.
- `review_type` (Invited/organic) equivalence via `review_source` is a **discovered heuristic**, not an officially documented field mapping — validated at 100% against 19 comparable ground-truth rows this run, but not guaranteed to hold on other domains or accounts.

## Scalability

- **10x volume behavior:** not tested — this run made exactly 50 sequential, deliberately-throttled requests.
- **Async/batch capability:** confirmed absent from documentation, not merely untested.
- **Basic plan's monthly cap and rate limit:** unknown — only Free/Pro/Ultra/Mega/PAYG limits are published.

## Developer Experience

- **Official SDK usability:** not tested — raw HTTP (`fetch`) was used; the docs advertise Ruby/Node.js/PHP/Python clients but none were exercised.
- **Support responsiveness:** not tested.

## What would resolve the remaining gaps

1. Contact OpenWeb Ninja or check the account/billing area of the dashboard for the "Basic" plan's exact rate and monthly cap.
2. Re-check quota remaining post-run via the dashboard for a true before/after usage delta.
3. If a second run against different domains is ever needed, watch whether `review_source` continues to reliably signal invited-review status before relying on it as a stable field.
