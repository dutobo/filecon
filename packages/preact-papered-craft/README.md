# @filecon/preact-papered-craft

[Filecon](https://filecon.dev) file icons for Preact – 703 file types, the papered-craft style (cut paper layers).
SSR-safe (preact-render-to-string), tree-shakable, no runtime dependencies besides Preact.

Part of the Filecon family: `@filecon/preact`, `@filecon/preact-default`, `@filecon/preact-gray`, `@filecon/preact-solid`, `@filecon/preact-papered`, `@filecon/preact-papered-flat`, `@filecon/preact-papered-craft`, `@filecon/preact-scratch`, `@filecon/preact-chalk`, `@filecon/preact-iconic`.
This package only contains the `papered-craft` style, so it is smaller than `@filecon/preact`; the API is identical except that there is no `style` prop (`style` is the regular inline-CSS prop here).

![File icons in the Papered Craft style, light and dark](https://raw.githubusercontent.com/dutobo/filecon/main/docs/previews/style-papered-craft.png)

```sh
npm install @filecon/preact-papered-craft
```

## Usage

```tsx
import { FileIcon } from "@filecon/preact-papered-craft";

<FileIcon name="pdf" />                                  // icon name / extension
<FileIcon file="report.final.pdf" />                     // picked by the resolver (file name only)
<FileIcon name="db-sqlite" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />   // follows prefers-color-scheme
```

Tree-shakable single icons:

```tsx
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/preact-papered-craft/icons";

<PdfIcon size={24} className="icon" />
```

Component names are PascalCase + `Icon` (`ts-stream` → `TsStreamIcon`); names starting with a digit get an
`Icon` prefix (`7z` → `Icon7z`). `iconComponentName(name)` returns the name for any icon.

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet – identical markup on server and client, no hydration mismatch |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `className`, … | SVG props | – | forwarded to `<svg>` (`ref` too on Preact 11, where `ref` is a regular prop) |

## Notes

- Built with `tsup` (ESM + CJS + `.d.ts`). Components use `h`, no JSX runtime needed. Peer: Preact 10.19+ or 11.
- Icon data comes from `@filecon/js-papered-craft` (only the inner SVG markup is stored once).

## Preview by category

![File icons in the Papered Craft style for every category, light and dark](https://raw.githubusercontent.com/dutobo/filecon/main/docs/previews/categories-papered-craft.png)

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
