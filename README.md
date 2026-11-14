# Filecon

File-type icons for **703 formats** in three styles – for every framework. [filecon.dev](https://filecon.dev)

- **3 styles**: `default` (outline, colored label), `gray` (filled gray page), `solid` (filled colored page)
- **Light, dark and `auto`** (follows `prefers-color-scheme`, SSR-safe, no hydration mismatch)
- **Smart resolver**: file name → magic bytes → extension (`Thumbs.db`, `Dockerfile`, SQLite vs. generic `.db`,
  MPEG-TS vs. TypeScript `.ts`, …)
- **Tree-shakable** single icons (`PdfIcon`, `TsStreamIcon`, `Icon7z`, …) and single-style packages for small bundles
- Accessible by default: `aria-hidden` without `title`, `role="img"` + `<title>` with it
- Apache-2.0, no third-party logos, labels embedded as paths (no font needed)

## Packages

| Package | |
|---|---|
| [`@filecon/shared`](packages/shared) | SVG files, manifest, types, resolver |
| [`@filecon/js`](packages/js) | framework-free: `getIcon()` → SVG string |
| [`@filecon/react`](packages/react) | React components (SSR/RSC-safe) |
| [`@filecon/preact`](packages/preact) | Preact components |
| [`@filecon/react-native`](packages/react-native) | React Native / Expo via `react-native-svg` |
| [`@filecon/vue`](packages/vue) | Vue 3 components (render functions, no SFC build) |
| [`@filecon/svelte`](packages/svelte) | Svelte 5 components |
| [`@filecon/solid`](packages/solid) | SolidJS components |
| [`@filecon/angular`](packages/angular) | Angular standalone component `<filecon-icon>` |
| [`@filecon/astro`](packages/astro) | Astro components (zero client JS) |

Every framework package exists in four flavors: `@filecon/<fw>` (all styles, `style` prop) and
`@filecon/<fw>-default`, `-gray`, `-solid` (one style each, same API without `style`).

## Quick start

```sh
npm install @filecon/react
```

```tsx
import { FileIcon } from "@filecon/react";
import { PdfIcon } from "@filecon/react/icons";

<FileIcon name="pdf" />
<FileIcon file="report.final.pdf" />
<FileIcon name="db-sqlite" style="solid" theme="dark" size={48} />
<FileIcon name="png" theme="auto" title="PNG image" />
<PdfIcon size={24} />
```

Without a framework:

```ts
import { getIcon, getFileIcon } from "@filecon/js";

element.innerHTML = getIcon("pdf", { style: "gray", theme: "dark" });
element.innerHTML = getFileIcon("data.db", { head: firstKilobyte }); // SQLite -> db-sqlite
```

## Development

Requirements: Node ≥ 22.18, pnpm 11 (Rust stable for the crate). The repository must be on a file system with
symlink support.

```sh
pnpm install
pnpm lint && pnpm typecheck && pnpm build && pnpm test
```

- `icon-pack/` is the read-only source of truth. Generated code (`src/generated/`) is created by `pnpm codegen`
  (part of `build`/`typecheck`) and never committed.
- Framework packages are generated from `tools/templates/<fw>/`: a new framework is just a new template.
- See [`CLAUDE.md`](CLAUDE.md) for conventions and [`ISSUES.md`](ISSUES.md) for known issues.

## License

Apache-2.0, see [`LICENSE`](LICENSE) and [`NOTICE`](NOTICE). The label glyphs are outlines of Inter Bold
(SIL Open Font License 1.1).
