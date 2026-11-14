# {{packageName}}

Framework-free [Filecon](https://filecon.dev) file icons as SVG strings – {{iconCount}} file types, {{styleLabel}}.

Part of the Filecon family: {{siblings}}.
{{#isSingle}}This package only contains the `{{fixedStyle}}` style, so it is smaller than `{{allPackage}}`; the API is identical except that there is no `style` option.{{/isSingle}}

```sh
npm install {{packageName}}
```

## Usage

```ts
import { getIcon, getFileIcon, resolveIcon, toDataUri, iconNames } from "{{packageName}}";

getIcon("pdf");                                   // <svg …>…</svg>
getIcon("db-sqlite", { {{#isAll}}style: "solid", {{/isAll}}theme: "dark", size: 48 });
getFileIcon("report.final.pdf");                  // resolves via the file name
getFileIcon("data.db", { head: firstBytes });     // magic bytes: SQLite -> db-sqlite
resolveIcon("Dockerfile");                        // "dockerfile"
img.src = toDataUri(getIcon("png", { title: "PNG image" }));
iconNames.length;                                 // {{iconCount}}
```

Tree-shakable single icons:

```ts
import { PdfIcon, TsStreamIcon, Icon7z } from "{{packageName}}/icons";

document.body.innerHTML = PdfIcon({ theme: "auto", title: "PDF" });
```

## Options

| Option | Type | Default | |
|---|---|---|---|
{{#isAll}}| `style` | `"default" \| "gray" \| "solid"` | `"default"` | |
{{/isAll}}| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet (SSR-safe). {{#isAll}}`solid` ignores the theme.{{/isAll}}{{#isSingle}}{{/isSingle}} |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `className` | `string` | – | `class` attribute |
| `attributes` | `Record<string, …>` | – | extra attributes on `<svg>` |

## Data entry

`{{packageName}}/data` exports the raw icon data (`d_pdf`, …, `iconData`) used by the framework packages.
Only the inner SVG markup is stored; the outer `<svg viewBox="0 0 40 40" fill="none">` is added at render time.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
