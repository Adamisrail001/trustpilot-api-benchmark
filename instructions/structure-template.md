# X API Article — Outline Template (Writer Reference)

**Format:** "{X} API" article
**Companion doc:** X API Testing Methodology (rubric, eliminations, display rules)
**Version:** 1.1 — July 2026

Replace `{X}` with the target platform (e.g. Google Maps, Zillow, Twitter/X).
Replace `{WINNER}` with the API that scored highest on the benchmark.

**Hard rule:** minimum 2–3 third-party APIs fully benchmarked per article. One option is an ad, not a verdict.

**Voice note:** the structure below is scaffolding, not a straitjacket. Keep the first-person, tested-it-myself voice — jokes, honest jabs, "access is the first joke" energy. The template adds proof; it must not flatten personality.

---

## Title & Meta

- **Title format:** `Best {X} API for Scraping Data at Scale [2026 Benchmark]`
  - Alt: `{X} API: Official Limits + {N} Scraping APIs Tested`
- **H1:** mirrors title
- **Meta description:** 1 sentence on what was tested + 1 sentence on the winner. ~150 chars.
- **Slug:** `/{x}-api/`

---

## 0. Above the Fold (before intro)

### 0.1 Blockquote summary (~40 words)

> The 40 words any AI would read. Answer the single most important question directly: **which API is best for scraping {X} at scale, its score, and the one number that proves it** (e.g. success rate or cost per 1K records).

- No hedging, no "it depends" — a direct, extractable answer
- Must stand alone: if this is the ONLY thing an LLM retrieves, the reader still gets the verdict
- Format as an actual `<blockquote>` element

### 0.2 15-second summary (bulleted)

Expand the blockquote into a scannable bullet list:

- **Bullet 1 — Pain point:** the core problem in one line (official API can't do X at scale because {reason})
- **Bullet 2 — Methodology:** what we tested and how ({N} APIs, {dataset size} requests, 7 criteria, raw runs public)
- **Bullets 3+:** one bullet per tested API — **its most important win AND its most painful caveat** in the same line
  - Format: `**{API}** ({score}/10) — {biggest win}, but {most painful caveat}`
- Keep the whole block under ~120 words. Every bullet must carry a number or a hard fact.

### 0.3 Master comparison table

One table covering every API discussed (official + third-party):

| API | Pricing | Type | Benchmark score | Best for | Main limitation |
|-----|---------|------|-----------------|----------|-----------------|

- Official APIs get "NA" or their real score if benchmarked
- This is the page's most-screenshotted asset — every cell must be specific (real prices, real limits)

---

## 1. Introduction — PAS structure

- **Hook (Pain):** hit the nerve — open with a pun/line/personal story on the biggest pain point of scraping {X}. One or two sentences max. It should make the target reader smirk in recognition, not groan. (Reddit/Discord lurking stories work — "people keep asking the same thing.")
- **Problem (Agitate):** the biggest pain points of the nerds reading this — rate limit walls, missing fields, surprise bills, bans. Name 2–3 concrete frustrations they've personally hit. Specific beats clever here.
- **Solution:** what we bring and how it's different — a standardized benchmark, {N} APIs, same dataset, same scripts, raw runs published in a public gist anyone can reproduce. End with a link to the repo.
- Do NOT restate the winner here — the blockquote and summary above already did that. The intro's job is emotional buy-in, not the verdict.

---

## 2. Why Would You Need a {X} API?

Short orientation block — 4–6 lines max:

- What data people want from {X} (listings, reviews, profiles, prices...)
- What they build with it (monitoring, analytics, alerts, tools)
- Who needs it (sellers, devs, agencies, researchers)

No fluff — this exists so the official API section lands in context, not as a docs dump.

---

## 3. Does {X} Have an Official API?

**Writer's north star for this section:** the reader should finish it knowing MORE than the official docs tell them. If a paragraph could have been written by skimming the docs homepage, cut it or add tested evidence. This section is where we earn trust before selling anything.

### 3.1 What the official API actually offers
- Endpoints and data types available — but organized by *what the reader wants to extract*, not by how {X} organizes its docs
- Auth model + access friction: how long approval actually takes, what gets rejected (test it or cite recent dev-community reports)
- Legitimate use cases (2–3 concrete ones) — be fair; the official API is genuinely right for some readers, say so

### 3.2 Example requests (working, tested code)
- 1–2 code examples the writer has **actually run** (Python `requests` preferred, curl as alt)
- Show the real (sanitized) JSON response — annotate 2–3 fields worth pointing at
- Pick examples that map to the article's target data type, not the docs' "hello world"

### 3.3 Can it be used for scraping data at scale? (No — prove it)
Every claim here needs a number or a source. Cover:

- **Rate limits / quotas:** exact figures from current docs + what that means in practice ("at {limit}, pulling 100K records takes {time/days}")
- **Data gaps:** a mini field-comparison — 5–10 fields visible on the {X} page vs what the official API returns. A small table beats prose here.
- **Cost at scale:** compute a realistic monthly bill at {volume} requests. Show the arithmetic — it's the most-quoted number in the section.
- **ToS / access ceilings:** approval tiers, use-case restrictions, revocation risk — factual, no editorializing
- **The wall:** identify THE single blocker (usually quota or missing fields) and lead with it — don't bury it in a list of minor gripes

### 3.4 Verdict box
- One paragraph: what the official API is genuinely good for, the exact point where it stops, and the natural bridge forward

**Anti-patterns to avoid in this section:**
- Paraphrasing the docs' feature list with no testing or numbers
- Vague claims like "the API is limited" — limited to WHAT number?
- Skipping the cost arithmetic — this is the section's most shareable asset
- Pretending the official API is useless — it isn't, and readers know it

---

## 4. The Internal (Hidden) API — *conditional section*

Include when the platform has an internal API worth discussing (most consumer platforms do). Skip only if genuinely nothing there.

### 4.1 Discovery walkthrough
- DevTools → Network tab → click around → capture real internal endpoints
- Show 1–2 actual endpoints with example responses (sanitized)
- Screenshot-heavy — this is the "aha" moment of the article

### 4.2 Why it dies at scale
- Anti-bot system in play ({Datadome/Cloudflare/PerimeterX} — name it, show the block screen)
- Undocumented = breaks without warning; maintenance tax (proxies, throttling, retries, cat-and-mouse)
- Reverse-engineering cost for anything beyond basics

### 4.3 The pivot
- One honest paragraph: internal API works for hobby volume, dies in production — which is why purpose-built third-party APIs exist

**Why this section matters:** it completes the story — official door closes, internal door closes, third-party is the earned conclusion, not a sales pitch. It's also the content devs search for and can't find anywhere else.

---

## 5. Best {X} API for Scraping at Scale: How We Tested

### 5.1 Testing criteria
- Summary table of the 7 criteria + points (from methodology doc, /10 total)
- One line per criterion explaining what it measures

### 5.2 Methodology
- Input dataset: what it is, size, how it was chosen (link versioned dataset in gist)
- Time window of testing
- Same script structure for every API — link the template script
- Everything logged publicly — link the gist/repo

### 5.3 Disqualified APIs
- Table: API name | Criterion failed (E1–E6) | One-line reason | Evidence link
- 1–2 sentences max of commentary; no pile-ons

---

## 6. Best {X} API: {WINNER}

### 6.1 Intro + user rating
- What {WINNER} is, who runs it, since when
- Aggregated user rating (G2/Trustpilot/Capterra — cite source)

### 6.2 Benchmark scorecard
- Aggregate score: **{score}/10** + verdict band
- Table: criterion | score | /5 stars (display rules per methodology doc — criterion-level only, no sub-criteria)

### 6.3 Pros & cons table
- 4–6 pros, 3–5 cons. Cons must be real and stated plainly — "async-only," "search/catalog pages only." Softened cons kill credibility.

### 6.4 Performance per criterion
Repeat this block for each of the 7 criteria:

> **Criterion #{n}: {name} — {score}**
> - **How it was tested:** 2–3 sentences, reference the exact script/log in the gist
> - **Findings:** the numbers — success rate, latency, cost figures, field coverage %
> - **Verdict:** 1–2 sentences, plain judgment
> - **CTA:** "Click here to access the detailed testing report" → gist/repo link

---

## 7. Getting Started with {WINNER} — Quickstart

Condensed hands-on walkthrough (the highest-utility block on the page):

- **Auth:** how to get the key, one test request
- **Setup:** create the scraper instance / configure inputs and key parameters
- **Run:** trigger + track progress (polling and/or webhooks)
- **Results:** fetch as JSON/CSV, plus automation options (Sheets, S3, scheduling)

Rules:
- Every snippet actually run by the writer — copy-paste-works or it doesn't ship
- Keep it a quickstart, not full docs — link the docs for depth
- End with a personal CTA hook ("want me to build {concrete thing} with this API? ping me on LinkedIn") — it converts and humanizes

---

## 8. Runners-Up: Full Benchmark Results

- One table, all tested APIs ranked: API | aggregate /10 | top strength | main weakness
- Then a short block per runner-up: features (brief), pricing, limitations — article-1 style, 100–150 words each
- Honest framing: what each one beats the winner at (there's always something)

---

## 9. Best {X} APIs by Use Case

Format per entry:

> ### {API name} — Best for {use case}
> - 2–3 sentences: why it wins this niche despite not winning overall
> - Its aggregate score + the specific criterion where it excelled
> - Pricing one-liner

Typical use-case slots (pick what fits the platform):
- Best for small volumes / hobby projects
- Best free tier
- Best synchronous / real-time option
- Best for {specific data type, e.g. reviews / listings / posts}
- Best for enterprise / SLA needs
- Best no-code option (bridge to the existing listicle — internal link)

*Note: lobstr.io usually lives here unless it genuinely won the aggregate benchmark.*

---

## 10. Concept Explainer — *one per article*

Pick THE concept that gates the reader's decision and explain it properly with a comparison table:

- Sync vs async APIs (when the winner is async)
- Place IDs / data IDs vs URLs (when input format confuses)
- Official vs internal vs third-party (when the landscape confuses)

Placement is flexible — put it where the confusion actually arises in the article, or before the FAQ. One per article; more dilutes.

---

## 11. FAQ

Required questions:
- Is scraping {X} legal? — one neutral, factual block; do not overpromise, do not moralize
- What's the difference between the official {X} API and scraping APIs?
- How much does scraping {X} at scale cost?
- Can I reproduce these benchmark results? — yes, link the gist + how to run it

Add 2–3 platform-specific questions from People Also Ask (rate limits, domain coverage, ID lookup, etc.).

---

## 12. Conclusion

- Restate winner + score in one line
- One-sentence honest caveat (when the winner is NOT the right pick)
- Final CTA to winner + link to testing repo
- Personal CTA hook (LinkedIn) for the next article/build

---

## Writer Checklist (before submitting)

- [ ] Blockquote answers the #1 question in ~40 words, standalone-extractable
- [ ] 15-second summary: pain → methodology → win + caveat per API, all with numbers
- [ ] Master comparison table above the fold, every cell specific
- [ ] Intro follows PAS (pain → agitate → solution), no verdict repetition
- [ ] Official API section has the field-gap table + cost arithmetic — not a docs paraphrase
- [ ] Internal API section included (or consciously skipped with reason)
- [ ] Minimum 2–3 third-party APIs fully benchmarked
- [ ] Every number traces to a logged run in the gist — no unverifiable claims
- [ ] Winner = highest score. No exceptions, including lobstr.io
- [ ] Winner cons stated plainly, not softened
- [ ] Quickstart snippets actually run — copy-paste-works
- [ ] Official API section cites current docs (check dates — limits change)
- [ ] Disqualified table complete with evidence links
- [ ] Per-criteria blocks follow: tested → findings → verdict → CTA
- [ ] Scores shown /10 aggregate, /5 stars per criterion, no sub-criteria decimals
- [ ] Exactly one concept explainer, placed where confusion arises
- [ ] Internal link to the matching no-code listicle (and vice versa after publish)
- [ ] Voice preserved — first-person, tested-it-myself, personality intact