# Apify (automation-lab/trustpilot) — Missing / Pending Evidence

Nothing below was assumed or invented. The run completed and produced a mostly-successful, well-documented result — these are the specific gaps left open.

## The SHEIN failure — root cause unresolved

- **Why SHEIN returned zero reviews:** Pending. No error, warning, or log entry exists anywhere in the API responses used by this benchmark (Run object, dataset items) that explains it. Checked and ruled out: HTTP errors (none), network errors (none), error-shaped dataset objects (none), abnormal Run stats (none — clean execution). Resolving this would require inspecting the Actor's live run log on the Apify console directly (`https://console.apify.com/actors/runs/AL74CUwNDfUDkRINC` or equivalent) — not exposed through the documented run/dataset REST endpoints used here.
- **Whether this is reproducible:** Pending — would require a second run, which was not performed per the no-automatic-retry rule.

## Cost

- **Event-level billing breakdown:** Pending. `usageTotalUsd` ($0.465) is an aggregate figure; whether the 2 duplicate records or SHEIN's zero-result domain incurred any separate charge cannot be isolated from it.
- **`usage` and `usageUsd` fields:** both absent from the settled Run object (Pending — not returned, not invented).

## Accuracy — domains without ground truth

`www.shein.com` (also had zero data this run), `temu.com`, `www.aliexpress.com`, `thehalara.com` have no manually-verified ground-truth sample, consistent with every prior benchmark.

## Scalability

- **10x volume behavior:** not tested.
- **Whether `maxReviewsPerCompany=0` (documented "unlimited") actually retrieves more than 200/company:** not tested this run — the project's own documentation flags this as requiring "a separate capability test," deliberately kept apart from the standard 5-domain benchmark.
- **Rate limits:** not stress-tested; no 429s encountered at this volume.

## Developer Experience

- **Official Apify SDK usability:** not tested — raw HTTP (`fetch`) was used, per this project's zero-dependency design.
- **Apify console/support experience for diagnosing the SHEIN failure:** not tested — would be the natural next step to actually resolve the open question above.

## What would resolve the remaining gaps

1. Check the Apify console's live log for run `AL74CUwNDfUDkRINC` to see what (if anything) the Actor reported internally about the SHEIN input.
2. If pursuing the "more than 200 reviews per company" capability claim, run a separate, explicitly-scoped test (per the project's own documentation) rather than folding it into this benchmark.
3. Contact Apify/the Actor developer for an event-level billing breakdown if per-domain cost attribution is needed.
