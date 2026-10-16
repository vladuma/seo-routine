# GEO observation and referral outcomes

GEO measures visibility and accuracy in AI answers. A controlled prompt panel is an **instrument**, not a
sample of market demand and not a measure of any engine's market share. Read the current panel, version
and source settings from config. Historical scorecard rows remain dated observations.

## Fixed panel

Use the configured exact prompts with their fixed IDs and intent labels. Cover commercial comparison,
provider-specific setup and how-to, privacy or constraint scenarios, and the problem your product solves.
A missing tutorial citation is a valid visibility gap. Changing "how to" into "best tool" after a miss
changes the experiment. Version any change to the panel, model or settings, keep the old baseline, and
run an overlap comparison where useful.

Record the engine and provider, the actual model and version, the date, prompt, sample ID, settings,
whether retrieval was requested and whether it was observed, the answer text and the cited URLs. Repeated
samples from the same model expose variability. They are not independent draws from your customers. If
sources permit, corroborate important gaps with another engine or a localized live AI overview, and state
the engine/country/device matrix you actually covered.

Choose a sample size for the decision. A level estimate needs more samples than a change detector, and a
prompt whose answers are bimodal (named in some samples, absent in others) is unreadable at n=3. Keep
sample sizes in separate series: never present an n=3 and an n=10 figure as one trend.

Hold the requested-sample denominator fixed. Failed calls, unanswered prompts, nonretrieval answers,
uncited brand mentions and citations to other domains each get an explicit status. Report coverage and
per-prompt results instead of dropping misses, carrying old wins forward as fresh data or averaging
unlike panels. Requested web search does not prove retrieval: establish it from tool output or citations,
not from token count. Training-only answers still describe that engine's behavior but stay separate from
retrieval-conditioned citation rates.

Record whether the brand is named, its recommendation position if the answer genuinely ranks options,
the cited URL, and whether price and capability claims match current authoritative product data. "12 of
12 tested answers named us" is an observation about those samples, not 100% market visibility. A
pre-existing first place is a maintenance baseline, not a growth achievement.

Repeated retired claims justify tracing the cited source. The cause is often a forgotten crawlable file
(an old pricing markdown, a static text route) rather than a stale model cache: sweep `public/`-style
paths and text routes, not just the article templates. A crawl or date change cannot guarantee that an
external model's cache refreshes, and a lastmod bump is not a proven refresh mechanism.

Impersonating or scraped copies of your site are not competitors. Keep them out of the competitor set and
do not spend analysis time on them. A one-line note when one appears in a panel answer is enough.

## Connect visibility to acquisition

Use the analytics contract in [measurement](measurement.md): distinct AI-referred entry visits by exact
referrer host and landing page, completed signup where observable, and separately verified activation
and paid outcomes. Publish them alongside the panel results. Direct and unknown visits remain
unattributed, so recorded AI referrals are an observable subset, not total AI influence. Do not use total
site sessions or login intent as AI acquisition success. Save referral and outcome denominators and
attribution windows explicitly.

Monthly keyword-demand or corpus-based share-of-voice tools may supplement the panel when they are
enabled and available. Do not turn on a paid add-on the owner declined to fill a reporting cell. Record
the vendor, corpus and methodology before calling a metric "share of voice". GSC already includes some AI
search surfaces, so it cannot be treated as a mutually exclusive channel without checking that source's
semantics.

## Reader and citation improvements

Choose changes from observed gaps: accurate direct answers, concrete setup steps, honest comparison
criteria, tables where they help, primary-source citations, original evidence and clear product
limitations. Preserve factual publication dates. Schema must describe visible content and the Google
eligibility that applies. FAQ markup is not a general rich-result strategy for a SaaS site.

Generated `/llms.txt` and `/llms-full.txt` routes are project surfaces: verify their published content
after changes and do not maintain an independent, stale price or capability copy. Their existence is not
a verified ranking lever. Treat research-derived GEO techniques ([geo-research](geo-research.md)) as
hypotheses that need local evidence, never as guaranteed percentage uplifts.

Write raw observations and per-prompt failures to the dated run's `inputs/`, append a clearly versioned
summary to `geo-scorecard.md` when this phase runs, and link any experiment from the ledger. A separate
accuracy or maintenance score is appropriate once citation prominence already meets its target.

`scripts/geo_panel.py` runs the panel through DataForSEO's LLM responses endpoint and writes the raw JSON
receipt plus a markdown summary, so a reading is reproducible from a command and a file instead of
terminal scrollback. The panel definition lives in a JSON file named by `geo.panel_file` in config.
