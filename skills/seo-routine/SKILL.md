---
name: seo-routine
description: Data-driven weekly SEO optimization routine with prediction tracking. Run /seo-routine calibrate to set up, then use analyze → plan → implement → verify → review cycle for continuous SEO improvement. Use when user says "seo routine", "weekly seo", "seo cycle", "seo analyze", "seo plan", "seo implement", "seo verify", "seo review", "seo calibrate", "seo status", "seo goals", "seo autopilot", or "seo publish".
---

# SEO Routine — Weekly Optimization Engine

Data-driven weekly SEO optimization cycle: **analyze → plan → implement → verify → review**.
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
| `verify` | Phase 5: Check published changes are live and correct |
| `autopilot` | Full cycle: analyze → plan → implement → publish (unattended) |
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

**Load environment:** Read `env_file` from config (defaults to `.env.seo`). **Every bash command** that needs credentials must source the file as a prefix — shell state does not persist between tool calls. Use this pattern:

```bash
# ALWAYS prefix credential-dependent commands with this:
set -a && source .env.seo && set +a && <actual command>

# Examples:
set -a && source .env.seo && set +a && python3 scripts/keyword_research.py "calendar sync"
set -a && source .env.seo && set +a && python3 scripts/gsc.py --days 7 --dimension query
set -a && source .env.seo && set +a && echo "GSC: ${GSC_SITE_URL:-NOT SET}"
```

**This is not optional.** Every `Bash` tool call runs in a fresh shell — sourcing `.env.seo` in one call does NOT carry over to the next. Always prefix.

`.env.seo` is the **single source of truth** for SEO credentials — do not look for vars in `.env`, shell profile, or other files.

**Version check:** Compare `config_version` in the loaded config against the current template version. If the config is outdated (or `config_version` is missing), warn the user: *"Your SEO config is at version N (current is M). Run `/seo-routine calibrate` to upgrade — your settings will be preserved."* Continue running the phase with the existing config (don't block).

**Load effective scoring weights:** Check `memory/seo/learnings.md` for an `## Effective Weights` section. If found, use those weights. Otherwise, use weights from `seo-config.md` `scoring_weights`.

**Determine current week:** Use ISO week format `YYYY-WNN` based on today's date.

---

## Phase 0: Calibrate (`/seo-routine calibrate`)

### Step 0 — Detect Existing Installation

Before anything else, check if `seo-config.md` already exists:

1. Check Claude memory `memory/seo/state.md` for the configured `root` path
2. If no state, search for `**/seo-config.md` in the project
3. If found, read it and extract `config_version` from the YAML block

**If no existing config:** proceed to Step 1 (fresh install).

**If existing config found:** enter **upgrade mode**:

1. Parse the existing config fully — preserve all user-provided values (site URL, competitors, scoring weights, weekly budget, enabled data sources with their credentials)
2. Compare `config_version` against the current template version (defined in `templates/seo-config.md`)
3. If versions match, tell the user the config is up to date and ask if they want to re-run discovery anyway (to pick up new project structure changes)
4. If the existing version is older (or missing — treat missing as version 1), apply migrations and show a diff summary:

```
## Config Upgrade: vN → vM

Example (v2 → v3):
Changes:
  + config_version: 3
  + env_file: ".env.seo"
  - data_sources.*.credentials_env (moved to .env.seo)
  + publishers: default publisher (command: null, routes: ["*"], approval: require)
  + autopilot: enabled: false, approval_fallback: require
  + .env.seo created at project root (added to .gitignore)

Preserved:
  ✓ site.url, site.brand, site.industry
  ✓ competitors
  ✓ scoring_weights (including any manual adjustments)
  ✓ weekly_budget
  ✓ self_crawl settings
  ✓ data_sources (enabled/disabled state, property IDs)
  ✓ All weekly data, scorecard, forward-log, goals
  ✓ Credential values (migrated from old location → .env.seo)
```

5. Ask the user to confirm before writing the upgraded config
6. Write the merged config (new structure + preserved user values) to `seo-config.md`
7. Skip Steps 1-3 unless the user asked to re-run discovery

**Migration definitions (apply in order):**

| From | To | Changes |
|------|-----|---------|
| v1 (or missing) | v2 | Add `config_version: 2`. Replace `gsc.property` with `gsc.site_url_env: "GSC_SITE_URL"`. Verify `GSC_SITE_URL` env var is set if GSC is enabled. Add `ga4.property_id` if not present. |
| v2 | v3 | Add `config_version: 3`. Add `env_file: ".env.seo"`. Remove `credentials_env`/`site_url_env`/`website_id_env` from data_sources (credentials now live in `.env.seo`, not config). Add `property_id` to GSC if not present. Add `site_id` to Umami if not present. Add `publishers` section with a `default` publisher (`command: null`, `routes: ["*"]`, `approval: require`). Add `autopilot` section (`enabled: false`, `approval_fallback: require`). Create `.env.seo` at project root with vars migrated from any existing `.env`/`env.seo`/shell. Add `.env.seo` to `.gitignore`. |

When adding future migrations, append a new row. Always apply all migrations between the current version and the latest sequentially.

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
6. **How do you deploy changes?** — determines publisher setup:
   - **PR to a branch** — code changes, infrastructure edits (scaffolds a `code` publisher using `gh pr create`)
   - **External command/script** — CMS API, custom deploy tool (user provides the command; skill scaffolds a publisher entry with their command)
   - **Manual** — user applies changes themselves (scaffolds `default` publisher with `command: null`)
   - User can set up **multiple publishers** — e.g., PRs for technical changes, a script for content. Ask if they want to route different change types to different publishers. This can also be refined later in `seo-config.md`.

### Step 3 — Credential Verification

All credentials live in `.env.seo` (or the path set in `env_file`). Check vars by sourcing inline:

```bash
set -a && source .env.seo && set +a && echo "GSC: ${GOOGLE_APPLICATION_CREDENTIALS:+OK}" && echo "DataForSEO: ${DATAFORSEO_LOGIN:+OK}"
```

**Required env vars per source (all defined in `.env.seo`):**

| Source | Required in `.env.seo` | What to add if missing |
|--------|----------------------|----------------------|
| GSC | `GOOGLE_APPLICATION_CREDENTIALS`, `GSC_SITE_URL` | `GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json` and `GSC_SITE_URL=https://example.com` |
| GA4 | `GOOGLE_APPLICATION_CREDENTIALS` | Same credentials file as GSC. Property ID goes in seo-config.md, not env file |
| Umami | `UMAMI_API_URL`, `UMAMI_SITE_ID` | `UMAMI_API_URL=https://analytics.example.com` and `UMAMI_SITE_ID=abc-123` |
| DataForSEO | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` | `DATAFORSEO_LOGIN=your@email.com` and `DATAFORSEO_PASSWORD=your_password` |
| Ahrefs (API) | `AHREFS_API_TOKEN` | `AHREFS_API_TOKEN=your_token` |

**Google credentials:** `GOOGLE_APPLICATION_CREDENTIALS` accepts either type:
- **Service account key** (`"type": "service_account"`) — direct API access, no browser needed. Service account must be granted access in GSC/GA4 admin.
- **OAuth client secret** (`client_secret_*.json`) — opens browser for user consent on first run, caches token as `.seo-token.json` for subsequent runs. No admin setup needed if the user already has access.

For each enabled data source, verify the required vars are set after sourcing. If missing:
1. Tell the user exactly what to add to `.env.seo`
2. Mark the source as `enabled: false` in config with a comment

**If `.env.seo` doesn't exist yet**, create it in the next step (Step 5).

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

Create the env file (at project root, not inside `{root}/`):

```
.env.seo                 # credentials for all SEO data sources
```

Populate `.env.seo` with placeholder entries for each enabled data source:

```bash
# SEO Routine credentials — sourced automatically by /seo-routine
# See seo-config.md for which sources are enabled

# Google (GSC + GA4) — service account JSON key
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json
# GSC_SITE_URL=https://example.com

# DataForSEO
# DATAFORSEO_LOGIN=
# DATAFORSEO_PASSWORD=

# Umami
# UMAMI_API_URL=
# UMAMI_SITE_ID=

# Ahrefs
# AHREFS_API_TOKEN=
```

Uncomment and fill the lines for enabled sources. If the user already provided values during credential verification (Step 3), write them directly (uncommented).

**Add `.env.seo` to `.gitignore`** if not already present:

```bash
grep -qxF '.env.seo' .gitignore 2>/dev/null || echo '.env.seo' >> .gitignore
grep -qxF '.seo-token.json' .gitignore 2>/dev/null || echo '.seo-token.json' >> .gitignore
```

Create Claude memory files:

```
memory/seo/
  state.md               # root path, calibration date, no runs yet
  learnings.md           # empty with section headers: ## Learnings, ## Effective Weights, ## Historical Summary
  keyword-tracker.md     # empty with headers: | Keyword | W-4 | W-3 | W-2 | W-1 | Current | Trend |
```

**If `{root}/` already exists (re-calibration/upgrade):** Only overwrite `seo-config.md` (merged with user values per Step 0). Preserve all other files (goals, scorecard, forward-log, weekly data, brand-voice). Create any new template files that don't exist yet. If `.env.seo` already exists, **do not overwrite it** — only add placeholder lines for newly enabled sources that aren't already in the file.

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
# Uses GOOGLE_APPLICATION_CREDENTIALS (service account) + GSC_SITE_URL env vars
python3 scripts/gsc.py --days 7 --compare --dimension page --limit 100
python3 scripts/gsc.py --days 7 --compare --dimension query --limit 100
```

Collects per-page and per-query: clicks, impressions, CTR, avg position for last 7 days vs previous 7 days with deltas. Also outputs striking-distance opportunities (positions 5-20).

**Agent 2: Analytics Data** (Umami or GA4, if enabled)
```bash
# GA4: Uses GOOGLE_APPLICATION_CREDENTIALS + property_id from seo-config.md
python3 scripts/ga4.py --property {property_id} --days 7 --compare --limit 100
# Umami: curl the Umami API for page views, bounce rate, session duration
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

### Step 3 — Generate Changes

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

If QA fails, **stop immediately**. Do not proceed to publishing. Report the error to the user.

### Step 5 — Write Changesets

After all changes are committed and QA passes, group changes by their classification (from the plan) and write a changeset JSON file for each group to `{root}/weeks/YYYY-WNN/changesets/`:

```json
{
  "week": "2026-W11",
  "group": "content",
  "classification": "content-only",
  "items": [
    {
      "action": "update_meta_and_faq",
      "target": "/blog/calendar-sync",
      "files": ["content/blog/calendar-sync.md"],
      "diff": "--- a/content/blog/calendar-sync.md\n+++ b/content/blog/calendar-sync.md\n@@ ...",
      "commit": "abc1234",
      "prediction": {
        "metric": "ctr",
        "baseline": "3.2%",
        "target": "5.5%",
        "by_week": "2026-W14"
      }
    }
  ]
}
```

Each changeset file is named `{publisher_name}.json` based on the routing in Step 6.

### Step 6 — Route to Publishers

Match each change group to a publisher from `seo-config.md`:

```
for each change in plan:
    find first publisher whose "routes" list includes change.classification
    if no match and routes includes "*", use that publisher
    if no match at all, use autopilot.approval_fallback:
        "require" → pause and ask user what to do
        "skip"    → drop the change, log as "Skipped — no publisher"
    group matched changes by publisher name

for each publisher group:
    write changeset file to {root}/weeks/YYYY-WNN/changesets/{publisher_name}.json
```

### Step 7 — Preview

For each publisher that has a `preview` command defined:

```bash
# Run the preview command with placeholders substituted
{publisher.preview}  # e.g., "git diff --stat seo/2026-W11"
```

Display the preview output to the user (or log it in autopilot mode). If no `preview` command is defined, show the changeset summary (files changed, diff stats).

### Step 8 — Approval Gate

For each publisher group, check the publisher's `approval` setting:

| Setting | Behavior |
|---------|----------|
| `auto` | Proceed to publish immediately (if QA passed) |
| `require` | Pause and show preview to user. Wait for explicit "go" before publishing. In autopilot mode, log as "Awaiting approval" and skip to next group |

When running interactively (not autopilot), present all groups and their approval requirements together so the user can approve in one go.

### Step 9 — Publish

For each approved publisher group, run the publisher's `command`:

```bash
# Substitute placeholders and execute
{publisher.command}  # e.g., "gh pr create --base main --head seo/2026-W11 ..."
```

**If `command` is `null`:** Changes stay in the worktree. Log as "Changes ready in worktree `{worktree_path}` on branch `{branch}`". The user handles deployment manually.

**Check exit codes:**

| Exit | Meaning | Skill action |
|------|---------|-------------|
| 0 | Published | Log "Published via {publisher_name}" in forward-log and changes report |
| 1 | Failed | Log "Publish failed via {publisher_name}", stop, notify user |
| 2 | Pending | Log "Awaiting action via {publisher_name}", continue to next group |

**Placeholder substitution reference:**

| Placeholder | Value |
|---|---|
| `{changeset_file}` | Absolute path to the publisher's changeset JSON |
| `{branch}` | Git branch name (`seo/YYYY-WNN`) |
| `{worktree_path}` | Absolute path to the worktree |
| `{title}` | Short description: `SEO {classification} — {week}` |
| `{body}` | Markdown summary: items, files, predictions |
| `{commit}` | Latest commit SHA on the branch |
| `{week}` | Current ISO week (`YYYY-WNN`) |

### Step 10 — Generate Changes Report

Write `{root}/weeks/YYYY-WNN/changes.md`:

```markdown
# Changes — YYYY-WNN

**Branch:** seo/YYYY-WNN
**Commits:** N

## Changes by Publisher

### {publisher_name} (approval: {auto|require})

| # | Action | File(s) | Commit | Status |
|---|--------|---------|--------|--------|
| 1 | Rewrote meta + FAQ | content/article.md | abc1234 | Published |
| 2 | Fixed schema | lib/schema.ts | def5678 | Published |

### {another_publisher} (approval: {auto|require})

| # | Action | File(s) | Commit | Status |
|---|--------|---------|--------|--------|
| 1 | New article | content/new-post.md | ghi9012 | Awaiting action |

## QA Results

- Build: PASS/FAIL
- Tests: PASS/FAIL/SKIPPED
- E2E: PASS/FAIL/SKIPPED

## Publish Summary

| Publisher | Changes | Status |
|-----------|---------|--------|
| code | 2 | Published |
| content | 1 | Awaiting action |

## Rollback Commands

If needed, run these to undo published changes:
- {publisher_name}: `{rollback_command}` (only shown if publisher defines rollback)
```

### Dry-Run Mode (`/seo-routine implement --dry-run`)

If `--dry-run` is passed, do NOT write any files or create branches. Instead:
1. Show what files would be changed
2. Show diff previews for each change
3. Show QA classification for each item
4. Show publisher routing — which changes go to which publisher
5. Show what publish commands would run
6. Summarize total impact

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

## Phase 5: Verify (`/seo-routine verify`)

Checks that published changes are actually live and correct on the production site. Run after deploy has propagated (typically 1-24h after publish, depending on the stack).

### Step 1 — Load Changes

1. Load config
2. Read `{root}/weeks/YYYY-WNN/changes.md` — if doesn't exist, tell user to run `implement` first
3. Read changeset files from `{root}/weeks/YYYY-WNN/changesets/` for details on what was changed
4. Build a verification checklist from the changes

### Step 2 — Build Verification Checklist

For each change, determine what to check based on the action type:

| Action type | Checks |
|---|---|
| Meta rewrite | Fetch page, confirm `<title>` and `<meta name="description">` match intended values |
| FAQ added | Confirm FAQ section exists in HTML, validate FAQPage JSON-LD schema |
| Schema fix | Fetch page, parse JSON-LD, verify expected `@type` and required fields |
| Content update | Fetch page, confirm key phrases/sections are present, word count meets threshold |
| New content | Page returns HTTP 200 (not 404/5xx), content length > 300 words, page appears in sitemap |
| Redirect | Old URL returns 301/302, `Location` header points to expected destination |
| Sitemap change | Fetch sitemap, confirm expected URLs are present/removed |
| Robots.txt change | Fetch robots.txt, confirm expected rules |
| Image optimization | Fetch page, confirm images have alt text, lazy loading attributes |

**Universal checks** on every changed page:
- HTTP status is 200
- Canonical tag is present and correct
- Page is not `noindex` (unless intentional)
- No broken internal links on the page
- Schema markup (if any) is valid JSON-LD (parseable, no syntax errors)

### Step 3 — Crawl and Verify

Fetch each changed page from the **live production URL** (from `site.url` in config):

```bash
# Fetch page and extract key elements
curl -sL "{site_url}{page_path}" | python3 -c "
import sys, json, re
html = sys.stdin.read()
# Check HTTP status, parse title, meta, schema, canonical, noindex
"
```

Rate limit: same as self-crawl (500ms between requests to own site).

For redirect checks, use `curl -sI` to inspect headers without following redirects:

```bash
curl -sI "{site_url}{old_path}" | head -5
```

For sitemap/robots checks, fetch them directly:

```bash
curl -sL "{site_url}/sitemap.xml"
curl -sL "{site_url}/robots.txt"
```

### Step 4 — Write Verify Report

Write `{root}/weeks/YYYY-WNN/verify.md`:

```markdown
# Verify — YYYY-WNN

**Checked:** YYYY-MM-DD
**Pages verified:** N/M passed

## Results

| Page | Check | Status | Detail |
|------|-------|--------|--------|
| /blog/calendar-sync | HTTP 200 | PASS | |
| /blog/calendar-sync | Meta title | PASS | Matches changeset |
| /blog/calendar-sync | FAQ schema | PASS | Valid FAQPage, 3 questions |
| /blog/calendar-sync | Canonical | PASS | Self-referencing |
| /new-article | HTTP 200 | FAIL | Returns 404 |
| /new-article | In sitemap | FAIL | Not found in sitemap.xml |

## Summary

- Passed: X checks across Y pages
- Failed: N checks across M pages
- Skipped: K (pages with publish status "Awaiting action")

## Action Needed

- [ ] /new-article — not live yet, check deploy status or request indexing via GSC
- [ ] /blog/old-post — redirect not active, verify server config
```

### Step 5 — Update Forward-Log

For changes that failed verification:
- Update the forward-log entry status from "Published" to "Verify failed — [reason]"
- These items should be flagged in the next `analyze` cycle for re-examination

For changes that passed:
- Update status to "Live" (confirms the change is deployed and correct)

### Verify Options

**Specific week:** `/seo-routine verify YYYY-WNN` — verify a specific past week instead of current week.

**Specific page:** `/seo-routine verify /blog/some-page` — verify only one page (useful for quick spot-checks).

---

## Phase 6: Autopilot (`/seo-routine autopilot`)

Runs the full cycle unattended: analyze → plan → implement → publish → review (if predictions are due).

### Prerequisites

1. `autopilot.enabled` must be `true` in `seo-config.md`
2. At least one publisher must be configured with a non-null `command` (otherwise there's nowhere to publish — warn and exit)
3. Config must be calibrated (seo-config.md exists)

### Execution Flow

```
1. Load config
2. Run Phase 1 (Analyze) — full data collection and scoring
3. Run Phase 2 (Plan) — select opportunities, classify, write plan
   └── Skip the "Present for Approval" step (Step 5) — autopilot doesn't wait
4. Run Phase 3 (Implement) — generate changes, QA, route, publish
   └── For each publisher group:
       - approval: auto  → publish immediately
       - approval: require → log as "Awaiting approval", skip
   └── If ALL publishers are "require", nothing gets published — log this
       and notify user that autopilot completed analysis + plan but
       changes need manual approval
5. If any predictions are due (forward-log has Pending items where by_week <= current week):
   └── Run Phase 4 (Review) — score predictions, update weights
6. Update memory/seo/state.md with last autopilot run date
```

### Error Handling in Autopilot

Autopilot must not silently fail. On any error:

| Error | Action |
|-------|--------|
| Data source fails | Continue with available sources (same as manual analyze) |
| QA fails (build/test) | **Stop entire autopilot.** Do not publish. Log error in `changes.md`. Notify user. |
| Publisher command exits 1 | Stop publishing for that group. Continue other groups. Log failure. |
| All publishers are `require` | Complete analyze + plan + implement (generate changes). Log: "Autopilot: changes ready, awaiting approval. Run `/seo-routine implement` to review and publish." |

### Autopilot Output

After autopilot completes, write a summary to `{root}/weeks/YYYY-WNN/autopilot-summary.md`:

```markdown
# Autopilot Summary — YYYY-WNN

**Run date:** YYYY-MM-DD
**Phases completed:** analyze, plan, implement, review

## Analysis
- Pages analyzed: N
- Top opportunity: [page] (score: X)

## Plan
- Content changes: N
- Technical changes: M

## Publishing
| Publisher | Changes | Approval | Status |
|-----------|---------|----------|--------|
| code | 2 | auto | Published |
| content | 1 | require | Awaiting approval |

## Review (if run)
- Predictions scored: N
- Accuracy: X%
- Weight adjustments: [list or "none"]

## Issues
- [Any errors, skipped items, or data gaps]
```

### Scheduling Autopilot

Autopilot can be triggered manually (`/seo-routine autopilot`) or scheduled using `/loop`:

```
/loop 7d /seo-routine autopilot
```

This runs the full cycle weekly. The skill is idempotent for a given week — if analysis already exists for the current week, it skips Phase 1 and uses the existing data. If a plan already exists, it skips Phase 2. This means re-running autopilot in the same week is safe.

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
| Publisher command exits 1 | Log failure, stop publishing that group, notify user |
| Publisher command exits 2 | Log as "Awaiting action", continue to next group |
| No publisher matches a change classification | Use `autopilot.approval_fallback`: `require` → ask user, `skip` → drop the change |
| Publisher command not found / not executable | Log error, treat as exit 1, suggest user check the command path |
| Autopilot with all `require` publishers | Complete analyze + plan + generate changes, log that approval is needed |
| No changes.md for current week (verify) | Tell user to run `implement` first |
| Page returns 5xx during verify | Log as FAIL with "Server error", don't retry — notify user |
| Page returns 404 during verify | Log as FAIL, may indicate deploy hasn't propagated or URL is wrong |

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
      verify.md              # Phase 5 output
```

### Claude Memory (`memory/seo/`)

```
memory/seo/
  state.md                   # last run dates, current week, root path
  learnings.md               # what works/doesn't, effective weights
  keyword-tracker.md         # tracked keywords + positions
```
