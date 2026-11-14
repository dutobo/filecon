# @filecon/vue

[Filecon](https://filecon.dev) file icons for Vue 3 – 703 file types, all three styles (default, gray, solid).
SSR-safe (Nuxt), tree-shakable, written with `defineComponent` + render functions (no SFC build step needed).

Part of the Filecon family: `@filecon/vue`, `@filecon/vue-default`, `@filecon/vue-gray`, `@filecon/vue-solid`.


```sh
npm install @filecon/vue
```

## Usage

```vue
<script setup lang="ts">
import { FileIcon } from "@filecon/vue";
import { PdfIcon } from "@filecon/vue/icons";
</script>

<template>
  <FileIcon name="pdf" />
  <FileIcon file="report.final.pdf" />
  <FileIcon name="db-sqlite" icon-style="solid" theme="dark" :size="48" />
  <FileIcon name="png" theme="auto" title="PNG image" />
  <PdfIcon :size="24" class="icon" />
</template>
```

## Props

| Prop | Type | Default | |
|---|---|---|---|
| `name` | `IconName \| string` | – | icon name or extension (exclusive with `file`) |
| `file` | `string` | – | file name, resolved with `resolveIcon` (exclusive with `name`) |
| `icon-style` | `"default" \| "gray" \| "solid"` | `"default"` | icon style |
| `theme` | `"light" \| "dark" \| "auto"` | `"light"` | `auto` embeds a `prefers-color-scheme` stylesheet – no hydration mismatch |
| `size` | `number \| string` | `40` | width and height |
| `title` | `string` | – | adds `<title>` and `role="img"`; without it the SVG is `aria-hidden="true"` |

`class`, `style` and other attributes fall through to the `<svg>`.

## Deviations from the other packages

- **`icon-style` instead of `style`**: Vue treats `style` as a reserved attribute (static `style="…"` is parsed as
  inline CSS), so the style prop is called `iconStyle` / `icon-style`.
- Components use `defineComponent` with render functions instead of `.vue` files, so the package is plain
  JavaScript built with `tsup` and needs no SFC compiler.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
