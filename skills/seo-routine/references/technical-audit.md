# Technical SEO Audit Reference

## 8-Category Technical Audit Checklist

| # | Category | Key Checks |
|---|----------|------------|
| 1 | **Crawlability** | robots.txt valid and not blocking resources; XML sitemap exists and referenced; no accidental noindex; crawl depth <=3 clicks; JS rendering of critical content; crawl budget (sites >10k pages) |
| 2 | **Indexability** | Self-referencing canonicals, no canonical/noindex conflicts; duplicate content (params, www/non-www); thin content; pagination (rel=next/prev); hreflang; index bloat |
| 3 | **Security** | HTTPS enforced, valid SSL, no mixed content; security headers present (see table below); HSTS preload for high-security sites |
| 4 | **URL Structure** | Clean, descriptive, hyphenated URLs; logical hierarchy; no redirect chains (max 1 hop, 301 for permanent); flag URLs >100 chars; consistent trailing slashes |
| 5 | **Mobile** | Viewport meta tag; responsive CSS; touch targets >=48x48px with 8px spacing; base font >=16px; no horizontal scroll |
| 6 | **Core Web Vitals** | LCP, INP, CLS (see thresholds below) |
| 7 | **Structured Data** | JSON-LD preferred; validate against Google supported types; check Microdata/RDFa |
| 8 | **JS Rendering** | Content in initial HTML vs JS-required; CSR vs SSR identification; flag SPA frameworks; verify dynamic rendering |

## Core Web Vitals Thresholds

Evaluated at the **75th percentile** of real user data (CrUX).

| Metric | Good | Needs Improvement | Poor |
|--------|------|--------------------|------|
| **LCP** (Largest Contentful Paint) | <2.5s | 2.5s - 4.0s | >4.0s |
| **INP** (Interaction to Next Paint) | <200ms | 200ms - 500ms | >500ms |
| **CLS** (Cumulative Layout Shift) | <0.1 | 0.1 - 0.25 | >0.25 |

INP replaced FID on March 12, 2024. FID was fully removed from all Chrome tools (CrUX API, PageSpeed Insights, Lighthouse) on September 9, 2024. Do NOT reference FID.

## Mobile-First Indexing

**100% complete as of July 5, 2024.** Google now crawls and indexes ALL websites exclusively with the mobile Googlebot user-agent. There is no separate desktop-first index.

## JavaScript SEO Clarifications (December 2025)

| Issue | Guidance |
|-------|----------|
| **Canonical conflicts** | If canonical in raw HTML differs from JS-injected canonical, Google may use EITHER one. Ensure they are identical. |
| **noindex in raw HTML** | If raw HTML has `noindex` but JS removes it, Google MAY still honor the raw HTML noindex. Serve correct directives in initial HTML. |
| **Non-200 status codes** | Google does NOT render JS on non-200 pages. JS-injected content/meta on error pages is invisible to Googlebot. |
| **JS-injected structured data** | Product, Article, and other structured data via JS may face delayed processing. Include time-sensitive markup in server-rendered HTML. |

**Best practice:** Serve canonical, meta robots, structured data, title, and meta description in the initial server-rendered HTML.

## AI Crawler Management

| Crawler | Company | robots.txt Token | Purpose |
|---------|---------|-------------------|---------|
| GPTBot | OpenAI | `GPTBot` | Model training |
| ChatGPT-User | OpenAI | `ChatGPT-User` | Real-time browsing |
| ClaudeBot | Anthropic | `ClaudeBot` | Model training |
| PerplexityBot | Perplexity | `PerplexityBot` | Search index + training |
| Bytespider | ByteDance | `Bytespider` | Model training |
| Google-Extended | Google | `Google-Extended` | Gemini training (NOT search) |
| CCBot | Common Crawl | `CCBot` | Open dataset |

**Key distinctions:**
- Blocking `Google-Extended` does NOT affect Google Search indexing or AI Overviews (those use `Googlebot`)
- Blocking `GPTBot` does NOT prevent ChatGPT from citing content via browsing (`ChatGPT-User`)

## Security Headers Checklist

| Header | Purpose |
|--------|---------|
| `Content-Security-Policy` (CSP) | Controls which resources the browser can load |
| `Strict-Transport-Security` (HSTS) | Forces HTTPS connections; consider HSTS preload for high-security sites |
| `X-Frame-Options` | Prevents clickjacking via iframe embedding |
| `X-Content-Type-Options` | Prevents MIME-type sniffing |
| `Referrer-Policy` | Controls referrer information sent with requests |

## IndexNow Protocol

IndexNow enables instant URL submission to Bing, Yandex, and Naver. Not supported by Google. Recommend implementation for faster indexing on non-Google search engines.
