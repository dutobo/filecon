# @filecon/solid

[Filecon](https://filecon.dev) file icons for SolidJS – 703 file types, all eight styles (default, gray, solid, papered, papered-flat, papered-craft, scratch, chalk).
Works with client rendering, SSR (SolidStart) and hydration; tree-shakable.

Part of the Filecon family: `@filecon/solid`, `@filecon/solid-default`, `@filecon/solid-gray`, `@filecon/solid-solid`, `@filecon/solid-papered`, `@filecon/solid-papered-flat`, `@filecon/solid-papered-craft`, `@filecon/solid-scratch`, `@filecon/solid-chalk`.


```sh
npm install @filecon/solid
```

## Usage

```tsx
import { FileIcon } from "@filecon/solid";
import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/solid/icons";

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" style="solid" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />
<PdfIcon size={24} class="icon" />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
| `style` | `Style`: `"default"`, `"gray"`, `"solid"`, `"papered"`, `"papered-flat"`, `"papered-craft"`, `"scratch"`, `"chalk"` | `"default"` | icon style (not inline CSS) |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet – no hydration mismatch |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `class`, … | SVG props | – | forwarded to `<svg>` |

All props are reactive.

## Deviation from the usual Solid tooling

Solid libraries usually ship JSX compiled with `babel-preset-solid` (separate DOM and SSR builds). These components
render `<svg>` through `Dynamic` from `solid-js/web` instead, so the package is plain JavaScript built with `tsup`;
`solid-js/web` picks its DOM or server implementation through the normal export conditions.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
