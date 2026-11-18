# @filecon/js-chalk

Framework-free [Filecon](https://filecon.dev) file icons as SVG strings – 703 file types, the chalk style (chalk on a blackboard, marker on a whiteboard).

Part of the Filecon family: `@filecon/js`, `@filecon/js-default`, `@filecon/js-gray`, `@filecon/js-solid`, `@filecon/js-papered`, `@filecon/js-papered-flat`, `@filecon/js-papered-craft`, `@filecon/js-scratch`, `@filecon/js-chalk`.
This package only contains the `chalk` style, so it is smaller than `@filecon/js`; the API is identical except that there is no `style` option.

```sh
npm install @filecon/js-chalk
```

## Usage

```ts
import { getIcon, getFileIcon, resolveIcon, toDataUri, iconNames } from "@filecon/js-chalk";

getIcon("pdf");                                   // <svg …>…</svg>
getIcon("db-sqlite", { theme: "dark", size: 48 });
getFileIcon("report.final.pdf");                  // resolves via the file name
getFileIcon("data.db", { head: firstBytes });     // magic bytes: SQLite -> db-sqlite
resolveIcon("Dockerfile");                        // "dockerfile"
img.src = toDataUri(getIcon("png", { title: "PNG image" }));
iconNames.length;                                 // 703
```

Tree-shakable single icons:

```ts
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/js-chalk/icons";

document.body.innerHTML = PdfIcon({ theme: "auto", title: "PDF" });
```

## Options

| Option | Type | Default | |
|---|---|---|---|
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet (SSR-safe).  |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `className` | `string` | – | `class` attribute |
| `attributes` | `Record<string, …>` | – | extra attributes on `<svg>` |

## Data entry

`@filecon/js-chalk/data` exports the raw icon data (`d_pdf`, …, `iconData`) used by the framework packages.
Only the inner SVG markup is stored; the outer `<svg viewBox="0 0 40 40" fill="none">` is added at render time.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
