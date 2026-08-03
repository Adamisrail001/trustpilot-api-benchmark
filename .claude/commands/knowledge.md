Build a knowledge.md through a structured interview for: $ARGUMENTS

This command interviews the writer section by section, researches what's researchable, and compiles `content/{articlefolder}/knowledge.md` — the single source of truth the writing commands consume. It does NOT write the article. It NEVER fills a gap with a guess: every fact is either writer-provided, research-with-source-confirmed, or explicitly marked `⚠️ MISSING`.

`$ARGUMENTS` is the article folder name or topic, optionally followed by the format: `howto` | `listicle` | `api` (alias: `scraper-api`).

## Step 0: The two fact classes (read this first)

Every question in every bank belongs to one of two classes. Never move a fact between classes.

- **🔴 Writer-provided.** Anything about a lobstr.io scraper or API (name, fields, settings, pricing, speeds, limits, quirks), any measured test result or benchmark number, any opinion/trade-off/pros-cons call, anything that positions lobstr.io, elimination decisions, step-by-step deviations. These come from the writer verbatim. If the writer doesn't have one, it becomes `⚠️ MISSING` — never an estimate, never "probably", never extrapolated from another tool.
- **🟡 Researchable.** Platform official APIs and their documented limits, platform ToS and the legal landscape, competitor public features/pricing/docs, user pain points on Reddit/forums/review sites, third-party ratings. Research these yourself (WebSearch first, WebFetch for specific URLs). Every researched fact carries its source URL and is presented to the writer as confirm/correct before it's marked confirmed. Unconfirmed research stays labeled `[unconfirmed research]`.

A number the writer gives from memory rather than a test ("it's fast, like 200/min ish") is not a measured result — record it with an `⚠️ UNVERIFIED` tag and ask whether they can run the test. Listicle and api articles are built on measured, logged numbers only.

## Step 1: Setup

1. Resolve the article folder under `content/` (folder name = article file name). If it doesn't exist, propose a name and confirm before creating anything.
2. Resolve the format. If not given and not obvious from the topic, ask: how-to / best-X-scrapers listicle / best-X-API benchmark. (Product updates, success stories, and vs/alternatives articles are not covered by this command yet — for a vs piece, stop and say so.)
3. Check `content/{articlefolder}/knowledge.md`:
   - **Absent** → fresh interview.
   - **Present** → NEVER overwrite silently. Read it, map its content onto the format's question bank, and enter resume mode: report per-section coverage (✅ filled / partial / empty), then interview only the gaps. Existing writer-provided content is preserved verbatim unless the writer revises it.
4. Read `facts.md` (repo root). Never re-ask anything it answers (catalog size, positioning line, Slots dimensions, export formats) and never copy its values into knowledge.md — reference it, so knowledge.md can't go stale when the product changes.
5. Check for a format methodology doc — first in the article folder (`criteria.md` or similar), then the repo root, then the format's instructions doc (`instructions/listicle_instructions.md` / `instructions/api_instructions.md`, both synced from Kritik). If one exists and is newer or more specific than this command's static bank, **it is authoritative**: reconcile before interviewing — adopt its criteria, sections, elimination rules, weights, and scoring; drop or demote whatever it demotes. Report the bank-vs-methodology deltas to the writer as command-update feedback, but run the interview against the methodology doc's structure. (Banks below were mined from the 2026-07-24 versions.)
6. Present the roadmap: the reconciled section list with each section's status (✅ from resume / 🔴 to ask / 🟡 to research). This is the writer's progress map for the whole interview.

Work ONLY from: the article folder, `facts.md`, the methodology docs named above, and files the writer explicitly hands you. Do not load `*_samples/` or other articles' folders. Never modify a published article, `*_final.md`, `*_db.json`, or `upload.py`.

## Step 2: Interview loop

Take the bank ONE SECTION at a time, in bank order:

1. **🟡 sections: research first.** Do the research, then present findings with source URLs as a confirm/correct list — the writer reacts instead of typing from scratch.
2. **🔴 sections: ask in one compact numbered block** — only that section's missing facts, nothing from other sections. Don't batch multiple sections of questions.
3. **Files beat typing.** If the section is grounded in an artifact (benchmark log, sample dataset, screenshot, docs URL), ask the writer to drop it in the article folder and extract from it. For a sample JSON/CSV: extract the field list, propose which fields are plumbing (internal IDs, run metadata) to exclude, and get the split confirmed.
4. **Write as you go.** After each section is settled, write it into knowledge.md immediately (create the file at the first settled section). An interrupted interview must leave a valid partial knowledge.md that resume mode can pick up.
5. The writer can answer "skip" (→ `⚠️ MISSING` marker, move on) or "later" (same marker, flagged in Open items) at any point. Never stall the interview on one hole.

Gap marker format, exactly: `⚠️ MISSING: {what} — {ask writer | needs test | needs research}`. Every marker is duplicated in the Open items section at the end of the file.

Arithmetic on writer-confirmed numbers (weighted aggregates, per-1k conversions, monthly ceilings) is yours to compute — show the math in the file. The inputs are never yours to invent.

## Step 3: Question banks

Each bank lists its sections in knowledge.md output order. 🔴/🟡 marks the fact class that dominates the section. Where a Step 1 methodology doc conflicts with a bank, the methodology doc wins.

### Bank: howto

1. **Article meta** — working title, folder/file names, main keyword, meta description (leave TBD — proposed at article time), companion dataset file if any
2. **The scraper** 🔴 — exact name, store URL + slug (builds the `#cta-link`), companion scraper for collecting input URLs (name + store URL) if one exists
3. **Task input rules** 🔴 — what one task is, accepted URL/input formats and required patterns, country/domain variants, per-run limits
4. **Settings** 🔴 — Basic settings table (setting → what it does, options, defaults), Advanced settings table, cross-setting quirks (e.g. a filter that disables other filters), end-of-run modes, relevant help-article links (`lobstr.crisp.help`)
5. **Data fields** 🔴 — full user-facing field list, ideally extracted from a sample dataset the writer drops in the folder (plumbing excluded, split confirmed); known field bugs or pending renames and how the article should handle them
6. **Pricing** 🔴 — free tier, entry price per 1k + plan name, at-scale price per 1k + plan name
7. **Step-by-step deviations** 🔴 — anything that differs from the standard 5-step Squid flow (Create a Squid / Add tasks / Adjust behavior / Launch / Enjoy); companion-scraper workflow; per-step notes worth calling out
8. **Official API** 🟡 — endpoint(s) + docs URLs, what it offers, the damning limits (caps, truncation, paid tiers, auth requirements, rate limits), schema gotchas readers would trip on
9. **Legal** 🟡 — ToS scraping clause: URL + verbatim quote; legality of scraping public data (jurisdiction-relevant precedent); platform-specific responsible-use notes
10. **Hook angle + pain points** 🟡 — Reddit/forum/review threads with URLs, which pain the hook should open on, broken tools readers have tried
11. **Use cases** 🟡 + 🔴 confirm — "what can you do with the data" ideas incl. Make.com/API/AI-agent angles; any unique fields or customer story the writer wants featured
12. **FAQ drafts** 🟡 — 5-8 Q&A pairs grounded ONLY in facts confirmed above
13. **Image plan** — generated from the structure: one line per required visual, section by section
14. **Open items** — auto-generated: every `⚠️ MISSING` and `⚠️ UNVERIFIED` in the file

### Bank: listicle

Mirrors `instructions/listicle_instructions.md` (v1.1 scoring: /10 per pillar, weighted aggregate — Data 2.0 · Usability 2.0 · Scalability 2.0 · Cost 1.8 · Speed 1.4 · Support 0.8; #1 = highest weighted score even when it isn't lobstr.io). Alternatives/head-to-head pieces are the vs format — not this bank.

1. **Article meta** — working title (`Best [X] Scrapers in [Year] ...`), main keyword, prior how-to to link, cluster links ([X] API article, vs pages) where they exist
2. **Tool roster + count claim** 🔴 — every ranked tool (exact actor/scraper name for marketplaces + who maintains it), the lobstr.io scraper + store slug, the longlist so count claims are accountable (ranked + disqualified + stated longlist), how candidates were discovered; per-tool third-party rating 🟡 (G2/Capterra/Trustpilot — source + review count + link, dated) writer-confirmed
3. **Benchmark record + evidence links** 🔴 — the standard job every tool ran (same input, same window, purchased plans), the anchor job (default 100K records), the public evidence: GitHub repo and/or per-tool verification Sheets URLs (or `⚠️ MISSING — needs publishing`)
4. **Eliminations (L1–L6)** 🔴 — per cut tool: which criterion (L1 core data failure · L2 no self-serve trial · L3 benchmark run failure · L4 uncomputable cost · L5 onboarding failure >48h · L6 dead/abandoned), reproduced-failure receipts (retried per the tool's own docs, both failures screenshotted), the measured numbers it posted before failing (for the scored cut-table), and "who it's right for"
5. **Data pillar** — owned by `/datacompare`: raw exports into `content/{articlefolder}/data/`, artifact numbers canonical (total AND meaningful field counts, usable ratio, fill consistency %, accuracy %, shape, freshness, exclusive fields). Collect for its config 🔴: when each output was captured (`captured_at` — staggered runs trigger the model's timing tiers) and which fields' values move over time (`volatile_fields`). Paid detail add-ons get a "worth it?" block: exact fields added, cost/speed deltas, "Skip it for… / Turn it on only if…" verdict 🔴
6. **Usability (per tool)** 🔴 — input flexibility (URL/query/ID/geo, bulk upload, strict-format traps), time-to-first-result + workflow gotchas as findings, each paid toggle documented (what it adds/costs/slows), broken-feature forensics (documented toggles tested with vs without — did it change anything?), filter matrix rows (✅ free / ✅ paid / ⚠️ via URL / ❌ per filter), exports & integrations, automation
7. **Speed (per tool)** 🔴 — measured wall-clock on the standard batch, per tier (base AND full-data), stopwatch vs vendor claim side by side, effect of user-controlled concurrency, ranges only when logged variance demands
8. **Cost (per tool)** 🔴 — pricing model, bundle cost per 1k at entry AND scale per configuration tier, add-ons/chains/filter costs itemized, anchor-job total, crossover points where rankings flip with volume, billing fairness, free-tier value, test-derived pricing labeled "based on this run"
9. **Scalability (per tool)** 🔴 — monthly ceiling = measured rate × 43,200 min per tier at a declared default config, paper vs real ceiling when they diverge, workers behind quoted rates disclosed, maintenance + data-loss behavior (pause+partial vs lost-on-failure; who maintains marketplace actors), lobstr.io math per the Slots dimensions in `facts.md`: single-Slot headline, per-Squid, per-account — always labeled
10. **Support (per tool)** 🔴 — primary: identical ticket to every ranked tool, timestamps logged; fallback: published response stats + review sentiment, stated as the method used; actor-scoped for marketplace tools, never platform-wide; note when support's answer contradicts measured reality
11. **Scorecard + lobstr.io trade-offs** 🔴 — per-pillar /10 scores with one-line reasoning, weighted aggregate computed and shown (weights above), anti-double-counting check, ranking; lobstr.io's named real cons + which are on the fix list
12. **Official API bridge (conditional)** 🟡 — 100-200 words of fodder when the API situation frames the buying decision; link the matching [X] API article if it exists
13. **Legal** 🟡 — jurisdiction-specific: ToS quote + URL, named case law relevant to the platform's home turf (hiQ for US; L342-3 / Entreparticuliers v. Leboncoin for French), collection-vs-use risk framing, responsible-use notes
14. **Hook + pain points** 🟡 — community receipts with URLs (they justify the criteria later), the angle
15. **FAQ drafts** 🟡 — the five query buckets (superlative / use-case / qualifier / entity / intent variants), each answer opening with a verdict + number, incl. the reproducibility Q
16. **Store / links** — store URLs, CTA links, repo/Sheets links, raw dataset links to publish
17. **Open items** — auto-generated gap list

### Bank: api

Mirrors `instructions/api_instructions.md` (X API Testing Methodology v1.0, synced from Kritik — Kritik's config is upstream source of truth). Scope: official API + internal/hidden API + minimum 2-3 fully benchmarked third-party APIs. Winner = highest weighted score, no exceptions. Reproducibility is the moat: every number must trace to a logged run in the public gist/repo.

1. **Article meta** — working title (`Best {X} API for Scraping Data at Scale [Year Benchmark]`), slug `/{x}-api/`, main keyword, target data type, the full roster (official + internal + third-party APIs), matching no-code listicle to cross-link
2. **Benchmark methodology record** 🔴 — the fixed input dataset (what, size, how chosen), the test window, the shared script template, what was logged, and the public gist/repo URL (or `⚠️ MISSING — needs publishing`; remind: `scripts/.env` and any keys stay out of the gist)
3. **Eliminations (E1–E6)** 🔴 — per disqualified API: criterion (E1 no self-serve access · E2 benchmark run failure <50% · E3 no usable docs · E4 uncomputable cost · E5 platform coverage failure · E6 dead/abandoned), one-line reason, evidence link
4. **Official API deep-dive** 🟡 + 🔴 — what it actually offers organized by what readers want to extract; auth model + real access friction (tested or cited from recent dev reports); 2-3 legitimate use cases; a working code example the writer actually ran + sanitized response 🔴; exact rate limits/quotas 🟡 + what they mean in practice ("at {limit}, 100K records takes {time}"); field-gap mini table (5-10 page-visible fields vs what the API returns); cost-at-scale arithmetic; ToS/access ceilings; THE wall (the single blocker)
5. **Internal (hidden) API** 🔴 — conditional: endpoints discovered via DevTools (sanitized examples), the anti-bot system by name + block-screen screenshot, the maintenance tax, why it dies at scale — or a conscious skip with the reason
6. **Success rate & reliability (per API)** 🔴 — success % on the 1K-request benchmark, empty/partial response rate, error handling quality (codes, safe retries, what a failure costs), stability during the window; data retention + abort/pause/resume + data-loss scenarios hit
7. **Data quality & completeness (per API)** — owned by `/datacompare` (API outputs as named scrapers): field coverage vs ground truth, accuracy, schema consistency, freshness; writer does the live spot-check. Collect for its config 🔴: when each output was captured (`captured_at` — staggered runs trigger the model's timing tiers) and which fields' values move over time (`volatile_fields`)
8. **Cost efficiency (per API)** 🔴 — pricing model (per result vs per request — and what one request returns), cost per 1K successful records entry → scale incl. chained endpoints, billing fairness (failed/empty charged?), free tier/trial credits, pricing transparency
9. **Speed & throughput (per API)** 🔴 — median latency per request, wall-clock for the 1K batch, p95 under load, async/batch endpoint availability
10. **Scalability (per API)** 🔴 — documented rate limits & max concurrency vs what actually happens at the limit, degradation at 10× volume, volume caps blocking production use
11. **Developer experience (per API)** 🔴 + 🟡 — docs quality/llms.txt/MCP/SDKs researched 🟡 with URLs; time-to-first-successful-request, error message clarity, support responsiveness, and what fought back — writer's hands-on take 🔴
12. **Input flexibility & coverage (per API)** 🔴 + 🟡 — accepted input types (URL/ID/query/geo-filters), endpoint breadth for the platform, enrichment/related endpoints
13. **Scorecard** 🔴 — per-criterion scores against the weighted rubric (Reliability 2.0 · Data 2.0 · Cost 1.5 · Speed 1.5 · Scalability 1.2 · DX 1.0 · Input 0.8), sub-criteria detail to the gist, weighted aggregate computed and shown, verdict bands, winner + honest use-case slots for the rest (incl. lobstr.io's real placement)
14. **Winner quickstart facts** 🔴 — auth (how to get the key, real sanitized header), setup, run + progress tracking, results retrieval + automation options — every snippet actually run by the writer
15. **Concept explainer choice** 🔴 — THE one concept that gates the reader's decision (sync vs async, ID vs URL inputs, official vs internal vs third-party) + the facts for its comparison table
16. **Legal FAQ block** 🟡 — one neutral, factual, platform-specific block: ToS quote + URL, jurisdiction-relevant precedent
17. **FAQ drafts** 🟡 — required Qs (official vs scraping APIs, cost at scale, reproducibility → gist link) + 2-3 platform-specific from People Also Ask
18. **Store / links** — docs URLs per API, lobstr.io store/CTA links, gist/repo, matching listicle
19. **Open items** — auto-generated gap list

## Step 4: Compile + gap report

When the last section is settled (or the writer says "wrap it up"):

1. Ensure knowledge.md opens with: `> This file is the article's single source of truth. Facts here are writer-provided or research-confirmed; ⚠️ markers are unresolved gaps — the writing command will stop on them.`
2. Verify every section of the bank exists in the file — filled or carrying its `⚠️ MISSING` marker.
3. Regenerate Open items from the actual markers in the file.
4. Present the writer a final gap report: confirmed sections, open markers, and which markers would block the article (a how-to can't ship without pricing; a listicle can't ship without measured speeds; an api article can't ship without the gist and per-criterion benchmark numbers).
5. Tell the writer the next step: the matching writing command — or `/datacompare {articlefolder}` first if the Data pillar is still open.

## Step 5: Mandatory self-review (do not skip)

Output PASS or FAIL per item, with the offending line on any FAIL; fix and re-run before presenting:

1. Every 🔴 fact in the file traces verbatim to the writer (this interview or the pre-existing knowledge.md) — nothing inferred, averaged, or extrapolated
2. Every 🟡 fact carries a source URL and is either writer-confirmed or still labeled `[unconfirmed research]`
3. Zero invented numbers; every non-measured figure carries `⚠️ UNVERIFIED`; every benchmark number names its logged evidence (gist/repo/Sheet) or carries a MISSING marker for it
4. Evergreen facts referenced from `facts.md`, not copied into the file
5. Every bank section present — filled or explicitly `⚠️ MISSING`, and Open items matches the markers in the body one-to-one
6. Data-pillar numbers come from the `/datacompare` artifact or are marked MISSING — none hand-computed
7. Any Slots/concurrency claim names its dimension per `facts.md`
8. Scorecard math uses the format's declared weights; aggregates recomputed correctly from writer-confirmed criterion scores, work shown
9. Nothing outside `content/{articlefolder}/knowledge.md` was created or modified (no article files, no `_final.md`, no `_db.json`)
10. Resume mode preserved all prior writer-provided content verbatim unless the writer revised it
11. The file opens with the source-of-truth header line

Present the gap report and checklist results together. The interview is done when the writer says so — open markers are allowed to remain; they are the point.
