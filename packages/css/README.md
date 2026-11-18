# @filecon/css

[Filecon](https://filecon.dev) file icons as plain CSS classes – 703 file types, no JavaScript. Every icon is an
embedded SVG (data URI) background image.

```sh
npm install @filecon/css
```

```css
@import "@filecon/css";            /* default style, light + dark via prefers-color-scheme */
```

```html
<i class="filecon filecon-pdf" role="img" aria-label="PDF document"></i>
<span class="filecon filecon-zip" aria-hidden="true"></span>
```

## Stylesheets

| File | Style | Theme |
|---|---|---|
| `@filecon/css` = `@filecon/css/default.css` | default (outline, colored label) | auto (`prefers-color-scheme`) |
| `@filecon/css/default-light.css`, `default-dark.css` | default | fixed |
| `@filecon/css/gray.css` | gray (filled gray page) | auto |
| `@filecon/css/gray-light.css`, `gray-dark.css` | gray | fixed |
| `@filecon/css/solid.css` | solid (filled colored page) | light and dark |

Without a bundler, link the file from a CDN:

```html
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@filecon/css@0.1/dist/default.css" />
```

## Classes

- `.filecon` – base class: `inline-block`, 40×40 px, background `no-repeat center / contain`. Change the size
  with `width`/`height` (or `font-size` + `1em` if you prefer).
- `.filecon-<name>` – the icon (`filecon-pdf`, `filecon-db-sqlite`, `filecon-7z`, …).

Background images are invisible to screen readers: add `role="img"` + `aria-label` for meaningful icons, or
`aria-hidden="true"` for decorative ones. To pick the icon for a file name at runtime, use the resolver from
`@filecon/js` (`resolveIcon("report.pdf")` → `"pdf"`).

Each stylesheet contains all 703 icons (a few hundred kB gzipped). If you only need a handful of icons, use a
JavaScript package (`@filecon/js`, `@filecon/react`, …) or `@filecon/iconify` with UnoCSS for on-demand CSS.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
