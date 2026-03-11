---
name: seo-routine
description: Data-driven weekly SEO optimization routine with prediction tracking. Run /seo-routine calibrate to set up, then use analyze → plan → implement → review cycle for continuous SEO improvement. Use when user says "seo routine", "weekly seo", "seo cycle", "seo analyze", "seo plan", "seo implement", "seo review", "seo calibrate", "seo status", or "seo goals".
---

# SEO Routine — Weekly Optimization Engine

Data-driven weekly SEO optimization cycle: **analyze → plan → implement → review**.
Tracks predictions vs actuals to learn what works for each specific site.

## Command Router

Parse the user's command to determine which phase to execute:

| Command | Phase |
|---------|-------|
| `calibrate` | Phase 0: Discover project, generate config |
| `analyze` | Phase 1: Collect data, score opportunities |
| `plan` | Phase 2: Select top items, create weekly plan |
| `implement` | Phase 3: Execute plan in git worktree |
| `review` | Phase 4: Compare predictions vs actuals |
| `status` | Quick: Show current state |
| `goals "..."` | Quick: Set/update strategic goal |

If no subcommand is given, run `status`.

---

## Configuration Loading

**Every phase starts by loading config.** Read the config in this order:

1. Check Claude memory `memory/seo/state.md` for the configured `root` path
2. If no state.md, search for `**/seo-config.md` in the project
3. If no config found, tell user to run `calibrate` first

**Parse config:** Read the `seo-config.md` file. Extract the YAML block inside the ` ```yaml ` fence. All paths in the config are relative to the project root unless they start with `/`.

**Load effective scoring weights:** Check `memory/seo/learnings.md` for an `## Effective Weights` section. If found, use those weights. Otherwise, use weights from `seo-config.md` `scoring_weights`.

**Determine current week:** Use ISO week format `YYYY-WNN` based on today's date.

---

## Phase 0: Calibrate (`/seo-routine calibrate`)

### Step 1 — Auto-Discovery (No Questions)

Scan the project silently to detect:

```
# Content files
Glob: **/*.md, **/*.mdx, **/articles/*.js, **/content/**, **/posts/**

# CMS detection
Glob: **/strapi/**, **/wordpress/**, **/contentful/**
Read: package.json (check dependencies for strapi, @contentful/*, etc.)

# SEO infrastructure
Glob: **/sitemap.ts, **/sitemap.xml, **/robots.txt, **/schema.*, **/llms.txt/**

# Framework detection
Read: package.json (next, nuxt, astro, gatsby in dependencies)

# Analytics
Grep: GA4|gtag|umami|plausible in **/*.{ts,tsx,js,jsx,env*}

# Project context
Read: CLAUDE.md, package.json
```

Build an internal discovery map from the results. Do NOT ask questions during this step.

### Step 2 — Targeted Questions (3-5 max)

Ask the user these questions (skip any already answered by auto-discovery):

1. **Site production URL** — e.g., `https://example.com`
2. **SEO data root directory** — where all SEO files will live (default: `docs/seo/`, alternatives: `seo/`, `marketing/seo/`). All generated files, weekly reports, and inputs live under this root.
3. **Top 3 competitors** — domain names
4. **Available data sources** — present checkboxes pre-filled from auto-detection:
   - [ ] Google Search Console (GSC)
   - [ ] Google Analytics 4 (GA4)
   - [ ] Umami
   - [ ] DataForSEO
   - [ ] Ahrefs (manual CSV or API)
5. **Current strategic goal** (optional) — e.g., "Rank top 5 for 'sync google calendars'"

### Step 3 — Credential Verification

For each enabled data source, check if required environment variables exist:

| Source | Required Env Vars | Setup Instructions if Missing |
|--------|------------------|-------------------------------|
| GSC | `GOOGLE_APPLICATION_CREDENTIALS` | "Create a GCP service account with Search Console read access, download JSON key, set GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json" |
| GA4 | `GOOGLE_APPLICATION_CREDENTIALS` | Same as GSC, plus add Analytics read access to the service account |
| Umami | `NEXT_PUBLIC_UMAMI_URL`, `NEXT_PUBLIC_UMAMI_WEBSITE_ID` | "Set NEXT_PUBLIC_UMAMI_URL to your Umami instance URL and NEXT_PUBLIC_UMAMI_WEBSITE_ID to the website ID" |
| DataForSEO | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | "Sign up at dataforseo.com, set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD env vars" |
| Ahrefs (API) | `AHREFS_API_TOKEN` | "Get API token from ahrefs.com/api, set AHREFS_API_TOKEN" |

```bash
# Check env var existence (example)
echo "GSC: ${GOOGLE_APPLICATION_CREDENTIALS:+configured}"
echo "DataForSEO: ${DATAFORSEO_LOGIN:+configured}"
```

Mark sources with missing credentials as `enabled: false` with a comment explaining what's needed.

### Step 4 — Generate Config

Write `{root}/seo-config.md` using the template from `templates/seo-config.md`, filled with discovered and user-provided values.

### Step 5 — Scaffold Directory Structure

Create all required files under the configured root:

```
{root}/
  seo-config.md          # already written in step 4
  goals.md               # from templates/goals.md (fill if user gave a goal)
  scorecard.md           # from templates/scorecard.md
  forward-log.md         # from templates/forward-log.md
  brand-voice.md         # from templates/brand-voice.md (only if content pipeline detected)
  weeks/
    .gitkeep
```

Create Claude memory files:

```
memory/seo/
  state.md               # root path, calibration date, no runs yet
  learnings.md           # empty with section headers: ## Learnings, ## Effective Weights, ## Historical Summary
  keyword-tracker.md     # empty with headers: | Keyword | W-4 | W-3 | W-2 | W-1 | Current | Trend |
```

**If `{root}/` already exists (re-calibration):** Only overwrite `seo-config.md`. Preserve all other files.

---

## Phase 1: Analyze (`/seo-routine analyze`)

### Step 1 — Setup

1. Load config (see Configuration Loading above)
2. Determine current week `YYYY-WNN`
3. Create directory `{root}/weeks/YYYY-WNN/` if it doesn't exist
4. Create `{root}/weeks/YYYY-WNN/inputs/` if it doesn't exist

### Step 2 — Collect Data (Parallel)

Launch multiple independent `Agent` tool calls in a single message for concurrency. Each agent collects from one data source:

**Agent 1: GSC Data** (if enabled)
```bash
# Use Google Search Console API via service account
# Fetch: clicks, impressions, CTR, avg position per page and per query
# Time range: last 7 days vs previous 7 days
# Use the Google APIs Python client or curl with OAuth2 token
```

Collect for all pages: clicks, impressions, CTR, average position for last 7 days and previous 7 days. Calculate deltas.

**Agent 2: Analytics Data** (Umami or GA4, if enabled)
```bash
# Umami: curl the Umami API for page views, bounce rate, session duration
# GA4: Use Google Analytics Data API for the same metrics
```

**Agent 3: DataForSEO** (if enabled)
```bash
# Use the bundled scripts for keyword research and SERP analysis
python3 scripts/serp_analysis.py --keywords "keyword1,keyword2" --location 2840
python3 scripts/competitor_gap.py --domain "example.com" --competitors "comp1.com,comp2.com"
```

Rate limit: max 2 requests/sec, exponential backoff on 429 (1s, 2s, 4s, max 3 retries).

**Agent 4: Self-Crawl** (always runs)

Crawl the site based on `self_crawl.scope` config:
- `sitemap`: Fetch sitemap, crawl up to `max_pages` URLs
- `scored`: Only crawl pages that appear in GSC/analytics data
- `manual-list`: Crawl URLs from config

For each page, check:
- Schema markup (valid JSON-LD?)
- Meta tags (title, description, og:image, canonical)
- Content length (word count)
- Internal links count
- Heading structure (H1, H2, H3 hierarchy)
- Image alt text coverage

```bash
# Fetch and parse each page
curl -sL "{url}" | python3 -c "
import sys, re
html = sys.stdin.read()
# Extract and validate schema, meta, headings, links, images
"
```

Core Web Vitals via PageSpeed Insights API (unless config says `lighthouse`):
```bash
curl -s "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url={encoded_url}&strategy=mobile&category=performance"
```
Rate limit: 1 request/sec, 3s backoff on 429.

Self-crawl of own site: 500ms delay between requests.

**Agent 5: Manual Inputs** (if files exist in `inputs/`)

Read any CSV/PDF/markdown files dropped in `{root}/weeks/YYYY-WNN/inputs/`:
- Ahrefs CSVs: parse organic keywords, backlinks
- `notes.md`: include user notes in analysis

### Step 3 — Score All Opportunities

Apply the **Composite Scoring Model** to every page and keyword opportunity:

#### Signal 1: Striking Distance (default weight: 25%)
```
if position in [5, 10] and impressions >= 100/week:
    score = 100
elif position < 5:
    score = 50  # already ranking well
elif position in (10, 20]:
    score = linear_scale(position, 10→100, 20→0) * min(impressions/100, 1.0)
elif impressions < 10/week:
    score = 0
else:  # position > 20
    score = 0
```

#### Signal 2: CTR Gap (default weight: 20%)

Expected CTR by position (AWR benchmarks):
| Position | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|----------|---|---|---|---|---|---|---|---|---|----|
| Expected | 31% | 16% | 11% | 8% | 7% | 5% | 4% | 3.5% | 3% | 2.5% |

```
score = max(0, (expected_ctr - actual_ctr) / expected_ctr * 100)
```
High score = page underperforming its position.

#### Signal 3: Content Quality (default weight: 15%)

Checklist-based scoring:
- Word count < 800: +30
- No FAQ section: +20
- No schema markup: +15
- No internal links: +15
- Missing meta description: +10
- No images: +10

Sum capped at 100. High score = more content issues to fix.

#### Signal 4: Technical Debt (default weight: 15%)

Checklist-based scoring:
- Missing canonical: +25
- Missing schema: +20
- Broken meta tags: +20
- No og:image: +15
- Missing alt text on images: +10
- Core Web Vitals issues (LCP > 2.5s or CLS > 0.1): +10

Sum capped at 100.

#### Signal 5: Keyword Gap (default weight: 15%)
```
For each keyword where a competitor ranks in top 20 and we don't:
    score = (competitor_impressions / max_impressions) * 100
Use the top gap keyword's score.
```

#### Signal 6: Goal Alignment (default weight: 10%)
```
Read goals.md. If page URL matches target_pages or keyword matches target_keywords:
    score = 100
Else:
    score = 0
```

#### Final Composite Score
```
final = sum(signal_score * weight for each signal) / sum(weights)
Normalize to 0-100.
```

### Step 4 — Identify Top Movers

Compare this week's data with last week's analysis (if exists):
- **Improved:** Pages that moved up 3+ positions or gained 20%+ clicks
- **Declined:** Pages that dropped 3+ positions or lost 20%+ clicks

### Step 5 — Write Analysis

Write `{root}/weeks/YYYY-WNN/analysis.md`:

```markdown
# SEO Analysis — YYYY-WNN

**Generated:** YYYY-MM-DD
**Data sources used:** GSC, Umami, DataForSEO, Self-crawl
**Pages analyzed:** N

## Top Opportunities (by composite score)

| Rank | Page/Keyword | Score | Top Signal | Position | Clicks | Impressions | CTR |
|------|-------------|-------|-----------|----------|--------|-------------|-----|
| 1 | /blog/example | 87 | Striking distance | 7 | 45 | 1200 | 3.8% |
| ... | | | | | | | |

## Top Movers

### Improved
| Page | Position Change | Click Change | Why |
|------|----------------|-------------|-----|

### Declined
| Page | Position Change | Click Change | Possible Cause |
|------|----------------|-------------|---------------|

## Technical Issues Found

| Page | Issue | Severity | Details |
|------|-------|----------|---------|

## Keyword Gaps

| Keyword | Our Position | Best Competitor | Their Position | Opportunity Score |
|---------|-------------|----------------|---------------|-----------------|

## Data Gaps

List any data sources that were unavailable or returned errors.

## Raw Data Summary

<details>
<summary>GSC Data (last 7 days)</summary>
[Full table of all pages with metrics]
</details>

<details>
<summary>Self-Crawl Results</summary>
[Technical audit results per page]
</details>
```

Update Claude memory:
- `memory/seo/state.md`: update last analyze date, current week
- `memory/seo/keyword-tracker.md`: update keyword positions

---

## Phase 2: Plan (`/seo-routine plan`)

### Step 1 — Load Context

1. Load config
2. Read `{root}/weeks/YYYY-WNN/analysis.md` — if doesn't exist, tell user to run `analyze` first
3. Read `{root}/forward-log.md` — identify pages touched in last 3 weeks (skip these)
4. Read `{root}/goals.md` — factor goals into selection
5. Read `memory/seo/learnings.md` — avoid repeating past mistakes

### Step 2 — Select Opportunities

From the analysis, select the top opportunities within the weekly budget:
- **Content changes:** 3-5 items (from `weekly_budget.content_changes`)
- **Technical changes:** 2-3 items (from `weekly_budget.technical_changes`)

**Selection rules:**
- Skip pages in the forward-log that were touched in the last 3 weeks
- Prioritize by composite score (highest first)
- Ensure mix of quick wins (striking distance) and strategic plays (goal alignment)
- If a goal is active, at least 1 item should be goal-aligned

### Step 3 — Classify and Specify

For each selected item, determine:

| Classification | Examples | QA Level |
|---------------|---------|----------|
| Content-only | Rewrite meta, add FAQ, improve E-E-A-T, add schema to content | Diff review (lightweight) |
| Technical | Edit schema generators, sitemap, llms.txt, redirects | Full QA — build + test |
| New content | Create new article, add to index/CMS | Diff review |
| Route/component | Edit pages, components, nav, footer | Full QA — build + E2E |

For each item specify:
- **What to change** — specific files and modifications
- **Why** — which scoring signal drives this
- **Expected impact** — predicted metric improvement with timeline
- **Prediction** — structured prediction for the forward-log

### Step 4 — Write Plan and Forward-Log

Write `{root}/weeks/YYYY-WNN/plan.md`:

```markdown
# SEO Plan — YYYY-WNN

**Based on:** analysis.md from YYYY-MM-DD
**Budget:** N content + M technical changes

## Content Changes

### 1. [Action] — [Target Page]
**Why:** [Scoring signal and rationale]
**What:** [Specific changes to make]
**Files:** [List of files to modify]
**QA:** Diff review
**Prediction:** [Metric] from [baseline] to [target] by [week]

### 2. ...

## Technical Changes

### 1. [Action] — [Target]
**Why:** [Scoring signal and rationale]
**What:** [Specific changes to make]
**Files:** [List of files to modify]
**QA:** Full QA — build + test
**Prediction:** [Metric] from [baseline] to [target] by [week]

## Skipped Opportunities
[Items from top-10 that were skipped and why (e.g., touched recently, blocked by dependency)]
```

Append predictions to `{root}/forward-log.md`:

```markdown
| WYYNN | [Action summary] | [Page/Keyword] | [metric] | [baseline] | [target] | [by_week] | | Pending |
```

**Supported metric types:** `position`, `ctr`, `clicks`, `impressions`, `rich_results`, `indexed`, `cwv_lcp`, `cwv_cls`

**Target formats:** exact number, `<30`, `3+`, `+50%` (relative)

### Step 5 — Present for Approval

Present the plan to the user and **wait for explicit approval** before proceeding to implement. Show:
- Summary of all planned changes
- Total predictions made
- Files that will be modified
- QA requirements

---

## Phase 3: Implement (`/seo-routine implement`)

### Step 1 — Load and Validate

1. Load config
2. Read `{root}/weeks/YYYY-WNN/plan.md` — if doesn't exist, tell user to run `plan` first
3. Verify plan was approved (check if user confirmed)

### Step 2 — Set Up Worktree

Create an isolated git worktree for the changes:

```bash
git worktree add ../seo-YYYY-WNN seo/YYYY-WNN 2>/dev/null || \
  git worktree add -b seo/YYYY-WNN ../seo-YYYY-WNN
```

All changes happen in the worktree, not the main working directory.

### Step 3 — Execute Changes

Work through the plan items in order. For each item:

**Content-only changes:**
1. Read the target file
2. Apply the specified modifications (rewrite sections, add FAQ, improve meta, add schema)
3. Apply GEO optimization techniques from [references/geo-research.md](./references/geo-research.md):
   - Cite authoritative sources (+40% AI visibility)
   - Add specific statistics (+37%)
   - Use authoritative, confident tone (+25%)
   - Include FAQ section with schema
4. Commit with descriptive message: `seo(content): [action] for [page]`

**Technical changes:**
1. Read all affected files
2. Apply changes (schema updates, sitemap modifications, redirects)
3. Use templates from [references/schema-templates.md](./references/schema-templates.md)
4. Run build to verify: `npm run build` or framework-specific build command
5. Run tests if they exist: `npm test`
6. Commit with descriptive message: `seo(technical): [action]`

**New content:**
1. Create new article file following the project's content pipeline format
2. Add to content index/CMS seed file if applicable
3. Add redirect if replacing an old URL
4. Apply full GEO optimization
5. Commit: `seo(content): new article [title]`

### Step 4 — Quality Assurance

Based on QA level from the plan:

| QA Level | Actions |
|----------|---------|
| Diff review | Show diff summary, check for obvious errors |
| Full QA — build + test | Run `npm run build`, run `npm test`, verify no errors |
| Full QA — build + E2E | Run build, run E2E tests if available, verify routes work |

### Step 5 — Generate Changes Report

Write `{root}/weeks/YYYY-WNN/changes.md`:

```markdown
# Changes — YYYY-WNN

**Branch:** seo/YYYY-WNN
**Commits:** N

## Content Changes

| # | Action | File(s) | Commit |
|---|--------|---------|--------|
| 1 | Rewrote meta + FAQ | content/article.md | abc1234 |

## Technical Changes

| # | Action | File(s) | Commit |
|---|--------|---------|--------|
| 1 | Fixed schema | lib/schema.ts | def5678 |

## QA Results

- Build: PASS/FAIL
- Tests: PASS/FAIL/SKIPPED
- E2E: PASS/FAIL/SKIPPED

## Next Steps

- [ ] Review PR
- [ ] Merge to main
```

### Dry-Run Mode (`/seo-routine implement --dry-run`)

If `--dry-run` is passed, do NOT write any files or create branches. Instead:
1. Show what files would be changed
2. Show diff previews for each change
3. Show QA classification for each item
4. Summarize total impact

---

## Phase 4: Review (`/seo-routine review`)

### Step 1 — Find Due Predictions

1. Load config
2. Read `{root}/forward-log.md`
3. Find all rows where `By When` <= current week AND `Status` = `Pending`

### Step 2 — Collect Current Data

For each due prediction, pull the current value of the predicted metric:

| Metric | Data Source | How to Get |
|--------|-----------|-----------|
| `position` | GSC or DataForSEO | Average position for the target page/keyword |
| `ctr` | GSC | Click-through rate for the target page |
| `clicks` | GSC | Total clicks for the target page |
| `impressions` | GSC | Total impressions for the target page |
| `rich_results` | Self-crawl Google | Count of rich result features for the page |
| `indexed` | GSC or `site:` search | Boolean — is the page in the index? |
| `cwv_lcp` | PageSpeed Insights | Largest Contentful Paint in seconds |
| `cwv_cls` | PageSpeed Insights | Cumulative Layout Shift score |

### Step 3 — Compare and Score

For each prediction, determine status:

```
delta = abs(baseline - target)  # expected improvement magnitude

if target has comparator (e.g., <30, 3+, +50%):
    evaluate against the comparator directly
else:
    actual_delta = abs(baseline - actual)
    achievement = actual_delta / delta  # how much of the delta was achieved

    if achievement >= 0.75:
        status = "Hit"
    elif achievement >= 0.25:
        status = "Partial"
    else:  # < 0.25 or regression
        status = "Miss"
```

Special cases:
- New content (baseline = `—`): compare actual directly to target
- Relative targets (`+50%`): calculate expected value from baseline, then score normally

### Step 4 — Update Forward-Log

Fill in the `Actual` and `Status` columns for each scored prediction in `{root}/forward-log.md`.

### Step 5 — Update Scorecard

Calculate weekly aggregate metrics and append to `{root}/scorecard.md`:

```markdown
| WYYNN | N pages | avg_pos | total_clicks | total_impressions | avg_ctr | X% accuracy |
```

Prediction accuracy = (Hit + Partial) / Total predictions scored this cycle.

### Step 6 — Weight Adjustment Feedback Loop

Check if weight adjustments are needed:

1. For each signal type (striking_distance, ctr_gap, content_quality, technical_debt, keyword_gap, goal_alignment):
   - Count predictions where this signal was the top driver
   - Calculate hit rate over the last 8 predictions for this signal
2. **Threshold:** Need 4+ data points before adjusting
3. **Adjustment:**
   - Hit rate < 40%: reduce weight by 3 points
   - Hit rate > 75%: increase weight by 2 points
4. **Clamp** all weights to [5, 40]
5. **Re-normalize** so weights sum to 100
6. Write effective weights to `memory/seo/learnings.md` under `## Effective Weights`

### Step 7 — Write Learnings

Update `memory/seo/learnings.md`:

```markdown
## Learnings

### YYYY-WNN Review
- [What worked and why]
- [What didn't work and why]
- [Pattern observed]
- Prediction accuracy: X%
```

**Memory retention:** If learnings exceed 12 weeks, summarize oldest entries into `## Historical Summary` (1-2 lines per quarter). Max 200 lines.

Update `memory/seo/keyword-tracker.md`: shift position columns left, add current week. Prune keywords not seen in 8 weeks. Max 100 keywords.

---

## Quick Commands

### Status (`/seo-routine status`)

Read `memory/seo/state.md` and display:
- Current week
- Last analyze/plan/implement/review dates
- Pending predictions count
- Active goal (from `goals.md`)
- Quick summary of last week's results

### Goals (`/seo-routine goals "..."`)

1. Read `{root}/goals.md`
2. If there's an active goal, move it to "Previous Goals" with current status
3. Parse the new goal text — extract objective, keywords, target pages if mentioned
4. Write the new active goal
5. Confirm to user

---

## Error Handling

| Situation | Action |
|-----------|--------|
| No `seo-config.md` found | Tell user to run `calibrate` first |
| Data source API fails | Skip it, note in analysis what's missing |
| No manual inputs in `inputs/` | Run with automated sources only, flag the gap |
| Build/test failure during implement | **Stop immediately.** Report error, don't commit broken code |
| No analysis exists for current week | Tell user to run `analyze` first |
| No plan exists for current week | Tell user to run `plan` first |
| Forward-log has no due predictions | Report "no predictions due yet", show next due date |

---

## Rate Limiting

All external API calls must respect these limits:

| API | Rate Limit | Backoff Strategy |
|-----|-----------|-----------------|
| DataForSEO | 2 req/sec | Exponential: 1s, 2s, 4s (max 3 retries) |
| PageSpeed Insights | 1 req/sec | 3s backoff on 429 |
| GSC API | 5 req/sec | Standard retry on 429 |
| Self-crawl (own site) | 2 req/sec | 500ms delay between requests |

---

## GEO Optimization Techniques

When creating or optimizing content, apply these methods from [references/geo-research.md](./references/geo-research.md):

| Method | Visibility Boost | Application |
|--------|-----------------|-------------|
| Cite Sources | +40% | Add authoritative citations with links |
| Statistics | +37% | Include specific numbers, percentages, data |
| Quotation Addition | +30% | Expert quotes with proper attribution |
| Authoritative Tone | +25% | Confident, expert-level language |
| Easy-to-understand | +20% | Simplify complex concepts, short paragraphs |
| Technical Terms | +18% | Domain-specific vocabulary |
| Unique Words | +15% | Vocabulary diversity |
| Fluency Optimization | +15-30% | Readability and natural flow |

**Best combo:** Fluency + Statistics for maximum boost.

**Always include:**
- FAQ section with FAQPage schema
- Answer-first format (direct answer at top)
- Clear heading hierarchy (H1 > H2 > H3)
- Tables for comparison data
- Schema markup (Article, FAQPage, SoftwareApplication as appropriate)

See [references/schema-templates.md](./references/schema-templates.md) for JSON-LD templates and schema type status registry.
See [references/platform-algorithms.md](./references/platform-algorithms.md) for platform-specific ranking factors.
See [references/seo-checklist.md](./references/seo-checklist.md) for the full audit checklist.
See [references/geo-research.md](./references/geo-research.md) for GEO techniques, AI crawler management, and llms.txt.
See [references/content-quality.md](./references/content-quality.md) for E-E-A-T scoring and AI citation readiness.
See [references/technical-audit.md](./references/technical-audit.md) for 8-category technical SEO audit checklist.
See [references/image-optimization.md](./references/image-optimization.md) for image file size, format, and lazy loading guidance.
See [references/programmatic-seo.md](./references/programmatic-seo.md) for quality gates and thin content safeguards.

---

## Scripts Reference

Bundled Python scripts for data collection (in `scripts/`):

| Script | Purpose | Requires |
|--------|---------|----------|
| `seo_audit.py` | Free technical SEO audit (no API needed) | Python 3 |
| `keyword_research.py` | Keyword research via DataForSEO | DataForSEO credentials |
| `serp_analysis.py` | SERP analysis for target keywords | DataForSEO credentials |
| `competitor_gap.py` | Keyword gap vs competitors | DataForSEO credentials |
| `backlinks.py` | Backlink profile analysis | DataForSEO credentials |
| `related_keywords.py` | Keyword expansion/related terms | DataForSEO credentials |
| `autocomplete_ideas.py` | Google autocomplete mining | DataForSEO credentials |
| `domain_overview.py` | Domain-level metrics | DataForSEO credentials |
| `dataforseo_api.py` | Shared API wrapper (used by other scripts) | DataForSEO credentials |
| `credential.py` | Credential helper | — |
| `gap_finder.py` | GSC keyword gap analysis (positions 5-20) | GSC OAuth credentials |
| `competitor_intel.py` | Competitor threat mapping from gap data | Gap analysis report |
| `content_plan.py` | Brand-voice weekly content plan | Gap + competitive reports |
| `build_dashboard.py` | Render reports into HTML dashboard | All reports |

Usage example:
```bash
python3 scripts/keyword_research.py --keyword "calendar sync" --location 2840 --language "en"
python3 scripts/seo_audit.py "https://example.com"
```

---

## Sub-Skill References

Reference documents for the GSC-based workflow (in `skills-ref/`):

| Document | Purpose |
|----------|---------|
| `gap-finder.md` | Instructions for running GSC gap analysis |
| `competitor-intel.md` | Instructions for competitor threat mapping |
| `brand-writer.md` | Instructions for brand-voice content planning |

---

## Directory Structure Reference

### Git-tracked (`{root}/`)

```
{root}/
  seo-config.md              # project adapter
  goals.md                   # active strategic goals
  scorecard.md               # global metrics table
  forward-log.md             # predictions tracking
  weeks/
    YYYY-WNN/
      inputs/                # manual data drops (Ahrefs CSVs, notes)
      analysis.md            # Phase 1 output
      plan.md                # Phase 2 output
      changes.md             # Phase 3 output
```

### Claude Memory (`memory/seo/`)

```
memory/seo/
  state.md                   # last run dates, current week, root path
  learnings.md               # what works/doesn't, effective weights
  keyword-tracker.md         # tracked keywords + positions
```
