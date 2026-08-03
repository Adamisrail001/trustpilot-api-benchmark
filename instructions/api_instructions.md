# "{X} API" Benchmark Article Instructions

Follow CLAUDE.md for voice, tone, brand rules, and research workflow. This file covers structure, methodology, and format-specific rules for "Best {X} API" benchmark articles.

**Synced with Kritik (2026-07-24).** This doc mirrors the lobstr.io project's per-format guidelines in Kritik (X API Testing Methodology v1.0 + Outline Template v1.1, July 2026) — the spec the Kritik judge scores `x-api` drafts against. When this doc and Kritik's config disagree, Kritik's config is the source of truth: re-sync this file.

**Format:** `Best {X} API for Scraping Data at Scale` — {X} = target platform (Google Maps, Zillow, Instagram…). `{WINNER}` = the API that scored highest on the benchmark.

**Scope:** API-only comparisons — official API + internal/hidden API + third-party scraping APIs. Full-platform SaaS comparisons are the `vs` format; no-code tool roundups are the `listicle` format.

**Hard rule:** minimum 2–3 third-party APIs fully benchmarked per article. One option is an ad, not a verdict.

**Voice note:** the structure below is scaffolding, not a straitjacket. Keep the first-person, tested-it-myself voice — jokes, honest jabs, "access is the first joke" energy. The template adds proof; it must not flatten personality.

There are no local sample exemplars for this format yet — voice calibrates from CLAUDE.md, `writing_tips.md`, and the listicle benchmarks' rhythm. (Older API drafts exist in `content/` but predate this methodology; don't match their structure.)

---

## Core Premise

Every API in the article is tested, scored, eliminated, and presented by this methodology, without exception. All raw testing assets (scripts, logs, outputs, timings, cost arithmetic) are published to a **public gist or GitHub repo linked from the article**, so readers can reproduce every result.

The public raw runs are the moat: nobody else publishes them. **Reproducibility is the differentiator, not just the scores.**

- **The winner is whichever API genuinely scores highest.** No predetermined outcomes. If lobstr.io does not win the aggregate benchmark, it does not get crowned — place it in the use-case section where it genuinely fits best.
- **Every claim traces back to a logged run in the gist.** No unverifiable numbers.
- All benchmark numbers come from `knowledge.md`; evergreen brand facts from `facts.md`. Never invent, estimate, or extrapolate a figure — if one is missing, stop and ask.

### Methodology skeleton (how every benchmark runs)
- **Same input dataset for every API** — one fixed list of URLs/IDs/queries per article, versioned in the gist
- **Same time window** — all APIs tested within the same period
- **Same script structure** — one benchmark script template, adapted only for each API's auth and request format
- **Everything logged to the public gist** — raw requests, responses, timings, failures, and cost calculations

---

## Elimination Criteria (E1–E6)

Checked **before** scoring. Failing any one disqualifies the API. Disqualified APIs appear in the article's Disqualified table — API name | Criterion failed | One-line reason | Evidence link — with 1–2 sentences max of commentary; no pile-ons.

| # | Criterion | Rule |
|---|-----------|------|
| E1 | No self-serve access | Sales-call-only, waitlist-gated, or no trial. If a key can't be obtained and the benchmark run within 48h, it's out |
| E2 | Benchmark run failure | Success rate below 50% on the standard 1K-request run, or the API breaks mid-run and cannot complete it |
| E3 | No usable documentation | No public docs, or docs so outdated/incomplete a working request can't be built from them alone. Community workarounds don't count |
| E4 | Uncomputable cost | Pricing so opaque that cost-per-1K-records cannot be calculated even after signup |
| E5 | Platform coverage failure | Does not return the core data type the article targets |
| E6 | Dead or abandoned | No response within the test window, broken infra, or clear abandonment (changelog/status dead 12+ months, key endpoints deprecated with no replacement) |

Do not add "violates platform ToS" as an elimination criterion — it applies to the entire category. Address legality once in a neutral FAQ block.

---

## The Seven Criteria (weights sum to 10)

1. **Success Rate & Reliability — 2.0 pts**: success rate on the 1K-request benchmark (1.0), empty/partial response rate (0.4), error handling quality — meaningful error codes, safe retries (0.3), stability during the test window (0.3)
2. **Data Quality & Completeness — 2.0 pts**: field coverage vs ground truth — fields returned ÷ fields on the page (0.8), data accuracy — values match source (0.5), schema consistency across responses (0.4), freshness — live data vs stale cache (0.3)
3. **Cost Efficiency — 1.5 pts**: cost per 1K successful records (0.8), billing fairness — failed requests not charged (0.3), free tier / trial credits (0.2), pricing transparency — self-serve, predictable (0.2)
4. **Speed & Throughput — 1.5 pts**: median latency per request (0.5), wall-clock time for a 1K-record batch (0.5), p95 latency — consistency under load (0.3), async/batch endpoint availability (0.2)
5. **Scalability — 1.2 pts**: rate limits & max concurrency allowed (0.5), degradation at 10× volume — do success rate/latency hold? (0.4), volume caps blocking production use (0.3)
6. **Developer Experience — 1.0 pt**: time-to-first-successful-request (0.3), docs quality (0.3), SDKs & working code examples (0.2), error message clarity + support responsiveness (0.2)
7. **Input Flexibility & Coverage — 0.8 pts**: accepted input types — URL, ID, search query, geo/filters (0.3), endpoint breadth for the platform (0.3), enrichment/related endpoints (0.2)

### Score bands (verdicts)

| Score | Verdict |
|-------|---------|
| 9.0–10 | Best-in-class — safe default choice |
| 7.5–8.9 | Strong — minor trade-offs |
| 6.0–7.4 | Usable with caveats — flag them |
| Below 6.0 | Not recommended at scale |

### Display rules
- Aggregate score shown as **/10** in the main benchmark table — state it wherever an API is discussed (winner deep-dive, runners-up table, use-case entries)
- Per-criteria rating blocks normalized to **/5 stars** — readers parse stars faster than decimals (criterion level only, e.g. "Reliability: 1.8/2.0" is fine in prose)
- **Sub-criteria scores stay internal** (or in the gist) — criterion-level scores only in the article
- Every criterion section follows: **How it was tested → Findings → Verdict → CTA** (link to the testing report/gist)

---

## Structure

### Title & Meta
- **Title:** `Best {X} API for Scraping Data at Scale [2026 Benchmark]` — alt: `{X} API: Official Limits + {N} Scraping APIs Tested`
- **H1** mirrors the title; **slug** `/{x}-api/`
- **Meta description:** 1 sentence on what was tested + 1 sentence on the winner. ~150 chars, directly under the H1

### 0. Above the Fold (before the intro)

**0.1 Verdict blockquote (~40 words) — an actual `>` blockquote, directly after the meta, before any section heading.** The 40 words any AI would read: **which API is best for scraping {X} at scale, its /10 score, and the one number that proves it** (success rate or cost per 1K records). No hedging, no "it depends". Must stand alone: if this is the ONLY thing an LLM retrieves, the reader still gets the verdict. A missing or buried verdict blockquote is a critical failure. (This format's verdict is a blockquote; the `vs`/`listicle` verdict is bolded prose — don't mix the conventions.)

**0.2 15-second summary (bulleted).** Expand the blockquote into a scannable list:
- **Bullet 1 — Pain point:** the core problem in one line (the official API can't do {X} at scale because {reason})
- **Bullet 2 — Methodology:** what I tested and how ({N} APIs, {dataset size} requests, 7 criteria, raw runs public)
- **Bullets 3+:** one per tested API — **its most important win AND its most painful caveat in the same line**: `**{API}** ({score}/10) — {biggest win}, but {most painful caveat}`
- Keep the whole block under ~120 words. Every bullet carries a number or a hard fact

**0.3 Master comparison table** — one table covering every API discussed (official + third-party), above the fold:

| API | Pricing | Type | Benchmark score | Best for | Main limitation |
|-----|---------|------|-----------------|----------|-----------------|

- Official APIs get "NA" or their real score if benchmarked
- This is the page's most-screenshotted asset — every cell must be specific (real prices, real limits)

### 1. Introduction — PAS
- **Hook (Pain):** hit the nerve — a pun/line/personal story on the biggest pain point of scraping {X}. One or two sentences max; it should make the target reader smirk in recognition, not groan. Reddit/Discord lurking stories work ("people keep asking the same thing")
- **Problem (Agitate):** the pain points the nerds reading this have personally hit — rate-limit walls, missing fields, surprise bills, bans. Name 2–3 concrete frustrations. Specific beats clever
- **Solution:** the standardized benchmark — {N} APIs, same dataset, same scripts, raw runs published in a public gist anyone can reproduce. End with a link to the repo
- Do NOT restate the winner here — the blockquote and summary already did. The intro's job is emotional buy-in, not the verdict

### 2. Why Would You Need a {X} API?
Short orientation block — 4–6 lines max: what data people want from {X}, what they build with it, who needs it. No fluff — this exists so the official API section lands in context, not as a docs dump.

### 3. Does {X} Have an Official API?
**Writer's north star:** the reader should finish this section knowing MORE than the official docs tell them. If a paragraph could have been written by skimming the docs homepage, cut it or add tested evidence. This section is where the article earns trust before selling anything.

- **3.1 What the official API actually offers** — endpoints and data types, organized by *what the reader wants to extract*, not by how {X} organizes its docs; auth model + access friction (how long approval actually takes, what gets rejected — test it or cite recent dev-community reports); 2–3 legitimate use cases — be fair; the official API is genuinely right for some readers, say so
- **3.2 Example requests (working, tested code)** — 1–2 code examples actually run (Python `requests` preferred, curl as alt); show the real (sanitized) JSON response and annotate 2–3 fields; pick examples that map to the article's target data type, not the docs' "hello world"
- **3.3 Can it be used for scraping at scale? (No — prove it.)** Every claim needs a number or a source:
  - **Rate limits / quotas:** exact figures from current docs + what they mean in practice ("at {limit}, pulling 100K records takes {time/days}")
  - **Data gaps:** a mini field-comparison table — 5–10 fields visible on the {X} page vs what the official API returns. A small table beats prose
  - **Cost at scale:** compute a realistic monthly bill at {volume} requests. Show the arithmetic — it's the most-quoted number in the section
  - **ToS / access ceilings:** approval tiers, use-case restrictions, revocation risk — factual, no editorializing
  - **The wall:** identify THE single blocker (usually quota or missing fields) and lead with it — don't bury it in minor gripes
- **3.4 Verdict box** — one paragraph: what the official API is genuinely good for, the exact point where it stops, the natural bridge forward

Anti-patterns: paraphrasing the docs' feature list with no testing; vague claims ("the API is limited" — limited to WHAT number?); skipping the cost arithmetic; pretending the official API is useless (it isn't, and readers know it).

### 4. The Internal (Hidden) API — *conditional section*
Include when the platform has an internal API worth discussing (most consumer platforms do). Skip only if genuinely nothing there.

- **4.1 Discovery walkthrough** — DevTools → Network tab → click around → capture real internal endpoints; show 1–2 actual endpoints with sanitized example responses; screenshot-heavy — this is the "aha" moment of the article
- **4.2 Why it dies at scale** — the anti-bot system in play (Datadome/Cloudflare/PerimeterX — name it, show the block screen); undocumented = breaks without warning; the maintenance tax (proxies, throttling, retries, cat-and-mouse)
- **4.3 The pivot** — one honest paragraph: the internal API works for hobby volume, dies in production — which is why purpose-built third-party APIs exist

Why this section matters: it completes the story — official door closes, internal door closes, third-party is the *earned* conclusion, not a sales pitch. It's also the content devs search for and can't find anywhere else.

### 5. Best {X} API for Scraping at Scale: How I Tested
- **5.1 Testing criteria** — summary table of the 7 criteria + points (/10 total), one line per criterion on what it measures
- **5.2 Methodology** — the input dataset (what, size, how chosen; link the versioned dataset in the gist), the time window, the same script structure per API (link the template script), everything logged publicly (link the gist/repo)
- **5.3 Disqualified APIs** — table: API | Criterion failed (E1–E6) | One-line reason | Evidence link

### 6. Best {X} API: {WINNER}
- **6.1 Intro + user rating** — what {WINNER} is, who runs it, since when; aggregated user rating (G2/Trustpilot/Capterra — source + review count + link)
- **6.2 Benchmark scorecard** — aggregate **{score}/10** + verdict band; table: criterion | score | /5 stars (criterion-level only, no sub-criteria decimals)
- **6.3 Pros & cons table** — 4–6 pros, 3–5 cons. Cons must be real and stated plainly — "async-only," "search/catalog pages only." Softened cons kill credibility
- **6.4 Performance per criterion** — repeat for each of the 7 criteria:
  > **Criterion #{n}: {name} — {score}**
  > - **How it was tested:** 2–3 sentences, reference the exact script/log in the gist
  > - **Findings:** the numbers — success rate, latency, cost figures, field coverage %
  > - **Verdict:** 1–2 sentences, plain judgment
  > - **CTA:** "Click here to access the detailed testing report" → gist/repo link

### 7. Getting Started with {WINNER} — Quickstart
Condensed hands-on walkthrough — the highest-utility block on the page:
- **Auth:** how to get the key, one test request (show the real header — API key / bearer token)
- **Setup:** create the scraper instance / configure inputs and key parameters
- **Run:** trigger + track progress (polling and/or webhooks)
- **Results:** fetch as JSON/CSV, plus automation options (Sheets, S3, scheduling)

Rules: every snippet actually run by the writer — copy-paste-works or it doesn't ship; keep it a quickstart, not full docs — link the docs for depth; end with a personal CTA hook ("want me to build {concrete thing} with this API? ping me on LinkedIn") — it converts and humanizes.

### 8. Runners-Up: Full Benchmark Results
- One table, all tested APIs ranked: API | aggregate /10 | top strength | main weakness
- Then a short block per runner-up: features (brief), pricing, limitations — 100–150 words each
- Honest framing: what each one beats the winner at (there's always something)

### 9. Best {X} APIs by Use Case
Format per entry:
> ### {API name} — Best for {use case}
> - 2–3 sentences: why it wins this niche despite not winning overall
> - Its aggregate score + the specific criterion where it excelled
> - Pricing one-liner

Typical slots (pick what fits the platform): best for small volumes / hobby projects · best free tier · best synchronous / real-time option · best for {specific data type} · best for enterprise / SLA needs · best no-code option (bridge to the matching listicle — internal link).

*lobstr.io usually lives here unless it genuinely won the aggregate benchmark.*

### 10. Concept Explainer — *exactly one per article*
Pick THE concept that gates the reader's decision and explain it properly with a comparison table: sync vs async APIs (when the winner is async) · place IDs / data IDs vs URLs (when input format confuses) · official vs internal vs third-party (when the landscape confuses). Placement is flexible — put it where the confusion actually arises, or before the FAQ. One per article; more dilutes.

### 11. FAQ
Required questions:
- **Is scraping {X} legal?** — one neutral, factual block; do not overpromise, do not moralize
- What's the difference between the official {X} API and scraping APIs?
- How much does scraping {X} at scale cost?
- **Can I reproduce these benchmark results?** — yes; link the gist + how to run it

Add 2–3 platform-specific questions from People Also Ask (rate limits, domain coverage, ID lookup…). Each answer self-contained, opening with the verdict.

### 12. Conclusion
Restate winner + score in one line → one-sentence honest caveat (when the winner is NOT the right pick) → final CTA to the winner + link to the testing repo → personal CTA hook (LinkedIn) for the next article/build.

---

## Shared Style Rules (same as every format)

- Use `...` instead of em (—) and en (–) dashes
- **Bold** for emphasis; *italics* only to name on-screen elements; backticks for field names, endpoints, parameters
- UpperCase at the start of list items; no bullet ends with a period; no colon before a heading; paragraphs 1–3 sentences
- Always "lobstr.io" (first body mention linked), Squid capital S; Slots claims qualified (20 per Squid / up to 100 per account — see `facts.md`)
- Banned filler: "delve", "in today's digital landscape", "it's important to note", "could potentially", "seamless(ly)", "robust", "a myriad", "leverage", "game-changer", "unleash", "navigating the"
- State costs as **$ per 1K records** wherever pricing appears; state exact rate-limit figures (requests per second/minute/day), never "the API is limited"
- At least two real fenced code blocks (a request per API/endpoint with auth + a sample response) — an API article with no runnable code is a FAIL
- Screenshots as evidence (DevTools captures, block screens, dashboards); draft-time images as `PLACEHOLDER_descriptive_name.png`
- All links carry `https://` schemes with descriptive anchors; internal (lobstr.io) + external citation links both present; the gist/repo link is mandatory
- Third-party ratings always sourced (G2 / Capterra / Trustpilot + review count + link, dated) — never a self-assigned star rating

---

## Writer Checklist (before submitting)

- [ ] Blockquote answers the #1 question in ~40 words, standalone-extractable, before any section heading
- [ ] 15-second summary: pain → methodology → win + caveat per API, all with numbers
- [ ] Master comparison table above the fold, every cell specific
- [ ] Intro follows PAS (pain → agitate → solution), no verdict repetition
- [ ] Official API section has the field-gap table + cost arithmetic — not a docs paraphrase
- [ ] Internal API section included (or consciously skipped with reason)
- [ ] Minimum 2–3 third-party APIs fully benchmarked, each with its aggregate /10 stated
- [ ] Every number traces to a logged run in the gist — no unverifiable claims
- [ ] Winner = highest score. No exceptions, including lobstr.io
- [ ] Winner cons stated plainly, not softened
- [ ] Quickstart section present ("Getting Started with {WINNER}"), snippets actually run — copy-paste-works
- [ ] Auth shown with a real header; rate limits stated with exact figures; cost per 1K stated with the arithmetic
- [ ] Official API section cites current docs (check dates — limits change)
- [ ] Disqualified table complete with evidence links
- [ ] Per-criteria blocks follow: tested → findings → verdict → CTA
- [ ] Scores shown /10 aggregate, /5 stars per criterion, no sub-criteria decimals in the article
- [ ] Exactly one concept explainer, placed where confusion arises
- [ ] Use-case section present with 2+ "best for …" entries
- [ ] Legality FAQ present, neutral and factual
- [ ] Public gist/repo linked (raw requests, responses, timings, cost calcs)
- [ ] Internal link to the matching no-code listicle (and vice versa after publish)
- [ ] Voice preserved — first-person, tested-it-myself, personality intact
