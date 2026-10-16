# seo-routine

A Claude Code skill for growing organic traffic on a site you own. It measures Search Console, analytics
and AI-answer visibility, plans a small number of falsifiable experiments, implements the changes you
authorize, checks them on the live site, and scores the outcome without flattering itself.

## Installation

```bash
# Add marketplace (one-time)
/plugin marketplace add vladuma/seo-routine

# Install into any project
/plugin install seo-routine@vladuma
```

## Quick start

```bash
/seo-routine calibrate     # one-time setup (or upgrade from an older config)

# Then, as often as you like:
/seo-routine analyze       # collect and reconcile data, rank evidence-backed opportunities
/seo-routine plan          # register at most the configured number of experiments
/seo-routine implement     # edit in a worktree, run independent review and the repo's checks
/seo-routine publish       # the configured, authorized action (e.g. open a PR)
/seo-routine verify        # check the deployed site
/seo-routine review        # score due predictions once
```

## Commands

| Command | What it does |
|---|---|
| `calibrate` | Discovers the project, asks a few questions, writes or upgrades `seo-config.md`, tests data sources |
| `analyze` | Collects and reconciles GSC, analytics, DataForSEO and a bounded self-crawl; ranks opportunities with their evidence |
| `plan` | Registers zero to N experiments in the ledger with predeclared baselines, targets and horizons |
| `implement` | Makes the planned edits, runs checks, gets an independent adversarial review. `--dry-run` shows the diff only |
| `publish` | Runs the configured publisher action when authorized; PR, merge and deploy are tracked separately |
| `verify` | Checks changed URLs on production: status, canonical, indexability, claims, schema, sitemap |
| `review` | Scores predictions whose live exposure and horizon exist, by direction and progress |
| `geo` | Runs a fixed AI-answer panel and reports it next to real AI-referral outcomes |
| `autopilot` | The whole cycle inside your authorized scope, with every phase's state recorded |
| `status` | Latest data dates, experiments and their review/PR/deploy/live states, next due dates |
| `goals "..."` | Sets the strategic goal and archives the previous one |

## What makes it different

- **Evidence, not scores.** Opportunities are ranked by recorded mechanism, evidence, the best competing
  explanation and what would refute it. There is no composite number, and no weights quietly tuned from
  a few results.
- **Budgets are maxima.** Zero experiments is a valid week. A verified fix is recorded as a repair, not a
  growth prediction.
- **Honest scoring.** Predictions are scored once, by direction and progress toward a target declared in
  advance. Hit, Partial and Miss are reported separately. Missing or confounded evidence is
  `pending`, `insufficient_evidence`, `confounded` or `unscorable`, never a Hit.
- **Separate states.** `local_only`, `pr_open`, `merged`, `deployed` and live verification are recorded
  independently. The outcome window only starts after live verification.
- **Failed sources are gaps.** A source that errors is never silently treated as zero traffic. GSC data
  is finalized, with property totals kept apart from page and query rows, and unknown query coverage
  reported instead of called nonbrand.
- **Independent review.** A fresh read-only reviewer must `PASS` content changes before they are
  published.
- **GEO as an instrument.** A fixed, versioned prompt panel is reported with its misses and sample sizes,
  beside actual AI referral visits and signups. Research-derived tactics are hypotheses, not promised
  uplifts.

## Data sources

| Source | Type | Requires |
|---|---|---|
| Google Search Console | Automated (`scripts/gsc.py`) | Service account or OAuth client with access |
| Google Analytics 4 | Automated, cross-check | Same Google credentials |
| Analytics provider (Umami, Plausible, ...) | Collector you configure | Provider URL and site ID |
| DataForSEO | Automated | Login and password |
| Ahrefs | Manual CSV drops or API | Subscription |
| AI answers | `scripts/geo_panel.py` | DataForSEO credentials and a panel file |
| Self-crawl | Always on | Nothing |

Credentials live in `.env.seo`, which calibrate adds to `.gitignore`.

## What it writes into your project

```
{root}/                              # default: docs/seo/
├── seo-config.md                    # settings (config version 4)
├── experiments.json                 # experiment ledger: predictions, delivery, verification, evaluation
├── goals.md  learnings.md
├── geo-panel.json  geo-scorecard.md # when GEO is enabled
└── weeks/<ISO-week>/<run-date>/     # inputs/, analysis.md, plan.md, changes.md, verify.md, review.md
```

## Upgrading from 1.x

Run `/seo-routine calibrate`. It migrates a v1-v3 config to v4, keeps your site, competitors, data
sources and credentials, retires the composite scoring weights and weekly quotas, and leaves your
`forward-log.md`, scorecards and weekly folders untouched as historical evidence. Old forward-log
predictions are not auto-scored under the new rules. See the migration table in `skills/seo-routine/SKILL.md`.

## Repository layout

This repository is a Claude Code marketplace. The plugin lives at `skills/seo-routine/`.

```
.claude-plugin/marketplace.json
skills/seo-routine/
├── .claude-plugin/plugin.json
├── SKILL.md              # router, setup, calibration and migrations, publishers, autopilot
├── references/           # measurement, experiments, delivery, geo + SEO/GEO background
├── scripts/              # Python collectors
├── templates/            # scaffolding written by calibrate
└── skills-ref/           # gap-finder, competitor-intel, brand-writer notes
docs/design-spec.md
```

## License

MIT
