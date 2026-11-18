# @filecon/shared

Core of [Filecon](https://filecon.dev): the 703 file icon SVGs of the three pack styles (`default`, `gray`, `solid`), the manifest, the TypeScript types
and the file-type resolver. All other `@filecon/*` packages build on it.

```sh
npm install @filecon/shared
```

## Contents

| Export | |
|---|---|
| `@filecon/shared/svg/default/{light,dark}/<name>.svg` | outline style, colored label |
| `@filecon/shared/svg/gray/{light,dark}/<name>.svg` | filled gray page |
| `@filecon/shared/svg/solid/<name>.svg` | filled colored page, white label (same in light and dark) |
| `@filecon/shared/manifest.json` | metadata per icon: `type`, `category`, `label`, `color`, `family`, `of`, `meaning`, `ambiguous` |
| `IconName` | string-literal union of all 703 names |
| `Style`, `Theme` | `"default" \| "gray" \| "solid"`, `"light" \| "dark" \| "auto"` |
| `resolveIcon(fileName, head?)` | picks an icon: file name → magic bytes (first 1 KB of `head`) → extension → `empty` |
| `iconNames`, `isIconName`, `toIconName` | name helpers |
| `iconComponentName(name)` | `pdf` → `PdfIcon`, `ts-stream` → `TsStreamIcon`, `7z` → `Icon7z` |
| `renderSvg`, `iconContent`, `svgAttributes`, `toDataUri` | rendering helpers used by the framework packages |

## Resolver

```ts
import { resolveIcon } from "@filecon/shared";

resolveIcon("report.final.pdf");                 // "pdf"
resolveIcon("Dockerfile");                       // "dockerfile"
resolveIcon("Makefile");                         // "mk"
resolveIcon("app.db", firstBytes);               // "db-sqlite" for "SQLite format 3\0…"
resolveIcon("clip.ts", firstBytes);              // "ts-stream" for MPEG-TS sync bytes, else "ts"
```

The resolver is a port of `icon-pack/resolve_icon.py` and passes the pack's `tests/resolve-cases.json`.
Without `head` only the file name and extension are used. Paths with `/` or `\` are accepted.

## Using the SVG files directly

```ts
import pdf from "@filecon/shared/svg/default/light/pdf.svg"; // with an SVG loader of your bundler
```

Prefer `@filecon/js` or a framework package (`@filecon/react`, `@filecon/vue`, …) for inline rendering,
`theme="auto"` and tree-shaking.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
