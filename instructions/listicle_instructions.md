# Listicle / Comparison Article Instructions

Follow CLAUDE.md for voice, tone, brand rules, and research workflow. This file covers structure, methodology, and listicle-specific rules.

**Synced with Kritik (2026-07-24).** This doc mirrors the lobstr.io project's per-format guidelines in Kritik (Best-X Listicle Testing Methodology v1.1 + Outline Template v1.0, July 2026) — the same spec the Kritik judge scores drafts against. When this doc and Kritik's project config disagree, Kritik's config is the source of truth: re-sync this file.

**Benchmarks** — the three articles in `instructions/listicles_samples/` calibrate voice and rhythm:

- `bestgooglemapssrapers.md`
- `bestgooglereviewsscrapers.md`
- `bestyelpreviewsscrapers.md`

They are voice exemplars only. They **predate the v1.1 scoring system** — they duplicate the master table, score /5, and auto-rank lobstr.io first. Where their structure conflicts with this doc, **this doc wins**. Facts and numbers in them are point-in-time — never reuse them as fact sources; facts come from the article's `knowledge.md`.

---

## The Core Premise: Tested, Not Compiled

Every listicle is built on one claim that competitors can't make:

> Most "best [X] scraper" lists online are recycled marketing. Nobody runs the same job through every tool and counts what comes back. So I did.

This means:

- **Every ranked tool gets actually run** on the same standard job, against the same target platform, in the same window, on a purchased plan. "I bought the paid plan of every tool" is part of the credibility claim — only say it if true.
- **Every number in the article is a measured result**, not a spec-sheet claim: fields counted from real exports, speed clocked across runs, cost normalized from real pricing pages, accuracy verified against the source platform.
- **The article shows its work.** Screenshots of runs, GIFs of exports, and mandatory evidence links: one public GitHub repo per comparison (raw dataset samples per tool per tier, run logs, timing evidence) and/or per-tool verification Sheets, each linked with "want to verify the numbers yourself?"
- **Count claims match reality.** "I tested dozens" requires the dozens to be accounted for: ranked + disqualified + a stated longlist. Otherwise say how many you tested.

### Where the numbers come from (knowledge rules)

All test results come from Shehriar. They live in `knowledge.md` and the article folder (datasets, comparison files, screenshots). Boilerplate tool descriptions (scraper counts, positioning lines, plan names) come from `facts.md` — never from memory. **Never invent, estimate, or extrapolate a benchmark figure.** If a number is missing — a speed, a fill rate, a price tier, a field count, an anchor-job cost — stop and ask for it.

Numbers must be **internally consistent** across the whole article: the verdict paragraph, the 30-second summary, the master table, the score summary, the per-tool deep dives, the FAQ, and the conclusion must all quote the same figures.

---

## Three Standing Decisions (settle every article's scoreboard)

1. **One scale: /10.** Every pillar scored 0-10; the aggregate is /10. No /5 in one article and /10 in the next. Per-pillar /5-star icons are allowed as a DISPLAY garnish only, always alongside the /10 number. Emojis (💯👍❌) may decorate a score cell, never replace its number.
2. **Weighted aggregation, weights declared.** Aggregate = Σ(pillar score × pillar weight) ÷ 10, using the weights below (they sum to 10). Every article carries the "How each criterion was scored" block AND one line naming the weights. No silent equal-weight averages.
   Worked example: pillar scores 9, 9, 10, 7, 9, 10 × weights 2.0, 2.0, 2.0, 1.8, 1.4, 0.8 → (18+18+20+12.6+12.6+8)/10 = **8.9/10**.
3. **Support is a scored pillar, not a bonus.** It's in the criteria list, the score table, and the aggregate — or the article doesn't mention it at all.

**#1 = highest weighted score, including when it isn't lobstr.io.** A tool can lose pillars in its own house article — that's the format working, not an incident.

---

## Scope: One Format, Not Two (updated 2026-07-24)

This doc covers **"Best [X] Scrapers"** only: ranked tool roundups for scraping ONE target platform; mixed tool types allowed (no-code SaaS, API, extension). Examples: "Best Google Maps Scrapers", "Best Instagram Profile Scrapers", "Best SeLoger Scrapers".

**"Best [Tool] Alternatives" articles are NO LONGER this format.** They moved to the SaaS vs SaaS methodology (which covers "{A} vs {B}", "{A} Alternatives", and self-alternatives) — see `instructions/vs_instructions.md`. In Kritik they score under the `vs` format, with its own 9-criteria rubric and skeleton.

---

## The Six Pillars (weights sum to 10)

Every tool is scored on the same six criteria — these are the backbone of the article:

1. **Data** — weight 2.0
2. **Usability** — weight 2.0
3. **Scalability** — weight 2.0
4. **Cost** — weight 1.8
5. **Speed** — weight 1.4
6. **Customer Support** — weight 0.8

Score bands: 9.0-10 best-in-class · 7.5-8.9 strong · 6.0-7.4 usable with caveats · <6.0 not recommended at scale.

**Anti-double-counting:** when two tools return identical data, score Data identically and put the ergonomic difference in Usability — one failure or advantage never scores twice ("same data, cleaner plumbing").

### How each pillar is measured (sub-criteria and their weight shares)

**Data (2.0)** — never just count columns; raw column counts lie.

- **Richness (0.6)** — meaningful field count vs the actual platform page. Report total AND meaningful ("84 total / ~70 meaningful") plus the **usable ratio** (meaningful ÷ total, as a %). Exclusive fields per tool; min/max counts per tier when toggles exist. Strip the plumbing: internal IDs, run metadata, input echoed back, listing data duplicated onto every row.
- **Fill consistency (0.4)** — % of columns actually populated across the test set, measured per field on the same list ("email 216/500 = 43%"). Field presence ≠ fill rate. Distinguish a confirmed zero from missing data where the platform allows it.
- **Accuracy (0.5)** — same input to every tool, then measure: geo match (in-target %), category/type match (%), uniqueness (duplicate count). Roll into one combined % per tool.
- **Shape & parseability (0.3)** — flat pre-parsed vs nested (report nesting depth), typed values vs strings (`352000.0` vs `"740 000 €"`), parsed identifiers vs text blobs, always-null fields tracked as a schema category.
- **Freshness (0.2)** — live vs cached.

Required evidence: side-by-side field tables, per-tool raw dataset samples (basic + full tier) in the comparison repo or per-tool Sheets, and a "what each tool has that others don't" list. When a `data/comparison.md` artifact exists (from `/datacompare`), its scores, composites, and field inventory are canonical — use them verbatim.

**Usability (2.0)**

- **Input flexibility (0.5)** — URL, username/query, ID, geo/filters, bulk CSV/TXT upload; note strict-format traps.
- **Ease of use (0.5)** — time-to-first-result + workflow gotchas (schedule pre-run? abort? live console? instance management? result caps vs cost caps?) — findings, not adjectives.
- **Data depth controls (0.4)** — add-on tiers, related scrapers/chaining; **document each toggle: what it adds, what it costs, what it slows**, with an add-on decision block: "Skip it for {use cases} / Turn it on only if you need {fields}."
- **Exports & integrations (0.4)** — formats, destinations (Sheets/S3/SFTP/email/webhook), API/SDK/CLI/MCP.
- **Automation (0.2)** — scheduling (granularity, timezone), monitoring, alerts, dedup.

**Broken-feature forensics:** any documented toggle or parameter the article relies on gets tested with and without; if it changes nothing, say so and tell readers not to pay for it.
**Filter matrix:** where tools offer pre-scrape filters, table them with ✅ (free) / ✅ (paid) / ❌ per tool — filters are a cost dimension, not a feature checkbox.

**Scalability (2.0)**

- **Monthly ceiling (0.5)** — measured rate × 43,200 min, computed **per tier** and at a declared default config so tools compare like with like; note conservative assumptions ("kept at 1 Slot on purpose").
- **Paper vs real ceiling (0.5)** — does the rate-limit headroom survive contact? (500s under load, anti-scraping escalation, memory-driven throttling). Report both numbers when they diverge.
- **Concurrency & account safety (0.5)** — user-controlled slider vs pay-for-compute vs none; disclose workers behind any quoted rate ("90/min = ~20 workers at 4GB"). On logged-in platforms: ban risk, account controls. (Account-safety share applies only when the platform requires auth; otherwise redistribute evenly.)
- **Maintenance & data-loss protection (0.5)** — fix speed when the platform changes, abandonment signals; pause+partial vs lost-on-failure as a first-class comparison row. For marketplace tools: who maintains the actor, and can platform support fix it.

**Cost (1.8)**

- **Bundle cost (0.8)** — entry AND scale, **per configuration tier** (base / +details / +enrichment each priced), chains and add-ons itemized, filter costs folded in, anchor-job total stated. Standard bundle units: **B1** basic records /1K, **B2** complete lead (email + validation) /1K, **B3** reviews /1K — plus platform-specific bundles defined per article before pricing anything.
- **Pricing predictability (0.4)** — per-result vs time/compute/pages-loaded models; **test-derived pricing** for alien models (measure the ratio, label it "based on this run"); crossover points named when rankings flip with volume.
- **Billing fairness (0.3)** — failed/empty runs not charged, no negative balance, runs pause at zero.
- **Free tier / trial value (0.3)** — recurring vs one-time, and whether it covers a meaningful test.

**Speed (1.4)**

- **Measured wall-clock (0.7)** — on the standard batch, **per tier** (base AND full-data — tools quote the fast number and hide the drop), our stopwatch vs vendor claims published side by side; time it yourself when the tool shows no completion time.
- **User control over speed (0.4)** — slots/concurrency the user can add, and what the full-data rate becomes with them.
- **Consistency (0.3)** — repeat runs; ranges ("20-40/min") allowed only when variance across logged runs demands it.

**Customer Support (0.8)**

- **Responsiveness (0.5)** — **primary evidence:** identical ticket to every ranked tool, timestamps logged (names redacted). **Acceptable fallback:** published response stats + review sentiment; the article states which was used. For marketplace tools, response stats MUST be scoped to the specific actor tested — actor stats vary wildly on the same platform.
- **Quality (0.3)** — actual resolution; the same-question-twice consistency probe is valid; note when support's answer contradicts measured reality.

### The anchor job

Pick one concrete volume (default 100K records) and state, for every ranked tool, the wall-clock time and total cost to complete it. One repeated reference beats scattered per-1K numbers ("6.4h / $25 vs 8h / $13 vs 5.75h / $90").

---

## Elimination Criteria (L1-L6)

Checked before scoring; failing one disqualifies. Disqualified tools appear in a **scored cut-table** — measured fields, speed, and cost where obtainable, not just reasons — plus a short block each with "who it's right for."

| # | Criterion | Rule |
|---|-----------|------|
| L1 | Core data failure | Cannot return the platform's core data type for this article |
| L2 | No self-serve trial | Can't run the standard benchmark without a sales call |
| L3 | Benchmark run failure | <50% success on the standard run, breaks mid-run, **or the run never completes** |
| L4 | Uncomputable cost | Bundle price can't be derived even after signup + test run |
| L5 | Onboarding failure | Signup → first successful result >48h following official docs |
| L6 | Dead or abandoned | 12+ months silent, or broken against the platform's current layout |

**Reproduced-failure protocol:** before disqualifying on a failed run, follow the tool's own documented requirements (e.g. a required proxy region), retry under that setup, and screenshot both failures. A disqualification nobody can dispute.

**The price-doesn't-save-you principle:** the cheapest price on the page still gets cut if the run never finishes. Feature lists and sticker prices mean nothing without a completed benchmark — apply it out loud when it bites.

No "violates ToS" eliminations. Prose disqualifications remain fine for category mismatches; conceding a genuine point while disqualifying is encouraged when true.

---

## Methodology Skeleton

- **Same standard job on every tool** — identical inputs, versioned in the comparison repo; default batch 1K (declare deviations and why)
- **Normalize openly** when platform controls force different caps (no fixed row limit → cost-capped run): state each tool's actual batch and normalize to per-minute / per-1K
- **Same window, fresh accounts, paid plans purchased**
- **Every tier measured** — base and full-data runs each timed and priced separately
- **Evidence published** — repo and/or Sheets, linked
- **Anti-double-counting** — one failure never scores in two pillars
- **Facts freshness** — boilerplate from `facts.md`, per-article numbers from `knowledge.md`
- **Count claims match reality**

---

## Format A: "Best [X] Scrapers" Structure

### 1. Title + Meta Description
- Title pattern: `Best [X] Scrapers in [Year] [No-Code + API]` or `Best [X] Scrapers in [Year] (Tested for Data, Speed, Cost & Scale)`
- Slug: `/best-{x}-scrapers/`
- Meta description right below the H1, under 160 characters: what was tested + the winner + one deciding number. No typos bleeding words together.

### 2. Verdict Paragraph (~40 words, bolded, before everything)
Directly after the meta, before any heading:

> **"{Winner} is the best {X} scraper in {year}**, tested across data, usability, scalability, cost, speed, and support. It wins on {2-3 measured edges with numbers}. {Runner-up} is the runner-up for {its edge}, but {its measured gap}."

Standalone-extractable — if an LLM retrieves only this paragraph, the reader has the verdict and the proof. Answer engines disproportionately cite the first chunk that directly answers the headline; a missing or buried verdict forfeits the citation the article is competing for.

### 3. 30-Second Summary (## heading: "⚡ 30-Second Summary")
Bullets, in this order:

- **Methodology first**: what you tested and how — N tools, same job, six criteria, paid plans bought
- **One bullet per ranked tool**: "**[Tool] ... best overall / best on a budget / best for [use case] ([score]/10).** [Biggest measured win]. **Pick it for** [use case]. Trade-off: [most painful measured caveat]." Phrase each tool's role as a "best ..." segment — each line is then independently citable for a different query
- **The cuts**: "Didn't make the cut: [A], [B], and [C]. Reasons at the end."

Use real measured numbers in the summary. Be opinionated; state winners clearly.

### 4. Hook / Opening (short)
- The reader's pain, sourced — a Reddit/community screenshot of someone failing at exactly this, or the official API's absurd limit ("The official API hands you **5 reviews per place**. Five. 🙃")
- Link the previous how-to article on the same topic: "This is the other half... **which tool you should actually use.**"
- The thesis: "Most 'best [X] scraper' lists online are recycled marketing. Nobody runs the same job through every tool and counts what comes back. So I did."

### 5. "Just tell me which one" (### heading)
A quick decision table for scanners — three columns, every row carries the proving number:

| If you want... | Go with | The number |
| --- | --- | --- |
| The best all-rounder | **lobstr.io** | 8.9/10 weighted |
| The cheapest at scale | **[tool]** | $[N]/1K at scale |

One row per decision driver (best overall, cheapest at scale, fastest, richest data, best for emails/reviews, best support).

### 6. Master Comparison Table — appears ONCE
The complete scorecard, above the fold. **Never duplicated** — the ranked-tools section gets a jump link back to it, not a second copy.

Rows are **measured criteria**, not generic specs:

- **Fields** (min/max per tier) + **usable ratio** (%)
- **Fill consistency** (% populated)
- **Accuracy** (combined %, where applicable)
- **Key data capabilities** — one row per differentiating field with ✅ / ❌ / ⚠️
- **Filters** — highlights with ✅ (free) / ✅ (paid) / ⚠️ via URL / ❌
- **Speed** (rows/min, measured, per tier)
- **Cost** /1K (entry → scale, per tier)
- **Max rows/month** (24/7, default config)
- **Concurrency**
- **Export formats**
- **API access**
- **Customer support** (actor-scoped for marketplaces)
- **User rating** (source + review count)
- **Overall /10**

Rules:
- **Bold the winning value in each row.** Numbers in cells, not adjectives.
- Annotate, don't just tick: "✅ (free)" vs "✅ (paid)", "⚠️ (missed ~36%)"
- Add a jump link after the table: `[Skip ahead to the detailed tool-by-tool breakdown](#anchor)`
- Bridge to legal: "But before tools... is this even legal?"

### 7. Score Summary + "How each criterion was scored"
Per-pillar /10 for every tool + the weighted aggregate, then the one-line-per-criterion block naming what was measured, plus one line naming the weights (Data 2.0 · Usability 2.0 · Scalability 2.0 · Cost 1.8 · Speed 1.4 · Support 0.8).

### 8. Legal Section (## heading: "Is it legal to scrape [X]?")
- Disclaimer blockquote first (not legal advice, consult a professional)
- **Platform-specific, researched per platform — no boilerplate reuse.** Jurisdiction-relevant law and named case law where it exists: Ninth Circuit / hiQ v. LinkedIn for US platforms; L342-3 / Entreparticuliers v. Leboncoin for French ones
- The real risk framing: collection vs what you do *after* (copyright on republishing, GDPR/CCPA on personal data)
- Responsible-use bullet list (rate limits, no logins, no republishing, no PII abuse)
- Link the [legal series](https://www.lobstr.io/blog/category/legal) and any platform-specific legal article
- Bridge: "But hold on... how do I even define 'the best'? Let me walk you through my criteria."

### 9. (Conditional) "Does [X] have an official API?" bridge
Include when the platform's API situation frames the buying decision ("there isn't one, so a scraper is the only option"). Keep it short — 100-200 words — and link the full "[X] API" article when one exists. Skip when irrelevant or when the how-to already covered it.

### 10. Selection Criteria (## heading: "How I chose the best [X] scrapers")
Wrap rigor in the filter story:

1. **Community research**: "I went where the complaints live... Reddit threads, community discussions, and review sites." Screenshot the pain points; they become the criteria's justification.
2. **The six criteria, one ### block each** — Data / Usability / Speed / Cost / Scalability / Support: 2-4 sentences on HOW it was measured (fill rates, the same-input accuracy test, per-tier timing, normalized bundles, ceilings at 43,200 min, actor-scoped support evidence), in article voice. A screenshot or GIF per criterion.
3. **What I left out and why**: the category-level cuts (Chrome extensions, abandoned GitHub repos, low-use actors, login-required tools, marketplace wrappers) with one honest line each — including the actor-selection rule ("picked the most-used actor; not a perfect signal, but it beats a ghost actor").
4. Bridge: "So which ones held up?"

### 11. The Ranked Tools (## heading: "Best [X] Scrapers of [Year]")
Jump-link target for the master table — do NOT re-paste it. "You've seen the scorecard. Here's the story behind the numbers, tool by tool."

#### For each tool (### numbered heading, rank order):

1. **Metadata block** — user rating (source, review count, link) · our score /10 · type · pricing from · one-line best-for. For marketplace platforms, name which specific actor you tested and why.
2. **Product screenshot**
3. **CTA link** — lobstr.io only: `👉 [Try the [X] Scraper](store-url#cta-link)`
4. **Per-pillar score table** — each pillar /10 plus the overall, matching the score summary exactly
5. **Pros/Cons table** — punchy lines with real numbers ("Fastest by far (400 reviews/min)" not "Fast"). Cons measured and plain — the winner's included (friendly-fire rule); roadmap admissions where true ("on the fix list")
6. **#### sections mirroring the six pillars, in order** — #### Data / #### Usability / #### Speed / #### Cost / #### Scalability / #### Support — each structured **How tested → Findings → Verdict → evidence link**:
   - **Data** — fields per tier (total AND meaningful + usable ratio), the category-grouped field table with emoji labels (✍️ Review content, 👤 Reviewer, ❤️ Engagement, 🏪 Business, 🛡️ Trust signals...), fields in backticks, fill-rate findings on the same list, the accuracy result (geo/category/uniqueness %), shape notes, exclusive fields, "want to verify? → per-tool Sheet / repo sample". Add-on decision block for every paid data toggle: **Skip it for... / Turn it on only if...**
   - **Usability** — ways to feed it a job, pre-scrape filters with free/paid flags, workflow gotchas as findings, broken-feature forensics where a documented toggle changed nothing, standout features
   - **Speed** — measured per tier, our stopwatch vs vendor claim, worker-count asterisks, what Slots/concurrency do to the number, and what it means in hours for a real job
   - **Cost** — per-function pricing entry → scale, the bundle totals, the anchor-job cost, test-derived pricing labeled where billing is alien, filter costs called out
   - **Scalability** — ceiling per tier at default config (conservative assumptions stated), paper vs real ceiling, concurrency mechanism, data-loss protection, maintenance/actor ownership
   - **Support** — channels, the evidence used (identical ticket OR actor-scoped published stats + review sentiment — state which), quality notes including contradictions caught
7. **"Best for:"** — one bold-led closing line: one concrete reader profile + the honest trade-off sentence.

#### Ranking and honesty
- **#1 = highest weighted score, even when it isn't lobstr.io.** lobstr.io can lose individual pillars in its own article.
- lobstr.io always gets real, named trade-offs — quirks, missing filters, buggy fields, slow modes ("Reaction counts are unreliable... on the fix list", "Full-data speed is slow before Slots")
- Keep the single-Slot math for headline scale claims, then present Slots as the lever: "the one weakness you can simply buy your way out of"
- Use 🎁 to mark exclusive fields and 🐛 to mark known-buggy ones in field tables (sparingly)

#### Competitor tools
- Be genuinely fair — acknowledge real strengths with the same energy as weaknesses
- When a competitor beats lobstr.io on something, say it plainly and credit it in the summary, table, deep dive, AND FAQ
- Ground every weakness in your test: "in my test", "across my runs", with the screenshot
- Pro tips that help the reader use a competitor better are good — they prove you actually used the tool

### 12. The Scrapers That Didn't Make the List (## heading)
- Transition: "After those, a few more names kept coming up that I looked at and cut. So why didn't they make it?"
- Open fair: "These aren't bad tools. They just lost on [the cores that matter]."
- **Scored cut-table**: Tool | measured fields | speed | cost | the failed criterion — receipts, not vibes
- **### subsection per cut tool**: what it is (linked), product screenshot, why it lost — bold-led bullets with measured evidence, reproduced-failure receipts where a run failed (followed its own instructions, retried, screenshots) — then **"Who it's right for"**: every cut ends with the reader it fits
- Apply the price-doesn't-save-you principle out loud when it bites: "the cheapest price on this page still couldn't finish a run"

### 13. FAQ (## heading)
Purchase-decision questions phrased the way people type into an LLM, covering five buckets:

1. **Superlative** — "Which [X] scraper returns the most data?" (fields + the consistency counterpoint), "Cheapest at scale?" (with the DQ'd-cheaper-tool caveat), "Fastest?" (per tier), "Most accurate?" (the combined % + the losing tool's number)
2. **Use-case segmentation** — "Best [X] scraper for [role/job]?"
3. **Decision/qualifier** — "Is scraping [X] legal?", "No-code vs API?"
4. **Definitional/entity** — "Does [X] have an official API?"
5. **Intent variants** — "Free [X] scraper?", "[Competitor] alternative?"

Rules: answers start with a **bold verdict**, then the number. Each answer self-contained. Cross-reference tools honestly — if the answer is "Outscraper, not lobstr.io", say so. Include the reproducibility question: "Can I verify these numbers?" → repo/Sheets. The FAQ doubles as the internal-link hub (how-to guide, [X] API article, related scrapers, free tools).

### 14. Conclusion (## heading)
- "That's a wrap on the **best [X] scrapers for [year]**."
- **Who-owns-what recap**: one line per ranked tool — "[Tool] owns [strengths]. The pick for [use case]."
- Living-list promise: "this list evolves as tools ship updates; I'll keep it current"
- Close with the LinkedIn CTA: "Tested something I missed, or got better results from a different tool? [Ping me on LinkedIn](https://pk.linkedin.com/in/shehriar-ahmad-awan) ... I'll retest, rerank, and add it."

---

## "Best [Tool] Alternatives" Articles → vs_instructions.md

Alternatives articles ("Best Apify Alternatives", "lobstr.io Alternatives") follow the **SaaS vs SaaS methodology**, not this doc — see `instructions/vs_instructions.md` (incumbent teardown, 9-criteria /10 rubric, S1–S6 eliminations, ranked-entry metadata blocks, switching guide). Don't apply this doc's 6-pillar skeleton to an alternatives piece.

---

## Listicle-Specific Writing Rules

### Extractability (GEO/AEO) — write for the answer engines too
- **Verdict first**: the ~40-word bolded answer paragraph before everything (see Format A §2)
- **Segmented picks near the top**: the summary's "best overall / best on a budget / best for X" lines — each independently citable for a different query
- **Entity-first claims**: every verdict, number, and superlative names its subject and is complete on its own ("Acme returns 78 fields, the most of any tool tested"), so a chunk lifted without its heading is still attributable; in comparisons name the other tool too. Keep connective prose natural — don't robotize the whole piece
- **A concrete detail or stat roughly every 150-200 words**
- **Honest asterisks travel with their numbers**: worker counts behind speed figures, default-config assumptions, per-tier quirks

### Dual ratings — never self-assigned
Everywhere a tool is introduced: third-party user rating (G2 / Capterra / Trustpilot — source + review count + link, dated) + our /10. Never a self-assigned star rating, never a "user rating" row sourced from nowhere. Independent corroboration is what makes the scorecard citable.

### Radical honesty about lobstr.io
- Always include real, named trade-offs — quirks, missing filters, buggy fields, slow modes. Every tool has them.
- Where a flaw is being worked on, say so: "On the fix list"
- The scorecard must show where lobstr.io LOSES. A page where the house brand wins every category is the pattern answer engines (and readers) discount — the losses are what make the wins believable.

### Radical honesty about competitors
- When a competitor genuinely excels, say so clearly — in the summary bullet, the table, the deep dive, AND the FAQ
- Then ground it: does this strength actually matter for most readers' use case?
- Every criticism needs evidence from your test: a number, a screenshot, a verified check

### Pricing math
- Always calculate **cost per 1,000 results**, at **entry → scale**, per configuration tier
- If a tool has confusing pricing (runtime-based, compute units, credit tiers), do the math for the reader and show your work — and label test-derived ratios "based on this run"
- Stack the full workflow too: what does a complete record cost with everything switched on?
- Call out hidden costs: paid filters, compute layers on top of per-row rates, expiring credits, overage charges
- State the anchor-job total for every ranked tool

### Scale math
- Always compute the 24/7 monthly ceiling: speed × 43,200 minutes × concurrency, per tier, default config
- Report paper vs real ceilings both when they diverge
- lobstr.io: headline number is the **single-Slot** ceiling (stated as the most modest estimate), then the per-Squid tier (× 20 Slots) and account-wide tier (× 100 Slots, top plan) explicitly labeled. Never "up to 100 Slots" without the per-account qualifier (see `facts.md`)
- Translate to real jobs: "To pull 100,000 reviews takes 6.7 hours; 1M takes 2.8 days."

### Comparison tables
- The master table appears exactly ONCE, with a jump link from the ranked-tools section
- Bold the winning value in every row; numbers in cells, not adjectives
- Use emojis for quick scanning: ✅ ❌ ⚠️ — as decoration next to values, never replacing a number
- Annotate ticks with the detail that matters: "✅ (free)" / "✅ (paid)" / "⚠️ via URL" / "⚠️ (missed ~36%)"
- Keep column headers short

### Field-set tables
- Group fields by category with emoji labels: ✍️ Review content, 👤 Reviewer, ❤️ Engagement & owner, ⭐ Sub-ratings, 🏪 Place/Business, 🛡️ Trust signals, ⚙️ Job metadata
- Field names in backticks
- Mark exclusive fields with 🎁 and known-buggy ones with 🐛 (sparingly)

### The "What sucks" energy
- Don't sugarcoat. If a tool is slow, say "Slow" — then prove it: "236 results took 70+ minutes and the run never finished."
- "A clean feature list and the cheapest price on the page mean nothing if the run never finishes."
- This is where your credibility lives

### Cluster links
Cross-link the platform cluster: the matching "[X] API" article and any vs/alternatives pages where they exist. All links carry `https://` schemes and descriptive anchors — never "click here" or a bare domain.

---

## What the Reader Gets

Every listicle must deliver:
1. A clear winner with honest, **measured** reasoning — every claim backed by a number from a real test, every score traceable to the stated method
2. Fair treatment of every tool — strengths AND weaknesses, including the cut tools
3. Real pricing and scale math they can plug their own volume into (the anchor job)
4. Verifiability — the repo/Sheets links that let them check the numbers themselves
5. Enough detail to choose without testing every tool themselves
6. Trust — because you were honest about lobstr.io's limitations too, and you showed your work
