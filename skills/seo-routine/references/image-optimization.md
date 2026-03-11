# Image Optimization Reference

## File Size Thresholds

| Image Category | Target | Warning | Critical |
|----------------|--------|---------|----------|
| Thumbnails | < 50KB | > 100KB | > 200KB |
| Content images | < 100KB | > 200KB | > 500KB |
| Hero/banner images | < 200KB | > 300KB | > 700KB |

## Format Recommendations

| Format | Browser Support | Use Case |
|--------|----------------|----------|
| WebP | 97%+ | Default recommendation |
| AVIF | 92%+ | Best compression, newer |
| JPEG | 100% | Fallback for photos |
| PNG | 100% | Graphics with transparency |
| SVG | 100% | Icons, logos, illustrations |

Prefer WebP/AVIF over JPEG/PNG. Use `<picture>` element for format fallbacks.

## Picture Element Pattern

AVIF first, WebP second, JPEG fallback:

```html
<picture>
  <source srcset="image.avif" type="image/avif">
  <source srcset="image.webp" type="image/webp">
  <img src="image.jpg" alt="Descriptive alt text" width="800" height="600" loading="lazy" decoding="async">
</picture>
```

## Lazy Loading

| Position | Attributes |
|----------|------------|
| Above fold (LCP) | `fetchpriority="high"` -- no `loading="lazy"` |
| Below fold | `loading="lazy" decoding="async"` |

```html
<!-- LCP / hero image -->
<img src="hero.webp" fetchpriority="high" alt="Hero description" width="1200" height="630">

<!-- Below-fold image -->
<img src="photo.webp" loading="lazy" decoding="async" alt="Description" width="600" height="400">
```

Never lazy-load LCP images -- it directly harms LCP scores.

## Alt Text

| Quality | Example | Problem |
|---------|---------|---------|
| Good | "Professional plumber repairing kitchen sink faucet" | -- |
| Good | "Red 2024 Toyota Camry sedan front view" | -- |
| Good | "Team meeting in modern office conference room" | -- |
| Bad | "image.jpg" | Filename, not description |
| Bad | "plumber plumbing plumber services" | Keyword stuffing |
| Bad | "Click here" | Not descriptive |

Target length: 10-125 characters. Include relevant keywords naturally.

## CLS Prevention

Always set explicit dimensions on `<img>` elements:

```html
<!-- Width/height attributes -->
<img src="photo.jpg" width="800" height="600" alt="Description">

<!-- CSS aspect-ratio alternative -->
<img src="photo.jpg" style="aspect-ratio: 4/3" alt="Description">
```

Images without dimensions cause layout shifts (CLS).

## Responsive Images (srcset/sizes)

```html
<img
  src="image-800.jpg"
  srcset="image-400.jpg 400w, image-800.jpg 800w, image-1200.jpg 1200w"
  sizes="(max-width: 600px) 400px, (max-width: 1200px) 800px, 1200px"
  alt="Description"
>
```

- `srcset`: list available widths
- `sizes`: map viewport breakpoints to rendered image width
