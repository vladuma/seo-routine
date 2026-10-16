---
name: seo-routine
description: Organic-growth routine for a site you own. Measures Search Console, analytics and AI-answer visibility, plans a small number of falsifiable experiments, implements authorized changes, verifies delivery on the live site, and scores outcomes honestly. Run /seo-routine calibrate to set up, then analyze → plan → implement → verify → review. Use when the user says "seo routine", "weekly seo", "seo cycle", "seo analyze", "seo plan", "seo implement", "seo verify", "seo review", "seo calibrate", "seo status", "seo goals", "seo geo", "seo autopilot", or "seo publish".
---

# SEO Routine

Run the requested phase against recorded evidence. An investigation request means analysis and
recommendations. A request to implement, or to run autopilot, also authorizes work inside that scope.
Publishing follows the session's existing authorization and the repository's delivery rules. It is never
inferred from a successful analysis.

The routine's central rule: **a claim is only as strong as the saved file behind it.** Delivery, live
verification and business outcome are separate states, and a missing or failed source is a gap, never a
zero.

## Setup for every phase

1. Read the repository's `CLAUDE.md` (and the nested one for `app_dir` if config names one). Run
   app-relative commands from `app_dir`.
2. Find and load `seo-config.md`: search for `**/seo-config.md`, or use the root a previous run
   recorded. It owns effective settings, source locations, budgets and publisher configuration. Read the
   configured experiment ledger and goals file for the work at hand. Agent memory is optional retrieval
   context and never the authoritative source of settings or state. No config means run `calibrate` first.
3. Source `env_file` on **every** credential-dependent shell call. Each Bash call is a fresh shell:
   `set -a && source .env.seo && set +a && <command>`. Credentials come only from this file and the
   credential or token paths it names. Never print them, and never write tokens, passwords or connection
   strings into reports. Read-only OAuth refresh from a cached token is allowed. A worktree may reuse the
   file from a verified main worktree; if the credential path is relative, override the variable with its
   resolved absolute path, because sourcing alone does not relocate it.
4. Use the actual ISO week and explicit dates. Write new runs to `run_dir`
   (`weeks/<ISO-week>/<YYYY-MM-DD>/`), which cannot overwrite an earlier run. Record `run_date`, source
   windows, freshness, timezone and source failures in every analysis. Existing folders may carry
   historical label drift: preserve them.
5. If `config_version` is older than 4, warn once and continue with what the old config provides:
   "Your SEO config is at version N (current is 4). Run `/seo-routine calibrate` to upgrade. Your
   settings are preserved."

## Phase routing

| Request | Read and do | Completion |
|---|---|---|
| `calibrate` | Follow [calibration](#calibration-and-upgrades) | Valid config; accessible sources tested; gaps recorded |
| `analyze` or a traffic investigation | [measurement](references/measurement.md), then rank opportunities under [experiments](references/experiments.md) | Dated analysis, sanitized raw inputs, supported findings and unknowns |
| `plan` | [experiments](references/experiments.md) | At most the configured number of content experiments; predeclared outcomes and exclusions |
| `implement` | [delivery](references/delivery.md), plus [seo-writing](references/seo-writing.md) for content | Authorized edits, appropriate checks, independent review, exact delivery status |
| `publish` | [delivery](references/delivery.md) | The configured, authorized action is done and verified; PR and deploy kept distinct |
| `verify` | [delivery](references/delivery.md) | Live URL checks recorded as passed, failed or pending |
| `review` | [measurement](references/measurement.md) for current traffic, then [experiments](references/experiments.md) | Due valid predictions scored once; insufficient evidence stays explicit |
| `geo` | [GEO](references/geo.md) | Fixed-panel observations, actual referral outcomes and missing coverage |
| `status`, or no request beyond the skill name | Read config, ledger and the latest dated run | Latest data dates, experiments, review/PR/deploy/live states, next due dates |
| `goals "..."` | Update only the requested goal in the configured goals file | Goal, success metric and horizon recorded; the previous goal archived with its outcome |
| `autopilot` | Measurement → plan → implement/review → authorized publish → verify → due outcome review | Every phase has an evidence-backed state, including "no change" and "pending" |

`--dry-run` on `implement` produces the diff and plan only: no commits, push or deployment.

Independent collection and a fresh adversarial review may use subagents when available. Give each one
bounded source ownership and a sanitized handoff, and do the dependent synthesis after collection. Pass
an explicit model on every dispatch, choosing from the models the current environment offers: the
cheapest capable one for mechanical collection, crawling, parsing and verification; a stronger one for
scoring judgment and content writing; the strongest available for adversarial review. Do not hardcode
model names from another runtime.

## What each phase must establish

- **Analyze.** Collect in parallel only what is independent: Search Console (`scripts/gsc.py`), analytics,
  DataForSEO or other enabled sources, a bounded self-crawl, and any manual files dropped in `inputs/`.
  Reconcile them under the [measurement contract](references/measurement.md): equal complete windows,
  property totals versus page rows, query coverage, entry-visit cohorts. For each candidate record the
  mechanism, evidence, the most plausible alternative and a refuting observation. Positions 5-20 with
  real impressions are a screening heuristic for striking distance, not a score. Do not rank with
  invented volumes or a composite number.
- **Plan.** Choose zero to the configured maximum of experiments. Each has one falsifiable mechanism and
  a primary outcome with baseline and target on the same definition and window. Repairs are recorded as
  repairs. Everything is registered in the [ledger](references/experiments.md#experiment-ledger) before
  any edit. A plan-only request stops at the reviewable plan.
- **Implement.** Edit only within the plan and the user's authorization, then run independent review and
  the repository's gates. Content writing uses [seo-writing](references/seo-writing.md); AI-answer
  hypotheses use [geo-research](references/geo-research.md), labeled as hypotheses.
- **Publish and verify.** Follow the publisher configuration and [delivery](references/delivery.md).
  `local_only`, `pr_open`, `merged`, `deployed` and live verification are separate recorded states.
- **Review.** Score only predictions whose verified exposure and horizon exist, by direction and progress
  against the declared target, once. Everything else is `pending`, `insufficient_evidence`, `confounded`
  or `unscorable`, each with a reason.

## Calibration and upgrades

Inspect any existing config and each source's `--help` before changing settings. A fresh install runs
discovery; an existing install enters **upgrade mode**, which merges authorized changes while keeping
every valid user choice. Show a diff summary and ask for confirmation before writing.

**1. Detect.** Find `seo-config.md`. Missing means fresh install. Present means read its
`config_version` and plan the migrations below.

**2. Auto-discover silently** (no questions): content files and pipeline (`*.md`, `*.mdx`, article
modules, a CMS in `package.json`), SEO infrastructure (`sitemap`, `robots`, schema generators,
`llms.txt` routes, redirects), framework, analytics snippets, the default branch
(`git symbolic-ref refs/remotes/origin/HEAD`), the monorepo app directory and the project's own
instructions.

**3. Ask at most six questions**, skipping anything discovery answered: production URL; the SEO data
root (default `docs/seo/`); top three competitors; available data sources (GSC, GA4, analytics provider,
DataForSEO, Ahrefs, GEO panel); an optional current strategic goal; and how changes are deployed
(PR to a branch, an external command, or manual) with optional per-classification routing.

**4. Verify credentials** by sourcing `.env.seo` and checking each enabled source with a small read-only
query. Add only missing variable names to the user's instructions, never values to config. A source that
fails stays `enabled: false` with a comment, and the gap is recorded rather than treated as zero traffic.

| Source | Required in `.env.seo` |
|---|---|
| GSC | `GOOGLE_APPLICATION_CREDENTIALS`, `GSC_SITE_URL` (optional `GSC_BRAND_REGEX`) |
| GA4 | `GOOGLE_APPLICATION_CREDENTIALS` (the property ID goes in config) |
| Analytics provider | provider URL and site ID variables as the collector documents |
| DataForSEO | `DATAFORSEO_LOGIN`, `DATAFORSEO_PASSWORD` |
| Ahrefs API | `AHREFS_API_TOKEN` |

`GOOGLE_APPLICATION_CREDENTIALS` accepts a service-account key (no browser; the account needs GSC/GA4
access) or an OAuth client secret (browser consent on first run with `--authorize`, token cached as
`.seo-token.json`).

**5. Write config and scaffold** from `templates/`: `seo-config.md`, `experiments.json`, `goals.md`,
`learnings.md`, `geo-scorecard.md` and `geo-panel.json` (when GEO is enabled), `brand-voice.md` (when a
content pipeline exists) and `weeks/.gitkeep` under the root. Create `.env.seo` at the project root with
commented placeholders for enabled sources. Never overwrite an existing one, and add only lines for newly
enabled sources. Make sure `.env.seo` and `.seo-token.json` are in `.gitignore`. In upgrade mode overwrite
only `seo-config.md` and create template files that are missing.

### Migrations (apply in order)

| From | To | Changes |
|---|---|---|
| 1 or missing | 2 | Add `config_version: 2`; replace `gsc.property` with `GSC_SITE_URL`; add `ga4.property_id` if absent |
| 2 | 3 | Add `env_file`, `publishers` (a `default` publisher with `command: null`, `approval: require`) and `autopilot`; move credentials into `.env.seo` |
| 3 | 4 | Add `app_dir`, `base_branch`, `branch_naming`, `run_dir`, `experiments_file`, `goals_file`, `learnings_file`, `legacy_forward_log`, `measurement`, `planning` and the `gsc`/`geo` settings. Rename `data_sources.umami` to `data_sources.analytics` (keeping its site ID). Convert `weekly_budget` to maxima under `planning` with zero minimums. Convert publisher `approval` into the v4 publisher block. Remove `scoring_weights`, the `## Effective Weights` section and automatic weight tuning. Create the empty ledger and move the old `forward-log.md` path into `legacy_forward_log` (its rows are not auto-migrated, see [legacy logs](references/experiments.md#legacy-logs)). Keep learnings, scorecards and goals as historical evidence |

Preserve historical scorecards, goals, weekly artifacts and forward-log rows. Never silently convert
legacy estimates into comparable observations, and never mark old predictions valid by fiat. Move any
Claude-memory state (`memory/seo/*`) into the repository only on the user's confirmation.

## Publishers and autopilot

After implementation, write one changeset JSON per change group under `changesets/` (action, target,
files, diff, commit, and the ledger prediction IDs). Route each change to the first publisher whose
`routes` include its classification (`content-only`, `new-content`, `technical`, `route/component`), then
to a `*` catch-all, then to `autopilot.approval_fallback` (`require` asks, `skip` drops the change and
logs it). `approval: auto` runs the configured action once QA and review have passed; `require` uses
existing authorization or presents the reviewed result and waits. A publisher `command` may use
`{changeset_file}`, `{branch}`, `{worktree_path}`, `{title}`, `{body}`, `{commit}` and `{week}`, passed
as safe arguments, never interpolated Markdown. Exit codes: 0 published, 1 failed (stop that group and
tell the user), 2 pending manual action (log "awaiting action" and continue). A `null` command leaves the
change committed in the worktree and reports `local_only`.

Autopilot requires `autopilot.enabled: true` and at least one publisher with a real action. It runs the
phases in order, skips only the interactive approval step, and writes `autopilot-summary.md` with each
phase's evidence-backed state. A data-source failure continues with the remaining sources. A QA or review
failure stops everything before publication. A failed publisher stops that group only. If every publisher
requires approval, autopilot completes analysis, plan and implementation and reports that the changes are
waiting. It is safe to rerun in the same week: valid existing analysis and plan are reused. To run it on a
schedule use `/loop 7d /seo-routine autopilot`, and never create or alter schedules on your own.

## Run record

Keep analysis, plan, changes, verification and outcome notes in the dated run folder only when that phase
runs. Sanitized collector output goes in `inputs/`. The ledger owns active experiment IDs and delivery
state. Report a justified "no change" run as a successful analysis and unshipped work as unshipped.
Source failures and an unverified deploy must stay visible in the final answer and in the ledger. Reuse
valid same-day inputs with their original collection time. Rerunning the same week does not by itself make
stale data current.

```
{root}/
  seo-config.md  goals.md  experiments.json  learnings.md  geo-scorecard.md  geo-panel.json
  weeks/<ISO-week>/<YYYY-MM-DD>/
    inputs/  analysis.md  plan.md  changes.md  changesets/  verify.md  review.md
```

## Rate limits

| API | Limit | Backoff |
|---|---|---|
| DataForSEO | 2 req/s | 1s, 2s, 4s; at most 3 retries |
| PageSpeed Insights | 1 req/s | 3s on 429 |
| GSC | 5 req/s | standard retry on 429 |
| Own site (crawl, verify) | 2 req/s | 500ms between requests |

## Scripts

Run from the plugin's `scripts/` directory (or reference them by path). Collectors print compact
structured output for LLM consumption; use `--json` where available to save a reproducible input.

| Script | Purpose | Requires |
|---|---|---|
| `gsc.py` | Finalized Search Console data: property totals, query partition and coverage, equal-window comparison | Google credentials |
| `ga4.py` | GA4 cross-check | Google credentials |
| `geo_panel.py` | Fixed AI-answer panel with raw receipt and per-prompt summary | DataForSEO credentials, `geo-panel.json` |
| `seo_audit.py` | Free technical audit of public URLs | Python 3 |
| `keyword_research.py`, `serp_analysis.py`, `competitor_gap.py`, `related_keywords.py`, `autocomplete_ideas.py`, `backlinks.py`, `domain_overview.py` | DataForSEO research | DataForSEO credentials |
| `gap_finder.py`, `competitor_intel.py`, `content_plan.py`, `build_dashboard.py` | Search-Console gap analysis and reporting | Gap reports |
| `dataforseo_api.py`, `credential.py` | Shared helpers | n/a |

Sub-skill notes for the gap workflow live in `skills-ref/` (`gap-finder`, `competitor-intel`,
`brand-writer`).

## References

[measurement](references/measurement.md) · [experiments](references/experiments.md) ·
[delivery](references/delivery.md) · [geo](references/geo.md) · [seo-writing](references/seo-writing.md) ·
[geo-research](references/geo-research.md) · [content-quality](references/content-quality.md) ·
[technical-audit](references/technical-audit.md) · [seo-checklist](references/seo-checklist.md) ·
[schema-templates](references/schema-templates.md) · [platform-algorithms](references/platform-algorithms.md) ·
[image-optimization](references/image-optimization.md) · [programmatic-seo](references/programmatic-seo.md) ·
[tools-and-apis](references/tools-and-apis.md)

The writing, schema and platform references are background knowledge. Anything in them that reads as a
rule of thumb (word counts, anchor-text ratios, percentage uplifts) is a hypothesis for this site to
test, not a requirement and not a prediction.
