# seo-routine

Data-driven weekly SEO optimization routine for Claude Code. Analyzes performance, plans improvements, implements changes, and tracks predictions vs actuals to learn what works.

## Installation

```bash
# Add marketplace (one-time)
/plugin marketplace add vladuma/seo-routine

# Install into any project
/plugin install seo-routine@vladuma
```

## Quick Start

```bash
# 1. Set up for your project (one-time)
/seo-routine calibrate

# 2. Weekly cycle
/seo-routine analyze       # Collect data, score opportunities
/seo-routine plan          # Pick top items, create plan
/seo-routine implement     # Execute in git worktree
/seo-routine review        # Compare predictions vs actuals
```

## Commands

| Command | What it does |
|---------|-------------|
| `calibrate` | Discovers project structure, asks 3-5 questions, generates `seo-config.md` |
| `analyze` | Collects data from GSC, analytics, DataForSEO, self-crawl; scores all pages |
| `plan` | Selects top opportunities within weekly budget, writes plan with predictions |
| `implement` | Executes plan in isolated git worktree on `seo/YYYY-WNN` branch |
| `review` | Scores past predictions (Hit/Partial/Miss), updates scorecard, adjusts weights |
| `status` | Shows current week, pending work, last run summary |
| `goals "..."` | Sets or updates strategic goal for weighted scoring |

## How It Works

### Composite Scoring Model

Each page/keyword gets a score (0-100) based on 6 weighted signals:

| Signal | Default Weight | What it measures |
|--------|---------------|-----------------|
| Striking distance | 25% | Pages at positions 5-20 with decent impressions |
| CTR gap | 20% | Pages underperforming expected CTR for their position |
| Content quality | 15% | Missing FAQ, short content, no schema, no internal links |
| Technical debt | 15% | Missing canonical, broken meta, no og:image, CWV issues |
| Keyword gap | 15% | Keywords where competitors rank but you don't |
| Goal alignment | 10% | Pages/keywords matching your active strategic goal |

Weights automatically adjust based on prediction accuracy over time.

### Prediction Tracking

Every planned change includes a measurable prediction:
> "Rewriting meta + FAQ for /blog/example will move position from 14 to 8 by W14"

The review phase scores each prediction as Hit (>=75% of target), Partial (25-74%), or Miss (<25%). This feedback loop adjusts scoring weights so the model gets smarter over time.

### Data Sources

| Source | Type | Requires |
|--------|------|----------|
| Google Search Console | Automated | Service account with GSC access |
| Google Analytics 4 | Automated | Service account with GA4 access |
| Umami | Automated | Umami URL + website ID |
| DataForSEO | Automated | DataForSEO login + password |
| Ahrefs | Manual CSV drops | Ahrefs subscription |
| Self-crawl | Automated (always on) | Nothing — crawls your own site |

## Typical Weekly Flow

```
Monday:
  1. Drop Ahrefs CSVs into docs/seo/weeks/YYYY-WNN/inputs/
  2. /seo-routine analyze         → produces analysis.md
  3. /seo-routine plan            → produces plan.md, review + approve

Tuesday-Thursday:
  4. /seo-routine implement       → creates branch, makes changes
  5. Review PR, merge

Next Monday:
  6. /seo-routine review          → scores past predictions
  7. Back to step 1
```

## Project Structure

This repo is a Claude Code marketplace. The actual plugin lives at `skills/seo-routine/`. All script/reference paths in SKILL.md are relative to the plugin root.

```
seo-routine/                         # marketplace repo
├── .claude-plugin/marketplace.json  # marketplace index
├── skills/seo-routine/              # the plugin
│   ├── .claude-plugin/plugin.json   # plugin manifest
│   ├── SKILL.md                     # core engine
│   ├── scripts/                     # Python automation
│   ├── references/                  # SEO/GEO knowledge base
│   ├── templates/                   # scaffolding templates
│   └── skills-ref/                  # sub-skill reference docs
├── docs/                            # design spec
└── README.md

# Generated in your project by calibrate:
{root}/                              # default: docs/seo/
├── seo-config.md                    # project-specific config
├── goals.md                         # strategic goals
├── scorecard.md                     # weekly metrics
├── forward-log.md                   # prediction tracking
├── brand-voice.md                   # brand voice guide (if content pipeline detected)
└── weeks/YYYY-WNN/                  # weekly data
    ├── inputs/                      # manual data drops
    ├── analysis.md                  # Phase 1 output
    ├── plan.md                      # Phase 2 output
    └── changes.md                   # Phase 3 output
```

## GEO Optimization

Content changes incorporate Princeton GEO research methods for AI search visibility:

- **Cite Sources** (+40%) — authoritative references
- **Statistics** (+37%) — specific data points
- **Authoritative Tone** (+25%) — expert-level language
- **FAQ Schema** — structured data for AI citation

## License

MIT
