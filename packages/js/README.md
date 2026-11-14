# @filecon/js

Framework-free [Filecon](https://filecon.dev) file icons as SVG strings – 703 file types, all three styles (default, gray, solid).

Part of the Filecon family: `@filecon/js`, `@filecon/js-default`, `@filecon/js-gray`, `@filecon/js-solid`.


```sh
npm install @filecon/js
```

## Usage

```ts
import { getIcon, getFileIcon, resolveIcon, toDataUri, iconNames } from "@filecon/js";

getIcon("pdf");                                   // <svg …>…</svg>
getIcon("db-sqlite", { style: "solid", theme: "dark", size: 48 });
getFileIcon("report.final.pdf");                  // resolves via the file name
getFileIcon("data.db", { head: firstBytes });     // magic bytes: SQLite -> db-sqlite
resolveIcon("Dockerfile");                        // "dockerfile"
img.src = toDataUri(getIcon("png", { title: "PNG image" }));
iconNames.length;                                 // 703
```

Tree-shakable single icons:

```ts
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/js/icons";

document.body.innerHTML = PdfIcon({ theme: "auto", title: "PDF" });
```

## Options

| Option | Type | Default | |
|---|---|---|---|
| `style` | `"default" \| "gray" \| "solid"` | `"default"` | |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet (SSR-safe). `solid` ignores the theme. |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `className` | `string` | – | `class` attribute |
| `attributes` | `Record<string, …>` | – | extra attributes on `<svg>` |

## Data entry

`@filecon/js/data` exports the raw icon data (`d_pdf`, …, `iconData`) used by the framework packages.
Only the inner SVG markup is stored; the outer `<svg viewBox="0 0 40 40" fill="none">` is added at render time.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
