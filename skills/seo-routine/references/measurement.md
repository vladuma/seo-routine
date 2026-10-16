# Measurement contract

How to collect, reconcile and interpret traffic and outcome data. Every number in an analysis must be
traceable to a saved input, and a source that failed is a gap, never a zero.

## Collect and reconcile

Capture site totals, landing-page acquisition, branded demand and business outcomes separately. Compare
complete, equal 7-day and 28-day windows, plus a longer daily trend, before calling a weekly decline a
sustained reversal. Save sanitized machine-readable inputs, collector arguments and version, and any
failures into the run's `inputs/` folder. Anything quoted in an artifact must come from a file there.

```bash
set -a && source .env.seo && set +a && python3 scripts/gsc.py --days 7 --compare --dimension property --brand-regex "<regex>" --json
set -a && source .env.seo && set +a && python3 scripts/gsc.py --days 28 --compare --dimension query,page --limit 25000 --brand-regex "<regex>" --json
```

`gsc.py` accepts an inclusive `--end-date YYYY-MM-DD` and, with `--json`, emits property totals, the
query partition, query coverage and the row-cap state even when you request dimensions. Do not replace
collector definitions with ad hoc queries that silently change the unit of measurement. If the analytics
source has no bundled collector, write one that states its windows, unit and timezone, and save its
output the same way.

## Google Search Console

- Query search type `web` with `dataState=final`. Probe freshness and anchor both windows on the latest
  finalized date. An all-state freshness probe may expose `firstIncompleteDate`, which is excluded.
  GSC date boundaries are Pacific time. Record that and any difference from the analytics timezone.
- Request a dimensionless property aggregate for headline clicks, impressions, CTR and position. Page rows
  aggregate by URL and can exceed property totals. Query rows omit anonymized and other unreturned data.
- Report a transparent brand-regex bucket and a visible-nonbrand bucket **plus unknown query coverage**.
  Unknown clicks = unfiltered property clicks − both query-filtered click totals. Never call the residual
  nonbrand. Save query coverage for clicks and impressions; a query filter excludes anonymized queries.
  A brand regex is a text classifier. It does not prove brand awareness, distinct searchers or intent,
  and a phrase that is also generic English (two ordinary words) will over-match.
- Fetch page, query, query×page, device and country breakdowns as needed. Record row limits and
  pagination or truncation. A top-N table is not an exhaustive total, and **a query missing from a
  truncated pull is not absent**: before claiming a query does not rank, pull deep enough to contain it
  (thousands of rows, then grep) rather than the default top 100.
- Use exact query×page metrics for target keywords. A page average near #7 cannot establish a head
  query's rank, and a shifting query mix can improve average position while clicks fall.
- Separate descriptive click decomposition (impressions × CTR) from causal explanation. Low CTR alone
  establishes neither AI Overview displacement nor a bad title. Inspect the actual SERP for that
  query, location and device, distinguish organic rank from ads and AI answers, and record result depth
  and timestamp.
- Flag prompt-like or tool-generated queries separately. Compare probe prompts and times before
  attributing them to the routine itself; their presence alone proves neither human demand nor
  self-contamination.

Primary semantics: [Search Analytics API](https://developers.google.com/webmaster-tools/v1/searchanalytics/query),
[query privacy and dimensions](https://support.google.com/webmasters/answer/17011259),
[property versus page aggregation](https://support.google.com/webmasters/answer/17011364).

## Analytics acquisition and outcomes

Use the authoritative host and source in config, never a stale export. Define the unit once: acquisition
cohorts count distinct **visits**, not pageviews and not browser sessions that span many visits.

Define visit entry from the earliest pageview in the visit and keep its referrer. Determine entry on the
complete retained visit *before* assigning it to a reporting window and *before* filtering to marketing
paths. Otherwise a returning product user's later blog pageview becomes a fabricated acquisition entry.
Use half-open timestamps `[start, end)` and complete days. State whether GSC alignment uses Pacific or
the analytics source uses another named timezone.

Classify referrers by parsed hostname and explicit source rules. Google means `google.com` or a validated
Google country domain, not arbitrary text containing `google`. AI sources use an explicit hostname
allowlist. Treat same-site referrers separately. A host that fails to parse stays unknown, and
direct/unknown is not AI traffic. Preserve the raw classification reason in sanitized output.

Report these separately for each cohort and for the all-content aggregate:

- Entry visits, split into Google organic, known AI referrers and direct/other.
- Distinct visits with login intent, completed signup, activation and paid conversion **as distinct
  events**, only when their actual event definitions and linkage exist. A `/login` pageview or CTA click
  is login intent, not a signup. A missing signup linkage is an instrumentation gap to record.
- Where privacy-safe identifiers allow it, separate new customers from returning users. Do not infer
  "new user" from a fresh visit alone. State the lookback and cross-visit attribution window.

The all-content aggregate always retains every eligible entry visit. A predeclared acquisition subset may
exclude informational pages, but show its numerator, denominator, included paths and definition version
next to the unchanged aggregate. Page prioritization never rewrites historical totals.

## CTA and event instrumentation

Read the project's analytics event contract before querying event data. A "shown" event that fires on
component mount is a **mount** event, not evidence the element entered the viewport. Label it as mounted,
keep its original series, and use a separately versioned viewport event for new exposure measurement.
Never join a new viewport numerator to an old mount denominator, never treat event occurrences as unique
people, and keep placement and content versions apart. Define exposure and click dedup at the
collector's documented unit, and count exposed visits and matching clicked visits consistently.

Small samples need counts and uncertainty. One login-intent visit out of 24 establishes no conversion
ceiling, no significance and no permanent failure. An observational before/after change can reflect
seasonality, distribution, incidents or query mix. Name those limits when interpreting it.

## Opportunity evidence

For each candidate record the target query and page, affected acquisition count, business relevance, the
mechanism, primary evidence, the most plausible alternative cause and an observation that would refute
the mechanism. Rank against the priorities in config. Omit invented keyword volume and composite
precision when sources are missing. Verify crawl and indexing defects before suggesting content churn.

A page-level fix is not a ranking or traffic claim. Before funding a sweep ("N pages contain the bad
phrase"), check the premise against the **live rendered surface**: a raw source grep cannot tell your own
claim from a competitor's name or a quoted definition. A claim about a whole estate is only as good as
its path list, so include generated and static surfaces (text routes, `public/` files, feeds) in it.

Crawl only the public URLs you need, honor source limits (GSC ≤5 requests/s, DataForSEO ≤2/s, own site
≤2/s) and back off on throttling. A failed source stops its dependent conclusion. Independent analysis
may continue.

## Technical checks and source failure

For a suspected technical cause, inspect a representative live set for response and redirects, canonical
and robots directives, sitemap coverage and lastmod, broken links, and rendered claims and schema.
Compare changes against actual deployment dates. Measure current Core Web Vitals when performance could
explain the symptom, and record device, field-versus-lab data and missing coverage. A local crawl or
build cannot establish Google indexing, and a 200 homepage does not establish backend health.

Distinguish a source fetch or auth failure from a valid empty dataset. Preserve successful independent
pulls, mark failed dependencies unavailable, and retry transient throttling with bounded backoff. Never
publish a completed comparison from an empty fallback or invent a value to fill a scorecard cell.
