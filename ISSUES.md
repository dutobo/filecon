# Issues

Problems and open points found while building the packages. The icon pack (`icon-pack/`) is the single source
of truth and is **never modified** here – pack issues are only recorded.

## Open TODOs

- [x] **Rust mobile: Tauri and Dioxus.** Built as `tauri-plugin-filecon` (+ JS binding `@filecon/tauri`) and
  `filecon-dioxus`. Only tested with Tauri's mock runtime and dioxus-ssr, not yet in real desktop/iOS/Android apps;
  the declared minimum Rust versions (1.85 / 1.90) come from the dependencies and were not built locally.
- [ ] **Not yet published: VS Code extension and Python package** (`extensions/vscode`, `ports/python`). They need
  Marketplace/Open VSX and PyPI accounts + tokens, see `docs/publishing.md`. The VS Code theme was packaged but not
  tried in a running VS Code; Python was only run on 3.12 locally (CI covers 3.9 and 3.13).
- [ ] **Go, Swift PM, Packagist, NuGet, pub.dev, RubyGems, Figma: not started** – they need a public repository
  with committed assets or toolchains that are not installed here (see `docs/publishing.md`).
- [ ] **Angular: no tree-shaking of the icon map.** `<filecon-icon>` supports `name`/`file`, so the component always
  contains the icon data of its package (~120 kB gzip per style, see `docs/sizes.md`). Single-icon definitions do not
  help here. Option: an additional data-free component (e.g. `<filecon-svg [icon]>`) – needs an API decision.
- [ ] **Rust has no `auto` theme.** The crate returns the original pack files (light or dark); an `auto` variant would
  need generated SVG files, which the brief excludes (`include_str!` of the pack SVGs).

## Icon pack

1. **Pack was delivered unpacked, not as `filecon-icon-pack.zip`.** The files were moved unchanged into `icon-pack/`
   (verified byte-identical; `.gitattributes` marks the folder `-text` so Git never touches line endings).
2. **README vs. resolver: family fallback.** `icon-pack/README.md` describes the chain
   "name → magic bytes → extension → `family` → `empty`", but `resolve_icon.py` never uses `family`
   (an extension that is in the manifest resolves to itself; unknown extensions go straight to `empty`).
   The TypeScript and Rust ports follow the reference implementation and its 20 test cases.
3. **Variants the resolver can never pick.** `db-paradox`, `pb-protobuf`, `pb-tf` and `dbf-oracle` are listed in
   `ambiguous`, but `resolve_icon.py` has no sniffing rule for them (only reachable by name).
4. **Visually identical icons.** In every style these groups render the same SVG (only `<title>` differs):
   `secret-key` = `key` = `key-private` = `pub-key`, `v` = `v-vlang`, `vhdl` = `vhd-vhdl`, `graphql` = `gql`,
   `sqlite` = `sqlite3` = `db-sqlite`, `pkl` = `pickle`. Most are intended aliases; questionable are
   `key-private`/`pub-key` (the resolver distinguishes them, the icons do not) and `v` = `v-vlang`
   (the "ambiguous" `v` icon carries the V-language look, so the neutral fallback is not neutral).
5. **Non-generic icons without `label`.** `db`, `key` (type `generic-ext`) and `key-private`, `pub-key`
   (type `variant`) have no `label` in the manifest, unlike the other variants.
6. **Name-only `Thumbs.db`.** `resolve_icon.py` only recognizes `Thumbs.db` inside the content sniffing step, so
   `resolveIcon("Thumbs.db")` without content returns `db` (ported as-is).
7. **Empty content for `.img`.** With content given but empty (`head = []`), `x.img` resolves to `img-disk`
   because the "not PNG/JPEG/GIF/RIFF" rule matches (ported as-is; without `head` it is `img`).

## Packages – known limitations (by design, documented in the READMEs)

- **Vue / Angular use `iconStyle` instead of `style`** (`style` is reserved/parsed as CSS there). Vue types `name` as
  `string` because the 703-member `IconName` union is too complex for Vue's prop inference.
- **Angular single icons are definitions** (`PdfIcon = { name, data }` for `[icon]`), not 703 components.
- **React Native `theme="auto"`** uses `useColorScheme()` (react-native-svg has no CSS media queries).
- **ng-packagr warnings**: the build warns that it would override the root `exports`; harmless, the package root (not
  `dist/`) is published and the generated `dist/package.json` is removed after the build.
- **Svelte / Astro "dist (gzip)"** in `docs/sizes.md` is the sum of 703+ individually gzipped component files; it is
  not what an app bundles (only imported components end up in the build).

## Tooling / environment

- **Node version.** Published packages declare `"node": ">=20"`. The development tooling (vitest 5, tsup 9,
  Angular 22, Astro 7) needs Node ≥ 22.18, so the workspace root requires that and CI runs Node 22 and 24.
- **File system.** pnpm workspaces need symlinks/junctions. The repository cannot live on exFAT/FAT drives
  (that is why it moved from `H:\filecon` to `C:\filecon`).
- **Git safe.directory.** On file systems without ownership information Git refuses to work in the repository;
  add `safe.directory` for the path (this was not changed globally by the automation).
