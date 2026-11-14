# {{packageName}}

[Filecon](https://filecon.dev) file icons for Svelte 5 – {{iconCount}} file types, {{styleLabel}}.
SSR-safe (SvelteKit), tree-shakable.

Part of the Filecon family: {{siblings}}.
{{#isSingle}}This package only contains the `{{fixedStyle}}` style, so it is smaller than `{{allPackage}}`; the API is identical except that there is no `style` prop (`style` is the regular inline-CSS attribute here).{{/isSingle}}

```sh
npm install {{packageName}}
```

## Usage

```svelte
<script>
  import { FileIcon } from "{{packageName}}";
  import { PdfIcon, TsStreamIcon, Icon7z } from "{{packageName}}/icons";
</script>

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" {{#isAll}}style="solid" {{/isAll}}theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />
<PdfIcon size={24} class="icon" />
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
{{#isAll}}| `style` | `"default" \| "gray" \| "solid"` | `"default"` | icon style (not inline CSS) |
{{/isAll}}| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet – no hydration mismatch |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |
| `class`, … | SVG attributes | – | forwarded to `<svg>` |

`Icon` renders raw icon data (`<Icon data={d_pdf} />` with `d_pdf` from `{{dataPackage}}/data`).

## Notes

- Built with `svelte-package`: the package ships `.svelte` components (compiled by your app) plus `.d.ts` files.
- Requires Svelte 5 (runes).

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
