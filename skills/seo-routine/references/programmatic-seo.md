# Programmatic SEO Reference

## Thin Content Uniqueness Calculation

```
Unique content % = (words unique to this page) / (total words on page) x 100
```

Measured against all other pages in the programmatic set. Shared headers, footers, and navigation are **excluded**. Template boilerplate text **is included**.

## Quality Gates

| Metric | Threshold | Action |
|--------|-----------|--------|
| Pages without content review | 100+ | WARNING — require content audit before publishing |
| Pages without justification | 500+ | HARD STOP — require explicit approval and thin content audit |
| Unique content per page | <40% | FLAG as thin content — likely penalty risk |
| Unique content per page | <30% | Recommended HARD STOP — scaled content abuse risk |
| Word count per page | <300 | FLAG for review — may lack sufficient value |
| Content differentiation | <30-40% unique between any two pages | Risk of scaled content abuse penalty |
| Human review sample | Minimum 5-10% of generated pages | Required before publishing |
| Progressive rollout | Batches of 50-100 pages | Monitor indexing 2-4 weeks before expanding |

## Safe Programmatic SEO Examples

| Page Type | Why It Works |
|-----------|-------------|
| Integration pages | Real setup docs, API details, screenshots |
| Template/tool pages | Downloadable content, usage instructions |
| Glossary pages | 200+ word definitions with examples, related terms |
| Product pages | Unique specs, reviews, comparison data |
| Data-driven pages | Unique statistics, charts, analysis per record |

## Penalty Risk Examples

| Pattern | Problem |
|---------|---------|
| City name swaps in identical text | No unique value per location |
| "Best [tool] for [industry]" | No industry-specific content |
| "[Competitor] alternative" | No real comparison data |
| AI-generated without human review | No unique value-add |
| >60% shared template boilerplate | Thin content signal |

## Scaled Content Abuse Timeline

| Date | Event |
|------|-------|
| March 2024 | Google introduces Scaled Content Abuse policy |
| November 2024 | Site reputation abuse enforcement begins (high-authority domains hosting third-party programmatic content) |
| June 2025 | Manual action wave targeting AI-generated content at scale |
| August 2025 | SpamBrain update — enhanced pattern detection for AI content farms and link schemes |

**Result:** Google reported 45% reduction in low-quality, unoriginal content in search results post-March 2024 enforcement.

**Standalone value test:** "Would this page be worth publishing even if no other similar pages existed?"

## URL Pattern Best Practices

| Pattern | Use Case |
|---------|----------|
| `/tools/[tool-name]` | Tool/product directory |
| `/[city]/[service]` | Location + service |
| `/integrations/[platform]` | Integration landing pages |
| `/glossary/[term]` | Definition/reference |
| `/templates/[template-name]` | Downloadable templates |

**Rules:**
- Lowercase, hyphenated slugs derived from data
- Logical hierarchy reflecting site architecture
- Enforce slug uniqueness at generation time
- Keep URLs under 100 characters
- No query parameters for primary content URLs
- Consistent trailing slash usage (match existing site)

## Internal Linking Automation

| Strategy | Detail |
|----------|--------|
| Hub/spoke model | Category hub pages linking to individual programmatic pages |
| Related items | Auto-link to 3-5 related pages based on shared data attributes |
| Breadcrumbs | Generate BreadcrumbList schema from URL hierarchy |
| Cross-linking | Link pages sharing attributes (same category, city, feature) |
| Anchor text | Descriptive, varied — avoid exact-match keyword repetition |
| Link density | **3-5 internal links per 1000 words** |

## Index Bloat Prevention Checklist

- [ ] Noindex pages that don't meet quality gates
- [ ] Noindex paginated results beyond page 1 (or use rel=next/prev)
- [ ] Noindex faceted navigation / filtered views; canonical to base category
- [ ] Monitor crawl stats in Search Console for sites with >10k programmatic pages
- [ ] Merge records with insufficient data into aggregated pages
- [ ] Monthly audit: indexed page count vs intended count
- [ ] Auto-generate sitemap entries (split at 50,000 URLs per file)
- [ ] Use `<lastmod>` with actual data update timestamp (not generation time)
- [ ] Exclude noindexed pages from sitemap
- [ ] Register sitemap in robots.txt

## Canonical Strategy for Programmatic Pages

| Scenario | Canonical Target |
|----------|-----------------|
| Standard programmatic page | Self-referencing canonical |
| Parameter variations (sort, filter, pagination) | Base URL |
| Paginated series | Page 1 (or use rel=next/prev) |
| Overlap with manual page | Manual page is canonical |
| Cross-domain | Only if intentional cross-domain setup |
