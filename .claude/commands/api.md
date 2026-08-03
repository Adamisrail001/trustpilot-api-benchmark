Write a "Best {X} API" benchmark article about: $ARGUMENTS

## Step 1: Facts

Locate the article folder for this topic under `content/` (folder name = article file name). If it doesn't exist, ask Shehriar to confirm the folder name before proceeding.

Read `content/{articlefolder}/knowledge.md`. It is the single source of truth for findings, benchmark results, and claims. Never contradict it, never invent facts beyond it. For evergreen brand facts (current scraper count, positioning line, Slots, export formats), read `facts.md` at the repo root — boilerplate descriptions come from there, not from memory. API articles are built on logged benchmark runs — if any figure is missing (a success rate, latency, cost per 1K, rate limit, field coverage %, the public gist/repo URL), list what's missing and ask before researching or drafting. Never estimate or extrapolate a test number. An api article CANNOT ship without the public gist/repo link and per-criterion benchmark numbers.

If `content/{articlefolder}/data/comparison.md` exists, read it too: it is the `/datacompare` artifact (API outputs scored as named scrapers). Its numbers are canonical for the Data Quality & Completeness criterion — use them verbatim, never recompute or contradict them. If it's absent and the topic needs rigorous data scoring, run `/datacompare` first.

Work ONLY from the files this command names: `knowledge.md`, `facts.md`, the `data/comparison.md` artifact if present, and the Step 2 benchmark. No repo-wide globs, greps, or exploration. If a relative path doesn't resolve, resolve it from the project root (the folder containing `CLAUDE.md` and `facts.md`) — do not search for it.

## Step 2: Reference

There is no api-format sample exemplar yet. If `instructions/listicles_samples/bestyelpreviewsscrapers.md` exists, read it once, for rhythm and voice calibration ONLY — it is a different format. Do not copy its structure: its verdict is bolded prose (this format's is a blockquote), its scoring system differs, its skeleton differs. Where anything in it conflicts with this contract, THIS CONTRACT WINS. If the file is missing, calibrate voice from the rhythm section below alone. Older API drafts in `content/` predate this methodology — never match their structure.

## Step 3: Style contract

### Voice
Shehriar, first person singular ("I"), talking to one reader ("you") — a dev or technical buyer. Confident, direct, slightly cheeky, contractions, light humor, 1-3 emojis at natural moments. "Access is the first joke" energy: the jokes and honest jabs survive the structure. Radical honesty in both directions: real trade-offs for lobstr.io, real credit for competitors. The skeleton below is scaffolding, not a straitjacket — it adds proof; it must not flatten personality.

### Scope guard (check before drafting)
This format is API-only comparisons: official API + internal/hidden API + third-party scraping APIs. Full-platform SaaS comparisons are the vs format; no-code tool roundups are `/listicle`. **Minimum 2-3 third-party APIs fully benchmarked per article — one option is an ad, not a verdict.** If the requested topic doesn't fit, STOP and tell Shehriar which format it belongs to instead of drafting it here.

### Core premise (hard rules)
Every API is tested, scored, eliminated, and presented by one methodology, without exception. All raw testing assets (scripts, logs, outputs, timings, cost arithmetic) live in a **public gist or GitHub repo linked from the article** — the public raw runs are the moat; reproducibility is the differentiator, not just the scores. The methodology skeleton: same input dataset for every API (versioned in the gist), same time window, same script template (adapted only for each API's auth and request format), everything logged publicly.

- **The winner is whichever API genuinely scores highest.** No predetermined outcomes. If lobstr.io doesn't win the aggregate, it doesn't get crowned — it lives in the use-case section where it genuinely fits best
- **Every claim traces back to a logged run in the gist.** No unverifiable numbers
- Numbers must be internally consistent across the blockquote, the summary, the tables, the deep dives, the FAQ, and the conclusion

### Eliminations (E1-E6 — checked before scoring; failing one disqualifies)
E1 no self-serve access (sales-call-only, waitlist-gated, or no trial; if a key can't be obtained and the benchmark run within 48h, it's out) · E2 benchmark run failure (success rate below 50% on the standard 1K-request run, or breaks mid-run) · E3 no usable documentation (a working request can't be built from the docs alone; community workarounds don't count) · E4 uncomputable cost (pricing so opaque cost-per-1K can't be calculated even after signup) · E5 platform coverage failure (doesn't return the core data type the article targets) · E6 dead or abandoned (no response in the test window, broken infra, or changelog/status dead 12+ months).

Disqualified APIs appear in one table — API | Criterion failed | One-line reason | Evidence link — with 1-2 sentences max of commentary; no pile-ons. **Never eliminate on "violates platform ToS"** — it applies to the entire category; legality is addressed once, in a neutral FAQ block.

### The seven criteria (weights sum to 10 — name them in the article)
1. **Success Rate & Reliability — 2.0**: success rate on the 1K-request benchmark (1.0), empty/partial response rate (0.4), error handling quality — meaningful codes, safe retries (0.3), stability during the window (0.3)
2. **Data Quality & Completeness — 2.0**: field coverage vs ground truth — fields returned ÷ fields on the page (0.8), accuracy — values match source (0.5), schema consistency (0.4), freshness — live vs cache (0.3). When `data/comparison.md` is present, this criterion's numbers come from it verbatim
3. **Cost Efficiency — 1.5**: cost per 1K successful records (0.8), billing fairness — failed requests not charged (0.3), free tier/trial credits (0.2), pricing transparency (0.2)
4. **Speed & Throughput — 1.5**: median latency per request (0.5), wall-clock for the 1K batch (0.5), p95 under load (0.3), async/batch endpoint availability (0.2)
5. **Scalability — 1.2**: rate limits & max concurrency (0.5), degradation at 10× volume (0.4), volume caps blocking production (0.3)
6. **Developer Experience — 1.0**: time-to-first-successful-request (0.3), docs quality (0.3), SDKs & working examples (0.2), error clarity + support responsiveness (0.2)
7. **Input Flexibility & Coverage — 0.8**: accepted input types — URL, ID, query, geo/filters (0.3), endpoint breadth (0.3), enrichment/related endpoints (0.2)

Score bands: 9.0-10 best-in-class, safe default · 7.5-8.9 strong, minor trade-offs · 6.0-7.4 usable with caveats, flag them · <6.0 not recommended at scale.

### Display rules
- Aggregate score shown as **/10** — stated wherever an API is discussed (winner deep-dive, runners-up table, use-case entries)
- Per-criterion rating blocks normalized to **/5 stars** — criterion level only; "Reliability: 1.8/2.0" is fine in prose
- **Sub-criteria scores stay in the gist** — never in the article
- Every criterion section follows: **How it was tested → Findings → Verdict → CTA** (link to the testing report/gist)

### Structure skeleton (exact order)
1. **H1** (`Best {X} API for Scraping Data at Scale [{Year} Benchmark]`; alt: `{X} API: Official Limits + {N} Scraping APIs Tested`; slug `/{x}-api/`) + meta description directly under it: one sentence on what was tested + one on the winner, under 160 characters
2. **Verdict blockquote** — an actual `>` blockquote, ~40 words, directly after the meta, BEFORE any heading: which API is best for scraping {X} at scale, its /10 score, and the one number that proves it (success rate or cost per 1K). No hedging, no "it depends". Standalone-extractable: if an LLM lifts only this, the reader has the verdict. A missing or buried verdict blockquote is a CRITICAL failure. (This format's verdict is a blockquote; the listicle verdict is bolded prose — don't mix conventions)
3. **15-second summary** (bulleted, under ~120 words) — bullet 1 pain point (the official API can't do {X} at scale because {reason}); bullet 2 methodology ({N} APIs, {dataset size} requests, 7 criteria, raw runs public); then one per tested API: `**{API}** ({score}/10) — {biggest win}, but {most painful caveat}`. Every bullet carries a number or a hard fact
4. **Master comparison table** — ONCE, above the fold, every API discussed (official included — "NA" or its real score): API | Pricing | Type | Benchmark score | Best for | Main limitation. The page's most-screenshotted asset — every cell specific (real prices, real limits)
5. **Introduction — PAS** — Hook (pain): one or two sentences that make the target reader smirk in recognition; Reddit/Discord lurking stories work. Agitate: 2-3 concrete frustrations (rate-limit walls, missing fields, surprise bills, bans) — specific beats clever. Solution: the standardized benchmark, ending with the repo link. Do NOT restate the winner — the blockquote already did; the intro's job is emotional buy-in
6. **Why would you need a {X} API?** (##) — 4-6 lines max: what data people want, what they build, who needs it. No fluff
7. **Does {X} have an official API?** (##) — the reader should finish knowing MORE than the official docs tell them; if a paragraph could be written by skimming the docs homepage, cut it or add tested evidence. Subsections: (a) what it actually offers, organized by what the reader wants to extract, auth model + real access friction, 2-3 legitimate use cases stated fairly; (b) 1-2 working code examples actually run (Python `requests` preferred) + real sanitized JSON response with 2-3 fields annotated; (c) can it scrape at scale? — NO, proven: exact rate limits + what they mean in practice ("at {limit}, 100K records takes {time}"), a 5-10 row field-gap mini table (page-visible fields vs API returns), cost-at-scale arithmetic shown (the section's most-quoted number), ToS/access ceilings stated factually, and THE wall — the single blocker — led with, not buried; (d) verdict box: what it's genuinely good for, where it stops, the bridge forward
8. **The internal (hidden) API** (##) — conditional; include when the platform has one worth discussing (most consumer platforms do), skip only with a stated reason. Discovery walkthrough (DevTools → Network tab, 1-2 real endpoints with sanitized responses, screenshot-heavy — the "aha" moment); why it dies at scale (the anti-bot system BY NAME + block-screen screenshot, undocumented = breaks without warning, the maintenance tax); the pivot: works for hobby volume, dies in production — which is why third-party APIs exist. This section completes the story: official door closes, internal door closes, third-party is the earned conclusion
9. **How I tested** (##) — criteria summary table (7 criteria + weights, one line each on what it measures); methodology (the input dataset: what, size, how chosen, linked in the gist; the window; the script template linked; everything logged publicly); disqualified table (API | E-criterion | one-line reason | evidence link)
10. **Best {X} API: {WINNER}** (##) — intro + sourced user rating (G2/Trustpilot/Capterra: source + review count + link); benchmark scorecard (aggregate /10 + verdict band; table: criterion | score | /5 stars); pros & cons table (4-6 pros, 3-5 cons stated plainly — "async-only", "search pages only"; softened cons kill credibility); then all 7 criteria as blocks, each: How it was tested (2-3 sentences, exact script/log referenced) → Findings (the numbers) → Verdict (1-2 plain sentences) → CTA ("Click here to access the detailed testing report" → gist)
11. **Getting started with {WINNER} — quickstart** (##) — the highest-utility block: auth (get the key, one test request, the real sanitized header), setup, run + progress tracking (polling/webhooks), results (JSON/CSV + automation: Sheets, S3, scheduling). Every snippet actually run by the writer — copy-paste-works or it doesn't ship; a quickstart, not full docs; end with a personal CTA hook ("want me to build {thing} with this API? ping me on LinkedIn")
12. **Runners-up: full benchmark results** (##) — one ranked table (API | /10 | top strength | main weakness), then 100-150 words per runner-up: features, pricing, limitations — and what each one beats the winner at (there's always something)
13. **Best {X} APIs by use case** (##) — per entry: `### {API} — Best for {use case}`, 2-3 sentences on why it wins the niche, its /10 + the criterion where it excelled, pricing one-liner. Typical slots: small volumes/hobby · best free tier · best synchronous/real-time · best for {data type} · enterprise/SLA · best no-code option (bridge to the matching listicle). lobstr.io usually lives here unless it genuinely won the aggregate
14. **Concept explainer** (##) — EXACTLY ONE per article: the concept that gates the reader's decision (sync vs async · IDs vs URLs · official vs internal vs third-party), explained with a comparison table, placed where the confusion actually arises. More than one dilutes
15. **FAQ** (##) — required: "Is scraping {X} legal?" (one neutral, factual block — no overpromising, no moralizing), official API vs scraping APIs, cost at scale, "Can I reproduce these results?" (yes → gist + how to run). Plus 2-3 platform-specific from People Also Ask. Each answer self-contained, opening with the verdict
16. **Conclusion** (##) — winner + score in one line → one honest caveat (when the winner is NOT the right pick) → CTA to the winner + testing repo link → personal LinkedIn hook for the next article/build

### Hard rules (verbatim)
- "Use `...` instead of em dashes (—) and en dashes (–)."
- **Bold/italic split**: `**bold**` for emphasis. *Italic* is reserved exclusively for naming an element visible on a screenshot. Backticks for field names, endpoints, and parameters
- **At least two real fenced code blocks** — a request per API/endpoint with auth + a sample response. An API article with no runnable code is a FAIL
- State costs as **$ per 1K records** wherever pricing appears; state exact rate-limit figures (requests per second/minute/day), never "the API is limited"
- **The gist/repo link is mandatory** — raw requests, responses, timings, cost calcs, all public
- **Dual ratings wherever an API is introduced**: third-party user rating (G2 / Capterra / Trustpilot — source + review count + link, dated) + the benchmark /10. Never a self-assigned star rating
- Screenshots as evidence (DevTools captures, block screens, dashboards); draft-time images as `PLACEHOLDER_descriptive_name.png`
- Every link carries a scheme (`https://...`) with a descriptive anchor; internal (lobstr.io) + external citation links both present
- Cross-link the platform cluster: the matching no-code listicle (and note to back-link after publish); store CTAs use `#cta-link`
- Always "lobstr.io" (first body mention linked), Squid capital S; any Slots/concurrency claim names its dimension per `facts.md` (20 per Squid / up to 100 per account)
- "Keep paragraphs short — 1-3 sentences max." / UpperCase at the start of list items / no bullet ends with a period / no colon before a heading

### Rhythm and micro-style
- Absurd numbers get a beat of their own: "The official API caps you at **500 requests a day**. Five hundred. 🙃"
- The methodology flex is short and cocky: "Nobody else publishes their raw runs. I do. Reproduce every number yourself."
- Kill-shots are earned with evidence: "Great docs and a free tier mean nothing if 4 requests in 10 come back empty."
- Weaknesses reframed honestly, not buried: "It's async-only... which is exactly what you want at 100K records, and exactly what you don't for a quick lookup."
- Transparency asides build trust: "I ran every API in the same 48-hour window, same input list, same script skeleton."

### Banned patterns
Everything banned in how-tos (hedging, corporate "we", marketing fluff, em/en dashes) plus the AI-tell filler list: "delve", "in today's digital landscape", "it's important to note", "could potentially", "seamless(ly)", "robust", "a myriad", "leverage", "game-changer", "unleash", "navigating the". Also banned: paraphrasing the docs' feature list with no testing, vague limit claims ("the API is limited" — limited to WHAT number?), skipping the cost arithmetic, pretending the official API is useless (it isn't, and readers know it), softened winner cons, sub-criteria decimals in the article body, spec-sheet claims without a logged run, "user rating" rows sourced from nowhere.

## Step 4: Draft

Write the complete article to `content/{articlefolder}/{articlefolder}.md` following the contract. If that file already exists and is non-empty, STOP and ask whether to overwrite it or write to a different file name (e.g. `{articlefolder}_v2.md`) — never overwrite a finished article silently. All factual claims must trace to knowledge.md, facts.md, the `data/comparison.md` artifact, or research Shehriar explicitly approved.

## Step 5: Mandatory self-review (do not skip, do not present the draft before this)

Check the draft against this checklist. For each item output PASS or FAIL with the offending line:

1. Contains zero em (—) or en (–) dashes; `...` used instead; none of the banned filler words appear
2. Formatting block holds: bold for emphasis with zero italics except on-screen element names; field names/endpoints/parameters in backticks; UpperCase at the start of list items; no bullet ends with a period; no colon before any heading; paragraphs 1-3 sentences
3. Meta description present directly below the H1, under 160 characters: what was tested + the winner
4. Verdict is an actual `>` blockquote (~40 words) before any section heading — standalone-extractable, naming the best API, its /10 score, and the one proving number; never bolded prose
5. 15-second summary present and under ~120 words: pain bullet, methodology bullet ({N} APIs, dataset size, 7 criteria, raw runs public), then one bullet per API with `({score}/10) — win, but caveat`; every bullet carries a number
6. Master comparison table appears exactly ONCE, above the fold, covering every API discussed including the official one; every cell specific — real prices, real limits, no adjective-only cells
7. Intro follows PAS (pain → agitate → solution ending in the repo link) and does NOT restate the winner
8. Official API section: organized by what readers extract, 1-2 code examples actually run with sanitized responses, exact rate-limit figures + the "at {limit}, 100K takes {time}" translation, the 5-10 row field-gap table, the cost-at-scale arithmetic shown, THE wall led with, the verdict box present, current docs cited — not a docs paraphrase
9. Internal API section present (DevTools walkthrough, anti-bot system named + block screen, maintenance tax, the pivot) — or consciously skipped with the reason stated
10. Minimum 2-3 third-party APIs fully benchmarked, each with its aggregate /10 stated everywhere it's discussed
11. "How I tested" carries the 7-criteria weight table, the dataset/window/script-template methodology with gist links, and the complete disqualified table (E1-E6 + evidence links)
12. Winner section complete: sourced user rating, scorecard (criterion | score | /5 stars) + verdict band, pros/cons with cons stated plainly, and all 7 criterion blocks each running How tested → Findings → Verdict → CTA to the gist
13. Winner = highest weighted aggregate, no exceptions including lobstr.io; the weighted math is correct and the weights are named in the article
14. Quickstart present with auth (real sanitized header), setup, run + progress, results + automation; every snippet one the writer actually ran per knowledge.md; ends with the personal CTA hook
15. Runners-up table + 100-150 word blocks, each naming what it beats the winner at; use-case section has 2+ entries in the prescribed format with lobstr.io placed honestly
16. Exactly one concept explainer, with a comparison table, placed where the confusion arises
17. FAQ covers the four required questions (legality — neutral and factual; official vs scraping APIs; cost at scale; reproducibility → gist + how to run) plus 2-3 platform-specific; every answer opens with the verdict
18. Conclusion: winner + score in one line, the honest caveat, repo link, LinkedIn hook
19. Every benchmark number traces to knowledge.md (Data criterion to `data/comparison.md` when present; boilerplate to facts.md) and to a logged run in the public gist; figures are identical across blockquote, summary, tables, deep dives, FAQ, and conclusion
20. Costs stated as $ per 1K records wherever pricing appears; at least two real fenced code blocks present (request with auth + sample response)
21. Scores are /10 aggregate + /5 stars at criterion level only; zero sub-criteria decimals in the body; score bands applied correctly
22. All links carry `https://` schemes with descriptive anchors; the gist/repo link is present; the matching no-code listicle is cross-linked; store CTA uses `#cta-link`; every major section has an image or `PLACEHOLDER_x.png` (summary, FAQ, conclusion, and table-only sections exempt)
23. Dual ratings wherever an API is introduced (sourced third-party rating + benchmark /10); no self-assigned or unsourced ratings
24. Voice reads as one person talking to one reader — personality intact, jokes present, lobstr.io's real trade-offs named

Fix every FAIL. Re-run the checklist. Only present the article when all items PASS. Include the final checklist results after the article.
