# @filecon/svelte-solid

[Filecon](https://filecon.dev) file icons for Svelte 5 – 703 file types, the solid style (filled colored page).
SSR-safe (SvelteKit), tree-shakable.

Part of the Filecon family: `@filecon/svelte`, `@filecon/svelte-default`, `@filecon/svelte-gray`, `@filecon/svelte-solid`.
This package only contains the `solid` style, so it is smaller than `@filecon/svelte`; the API is identical except that there is no `style` prop (`style` is the regular inline-CSS attribute here).

```sh
npm install @filecon/svelte-solid
```

## Usage

```svelte
<script>
  import { FileIcon } from "@filecon/svelte-solid";
  import { PdfIcon, TsStreamIcon, Icon7z } from "@filecon/svelte-solid/icons";
</script>

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />
<PdfIcon size={24} class="icon" />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet – no hydration mismatch |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `class`, … | SVG attributes | – | forwarded to `<svg>` |

`Icon` renders raw icon data (`<Icon data={d_pdf} />` with `d_pdf` from `@filecon/js-solid/data`).

## Notes

- Built with `svelte-package`: the package ships `.svelte` components (compiled by your app) plus `.d.ts` files.
- Requires Svelte 5 (runes).

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
