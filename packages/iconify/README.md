# @filecon/iconify

[Filecon](https://filecon.dev) file icons as [Iconify](https://iconify.design) JSON icon sets – 703 file types.
Use them with UnoCSS, `unplugin-icons` (Vite, Nuxt, Astro, …), the Iconify runtime or any tool that reads
Iconify JSON.

```sh
npm install -D @filecon/iconify
```

| Prefix | Style | Theme |
|---|---|---|
| `filecon` | default (outline, colored label) | light |
| `filecon-dark` | default | dark |
| `filecon-gray` | gray (filled gray page) | light |
| `filecon-gray-dark` | gray | dark |
| `filecon-solid` | solid (filled colored page) | light and dark |

Icons are multicolor (`palette: true`), 40×40. Icon names are the Filecon names (`pdf`, `db-sqlite`, `7z`, …).

## UnoCSS

```ts
// uno.config.ts
import { defineConfig, presetIcons } from "unocss";
import { collections } from "@filecon/iconify";

export default defineConfig({
  presets: [presetIcons({ collections })],
});
```

```html
<span class="i-filecon-pdf"></span>
<span class="i-filecon-gray-dark-zip text-3xl"></span>
```

## unplugin-icons (Vite, Nuxt, Astro, …)

```ts
import Icons from "unplugin-icons/vite";
import { collections } from "@filecon/iconify";

Icons({ customCollections: collections });
```

```ts
import PdfIcon from "~icons/filecon/pdf";
```

## Tailwind CSS

With the Iconify Tailwind plugin, load the sets from this package:

```js
// tailwind.config.js (Tailwind 3) – @iconify/tailwind
const { addIconSelectors } = require("@iconify/tailwind");

module.exports = {
  plugins: [addIconSelectors({ iconSets: { filecon: require("@filecon/iconify/filecon.json") } })],
};
```

```html
<span class="iconify filecon--pdf"></span>
```

## Iconify runtime / raw JSON

```ts
import { addCollection } from "@iconify/iconify"; // or iconify-icon / @iconify/react
import filecon from "@filecon/iconify/filecon";

addCollection(filecon);
```

Raw JSON: `@filecon/iconify/filecon.json`, `@filecon/iconify/filecon-dark.json`, … The default export of
`@filecon/iconify/<prefix>` is the same object.

## License

Apache-2.0 – see `LICENSE` and `NOTICE`. Label glyphs are outlines of Inter Bold (SIL OFL 1.1).
